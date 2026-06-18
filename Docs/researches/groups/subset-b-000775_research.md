# subset-b-000775 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_85xx.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_85xx.S

## Purpose
Provides the 32-bit Freescale/NXP 85xx/e500 BookE kernel entry path, early MMU setup, exception vectors, fast TLB miss handlers, SMP secondary entry, SPE save/restore glue, and relocation helpers. It is the first architecture-specific code for these CPUs after firmware hands control to the kernel.

## Important APIs, Types, And Functions
Important exported labels include `_stext`, `_start`, `__early_start`, `__secondary_start`, `__secondary_hold_acknowledge`, `create_kaslr_tlb_entry`, `reloc_kernel_entry`, `switch_to_as1`, `restore_to_as0`, `abort`, and, with SPE, `load_up_spe` and `__giveup_spe`. It relies heavily on BookE SPRs such as IVPR/IVOR, MAS0-MAS7, SRR, CSRR, DBSR/DBCR0, DEAR, ESR, PIR, and SPRG thread/scratch registers. Local helpers include `get_phys_addr`, `finish_tlb_load`, and SPE kernel exception handling.

## Control Flow
Boot begins at `_start`, translates the device tree and kernel runtime addresses to physical addresses, optionally performs relocatable/KASLR setup, establishes an initial TLB1 mapping through `85xx_entry_mapping.S`, programs IVORs and IVPR, initializes DBCR/DBSR, detects secondary CPUs, sets up `init_task`, the initial stack, and `SPRG_THREAD`, then calls `early_init`, optional KASAN/relocation init, `machine_init`, and `MMU_init` before jumping to `start_kernel` via `rfi`. Exception vectors under `interrupt_base` use `head_booke.h` prolog macros for normal, critical, debug, machine-check, syscall, timer, doorbell, hypervisor, and SPE paths. Data and instruction TLB errors try a fast page-table walk via `FIND_PTE`; valid hits branch to `finish_tlb_load`, while permission or missing-PTE cases restore scratch state and fall back to the storage exception handlers.

## State And Persistence
The file establishes persistent per-CPU execution state in SPRs, TLB entries, thread save slots, `SPRG_THREAD`, MAS defaults, IVOR mappings, and secondary CPU rendezvous globals. It also writes debugger-visible `abatron_pteptrs`, relocation globals such as `kernstart_addr`, and per-CPU hugepage CAM allocation state through `next_tlbcam_idx`. No filesystem state is touched; persistence lasts until CPU reset or later architecture code rewrites the same registers.

## Dependencies And Integration Points
Depends on BookE exception macros from `head_booke.h`, `85xx_entry_mapping.S`, e500 MMU/TLB layout, Linux PTE bit definitions, KVM BookE hooks, CPU feature fixups, SPE support, and platform calls such as `early_init`, `machine_init`, `MMU_init`, `start_kernel`, `start_secondary`, `call_setup_cpu`, `loadcam_entry`, and `relocate_init`. It integrates with page fault handling (`do_page_fault`), IRQ/timer handlers, debug handlers, KASAN, dynamic memory start, KASLR, SMP bring-up, and optional embedded hypervisor facilities.

## Risks And Edge Cases
The high-risk areas are early address translation before normal mappings exist, preserving the executing TLB entry while invalidating firmware mappings, 64-bit physical address handling, hugepage CAM replacement, KUAP fault rejection, KVM interception in exception prologs, SPE state ownership, and second relocation when `PAGE_OFFSET` changes physical backing. Bad IVOR offsets or MAS bit construction can make the CPU unrecoverable before printk works. TLB miss fast paths must avoid clobbering scratch registers and must reject invalid permissions precisely.

## Test Signals
Useful signals are successful 85xx/e500 boot to `start_kernel`, SMP secondary startup, kexec/KASLR boot, page fault and TLB miss stress, hugetlb mappings, SPE user/kernel traps, BookE KVM entry/exit smoke tests, watchdog/decrementer/doorbell interrupt delivery, and cross-build coverage for E500, E500MC, 32/64-bit physical address, SPE, KASAN, SMP, and relocatable kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_85xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_8xx.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_8xx.S

## Purpose
Implements low-level startup, exception vectors, MPC8xx software TLB refill, early MMU/cache setup, optional pinned TLB mappings, and 8xx errata workarounds for 32-bit PowerPC 8xx embedded processors.

## Important APIs, Types, And Functions
Key labels are `_stext`, `_start`, `__start`, `start_here`, `initial_mmu`, `mmu_pin_tlb`, `FixupPGD`, and `FixupDAR`. The file defines optional perf counters `itlb_miss_counter`, `dtlb_miss_counter`, and `instruction_counter`. It uses 8xx MMU SPRs such as MI/MD_CTR, MI/MD_EPN, MI/MD_TWC, MI/MD_RPN, M_TWB, M_TW, DAR, DSISR, IMMR, IC_CST, DC_CST, and DER.

## Control Flow
Firmware enters `__start` with boot arguments; the code saves the device tree pointer, calls `initial_mmu`, enables IR/DR with `rfi`, and then runs normal initialization at `start_here`. The exception table handles reset, machine check, external IRQ, alignment, program, decrementer, syscall, single-step, software emulation, 8xx instruction/data TLB misses, TLB errors, breakpoints, and unknown traps. TLB miss handlers perform a software table walk via `M_TWB`, populate MI/MD TLB registers from Linux PTEs, optionally increment perf counters, then return directly with `rfi`. TLB error paths build `pt_regs` and call `do_page_fault`; special 8xx bug paths repair bad DAR values for cache-block instructions and can fill missing kernel PGD entries from `swapper_pg_dir`.

## State And Persistence
The file initializes early ITLB/DTLB entries, cache enable state, protection-mode SPRs, optional pinned text/data/IMMR TLB entries, `SPRG_THREAD`, the initial stack, `M_TWB`, Abatron debugger PTE pointers, and optional perf counters. These are CPU-local architectural state plus global counters; there is no durable persistence.

## Dependencies And Integration Points
Depends on `head_32.h`, 8xx PTE bit layout, `asm/code-patching-asm.h` patch sites, `machine_init`, `MMU_init`, `early_init`, `kasan_early_init`, `start_kernel`, `do_page_fault`, `do_IRQ`, `timer_interrupt`, `alignment_exception`, `program_check_exception`, `emulation_assist_interrupt`, and optional pinning symbols such as `VIRT_IMMR_BASE`. It integrates with perf events via patched miss counters and with vmapped-stack overflow handlers when configured.

## Risks And Edge Cases
The 8xx path is sensitive to exact MI/MD register programming, Linux-PTE-to-hardware-bit conversion, 512K/8M page encodings, cache mode setup, and the DAR fixup instruction decoder. Incorrect handling of the `RPN_PATTERN` DAR tag, `dcbi/dcbx/icbi` emulation, or missing PGD repair can turn recoverable TLB misses into silent bad mappings. Pinned TLB configurations reduce available TLB capacity and must match text/data/IMMR layout.

## Test Signals
Useful signals include MPC8xx boot with MMU enabled, page fault stress, instruction and data TLB miss counters under perf, cache-block instruction tests that trigger DAR fixup, pinned-TLB boot variants, device-tree IMMR access, external IRQ and decrementer delivery, and build coverage across `CONFIG_8xx`, `CONFIG_PIN_TLB_*`, `CONFIG_PERF_EVENTS`, and `CONFIG_VMAP_STACK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_8xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_book3s_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_book3s_32.S

## Purpose
Provides 32-bit Book3S kernel entry, Open Firmware and BootX handoff, early BAT/hash/MMU setup, exception vectors, 603/604 TLB/hash refill paths, SMP secondary startup, and BAT update helpers for non-8xx classic PowerPC systems.

## Important APIs, Types, And Functions
Key labels include `_stext`, `_start`, `__start`, `__secondary_hold`, `__secondary_start`, `copy_and_flush`, `load_segment_registers`, `update_bats`, and local helpers `early_hash_table`, `load_up_mmu`, `clear_bats`, `flush_tlbs`, `mmu_off`, `initial_bats`, `setup_disp_bat`, `setup_cpm_bat`, and `setup_usbgecko_bat`. Exception labels include `MachineCheck`, `DataAccess`, `InstructionAccess`, `InstructionTLBMiss`, `DataLoadTLBMiss`, `DataStoreTLBMiss`, `AltiVecUnavailable`, and `PerformanceMonitor`.

## Control Flow
The boot path handles Open Firmware trampolines, BootX, and direct firmware entry, then calls `early_init`, turns the MMU off, clears BATs and TLBs, installs initial BAT mappings and segment registers, creates an early hash table, initializes CPU and 6xx idle state, optionally relocates the kernel to `PHYSICAL_START`, then enables the MMU and enters `start_here`. Later, `start_here` installs thread and stack state, calls platform/MMU init, reloads final SDR1/BAT state with MMU off, and jumps to `start_kernel`. Exception vectors dispatch to C handlers or fast 603/604 TLB/hash refill code that constructs hardware PTEs and falls back to storage exceptions when access checks fail.

## State And Persistence
Persistent CPU state includes BAT registers, segment registers, SDR1, TLB entries, SPRG thread pointer, secondary hold globals, Abatron PTE pointers, and optional early debug BAT mappings. SMP paths install per-CPU stacks and thread state before `start_secondary`. State is architectural and boot-time only; no storage persistence exists.

## Dependencies And Integration Points
Depends on `head_32.h`, classic Book3S BAT/segment/hash MMU details, `early_init`, `prom_init`, `bootx_init`, `machine_init`, `MMU_init`, `MMU_init_hw_patch`, `__save_cpu_setup`, `__restore_cpu_setup`, `call_setup_cpu`, `init_idle_6xx`, `start_kernel`, `start_secondary`, `hash_page`, and KVM Book3S real-mode handlers when configured. It feeds page fault, IRQ, decrementer, FPU, Altivec, perf, and debug exception infrastructure.

## Risks And Edge Cases
Risk is concentrated in early real-mode relocation, BAT validity ordering, firmware-provided mappings, CHRP RTAS machine-check stack handling, 603 software LRU TLB refill, 604 hash fault shortcuts, little-endian DAR adjustment, and SMP secondary entry assumptions. Bad segment/BAT programming can make early exceptions unrecoverable. Open Firmware and BootX entry paths have unusual register contracts that are difficult to test in generic CI.

## Test Signals
Signals include boot on PowerMac/PReP/CHRP/QEMU ppc32, Open Firmware and BootX handoff coverage, SMP secondary startup, relocation to `PHYSICAL_START`, 603/604 page fault and TLB miss stress, hash table operation, BAT update tests, Altivec/FPU unavailable traps, and cross-builds for `CONFIG_PPC_BOOK3S_604`, `CONFIG_SMP`, `CONFIG_PPC_OF_BOOT_TRAMPOLINE`, early debug BAT options, and KVM Book3S handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_book3s_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_booke.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_booke.h

## Purpose
Defines common assembler macros for BookE exception vector setup, normal/critical/debug/machine-check prologs, syscall entry, KVM interception hooks, MMU register saving, and standard storage/alignment/program/decrementer/FPU exception bodies.

## Important APIs, Types, And Functions
Major macros include `SET_IVOR`, `ALLOC_STACK_FRAME`, `THREAD_NORMSAVE`, `NORMAL_EXCEPTION_PROLOG`, `COMMON_EXCEPTION_PROLOG_END`, `prepare_transfer_to_handler`, `SYSCALL_ENTRY`, `BOOKE_LOAD_EXC_LEVEL_STACK`, `EXC_LEVEL_EXCEPTION_PROLOG`, `SAVE_xSRR`, `SAVE_MMU_REGS`, `CRITICAL_EXCEPTION_PROLOG`, `DEBUG_EXCEPTION_PROLOG`, `MCHECK_EXCEPTION_PROLOG`, `GUEST_DOORBELL_EXCEPTION`, `START_EXCEPTION`, `EXCEPTION`, `CRITICAL_EXCEPTION`, `MCHECK_EXCEPTION`, `DEBUG_DEBUG_EXCEPTION`, `DEBUG_CRIT_EXCEPTION`, `DATA_STORAGE_EXCEPTION`, `INSTRUCTION_STORAGE_EXCEPTION`, `ALIGNMENT_EXCEPTION`, `PROGRAM_EXCEPTION`, `DECREMENTER_EXCEPTION`, and `FP_UNAVAILABLE_EXCEPTION`.

## Control Flow
Vector files instantiate these macros to build aligned exception labels. Normal exceptions save scratch state in thread save slots, switch to kernel MSR, choose current or top-of-kernel stack based on MSR_PR, build a `pt_regs` frame, save volatile and nonvolatile GPRs, and call the C handler. Critical, machine-check, and debug paths use dedicated per-CPU stacks and distinct xSRR registers so they can interrupt normal exception handling. Syscall entry builds a compact frame and branches to `transfer_to_syscall`. Debug macros detect accidental single-step traps in vector entry code and clear DE/DBSR to resume the original exception safely.

## State And Persistence
The macros manipulate CPU SPRs, per-thread scratch save slots, per-CPU critical/debug/machine-check stacks, `pt_regs`, MSR bits, and KVM state transitions. They do not own durable data but define the frame layout and register-saving contract that all BookE exception return code relies on.

## Dependencies And Integration Points
Depends on `asm/ptrace.h`, `asm/kvm_asm.h`, `asm/kvm_booke_hv_asm.h`, `asm/thread_info.h`, BookE SPR definitions, stack offsets, KVM `DO_KVM` handlers, and low-level return paths such as `interrupt_return`, `ret_from_crit_exc`, `ret_from_mcheck_exc`, and `ret_from_debug_exc`. It integrates with page fault, alignment, program, timer, FPU, debug, and syscall C handlers.

## Risks And Edge Cases
Because these macros generate entry code, mistakes corrupt every BookE interrupt path. Risks include stack selection during nested critical exceptions, incomplete MMU/xSRR saving, stale ESR/DEAR values, MSR_DE single-step recursion in vector code, KVM GS/HV dispatch ordering, and differences between e500/e500mc/debug-level configurations. The `INSTRUCTION_STORAGE_EXCEPTION` explicitly zeros ESR to avoid stale store-fault state confusing page fault handling.

## Test Signals
Signals include build coverage for BookE/e500/e500mc/KVM/debug variants, boot-time vector setup, syscall smoke tests, nested machine-check or debug exception tests where available, page fault and alignment fault handling, timer/decrementer interrupts, FPU unavailable traps, and kgdb/kprobes tests that exercise debug exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_booke.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/hw_breakpoint.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/hw_breakpoint.c

## Purpose
Implements PowerPC hardware watchpoint support for the generic Linux perf/hw_breakpoint and ptrace breakpoint facilities using DABR/DAWR-like debug registers.

## Important APIs, Types, And Functions
Public architecture hooks include `hw_breakpoint_slots`, `arch_install_hw_breakpoint`, `arch_uninstall_hw_breakpoint`, `arch_check_bp_in_kernelspace`, `arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `thread_change_pc`, `hw_breakpoint_handler`, `hw_breakpoint_exceptions_notify`, `flush_ptrace_hw_breakpoint`, `hw_breakpoint_pmu_read`, and `ptrace_triggered`. Internal helpers include `hw_breakpoint_validate_len`, `stepping_handler`, `handle_p10dd1_spurious_exception`, `single_step_dabr_instruction`, `handler_error`, and `larx_stcx_err`. Per-CPU state is `bp_per_reg[HBP_NUM_MAX]`.

## Control Flow
Install searches the current CPU's breakpoint slots, stores the `perf_event`, and programs hardware unless the breakpoint is waiting for single-step rearming. Parse translates perf attributes into PowerPC type bits, privilege filters, address, length, and hardware-aligned length. On DABR/DAWR exceptions, the handler disables breakpoints, reads instruction details, checks constraints for every active slot, handles ptrace one-shot semantics, rejects larx/stcx and unemulatable kernel instructions, emulates or arranges single-step, invokes perf callbacks after the triggering instruction, and finally reprograms surviving breakpoints. Single-step exceptions complete pending callback delivery and rearm hardware.

## State And Persistence
State lives in per-CPU breakpoint slot arrays, each `perf_event`'s `arch_hw_breakpoint`, debug registers programmed by `__set_breakpoint`, and `perf_single_step` flags used across an exception/single-step pair. Ptrace breakpoints are stored in `task_struct.thread.ptrace_bps[]`. State is in-memory and CPU-local; no durable persistence exists.

## Dependencies And Integration Points
Depends on perf events, generic hw_breakpoint callbacks, ptrace, notifier `DIE_DABR_MATCH`/`DIE_SSTEP`, PowerPC instruction analysis and emulation (`wp_get_instr_detail`, `analyse_instr`, `emulate_step`), DABR/DAWR helpers, CPU features including ARCH_31, and 8xx-specific behavior. It integrates with debug exception delivery, task PC changes, and ptrace SIGTRAP behavior.

## Risks And Edge Cases
Risks include DAWR length and 512-byte boundary constraints, extraneous hardware matches caused by alignment granularity, Power10 DD1 spurious VSX octword exceptions, larx/stcx instructions that cannot be emulated safely, user-mode single-step interactions with ptrace, concurrent perf event release under RCU, and forgetting to rearm breakpoints after exception handling. Kernel-mode emulation failure disables the breakpoint to prevent livelock.

## Test Signals
Useful tests include perf watchpoint selftests for read/write and privilege filters, ptrace hardware watchpoints, multi-slot watchpoints, unaligned and boundary-crossing lengths, user versus kernel watchpoints, single-step interaction, larx/stcx and VSX access cases, 8xx watchpoints, and fault injection around instruction fetch failure. Hardware coverage should include DABR-only, DAWR, Power10, and ARCH_31 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/hw_breakpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/hw_breakpoint_constraints.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/hw_breakpoint_constraints.c

## Purpose
Provides the address, access-type, privilege, and instruction-size constraint checks used by the PowerPC hardware watchpoint exception handler.

## Important APIs, Types, And Functions
Exports `wp_check_constraints` and `wp_get_instr_detail`. Internal helpers include `dar_in_user_range`, `ea_user_range_overlaps`, `dar_in_hw_range`, `ea_hw_range_overlaps`, and `check_dawrx_constraints`. It uses `struct arch_hw_breakpoint`, `struct pt_regs`, `ppc_inst_t`, `struct instruction_op`, and instruction type/size macros from the single-step decoder.

## Control Flow
`wp_get_instr_detail` fetches the instruction at `regs->nip` with page faults disabled, decodes it, computes effective address and size, truncates 32-bit effective addresses, and normalizes cache/VMX accesses to their real access granularity. `wp_check_constraints` first treats 8xx as a single-breakpoint special case, then handles failed instruction decode, unknown instruction types, exact user-range overlap, hardware-aligned overlap, and privilege/access filters from DAWRX-style bits. Hardware-aligned but user-range-missing matches are marked as extraneous so callbacks can be suppressed when appropriate.

## State And Persistence
The file has no long-lived state. It mutates only `info->type` by setting `HW_BRK_TYPE_EXTRANEOUS_IRQ` when a hardware match is valid at DAWR granularity but not within the requested user range.

## Dependencies And Integration Points
Depends on PowerPC instruction decoding in `asm/sstep.h`, cache line size helpers, CPU feature `CPU_FTR_ARCH_31`, user instruction access helpers, and the main handler in `hw_breakpoint.c`. It encodes DAWR granularity assumptions used by perf and ptrace watchpoint delivery.

## Risks And Edge Cases
Risks include integer overlap checks near address wraparound, cache-op size normalization, VMX alignment, quadword behavior before ARCH_31, inability to fetch user instructions, and unknown decoded instruction types. If constraints are too permissive, users see false watchpoint hits; if too strict, real hardware matches are lost.

## Test Signals
Signals include watchpoint tests for read-only, write-only, read/write, user-only, kernel-only, cache operations, VMX/VSX aligned accesses, unknown or faulting instruction fetches, and DAWR granularity false-positive suppression on pre-ARCH_31 and ARCH_31 CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/hw_breakpoint_constraints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle.c

## Purpose
Implements the common PowerPC architecture idle entry wrapper, boot option disabling of platform power-save callbacks, and optional sysctl for Power4/970 nap mode.

## Important APIs, Types, And Functions
Exports `cpuidle_disable` and defines `arch_cpu_idle`, `powersave_off`, `power4_idle`, `powersave_nap`, and `register_powersave_nap_sysctl`. It uses platform callback `ppc_md.power_save`, runlatch helpers, HMT priority macros, and `prep_irq_for_idle`.

## Control Flow
`powersave=off` clears `ppc_md.power_save` and marks cpuidle disabled. `arch_cpu_idle` turns the runlatch off, calls the platform power-save routine when present, normalizes interrupt state by disabling local IRQs if the platform returned enabled, or otherwise drops hardware thread priority. It then restores medium priority and runlatch-on state. With `CONFIG_PPC_970_NAP`, `power4_idle` checks CPU support and `powersave_nap`, prepares IRQ state, flushes Altivec data streams if needed, and enters the assembly nap routine.

## State And Persistence
Persistent runtime state is `cpuidle_disable`, `powersave_nap`, and `ppc_md.power_save`. The sysctl under `kernel/powersave-nap` changes `powersave_nap` until reboot. No durable storage is used.

## Dependencies And Integration Points
Integrates with scheduler idle, PowerPC machdep callbacks, cpuidle policy, runlatch accounting, HMT thread priority, sysctl, timer/IRQ lazy masking, and assembly routines in `idle_book3s.S`. It relies on callers accepting either disabled or enabled interrupts after idle return.

## Risks And Edge Cases
The key risk is mismatched interrupt state around platform power-save code. `prep_irq_for_idle` must reject idle entry when a soft-masked interrupt is pending. Clearing `ppc_md.power_save` via boot option affects every CPU and disables deeper platform idle states. Power4 nap depends on CPU feature bits, user/sysctl enablement, and correct wakeup fixup.

## Test Signals
Signals include boot with and without `powersave=off`, idle loop residency, `/proc/sys/kernel/powersave-nap` behavior, interrupt wakeups from idle, runlatch accounting, scheduler idle tracing, and PowerMac/970 nap wakeup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_64e.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_64e.S

## Purpose
Provides generic 64-bit Book3E/e500 idle entry routines, including normal `wait` idle and ePAPR event-driven idle hypercall loops.

## Important APIs, Types, And Functions
Defines the macro `BOOK3E_IDLE`, loop macros `BOOK3E_IDLE_LOOP` and `EPAPR_EV_IDLE_LOOP`, exported labels `epapr_ev_idle`, `e500_idle`, and patch site `epapr_ev_idle_start`. It uses PACA fields `PACAIRQHAPPENED`, `PACAIRQSOFTMASK`, `PACACURRENT`, thread flag `_TLF_NAPPING`, and ePAPR `EV_IDLE` hcall token.

## Control Flow
The idle wrapper saves LR, hard-disables interrupts, checks whether a soft-disabled interrupt already happened, traces hard IRQs on, marks soft IRQs enabled, arranges LR so an interrupt returns to the caller, sets `_TLF_NAPPING`, hard-enables interrupts, and executes the selected idle loop. Normal e500 idle spins on `PPC_WAIT_v203`; ePAPR idle repeatedly issues the patched EV_IDLE hypercall sequence. If a pending interrupt is observed before sleeping, it marks `PACA_IRQ_HARD_DIS` and returns without entering idle.

## State And Persistence
State is per-CPU PACA soft-mask/pending IRQ state, the current thread's local flags, LR saved on the stack, and patched hcall opcodes at `epapr_ev_idle_start`. It persists only across the idle entry/wakeup interval.

## Dependencies And Integration Points
Depends on 64-bit Book3E interrupt return code honoring `_TLF_NAPPING`, PACA layout, trace IRQ flags, ePAPR hypercall patching, and `arch_cpu_idle`/platform power-save callbacks. It integrates with lazy interrupt replay and hypervisor idle facilities.

## Risks And Edge Cases
The critical edge case is losing an interrupt that arrived while soft-disabled but before hard-enable and idle. The early `PACAIRQHAPPENED` check and `PACA_IRQ_HARD_DIS` marking are intended to close that window. The ePAPR loop depends on runtime patching of hcall instructions; bad patching traps or spins forever.

## Test Signals
Signals include Book3E 64-bit idle wakeups by decrementer, doorbell, and external IRQ, trace IRQ flag consistency, ePAPR guest idle under a hypervisor, no lost-interrupt stress, and inspection that `epapr_ev_idle_start` is patched during initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_64e.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_6xx.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_6xx.S

## Purpose
Implements 6xx/7xxx 32-bit PowerPC idle power-save routines, including DOZE/NAP entry, CPU-specific pre/post handling, and early per-CPU idle initialization.

## Important APIs, Types, And Functions
Exports `init_idle_6xx`, `ppc6xx_idle`, `power_save_ppc32_restore`, `nap_save_msscr0`, `nap_save_hid1`, and `powersave_lowspeed`. It manipulates HID0/HID1/MSSCR0, MSR POW/EE, Altivec DSSALL, and thread flag `_TLF_NAPPING`.

## Control Flow
`init_idle_6xx` clears leftover NAP mode and records per-CPU default MSSCR0/HID1 values for CPUs that need restore after nap. `ppc6xx_idle` selects DOZE or NAP based on CPU features and `powersave_nap`, performs errata workarounds such as disabling L2 prefetch and 750FX low-speed mode, writes HID0 to enter low power, marks `_TLF_NAPPING`, enables EE and POW in MSR, then spins until an exception redirects return. `power_save_ppc32_restore` changes the interrupted NIP to LR so the idle function returns and restores saved MSSCR0/HID1.

## State And Persistence
Per-CPU saved SPR snapshots are stored in `nap_save_msscr0` and `nap_save_hid1`; `powersave_lowspeed` and `powersave_nap` influence runtime behavior. CPU SPR changes persist until restored on wakeup. No durable storage exists.

## Dependencies And Integration Points
Depends on CPU feature fixups, `powersave_nap` from `idle.c`, exception wakeup code that recognizes `_TLF_NAPPING`, PowerPC 6xx SPR definitions, Altivec support, and `head_book3s_32.S` calling `init_idle_6xx` during boot and secondary startup.

## Risks And Edge Cases
Risks include entering NAP on CPUs or boards that do not tolerate it, incomplete restoration of HID1/MSSCR0, L2 prefetch errata timing, low-speed PLL assumptions on 750FX, and interrupt return paths not rewriting NIP to LR. The code assumes per-CPU save arrays are indexed consistently before normal per-CPU infrastructure is fully active.

## Test Signals
Signals include 6xx/7xxx boot, idle wakeup by timer and external interrupts, `powersave_nap` toggling, CPU feature matrix builds, Altivec-enabled nap, SMP secondary idle initialization, and hardware tests on 745x and 750FX-like systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_6xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_85xx.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_85xx.S

## Purpose
Provides 32-bit e500/85xx idle entry and wakeup restore code for BookE processors, covering both e500mc `wait` idle and older HID0-based DOZE/NAP.

## Important APIs, Types, And Functions
Exports `e500_idle` and `power_save_ppc32_restore`. It uses thread flag `_TLF_NAPPING`, HID0 DOZE/NAP/SLEEP bits, MSR WE/EE, `wrteei`, `wait`, `flush_dcache_L1`, and `powersave_nap`.

## Control Flow
`e500_idle` marks the current thread as napping. On e500mc it hard-enables interrupts and loops on `wait`, relying on a real interrupt to return through the napping fixup. On older e500 it selects DOZE or NAP based on features and `powersave_nap`, flushes L1 data cache before NAP, programs HID0, enables MSR_WE and MSR_EE, and spins. `power_save_ppc32_restore` changes the saved NIP to LR so the interrupted idle function returns normally.

## State And Persistence
State is the thread local napping flag and transient HID0/MSR changes. No separate save arrays are used in this file; architectural state is restored by exception return or remains as configured for the CPU.

## Dependencies And Integration Points
Depends on BookE/e500 exception wakeup handling, CPU feature fixups, `powersave_nap`, `flush_dcache_L1`, and platform assignment of this routine as `ppc_md.power_save`. It integrates with `idle.c` and early 85xx CPU setup.

## Risks And Edge Cases
The main risks are missed wakeups if `_TLF_NAPPING` is not honored, cache coherency problems when entering NAP without the L1 flush, and spurious hypervisor wakeups on e500mc requiring the `wait` loop. HID0 bit selection must match CPU feature fixups.

## Test Signals
Signals include e500/e500mc idle wakeup tests, nap/doze feature builds, `powersave_nap` behavior, timer and doorbell wakeups, L1 flush path execution, and no lost interrupts under idle stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_85xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_book3s.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_book3s.S

## Purpose
Implements Book3S idle primitives for ISA 2.06/3.00 low-power states, including STOP/NAP/SLEEP/WINKLE entry, GPR-loss save/restore, and Power4/970 nap support.

## Important APIs, Types, And Functions
Exports `isa300_idle_stop_noloss`, `isa300_idle_stop_mayloss`, `idle_return_gpr_loss`, `isa206_idle_insn_mayloss`, `power4_idle_nap`, and `power4_idle_nap_return`. It uses PSSCR, `PPC_STOP`, `PPC_NAP`, `PPC_SLEEP`, `PPC_WINKLE`, `PACAR1`, `PACA_THREAD_INFO`, `_TLF_NAPPING`, and `PNV_THREAD_*` state constants.

## Control Flow
No-loss STOP simply writes PSSCR, executes STOP, returns zero for normal wakeup, and relies on SRESET wakeup to return via LR. May-loss STOP and ISA 2.06 idle save stack pointer, LR, CR, TOC, and nonvolatile GPRs in the red zone before entering the low-power instruction. SRESET wakeup code can call `idle_return_gpr_loss` with a return value to restore the saved context and return to the original caller. The ISA 2.06 path selects NAP/SLEEP/WINKLE and uses the required real-mode store/ptesync/load/false-dependency sequence. `power4_idle_nap` marks `_TLF_NAPPING`, enables POW/EE, and loops until exception fixup returns.

## State And Persistence
State is saved in the current stack red zone and `PACAR1` while in an idle state that may lose GPRs. PSSCR or MSR POW state is written before sleep. The napping flag persists only until wakeup fixup. No durable storage exists.

## Dependencies And Integration Points
Depends on Book3S idle callers saving non-GPR state, interrupt/SRESET wakeup code, PACA layout, cpuidle platform code, KVM nap requirements for r2, and `irq_set_pending_from_srr1` style wakeup reason handling. Power4 nap is called from `idle.c`.

## Risks And Edge Cases
Risks include using may-loss return on a no-loss entry, stack red-zone corruption, missing SPR/MSR/timebase save by the caller, failing the ISA-required idle entry sequence, SRESET wakeup with clobbered volatiles, and KVM requiring exact r2 restoration. The infinite branch after low-power instructions intentionally catches impossible direct fallthrough.

## Test Signals
Signals include POWER7/POWER8/POWER9/POWER10 cpuidle state tests, wakeup by decrementer/external IRQ/doorbell/system reset, GPR corruption tests after deep idle, KVM guest/host idle, Power4/970 nap tests, and tracing of SRR1 wakeup reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/idle_book3s.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ima_arch.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ima_arch.c

## Purpose
Supplies PowerPC-specific default IMA policy rules based on secure boot and trusted boot state.

## Important APIs, Types, And Functions
Defines policy arrays `secure_rules`, `trusted_rules`, and `secure_and_trusted_rules`, and exports architecture hook `arch_get_ima_policy`. It calls `is_ppc_secureboot_enabled`, `is_ppc_trustedboot_enabled`, and `set_module_sig_enforced`.

## Control Flow
When IMA asks for architecture policy, the function first checks secure boot. Secure boot enforces module signatures and returns appraisal rules, combined with measurement rules if trusted boot is also enabled. Trusted boot alone returns measurement rules. Systems with neither mode return `NULL`.

## State And Persistence
The policy arrays are static read-only strings. The only state mutation is module signature enforcement when secure boot is active. IMA consumes returned rules during policy setup; this file does not persist data.

## Dependencies And Integration Points
Depends on generic IMA policy parsing, PowerPC secure/trusted boot detection, kexec kernel appraisal, module appraisal/measurement hooks, and `CONFIG_MODULE_SIG` to avoid duplicate module appraisal rules.

## Risks And Edge Cases
Incorrect boot-state detection can under- or over-enforce module and kexec appraisal. When `CONFIG_MODULE_SIG` is enabled, module appraisal is intentionally omitted from secure rules to avoid duplicate verification. Policy strings must remain compatible with IMA parser syntax.

## Test Signals
Signals include secure boot returning appraisal policy and enforcing module signatures, trusted boot returning measurement policy, combined secure+trusted using `ima-modsig` template, kexec/module loading tests with signed and unsigned images, and builds with and without `CONFIG_MODULE_SIG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/ima_arch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/interrupt.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/interrupt.c

## Purpose
Implements C-side PowerPC syscall and interrupt exit preparation, including user work processing, lazy IRQ state reconciliation, KUAP restore, transactional memory/math restore, debug register reload, and restartable exit handling.

## Important APIs, Types, And Functions
Key functions are `syscall_exit_prepare`, `syscall_exit_restart`, `interrupt_exit_user_prepare`, `interrupt_exit_kernel_prepare`, `interrupt_exit_user_restart`, and `interrupt_exit_kernel_restart`. Internal helpers include `prep_irq_for_enabled_exit`, `booke_load_dbcr0`, `check_return_regs_valid`, and `interrupt_exit_user_prepare_main`. State includes `global_dbcr0`, `sk_dynamic_irqentry_exit_cond_resched`, and `interrupt_exit_not_reentrant`.

## Control Flow
Syscall exit stores the syscall result, applies PowerPC error signaling, handles per-syscall flags and tracing, disables local IRQs, then delegates to the common user-exit path. The user-exit loop enables IRQs to handle rescheduling or signal work, restores TM or math state, validates SRRs, enters context tracking user state, prepares for enabled interrupt return, reloads BookE debug registers, accounts CPU time, and restores KUAP user access locks. Kernel exit handles unrecoverable frames, optional preemption on IRQ return, SRR validation, pending soft-masked interrupts via `prep_irq_for_enabled_exit`, stack-store emulation, TM scratch, and KUAP kernel restore. Restart functions reestablish hard-disabled, soft-masked state and re-run the relevant prepare path.

## State And Persistence
State spans thread flags, `pt_regs`, PACA `irq_happened`/soft mask state, context tracking, KUAP AMR state, TM scratch, BookE debug DBCR0/DBSR, syscall result fields, and optional SRR-valid debug flags. All state is in-memory CPU/task state.

## Dependencies And Integration Points
Depends on low-level assembly in `interrupt_64.S` and 32-bit return paths, context tracking, scheduler, signal delivery, rseq, syscall tracing, KUAP, KVM/TM/math restore code, BookE advanced debug registers, and lazy IRQ helpers from `irq_64.c`. It is a central bridge between exception handlers and final return-to-user/kernel assembly.

## Risks And Edge Cases
High-risk areas are lost soft-masked interrupts, returning with wrong hard IRQ state, context tracking imbalance, KUAP unlocked across return, SRR clobbering by NMI/soft-NMI windows, transactional memory restore ordering, syscall error convention for `sc` versus `scv`, and stack-store emulation restart safety. Many functions are `notrace` because tracing in unreconciled interrupt state can recurse or touch unsafe vmaps.

## Test Signals
Signals include syscall ABI tests, signal/reschedule-on-exit tests, rseq selftests, ftrace/syscall tracing, KUAP fault tests, TM/math state restore tests, lockdep IRQ tracing, preemption-on-IRQ-return behavior, BookE debug single-step tests, and stress with soft-masked interrupt replay on Book3S64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/interrupt_64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/interrupt_64.S

## Purpose
Contains 64-bit PowerPC low-level syscall entry/exit, interrupt return, restart-table protected return sequences, fork return trampolines, and register sanitization/restoration paths.

## Important APIs, Types, And Functions
Defines `system_call_common_real`, `system_call_common`, `system_call_vectored_common`, `system_call_vectored_sigill`, `fast_interrupt_return_srr`, generated `interrupt_return_srr`, generated `interrupt_return_hsrr`, `ret_from_fork_scv`, `ret_from_fork`, `ret_from_kernel_user_thread`, and `start_kernel_thread`. Macros include `DEBUG_SRR_VALID`, `system_call_vectored`, and `interrupt_return_macro`. It uses PACA fields for save areas, IRQ soft masks, pending IRQs, SRR validity, and restart save state.

## Control Flow
System call entry saves user state into the kernel stack frame, sets up PACA/TOC, records syscall arguments and `pt_regs`, soft-disables IRQs, enables hard interrupts where appropriate, sanitizes volatile user registers, and calls `system_call_exception`. Exit calls `syscall_exit_prepare`, enters a restart-protected sequence that checks pending soft-masked interrupts, restores SRR/LR/CTR/XER/CR/GPRs, optionally restores all registers, and returns via `rfid` or `rfscv`. Generic interrupt return calls C user/kernel prepare helpers, saves restart R1, reconciles PACA soft-mask state, restores SRR or HSRR, clears reservations, restores registers, handles emulated stack-store update, and returns to user or kernel. Restart labels reload PACA/TOC and re-enter C prepare functions when an interrupt arrives during a return sequence.

## State And Persistence
State is the interrupt frame on the kernel stack, PACA save slots (`PACAKSAVE`, `PACA_EXIT_SAVE_R1`, `PACAIRQSOFTMASK`, `PACAIRQHAPPENED`, SRR-valid flags), architectural SRR/HSRR/LR/CTR/XER/CR/GPRs, and optional PPR. It is transient return-path state and not durable.

## Dependencies And Integration Points
Depends on exception-64s/64e macros, `syscall_exit_prepare`, `syscall_exit_restart`, `interrupt_exit_user_prepare`, `interrupt_exit_kernel_prepare`, restart and soft-mask table machinery, KUAP macros, register sanitization configuration, SCV support, and schedule tail for fork/thread return. It integrates directly with the C code in `interrupt.c`.

## Risks And Edge Cases
Return paths are extremely sensitive to register ordering, PACA soft-mask atomics, SRR validity, speculative execution barriers, clearing load/store reservations, and not restoring sensitive kernel register contents to user state. Restart tables must exactly cover windows where pending interrupts can redirect control. The emulated `stdu` stack-store path must avoid clobbering the frame before all registers are restored.

## Test Signals
Signals include syscall ABI tests for `sc` and `scv`, signal and ptrace register restoration, fork/kernel-thread startup, interrupt storm tests during syscall/interrupt return, KUAP debug checks, RFI SRR debug warnings, register-sanitization builds, KASAN/lockdep IRQ tracing, and Book3S HSRR interrupt return coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/interrupt_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/io.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/io.c

## Purpose
Implements exported PowerPC I/O port string and memory-copy helper functions used by generic drivers for repeated MMIO/PIO-style access.

## Important APIs, Types, And Functions
Defines global `isa_io_special` and exports `_insb`, `_outsb`, `_insw`, `_outsw`, `_insl`, `_outsl`, `_memset_io`, `_memcpy_fromio`, and `_memcpy_toio`. Internal macro `IO_CHECK_ALIGN` gates word-sized access optimization.

## Control Flow
Input helpers memory-barrier before the loop, repeatedly load from the volatile I/O address, execute `eieio`, copy to the caller buffer, and use `data_barrier` on the final read value. Output helpers memory-barrier before and after repeated volatile stores. Memory set/copy helpers first byte-align source/destination, transfer aligned words where possible, then finish remaining bytes, with ordering barriers around the operation.

## State And Persistence
The only file-level state is `isa_io_special`. The functions perform direct side effects on I/O memory and caller buffers; they do not retain mappings or durable state.

## Dependencies And Integration Points
Depends on PowerPC barrier semantics (`mb`, `eieio`, `data_barrier`), `__iomem` conventions, exported symbols for drivers, and architecture `asm/io.h` wrappers that route generic I/O APIs here.

## Risks And Edge Cases
Risks include incorrect ordering around device registers, unaligned buffer or I/O addresses, count values less than or equal to zero, endian/device access assumptions, and using volatile casts in a way that bypasses sparse annotations intentionally. The helpers do not perform bounds checking on caller buffers.

## Test Signals
Signals include driver smoke tests using `ins*`/`outs*`, MMIO memcpy/memset tests on devices or emulators, KCSAN/sparse builds for `__iomem`, and barrier-sensitive hardware tests such as FIFO or PIO devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/iomap.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/iomap.c

## Purpose
Provides the PowerPC implementation of simple I/O port mapping and PCI I/O unmap behavior.

## Important APIs, Types, And Functions
Exports `ioport_map` and, with PCI, `pci_iounmap`.

## Control Flow
`ioport_map` converts an I/O port number to an `__iomem` virtual address by adding `_IO_BASE`. `pci_iounmap` ignores addresses recognized as ISA or PCI I/O port windows and calls `iounmap` only for true MMIO mappings.

## State And Persistence
No owned state. The functions interpret existing global I/O mapping state such as `_IO_BASE`, ISA bridge mappings, and PCI host bridge I/O windows.

## Dependencies And Integration Points
Depends on `asm/io.h`, PCI bridge helpers, ISA bridge helpers, and generic PCI resource mapping code. It prevents generic PCI unmap from tearing down permanently mapped I/O port windows.

## Risks And Edge Cases
Incorrect classification of an address as I/O port versus MMIO can leak an ioremap or unmap a fixed I/O window. The simple `_IO_BASE` arithmetic assumes platform setup already established the I/O space mapping.

## Test Signals
Signals include PCI driver probe/remove paths using `pci_iomap`/`pci_iounmap`, legacy I/O port access, ISA bridge systems, and resource leak checks during repeated driver bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/iommu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/iommu.c

## Purpose
Implements bus-independent PowerPC dynamic DMA/IOMMU TCE mapping management, including table allocation, bitmap pools, SG mapping, coherent allocations, kdump preservation, debugfs/fault injection, and SPAPR IOMMU API integration.

## Important APIs, Types, And Functions
Major functions include `iommu_init_table`, `iommu_table_clear`, `iommu_table_reserve_pages`, `iommu_table_in_use`, `iommu_tce_table_get`, `iommu_tce_table_put`, `iommu_map_phys`, `iommu_unmap_phys`, `iommu_alloc_coherent`, `iommu_free_coherent`, `ppc_iommu_map_sg`, `ppc_iommu_unmap_sg`, `iommu_direction_to_tce_perm`, `iommu_register_group`, `iommu_add_device`, `iommu_flush_tce`, `iommu_tce_check_ioba`, `iommu_tce_check_gpa`, `iommu_tce_xchg_no_kill`, `iommu_tce_kill`, `ppc_iommu_register_device`, and `ppc_iommu_unregister_device`. Internal allocation is centered on `iommu_range_alloc`, `iommu_alloc`, `__iommu_free`, and per-table `iommu_pool` locks.

## Control Flow
Boot parameters configure virtual merging and optional fault injection. Table initialization allocates the bitmap, reserves forbidden pages, splits large tables into hashed small pools plus a large-allocation pool, clears or preserves TCEs depending on kdump/fadump state, and registers debugfs. Mapping allocates bitmap space, calls table operations to install TCEs, flushes if required, and uses memory barriers before hardware can DMA. SG mapping allocates per input segment, optionally merges contiguous DMA ranges, and backs out all successful allocations on failure. Unmap clears hardware TCEs and bitmap bits. IOMMU API support creates groups/domains and registers SPAPR TCE IOMMU devices for PHBs.

## State And Persistence
Persistent in-memory state includes each `iommu_table` bitmap, pool hints and spinlocks, kref, reserved range metadata, table operation pointers, debugfs entries, per-CPU pool hashes, fault-injection attributes, device `archdata.fail_iommu`, and IOMMU groups/domains. Hardware-visible state is the TCE table programmed by platform `it_ops`. Kdump paths may intentionally preserve first-kernel TCEs in the bitmap.

## Dependencies And Integration Points
Depends on DMA mapping core, scatterlist APIs, PowerPC PCI/VIO/platform TCE operations, `iommu-helper`, crash dump/fadump detection, debugfs, fault injection, generic IOMMU API, VFIO/SPAPR TCE ownership callbacks, PCI hose list, and platform-specific `iommu_table_ops`.

## Risks And Edge Cases
Risks include bitmap/hardware TCE mismatch, allocation fragmentation, mask and segment-boundary constraints, SG merge correctness, transient `set` failures and backout, kdump preserving too many or too few TCEs, reserved MMIO32 windows, reference lifetime of tables and IOMMU groups, and ownership transitions between platform and blocked domains. The allocator assumes `nr_pools` is power-of-two for hash masking.

## Test Signals
Signals include DMA API tests, high-throughput SG DMA, boundary/mask-limited devices, coherent allocation/free stress, driver bind/unbind leak checks, kdump/fadump boot with active DMA mappings, debugfs table weight, `fail_iommu` injection, VFIO/SPAPR TCE tests, IOMMU group sysfs presence, and cross-platform pseries/powernv/VIO/PCI coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/irq.c

## Purpose
Provides generic PowerPC IRQ handling glue: interrupt accounting, IRQ stack switching, platform IRQ dispatch, softirq stack support, IRQ initialization, hardware IRQ lookup, and SMP IRQ CPU selection.

## Important APIs, Types, And Functions
Defines and exports per-CPU `irq_stat`, plus `ppc_n_lost_interrupts` on PPC32. Key functions are `arch_show_interrupts`, `arch_irq_stat_cpu`, `__do_IRQ`, `do_IRQ`, `init_IRQ`, `do_softirq_own_stack`, `virq_to_hw`, and `irq_choose_cpu`. Internal helpers include `check_stack_overflow`, `call_do_softirq`, `__do_irq`, `call_do_irq`, `alloc_vm_stack`, and `vmap_irqstack_init`. It defines static call `ppc_get_irq`.

## Control Flow
`init_IRQ` allocates vmapped hard/soft IRQ stacks when configured, calls platform IRQ init, and patches the static call to `ppc_md.get_irq`. On an external interrupt, `do_IRQ` calls `__do_IRQ`, which switches to the per-CPU hardirq stack if not already on it, then `__do_irq` traces entry, checks stack depth, asks the platform interrupt controller for a virtual IRQ, optionally hard-enables interrupts for perf, handles spurious IRQ zero, and calls `generic_handle_irq`. Softirqs can similarly run on a per-CPU softirq stack. `/proc/interrupts` and `/proc/stat` aggregate architecture counters.

## State And Persistence
State includes per-CPU IRQ statistics, hardirq/softirq stack pointers, BookE critical/debug/machine-check stack arrays, static call target, and SMP round-robin rover protected by a raw spinlock. All state is runtime memory.

## Dependencies And Integration Points
Depends on generic IRQ core, `ppc_md.get_irq` and `ppc_md.init_IRQ`, tracing, lockdep, vmalloc, softirq stack support, device tree/PCI IRQ infrastructure, SMP CPU maps, and PowerPC stack frame conventions.

## Risks And Edge Cases
Risks include stack overflow during nested interrupts, failing to allocate vmapped stacks, platform `get_irq` returning zero for real interrupts, hard-enabling IRQs too early, static call not installed, and round-robin CPU selection on masks with no online CPUs. Inline assembly stack switching must preserve ABI-clobbered registers correctly.

## Test Signals
Signals include `/proc/interrupts` counters, spurious IRQ counts, timer/perf/doorbell/MCE/HMI accounting, interrupt storm tests, vmapped IRQ stack boot, softirq-on-own-stack tests, platform PIC dispatch, and SMP affinity distribution checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/irq_64.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/irq_64.c

## Purpose
Implements 64-bit PowerPC lazy interrupt soft-masking, pending-interrupt replay, idle IRQ preparation, SRR1 wake reason conversion, forced external IRQ replay, and the `noirqdistrib` boot option.

## Important APIs, Types, And Functions
Defines `distribute_irqs` and functions `replay_soft_interrupts`, `arch_local_irq_restore`, `prep_irq_for_idle`, `prep_irq_for_idle_irqsoff`, `replay_system_reset`, `irq_set_pending_from_srr1`, and `force_external_irq_replay`. Internal helpers include `next_interrupt`, `irq_happened_test_and_clear`, `__replay_soft_interrupts`, and `replay_soft_interrupts_irqrestore`. It uses PACA bits such as `PACA_IRQ_HARD_DIS`, `PACA_IRQ_HMI`, `PACA_IRQ_DEC`, `PACA_IRQ_EE`, `PACA_IRQ_DBELL`, `PACA_IRQ_PMI`, and `PACA_IRQ_REPLAYING`.

## Control Flow
Soft-masked interrupts set pending bits in PACA. `arch_local_irq_restore(0)` atomically tries to clear the soft mask if nothing is pending; otherwise it hard-disables interrupts, enters IRQ context, replays pending interrupts in priority order, exits IRQ context, and retries if softirq handling created new pending work. Replay synthesizes `pt_regs` and calls HMI, decrementer, external IRQ, doorbell, and PMI handlers. Idle preparation hard-disables interrupts, checks pending work, and either refuses idle or marks interrupts soft-enabled for low-power entry. Book3S idle wakeup converts SRR1 reason bits into pending IRQ bits or immediately handles system reset.

## State And Persistence
State is per-CPU PACA soft-mask and pending-bit fields, `distribute_irqs`, lockdep/tracing IRQ state, and optional KUAP AMR state saved around replay. No durable state exists.

## Dependencies And Integration Points
Depends on `interrupt.c` return preparation, `interrupt_64.S` restart sections, timer/IRQ/doorbell/PMI/HMI handlers, PS3 LV1 firmware side-effect call, KUAP, context tracking through `irq_enter`/`irq_exit`, and Book3S idle wakeup reason definitions.

## Risks And Edge Cases
The main risk is losing or reordering interrupts around transitions between hard-disabled, soft-disabled, and enabled states. Replay must avoid recursion through softirq-enabled sections, preserve KUAP, and prioritize HMI. Idle preparation must not enter low power when a pending interrupt exists. SRR1 reason mapping must match CPU architecture; doorbell wakeup needs `msgclr` to avoid duplicate interrupts.

## Test Signals
Signals include lockdep IRQ trace correctness, interrupt storm while toggling local IRQs, idle wakeup by DEC/EE/doorbell/HMI/system reset, PS3 builds, KUAP debug checks, forced external replay, `noirqdistrib` boot parameter, and softirq recursion stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/irq_64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/isa-bridge.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/isa-bridge.c

## Purpose
Tracks and maps the legacy ISA I/O bridge on PowerPC systems, supporting early PHB discovery, non-PCI ISA bridges, late PCI bus notification, and removal.

## Important APIs, Types, And Functions
Exports `isa_io_base` and `isa_bridge_pcidev`. Public setup functions are `isa_bridge_find_early` and `isa_bridge_init_non_pci`. Internal helpers include `remap_isa_base`, `process_ISA_OF_ranges`, `isa_bridge_find_late`, `isa_bridge_remove`, `isa_bridge_notify`, and `isa_bridge_init`.

## Control Flow
Early discovery scans OF nodes of type `isa` under a PCI host bridge, parses I/O ranges, remaps the ISA I/O window at `ISA_IO_BASE`, and marks `isa_io_base` valid. Non-PCI setup does the same directly from a device node. Late PCI notifications attach a discovered PCI device to an existing early node or detect a newly added ISA bridge. Removal clears cached references and unmaps the fixed 64K ISA area.

## State And Persistence
State is global `isa_io_base`, cached `isa_bridge_devnode`, and `isa_bridge_pcidev`. The virtual mapping at `ISA_IO_BASE` persists while the bridge is registered. Device node and PCI references are runtime-only.

## Dependencies And Integration Points
Depends on Open Firmware range parsing, PCI host bridge data, early ioremap/vmap APIs, PCI bus notifiers, ISA bridge helpers used by `iomap.c`, and platform code that calls early discovery while adding PHBs.

## Risks And Edge Cases
Risks include non-page-aligned OF ranges, missing or malformed `ranges`, multiple ISA bridges where only one global bridge is tracked, hot removal of a bridge used by legacy drivers, and the suspicious removal path leaving `isa_io_base` set to `ISA_IO_BASE` rather than clearing to zero. Fallback mapping of 64K from PHB base is only a compatibility path.

## Test Signals
Signals include boot on systems with legacy ISA devices, OF range parsing logs, successful port I/O through `ioport_map`, PCI hotplug notifier behavior, bridge removal/unmap tests where hardware supports it, and malformed device-tree range tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/isa-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/jump_label.c

## Purpose
Implements the PowerPC static key/jump label text patching hook.

## Important APIs, Types, And Functions
Defines `arch_jump_label_transform(struct jump_entry *entry, enum jump_label_type type)`. It uses `jump_entry_code`, `jump_entry_target`, `patch_branch`, `patch_instruction`, and `PPC_RAW_NOP`.

## Control Flow
When generic jump-label code toggles a static key, this function locates the instruction address. For `JUMP_LABEL_JMP` it patches a branch to the jump target; otherwise it patches a NOP.

## State And Persistence
No data state is owned. The function mutates kernel text, so its effects persist until the key is toggled again or code is unloaded/reset.

## Dependencies And Integration Points
Depends on PowerPC text patching and instruction encoding helpers plus the generic static key infrastructure. It is used by many subsystems that rely on static branches.

## Risks And Edge Cases
Risks include patching an address that is not writable/safe, branch target reach or encoding issues, instruction cache coherency handled by patch helpers, and concurrent execution while patching. This wrapper relies on lower-level patching code for synchronization.

## Test Signals
Signals include static key selftests, ftrace/jump-label heavy workloads, module load/unload with static keys, and text patching debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/jump_label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kdebugfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kdebugfs.c

## Purpose
Creates and exports the architecture debugfs root directory for PowerPC.

## Important APIs, Types, And Functions
Exports `arch_debugfs_dir` and defines init function `arch_kdebugfs_init`, registered with `arch_initcall`.

## Control Flow
During architecture initcall processing, `debugfs_create_dir("powerpc", NULL)` creates the top-level `/sys/kernel/debug/powerpc` directory and stores the returned dentry for other PowerPC code.

## State And Persistence
State is the global debugfs dentry pointer. The debugfs directory exists until debugfs teardown or reboot and has no durable persistence.

## Dependencies And Integration Points
Depends on debugfs and initcall ordering. Other architecture code can create files under `arch_debugfs_dir`.

## Risks And Edge Cases
If debugfs is disabled or creation fails, consumers must tolerate a NULL/error dentry. There is no explicit cleanup path because debugfs and kernel lifetime manage it.

## Test Signals
Signals include boot with debugfs enabled, presence of `/sys/kernel/debug/powerpc`, and downstream architecture debugfs files appearing under the directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kdebugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kgdb.c

## Purpose
Implements the PowerPC backend for KGDB, including trap-to-signal mapping, register serialization, breakpoint patching, single-step handling, and installation of architecture debugger hooks.

## Important APIs, Types, And Functions
Important functions include `kgdb_skipexception`, `kgdb_roundup_cpus`, `sleeping_thread_to_gdb_regs`, `dbg_get_reg`, `dbg_set_reg`, `kgdb_arch_set_pc`, `kgdb_arch_handle_exception`, `kgdb_arch_set_breakpoint`, `kgdb_arch_remove_breakpoint`, `kgdb_arch_init`, and `kgdb_arch_exit`. Internal handlers include `computeSignal`, `kgdb_debugger_ipi`, `kgdb_debugger`, `kgdb_handle_breakpoint`, `kgdb_singlestep`, `kgdb_iabr_match`, `kgdb_break_match`, and `kgdb_not_implemented`. Data includes `hard_trap_info`, `dbg_reg_def`, and saved old `__debugger*` hook pointers.

## Control Flow
Trap entry maps the PowerPC vector to a GDB signal and invokes generic KGDB exception handling. Breakpoint handling ignores user-mode traps, calls KGDB, and advances NIP past `BREAK_INSTR` when appropriate. Register get/set functions marshal `pt_regs` and optional SPE EVR state into GDB's register order. Continue/step packets optionally update PC and set MSR_SE or BookE DBCR0 single-step bits. Breakpoint install saves the original instruction with nofault read and patches in `BREAK_INSTR`; removal restores the saved instruction. Init swaps architecture debugger callbacks to KGDB handlers, and exit restores prior hooks.

## State And Persistence
State includes patched breakpoint instructions, saved original instructions in `kgdb_bkpt`, current task EVR state for SPE, global debugger hook pointers, `kgdb_cpu_doing_single_step`, and register contents in `pt_regs`. Text patches persist until breakpoint removal.

## Dependencies And Integration Points
Depends on generic KGDB, SMP debugger IPIs, PowerPC debug hook globals, text patching, instruction constants, ptrace register layout, SPE support, and trap numbering from exception code. It integrates with kdebug, single-step/debug exceptions, and kernel text mutation.

## Risks And Edge Cases
Risks include patching inaccessible or module-unloaded text, stale removed breakpoints, wrong register sizes between PPC32/PPC64/SPE, single-step state not cleared, user-mode traps accidentally consumed by KGDB, and failing to restore previous debugger hooks on exit. Breakpoint patching must preserve instruction cache coherency through `patch_instruction`.

## Test Signals
Signals include KGDB connect/continue/step, software breakpoint set/remove, SMP CPU roundup, register read/write through GDB, sleeping thread backtraces, BookE advanced debug stepping, SPE register access on 85xx, and module breakpoint tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kprobes-ftrace.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kprobes-ftrace.c

## Purpose
Implements the PowerPC optimized kprobe path that uses ftrace callbacks instead of software breakpoint single-step for eligible probe sites.

## Important APIs, Types, And Functions
Defines `kprobe_ftrace_handler` and `arch_prepare_kprobe_ftrace`. It uses `struct kprobe`, `struct kprobe_ctlblk`, `struct ftrace_ops`, `struct ftrace_regs`, `get_kprobe`, `kprobe_disabled`, `get_kprobe_ctlblk`, `kprobe_running`, `kprobes_inc_nmissed_count`, `current_kprobe`, and `KPROBE_HIT_*` states.

## Control Flow
The ftrace callback returns immediately if kprobe ftrace is globally disabled or recursion lock acquisition fails. It gets `pt_regs`, finds the kprobe for `nip`, skips disabled probes, and either records a missed hit when another kprobe is active or runs the pre-handler. PowerPC adjusts NIP backward before the pre-handler because the ftrace call site reports NIP after the mcount instruction. If the pre-handler does not redirect control, the code emulates a NOP by advancing NIP and optionally calls the post-handler. It then clears `current_kprobe` and releases the ftrace recursion lock.

## State And Persistence
State is per-CPU `current_kprobe` and `kprobe_ctlblk.kprobe_status`, plus per-probe missed-hit counters. `arch_prepare_kprobe_ftrace` marks the optimized instruction slot as unused and boostability as disabled.

## Dependencies And Integration Points
Depends on ftrace with register capture, generic kprobes, PowerPC `regs_add_return_ip`, mcount instruction size, recursion protection, and NOKPROBE marking to avoid probing the handler itself.

## Risks And Edge Cases
Risks include incorrect NIP adjustment, recursion through ftrace/kprobe handlers, pre-handler redirection requiring post-handler suppression, missing probes when `get_kprobe` fails, and interactions with hardirq/preempt context. The handler must not itself be probed.

## Test Signals
Signals include kprobes selftests with ftrace optimization enabled, pre/post handlers that modify NIP, nested probe miss accounting, disabled probe behavior, ftrace recursion stress, and comparison with breakpoint-based kprobe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/kprobes-ftrace.c -->
