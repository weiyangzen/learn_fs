<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/sev.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/sev.c

## Purpose
`sev.c` provides AMD SEV, SEV-ES, and SEV-SNP VM launch helpers for x86 KVM selftests. It initializes encrypted-guest state, encrypts registered memory regions, performs launch update/measure/finish flows, and creates launched VMs for tests.

## Important APIs, Types, and Functions
Key functions are `sev_vm_init()`, `sev_es_vm_init()`, `snp_vm_init()`, `sev_vm_launch()`, `sev_vm_launch_measure()`, `sev_vm_launch_finish()`, `snp_vm_launch_start()`, `snp_vm_launch_update()`, `snp_vm_launch_finish()`, `vm_sev_create_with_one_vcpu()`, and `vm_sev_launch()`. Internal `encrypt_region()` iterates `region->protected_phy_pages` with sparsebit range macros and calls SEV or SNP update helpers.

## Control Flow
SEV and SEV-ES initialization uses legacy init ioctls for default VM type or `KVM_SEV_INIT2` for explicit VM types. Launch begins with policy setup, verifies guest status, encrypts all protected pages across memslots, optionally updates VMSA for SEV-ES, measures, and finishes. SNP launch enables hypercall exits for GPA range mapping, starts launch, updates all private pages with SNP page type normal, and finishes without the SEV measurement step.

## State and Persistence
State persists in `vm->arch.sev_fd`, `vm->arch.is_pt_protected`, protected-page sparsebits per memory region, private/shared page attributes, and firmware-side launch state. Measurements are returned through caller-provided buffers.

## Dependencies and Integration Points
The file depends on `sev.h`, sparsebit helpers, KVM SEV ioctls, memory attribute helpers, `vm_mem_set_private()`, `sev_launch_update_data()`, and `snp_launch_update_data()`. It integrates with x86 VM creation, protected guest tests, and page-table code that must not walk protected page tables after launch.

## Risks and Test Signals
Risks include encrypting the wrong page ranges, missing protected pages, using the wrong init ioctl for VM type, failing to update VMSA for SEV-ES, and mishandling SNP private memory. Test signals are guest status state checks, policy equality checks, successful launch measure/finish transitions, and protected guest tests that run only after `vm->arch.is_pt_protected` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/sev.c -->
