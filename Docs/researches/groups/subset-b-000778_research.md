# Research: subset-b-000778

This grouped report covers the requested PowerPC Open Firmware, ptrace, relocation, rethook, and RTAS source files. Each source-tree-aligned section is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_init.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_init.c

## Purpose
`prom_init.c` is the early PowerPC Open Firmware bridge that runs before the normal kernel mapping and runtime services are available. Its job is to talk to the firmware while firmware calls are still safe, discover boot-time platform state, claim and reserve early memory, instantiate RTAS/SML/TCE resources, fix known firmware device-tree defects, flatten the Open Firmware tree into the boot parameter format, quiesce firmware, and tail-call `__start()` with the flattened device tree and kernel base.

## Important APIs, Types, And Functions
Key local types are `struct prom_args` for 32-bit OF client-interface calls, `struct prom_t` for handles to `/chosen`, root, stdout, MMU, and memory packages, `struct mem_map_entry` for the reserve map copied into the flattened tree, and pSeries option-vector structures used by `ibm,client-architecture-support`. `call_prom()` and `call_prom_ret()` are the central firmware-call gateways; all OF services go through them and `enter_prom()`. `prom_init()` is the only exported entry in this file and orchestrates the complete handoff. Other important helpers include `early_cmdline_parse()`, `prom_send_capabilities()`, `prom_init_mem()`, `alloc_up()`, `alloc_down()`, `prom_instantiate_rtas()`, `prom_initialize_tce_table()`, `prom_hold_cpus()`, `fixup_device_tree()`, and `flatten_device_tree()`.

## Control Flow
`prom_init()` first relocates 32-bit GOT state if needed, clears BSS, initializes OF service handles, applies old-firmware MMU workarounds, opens stdout, identifies the platform, checks initrd arguments, parses boot options, and optionally sends pSeries capability vectors. It then copies the low-memory secondary CPU holding code, scans memory nodes to configure the early allocator, finds the boot CPU, opens displays, creates pSeries TCE tables, instantiates RTAS and SML, holds secondary CPUs, publishes selected boot properties under `/chosen`, applies device-tree fixups, flattens the tree, closes stdin on non-PowerMac systems, calls `quiesce`, optionally enters secure guest mode, and finally calls `__start(hdr, kbase, 0, ...)`.

## State And Persistence
The file relies on `.bss.prominit` globals because ordinary kernel services are not live. Persistent boot state written for the later kernel includes `/chosen/linux,stdout-path`, initrd start/end, memory limit, IOMMU flags, TCE allocation bounds, RTAS base/entry, SML base/size, `linux,boot-display`, and the flattened device-tree reserve map. Allocator state is held in `alloc_bottom`, `alloc_top`, `alloc_top_high`, `rmo_top`, and `ram_top`; reserve state is bounded by `MEM_RESERVE_MAP_SIZE`.

## Dependencies And Integration Points
This code integrates with Open Firmware client services, pSeries PAPR capability negotiation, platform-specific device-tree quirks, low-level relocation helpers, secondary CPU holding code, RTAS, SML/vTPM firmware methods, IOMMU/TCE firmware calls, the flattened device-tree format, and secure virtual machine ultravisor calls. It deliberately avoids normal kernel library dependencies and uses local string/parse/print helpers to avoid relocation and external-symbol hazards.

## Risks
The riskiest areas are external symbol creep, firmware calls after mappings become unsafe, allocator overlap with kernel/initrd/TCE/RTAS/device-tree memory, incomplete reserve-map accounting, bad endian or cell-size handling while scanning memory and device-tree properties, and stale platform workarounds. Device-tree fixups mutate firmware state by path and can be brittle if firmware layouts vary. Secure guest setup temporarily relocates the kernel back and forth around the ultracall, so relocation correctness is critical.

## Test Signals
Strong build-time signals include `prom_init_check.sh`, link success under PPC32/PPC64 and BE/LE configurations, and `BUILD_BUG_ON`/configuration coverage in dependent assembly and headers. Runtime signals include early console output, correct `/chosen` properties, successful RTAS/SML/TCE reservations, stable secondary CPU bring-up, boot with `mem=`, `iommu=`, `disable_radix`, `xive=off`, and `svm=` options, and successful boot on pSeries, PowerMac, CHRP/Pegasos, Efika, and PA-Semi/Nemo firmware variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_init_check.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_init_check.sh

## Purpose
This build-time shell validator protects `prom_init.o` from accidentally referencing ordinary kernel symbols or storing data in sections that are unsafe for early Open Firmware execution.

## Important APIs, Types, And Functions
The script accepts `NM` and `OBJ` as positional arguments. `has_renamed_memintrinsics()` checks Kconfig for KASAN configurations where memory intrinsic names are prefixed. `WHITELIST` enumerates permitted undefined symbols such as relocation helpers, low-memory CPU hold labels, `__start`, minimal memory functions, banner/logo/display hooks, and `relocate`. `check_section()` uses `objdump -h -j` to require `.data`, `.bss`, and `.init.data` to be empty in the object.

## Control Flow
The script derives allowed memory-function names from `KCONFIG_CONFIG`, iterates undefined symbols from `$NM -u "$OBJ"`, strips leading function-descriptor dots, optionally logs each symbol when verbose, matches against the whitelist, separately accepts compiler register save/restore helpers, and emits errors for anything else. It then checks forbidden sections and exits with accumulated error status.

## State And Persistence
No persistent repository state is changed. `ERROR` is process-local and controls the exit code.

## Dependencies And Integration Points
It is intended for the PowerPC kernel build and depends on `nm`, `objdump`, `awk`, `grep`, `KCONFIG_CONFIG`, and `KBUILD_VERBOSE`. It directly enforces the isolation assumptions of `prom_init.c`.

## Risks
The whitelist must evolve with real early-boot dependencies; too broad a whitelist weakens isolation, while missing legitimate compiler helper names breaks valid builds. Numeric section-size parsing assumes `objdump` format and shell arithmetic can interpret the hexadecimal section size.

## Test Signals
A passing build shows no forbidden undefined symbols and empty forbidden sections. Negative tests are easy: add a normal kernel call or initialized global to `prom_init.c` and verify the script fails with a clear diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_init_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_parse.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_parse.c

## Purpose
This file provides a small helper for decoding Open Firmware DMA window properties into bus number, physical address, and size values.

## Important APIs, Types, And Functions
`of_parse_dma_window(struct device_node *dn, const __be32 *dma_window, unsigned long *busno, unsigned long *phys, unsigned long *size)` is the sole function. It uses `of_read_number()`, `of_get_property()`, `of_n_addr_cells()`, and `of_n_size_cells()`.

## Control Flow
The parser reads the first cell as `busno`, then determines the number of DMA address cells from `ibm,#dma-address-cells`, falling back to `#address-cells` and finally the node default. It reads the physical address, advances by that cell count, determines the DMA size cell count from `ibm,#dma-size-cells` or the normal size-cell default, and reads the size.

## State And Persistence
The function has no static state. It writes only through caller-provided output pointers.

## Dependencies And Integration Points
It integrates with OF/device-tree PCI and DMA code that consumes IBM DMA window properties. The includes indicate use alongside resource and Ethernet/Open Firmware address helpers, though this file itself only needs the OF cell-parsing path.

## Risks
The function trusts that `dma_window` contains enough cells for the chosen address and size widths. Incorrect cell-count properties or a malformed property can cause wrong decoding by the caller.

## Test Signals
Useful tests include device-tree fixtures with IBM-specific cell-count properties, generic `#address-cells`/`#size-cells` fallback, one-cell and two-cell addresses, and big-endian cell values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/prom_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/Makefile

## Purpose
This Makefile composes the PowerPC ptrace implementation from core, compatibility, feature-specific regset, and debug-breakpoint source files.

## Important APIs, Types, And Functions
It sets `CFLAGS_ptrace-view.o += -DUTS_MACHINE='"$(UTS_MACHINE)"'` so `ptrace-view.c` can name the native user regset view. It always builds `ptrace.o`, `ptrace-view.o`, and `ptrace-fpu.o`; conditionally builds `ptrace32.o`, `ptrace-vsx.o`, `ptrace-altivec.o`, `ptrace-spe.o`, `ptrace-tm.o`, and `ptrace-adv.o`; and builds `ptrace-novsx.o` or `ptrace-noadv.o` as fallback implementations when the matching feature is absent.

## Control Flow
Kernel Kbuild evaluates `obj-y`, `obj-$(CONFIG_*)`, and `ifneq` clauses to select the correct object set for the target configuration.

## State And Persistence
There is no runtime state. The persistent effect is the build graph and the compile-time definition of `UTS_MACHINE` for native regset metadata.

## Dependencies And Integration Points
The Makefile gates C definitions declared in `ptrace-decl.h`; exactly one FPR regset provider (`ptrace-vsx.c` or `ptrace-novsx.c`) and exactly one advanced-debug provider (`ptrace-adv.c` or `ptrace-noadv.c`) should be linked.

## Risks
Incorrect conditionals can produce duplicate symbols or missing symbols for declarations shared by `ptrace-decl.h`. Configuration combinations such as VSX without Altivec or PPC32 with VSX are constrained elsewhere and need build coverage.

## Test Signals
Build matrices should cover native PPC32, PPC64 with compat, VSX and non-VSX, Altivec, SPE, transactional memory, advanced debug registers, and generic hardware breakpoint configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-adv.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-adv.c

## Purpose
`ptrace-adv.c` implements ptrace stepping and hardware debug support for PowerPC targets with advanced debug registers (`CONFIG_PPC_ADV_DEBUG_REGS`).

## Important APIs, Types, And Functions
It exports `user_enable_single_step()`, `user_enable_block_step()`, `user_disable_single_step()`, `ppc_gethwdinfo()`, `ptrace_get_debugreg()`, `ptrace_set_debugreg()`, `ppc_set_hwdebug()`, and `ppc_del_hwdebug()`. Internal helpers allocate and remove instruction address comparators (`set_instruction_bp()`, `del_instruction_bp()`), data address comparators (`set_dac()`, `del_dac()`), and optional DAC range mode (`set_dac_range()`).

## Control Flow
Single-step/block-step toggles DBCR0 instruction-complete or branch-taken bits and enables MSR_DE. Legacy debugreg access exposes DAC1 only. `ppc_set_hwdebug()` validates ABI version, trigger, address, mode, and condition fields, then routes execute breakpoints to IAC setup and read/write breakpoints to DAC exact or range setup. `ppc_del_hwdebug()` decodes the returned slot number and clears related DBCR, IAC, DAC, DVC, and range-mode state; if no debug events remain it clears DBCR0_IDM and MSR_DE.

## State And Persistence
All persistent debug state lives in `task->thread.debug` and `task->thread.regs->msr`; ptrace flags are stored via `TIF_SINGLESTEP`. Slot numbers returned to userspace are stable handles for later deletion.

## Dependencies And Integration Points
The file depends on BookE/embedded debug register macros such as DBCR0, DBCR1, DBCR2, IAC, DAC, and DVC helpers, plus the generic ptrace request path in `ptrace.c`. It is selected instead of `ptrace-noadv.c`.

## Risks
Slot-pair allocation for ranges is subtle: deleting the second half of a range is invalid, and exact breakpoints try to preserve pairs for future ranges. Address validation must prevent kernel-space traps. MSR_DE must stay enabled while any debug event is active and disabled only when all events are gone.

## Test Signals
Exercise single step, block step, exact execute breakpoints, IAC inclusive/exclusive ranges, DAC read/write exact breakpoints, DAC ranges and masks where configured, DVC conditions, deletion by returned slot, invalid slot deletion, and address values at or above `TASK_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-adv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-altivec.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-altivec.c

## Purpose
This file exposes Altivec/VMX register state through the ptrace regset interface.

## Important APIs, Types, And Functions
It exports `vr_active()`, `vr_get()`, and `vr_set()`. The ABI buffer is 34 `vector128` slots: VR0-VR31, VSCR as the 33rd vector, and VRSAVE in the low word of the 34th vector.

## Control Flow
`vr_active()` flushes live Altivec state and returns the regset size only if the task used VMX. `vr_get()` flushes state, verifies `thread_vr_state` layout, writes 33 vectors from `target->thread.vr_state`, then writes a zero-padded vector containing `target->thread.vrsave`. `vr_set()` flushes state, copies incoming VR/VSCR data directly into `vr_state`, then optionally copies the VRSAVE vector and stores only its first word.

## State And Persistence
The persistent task fields are `thread.vr_state` and `thread.vrsave`; flushing reconciles live CPU registers with `thread_struct` before copying.

## Dependencies And Integration Points
It is wired into `native_regsets` and `compat_regsets` as `REGSET_VMX` under `CONFIG_ALTIVEC`, and shares layout macros from `ptrace-decl.h`.

## Risks
The userspace VRSAVE vector layout only uses one word, so endian/layout assumptions matter. Missing flushes would expose stale live vector state. VMX state also interacts with transactional memory checkpointed state in `ptrace-tm.c`.

## Test Signals
Regset get/set tests should verify all 32 VRs, VSCR placement, VRSAVE low-word semantics, active state before and after VMX use, native and compat views, and core dump note size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-altivec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-decl.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-decl.h

## Purpose
`ptrace-decl.h` is the internal contract for the split PowerPC ptrace implementation. It centralizes writeability limits, regset IDs, layout-offset helpers, and cross-file prototypes.

## Important APIs, Types, And Functions
Key macros include `MSR_DEBUGCHANGE`, `PT_MAX_PUT_REG`, `TVSO()`, `TFSO()`, and `TSO()`. `enum powerpc_regset` defines regset indexes for GPR, FPR, VMX, VSX, SPE, transactional memory checkpointed sets, PPR, DSCR, TAR, EBB, PMU, DEXCR, HASHKEYR, and PKEY depending on configuration. Prototypes cover FPR/VSX/Altivec/SPE accessors, GPR32 helpers, TM accessors, scalar register helpers, debug breakpoint handlers, and `user_ppc_native_view`.

## Control Flow
The header has no runtime flow, but its conditional declarations must match the Makefile-selected object files and the regset arrays in `ptrace-view.c`.

## State And Persistence
It stores no state. It defines which parts of `thread_struct`, `thread_fp_state`, and `thread_vr_state` other files are allowed to address.

## Dependencies And Integration Points
It depends on kernel regset definitions and PowerPC register constants. It is included by every C file in the ptrace subdirectory and is the binding between build-time feature selection and exported implementation symbols.

## Risks
Mismatched configuration guards can cause missing or duplicate symbols. Incorrect `PT_MAX_PUT_REG` or `MSR_DEBUGCHANGE` can accidentally allow userspace to modify privileged register bits. Regset enum ordering must remain consistent with array initialization in `ptrace-view.c`.

## Test Signals
Build coverage across feature matrices and `pt_regs_check()` failures are the main guardrails. Regset note ordering can also be validated through coredump and `PTRACE_GETREGSET` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-decl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-fpu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-fpu.c

## Purpose
This file implements legacy `PTRACE_PEEKUSR`/`PTRACE_POKEUSR` access to individual floating-point registers and FPSCR.

## Important APIs, Types, And Functions
It exports `ptrace_get_fpr()` and `ptrace_put_fpr()`. It uses `flush_fp_to_thread()`, `PT_FPR0`, `PT_FPSCR`, `TS_FPR()`, and `CONFIG_PPC_FPU_REGS`.

## Control Flow
Both functions reject indexes past `PT_FPSCR`. With FPU registers configured, they flush live FP state to `thread.fp_state`; register indexes before FPSCR read or write FPR words, with PPC32 treating the index as 32-bit words and non-PPC32 copying a native long from the selected FPR lane. The FPSCR index reads or writes `thread.fp_state.fpscr`. Without FPU registers, reads return zero and writes are ignored after validation.

## State And Persistence
State is persisted in `task->thread.fp_state`. There is no file-local state.

## Dependencies And Integration Points
The functions are called by `arch_ptrace()` and `compat_arch_ptrace()` for USER-area FPR access. Whole-regset FPR access is handled by `ptrace-vsx.c` or `ptrace-novsx.c`.

## Risks
The PPC32 word-index ABI differs from native 64-bit FPR layout and can break debuggers if changed. Missing flushes can expose stale FPU state. The code relies on PPC32 and VSX being incompatible, checked in `pt_regs_check()`.

## Test Signals
Tests should cover PEEK/POKE of FPR0, middle registers, FPSCR, out-of-range indexes, PPC32 word halves, and no-FPU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-noadv.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-noadv.c

## Purpose
`ptrace-noadv.c` provides stepping and data-breakpoint support for PowerPC systems without advanced debug registers.

## Important APIs, Types, And Functions
It exports the same API as `ptrace-adv.c`: stepping helpers, `ppc_gethwdinfo()`, debugreg get/set, `ppc_set_hwdebug()`, and `ppc_del_hwdebug()`. It uses generic hardware breakpoint facilities when `CONFIG_HAVE_HW_BREAKPOINT` is enabled and direct `thread.hw_brk[]` state otherwise.

## Control Flow
Single step and block step toggle `MSR_SE` and `MSR_BE`. Hardware-info reports available watchpoint slots and DAWR/ARCH_31 capabilities. `ptrace_set_debugreg()` maintains the legacy one-DABR interface, translating DABR flags into `arch_hw_breakpoint` state and registering/modifying/unregistering a single perf hardware breakpoint when supported. `ppc_set_hwdebug()` validates a read/write-only breakpoint, translates exact or inclusive range mode into a perf breakpoint length, finds a free slot, registers it, and returns a one-based handle. Without generic breakpoints it stores an exact hardware breakpoint in a free `hw_brk` slot. `ppc_del_hwdebug()` unregisters by handle or clears raw slot state.

## State And Persistence
Persistent task state is in `thread.hw_brk[]` and optionally `thread.ptrace_bps[]` perf events. Stepping state is in `regs->msr` and `TIF_SINGLESTEP`.

## Dependencies And Integration Points
The file integrates with `linux/hw_breakpoint.h`, arch breakpoint translation helpers, `ptrace_triggered`, `ppc_breakpoint_available()`, DAWR feature detection, and the generic ptrace command dispatcher.

## Risks
The legacy DABR ABI accepts low bits as flags and requires the translation bit when nonzero. Range length calculation for inclusive ranges depends on addr ordering and perf semantics. Mixed perf-event and raw `hw_brk` state must stay consistent for deletion and GET_DEBUGREG compatibility.

## Test Signals
Exercise legacy DABR set/clear/get, exact watchpoints, inclusive range watchpoints under perf hardware breakpoint support, unsupported range mode without perf support, slot exhaustion, deletion of empty slots, and stepping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-noadv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-novsx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-novsx.c

## Purpose
This file implements whole-FPR regset get/set for configurations without VSX.

## Important APIs, Types, And Functions
It exports `fpr_get()` and `fpr_set()`. It uses `struct thread_fp_state`, `flush_fp_to_thread()`, `membuf_write()`, `user_regset_copyin()`, and `empty_zero_page`.

## Control Flow
When FPU registers exist, both functions assert that `fpscr` follows `fpr[32]`, flush live FP state, and copy the contiguous 33-u64 FPR/FPSCR block out of or into `target->thread.fp_state`. Without FPU registers, get returns zeros and set succeeds without changing state.

## State And Persistence
The only persistent state touched is `thread.fp_state`.

## Dependencies And Integration Points
The Makefile builds this when `CONFIG_VSX` is not enabled. `ptrace-view.c` references these symbols for `REGSET_FPR` in native and compat views.

## Risks
The contiguous layout assumption is enforced by `BUILD_BUG_ON`; if the structure changes, this file must change with it. No-FPU behavior intentionally preserves ABI shape by returning zeros.

## Test Signals
Regset tests should verify FPR/FPSCR round trips, partial copy offsets, no-FPU zero behavior, and coredump PRFPREG note size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-novsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-spe.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-spe.c

## Purpose
This file exposes Signal Processing Engine register state through ptrace regsets.

## Important APIs, Types, And Functions
It exports `evr_active()`, `evr_get()`, and `evr_set()`. The userspace buffer contains 32 EVR upper halves, a 64-bit accumulator, and a 32-bit SPEFSCR.

## Control Flow
`evr_active()` flushes live SPE state and reports the regset only if used. `evr_get()` flushes and writes `thread.evr`, then a contiguous accumulator plus SPEFSCR block after a layout check. `evr_set()` flushes, copies EVRs, checks the accumulator/SPEFSCR adjacency, and copies the trailing state.

## State And Persistence
Persistent state is in `thread.evr`, `thread.acc`, and `thread.spefscr`.

## Dependencies And Integration Points
It is built under `CONFIG_SPE` and attached to `REGSET_SPE` in native and compat views. It depends on `flush_spe_to_thread()` from switch/state management.

## Risks
The ABI depends on `acc` immediately preceding `spefscr`; structure changes must preserve or update the regset copy path. SPE is configuration-specific, so build coverage can be sparse.

## Test Signals
Tests should cover active detection, full get/set round trips, partial writes across the EVR-to-ACC boundary, and absent-regset behavior when SPE is not configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-spe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-tm.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-tm.c

## Purpose
`ptrace-tm.c` exposes transactional-memory checkpointed register state and TM SPRs to ptrace and coredump regsets.

## Important APIs, Types, And Functions
The file exports `flush_tmregs_to_thread()`, active/get/set functions for checkpointed GPR (`tm_cgpr_*`), FPR (`tm_cfpr_*`), VMX (`tm_cvmx_*`), VSX (`tm_cvsx_*`), TM SPRs (`tm_spr_*`), checkpointed TAR/PPR/DSCR (`tm_tar_*`, `tm_ppr_*`, `tm_dscr_*`), and compat checkpointed GPR helpers (`tm_cgpr32_*`). Internal helpers sanitize checkpointed MSR and trap fields.

## Control Flow
Every active/get/set path first checks `CPU_FTR_TM`; checkpointed data paths additionally require `MSR_TM_ACTIVE(target->thread.regs->msr)`, except the TM SPR regset reports available registers whenever TM exists. `flush_tmregs_to_thread()` reclaims suspended current transactions or saves TM SPRs before exposing state. Getters flush TM/FP/Altivec/VSX state as needed, then copy checkpointed state with `membuf`. Setters copy through temporary buffers or field-by-field to keep special MSR/trap rules and ABI padding intact.

## State And Persistence
Persistent state lives in `thread.ckpt_regs`, `ckfp_state`, `ckvr_state`, `ckvrsave`, `tm_tfhar`, `tm_texasr`, `tm_tfiar`, `tm_tar`, `tm_ppr`, and `tm_dscr`. The code is not persistent across tasks beyond normal `thread_struct` scheduling state.

## Dependencies And Integration Points
It depends on PowerPC TM feature detection, `asm/tm.h`, transactional reclaim/save helpers, normal FP/Altivec/VSX flush paths, and common GPR32 helpers from `ptrace-view.c`. It fills the `REGSET_TM_*` entries declared in `ptrace-decl.h`.

## Risks
The main risk is exposing stale checkpointed state if live TM registers are not reclaimed or saved. Active-state checks depend on `thread.regs` and the MSR TM bits. The compat GPR32 helpers assume checkpointed GPR layout mirrors normal GPR layout. Partial copy paths must preserve unwriteable registers and padding.

## Test Signals
Useful signals include TM-enabled and TM-disabled builds, active and inactive transaction ptrace GETREGSET behavior, checkpointed GPR/FPR/VMX/VSX round trips, SPR note values after transaction abort/suspend paths, compat coredumps, and negative tests for `-ENODEV` and `-ENODATA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-tm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-view.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-view.c

## Purpose
`ptrace-view.c` defines the PowerPC user regset views, scalar register get/set policy, register-name lookup helpers, and 32-bit compat GPR conversion.

## Important APIs, Types, And Functions
It exports `regs_query_register_offset()`, `regs_query_register_name()`, `ptrace_get_reg()`, `ptrace_put_reg()`, `user_ppc_native_view`, and `task_user_regset_view()`. It also defines native and compat `struct user_regset` arrays. Important internal functions include `gpr_get()`, `gpr_set()`, `ppr_get/set`, `dscr_get/set`, `tar_get/set`, EBB/PMU/DEXCR/HASHKEYR/PKEY handlers, `gpr32_get_common()`, and `gpr32_set_common()`.

## Control Flow
Scalar register access validates `thread.regs`, special-cases MSR, trap, DSCR, and SOFTE, bounds indexes with `array_index_nospec`, and only permits writes up to `PT_MAX_PUT_REG` plus sanitized trap/MSR fields. Regset get/set paths copy `struct user_pt_regs` while substituting synthetic or sanitized fields. Native and compat arrays are initialized with feature-guarded entries, and `task_user_regset_view()` returns the compat view for 32-bit tasks under `CONFIG_COMPAT`.

## State And Persistence
The file reads and writes `thread.regs`, `thread.dscr`, `thread.dscr_inherit`, TAR, EBB, PMU, DEXCR, HASHKEYR, and AMR/IAMR state. It does not own persistence; it provides controlled ptrace/coredump access to task state.

## Dependencies And Integration Points
It integrates with the Linux regset core, ELF core note types, seccomp/ptrace syscall paths, pkeys, CPU feature flags, and feature-specific accessors from the sibling ptrace files. `UTS_MACHINE` comes from the Makefile for the native view name.

## Risks
This is ABI-sensitive code. Register ordering, note types, sizes, and compat conversions must not change casually. Writable MSR bits are intentionally restricted, SOFTE is forced to a benign value, PKEY writes are masked by UAMOR, and DEXCR HDEXCR is read-only. Mistakes can leak privileged state or break debuggers and coredump consumers.

## Test Signals
Signals include `PTRACE_GETREGS/SETREGS`, `PTRACE_GETREGSET/SETREGSET`, native and compat coredumps, register-name lookup tests, MSR/trap/DSCR write sanitization, PKEY AMR masking, CPU-feature-gated EBB/PMU/DEXCR/HASHKEYR availability, and `pt_regs_check()` build assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-view.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-vsx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-vsx.c

## Purpose
This file implements FPR regset access for VSX-capable builds and exposes the lower halves of the first 32 VSX registers.

## Important APIs, Types, And Functions
It exports `fpr_get()`, `fpr_set()`, `vsr_active()`, `vsr_get()`, and `vsr_set()`. It uses `TS_FPR()` and `TS_VSRLOWOFFSET` to address the correct FPR/VSX storage lanes.

## Control Flow
`fpr_get()` and `fpr_set()` flush FP state, copy the 32 FPRs and FPSCR through a temporary 33-u64 buffer, and then update thread state. `vsr_active()` flushes VSX state and reports availability only after VSX use. `vsr_get()` and `vsr_set()` flush TM, FP, Altivec, and VSX state, copy the lower VSX halves from `thread.fp_state.fpr[i][TS_VSRLOWOFFSET]`, and write back after successful copyin.

## State And Persistence
Persistent task state is `thread.fp_state.fpr`, `thread.fp_state.fpscr`, and the `used_vsr` activity flag.

## Dependencies And Integration Points
This file is built under `CONFIG_VSX` and provides both `REGSET_FPR` and `REGSET_VSX` functions referenced from `ptrace-view.c`. It must stay consistent with transactional checkpointed VSX handling in `ptrace-tm.c`.

## Risks
VSX overlays FPR and VMX architectural state, so flushing all related units before VSR access is important. Temporary buffers avoid partial-copy corruption; direct writes without that pattern would be risky. ABI comments clarify that callers need FP and VMX regsets in addition to VSX to reconstruct all VSX state.

## Test Signals
Tests should include FPR/FPSCR round trips on VSX kernels, VSR lower-half get/set, active state before and after VSX use, partial copy offsets, and interaction with VMX/FPR regsets in debugger and coredump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-vsx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace.c

## Purpose
`ptrace.c` is the top-level PowerPC ptrace request dispatcher and syscall tracing hook implementation.

## Important APIs, Types, And Functions
It exports `ptrace_disable()`, `arch_ptrace()`, `do_syscall_trace_enter()`, `do_syscall_trace_leave()`, and `pt_regs_check()`. It uses `ptrace_get_reg()`, `ptrace_put_reg()`, FPR helpers, debug helpers, `copy_regset_to_user()`, `copy_regset_from_user()`, audit hooks, seccomp, and syscall tracepoints.

## Control Flow
`arch_ptrace()` handles USER-area peek/poke, hardware debug information and breakpoint commands, debugreg get/set, whole GPR/FPR/VMX/VSX/SPE regset requests, and delegates unknown requests to `ptrace_request()`. `do_syscall_trace_enter()` runs ptrace syscall-entry reporting, syscall emulation skipping, seccomp, syscall-number validation, tracepoints, and audit setup, returning either a valid syscall number or `-1` with `r3 = -ENOSYS`. `do_syscall_trace_leave()` records audit exit, tracepoint exit, and ptrace syscall-exit stops. `pt_regs_check()` is a build-time ABI assertion function.

## State And Persistence
The file manipulates task register state through helper functions and syscall trace flags. It does not store file-local persistent state.

## Dependencies And Integration Points
It integrates with generic Linux ptrace, seccomp, audit, trace/events/syscalls, PowerPC switch/debug helpers, native regset views, and compat handling through `ptrace32.c`.

## Risks
Syscall entry register semantics are ABI-sensitive, especially the difference between seccomp and ptrace use of `gpr[3]` and `orig_gpr3`. Invalid syscall handling must avoid audit/trace side effects. USER-area offsets and pt_regs layout must stay synchronized with UAPI constants.

## Test Signals
Run ptrace USER peek/poke tests, GET/SETREGS and feature regsets, seccomp trace/errno/allow paths, syscall emulation via `PTRACE_SYSEMU`, audit/tracepoint coverage, single-step detach behavior, and build failures from intentional pt_regs layout mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace32.c

## Purpose
`ptrace32.c` implements compat ptrace handling for 32-bit tracers or tracees on a 64-bit PowerPC kernel, including special 32-to-64 USER-area commands.

## Important APIs, Types, And Functions
It exports `compat_arch_ptrace()`. Local macros `FPRNUMBER()`, `FPRHALF()`, and `FPRINDEX()` translate 32-bit FPR word indexes into `thread.fp_state` positions. It delegates many commands to `arch_ptrace()` or `compat_ptrace_request()`.

## Control Flow
The function handles 3264 memory peek/poke by reading a 32-bit pointer from the tracer and using `ptrace_access_vm()` against a 64-bit target address. It handles normal 32-bit USER peek/poke with 4-byte alignment and FPR word indexing, and 3264 USER peek/poke by selecting high or low halves of 64-bit registers. It has special legacy debugreg handling, then routes GET/SETREGS through the current task's regset view and delegates broader commands to native `arch_ptrace()`.

## State And Persistence
State changes are made through `ptrace_put_reg()`, direct FPR word updates after `flush_fp_to_thread()`, `ptrace_access_vm()` writes, and delegated breakpoint/register handlers.

## Dependencies And Integration Points
It is built under `CONFIG_COMPAT`, depends on `linux/compat.h`, and bridges old PPC32 ptrace ABIs with the shared native helper layer.

## Risks
The high/low half selection uses host memory layout for a temporary `u64`, so endian assumptions are important. Address arguments are mixed 32-bit userspace pointers and 64-bit target addresses. FPR indexing has legacy PPC32 semantics that differ from whole-regset access.

## Test Signals
Compat tests should cover PPC_PTRACE_PEEKTEXT_3264/POKETEXT_3264, PEEKUSR/POKEUSR for GPR and FPR halves, PEEKUSR_3264/POKEUSR_3264 high and low halves, GETREGS/SETREGS for 32-bit tasks, debugreg compatibility, and invalid alignment/out-of-range cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/reloc_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/reloc_32.S

## Purpose
`reloc_32.S` applies dynamic relocations for a relocatable PPC32 kernel image at early boot or secure-guest transitions.

## Important APIs, Types, And Functions
It exports `_GLOBAL(relocate)`, taking the desired final address in `r3`. It parses dynamic tags `DT_RELA`, `DT_RELASZ`, and `DT_RELAENT`, handles relocation types `R_PPC_RELATIVE`, `R_PPC_ADDR16_HI`, `R_PPC_ADDR16_HA`, and `R_PPC_ADDR16_LO`, and references linker-provided offsets for `__dynamic_start`, `__rela_dyn_start`, `__dynamic_symtab`, and `_stext`.

## Control Flow
The routine obtains its runtime address with a branch-and-link trick, computes runtime addresses for dynamic, rela, symbol, and text sections, scans `.dynamic` for RELA metadata, computes current and final relocation offsets, then iterates each relocation. Relative relocations store addend plus final offset; halfword relocations compute symbol/addend/final-offset high, high-adjusted, or low halves. Modified locations are flushed from data cache and invalidated from instruction cache before returning.

## State And Persistence
It mutates the loaded kernel image in place. There is no global data beyond embedded PC-relative pointers.

## Dependencies And Integration Points
It is called by early boot/relocation code such as secure guest setup in `prom_init.c`. It depends on the linker script producing dynamic relocation metadata and on PowerPC cache-management instructions.

## Risks
Incorrect offset calculation corrupts code/data before the kernel runs. Unknown relocation types are skipped, so new relocation forms must be added deliberately. Cache synchronization is mandatory for modified instructions.

## Test Signals
Build and boot relocatable PPC32 kernels, inspect relocation sections for supported types, test nonzero final bases, and validate instruction patching after relocation through early boot execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/reloc_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/reloc_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/reloc_64.S

## Purpose
`reloc_64.S` applies dynamic relocations for a relocatable 64-bit PowerPC kernel image.

## Important APIs, Types, And Functions
It exports `_GLOBAL(relocate)`, with final kernel address in `r3`. It parses RELA dynamic tags and supports `R_PPC64_RELATIVE` and `R_PPC64_UADDR64`. Embedded pointers reference `__dynamic_start`, `__rela_dyn_start`, `__dynamic_symtab`, and `_stext`.

## Control Flow
The function computes runtime addresses via link-register self-reference, scans `.dynamic` for RELA pointer, size, and entry size, calculates the current offset and final relocation offset, divides size by entry size to get a loop count, and then processes each RELA entry. Relative relocations use addend plus final offset; `UADDR64` also resolves the dynamic symbol value before storing. Unsupported relocation types are skipped.

## State And Persistence
The routine patches 64-bit words in the kernel image. It keeps no external state.

## Dependencies And Integration Points
It is used by relocatable PowerPC64 boot paths and by secure guest setup in `prom_init.c` when the kernel image must be restored and re-relocated.

## Risks
Only two relocation types are handled, so toolchain changes that emit other relocation kinds can leave stale addresses. Unlike the PPC32 version, no explicit cache flush appears here, so it relies on usage/context not requiring instruction-cache invalidation for handled relocations.

## Test Signals
Boot relocated PPC64 kernels at varied bases, inspect `.rela.dyn` for only supported relocations, run secure guest relocation paths, and validate symbols requiring `R_PPC64_UADDR64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/reloc_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rethook.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rethook.c

## Purpose
This file implements the PowerPC architecture hooks for generic `rethook`, using a kprobe on a return trampoline.

## Important APIs, Types, And Functions
It defines the assembly symbol `arch_rethook_trampoline`, exports `arch_rethook_prepare()`, `arch_rethook_fixup_return()`, and `arch_init_kprobes()`, and registers a `struct kprobe trampoline_p` with `trampoline_rethook_handler()`.

## Control Flow
`arch_rethook_prepare()` records the original link register and stack frame in the rethook node, then replaces the function return address with the trampoline address. When the trampoline is reached, the kprobe pre-handler calls `rethook_trampoline_handler(regs, regs->gpr[1])`. During fixup, `arch_rethook_fixup_return()` sets `nip` to `orig_ret_address - 4` for trap/kprobe emulation and sets `link` to the original return address for optimized probe paths.

## State And Persistence
Per-return state is stored in `struct rethook_node` (`ret_addr`, `frame`) and temporary `pt_regs` modifications. The registered kprobe persists after `arch_init_kprobes()`.

## Dependencies And Integration Points
It depends on generic kprobes and rethook frameworks. `NOKPROBE_SYMBOL` annotations prevent recursive instrumentation of the handler and arch hooks.

## Risks
Return-address fixup is path-sensitive: trap-based kprobes use `nip`, optimized probes use `link`. An off-by-one-instruction mistake would resume at the wrong address. The implementation assumes `gpr[1]` is the stack pointer frame key.

## Test Signals
Kretprobe/rethook tests should verify normal returns, optimized probes, nested hooks, stack-frame matching, and that instrumentation recursion does not occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rethook.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas-proc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas-proc.c

## Purpose
`rtas-proc.c` creates legacy `/proc/powerpc/rtas/*` interfaces for pSeries RTAS services: progress display, clock, scheduled power-on, sensors, tone frequency/volume, and user RTAS RMO buffer discovery.

## Important APIs, Types, And Functions
Important structures are `struct individual_sensor` and `struct rtas_sensors`. `proc_rtas_init()` creates proc entries. Write/show handlers include `ppc_rtas_poweron_write/show`, `ppc_rtas_progress_write/show`, `ppc_rtas_clock_write/show`, `ppc_rtas_tone_freq_write/show`, `ppc_rtas_tone_volume_write/show`, and `ppc_rtas_rmo_buf_show`. Sensor helpers include `ppc_rtas_find_all_sensors()`, `ppc_rtas_process_error()`, `ppc_rtas_process_sensor()`, `check_location_string()`, and `get_location_code()`.

## Control Flow
Initialization only proceeds on `machine_is(pseries)` and when an `rtas` device node exists. User writes are parsed as decimal numbers through `parse_number()` or copied into `progress_led`; handlers call the matching RTAS token via `rtas_call()` or `rtas_progress()`. Sensor display reads the `rtas-sensors` property, then for each token/quantity calls `get-sensor-state`, formats known token classes, appends RTAS condition text, and decodes optional location-code strings from `ibm,sensor-XXXX` properties.

## State And Persistence
Global state includes cached `rtas_node`, the last requested `power_on_time`, last `progress_led` string, and tone frequency/volume values. Firmware state changes persist outside the kernel for clock, power-on time, indicators, and progress display.

## Dependencies And Integration Points
The file depends on procfs, seq_file, uaccess, OF property APIs, RTAS token lookup/calls, pSeries machine detection, RTC conversion helpers, and `rtas_rmo_buf` exported by RTAS core. It exposes a userspace ABI under `/proc`.

## Risks
The sensor array is fixed at `MAX_SENSORS` but `ppc_rtas_find_all_sensors()` assigns `sensors.quant = len / 8` without an explicit cap before filling, so malformed firmware with too many sensors would be dangerous. Proc writes are not serialized around global variables. The interfaces are legacy and thinly validate semantic ranges except tone volume clamping. User access to the RMO buffer is explicitly not arbitrated by the kernel.

## Test Signals
Tests should verify proc entry creation only on pSeries with RTAS, clock/power-on writes with valid and invalid decimal input, progress string truncation, tone frequency/volume writes, sensor formatting for known and unknown tokens, location-code parsing, behavior when `rtas-sensors` is absent, and RMO buffer output formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas-rtc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas-rtc.c

## Purpose
`rtas-rtc.c` implements RTAS-backed real-time clock operations for boot time, read time, and set time.

## Important APIs, Types, And Functions
It provides `rtas_get_boot_time()`, `rtas_get_rtc_time()`, and `rtas_set_rtc_time()`. It uses RTAS tokens `RTAS_FN_GET_TIME_OF_DAY` and `RTAS_FN_SET_TIME_OF_DAY`, `rtas_busy_delay_time()`, timebase helpers, `mktime64()`, `rtc_time`, `msleep()`, and `udelay()`.

## Control Flow
Each function calls the relevant RTAS method in a loop while RTAS reports busy delay and a five-second `MAX_RTC_WAIT` timebase budget has not expired. Boot-time read spins with `udelay()` because scheduling is not available. Normal read/set uses `msleep()` but refuses to delay in interrupt context; read clears the output time on would-delay interrupt context, while set returns `1`. Successful reads translate RTAS year/month/day/hour/min/sec fields into `time64_t` or `struct rtc_time`; set passes converted fields to RTAS.

## State And Persistence
There is no local persistent state. `rtas_set_rtc_time()` changes firmware/hardware RTC state.

## Dependencies And Integration Points
The file plugs into PowerPC time/RTC machine operations and depends on RTAS core token lookup, busy-delay interpretation, and timebase frequency.

## Risks
Interrupt-context behavior is intentionally limited; callers may receive unchanged/zeroed time instead of sleeping. Busy loops stop after five seconds but still return or log based on the final RTAS error. The functions trust RTAS return field ordering.

## Test Signals
Exercise successful get/set, RTAS busy retry, timeout behavior, interrupt-context read and set paths, error logging, month/year conversion boundaries, and boot-time read before scheduler availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas-rtc.c -->
