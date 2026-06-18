# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_phys.c

## Purpose
This file implements physical destination mode for x2APIC. It also owns the global x2APIC maximum APIC ID limit used when interrupt remapping or hypervisor constraints restrict addressable APIC IDs.

## Important APIs, Types, And Functions
`x2apic_phys` records forced physical mode from `x2apic_phys`. `x2apic_max_apicid` defaults to `UINT_MAX`. `x2apic_set_max_apicid(apicid)` updates the global limit and active driver limit when supported. `x2apic_fadt_phys()` checks ACPI FADT physical-mode requirement. IPI helpers send physical x2APIC IPIs to one CPU, masks, all, all-but-self, and self. `x2apic_get_apic_id()` returns the APIC ID unchanged. `apic_x2apic_phys` is the physical x2APIC driver.

## Control Flow
Early boot option `x2apic_phys` forces physical mode. Driver probe succeeds when x2APIC mode is active and either forced, required by FADT, or the active driver pointer already indicates physical x2APIC. Send paths use `weak_wrmsr_fence()` and write x2APIC ICRs with physical destination IDs. Shorthand all/all-but-self IPIs use destination shorthand.

## State And Persistence
Persistent state is the forced physical flag and maximum APIC ID limit. The APIC driver struct is read-only after init and exposes `x2apic_set_max_apicid` support so `apic.c` can clamp APIC IDs in non-remapped modes.

## Dependencies And Integration Points
It depends on ACPI FADT, x2APIC native MSR accessors, per-CPU physical APIC IDs, APIC driver probing, and x2APIC enablement policy in `apic.c`. It integrates with MSI/IO-APIC non-remapped destination limits.

## Risks
Without interrupt remapping, only addressable APIC IDs may receive IO-APIC/MSI interrupts; the limit must match hardware or hypervisor support. Physical mask delivery loops over CPUs and can be less efficient than cluster logical mode on large systems. FADT-forced mode must override cluster preference.

## Test Signals
Boot with `x2apic_phys`, ACPI FADT physical-mode systems, non-remapped x2APIC guests, large APIC ID limits, and IPI/mask delivery. Check selected routing log and interrupt affinity behavior.
