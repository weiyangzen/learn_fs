# sources/distributed-fs/ceph-client/arch/powerpc/kernel/exceptions-64s.S

## Purpose

`exceptions-64s.S` contains the 64-bit Book3S/server PowerPC exception vectors and common handlers. It is included from `head_64.S` because the vector layout is position dependent. The file lays out fixed real-mode vectors, real trampolines, virtual AIL vectors, virtual trampolines, the FWNMI page, common relocated handlers, masked-interrupt return paths, KVM interrupt routing, and mitigation fallback code for entry/RFI flushing.

## Important APIs, entry points, and macros

The macro system begins with fixed-section helpers such as `EXC_REAL_BEGIN`, `EXC_VIRT_BEGIN`, `TRAMP_REAL_BEGIN`, `TRAMP_VIRT_BEGIN`, and `EXC_COMMON_BEGIN`. Interrupt definitions use `INT_DEFINE_BEGIN/END` to declare per-vector attributes, then `GEN_INT_ENTRY`, `GEN_COMMON`, `__GEN_COMMON_ENTRY`, and `__GEN_COMMON_BODY` generate entry and register-frame code. `KVMTEST` routes interrupts taken while a KVM guest is active. `EXCEPTION_RESTORE_REGS`, `MASKED_INTERRUPT`, `SEARCH_RESTART_TABLE`, and `SEARCH_SOFT_MASK_TABLE` implement return and soft-mask behavior.

Named vectors cover system reset, machine check, data and instruction storage, SLB faults, external interrupts, alignment, program check, FP/Altivec/VSX/facility unavailable, decrementer and hdecrementer, doorbells, system calls and hypercalls, trace, hypervisor storage and emulation assists, HMI, virtualization IRQs, PMU, instruction breakpoint, denormal assists, and soft-NMI watchdog. Exported or global helpers include `do_uaccess_flush` and `enable_machine_check`; `disable_machine_check` is local.

## Control flow

The file first defines vector metadata and then opens fixed sections: real vectors at `0x0100..0x18ff`, real trampolines at `0x1900..0x2fff`, virtual vectors at `0x3000..0x58ff`, virtual trampolines at `0x5900..0x6fff`, and the FWNMI page at `0x7000..0x7fff` on pseries/powernv. Real entries save minimal state in PACA, optionally test KVM, collect SRR/HSRR/DAR/DSISR/CFAR/PPR state, switch to kernel MSR or stay in real mode for early handlers, then branch to common handlers. Virtual AIL entries run similar logic with relocation already on.

Machine check and system reset are special NMI-like paths. System reset uses the NMI emergency stack and tracks `PACA_IN_NMI`. Machine check runs an early real-mode handler on the MCE emergency stack, supports limited nesting through `PACA_IN_MCE`, queues recoverable kernel-context events, delivers user/guest events to late handlers, and panics through `unrecoverable_mce` when state is unsafe. HMI uses an early real-mode handler before optionally redelivering to the virtual handler.

Maskable interrupts check soft-mask state and soft-mask tables before normal delivery. If masked, they set `PACAIRQHAPPENED`, adjust DEC or hard-disable bits where needed, search restart entries, restore volatile state, and return through RFI/HRFI without calling the C handler. System call paths include classic `sc`, hypercall routing to KVM, and vectored `scv` entries that are treated as soft-masked because they can enter with interrupts enabled.

## State and persistence behavior

The code persists exception state in PACA save areas, `pt_regs` stack frames, SRR/HSRR validity flags, soft-mask and pending-interrupt fields, emergency stack counters, KVM host state, and fixed sections copied to low physical memory for relocatable kernels. It also relies on CPU feature fixup sections to patch behavior for PPR, CFAR, HV mode, radix versus hash MMU, transactional memory, denormalization support, and mitigation requirements.

## Dependencies and integration points

Dependencies include `exception-64s.h`, `head-64.h`, PACA and `pt_regs` offsets, IRQ soft-mask constants, KUP/KUAP helpers, CPU/MMU feature fixups, KVM Book3S handlers, and common return code from `interrupt_64.S`. C integration includes `do_IRQ`, `timer_interrupt`, `do_page_fault`, `do_hash_fault`, `do_slb_fault`, `do_bad_segment_interrupt`, `machine_check_early`, `machine_check_exception_async`, `system_reset_exception`, `handle_hmi_exception`, `performance_monitor_exception_*`, `load_up_fpu`, `load_up_altivec`, TM unavailable handlers, and many unknown/facility handlers.

## Risks and invariants

The file is constrained by fixed vector sizes, relocatable branch reach, real-mode addressability, and exact register save order. Any change to entry size can break fixed offsets or branch ranges. KVM tests must run only on vectors that can be taken while guest state is active. MCE, SRESET, and HMI paths must avoid touching unsafe virtual memory too early. Soft-mask replay must not lose edge-triggered doorbells, decrementer events, or hard-mask requirements. Mitigation trampolines must preserve scratch state despite running in extremely constrained contexts.

## Test signals

Signals include successful boot across pseries, powernv, radix and hash MMU builds; correct syscall and scv behavior; external interrupts and timers under irq-disable stress; KVM guest interrupt exits; machine-check and HMI injection tests; PMU and watchdog NMI behavior; FP/Altivec/VSX unavailable lazy-load behavior; and runtime checks from BUG/WARN entries in stack or soft-mask paths. Build coverage should exercise relocatable, KVM HV/PR, transactional memory, denormalization, KUAP, and mitigation configurations.
