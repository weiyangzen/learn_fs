# sources/distributed-fs/ceph-client/include/hyperv/hvhdk_mini.h

Source read summary: 551 lines, 13097 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvhdk_mini.h` provides the smaller host Hyper-V definition base shared by the full HVDK header: generic-set encodings, scheduler and statistics enums, partition/system property codes, VMM capabilities, SNP/TDX-related flags, GPA mapping permissions, and processor-property controls.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_generic_set_format`, `hv_scheduler_type`, `hv_stats_area_type`, `hv_stats_object_type`, `hv_stats_object_identity`, `hv_partition_property_code`, `hv_partition_property_vmm_capabilities`, `hv_snp_status`, `hv_system_property`, `hv_pfn_range`, `hv_sleep_state`, `hv_dynamic_processor_feature_property`, `hv_input_get_system_property`, `hv_output_get_system_property`, `hv_sleep_state_info`, `hv_input_set_system_property` and 42 more. Important constants/macros: `HV_MAX_CONTIGUOUS_ALLOCATION_PAGES`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_MASK`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_ANY`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_BYTE`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_WORD`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_DWORD`, `HV_DOORBELL_FLAG_TRIGGER_SIZE_QWORD`, `HV_DOORBELL_FLAG_TRIGGER_ANY_VALUE`, `HV_GENERIC_SET_SHIFT`, `HV_GENERIC_SET_MASK`, `HV_GENERIC_SET_FORMAT`, `HV_PARTITION_VMM_CAPABILITIES_BANK_COUNT`, `HV_PARTITION_VMM_CAPABILITIES_RESERVED_BITFIELD_COUNT`, `HV_PFN_RANGE_PGBITS`, `HV_MAP_GPA_PERMISSIONS_NONE`, `HV_MAP_GPA_READABLE` and 11 more.

Control flow: It is included by host control-plane code and by `hvhdk.h` so hypercall builders share the same property codes, bit masks, and packed payload shapes.

State and persistence behavior: No local storage exists. Values identify hypervisor-owned persistent objects such as partitions, statistics areas, memory mappings, and dynamic processor feature state.

Dependencies and integration points: It includes `hvgdk_mini.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: The risk is ABI mismatch in packed enums, property codes, and permission bits; mapping permissions in particular can overgrant access if composed incorrectly.

Test signals: Compile all HVDK users, check property and permission encodings against TLFS, and test GPA map/unmap plus property query/set hypercall flows.
