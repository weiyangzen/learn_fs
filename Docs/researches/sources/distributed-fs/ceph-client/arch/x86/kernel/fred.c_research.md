# sources/distributed-fs/ceph-client/arch/x86/kernel/fred.c

## Purpose
Initializes Flexible Return and Event Delivery (FRED) exception delivery for x86 CPUs and programs FRED stack levels and RSP slots.

## Important APIs, Types, And State
Exports per-CPU `fred_rsp0` and defines `cpu_init_fred_exceptions()` and `cpu_init_fred_rsps()`. Stack level macros assign kernel #DB to level 1, NMI and #MC to level 2, and #DF to level 3. The code programs MSRs `MSR_IA32_FRED_CONFIG`, `MSR_IA32_FRED_STKLVLS`, and `MSR_IA32_FRED_RSP0..3`.

## Control Flow And Persistence
`cpu_init_fred_exceptions()` loads `SS` with `__KERNEL_DS`, writes the user entrypoint and redzone/interrupt-stack config, restores cached RSP0 after offline/online cycles, zeros RSP1-RSP3, enables `X86_CR4_FRED`, invalidates the IDT to catch accidental IDT use, and disables fast 32-bit syscall capabilities. `cpu_init_fred_rsps()` must run after CPU entry areas exist and maps FRED stack levels to the DB/NMI/DF IST top addresses.

## Dependencies And Integration Points
Integrates with descriptor/IDT code, CPU entry area IST helpers, trap vectors, CR4, and syscall capability setup. IRQ init calls `fred_complete_exception_setup()` elsewhere before selecting FRED vs IDT delivery.

## Risks And Test Signals
Risks are wrong stack-level assignment, stale RSP0 after CPU hotplug, invalid SS in early kernel events, and accidental IDT use after FRED activation. Test signals include FRED boot, CPU hotplug, NMI/#DB/#DF/#MC delivery, 32-bit syscall compatibility, and absence of #GP on first return to user mode.
