<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/svm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/svm.c

## Purpose
`svm.c` implements nested AMD SVM support helpers for KVM selftests. It allocates VMCB-related pages, configures nested paging, builds a runnable VMCB from current guest state, runs nested guests with `vmrun`, and opens `/dev/sev` for SEV tests.

## Important APIs, Types, and Functions
Public functions include `vcpu_alloc_svm()`, `vm_enable_npt()`, `generic_svm_setup()`, `run_guest()`, and `open_sev_dev_path_or_exit()`. The file also defines global `guest_regs` and `rflags`, plus `vmcb_set_seg()` and assembly register save/restore macros.

## Control Flow
Allocation reserves pages for `struct svm_test_data`, VMCB, host-save area, and MSR permission map, then records GPAs/HVAs. `vm_enable_npt()` clones the VM's PTE masks but clears the C-bit and marks NPT walks as user accesses before initializing the stage-2 MMU. `generic_svm_setup()` enables EFER.SVME, writes `MSR_VM_HSAVE_PA`, snapshots current segment/control/debug state into the VMCB, sets intercepts for VMRUN and VMMCALL, sets the nested RIP/RSP, and enables nested paging when an NCR3 is present. `run_guest()` uses inline assembly to vmload/vmrun/vmsave while exchanging GPRs with the global save area.

## State and Persistence
Per-nested-vCPU state lives in allocated VMCB, save-area, MSRPM, and optional NPT root pages. Global register save state is process/guest global and is overwritten for each nested run.

## Dependencies and Integration Points
The file depends on `svm_util.h`, `processor.h`, KVM VM allocation helpers, x86 MSRs, and SVM instructions. It integrates with nested SVM tests and x86 memstress nested execution.

## Risks and Test Signals
Risks include incorrect VMCB segment attributes, stale global GPR save state across concurrent runs, missing SVME/HSAVE setup, C-bit leakage into NPT entries, and incorrect exit-code expectations. Test signals are `TEST_ASSERT()`s for NPT support, guest `GUEST_ASSERT()`s after `run_guest()`, and expected SVM exits such as `SVM_EXIT_VMMCALL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/svm.c -->
