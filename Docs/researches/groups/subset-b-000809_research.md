# subset-b-000809 research

This grouped report covers the requested PowerPC XIVE interrupt-controller, build-tool, and xmon support files. Each section is wrapped with source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/common.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/common.c

## Purpose
`common.c` is the generic PowerPC XIVE interrupt-controller core. It connects Linux `irq_chip`, `irq_domain`, SMP IPI, CPU hotplug, xmon, and debugfs behavior to a backend-specific `struct xive_ops` implementation supplied by native OPAL or sPAPR. It owns interrupt queue scanning, source masking and EOI sequencing, CPU target selection, per-CPU queue setup, and global XIVE initialization.

## Important APIs, Types, And Functions
Global state includes `__xive_enabled`, `xive_tima`, `xive_tima_offset`, `xive_ops`, `xive_irq_domain`, `xive_irq_priority`, and per-CPU `struct xive_cpu *`. The main callbacks exposed to generic IRQ code are in `xive_irq_chip`: `xive_irq_startup`, `xive_irq_shutdown`, `xive_irq_eoi`, `xive_irq_mask`, `xive_irq_unmask`, `xive_irq_set_affinity`, `xive_irq_set_type`, `xive_irq_retrigger`, `xive_irq_set_vcpu_affinity`, and `xive_get_irqchip_state`. `xive_core_init` is the central backend entry point, and `xive_queue_page_alloc`, `xive_cleanup_irq_data`, `is_xive_irq`, `xive_smp_probe`, `xive_smp_prepare_cpu`, `xive_smp_setup_cpu`, `xive_smp_disable_cpu`, `xive_flush_interrupt`, `xive_teardown_cpu`, and `xive_core_debug_init` are the key integration functions.

## Control Flow
Initialization records backend ops and TIMA mapping, installs `ppc_md.get_irq`, creates the IRQ domain, allocates the boot CPU queue, and enables CPU interrupt flow by setting CPPR to `0xff`. When an interrupt arrives, `xive_get_irq` asks the backend to acknowledge pending priorities, then `xive_scan_interrupts` consumes the highest-priority valid queue entry and updates CPPR. Startup chooses a target CPU, programs the backend with hardware target, priority, and Linux IRQ number, then unmasks the ESB. EOI updates source state, handles StoreEOI or legacy PQ/LSI paths, clears saved queue occupancy, and peeks for more queued work to trigger replay. Affinity changes pick a new target and defer old queue count cleanup until the old queue drains. KVM pass-through uses `xive_irq_set_vcpu_affinity` to move sources between host and guest while preserving pending P/Q state.

## State And Persistence
All state is runtime kernel state. Per-CPU `xive_cpu` records queue pages, pending priority bits, cached CPPR, chip id, and IPI metadata. Per-interrupt `xive_irq_data` records MMIO mappings, ESB flags, target CPU, saved/stale P state, and hardware IRQ id. Queue accounting uses `count` and `pending_count` atomics to avoid freeing capacity before stale queue entries are observed. Command-line settings persist only for the booted kernel: `xive=off` and `xive.store-eoi=off`.

## Dependencies And Integration Points
This file depends on Linux IRQ domains, generic IRQ descriptors, SMP, CPU hotplug, debugfs, xmon, Open Firmware device nodes, PowerPC TIMA and XIVE register definitions, and backend `xive_ops`. It integrates with KVM through forwarded IRQ handling, with xmon through dump helpers, with `arch_debugfs_dir` for diagnostics, and with backend native/sPAPR files for hardware programming.

## Risks
The riskiest paths are P/Q state transitions around mask, EOI, retrigger, shutdown, and KVM pass-through because losing `saved_p` or `stale_p` can drop or duplicate interrupts. Queue target accounting intentionally delays decrements, so changes can cause queue exhaustion or premature reuse. CPU hotplug flushes stale queue entries with descriptor locks and must not mishandle IPIs or non-XIVE IRQs. `xive_get_irq` drops `XIVE_BAD_IRQ` and warns on missing descriptors, which indicates shutdown synchronization failures.

## Test Signals
Coverage is mostly platform and boot-test driven: successful boot on XIVE native and pseries guests, interrupt delivery under load, CPU hotplug, affinity changes, MSI and LSI behavior, KVM device pass-through, IPI storms, and debugfs/xmon dumps. Build coverage requires both `CONFIG_SMP`, `CONFIG_HOTPLUG_CPU`, `CONFIG_XMON`, `CONFIG_DEBUG_FS`, and irqdomain hierarchy variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/native.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/native.c

## Purpose
`native.c` implements the XIVE backend for PowerNV systems running against OPAL/skiboot. It supplies the generic core with OPAL-backed interrupt source discovery, source programming, queue setup, TIMA acknowledgement, IPI allocation, CPU setup, shutdown, and debug hooks. It also exports native XIVE helper APIs used by KVM and other PowerNV code for VP and queue management.

## Important APIs, Types, And Functions
Backend callbacks are collected in `xive_native_ops`. Important backend functions include `xive_native_populate_irq_data`, `xive_native_configure_irq`, `xive_native_configure_queue`, `xive_native_disable_queue`, `xive_native_setup_queue`, `xive_native_cleanup_queue`, `xive_native_update_pending`, CPU prepare/setup/teardown callbacks, IPI get/put callbacks, and `xive_native_shutdown`. Exported helper APIs include `xive_native_alloc_irq_on_chip`, `xive_native_free_irq`, `xive_native_alloc_vp_block`, `xive_native_free_vp_block`, `xive_native_enable_vp`, `xive_native_disable_vp`, `xive_native_get_vp_info`, `xive_native_get_queue_info`, queue state get/set helpers, feature probes for single escalation/save-restore, and sync helpers.

## Control Flow
`xive_native_init` locates the OPAL XIVE device tree node, maps the hypervisor TIMA window, chooses the queue size and maximum priority, records KVM TIMA mappings, reads provisioning configuration, switches OPAL to exploitation mode, allocates pool VPs, and calls `xive_core_init`. Interrupt data population asks OPAL for source flags/pages, maps EOI and trigger pages, and records LSI/StoreEOI attributes. Queue configuration asks OPAL for queue info, initializes queue indexes and masks, sets `OPAL_XIVE_EQ_ALWAYS_NOTIFY | OPAL_XIVE_EQ_ENABLED`, optionally enables escalation, and publishes `q->qpage` after a write barrier. Interrupt acknowledgement reads `TM_SPC_ACK_HV_REG`, derives CPPR and HE, and marks pending priorities for the generic scanner.

## State And Persistence
Runtime state includes queue shift, provisioning page size/chip list/cache, pool VP base, and capability booleans. OPAL mode is changed from emulation to exploitation during init and reset to emulation during shutdown. Queue pages and provisioning pages are kernel allocations; donated provisioning pages are intentionally ignored by kmemleak. VP, queue, and IRQ state live in firmware and are accessed through OPAL calls.

## Dependencies And Integration Points
This file depends on OPAL XIVE calls, PowerNV machine init, device tree properties such as `ibm,opal-xive-pe`, `ibm,xive-eq-sizes`, provisioning properties, TIMA registers, `kvmppc_set_xive_tima`, and generic XIVE core contracts. KVM integration is substantial through exported VP, queue, escalation, save/restore, and TIMA APIs.

## Risks
OPAL calls can return `OPAL_BUSY` or `OPAL_XIVE_PROVISIONING`; retry and provisioning paths must remain correct or initialization and KVM VP allocation fail. MMIO mappings must be cleaned correctly when trigger and EOI pages alias. Publishing `q->qpage` before queue fields are visible would race KVM IPI EOI logic. Firmware capability mismatches around queue state, VP save/restore, and single escalation affect migration and virtualization.

## Test Signals
Signals include successful PowerNV boot with native XIVE, OPAL exploitation-mode entry, MSI/LSI delivery, IPI allocation/free, KVM XIVE guests, VP block allocation under provisioning pressure, queue state save/restore tests when firmware supports it, and debugfs exposure of `save-restore`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/native.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/spapr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/spapr.c

## Purpose
`spapr.c` implements the XIVE backend for pseries/sPAPR guests. It translates the generic XIVE core operations into PAPR `H_INT_*` hypercalls, manages guest-available logical interrupt source number ranges, shares queue pages for secure guests, and initializes XIVE from the pseries device tree and option-vector state.

## Important APIs, Types, And Functions
`struct xive_irq_bitmap` tracks allocatable LISN ranges from `ibm,xive-lisn-ranges`; helpers add, allocate, free, and remove these bitmaps. PAPR wrappers include `plpar_int_reset`, source info/config get/set, queue info/config get/set, `plpar_int_sync`, and `plpar_int_esb`. Backend callbacks in `xive_spapr_ops` include IRQ data population, IRQ configuration, queue setup/cleanup, IPI get/put, update pending, ESB read/write via hcall, shutdown, source sync, and debug display. Init helpers include `xive_get_max_prio`, `get_vec5_feature`, `xive_spapr_disabled`, and `xive_spapr_init`.

## Control Flow
Initialization first checks architecture vector 5 and `xive=off` policy, finds `ibm,power-ivpe`, maps the OS TIMA window, computes an allowed priority from `ibm,plat-res-int-priorities`, builds LISN allocator bitmaps, selects a queue size, then calls `xive_core_init`. Interrupt source population calls `H_INT_GET_SOURCE_INFO`, records StoreEOI/LSI/H_INT_ESB flags, and either relies on hypercall ESB access or maps EOI/trigger pages. Queue setup allocates a queue page, asks for queue notification info, programs `H_INT_SET_QUEUE_CONFIG`, and shares the page with the ultravisor for secure guests. Interrupt acknowledgement reads `TM_SPC_ACK_OS_REG`, updates pending priority bits, and lets common code drain queues.

## State And Persistence
The backend keeps runtime queue shift and a list of LISN allocation bitmaps. Allocated IPI LISNs are marked in these bitmaps until CPU teardown. Queue pages are normal kernel pages but become shared/unshared with the ultravisor for secure guests. Hypervisor-side interrupt source and queue configuration is mutable runtime state reset by `H_INT_RESET`.

## Dependencies And Integration Points
Dependencies include PAPR hcalls, RTAS-like busy delay semantics, flattened and live device tree data, PowerPC TIMA registers, secure guest helpers `is_secure_guest`, `uv_share_page`, and `uv_unshare_page`, and the shared XIVE core. It integrates with pseries machine init and uses `machine_arch_initcall(pseries, xive_core_debug_init)`.

## Risks
Hypercalls may return busy and require delay/retry; missing retries would cause transient boot or interrupt setup failures. LISN bitmap locking must protect concurrent IPI allocation. H_INT_ESB sources deliberately skip MMIO mapping, so common ESB access depends on the `esb_rw` callback. Secure guest page share/unshare balance is required for memory isolation. Priority selection must avoid hypervisor-reserved priorities.

## Test Signals
Signals include pseries guest boot with XIVE enabled, fallback behavior when option vector or `xive=off` disables XIVE, CPU hotplug with IPI LISN allocation/free, secure guest queue sharing, interrupt delivery through H_INT_ESB and MMIO ESB paths, and debugfs bitmap dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/spapr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/xive-internal.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/xive-internal.h

## Purpose
`xive-internal.h` is the private contract between the generic XIVE core and its native/sPAPR backends. It defines per-CPU XIVE state, backend operation callbacks, disabled IRQ sentinels, queue constants, and shared initialization/debug helpers.

## Important APIs, Types, And Functions
`XIVE_BAD_IRQ` marks disabled interrupts and `XIVE_MAX_IRQ` bounds valid logical interrupt values. `struct xive_cpu` stores optional IPI hardware state, chip id, up to eight queues, pending-priority bits, and cached CPPR. `struct xive_ops` defines backend hooks for IRQ data population, IRQ configuration/query, queue setup/cleanup, CPU lifecycle, node matching, shutdown, pending update, source sync, ESB access, IPI allocation/free, and debugfs support. Declared helpers are `xive_core_init`, `xive_queue_page_alloc`, `xive_core_debug_init`, and `xive_alloc_order`.

## Control Flow
The header itself has no runtime control flow, but it shapes the sequence used by both backends: discover hardware, provide a populated `xive_ops`, call `xive_core_init`, allocate per-CPU queues through `setup_queue`, acknowledge pending work through `update_pending`, and let common IRQ paths call backend configuration callbacks.

## State And Persistence
It defines in-memory runtime state only. `xive_cpu.queue` entries carry queue page and accounting fields declared in public XIVE headers, while `pending_prio` and `cppr` mirror current CPU interrupt flow state. `xive_cmdline_disabled` and `xive_has_save_restore` are shared global capability/configuration flags.

## Dependencies And Integration Points
The definitions depend on `struct xive_irq_data`, `struct xive_q`, `struct device_node`, `struct seq_file`, and debugfs dentry types from surrounding kernel headers. It is included by `common.c`, `native.c`, and `spapr.c`, and backs external users through exported globals declared here.

## Risks
`struct xive_ops` is a strict backend ABI inside the kernel; common code assumes required callbacks are present for the selected backend. `XIVE_MAX_QUEUES` and priority bit handling are coupled to a `u8 pending_prio`, so adding more priorities requires wider state. Misusing `XIVE_BAD_IRQ` as a real IRQ would corrupt disabled-source handling.

## Test Signals
Compile coverage across native and pseries XIVE configurations validates this header. Runtime signals are successful backend initialization, queue allocation at the selected priority, debugfs creation, IPI setup under `CONFIG_SMP`, and KVM save/restore capability exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/xive-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/tools/Makefile

## Purpose
This Makefile hooks PowerPC architecture build tooling into Kbuild for generating `vmlinux.arch.S`, the assembly reservation file for out-of-line ftrace stubs.

## Important APIs, Types, And Functions
It defines `quiet_cmd_gen_ftrace_ool_stubs` and `cmd_gen_ftrace_ool_stubs`, invoking `ftrace-gen-ool-stubs.sh` with the configured text-stub reserve count, 64-bit setting, objdump path, `vmlinux.o`, and output file. The target rule builds `$(obj)/vmlinux.arch.S` from the script and `vmlinux.o`, and adds the output to `targets`.

## Control Flow
During the architecture build, Kbuild detects the generated assembly target and runs the command through `if_changed`, regenerating only when inputs or command text change. The generated assembly is later linked into the kernel to reserve ftrace trampoline space.

## State And Persistence
The persistent build artifact is `vmlinux.arch.S` in the object tree. No source-tree state is modified by the Makefile itself.

## Dependencies And Integration Points
It depends on Kbuild variables `CONFIG_PPC_FTRACE_OUT_OF_LINE_NUM_RESERVE`, `CONFIG_64BIT`, `OBJDUMP`, `obj`, `src`, and `FORCE`, and integrates with `ftrace-gen-ool-stubs.sh` and the final PowerPC link.

## Risks
Incorrect argument ordering or stale dependency tracking would reserve the wrong number of stubs, causing ftrace patching failures. Because `vmlinux.o` is an input, this rule sits late enough in the build that missing tools or section format changes can break final linking.

## Test Signals
Builds with function tracing and patchable function entries enabled should generate `vmlinux.arch.S`; incremental builds should regenerate it when `vmlinux.o` or the script changes. Link-time ftrace failures are the primary downstream signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/check-fpatchable-function-entry.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/tools/check-fpatchable-function-entry.sh

## Purpose
This shell probe verifies that the compiler supports `-fpatchable-function-entry=2` for ppc64 ELFv2 and emits patchable entries in the layout expected by PowerPC ftrace.

## Important APIs, Types, And Functions
The script receives the compiler command as `$*`, forces `-m64 -mabi=elfv2`, compiles small C snippets to assembly, and uses `grep` plus `awk` to check for `__patchable_function_entries` and two `nop` instructions after `.localentry`.

## Control Flow
With `set -e`, any failed compile or missing pattern exits nonzero. The first compile checks that the option exists and emits the metadata section. The second compile checks code placement by splitting assembly records on semicolons and finding a function whose local entry is followed by two NOPs.

## State And Persistence
The script is stateless and writes no files; it streams source to the compiler and assembly to filters.

## Dependencies And Integration Points
It depends on bash, the configured compiler, assembler output syntax, `grep`, and `awk`. It is intended for Kconfig/build feature detection for PowerPC ftrace patching.

## Risks
The probe is intentionally ppc64 ELFv2-specific and should not be used for other ABIs. Assembly formatting differences across compilers can create false negatives. Passing the compiler through `$*` preserves simple command use but can be fragile with unusual quoting.

## Test Signals
A zero exit status means the toolchain supports the expected patchable-function-entry format. Nonzero status should disable the dependent ftrace feature or fail the capability check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/check-fpatchable-function-entry.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/checkpatch.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/tools/checkpatch.sh

## Purpose
This script is a PowerPC wrapper around the kernel `scripts/checkpatch.pl` tool with architecture-maintainer preferred options and ignores.

## Important APIs, Types, And Functions
It computes `script_base` with `realpath $(dirname $0)` and `exec`s the top-level `scripts/checkpatch.pl` with `--subjective`, `--no-summary`, `--show-types`, and a curated set of `--ignore` rules. Arguments from the caller are appended unchanged with `$@`.

## Control Flow
The wrapper immediately replaces itself with checkpatch. There is no intermediate validation; all patch/file arguments are handled by the upstream script.

## State And Persistence
No state is persisted. Output and exit status are those of `checkpatch.pl`.

## Dependencies And Integration Points
It depends on bash, `realpath`, the kernel source tree layout relative to `arch/powerpc/tools`, Perl checkpatch, and PowerPC contribution workflows.

## Risks
Ignored warning categories encode local policy and can hide issues if used outside PowerPC review. The unquoted `dirname $0` command substitution is conventional here but could misbehave for paths containing whitespace. Any move in tree layout breaks the relative checkpatch path.

## Test Signals
Running the wrapper on a known patch should show typed checkpatch diagnostics without the ignored classes and should return checkpatch's status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/checkpatch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/ftrace-gen-ool-stubs.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/tools/ftrace-gen-ool-stubs.sh

## Purpose
This generator counts patchable function-entry relocations in `vmlinux.o` and emits assembly reserving out-of-line ftrace stub space for normal text and init text.

## Important APIs, Types, And Functions
Inputs are reserve count, 64-bit flag, objdump path, `vmlinux.o`, and output assembly path. It selects relocation type `R_PPC64_ADDR64` or `R_PPC_ADDR32`, counts total and init-text relocations in `__patchable_function_entries`, computes text-end stubs beyond the built-in reserve, and writes symbols `ftrace_ool_stub_text_end_count`, `ftrace_ool_stub_text_end`, `ftrace_ool_stub_inittext_count`, and `ftrace_ool_stub_inittext`.

## Control Flow
With `set -e`, objdump/grep/count failures stop the build. The script counts relocations, subtracts init/startup entries from total text entries, clamps extra text-end stubs at zero, then writes an assembly file with `.tramp.ftrace.text` and `.tramp.ftrace.init` sections sized by `FTRACE_OOL_STUB_SIZE`.

## State And Persistence
The persistent output is the generated `vmlinux.arch.S`. It derives entirely from the current `vmlinux.o` relocation table and configuration inputs.

## Dependencies And Integration Points
It depends on objdump output format, `grep`, POSIX shell arithmetic, and assembly macros from `asm/asm-offsets.h`, `asm/ppc_asm.h`, and `linux/linkage.h`. The Makefile uses it during the PowerPC final build.

## Risks
Relocation naming or section naming changes can miscount stubs. The generated file is critical for ftrace patch reachability, so under-reservation can break runtime tracing while over-reservation wastes text space. The script overwrites its output path directly.

## Test Signals
Builds with `CONFIG_FUNCTION_TRACER` and patchable entries should produce nonzero counts when functions exist. The downstream `ftrace_check.sh` and successful boot with ftrace enabled are practical validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/ftrace-gen-ool-stubs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/ftrace_check.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/tools/ftrace_check.sh

## Purpose
`ftrace_check.sh` verifies that the built kernel places `ftrace_caller` and `ftrace_tramp_text` within branch reach constraints required by PowerPC ftrace.

## Important APIs, Types, And Functions
The script consumes paths to `nm` and `vmlinux`, extracts `_stext`, `ftrace_caller`, and `ftrace_tramp_text` addresses, computes offsets with `bc`, and compares them against 32 MiB and 64 MiB limits.

## Control Flow
After argument validation, it reads symbol addresses, normalizes them to uppercase hex, computes `ftrace_caller - _stext` and `ftrace_tramp_text - ftrace_caller`, then emits explicit errors and exits nonzero when either architectural reachability limit is exceeded.

## State And Persistence
It is stateless and writes no files.

## Dependencies And Integration Points
It depends on bash, `nm`, `grep`, `cut`, `tr`, `bc`, and final `vmlinux` symbols. It is a post-link architecture validation gate for function tracing.

## Risks
Missing symbols produce empty arithmetic inputs and confusing failures. Symbol type assumptions must match linker output. The check is address-distance based and does not inspect individual call sites, so it complements but does not replace runtime ftrace testing.

## Test Signals
A passing run exits zero. Failure messages identify whether `ftrace_caller` is too far from `_stext` or kernel text extends too far from `ftrace_caller`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/ftrace_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/gcc-check-mprofile-kernel.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/tools/gcc-check-mprofile-kernel.sh

## Purpose
This compiler probe checks whether a ppc64 ELFv2 toolchain supports `-mprofile-kernel` correctly for kernel profiling and respects the `notrace` attribute.

## Important APIs, Types, And Functions
It receives the compiler invocation as `$*`, forces `-m64 -mabi=elfv2`, compiles small C snippets with `-S -x c -O2 -p -mprofile-kernel`, searches for `_mcount`, and includes `<linux/compiler.h>` to test `notrace`.

## Control Flow
The first compile must produce an `_mcount` call. The second compile marks the function `notrace`; if `_mcount` still appears, the script exits with status 1. Otherwise it exits zero.

## State And Persistence
The script writes no files and keeps no state.

## Dependencies And Integration Points
It depends on bash, the configured compiler, kernel include paths supplied by the caller environment, and assembly naming conventions. It is used as a build-time feature check before enabling mprofile-based tracing.

## Risks
It is valid only for 64-bit ELFv2 and can be misleading for other targets. Assembly output differences or missing include paths can cause false negatives. The second test's failure condition is inverted through `grep ... && exit 1`, so changes should preserve that logic.

## Test Signals
Zero exit means `_mcount` is emitted for normal functions and suppressed for `notrace`; nonzero means the feature should not be enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/gcc-check-mprofile-kernel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/head_check.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/tools/head_check.sh

## Purpose
`head_check.sh` validates that 64-bit PowerPC head code remains at fixed expected locations and has not been displaced by linker-inserted branch stubs.

## Important APIs, Types, And Functions
It accepts paths to `nm` and `vmlinux`, extracts `_stext`, `start_first_256B`, `text_start`, and `start_text` into `.tmp_symbols.txt`, compares expected and actual addresses, and emits guidance about `LD_HEAD_STUB_CATCH` on failure.

## Control Flow
The script validates arguments, captures relevant symbols, checks that `start_first_256B` equals `_stext`, derives the top VMA prefix, checks that `start_text` equals the relocated `text_start`, then removes the temporary symbol file.

## State And Persistence
It temporarily creates `.tmp_symbols.txt` in the current working directory and deletes it on the success path. It has no intended persistent output.

## Dependencies And Integration Points
It depends on POSIX shell, `nm`, `grep`, `cut`, and `sed`, and integrates with the PowerPC post-link checks that protect early boot and interrupt-vector placement.

## Risks
Failure before cleanup can leave `.tmp_symbols.txt`. Address derivation with `cut -d'0' -f1` assumes the expected kernel VMA string shape. The check is sensitive to symbol names and types emitted by different toolchains.

## Test Signals
Passing output is silent with zero exit. Failures report the mismatched symbol address and point maintainers to branch-stub placement comments in the script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/head_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/relocs_check.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/tools/relocs_check.sh

## Purpose
This wrapper filters the generic kernel relocation checker for PowerPC, warning only on relocations that are suspicious for PowerPC kernel images.

## Important APIs, Types, And Functions
It expects objdump, nm, and vmlinux arguments, calls `${srctree}/scripts/relocs_check.sh "$@"`, removes allowed relocation names with fixed-string word grep, counts remaining lines, and prints a warning plus the bad relocation list.

## Control Flow
If too few arguments are supplied, it exits with usage. Otherwise it runs the generic checker, filters allowed PPC32/PPC64 relocation types, exits zero when none remain, or prints the count and entries. It does not force a nonzero exit for warnings after printing.

## State And Persistence
No state is persisted; all data flows through command substitution and stdout.

## Dependencies And Integration Points
It depends on `${srctree}`, the generic relocation checker, grep, wc, and shell command substitution. It is part of post-link architecture validation.

## Risks
Because warnings do not necessarily fail the build, downstream policy must decide severity. The whitelist must track legitimate relocation types; missing entries create noisy warnings, while overly broad entries hide real boot-time relocation hazards.

## Test Signals
Clean builds produce no output and zero exit. Introducing an unsupported relocation should produce `WARNING: N bad relocations` followed by the generic checker lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/relocs_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/unrel_branch_check.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/tools/unrel_branch_check.sh

## Purpose
`unrel_branch_check.sh` detects suspicious relative branches from unrelocated early PowerPC code to relocated code beyond the interrupt-vector region.

## Important APIs, Types, And Functions
It consumes objdump, nm, and vmlinux paths, finds `__end_interrupts` and `__start_initialization_multiplatform`, disassembles from kernel start `0xc000000000000000` to `__end_interrupts`, filters branch instructions with sed, normalizes branch targets, and prints warnings for targets past the unrelocated region.

## Control Flow
If `__end_interrupts` is absent, it exits successfully. Otherwise it disassembles early code, removes CTR/LR branches, handles GNU and Clang objdump conditional branch spelling, computes absolute targets for direct and relative branches, skips the one known valid branch to initialization, and emits warnings when a branch lands after `__end_interrupts`.

## State And Persistence
The script is stateless and writes only diagnostics.

## Dependencies And Integration Points
It depends on bash arithmetic, objdump, nm, sed, PowerPC branch encoding ranges, and early kernel symbol names. It is part of post-link validation for head and interrupt-vector code.

## Risks
Parsing disassembly text is fragile across tool versions. The script contains a typo in the unknown-format diagnostic but still identifies the path. Incorrect branch offset sign extension would either miss invalid branches or warn on valid ones. The known-good exception must remain aligned with early boot code.

## Test Signals
Passing output is silent. A problematic branch produces `WARNING: Unrelocated relative branches` followed by source address, branch mnemonic, computed target, and optional symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/tools/unrel_branch_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/Makefile

## Purpose
This Makefile builds the PowerPC xmon debugger components while disabling instrumentation that is unsafe or noisy inside low-level debug code.

## Important APIs, Types, And Functions
It disables GCOV, KCOV, UBSAN, KASAN, and KCSAN for the directory, removes ftrace flags when function tracing is enabled, adds a Clang-specific larger frame warning threshold, always builds `xmon.o`, `nonstdio.o`, `spr_access.o`, and `xmon_bpts.o`, and conditionally builds `ppc-dis.o` and `ppc-opc.o` for `CONFIG_XMON_DISASSEMBLY`.

## Control Flow
Kbuild evaluates instrumentation variables and object lists based on configuration, then compiles xmon code with tracing and sanitizers disabled.

## State And Persistence
The Makefile creates normal object files in the build tree and no runtime persistent state.

## Dependencies And Integration Points
It depends on Kbuild, `CONFIG_FUNCTION_TRACER`, `CONFIG_CC_IS_CLANG`, and `CONFIG_XMON_DISASSEMBLY`. It integrates xmon with low-level SPR access, breakpoint support, and optional disassembly tables.

## Risks
Re-enabling tracing or sanitizers in this directory can recurse into debugging paths or break fragile low-level contexts. Optional disassembly objects must remain paired with declarations in `dis-asm.h`.

## Test Signals
Builds with and without `CONFIG_XMON_DISASSEMBLY`, GCC and Clang builds, and entering xmon during boot or crash paths are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/ansidecl.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/ansidecl.h

## Purpose
`ansidecl.h` provides legacy ANSI/traditional C compatibility macros imported from old GNU code so the xmon disassembler sources can compile in the kernel tree.

## Important APIs, Types, And Functions
Macros include `PTR`, `PTRCONST`, `LONG_DOUBLE`, `AND`, `NOARGS`, `CONST`, `VOLATILE`, `SIGNED`, `DOTS`, `EXFUN`, `DEFUN`, `DEFUN_VOID`, `PROTO`, `PARAMS`, and `ANSI_PROTOTYPES`. The header selects ANSI definitions when `__STDC__`, `_AIX`, certain MIPS SVR4 modes, or `WIN32` are defined; otherwise it falls back to traditional C forms.

## Control Flow
There is no runtime control flow. Preprocessor conditionals expand declarations and function definitions differently depending on compiler mode.

## State And Persistence
The header has no state and no persistence.

## Dependencies And Integration Points
It is included by `ppc-dis.c` and supports binutils-derived headers and code such as `ppc.h`. In a modern kernel build, the ANSI branch is expected.

## Risks
These macros are obsolete and can conflict with kernel style or names if included broadly. The non-ANSI branch redefines `const` when missing and should remain isolated to the imported disassembler code. Changes can break compatibility with `ppc.h` declarations.

## Test Signals
Successful xmon disassembly builds are the main signal. Because runtime behavior is preprocessor-only, compile failures in `ppc-dis.c` or `ppc-opc.c` reveal regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/ansidecl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/dis-asm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/dis-asm.h

## Purpose
`dis-asm.h` declares the small disassembler interface used by xmon and provides fallback instruction printing when full xmon disassembly is disabled.

## Important APIs, Types, And Functions
It declares `print_address`. Under `CONFIG_XMON_DISASSEMBLY`, it declares `print_insn_powerpc` and `print_insn_spu`. Otherwise it defines inline fallbacks that print the instruction word as eight hex digits and return zero.

## Control Flow
Callers can use the same print functions regardless of configuration. With disassembly enabled, calls resolve to real decoder implementations; without it, the inline fallback emits raw words.

## State And Persistence
The header carries no state. Output goes through `printf`, which xmon maps to `xmon_printf`.

## Dependencies And Integration Points
It depends on the xmon `printf` environment and on `CONFIG_XMON_DISASSEMBLY`. It is implemented by `ppc-dis.c` and used by xmon command paths that display instructions.

## Risks
The disabled fallback returns zero, while real disassemblers return instruction lengths; callers must tolerate both. The header assumes `printf` is available through xmon's nonstdio layer.

## Test Signals
Builds with `CONFIG_XMON_DISASSEMBLY=y` should link real functions. Builds without it should still allow xmon to display raw instruction words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/dis-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/nonstdio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/nonstdio.c

## Purpose
`nonstdio.c` implements xmon's minimal console I/O layer on top of `udbg`, including character input, line editing, printf-style output, and optional pagination for long debugger output.

## Important APIs, Types, And Functions
Public functions are `xmon_start_pagination`, `xmon_end_pagination`, `xmon_set_pagination_lpp`, `xmon_putchar`, `xmon_gets`, `xmon_printf`, and `xmon_puts`. Internal helpers include `xmon_readchar`, `xmon_write`, and `xmon_getchar`. Static state includes pagination flags, lines-per-page, current line count, a 256-byte input line buffer, and a 1024-byte printf output buffer.

## Control Flow
Output flows through `xmon_write`, which optionally paginates on newline boundaries, prompts after the configured number of lines, and accepts `a` for all output, `q` for truncation, or any other key for the next page. `xmon_putchar` translates newline to CRLF. Input is line buffered: it reads from `udbg_getc`, echoes characters, handles backspace/delete and Ctrl-U, rings the bell on overflow, and returns buffered characters to `xmon_gets`.

## State And Persistence
All state is in static memory and lasts for the running kernel. Pagination state persists across xmon output until explicitly ended. Input and output buffers are shared, not per-caller, matching xmon's single-console use.

## Dependencies And Integration Points
It depends on `udbg_getc`, `udbg_write`, kernel `vsnprintf`, `pr_cont` fallback output, and declarations from `nonstdio.h`. Higher-level xmon commands and the disassembler use this instead of libc stdio.

## Risks
The static buffers are not reentrant. If no `udbg` hooks are installed, `xmon_printf` can fall back to `printk` continuation output, which the source labels dangerous. Pagination can drop output after `q` while still reporting bytes consumed to callers. Input editing is limited to simple control characters and fixed line size.

## Test Signals
Manual xmon sessions validate line editing, CRLF output, pagination prompts, truncation, and fallback output. Build coverage ensures `__printf` users match format arguments through the header declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/nonstdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/nonstdio.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/nonstdio.h

## Purpose
`nonstdio.h` exposes xmon's minimal stdio replacement and maps familiar names to xmon-specific console routines.

## Important APIs, Types, And Functions
It defines `EOF` as `-1`, declares pagination controls, `xmon_putchar`, `xmon_puts`, `xmon_gets`, and `xmon_printf`, and maps `printf` to `xmon_printf` and `putchar` to `xmon_putchar`.

## Control Flow
The header has no runtime flow, but the macros redirect imported or debugger code that calls `printf`/`putchar` into xmon's `udbg`-backed I/O path.

## State And Persistence
No state is defined here; implementation state lives in `nonstdio.c`.

## Dependencies And Integration Points
It depends on kernel `__printf` annotation support and is included by xmon code and the binutils-derived disassembler.

## Risks
The `printf` and `putchar` macros are broad and can surprise code included after this header. The header intentionally provides only a tiny subset of stdio, so imported code must not require full libc behavior.

## Test Signals
Successful xmon and disassembler builds validate macro compatibility. Runtime xmon command output validates redirection through `xmon_printf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/nonstdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc-dis.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc-dis.c

## Purpose
`ppc-dis.c` is the xmon PowerPC instruction disassembler, derived from GNU binutils. It decodes a 32-bit instruction word using opcode and operand tables and prints a textual instruction form through xmon's nonstdio layer.

## Important APIs, Types, And Functions
The public entry point is `print_insn_powerpc`. Internal helpers are `operand_value_powerpc`, which extracts and sign-extends operands, `skip_optional_operands`, which suppresses optional operands at default values, and `lookup_powerpc`, which scans `powerpc_opcodes` and validates operand extraction. It consumes `struct powerpc_opcode`, `struct powerpc_operand`, `powerpc_opcodes`, `powerpc_num_opcodes`, `powerpc_operands`, and `ppc_optional_operand_value` from `ppc.h`/`ppc-opc.c`.

## Control Flow
`print_insn_powerpc` builds a dialect mask from base PPC/common flags, 64-bit configuration, and runtime CPU features for HTM, AltiVec, and VSX. It looks up the opcode by mask and dialect, falls back to any dialect if allowed, prints the mnemonic, iterates operands, skips fake and optional operands as needed, formats registers, relative and absolute addresses, condition register bits, and immediates, then returns the instruction length. Unknown instructions print as `.long`.

## State And Persistence
The file holds no mutable persistent state except a small static condition-bit name table inside printing. Output is immediate xmon console text. Dialect selection is derived each call from CPU feature state.

## Dependencies And Integration Points
It depends on `asm/cputable.h`, `cpu_has_feature`, `nonstdio.h`, legacy `ansidecl.h`, opcode declarations in `ppc.h`, and `dis-asm.h`. Xmon command code calls it when `CONFIG_XMON_DISASSEMBLY` includes the disassembler objects.

## Risks
Opcode table order matters because lookup returns the first valid match. Operand extraction callbacks can mark instructions invalid; errors there affect decoding quality. The dialect mask must track new CPU features and ISA extensions or xmon will print valid instructions as `.long`. Imported coding style differs from kernel style and should be changed cautiously.

## Test Signals
Manual xmon disassembly of known instructions, build tests with and without CPU feature options, and comparison against objdump for representative PowerPC instructions are the best signals. Unknown instruction paths should print raw `.long` values without crashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc-dis.c -->
