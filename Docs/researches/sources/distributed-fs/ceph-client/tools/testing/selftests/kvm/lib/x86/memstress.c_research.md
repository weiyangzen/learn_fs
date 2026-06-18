<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/memstress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/memstress.c

## Purpose
`memstress.c` adds x86 nested-virtualization support to the generic KVM memstress framework. It lets memstress run in L2 by preparing either VMX or SVM state in an L1 guest and then entering nested guest code.

## Important APIs, Types, and Functions
Public functions include `memstress_l2_guest_code()`, `memstress_nested_pages()`, and `memstress_setup_nested()`. Internal paths include the assembly entry `memstress_l2_guest_entry`, `l1_vmx_code()`, `l1_svm_code()`, `memstress_l1_guest_code()`, and `memstress_setup_ept_mappings()`.

## Control Flow
L1 setup chooses VMX when `X86_FEATURE_VMX` is available, otherwise SVM. VMX setup enables VMX operation, loads a VMCS, requires 1G EPT support, prepares the VMCS with an L2 stack containing the vCPU id, launches L2, and expects a `VMCALL` exit. SVM setup builds a VMCB and expects `SVM_EXIT_VMMCALL`. Host setup enables TDP, identity maps low memory and the memstress region with 1G mappings, allocates per-vCPU nested state, rewrites the vCPU RIP to L1 code, and passes nested data plus vCPU id.

## State and Persistence
State includes per-vCPU VMX/SVM pages, nested page tables, the L2 stack, and the global `memstress_args`. It persists for the life of the memstress VM and is cleaned up with the VM.

## Dependencies and Integration Points
The file depends on `memstress.h`, `processor.h`, `svm_util.h`, `vmx.h`, TDP helpers, and generic memstress guest code. It integrates with tests that request nested memstress and need KVM to shadow EPT12/NPT efficiently.

## Risks and Test Signals
Risks include missing TDP, missing 1G EPT support, wrong nested entry stack ABI, VMX/SVM feature mismatch, and failure to map the tested GPA range in L2. Test signals are `GUEST_ASSERT()` checks, expected `EXIT_REASON_VMCALL` or `SVM_EXIT_VMMCALL`, and normal memstress completion from L2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/memstress.c -->
