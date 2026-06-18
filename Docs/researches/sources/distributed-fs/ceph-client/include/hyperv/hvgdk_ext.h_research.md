# sources/distributed-fs/ceph-client/include/hyperv/hvgdk_ext.h

Source read summary: 47 lines, 1242 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/hyperv/hvgdk_ext.h` adds extended Hyper-V guest hypercall definitions, currently capability query and memory heat/cold-discard hint payloads.

Important APIs, types, and functions: Important exported functions or hooks: none. Important types: `hv_memory_hint`, `__packed`. Important constants/macros: `HV_EXT_CALL_QUERY_CAPABILITIES`, `HV_EXT_CALL_MEMORY_HEAT_HINT`, `HV_EXT_CAPABILITY_MEMORY_COLD_DISCARD_HINT`, `HV_MEMORY_HINT_MAX_GPA_PAGE_RANGES`, `HV_EXT_MEMORY_HEAT_HINT_TYPE_COLD_DISCARD`.

Control flow: Guest memory-management code can build `hv_memory_hint` ranges and issue an extended hypercall so the host can treat selected GPA ranges as cold or discardable.

State and persistence behavior: The only state is transient hypercall input. Host-side policy may persist the hint, but this header only defines the ABI layout and capability bits.

Dependencies and integration points: It includes `hvgdk_mini.h`. Integration is with the owning kernel subsystem implementation and any external ABI named by the structures or constants.

Risks and edge cases: Range counts are bounded by `HV_MEMORY_HINT_MAX_GPA_PAGE_RANGES`; callers must avoid overflowing the fixed array and must only use features advertised by the capability query.

Test signals: Check structure sizes, issue capability queries on Hyper-V, and test memory-hint calls with zero, one, and maximum range counts.
