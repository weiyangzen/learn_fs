# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/x2apic_savic.c

## Purpose
This file implements the Secure AVIC x2APIC backend for AMD SEV-SNP guests. Secure AVIC accelerates APIC state through per-vCPU backing pages and requires special handling for APIC register access, IPI injection, EOI, and hypervisor GPA registration.

## Important APIs, Types, And Functions
`struct secure_avic_page` defines a page-aligned APIC backing page, and per-CPU `savic_page` stores those pages. Register helpers read/write APIC bitmaps and vectors. `savic_read()` returns backing-page values for accelerated registers and GHCB MSR reads for nonaccelerated timer/LVT registers. `savic_write()` updates backing-page or GHCB state. `savic_icr_write()` emulates ICR delivery to self/all/all-but/destination, updates backing-page ICR state, and notifies the hypervisor when needed. IPI callbacks wrap this path. `savic_eoi()` clears ISR locally for edge interrupts or propagates EOI through GHCB for level interrupts. `savic_setup()` registers the backing page GPA and enables Secure AVIC; `savic_teardown()` disables it and unregisters GPA. `apic_x2apic_savic` is the driver.

## Control Flow
Probe requires `CC_ATTR_SNP_SECURE_AVIC`; if Secure AVIC is present without x2APIC mode, the guest terminates. Probe allocates per-CPU backing pages. Setup initializes APIC ID from the hypervisor-visible APIC MSR, registers the backing page GPA via GHCB, and writes `MSR_AMD64_SAVIC_CONTROL` with enable/allowed-NMI bits. Runtime reads/writes avoid expensive intercepted APIC MSRs by touching the backing page where allowed. IPI sends update target backing-page IRR or NMI request state and use GHCB notification for non-self destinations.

## State And Persistence
Per-CPU APIC backing pages persist while the driver is active and mirror APIC ISR/TMR/IRR/allowed-IRR and control registers. Secure AVIC enablement persists in `MSR_AMD64_SAVIC_CONTROL` until teardown. Vector updates maintain the `SAVIC_ALLOWED_IRR` bitmap through the APIC driver's `update_vector` callback.

## Dependencies And Integration Points
It depends on confidential-computing platform attributes, SEV/GHCB helpers, native x2APIC MSR operations for accelerated self IPI/EOI pieces, APIC bitmap helpers, and the generic APIC driver infrastructure. It integrates with vector allocation via `update_vector`, NMI/IPI delivery, local APIC setup/teardown, and SNP guest termination policy.

## Risks
The register allowlist is security- and correctness-sensitive: unknown or misaligned offsets are rejected/logged. Backing-page GPA registration must succeed before VMRUN or the guest cannot continue. EOI differs for level vs edge interrupts; wrong ISR/TMR handling can lose or repeat interrupts. Directly updating remote per-CPU backing pages assumes online CPU mappings and correct APIC ID-to-CPU association.

## Test Signals
Run under SEV-SNP Secure AVIC with x2APIC enabled. Validate setup GPA registration, local timer/LVT accesses, self and remote IPIs, NMI delivery, level-triggered IO-APIC/MSI behavior requiring propagated EOI, vector allocation updates in allowed IRR, CPU hotplug/teardown, and absence of unknown-register errors.
