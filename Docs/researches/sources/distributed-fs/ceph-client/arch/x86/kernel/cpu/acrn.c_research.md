# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/acrn.c

## Purpose
This file implements ACRN hypervisor detection and guest callback interrupt setup.

## Important APIs, Types, and Functions
`acrn_detect()` returns the ACRN CPUID base. `acrn_init_platform()` installs `sysvec_acrn_hv_callback` on `HYPERVISOR_CALLBACK_VECTOR` and routes TSC calibration to `acrn_get_tsc_khz`. `acrn_x2apic_available()` reports x2APIC availability from the boot CPU feature. `acrn_setup_intr_handler()` and `acrn_remove_intr_handler()` export registration for a single callback handler. `x86_hyper_acrn` registers the hypervisor descriptor.

## Control Flow
During hypervisor detection, the descriptor's detect callback identifies ACRN. Platform init installs the system vector and calibration hooks. On callback interrupt, the IDT entry saves old irq regs, sends APIC EOI as required by ACRN, increments hypervisor callback stats, calls the optional registered handler, and restores irq regs.

## State and Persistence
Persistent state is the global function pointer `acrn_intr_handler`, installed IDT vector, and modified `x86_platform` calibration hooks.

## Dependencies and Integration Points
The file depends on ACRN CPUID helpers, APIC EOI, IDT system vectors, irq register tracking, hypervisor framework registration, TSC calibration hooks, and exported symbols for ACRN device code.

## Risks and Test Signals
Risks include missing EOI causing lower-priority interrupts to be blocked, races around handler registration/removal, and incorrect TSC calibration. Test signals include ACRN guest boot detection, callback interrupt count increments, registered handler invocation, and stable TSC/cpu calibration.
