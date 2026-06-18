# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic_noop.c

## Purpose
This file defines the no-op APIC backend used when APIC support is disabled or unavailable. It lets generic APIC call sites continue to invoke callbacks without scattering APIC-disabled conditionals through low-level interrupt code.

## Important APIs, Types, And Functions
The file provides empty IPI senders, an ICR writer that drops writes, an ICR reader returning zero, `noop_get_apic_id()`, `noop_apic_eoi()`, and a secondary CPU wakeup function returning failure. `noop_apic_read()` and `noop_apic_write()` warn if hardware APIC support appears present and APIC is not explicitly disabled. `apic_noop` is a full `struct apic` instance using logical destination defaults and shared CPU-to-APIC helpers.

## Control Flow
`apic.c` calls `apic_disable()` to install `apic_noop` when APIC facilities are disabled during early mapping/detection. After installation, static calls are updated by `apic_install_driver()` so later APIC operations become harmless no-ops.

## State And Persistence
The driver has no mutable runtime state. Its warning behavior depends on `boot_cpu_has(X86_FEATURE_APIC)` and `apic_is_disabled`.

## Dependencies And Integration Points
It integrates with the APIC driver switch mechanism in `init.c` and provides the fallback implementation for APIC read/write, EOI, IPI, ICR, and CPU wakeup callbacks. It depends on common APIC ID helpers and x86 feature flags.

## Risks
The no-op backend hides APIC hardware access, so accidental installation on systems that require APIC can leave interrupts, timers, IPIs, CPU bring-up, and MSI routing nonfunctional. The read/write warnings are useful but only catch some incorrect call paths. Wakeup always fails, so SMP boot must not depend on this driver.

## Test Signals
Boot with `nolapic` or configurations without APIC should not crash due to APIC call sites. Logs should show APIC-disabled mode, no unexpected `WARN_ON_ONCE` from noop reads/writes, and expected loss or fallback of APIC-dependent capabilities.
