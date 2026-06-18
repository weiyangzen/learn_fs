<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_smoke_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_smoke_test.c

## Purpose
This is a functional smoke test for SEV, SEV-ES, and SNP guests. It verifies SEV status MSRs, selected control-register/MSR round trips, GHCB termination exits for SEV-ES/SNP, shutdown handling, and VMSA XSAVE synchronization.

## Important APIs, Types, and Functions
Important guest functions are `guest_sev_code()`, `guest_sev_es_code()`, `guest_snp_code()`, `guest_shutdown_code()`, and the assembly entry `guest_code_xsave`. Host helpers are `test_sev()`, `test_sev_shutdown()`, `test_sync_vmsa()`, `compare_xsave()`, and `test_sev_smoke()`. The test uses `vm_sev_create_with_one_vcpu()`, `vm_sev_launch()`, `vcpu_xsave_set()`, `KVM_EXIT_SYSTEM_EVENT`, `KVM_SYSTEM_EVENT_SEV_TERM`, GHCB MSR protocol constants, and SEV/SNP policy bits.

## Control Flow, State, and Persistence
For SEV, the guest checks CPUID/MSR state, touches EFER and control registers, then exits with `GUEST_DONE`. For SEV-ES and SNP, the guest verifies SEV status bits, tests registers, writes `GHCB_MSR_TERM_REQ`, and performs `vmgexit()`, which the host expects as a system-event termination. Shutdown tests deliberately corrupt the IDT and execute `ud2`. VMSA sync tests seed host XSAVE state, launch an encrypted guest that saves its initial XSAVE image into a shared page, and compare bytes. State is per-VM encrypted launch state, guest VMSA, shared page data, and XSAVE contents.

## Dependencies and Integration Points
This integrates with SEV/SEV-ES/SNP CPU features, SEV launch helpers, GHCB MSR termination, KVM XCRS/XSAVE support, shared-page allocation in encrypted VMs, and SNP/SEV policy handling.

## Risks and Test Signals
Risks include missing SEV MSR bits, bad GHCB termination mapping, VMSA state not synced before guest entry, and shutdown exits being misreported. Signals are `UCALL_DONE` for SEV guests, exact `KVM_SYSTEM_EVENT_SEV_TERM` data for SEV-ES/SNP, `KVM_EXIT_SHUTDOWN` for corrupted IDT, and byte-identical XSAVE images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_smoke_test.c -->
