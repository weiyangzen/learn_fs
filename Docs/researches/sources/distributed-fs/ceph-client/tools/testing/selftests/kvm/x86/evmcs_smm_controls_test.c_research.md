# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/evmcs_smm_controls_test.c

Purpose: Tests that VMX SMM exit/resume handling validates eVMCS/VMCS12 controls before re-entering nested guest mode on `RSM`. It is a targeted regression test for invalid nested controls during `vmx_leave_smm()`.

Important APIs/types/functions: The real-mode `smi_handler[]` reports `SMRAM_STAGE` then executes `RSM`; `sync_with_host()` does port I/O on `SYNC_PORT`; `l2_guest_code()` and `guest_code()` set up Hyper-V enlightenments, eVMCS, and nested VMX. Host setup uses `smm.h`, `hyperv.h`, `vmx.h`, SMRAM mapping, `vcpu_enable_evmcs()`, and Hyper-V test pages.

Control flow: The guest enables Hyper-V guest OS ID, VP assist, eVMCS, VMX operation, loads eVMCS, and launches L2. L2 syncs to host, then host injects an SMI path through the installed SMRAM handler. The test expects invalid controls to prevent successful return to L2; reaching the post-RSM `vmcall` path is a failure signal.

State and persistence behavior: Important state lives in SMRAM, eVMCS fields, Hyper-V VP assist pages, and nested VMX state. The test persists only within a single VM execution.

Dependencies and integration points: Requires VMX, Hyper-V enlightened VMCS support, SMM selftest helpers, and correct KVM interaction between SMM, eVMCS, and nested VM-entry validation.

Risks and maintenance notes: This is highly architecture- and KVM-internals-sensitive. eVMCS field layout, SMM handler staging, or nested control validation changes can require careful updates. The real-mode handler is raw opcodes, so edits are easy to break.

Test signals: Passing shows KVM refuses to re-enter nested guest mode from SMM with invalid eVMCS controls and exits in the expected host-observable way. Failure implies an SMM/nested VMX validation regression.
