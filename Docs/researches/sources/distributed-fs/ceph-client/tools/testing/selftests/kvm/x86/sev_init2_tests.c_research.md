<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_init2_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_init2_tests.c

## Purpose
This test validates the `KVM_SEV_INIT2` memory-encryption command across SEV, SEV-ES, and SNP VM types. It checks VM type acceptance, invalid flag rejection, and VMSA feature filtering against the kernel-reported feature mask.

## Important APIs, Types, and Functions
Important helpers are `__sev_ioctl()`, `test_init2()`, `test_init2_invalid()`, `test_vm_types()`, `test_flags()`, and `test_features()`. It uses `struct kvm_sev_cmd`, `struct kvm_sev_init`, `KVM_MEMORY_ENCRYPT_OP`, `KVM_SEV_INIT2`, `KVM_X86_GRP_SEV/KVM_X86_SEV_VMSA_FEATURES`, `KVM_CAP_VM_TYPES`, and CPUID probes for SEV, SEV-ES, and SEV-SNP.

## Control Flow, State, and Persistence
`main()` opens KVM, fetches supported VMSA features, checks that VM-type capability bits match CPUID, and then creates throwaway barebones VMs for valid and invalid `KVM_SEV_INIT2` calls. It tests the default SEV type, SEV-ES and SNP when present, rejects default and software-protected VM types, rejects every flag bit, and allows only known supported VMSA feature bits. No persistent state is kept beyond firmware/KVM initialization of each temporary VM.

## Dependencies and Integration Points
The test integrates with `/dev/sev`, KVM SEV device attributes, KVM VM-type creation, PSP firmware return codes, and SEV feature enumeration.

## Risks and Test Signals
Risks include CPUID/capability mismatch, accepting unknown flags/features, or misclassifying SEV-ES/SNP feature dependencies. Signals are successful `KVM_SEV_INIT2` for supported combinations and `EINVAL` for invalid VM types, flags, and unknown VMSA feature bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_init2_tests.c -->
