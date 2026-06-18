# sources/distributed-fs/ceph-client/include/hyperv/hvgdk_mini.h

Source read summary: 1544 lines, 45544 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvgdk_mini.h` is the core Hyper-V guest definition kit: status codes, hypercall numbers, MSRs, synthetic interrupt/VP assist layouts, VP-set formats, partition and isolation constants, VTL permissions, TLB flush inputs, and many register identifiers.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_u128`, `hv_reenlightenment_control`, `hv_tsc_emulation_status`, `hv_tsc_emulation_control`, `hv_output_get_partition_id`, `hv_reference_tsc_msr`, `hv_vpset`, `hv_hypervisor_version_info`, `hv_isolation_type`, `hv_x64_msr_hypercall_contents`, `hv_vp_assist_msr_contents`, `hv_guest_mapping_flush`, `hv_gpa_page_range`, `hv_guest_mapping_flush_list`, `hv_tlb_flush`, `hv_tlb_flush_ex` and 60 more. Important constants/macros: `HV_STATUS_SUCCESS`, `HV_STATUS_INVALID_HYPERCALL_CODE`, `HV_STATUS_INVALID_HYPERCALL_INPUT`, `HV_STATUS_INVALID_ALIGNMENT`, `HV_STATUS_INVALID_PARAMETER`, `HV_STATUS_ACCESS_DENIED`, `HV_STATUS_INVALID_PARTITION_STATE`, `HV_STATUS_OPERATION_DENIED`, `HV_STATUS_UNKNOWN_PROPERTY`, `HV_STATUS_PROPERTY_VALUE_OUT_OF_RANGE`, `HV_STATUS_INSUFFICIENT_MEMORY`, `HV_STATUS_INVALID_PARTITION_ID`, `HV_STATUS_INVALID_VP_INDEX`, `HV_STATUS_NOT_FOUND`, `HV_STATUS_INVALID_PORT_ID`, `HV_STATUS_INVALID_CONNECTION_ID` and 328 more.

Control flow: Low-level Hyper-V guest, KVM-on-Hyper-V, and architecture code include it to compose hypercalls, decode status codes, program synthetic MSRs, and share VP/interrupt/timer state with the hypervisor.

State and persistence behavior: State is external to the header but layout-critical: MSR bitfields, VP assist pages, reference TSC pages, synthetic interrupt controller fields, and hypercall input buffers are live ABI memory shared with Hyper-V.

Dependencies and integration points: It includes `linux/types.h`, `linux/bits.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: The file is broad and dense; the main risks are wrong bit numbering, missing packing, endian/layout assumptions, and accidental divergence from the TLFS as new status codes or hypercalls are added.

Test signals: Use build coverage on Hyper-V guest and KVM paths, static size/offset checks where available, hypercall status decoding tests, synthetic interrupt/timer smoke tests, and nested/isolated guest boot tests.
