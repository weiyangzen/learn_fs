# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.h

Purpose: this header exports the shared GFX9 helper surface used both by the base GFX9 callback table and by closely related ASIC-specific files such as Arcturus, Aldebaran, and GC 9.4.3.

Important APIs: declarations cover shared memory programming, PASID/VMID mapping, interrupt setup, compute HQD load/HIQ load/dump/occupancy/destroy, wave control, ATC mapping query, VM page-table base setup, CU occupancy, trap handler setup, queue acquire/release and queue-mask helpers, wave launch stall, debug trap enable/disable, trap override validation/programming, wave launch mode, address watch setup/clear, IQ wait retrieval and dequeue packet construction, HQD PQ address reporting, HQD reset, and SDMA doorbell reporting.

Control flow and integration: ASIC files include this header to compose their `kfd2kgd_calls` tables from generic GFX9 operations while overriding only the hardware-specific pieces. GC 9.4.3 uses queue acquire/release and base queue mask helpers, Arcturus and Aldebaran reuse most compute/VM functions, and Aldebaran/GC 9.4.3 share debug helpers through this surface where compatible.

State and persistence: the header itself is stateless. The declared functions mutate queue, VM, debug, watch, and hub registers and sometimes save queue pointers into MQDs.

Dependencies: consumers need `struct amdgpu_device`, `struct mm_struct`, `struct kfd_cu_occupancy`, KFD preemption/debug constants, user-pointer annotations, and fixed-width integer types. The header is a private driver contract.

Risks and test signals: this is a broad sharing boundary; signature or semantic changes can affect several ASIC generations. Some helpers are safe only for GFX9 register layouts, so new ASIC files should not reuse them without checking register offsets, hub topology, and debug-mask scope. Compile coverage catches API drift; runtime signals should include all callback-table consumers, multi-XCC queue selection, debug watchpoints, CU occupancy, and HQD reset/PQ introspection.
