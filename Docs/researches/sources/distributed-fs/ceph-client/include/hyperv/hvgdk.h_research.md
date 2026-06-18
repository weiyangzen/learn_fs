# sources/distributed-fs/ceph-client/include/hyperv/hvgdk.h

Source read summary: 309 lines, 7516 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvgdk.h` defines guest-facing Hyper-V data structures layered on the mini guest definitions, including enlightened VMCS/VMCB state, synthetic exit reasons, connection IDs, partition assist pages, and GPA unmap inputs.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_enlightened_vmcs`, `hv_vmcb_enlightenments`, `hv_partition_assist_pg`, `hv_connection_id`, `hv_input_unmap_gpa_pages`, `__packed`. Important constants/macros: `HV_LINUX_VENDOR_ID`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_NONE`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_IO_BITMAP`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_MSR_BITMAP`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_GRP2`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_GRP1`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_PROC`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_EVENT`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_ENTRY`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_EXCPN`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CRDR`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_CONTROL_XLAT`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_GUEST_BASIC`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_GUEST_GRP1`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_GUEST_GRP2`, `HV_VMX_ENLIGHTENED_CLEAN_FIELD_HOST_POINTER` and 7 more.

Control flow: Nested virtualization and Hyper-V guest code include this header when exchanging enlightenments and hypercall payloads with the hypervisor; the structures are copied into architected shared pages or hypercall input/output buffers.

State and persistence behavior: State is shared-memory ABI state, not file persistence. Fields such as VMCS clean bits, VMCB enlightenment controls, and assist pages persist as long as the guest/hypervisor shared page remains mapped.

Dependencies and integration points: It includes `hvgdk_mini.h`, `hvgdk_ext.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: The risk is binary-layout drift: packed fields, bitfields, and union aliases must exactly match Hyper-V TLFS expectations or nested virtualization, TLB flush, and assist-page flows can corrupt guest state.

Test signals: Compile with layout-sensitive KVM/Hyper-V users, run nested virtualization smoke tests, validate structure sizes/offsets against TLFS, and exercise enlightened VMCS/VMCB plus GPA unmap hypercalls.
