# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/cpuid_test.c

Purpose: Validates KVM CPUID ABI behavior for guest-visible CPUID data, including consistency between userspace-provided CPUID, in-guest `CPUID` results, `KVM_GET_CPUID2`, and immutability rules after a vCPU has run.

Important APIs/types/functions: `struct cpuid_mask` models constant CPUID bits that KVM should not allow userspace to override. `guest_main()` walks guest CPUID entries, `compare_cpuids()` compares expected versus observed entries with masks, `vcpu_alloc_cpuid()` copies CPUID data into guest memory, `run_vcpu()` handles staged ucalls, `set_cpuid_after_run()` tests post-run failure behavior, and `test_get_cpuid2()` validates get/set round trips. It uses `KVM_SET_CPUID2`, `KVM_GET_CPUID2`, `vcpu_get_cpuid()`, `kvm_get_supported_cpuid()`, and ucall syncs.

Control flow: The host prepares a vCPU CPUID table, maps a copy into guest memory, and runs the guest through stages. The guest compares hardware `CPUID` instruction output with the userspace table for each entry. The host then tests that changing CPUID after `KVM_RUN` is rejected where the ABI requires it and that `KVM_GET_CPUID2` returns a coherent table.

State and persistence behavior: CPUID state is vCPU-local and becomes effectively frozen after first run. The only shared state is a guest-memory copy of the expected `kvm_cpuid2` structure.

Dependencies and integration points: Depends on KVM CPUID ioctl semantics, x86 CPUID leaf handling, selftest processor helpers, and paravirtual CPUID leaves. It is a direct ABI conformance test for userspace VMM CPUID management.

Risks and maintenance notes: CPUID constant masks must be updated when KVM or architecture rules change. New leaves or subleaves can expose stale comparison assumptions. Post-run CPUID mutability is ABI-sensitive and should not be relaxed accidentally.

Test signals: Passing means guest CPUID output matches the KVM-configured table except for documented constant bits, `KVM_GET_CPUID2` returns expected data, and post-run `KVM_SET_CPUID2` behavior is preserved. Failures point to CPUID filtering, ioctl ABI, or feature-masking regressions.
