# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/smm.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/smm.h

Purpose: x86 System Management Mode helper declarations for KVM selftests.

Important APIs/types/functions: `SMRAM_SIZE`, `SMRAM_MEMSLOT`, `SMRAM_PAGES`, `setup_smram`, and `inject_smi`.

Control flow and state: host tests reserve/map SMRAM, configure a vCPU for SMM testing, inject SMI, run the vCPU, and check SMM entry/exit behavior. State includes SMRAM memslot content and vCPU SMM/MP state.

Dependencies and integration: depends on `kvm_util.h` and x86 vCPU/register helpers from `processor.h` through implementation files.

Risks: SMM state is special and interacts with memory slots, hidden CPU state, and nested virtualization. SMRAM slot numbers must avoid collisions with normal test memory.

Test signals: x86 SMM selftests validate SMRAM setup, SMI injection, and guest transitions into/out of SMM.
