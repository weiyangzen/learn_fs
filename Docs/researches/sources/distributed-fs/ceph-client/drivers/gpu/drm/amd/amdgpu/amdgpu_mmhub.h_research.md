## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mmhub.h

Purpose: declares MMHUB RAS memory IDs, function table, client name mapping, device state, and RAS software initialization.

Important APIs/types: `enum amdgpu_mmhub_ras_memory_id` names MMHUB memory blocks used for RAS reporting. `struct amdgpu_mmhub_funcs` provides callbacks for framebuffer location, MC FB offset, init, GART enable/disable, fault defaults, clock/power gating, VM page table registers, and XGMI info. `struct amdgpu_mmhub_client_ids` and inline helpers map client IDs to read/write names. `struct amdgpu_mmhub` stores RAS interface, function table, RAS object, and client ID names.

Control flow contract: ASIC-specific MMHUB code installs function table and optional client ID map. Generic memory-management code calls the callbacks for GART and VM setup; RAS setup calls `amdgpu_mmhub_ras_sw_init()`.

State and persistence: runtime state only: callback pointers, RAS pointer/interface, and client name table.

Dependencies/integration: used by GMC/VM setup, page fault reporting, RAS, XGMI, and power management.

Risks: client name lookup returns `NULL` for out-of-range IDs, so fault-reporting callers must handle missing names. GART and VM callbacks are required for functional memory management on supported ASICs but are optional at the type level.

Test signals: GART enable/disable, VM PT register setup, MMHUB page fault decoding with client names, clock/power-gating tests, and RAS registration.
