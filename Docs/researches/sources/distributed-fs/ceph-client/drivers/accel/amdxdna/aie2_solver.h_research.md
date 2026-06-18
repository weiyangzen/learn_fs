# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_solver.h

Purpose: defines the public contract for the AIE2 resource solver: partition descriptions, QoS capability/requirements, CDO relocation choices, allocation requests, load actions, power-level constants, clock lists, action callbacks, and solver init/allocate/release APIs.

Important APIs/types: `struct aie_part` names a start column and number of columns. `struct cdo_parts` carries legal start columns, column count, and QoS capacity for a relocatable CDO. `struct aie_qos` captures requested GOPS, FPS, DMA bandwidth, latency, execution time, and priority. `struct alloc_requests` binds a request ID to CDO and QoS. `struct xrs_action_ops` lets the solver ask the device layer to load/unload a partition and set default DPM level. `xrsm_init()`, `xrs_allocate_resource()`, and `xrs_release_resource()` are the exported solver lifecycle calls.

Control flow: device code initializes one solver per AIE array, then callers submit allocation requests when creating hardware contexts and release the request ID when tearing them down.

State and persistence: this header owns no state; it documents the in-memory state managed by `aie2_solver.c`. The comments explicitly state that the caller must provide locking.

Dependencies: depends on DRM device types and Linux fixed-width integer types through included translation units.

Risks: `XRS_MAX_COL` bounds bitmap-backed allocation; devices with more columns require changes. Caller-provided start-column arrays and QoS fields must be validated before or during allocation.

Test signals: ABI compile coverage for all solver clients, resource allocation with each power level, and negative tests for invalid CDO dimensions and missing callbacks.
