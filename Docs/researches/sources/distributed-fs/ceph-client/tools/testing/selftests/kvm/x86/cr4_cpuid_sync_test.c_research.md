# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/cr4_cpuid_sync_test.c

Purpose: Tests synchronization between guest CR4 feature bits and CPUID exposure for features whose availability depends on CR4 state. The guest toggles CR4 controls and checks CPUID reflects KVM's expected dynamic behavior.

Important APIs/types/functions: `MAGIC_HYPERCALL_PORT` provides a host sync point; `guest_code()` performs CR4/CPUID transitions and port I/O exits; `main()` creates the VM and drives the expected exits. It relies on selftest `set_cr4()`, CPUID helpers, and KVM I/O exits.

Control flow: The guest runs through staged CR4 mutations, using port I/O to give userspace a chance to inspect or continue execution. The host expects KVM I/O exits at the magic port and reports guest assertions on failure.

State and persistence behavior: CR4 state is vCPU architectural state; CPUID exposure is vCPU configuration plus any KVM dynamic synchronization. No persistent external state is touched.

Dependencies and integration points: Integrates with KVM's x86 register emulation, guest CPUID instruction handling, and feature exposure rules. The test is particularly relevant for features that are legal only when their CR4 enabling bit is set.

Risks and maintenance notes: Dynamic CPUID behavior is subtle because some CPUID fields are fixed by userspace while others are derived from runtime state. Architecture additions may require new assertions or mask updates.

Test signals: Passing shows KVM keeps CR4-dependent CPUID output coherent across guest CR4 writes. Failures suggest stale CPUID caching, missed CR4 validation, or incorrect feature exposure.
