<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/smm_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/smm_test.c

## Purpose
This test validates System Management Mode save/restore behavior, including SMI handling while nested VMX or SVM state is active. It verifies that state snapshots taken inside and around SMM can be restored into a recreated VM.

## Important APIs, Types, and Functions
Important pieces are `smi_handler[]`, `setup_smram()`, `self_smi()`, `guest_code()`, `l2_guest_code()`, `inject_smi()`, `vcpu_save_state()`, `vm_recreate_with_one_vcpu()`, and `vcpu_load_state()`. It uses `KVM_CAP_X86_SMM`, optional `KVM_CAP_NESTED_STATE`, VMX helpers, SVM helpers, x2APIC self-SMI delivery, and an I/O sync port.

## Control Flow, State, and Persistence
The host sets up SMRAM and optional nested virtualization pages. The guest enables x2APIC, triggers SMI to itself, optionally enters nested L2, and syncs fixed stage numbers through port I/O. The host loops over every sync, validates reported stages or the fixed SMRAM stage, injects additional SMIs during L2 execution, and on almost every stage saves KVM x86 state, releases/recreates the VM, reloads state, and continues. State spans SMRAM contents, SMM save state, nested VMCS/VMCB state, APIC mode, and selftest stage counters.

## Dependencies and Integration Points
The file integrates KVM SMM capability, SMRAM setup, APIC SMI delivery, nested VMX/SVM execution, KVM x86 state serialization, and VM recreation.

## Risks and Test Signals
Risks include losing SMM state during migration-style save/restore, corrupting nested state while in SMM, incorrect RSM return, and save/restore while an SMI is active. Signals are sequential stage reports, expected SMRAM-stage reports while in SMM, and eventual `DONE` without guest assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/smm_test.c -->
