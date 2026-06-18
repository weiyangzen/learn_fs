# sources/distributed-fs/ceph-client/include/hyperv/hvhdk.h

Source read summary: 956 lines, 23516 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvhdk.h` defines host/direct-kernel Hyper-V control-plane structures for partition creation, initialization, properties, processor features, intercepts, synthetic MSRs, registers, ports, messages, and VSM/VTL operations.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_stats_page`, `hv_vp_register_page_interrupt_vectors`, `hv_vp_register_page`, `hv_partition_processor_features`, `hv_partition_processor_xsave_features`, `hv_partition_creation_properties`, `hv_partition_synthetic_processor_features`, `hv_partition_isolation_properties`, `hv_input_create_partition`, `hv_output_create_partition`, `hv_input_initialize_partition`, `hv_input_finalize_partition`, `hv_input_delete_partition`, `hv_input_get_partition_property`, `hv_output_get_partition_property`, `hv_input_set_partition_property` and 64 more. Important constants/macros: `HV_X64_REGISTER_CLASS_GENERAL`, `HV_X64_REGISTER_CLASS_IP`, `HV_X64_REGISTER_CLASS_XMM`, `HV_X64_REGISTER_CLASS_SEGMENT`, `HV_X64_REGISTER_CLASS_FLAGS`, `HV_VP_REGISTER_PAGE_VERSION_1`, `HV_VP_REGISTER_PAGE_MAX_VECTOR_COUNT`, `HV_PARTITION_PROCESSOR_FEATURES_BANKS`, `HV_PARTITION_SYNTHETIC_PROCESSOR_FEATURES_BANKS`, `HV_COMPATIBILITY_21_H2`, `HV_PARTITION_ISOLATION_TYPE_NONE`, `HV_PARTITION_ISOLATION_TYPE_SNP`, `HV_PARTITION_ISOLATION_TYPE_TDX`, `HV_PARTITION_ISOLATION_HOST_TYPE_NONE`, `HV_PARTITION_ISOLATION_HOST_TYPE_HARDWARE`, `HV_PARTITION_ISOLATION_HOST_TYPE_RESERVED` and 30 more.

Control flow: Hyper-V host-side or VMM code uses these definitions to create partitions, configure virtual processors, set partition properties, map GPA pages, send synthetic interrupts, and manage partition lifecycle through hypercalls.

State and persistence behavior: The state described here is partition and VP configuration held by the hypervisor. Header structs are serialized into hypercall input/output pages and must remain layout-compatible for the lifetime of the ABI.

Dependencies and integration points: It includes `linux/build_bug.h`, `hvhdk_mini.h`, `hvgdk.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Feature banks, isolation settings, register classes, and nested unions are easy to misuse; a wrong property code or feature bit can create an unsupported partition shape or expose the wrong CPU capability set.

Test signals: Validate struct sizes with `BUILD_BUG_ON` users, create/destroy test partitions, exercise processor feature negotiation, register get/set paths, GPA mapping, and isolated-partition configurations.
