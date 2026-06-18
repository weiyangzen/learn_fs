# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/kvm-uuid.c

Purpose: this small arm64 KVM selftest ensures KVM's vendor hypervisor SMCCC UID remains the hard-coded expected UUID.

Important APIs and functions: `guest_code()` calls `do_smccc(ARM_SMCCC_VENDOR_HYP_CALL_UID_FUNC_ID, ...)` and compares return registers `a0` through `a3` against constants for UUID `28b46fb6-2ec5-11e9-a9ca-4b564d003a74`. Host `main()` runs a one-vCPU VM and handles `UCALL_DONE`, `UCALL_ABORT`, `UCALL_PRINTF`, and sync.

Control flow: the guest performs one SMCCC call and either asserts the UID matches or reports failure, then signals done. The host loops until done.

State and persistence: no persistent state. The expected UUID constants are intentionally local rather than shared to detect accidental global changes.

Dependencies and integration points: depends on ARM SMCCC vendor hypervisor call handling in KVM, libkvm VM creation, and ucall reporting.

Risks: the constants must not be "deduplicated" with production headers because the point is detecting tampering or drift. If KVM intentionally changes ABI identity, this test must be deliberately updated.

Test signals: mismatch in any SMCCC return word is a guest assertion failure. Passing confirms stable KVM vendor UID exposure.
