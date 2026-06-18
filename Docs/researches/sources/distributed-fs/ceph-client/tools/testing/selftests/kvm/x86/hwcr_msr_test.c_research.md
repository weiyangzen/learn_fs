# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hwcr_msr_test.c

Purpose: Tests KVM emulation/filtering of AMD `MSR_K7_HWCR` bits. It verifies that only valid bits are stored, ignored bits are accepted but not persisted, and illegal bits are rejected.

Important APIs/types/functions: `test_hwcr_bit()` defines ignored bits 3/6/8, valid bits 18/24, and the derived legal mask. It uses `_vcpu_set_msr()`, `vcpu_get_msr()`, and `vcpu_set_msr()` against `MSR_K7_HWCR`. `main()` iterates every bit in `BITS_PER_LONG`.

Control flow: For each bit, the host writes a single-bit value through KVM_SET_MSRS, asserts success for legal bits and failure for illegal bits, reads back HWCR, checks only valid bits persist, and resets HWCR to zero.

State and persistence behavior: HWCR state is vCPU MSR state and is reset after each bit case. No external persistence exists.

Dependencies and integration points: Depends on KVM's AMD HWCR MSR emulation and host-side MSR ioctl return semantics.

Risks and maintenance notes: If KVM adds support for additional HWCR bits, the valid/ignored masks must be updated. The test is intentionally bit-exhaustive, so it catches both overly permissive and overly strict changes.

Test signals: Passing means HWCR write filtering and readback semantics match KVM's intended ABI. Failures identify invalid MSR acceptance, legal MSR rejection, or incorrect bit persistence.
