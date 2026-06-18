# subset-b-000781 Research

Grouped research report for the requested PowerPC Ceph-client kernel subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/traps.c

## Purpose
Implements the architecture-specific exception and trap handlers for PowerPC. It turns low-level interrupt vectors into kernel oops/panic paths, debugger/kprobe/uprobe notifications, user signals, instruction emulation, machine-check recovery, facility-unavailable handling, performance/debug exceptions, and optional emulated-instruction accounting.

## Important APIs, Types, And Functions
The externally visible and interrupt-entry functions include `die_will_crash`, `panic_flush_kmsg_start`, `panic_flush_kmsg_end`, `die`, `user_single_step_report`, `_exception`, `_exception_pkey`, `hv_nmi_check_nonrecoverable`, `system_reset_exception`, `machine_check_*`, `die_mce`, `machine_check_exception`, `handle_hmi_exception`, `instruction_breakpoint_exception`, `single_step_exception`, `emulate_single_step`, `program_check_exception`, `emulation_assist_interrupt`, `alignment_exception`, `facility_unavailable_exception`, TM unavailable handlers, `performance_monitor_exception*`, `DebugException`, `altivec_assist_exception`, SPE handlers, `unrecoverable_exception`, `WatchdogException`, and `kernel_bad_stack`. Support helpers include `oops_begin`, `oops_end`, `exception_common`, `show_signal_msg`, `check_io_access`, `parse_fpe`, `emulate_instruction`, string/popcntb/isel emulators, and optional `ppc_emulated` debugfs state.

## Control Flow
Fatal kernel exceptions enter `die()`, optionally give the debugger first chance, serialize oops output with `die_lock`, print machine/MMU/config context, notify die notifiers, dump registers/modules, then trigger fadump/kdump/panic or kill the current task. User exceptions pass through `exception_common`, set `current->thread.trap_nr`, optionally log rate-limited instruction context, and call `force_sig_fault` or `force_sig_pkuerr`. System reset is an NMI path: it preserves HSRRs in HV mode, marks nonrecoverable HSRR scratch windows, lets platform/debugger handlers run, then routes to fadump, kdump, secondary crash holding, oops, and finally `nmi_panic`. Machine checks call platform or CPU handlers, debugger fault handlers, I/O extable recovery, and otherwise `die_mce`.

Program checks decode reason bits for FP exceptions, traps, TM bad-thing exceptions, illegal or privileged instructions, optional math emulation, and user instruction emulation. Successful emulation advances NIP and replays single-step state. Alignment traps try `fix_alignment` unless the task requested `PR_UNALIGN_SIGBUS`. Facility-unavailable traps either lazily enable or emulate DSCR/TM access or signal `SIGILL`. Debug and performance handlers integrate with perf, kprobes, hardware breakpoints, and debugger callbacks.

## State And Persistence
Persistent state is kernel runtime state: debugger callback pointers, oops serialization counters, `current->thread` trap/debug/FP/vector/TM fields, PACA NMI/HMI flags, irq statistics, taint flags, and optional debugfs counters under `emulated_instructions`. No filesystem data is persisted except debugfs-visible counters and console/kmsg output.

## Dependencies And Integration Points
Depends on PowerPC interrupt macros, `pt_regs`, PACA, machine descriptor callbacks, fadump/kexec crash paths, perf, kprobes, bug tables, exception tables, signal delivery, FP/Altivec/VSX/SPE/TM save-restore code, debug registers, cache/TLB platform machine-check handlers, and `udbg` for early machine checks. It is central to user ABI signal behavior and to crash dump reliability.

## Risks And Edge Cases
This file is high risk because many paths run with interrupts disabled, in NMI context, or after register state is partially unrecoverable. HSRR/HSPRG1 NMI windows, machine-check recoverability, real-mode address fixups, TM transaction abort semantics, endian-sensitive vector emulation, prefixed instruction lengths, and single-step replay are correctness-sensitive. Debugger and notifier callbacks can suppress normal signal/oops handling, so ordering matters.

## Test Signals
Useful signals include PowerPC boot and exception selftests, kprobes/uprobes/perf tests, unaligned access tests, ptrace single-step tests, user `SIGILL`/`SIGTRAP` behavior, math/Altivec/SPE emulation tests, kdump/fadump system-reset drills, machine-check injection where available, and cross-builds for Book3S, BookE, 32-bit, 64-bit, TM, VSX, SPE, and advanced debug configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ucall.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ucall.S

## Purpose
Provides the minimal assembly helper for issuing a PowerPC ultravisor call and returning the status in `r3`.

## Important APIs, Types, And Functions
Exports GPL symbol `ucall_norets`. The body executes `sc 2`, the ultravisor system-call variant, and then returns with `blr`.

## Control Flow
Callers load ultravisor arguments according to the platform ABI and branch to `ucall_norets`. The ultravisor handles the secure call and returns to the helper, which immediately returns to the caller with `r3` carrying the status.

## State And Persistence
The helper has no private state and touches no memory. Its effects are entirely those of the ultravisor operation invoked by `sc 2`.

## Dependencies And Integration Points
Depends on `<asm/ppc_asm.h>` for `_GLOBAL` and on the ultravisor ABI implemented by secure PowerPC platforms. Kernel secure-VM code can link to the exported symbol.

## Risks And Edge Cases
Correctness depends on the caller setting registers exactly as the ultravisor ABI expects. The helper has no local validation, no register save frame, and no fallback for systems without an ultravisor.

## Test Signals
Build/link coverage with ultravisor users and secure guest runtime tests are the main signals. Functional testing should exercise successful and failing ultravisor calls and validate returned status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ucall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/udbg.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/udbg.c

## Purpose
Implements the generic early polling debug console abstraction used before the normal console subsystem is available and by low-level debugger paths.

## Important APIs, Types, And Functions
Global function pointers `udbg_putc`, `udbg_flush`, `udbg_getc`, and `udbg_getc_poll` define the active backend. `udbg_early_init` selects one configured backend such as LPAR, HVSI, G5, RTAS panel, BootX, 44x, CPM, USB Gecko, memory console, OPAL, or 16550. Output helpers are `udbg_puts`, `udbg_write`, `udbg_printf`, and `udbg_progress`. `register_early_udbg_console` installs the `udbg` boot console.

## Control Flow
Early boot calls `udbg_early_init`, which initializes exactly one backend selected by Kconfig, raises the console loglevel for early debug, and registers a boot console if `udbg_putc` is available. Output helpers check the function pointers, emit characters, and flush if supported. The console write callback delegates to `udbg_write`.

## State And Persistence
State is the backend function-pointer set and the registered early console pointer. Output is transient console/kmsg data. The `udbg-immortal` boot option clears `CON_BOOT` so the early console survives beyond normal boot-console teardown.

## Dependencies And Integration Points
Integrates PowerPC platform early-debug backends with Linux console registration, xmon/debugger printing, and early machine-check diagnostics. Backend implementations live in platform-specific files such as `udbg_16550.c`.

## Risks And Edge Cases
Kconfig selects a backend that may make the kernel unbootable on other hardware. `udbg_write` stops on NUL bytes even if `n` is larger, so it is a text console path rather than a binary write path. Registering too early without `udbg_putc` silently does nothing.

## Test Signals
Boot with each early-debug Kconfig on matching hardware or emulation, confirm early panic/machine-check output, verify `udbg-immortal`, and build-test all backend combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/udbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/udbg_16550.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/udbg_16550.c

## Purpose
Provides an NS16550-compatible UART backend for the generic `udbg` early polling console.

## Important APIs, Types, And Functions
Backend setup functions are `udbg_uart_init_pio`, `udbg_uart_init_mmio`, `udbg_uart_setup`, `udbg_probe_uart_speed`, `udbg_init_pas_realmode`, `udbg_init_44x_as1`, and `udbg_init_debug_16550`. Internal callbacks are `udbg_uart_putc`, `udbg_uart_flush`, `udbg_uart_getc`, and `udbg_uart_getc_poll`. Static callbacks `udbg_uart_in` and `udbg_uart_out` abstract PIO, MMIO, real-mode PASEMI, 44x address-space-1, and early-ioremap access.

## Control Flow
Initialization records a port or MMIO base, stride, and register accessors, then installs the UART callbacks into the global `udbg` hooks. `udbg_uart_setup` programs divisor latch, line control, modem control, and FIFO registers. Output waits for transmit-holding-register empty, emits CR before LF, and writes to `UART_THR`. Blocking input spins until `LSR_DR`, while polling input returns immediately.

## State And Persistence
State is the selected UART base, stride, register accessors, and optional early-ioremap address. `udbg_init_debug_16550_ioremap` remaps the physical UART later with normal `ioremap`, switches the backend, and unmaps the early mapping. UART hardware registers retain programmed baud/line/FIFO state until reconfigured or reset.

## Dependencies And Integration Points
Depends on PowerPC I/O helpers, early ioremap, real-mode byte accessors, PASEMI and 44x platform hooks, and the generic `udbg` function pointers. It is selected by early debug Kconfig symbols and feeds the early console path in `udbg.c`.

## Risks And Edge Cases
The polling loops can spin forever if hardware is absent or wedged. The poll helper appears inverted: it reads `UART_RBR` when `LSR_DR` is not set and returns `-1` otherwise, which is worth verifying against surrounding kernel version history. Wrong stride, physical address, or clock produces unreadable output or bus faults in early boot.

## Test Signals
Boot tests with `CONFIG_PPC_EARLY_DEBUG_16550`, PIO and MMIO paths, baud probing, newline translation, early-to-normal ioremap transition, and platform-specific PASEMI/44x early consoles are useful. Hardware or QEMU serial output is the primary functional signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/udbg_16550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/uprobes.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/uprobes.c

## Purpose
Implements PowerPC architecture glue for user-space probes, including trap validation, out-of-line execution setup, single-step completion, exception notifier integration, and return-probe address hijacking.

## Important APIs, Types, And Functions
Defines `is_trap_insn`, `arch_uprobe_analyze_insn`, `arch_uprobe_pre_xol`, `uprobe_get_swbp_addr`, `arch_uprobe_xol_was_trapped`, `arch_uprobe_post_xol`, `arch_uprobe_exception_notify`, `arch_uprobe_abort_xol`, `arch_uprobe_skip_sstep`, `arch_uretprobe_hijack_return_addr`, and `arch_uretprobe_is_alive`. It uses `UPROBE_TRAP_NR` as a sentinel in `current->thread.trap_nr`.

## Control Flow
Probe analysis rejects unaligned addresses, prefixed instructions crossing a 64-byte boundary on ISA 3.1 CPUs, and instructions the architecture cannot single-step. Before XOL, it saves the task trap number, sets the sentinel, redirects NIP to the XOL slot, and enables user single-step. After single-step, it restores the saved trap number, sets NIP to the instruction following the probed instruction, and disables single-step. Die notifiers route breakpoint and single-step exceptions to generic uprobe pre/post handlers.

## State And Persistence
State lives in `current->utask->autask.saved_trap_nr`, `current->thread.trap_nr`, the saved user registers, and the temporary XOL mapping owned by generic uprobes. No durable persistence is involved.

## Dependencies And Integration Points
Depends on generic uprobes, die notifiers, PowerPC instruction helpers, software single-step and instruction emulation (`can_single_step`, `emulate_step`), and ptrace register helpers. Return probes integrate by replacing `regs->link` with a trampoline.

## Risks And Edge Cases
Prefixed instruction alignment is critical because placing a breakpoint in a split prefixed instruction would corrupt execution. XOL trap detection relies on every fault path changing `thread.trap_nr` away from the sentinel. Return-probe liveness depends on PowerPC stack direction and the chain-call special case.

## Test Signals
Run uprobes and uretprobes selftests on PowerPC, including branches/calls, emulated instructions, fatal XOL faults, single-step fallback, prefixed ISA 3.1 instructions near 64-byte boundaries, and nested return probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/uprobes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso.c

## Purpose
Installs and initializes the PowerPC vDSO and vvar mappings for each userspace process, prepares vDSO runtime data, applies CPU/MMU/firmware fixups, and sets up getcpu support.

## Important APIs, Types, And Functions
Key functions are `arch_setup_additional_pages`, `__arch_setup_additional_pages`, `vdso_mremap`, `vdso_close`, `vdso_fixup_features`, `vdso_setup_syscall_map`, `vdso_getcpu_init`, `vdso_setup_pages`, and `vdso_init`. It uses `vdso32_spec` and `vdso64_spec` `vm_special_mapping` objects, external `vdso32_start/end` and `vdso64_start/end`, and `vdso_k_arch_data`.

## Control Flow
At exec time, `arch_setup_additional_pages` locks the mm, clears the previous vDSO pointer, chooses 32-bit or 64-bit vDSO based on the task, reserves enough unmapped space for vvar plus aligned vDSO, installs vvar first, installs executable vDSO text, and records `mm->context.vdso`. At boot, `vdso_init` fills cache block sizes, builds syscall bitmaps, patches feature-dependent alternatives in embedded vDSOs, converts embedded vDSO pages to page lists, and publishes with an SMP write barrier.

## State And Persistence
Per-mm state is `mm->context.vdso`, updated on install, mremap, and close. Boot state includes vDSO page lists in `vdso*_spec.pages`, syscall maps, cache metadata, and on 64-bit the per-CPU SPRG value used by vDSO getcpu.

## Dependencies And Integration Points
Integrates with `binfmt_elf`, special mappings, generic vDSO data pages, PowerPC feature fixup machinery, syscall tables, CPU topology, PACA, and embedded vDSO images from `vdso32_wrapper.S` and `vdso64_wrapper.S`.

## Risks And Edge Cases
Mapping order and alignment matter for ABI stability and for `AT_SYSINFO_EHDR`. COW of vvar by ptrace can break live time updates for a process. mremap only accepts exact vDSO text size. Feature fixup symbol ranges must match linker script symbols, and getcpu only stores 16-bit CPU/node values.

## Test Signals
Useful signals include `gettimeofday`, `clock_gettime`, `clock_getres`, `time`, `getcpu`, `getrandom`, and signal trampoline tests in 32-bit and 64-bit tasks, `mremap`/`munmap` behavior, `/proc/self/maps` vvar/vdso placement, feature-fixup boot logs, and cross-builds with and without `CONFIG_VDSO32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/Makefile

## Purpose
Defines Kbuild rules for building PowerPC 32-bit and 64-bit vDSO shared objects, their C and assembly objects, linker scripts, generated offset headers, and vDSO validation.

## Important APIs, Types, And Functions
The file declares `obj-vdso32`, `obj-vdso64`, `targets`, `VDSOCC`, `CC32FLAGS`, `LD32FLAGS`, `AS32FLAGS`, `LD64FLAGS`, `AS64FLAGS`, `gen-vdso32sym`, `gen-vdso64sym`, and build commands `vdso32ld_and_check`, `vdso64ld_and_check`, `vdso32as`, `vdso32cc`, and `vdso64as`. It includes `lib/vdso/Makefile.include` for validation and generic C-vDSO inputs.

## Control Flow
Kbuild compiles assembly files twice with 32-bit and 64-bit defines, compiles C helpers with appropriate included generic vDSO sources, links `vdso32.so.dbg` and `vdso64.so.dbg` with explicit linker scripts, runs vDSO checks, and then uses `NM` plus generator scripts to create `include/generated/vdso{32,64}-offsets.h`.

## State And Persistence
State is build artifacts under the object tree: vDSO objects, `.so.dbg` files, linker scripts, and generated offset headers. There is no runtime state.

## Dependencies And Integration Points
Integrates PowerPC vDSO sources with generic vDSO C implementations, Kconfig flags, compiler/linker feature flags, `CROSS32_COMPILE`, LLD, orphan-section warnings, and wrappers that later embed the produced `.so.dbg` into the kernel image.

## Risks And Edge Cases
Flag filtering is fragile because kernel-wide 64-bit flags may be invalid for 32-bit vDSO builds. The fixed `r30` workaround preserves compatibility with older Go assumptions. Linker script ordering and generated offsets are ABI-sensitive. Missing `CROSS32_COMPILE` support can break 32-bit vDSO builds on some toolchains.

## Test Signals
Build `allyesconfig` and representative 32/64-bit PowerPC configs with GCC and Clang/LLD, verify `cmd_vdso_check`, inspect exported symbols with `readelf`, and ensure generated offset headers are stable across no-op rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/cacheflush.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/cacheflush.S

## Purpose
Provides the userspace vDSO routine `__kernel_sync_dicache`, which flushes data cache and invalidates instruction cache for a supplied address range.

## Important APIs, Types, And Functions
Exports vDSO function `__kernel_sync_dicache(start, end)`. It uses `get_datapage`, cache block-size fields from `vdso_u_arch_data` on 64-bit, and the `CPU_FTR_COHERENT_ICACHE` feature section.

## Control Flow
If the CPU has coherent I-cache, the function takes a short path with `sync`, one `icbi`, `isync`, and returns zero. Otherwise it rounds the start address down to a D-cache line boundary, computes line count, emits `dcbst` over the range, synchronizes, then invalidates I-cache lines with `icbi`, finishes with `isync`, clears SO, and returns zero.

## State And Persistence
It changes hardware cache state for the caller-provided range and has no persistent software state.

## Dependencies And Integration Points
Depends on cache metadata populated by `vdso_init`, PowerPC cache instructions, vDSO feature fixups, and user JIT/self-modifying-code callers that need instruction visibility without a syscall.

## Risks And Edge Cases
Range calculation must handle empty ranges, unaligned addresses, and dynamic 64-bit cache block sizes. Incorrect feature fixups or cache metadata can leave stale instructions visible. Users must provide a valid range; the code does not fault-probe addresses.

## Test Signals
JIT/self-modifying-code tests should write instructions, call `__kernel_sync_dicache`, and execute them. Build/runtime coverage should include coherent and noncoherent I-cache CPUs, 32-bit and 64-bit vDSOs, and unusual cache block sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/cacheflush.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/datapage.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/datapage.S

## Purpose
Provides vDSO accessors for the PowerPC vDSO architecture data page: available syscall bitmap and timebase frequency.

## Important APIs, Types, And Functions
Exports `__kernel_get_syscall_map(unsigned int *syscall_count)` and `__kernel_get_tbfreq(void)`. It uses `get_datapage`, `CFG_SYSCALL_MAP32`, `CFG_SYSCALL_MAP64`, `CFG_TB_TICKS_PER_SEC`, and `NR_syscalls`.

## Control Flow
`__kernel_get_syscall_map` loads the arch data page, returns a pointer to the 32-bit or 64-bit syscall map, and optionally stores `NR_syscalls` through the caller's pointer. `__kernel_get_tbfreq` returns the 64-bit timebase frequency, using `r3/r4` for 32-bit ABI return and `r3` for 64-bit.

## State And Persistence
Reads shared vDSO data populated by the kernel at boot and updated as needed. It does not modify state.

## Dependencies And Integration Points
Depends on `vdso_setup_syscall_map` in `vdso.c`, generic vDSO data placement, PowerPC ABI return conventions, and the linker scripts that export these functions.

## Risks And Edge Cases
The syscall bitmap ordering is big-bit-first within 32-bit words, unlike native kernel bitops. 32-bit callers rely on correct high/low return register handling for the timebase frequency.

## Test Signals
Userspace can compare the syscall map against known implemented syscalls and compare `__kernel_get_tbfreq` with kernel-exposed timebase frequency. ABI tests should run under 32-bit and 64-bit tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/datapage.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gen_vdso32_offsets.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gen_vdso32_offsets.sh

## Purpose
Generates C preprocessor defines for offsets of `VDSO_*` symbols in the 32-bit PowerPC vDSO shared object.

## Important APIs, Types, And Functions
The script reads `nm` output on stdin and emits lines of the form `#define vdso32_offset_<name> 0x<addr>` for matching `VDSO_` symbols.

## Control Flow
It sets `LC_ALL=C`, runs a `sed` script that normalizes leading zeroes and captures hex addresses whose symbol type is a single arbitrary `nm` field and whose name begins with `VDSO_`.

## State And Persistence
No internal state. Its output is redirected by the Makefile into `include/generated/vdso32-offsets.h`.

## Dependencies And Integration Points
Used by the vDSO Makefile after linking `vdso32.so.dbg`. The generated header lets kernel C code refer to embedded vDSO symbol offsets without parsing ELF at runtime.

## Risks And Edge Cases
The parser depends on `nm` formatting and symbol names. It intentionally lives outside the Makefile because embedding the sed logic there interferes with Kbuild filtering and rebuild behavior.

## Test Signals
Build tests should confirm `include/generated/vdso32-offsets.h` contains expected `vdso32_offset_sigtramp*` symbols and does not regenerate on no-op builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gen_vdso32_offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gen_vdso64_offsets.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gen_vdso64_offsets.sh

## Purpose
Generates C preprocessor defines for offsets of `VDSO_*` symbols in the 64-bit PowerPC vDSO shared object.

## Important APIs, Types, And Functions
The script reads `nm` output and emits `#define vdso64_offset_<name> 0x<addr>` for `VDSO_` symbols.

## Control Flow
It sets `LC_ALL=C` and applies the same symbol-matching `sed` transform as the 32-bit variant, with the output prefix changed to `vdso64_offset_`.

## State And Persistence
No internal state. The Makefile redirects output to `include/generated/vdso64-offsets.h`.

## Dependencies And Integration Points
Runs after `vdso64.so.dbg` is linked and provides offsets used by kernel code for embedded 64-bit vDSO symbols, especially signal trampoline entry points.

## Risks And Edge Cases
Depends on stable `nm` output and linker-script-provided `VDSO_*` symbols. Missing or renamed symbols would silently omit defines and fail later at compile time.

## Test Signals
Build coverage should verify generated `vdso64_offset_*` definitions, especially `vdso64_offset_sigtramp_rt64`, and ensure no spurious rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gen_vdso64_offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/getcpu.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/getcpu.S

## Purpose
Implements the vDSO `__kernel_getcpu` fast path for PowerPC, returning CPU and NUMA node without a syscall where supported.

## Important APIs, Types, And Functions
Exports `__kernel_getcpu(unsigned *cpu, unsigned *node)`. On 64-bit it reads `SPRN_SPRG_VDSO_READ`; on non-SMP builds it returns zero for both CPU and node.

## Control Flow
The 64-bit path reads a packed SPRG value where low 16 bits are CPU and the next 16 bits are node, stores each value only if the caller pointer is non-null, clears SO, and returns zero. The non-SMP fallback stores zeroes similarly.

## State And Persistence
Reads per-CPU SPRG state initialized by `vdso_getcpu_init` and maintained in PACA. It does not mutate state.

## Dependencies And Integration Points
Depends on `vdso.c` setting `SPRN_SPRG_VDSO_WRITE`, CPU-to-node topology, and linker scripts exporting `__kernel_getcpu` only for 64-bit or non-SMP 32-bit cases.

## Risks And Edge Cases
CPU and node values are truncated to 16 bits. The function is absent for SMP 32-bit, so userspace must handle symbol availability or fallback.

## Test Signals
Userspace `getcpu` tests should compare vDSO results with syscall results across CPUs and NUMA nodes, including null pointer arguments and task migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/getcpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/getrandom.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/getrandom.S

## Purpose
Provides the assembly vDSO wrapper for `__kernel_getrandom`, bridging PowerPC ABI details to the generic C vDSO getrandom implementation.

## Important APIs, Types, And Functions
Exports `__kernel_getrandom(buffer, len, flags, opaque_state, opaque_len)`. The `cvdso_call` macro builds caller and callee stack frames, saves LR and on 64-bit TOC `r2`, calls `__c_kernel_getrandom`, and converts negative errors to syscall-style return with SO set.

## Control Flow
The wrapper creates two minimum stack frames because vDSO callers are not required to have one, calls the C helper, restores LR/TOC, tears down both frames, returns nonnegative results directly, and returns positive errno with SO set for failures.

## State And Persistence
No private state. It reads/writes caller-provided buffer and opaque getrandom state through the C helper.

## Dependencies And Integration Points
Depends on the generic vDSO random implementation included by the Makefile, PowerPC ABI stack/TOC conventions, and `vgetrandom-chacha.S` for the architecture ChaCha20 block primitive.

## Risks And Edge Cases
Stack-frame correctness is ABI-critical, especially for callers without frames and 64-bit TOC preservation. Error conversion must match libc expectations for vDSO calls. The routine assumes the C helper handles validation and fallback.

## Test Signals
Run getrandom vDSO selftests for success, unsupported flags, short buffers, opaque state handling, signal safety, 32-bit and 64-bit ABIs, and forced fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/getrandom.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gettimeofday.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gettimeofday.S

## Purpose
Provides assembly wrappers for PowerPC vDSO time functions, calling generic C vDSO implementations while satisfying PowerPC stack, TOC, and error conventions.

## Important APIs, Types, And Functions
Exports `__kernel_gettimeofday`, `__kernel_clock_gettime`, `__kernel_clock_gettime64` on 32-bit, `__kernel_clock_getres`, `__kernel_clock_getres_time64` on 32-bit, and `__kernel_time`. The `cvdso_call` macro obtains `vdso_u_time_data`, saves LR and 64-bit TOC, and handles error conversion where needed.

## Control Flow
Each exported wrapper creates two minimum stack frames, passes the vDSO time data pointer in the correct argument register, calls its `__c_kernel_*` helper, restores saved registers, clears SO, and for integer-returning functions sets SO and negates negative error codes. `__kernel_time` uses a variant that does not treat the returned time value as an errno status.

## State And Persistence
Reads the kernel-updated vvar time data page and optionally writes caller-provided result structures. It does not persist software state.

## Dependencies And Integration Points
Depends on generic C vDSO time helpers included via the Makefile, PowerPC `get_datapage`, ABI-specific timespec layouts, and exported linker-script symbol versions used by libc.

## Risks And Edge Cases
The wrapper must preserve TOC and LR and provide unwind-safe CFI. 32-bit time64 and old 32-bit timespec variants must call the matching C helper. Error/SO behavior is part of userspace ABI.

## Test Signals
Run vDSO time selftests comparing against syscalls for supported clock ids, invalid clock ids, null result pointers, 32-bit compat time64 behavior, and ABI unwind through vDSO frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/gettimeofday.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/note.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/note.S

## Purpose
Adds ELF note sections to the PowerPC vDSO, including kernel version and build salt metadata.

## Important APIs, Types, And Functions
Defines `ASM_ELF_NOTE_BEGIN` and `ASM_ELF_NOTE_END` macros, emits `.note.kernel-version` with `LINUX_VERSION_CODE`, and includes `BUILD_SALT`.

## Control Flow
At assembly time the macros lay out a standard ELF note with aligned name, descriptor, and type fields. The linker scripts collect `.note.*` into a PT_NOTE segment.

## State And Persistence
The resulting metadata is embedded read-only in the vDSO ELF image and visible to userspace ELF readers.

## Dependencies And Integration Points
Depends on Linux version headers, build-salt support, and vDSO linker scripts that map `.note` into a read-only note program header.

## Risks And Edge Cases
Alignment and length fields must match ELF note format. Incorrect note layout can confuse tooling that inspects vDSO metadata.

## Test Signals
Use `readelf -n` on built `vdso32.so.dbg` and `vdso64.so.dbg` to verify kernel-version and build-salt notes parse correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/note.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/sigtramp32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/sigtramp32.S

## Purpose
Provides 32-bit PowerPC signal and realtime-signal return trampolines in the vDSO, plus `.eh_frame` unwind descriptions for signal frames.

## Important APIs, Types, And Functions
Exports `__kernel_sigtramp32` and `__kernel_sigtramp_rt32`. The trampolines issue `__NR_sigreturn` and `__NR_rt_sigreturn`. It defines DWARF helper macros `cfa_save`, `rsave`, `vsave_msr*`, `vsave`, `EH_FRAME_GEN`, `EH_FRAME_FP`, and `EH_FRAME_VMX`.

## Control Flow
Signal handlers return into the trampoline, which loads the proper syscall number in `r0` and executes `sc`. Preceding NOPs widen unwind coverage for tools that subtract one from return addresses. The `.eh_frame` section describes where GPRs, LR, CR, FP registers, and optional VMX registers can be found via the saved `pt_regs` pointer in the signal frame.

## State And Persistence
The trampoline itself has no mutable state. It relies on the kernel-created user signal frame and `pt_regs` layout.

## Dependencies And Integration Points
Depends on PowerPC 32-bit signal-frame layouts, syscall numbers, DWARF register numbering, optional `CONFIG_ALTIVEC`, vDSO linker exports `VDSO_sigtramp32` and `VDSO_sigtramp_rt32`, and libc/unwinder signal-frame recognition.

## Risks And Edge Cases
Unwind offsets are ABI-sensitive and differ between plain and realtime signal frames. VMX unwind expressions depend on MSR bits and saved VMX area layout. Any mismatch breaks debuggers, profilers, exception unwinders, and signal return.

## Test Signals
Run signal handling tests for 32-bit tasks, `sigreturn` and `rt_sigreturn`, GDB/libunwind backtraces through signal frames, Altivec register unwinding, and `readelf --debug-dump=frames` validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/sigtramp32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/sigtramp64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/sigtramp64.S

## Purpose
Provides the 64-bit PowerPC realtime signal trampoline in the vDSO and associated unwind metadata for signal frames.

## Important APIs, Types, And Functions
Exports `__kernel_start_sigtramp_rt64` and `__kernel_sigtramp_rt64`. The first calls the signal handler via `bctrl`; the second adjusts the stack by `__SIGNAL_FRAMESIZE`, invokes `__NR_rt_sigreturn`, and has `.eh_frame` metadata built from the same family of GPR, FP, and VMX DWARF expression macros as the 32-bit file.

## Control Flow
The kernel jumps to `__kernel_start_sigtramp_rt64`; the handler returns indirectly to `__kernel_sigtramp_rt64`, which performs the realtime signal-return syscall. Extra aligned words mimic the historical stack trampoline layout for older unwinders. The FDE describes register locations through a saved `pt_regs` pointer.

## State And Persistence
No mutable state. Runtime behavior depends on the signal frame constructed by the kernel and on userland returning through the prescribed trampoline.

## Dependencies And Integration Points
Depends on 64-bit PowerPC signal ABI, `__SIGNAL_FRAMESIZE`, syscall numbers, DWARF register numbering, optional Altivec save areas, and the linker script symbol `VDSO_sigtramp_rt64`.

## Risks And Edge Cases
The split trampoline entry is ABI-sensitive because libc uses `__kernel_sigtramp_rt64` as the return address for frame identification. Endian-specific CR offsets and VMX pointer indirection must match `pt_regs` and vector-save layouts.

## Test Signals
Signal tests in 64-bit tasks, unwinder/GDB backtraces through signal handlers, Altivec signal-frame unwind checks, and `readelf` verification of the FDE and exported trampoline symbols provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/sigtramp64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vdso32.lds.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vdso32.lds.S

## Purpose
Defines the linker script for the 32-bit PowerPC vDSO ELF shared object, including segment layout, exported symbols, feature-fixup sections, and trampoline offset symbols.

## Important APIs, Types, And Functions
Sets `OUTPUT_FORMAT` to `elf32-powerpc` or `elf32-powerpcle`, `OUTPUT_ARCH(powerpc:common)`, emits `VDSO_VVAR_SYMS`, defines fixup range symbols such as `VDSO_ftr_fixup_start/end`, and exports the vDSO versioned symbols. It defines `VDSO_sigtramp32` and `VDSO_sigtramp_rt32`.

## Control Flow
The linker lays out ELF headers, hash/dynamic symbol tables, notes, text, feature fixups, rodata, unwind data, dynamic sections, GOT/PLT, relocations, debug details, and discards writable/BSS/unsupported sections. PHDRS force a single read-execute PT_LOAD plus read-only dynamic, note, and EH frame headers.

## State And Persistence
Produces the static 32-bit vDSO image that is embedded into the kernel and mapped into userspace. No runtime state is defined here.

## Dependencies And Integration Points
Depends on generic linker macros, vDSO data-page symbols, build objects listed in the vDSO Makefile, and `gen_vdso32_offsets.sh` consuming `VDSO_*` symbols.

## Risks And Edge Cases
Exported symbols are user ABI. Section discard rules must prevent writable data in the vDSO. Fixup section boundaries must align with `vdso_fixup_features`. Program headers must remain compatible with dynamic loaders and vDSO validators.

## Test Signals
Build and inspect `vdso32.so.dbg` with `readelf -h -l -s -S`, validate one PT_LOAD with RX flags, confirm exported symbol versioning, generated offsets, and absence of writable alloc sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vdso32.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vdso64.lds.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vdso64.lds.S

## Purpose
Defines the linker script for the 64-bit PowerPC vDSO ELF shared object, including exported ABI symbols, feature-fixup sections, read-only segment layout, and signal trampoline offset symbol.

## Important APIs, Types, And Functions
Sets `OUTPUT_FORMAT` to `elf64-powerpc` or `elf64-powerpcle`, `OUTPUT_ARCH(powerpc:common64)`, declares fixup range symbols, exports vDSO functions under `VDSO_VERSION_STRING`, and defines `VDSO_sigtramp_rt64 = __kernel_start_sigtramp_rt64`.

## Control Flow
The linker places ELF metadata, notes, text including `.sfpr`, feature/MMU/lwsync/firmware fixup sections, rodata, dynamic data, unwind sections, relocations, GOT/TOC, debug details, and discards writable data, BSS, OPD, PLT/glink, and unsupported metadata. PHDRS force read-execute load and read-only dynamic/note/EH frame segments.

## State And Persistence
Produces the static 64-bit vDSO image embedded in the kernel and mapped into each 64-bit process.

## Dependencies And Integration Points
Depends on the vDSO Makefile, generic linker macros, `vdso.c` feature fixup ranges, 64-bit ABI TOC/GOT needs, and the offset generator for `VDSO_*` symbols.

## Risks And Edge Cases
The symbol export list and trampoline symbol are ABI-sensitive. Discarding OPD/PLT/glink must match the selected ABI and compiler output. Relocation and TOC placement must remain valid for the freestanding vDSO.

## Test Signals
Use `readelf` on `vdso64.so.dbg` to verify symbol versions, program headers, dynamic section, absence of writable alloc sections, and expected `VDSO_sigtramp_rt64` offset generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vdso64.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgetrandom-chacha.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgetrandom-chacha.S

## Purpose
Implements a stack-conscious PowerPC ChaCha20 block generator for the vDSO getrandom path.

## Important APIs, Types, And Functions
Exports `__arch_chacha20_blocks_nostack(dst_bytes, key, counter, nblocks)`. It defines register aliases for the key, counter, and 16-word state, plus `quarterround4` and `QUARTERROUND4` macros that perform four ChaCha quarter rounds in parallel.

## Control Flow
The function saves callee-saved registers, loads the 256-bit key and 64-bit counter, then for each 64-byte block initializes constants/key/counter/zero nonce, runs 10 double-round iterations, adds the original state, writes little-endian output (using byte-reversed stores on big-endian), increments the 64-bit counter, and loops. At the end it writes back the updated counter, clears key registers `r6-r12`, restores saved registers, and returns.

## State And Persistence
Mutates caller-provided output and counter memory. It has no static state. On 64-bit it saves registers below `r1` without moving the stack pointer, while 32-bit uses a small stack frame.

## Dependencies And Integration Points
Used by the generic vDSO getrandom implementation included by `vgetrandom.c`. Depends on PowerPC integer rotate/add/xor instructions, endian handling, and ABI register preservation.

## Risks And Edge Cases
The routine assumes a positive block count and valid pointers supplied by higher-level code. Register save/restore and 64-bit below-stack usage are ABI-sensitive. Key material clearing covers volatile key registers but does not erase output or caller state. Big-endian byte order must match ChaCha's little-endian block format.

## Test Signals
Known-answer ChaCha20 tests for 32-bit/64-bit and big/little endian, getrandom vDSO tests, KASAN/objtool-style checks where available, and stress tests around counter carry and multi-block output are valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgetrandom-chacha.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgetrandom.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgetrandom.c

## Purpose
Provides the PowerPC C wrapper that exposes generic vDSO getrandom logic to the assembly vDSO entry point.

## Important APIs, Types, And Functions
Defines `__c_kernel_getrandom(void *buffer, size_t len, unsigned int flags, void *opaque_state, size_t opaque_len)`, returning `ssize_t` from `__cvdso_getrandom`.

## Control Flow
The assembly wrapper calls this C helper with user arguments. The helper directly delegates to the generic vDSO getrandom implementation, which decides whether it can satisfy the request in userspace or must fall back.

## State And Persistence
No local state. The generic helper may read vvar random state and update caller-provided opaque state and output buffer.

## Dependencies And Integration Points
Depends on the generic getrandom implementation included by the vDSO Makefile and on `getrandom.S` for ABI framing and error conversion. The ChaCha20 primitive is supplied by `vgetrandom-chacha.S`.

## Risks And Edge Cases
This file is intentionally thin, so most risk is in included generic code and assembly ABI glue. The signature must remain exactly matched to the assembly caller and generic helper expectations.

## Test Signals
vDSO getrandom selftests for flags, buffer lengths, opaque-state sizes, fallback behavior, and 32-bit/64-bit ABI execution cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgetrandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgettimeofday.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgettimeofday.c

## Purpose
Provides PowerPC C wrappers around the generic vDSO time implementation for gettimeofday, clock_gettime, clock_getres, and time.

## Important APIs, Types, And Functions
Defines 64-bit `__c_kernel_clock_gettime` and `__c_kernel_clock_getres`, 32-bit `__c_kernel_clock_gettime`, `__c_kernel_clock_gettime64`, `__c_kernel_clock_getres`, `__c_kernel_clock_getres_time64`, plus common `__c_kernel_gettimeofday` and `__c_kernel_time`. They delegate to `__cvdso_*_data` helpers using a supplied `vdso_time_data` pointer.

## Control Flow
Assembly wrappers pass user arguments and a vvar time-data pointer. These C functions call the matching generic helper for ABI-specific result structures and return its status or value.

## State And Persistence
Reads vvar timekeeping data and writes user-provided result buffers. No local persistent state exists.

## Dependencies And Integration Points
Depends on generic vDSO time code included by the Makefile, PowerPC assembly wrappers in `gettimeofday.S`, and 32-bit versus 64-bit ABI type definitions.

## Risks And Edge Cases
Wrapper prototypes must match assembly call conventions and exported symbols. 32-bit time64 compatibility requires routing to the correct generic helper. Time correctness depends on vvar data consistency managed outside this file.

## Test Signals
Run vDSO time tests for all exported symbols, supported and unsupported clocks, 32-bit compat time64 cases, null pointers, timezone handling, and comparisons against syscalls under clock updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso32_wrapper.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso32_wrapper.S

## Purpose
Embeds the built 32-bit PowerPC vDSO shared object into the kernel image.

## Important APIs, Types, And Functions
Defines global symbols `vdso32_start` and `vdso32_end` in `.data..ro_after_init`, aligned to `PAGE_SIZE`, and includes `arch/powerpc/kernel/vdso/vdso32.so.dbg` with `.incbin`.

## Control Flow
At assembly/link time the vDSO binary is copied byte-for-byte into the kernel. Runtime code in `vdso.c` uses the start/end symbols to create page lists and map the image into userspace.

## State And Persistence
The embedded bytes become read-only-after-init kernel data. There is no active control flow in this file.

## Dependencies And Integration Points
Depends on the vDSO Makefile producing `vdso32.so.dbg`, page alignment, and `vdso.c` external symbol declarations.

## Risks And Edge Cases
The included file path must match the object tree layout. Incorrect alignment or missing end padding would break page-list construction and mapping size calculations.

## Test Signals
Build tests with `CONFIG_VDSO32`, symbol inspection for `vdso32_start/end`, and runtime 32-bit vDSO mapping tests validate this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso32_wrapper.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso64_wrapper.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso64_wrapper.S

## Purpose
Embeds the built 64-bit PowerPC vDSO shared object into the kernel image.

## Important APIs, Types, And Functions
Defines `vdso64_start` and `vdso64_end` in `.data..ro_after_init`, page-aligns both boundaries, and includes `arch/powerpc/kernel/vdso/vdso64.so.dbg`.

## Control Flow
The assembler includes the linked vDSO image into kernel data. `vdso.c` later converts the embedded range into pages for special mappings.

## State And Persistence
The embedded vDSO image is static kernel data that becomes read-only after init.

## Dependencies And Integration Points
Depends on `vdso64.so.dbg` build output, `PAGE_SIZE`, and runtime references from `vdso.c`.

## Risks And Edge Cases
Missing or stale included vDSO artifacts break the kernel build or map an outdated ABI image. Page alignment must be preserved for page-list mapping.

## Test Signals
Build tests for 64-bit PowerPC, symbol inspection for `vdso64_start/end`, and runtime vDSO function tests validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso64_wrapper.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vecemu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vecemu.c

## Purpose
Emulates selected AltiVec/VMX floating-point instructions that can trap, notably Java-mode denormal-sensitive operations and estimate/round/convert instructions.

## Important APIs, Types, And Functions
Exports `emulate_altivec(struct pt_regs *regs)`. Internal helpers implement approximate `eexp2`, `elog2`, signed/unsigned conversions `ctsxs` and `ctuxs`, and rounding helpers `rfiz`, `rfii`, and `rfin`. It calls assembly helpers from `vector.S`: `vaddfp`, `vsubfp`, `vmaddfp`, `vnmsubfp`, `vrefp`, and `vrsqrtefp`.

## Control Flow
The trap handler fetches the instruction at NIP, validates primary opcode 4, decodes vector register fields, and dispatches on minor opcode and `vc`. Arithmetic estimate instructions either call assembly routines using FP hardware or compute per-lane integer approximations in C. Conversion helpers update the VSCR saturation bit when needed. Unknown instructions return `-EINVAL`; fetch faults return `-EFAULT`; success leaves the result in `current->thread.vr_state`.

## State And Persistence
Mutates the current task's saved vector register state and VSCR. No global state is modified.

## Dependencies And Integration Points
Called from `altivec_assist_exception` in `traps.c` after `flush_altivec_to_thread`. Depends on PowerPC instruction fetch helpers, `current->thread.vr_state`, and FP-backed assembly helpers that must run with preemption disabled.

## Risks And Edge Cases
Floating-point approximation behavior must match architecture expectations closely enough for trapped instructions. NaN, infinity, denormal, saturation, endian layout, and VSCR updates are subtle. Unknown instructions only log and set non-Java behavior in the caller, which may hide unsupported cases.

## Test Signals
AltiVec instruction tests for `vaddfp`, `vsubfp`, `vmaddfp`, `vnmsubfp`, estimate, log/exp estimate, rounding, signed/unsigned conversion, NaN/Inf/denormal inputs, and VSCR saturation behavior are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vecemu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vector.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vector.S

## Purpose
Provides low-level PowerPC VMX/Altivec and VSX save/restore helpers plus FP-backed scalar implementations used by vector instruction emulation.

## Important APIs, Types, And Functions
Exports `load_vr_state`, `store_vr_state`, `load_up_altivec`, `save_altivec`, optional `load_up_vsx`, and vector arithmetic helpers `vaddfp`, `vsubfp`, `vmaddfp`, `vnmsubfp`, `vrefp`, and `vrsqrtefp`. Internal `fpenable` and `fpdisable` enable FP, save/restore FPSCR and scratch FP registers, and frame temporary state.

## Control Flow
Save/restore helpers move 32 vector registers and VSCR between hardware and thread memory. `load_up_altivec` enables MSR_VEC, sets VRSAVE if zero, marks thread state as loaded/used, restores saved vector state, and arranges return MSR bits. `load_up_vsx` ensures FP and vector facilities are loaded, marks VSX used, and returns through interrupt exit. Emulation helpers enable FP, loop over four single-precision lanes, compute results, store them into vector buffers, and restore FP/MSR state.

## State And Persistence
Mutates hardware vector/FP registers, MSR facility bits, VRSAVE, PACA interrupt-valid state, and per-task thread flags/register save areas. No durable storage is touched.

## Dependencies And Integration Points
Used by context switch, facility-unavailable handlers, and `vecemu.c`. Depends on `asm-offsets`, PACA/current layout, thread_struct offsets, MSR bits, FP/VMX instructions, and 32/64-bit ABI constraints.

## Risks And Edge Cases
This is register-state-critical assembly. 32-bit `load_up_altivec` can use only registers restored by fast exception return. VSX code is intentionally unavailable for 32-bit kernels. PACA SRR validity changes and RI-bit handling are important on Book3S. FP helper routines must preserve caller state and avoid preemption hazards.

## Test Signals
Context-switch tests with FP/Altivec/VSX users, signal save/restore tests, AltiVec emulation tests, kprobe exclusion checks, and stress tests with preemption/SMP should cover the behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vector.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vmlinux.lds.S

## Purpose
Defines the PowerPC kernel linker script, controlling section ordering, load addresses, program headers, special fixup tables, init/runtime boundaries, per-CPU layout, and discarded sections.

## Important APIs, Types, And Functions
Defines `ENTRY(_stext)`, PHDRS for text and note, architecture output, `jiffies` aliasing, macros `SOFT_MASK_TABLE` and `RESTART_TABLE`, strict RWX boundary symbols, feature-fixup sections, exception/bug/percpu/init/data/BSS sections, and exported boundary symbols such as `_stext`, `_etext`, `__init_begin`, `__init_end`, `_sdata`, `_edata`, and `_end`.

## Control Flow
At link time, fixed head text is placed first so exception vectors and trampolines remain at required offsets. Main text, read-only data, GOT/TOC/OPD, fixup tables, init text/data, runtime data, aligned data, bug tables, and BSS are then laid out with physical load addresses adjusted by `LOAD_OFFSET`. Relocatable builds keep dynamic symbol and relocation sections. Discards remove unsupported or unsafe sections.

## State And Persistence
This file shapes the kernel image rather than runtime logic. The resulting symbols drive boot, memory reservation, kexec, module/runtime patching, and init memory freeing.

## Dependencies And Integration Points
Depends on generic linker macros, PowerPC head/exception code, feature patching, speculative barrier fixups, percpu setup, init task layout, ftrace trampolines, sanitizers, relocatable-kernel support, and kexec exports such as `_end`.

## Risks And Edge Cases
Section placement is boot-critical. Head text must not receive random linker stubs. `CONFIG_DATA_SHIFT` must be at least page shift. Fixup table boundaries must align with runtime patching code. Discarding relocations or unwind data differs for relocatable and non-relocatable builds.

## Test Signals
Full kernel link success across 32/64-bit, Book3S/BookE, relocatable, sanitizer, and mitigation configs; `readelf`/`objdump` section checks; boot tests; feature-patching tests; and kexec tests that rely on `_end` and fixed head placement are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/watchdog.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/watchdog.c

## Purpose
Implements PowerPC hard-lockup watchdog support using per-CPU hrtimer heartbeats, soft-NMI self-detection, and SMP cross-CPU pending-mask detection.

## Important APIs, Types, And Functions
External hooks are `soft_nmi_interrupt`, `arch_touch_nmi_watchdog`, `watchdog_hardlockup_stop`, `watchdog_hardlockup_start`, `watchdog_hardlockup_probe`, and pseries `watchdog_hardlockup_set_timeout_pct`. Internal logic includes `wd_smp_lock`, `wd_try_report`, `wd_end_reporting`, `wd_lockup_ipi`, `watchdog_smp_panic`, `wd_smp_clear_cpu_pending`, `watchdog_timer_interrupt`, `watchdog_timer_fn`, `start_watchdog`, `stop_watchdog`, and `watchdog_calc_timeouts`.

## Control Flow
Each enabled CPU runs a pinned hrtimer heartbeat that updates its timestamp and clears its bit from the global pending mask. When all enabled non-stuck CPUs clear their bits, the last clearer resets the SMP timestamp and refills pending. Soft-NMI interrupts compare the local timebase against the local heartbeat and self-report hard lockups. The hrtimer path also checks whether the global SMP timestamp has expired and reports CPUs whose pending bits remain set, optionally sending NMI IPIs or all-CPU backtraces before panicking.

## State And Persistence
Global state includes enabled CPU masks, pending/stuck masks, watchdog timeouts in timebase ticks, reporting locks, NMI output flush flags, and pseries timeout percentage. Per-CPU state includes hrtimers and last heartbeat timebase values. No durable storage is used.

## Dependencies And Integration Points
Integrates with Linux lockup detector controls, CPU hotplug state, NMI/backtrace APIs, PowerPC timebase/DEC, PACA soft-NMI accounting, sys_info reporting, panic policy, and pseries timeout tuning.

## Risks And Edge Cases
Runs in soft-NMI and hardlockup contexts, so locking and printk are sensitive. Pending-mask races are handled with barriers; regressions can cause false positives or missed lockups. NMI printk requires a later console flush from another CPU. CPU hotplug and stuck/unstuck transitions are tricky.

## Test Signals
Hard-lockup injection with interrupts soft-disabled and hard-disabled, SMP stuck CPU tests, CPU hotplug start/stop tests, all-CPU backtrace and panic policy validation, pseries timeout-factor changes, and stress under heavy printk/NMI load are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/watchdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/Makefile

## Purpose
Selects PowerPC kexec, kexec-file, vmcore-info, and crash-dump objects for the kernel build and disables instrumentation on sensitive transition code.

## Important APIs, Types, And Functions
Uses Kbuild assignments for `core.o`, `core_$(BITS).o`, `ranges.o`, `relocate_32.o`, `file_load.o`, `file_load_$(BITS).o`, `elf_$(BITS).o`, `vmcore_info.o`, and `crash.o`. It disables GCOV, KCOV, UBSAN, and KASAN instrumentation for selected core objects.

## Control Flow
Kbuild evaluates `CONFIG_PPC32`, `CONFIG_KEXEC_FILE`, `CONFIG_VMCORE_INFO`, and `CONFIG_CRASH_DUMP` to include the correct objects for the selected architecture width and feature set.

## State And Persistence
No runtime state. It controls build artifacts and instrumentation flags.

## Dependencies And Integration Points
Integrates PowerPC architecture kexec code with generic kexec, crash dump, and vmcore infrastructure. Instrumentation disables are important because kexec transition code runs with unusual MMU/IRQ/stack constraints.

## Risks And Edge Cases
Omitting an object causes unresolved symbols or missing runtime support. Accidentally enabling sanitizers or coverage in transition code can break no-allocation/no-instrumentation assumptions during kexec.

## Test Signals
Build matrices for 32-bit, 64-bit, `CONFIG_KEXEC_FILE`, `CONFIG_CRASH_DUMP`, and sanitizer configs verify object selection and instrumentation exclusions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/core.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/core.c

## Purpose
Provides generic PowerPC kexec entry points, crashkernel reservation, and device-tree properties consumed by userspace and the next kernel.

## Important APIs, Types, And Functions
Defines `machine_crash_shutdown`, `machine_kexec_cleanup`, `machine_kexec`, `arch_reserve_crashkernel`, `kdump_cma_reserve`, `overlaps_crashkernel`, and `kexec_setup`. Internal helpers include `get_crash_base` and `export_crashk_values`.

## Control Flow
`machine_kexec` disables ftrace on the current CPU, calls the platform `machine_kexec` hook or `default_machine_kexec`, restores ftrace if it unexpectedly returns, and falls back to `machine_restart`. Crashkernel reservation parses `crashkernel=`, chooses or aligns a base, rejects overlap with the running kernel, and reserves memory through generic crashkernel helpers. Late init updates `/chosen` with `linux,kernel-end`, crashkernel base/size, and memory limit.

## State And Persistence
Persists crashkernel reservation in resource state, optional crash CMA size, and Open Firmware `/chosen` properties. No data files are written.

## Dependencies And Integration Points
Depends on generic kexec, memblock, ftrace, platform machine descriptors, fadump/kdump, Open Firmware device tree APIs, firmware features, and architecture constants such as `KDUMP_KERNELBASE`.

## Risks And Edge Cases
Crashkernel placement must avoid the running kernel and meet platform expectations, especially nonstatic kernels and LPAR RMA limits. `machine_kexec` is point-of-no-return code and must not allocate or fail. Device-tree property endianness differs by word size.

## Test Signals
Boot with multiple `crashkernel=` forms, inspect `/proc/device-tree/chosen` properties, verify overlap rejection, run normal kexec and crash kexec, and test LPAR/non-LPAR placement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/core_32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/core_32.c

## Purpose
Implements the default 32-bit PowerPC machine kexec handoff by copying relocation code to the control page and jumping to it with interrupts masked.

## Important APIs, Types, And Functions
Defines `default_machine_kexec(struct kimage *image)` and `machine_kexec_prepare(struct kimage *image)`. Uses `relocate_new_kernel`, `relocate_new_kernel_size`, and function pointer type `relocate_new_kernel_t`.

## Control Flow
The default handoff disables local IRQs, masks interrupt sources, locates the image indirection list and control code page, copies relocation code into the control page, flushes I-cache over that page, prints "Bye!", and jumps either directly to the original relocation symbol on most systems or through the copied control page on 85xx/44x. `machine_kexec_prepare` accepts all images.

## State And Persistence
Mutates the control code page and hardware interrupt state. It does not persist data.

## Dependencies And Integration Points
Depends on generic `struct kimage`, interrupt masking, cache flushing, physical/virtual address helpers, and `relocate_32.S`.

## Risks And Edge Cases
This path runs after reboot commitment. The relocation code size must fit in the control page, I-cache flushing must cover the copied code, and effective versus physical addresses must be correct for the target platform.

## Test Signals
32-bit kexec boot tests, crash-dump handoff where applicable, cache coherency checks around copied relocation code, and board coverage for 85xx/44x versus other PPC32 platforms are needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/core_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/core_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/core_64.c

## Purpose
Implements 64-bit PowerPC kexec preparation, CPU shutdown coordination, MMU-sensitive image copying, static stack/PACA handoff, hash table export, and CPU-node FDT updates.

## Important APIs, Types, And Functions
Defines `machine_kexec_prepare`, `kexec_copy_flush`, `default_machine_kexec`, and `update_cpus_node`. Internal pieces include `copy_segments`, SMP helpers `kexec_smp_down`, `kexec_prepare_cpus_wait`, `wake_offline_cpus`, `kexec_prepare_cpus`, static `kexec_stack`, static `kexec_paca`, `export_htab_values`, and `add_node_props`.

## Control Flow
Preparation rejects segments that overwrite static kernel memory or TCE tables. The transition path stops or wakes CPUs as needed, disables IRQs, waits for all CPUs to enter real mode, optionally disables pseries relocation-on-exception, switches to a static stack and copied PACA, unshares secure guest pages for normal kexec, chooses whether to copy with MMU off, and enters assembly `kexec_sequence`. `kexec_copy_flush` copies indirection-listed pages with MMU off and flushes I-cache for destination ranges.

## State And Persistence
Mutates PACA kexec states, CPU online state, interrupt state, static kexec stack/PACA, Open Firmware `/chosen` htab properties, and FDT CPU nodes. No filesystem persistence occurs.

## Dependencies And Integration Points
Integrates with generic kexec, SMP/hotplug, pseries/powernv firmware hooks, hash/radix MMU state, secure VM ultravisor sharing, hardware breakpoints, libfdt, and the assembly `kexec_sequence` in `misc_64.S`.

## Risks And Edge Cases
CPU rendezvous and real-mode entry are fragile, especially with offline CPUs, SMT state, and crash versus normal kexec. Copying with MMU off is necessary on radix/non-LPAR to avoid overwriting page tables. Switching PACA and stack invalidates many normal kernel assumptions. Segment overlap checks must catch TCE/static memory collisions.

## Test Signals
Normal kexec on radix and hash MMU, LPAR and bare metal, secure guest kexec, CPU hotplug/offline CPU cases, SMT-disabled systems, TCE table overlap rejection, and FDT CPU-node validation are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/core_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/crash.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/crash.c

## Purpose
Implements PowerPC crash-kexec CPU stopping, crash shutdown handler registration, crash CPU state saving, backup-region ELF synchronization, and crash hotplug updates.

## Important APIs, Types, And Functions
Defines `crash_ipi_callback`, `crash_kexec_secondary`, `crash_kexec_prepare`, `crash_shutdown_register`, `crash_shutdown_unregister`, `default_machine_crash_shutdown`, `sync_backup_region_phdr`, `machine_kexec_post_load`, `arch_crash_get_elfcorehdr_size`, `arch_crash_hotplug_support`, and `arch_crash_handle_hotplug_event`. Internal helpers include `handle_fault`, `crash_kexec_prepare_cpus`, `crash_kexec_wait_realmode`, `update_crash_elfcorehdr`, `get_fdt_index`, and `update_crash_fdt`.

## Control Flow
On crash, the crashing CPU disables hard IRQs, records `crashing_cpu`, and tries to stop other CPUs through IPIs or system-reset rendezvous. Secondaries save their registers once, increment `cpus_in_crash`, wait for `time_to_dump`, call platform CPU-down hooks, and park. The primary saves CPU state, marks dumping ready, waits for real mode, masks interrupts, runs registered crash shutdown handlers under a setjmp/longjmp fault guard, and calls platform CPU-down hooks. Hotplug support can rebuild the crash ELF core header or refresh CPU nodes in the crash FDT while temporarily invalidating `kexec_crash_image`.

## State And Persistence
State includes `time_to_dump`, `is_via_system_reset`, `crash_wake_offline`, crash shutdown handler slots, fault-recovery jump buffer, `crash_shutdown_cpu`, `cpus_in_crash`, saved per-CPU crash notes, backup region offsets, and live crash image segment contents.

## Dependencies And Integration Points
Integrates with generic crash kexec, PowerPC debugger fault hooks, SMP IPIs, platform `kexec_cpu_down`, ELF core header generation, memory/CPU hotplug, libfdt, and `update_cpus_node` from `core_64.c`.

## Risks And Edge Cases
Crash code runs after the kernel may be corrupt. CPUs may not respond to IPIs, so system reset fallback and timeouts matter. Shutdown handlers can fault and are bounded to three entries. Hotplug rewriting of live crash segments must avoid exposing a partially updated image.

## Test Signals
Crash dump end-to-end tests, nonresponsive CPU scenarios, system-reset crash entry, registered shutdown handler fault injection, backup-region offset checks, CPU add/remove crash hotplug, memory add/remove crash hotplug, and vmcore readability are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/crash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/elf_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/elf_64.c

## Purpose
Implements the 64-bit PowerPC ELF kernel loader for the `kexec_file_load` syscall.

## Important APIs, Types, And Functions
Defines static `elf64_load` and exports `kexec_elf64_ops` with `.probe = kexec_elf_probe` and `.load = elf64_load`.

## Control Flow
The loader parses ELF metadata, adjusts buffer placement for crash kernels, loads kernel segments, loads purgatory, adds crashdump segments and dm-crypt keys for kdump, prepends `elfcorehdr=` to the kdump command line, loads initrd if present, allocates and prepares an FDT with extra room, applies PowerPC FDT updates, optionally packs the FDT, adds it as a segment, stores it for cleanup, and initializes purgatory symbols with kernel/FDT addresses and slave code.

## State And Persistence
Mutates `struct kimage` segment arrays and architecture fields including `image->arch.fdt`, `elf_load_addr`, backup/elf headers via helpers, and purgatory symbol storage. Allocated FDT and command-line buffers are freed on cleanup or error.

## Dependencies And Integration Points
Depends on generic ELF kexec loading, purgatory loading, crashdump segment helpers, dm-crypt crash key loading, reserved memory range discovery, Open Firmware FDT setup, and `setup_new_fdt_ppc64`.

## Risks And Edge Cases
Kdump buffer ranges must stay within crashkernel/RMA constraints. FDT ownership is transferred only after segment addition; error paths must free correctly. Crash hotplug may require leaving FDT unpacked. Slave code assumes the first ELF program header contains the first 0x100 bytes.

## Test Signals
`kexec_file_load` tests with ELF kernels, initrd and no-initrd, kdump images, dm-crypt key capture, FDT inspection, error injection for segment placement, and cleanup leak checks are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/elf_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/file_load.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/file_load.c

## Purpose
Provides common PowerPC helpers for `kexec_file_load`, covering kdump command-line construction and purgatory symbol initialization.

## Important APIs, Types, And Functions
Defines `setup_kdump_cmdline` and `setup_purgatory`. Uses `SLAVE_CODE_SIZE` for the first 0x100 bytes copied into purgatory and generic `kexec_purgatory_get_set_symbol`.

## Control Flow
`setup_kdump_cmdline` allocates a command-line buffer, prepends `elfcorehdr=0x<addr> `, validates the combined length against `COMMAND_LINE_SIZE`, copies the existing command line, and NUL terminates. `setup_purgatory` reads the current purgatory start buffer to preserve the master entry word, copies slave code from the new kernel into purgatory, restores the master entry, writes the buffer back, and sets `kernel` and `dt_offset` purgatory symbols.

## State And Persistence
Mutates allocated command-line memory and purgatory symbol storage embedded in the kexec image. No durable storage is used.

## Dependencies And Integration Points
Used by `elf_64.c` and `file_load_64.c`. Depends on generic kexec purgatory APIs, PowerPC boot convention for slave code, and `image->elf_load_addr`.

## Risks And Edge Cases
Command-line length checking must include the added `elfcorehdr` prefix. Purgatory setup assumes the first word of `purgatory_start` is the master entry and must be preserved while replacing slave code.

## Test Signals
Kdump command-line tests for boundary lengths and purgatory symbol inspection after `kexec_file_load` provide coverage. End-to-end file-based kexec verifies the kernel and FDT addresses reach purgatory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/file_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/file_load_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kexec/file_load_64.c

## Purpose
Implements 64-bit PowerPC architecture support for `kexec_file_load`: loader registration, excluded ranges, crashdump segments, purgatory symbols, FDT sizing and mutation, usable-memory restrictions, PCI DMA node updates, and cleanup.

## Important APIs, Types, And Functions
Defines `kexec_file_loaders`, `arch_check_excluded_range`, `load_crashdump_segments_ppc64`, `setup_purgatory_ppc64`, `kexec_extra_fdt_size_ppc64`, `setup_new_fdt_ppc64`, `arch_kexec_kernel_image_probe`, and `arch_kimage_file_post_load_cleanup`. Internal helpers manage `struct umem_info`, usable-memory buffers, dynamic reconfiguration memory, backup segments, elfcorehdr segments, CPU node sizing, property copying, and PCI DMA properties.

## Control Flow
Image probing first gathers excluded memory ranges and delegates to generic loader probing. For kdump, helpers allocate a dummy backup segment for the first 64K, build an ELF core header segment with optional hotplug headroom, and add usable-memory properties to memory nodes and dynamic LMBs so the capture kernel uses only crashkernel memory. FDT setup updates CPU nodes, direct/DMA64 PCI window properties for LPAR, memory reserve map entries, backup reservations, crash usable-memory restrictions, and PLPKS password data. Purgatory setup calls the common helper, sets `run_at_load` for crash kernels, writes backup/OPAL symbols, and reports errors.

## State And Persistence
Mutates `struct kimage` architecture fields: exclude ranges, backup buffer/start, ELF headers, FDT pointer, and purgatory symbols. It also mutates the loaded FDT blob by adding properties and reservations. Cleanup frees all architecture allocations and delegates to generic cleanup.

## Dependencies And Integration Points
Depends on generic kexec-file loaders, crash memory range helpers, libfdt, Open Firmware live tree, DRMEM/LMB APIs, pseries firmware features, IOMMU PCI DMA properties, PLPKS, OPAL device-tree properties, and common helpers in `file_load.c`.

## Risks And Edge Cases
Usable-memory property construction must correctly intersect crash ranges with memory nodes and dynamic LMBs; existing `linux,drconf-usable-memory` rejects kdump load. FDT extra-size estimation must cover hotplug CPU nodes, usable-memory data, reserved ranges, and PLPKS data. Backup/elfcorehdr segment ownership and cleanup must avoid leaks. LPAR PCI DMA properties must match live firmware state.

## Test Signals
`kexec_file_load` and kdump tests with static and dynamic memory, LPAR PCI devices, OPAL systems, PLPKS availability, CPU hotplug, memory hotplug, crashkernel ranges, FDT inspection, excluded-range placement failures, and cleanup paths should cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kexec/file_load_64.c -->
