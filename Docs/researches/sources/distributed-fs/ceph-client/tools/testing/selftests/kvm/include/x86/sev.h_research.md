# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/sev.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/sev.h

Purpose: x86 AMD SEV/SEV-ES/SNP helper interface for KVM selftests. It defines guest state classification, policy bits, launch helpers, VM creation wrappers, SEV ioctls, VM init hooks, VMGEXIT, encrypted-memory registration, and launch-update helpers.

Important APIs/types/functions: `enum sev_guest_state`, `SEV_POLICY_*`, `SNP_POLICY_*`, `GHCB_MSR_TERM_REQ`, `is_sev_snp_vm`, `is_sev_es_vm`, `is_sev_vm`, `sev_vm_launch`, `sev_vm_launch_measure`, `sev_vm_launch_finish`, `snp_vm_launch_start`, `snp_vm_launch_update`, `snp_vm_launch_finish`, `vm_sev_create_with_one_vcpu`, `vm_sev_launch`, `snp_default_policy`, `__vm_sev_ioctl`, `vm_sev_ioctl`, `sev_vm_init`, `sev_es_vm_init`, `snp_vm_init`, `vmgexit`, `sev_register_encrypted_memory`, `sev_launch_update_data`, and `snp_launch_update_data`.

Control flow and state: tests create a protected VM type, initialize SEV/ES/SNP state, register encrypted regions, perform launch-update over guest memory, measure/finish launch, then run encrypted guests. State persists in VM type, SEV launch state, guest memory attributes, encryption registration, and firmware/KVM-managed handles.

Dependencies and integration: depends on `linux/psp-sev.h`, `kvm_util.h`, `svm_util.h`, and `processor.h`. It integrates with guest memfd/private memory, SNP memory attributes, and AMD nested/SVM helpers.

Risks: SEV firmware availability, kernel capabilities, memory encryption C-bit handling, and policy compatibility are environment-sensitive. SEV ioctls must be routed to the right fd and negative tests need raw helpers.

Test signals: SEV, SEV-ES, and SNP launch tests validate policy setup, encrypted-memory registration, launch measurement/update, VMGEXIT behavior, and private/shared memory transitions.
