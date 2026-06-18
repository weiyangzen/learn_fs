# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.h

## Purpose

`dcn20_resource.h` declares the public DCN 2.0 resource-pool interface and reusable helper APIs shared by later DCN resource implementations. It exposes the `dcn20_resource_pool` wrapper, DCN2.0 SoC/IP bounding-box globals, resource-pool construction, hardware block factories, stream/resource operations, bandwidth validation, pipe split/merge helpers, DSC management, writeback arbitration, and unknown-plane patching.

## Important APIs, Types, And Functions

- `TO_DCN20_RES_POOL()` casts a generic `resource_pool` pointer to the DCN20 pool container.
- `struct dcn20_resource_pool` embeds `struct resource_pool base`.
- Extern bounding boxes and IP params: `dcn2_0_ip`, `dcn2_0_nv14_ip`, `dcn2_0_soc`, `dcn2_0_nv14_soc`, and `dcn2_0_nv12_soc`.
- Construction/factory declarations cover resource pool, link/stream encoder, hwseq, DPP/IPP/OPP/HUBP/TG/MPC/HUBBUB/AUX/I2C/DSC/DWB/MCIF_WB, and clock-source destruction.
- Resource-management declarations cover acquiring/releasing pipes and DSCs, adding/removing streams, adding DSC resources, building mapped resources, building pixel-clock parameters, validating bandwidth and DSC, fast bandwidth validation, applying split flags, ODM/MPC split helpers, pipe merge, DCC cap query, writeback arbitration, and unknown-plane patching.

## Control Flow

The header has no runtime control flow. It lets the generic DC resource manager and sibling generation files call the DCN20 implementation. Typical use starts with `dcn20_create_resource_pool()`, then the returned pool's `resource_funcs` dispatches to the declared functions as streams and planes are validated, mapped, split, programmed, or removed.

## State And Persistence Behavior

The header stores no state. Its declarations are for functions that mutate caller-owned `dc`, `dc_state`, `resource_context`, `pipe_ctx`, stream, plane, and pool state. The extern DML bounding-box objects are process-global kernel data defined elsewhere and patched by implementation code during initialization or bandwidth updates.

## Dependencies And Integration Points

The header includes `core_types.h` and `dml/dcn20/dcn20_fpu.h`, so it exposes DC core types plus DML/FPU-related pipe parameter types. It is included by `dcn20_resource.c` and by later generation files such as DCN201, DCN21, and DCN30 that reuse DCN20 helpers for validation, stream mapping, DSC, writeback, and pipe topology operations.

## Risks And Edge Cases

- This is a broad internal API. Signature drift can break several generations, not just DCN20.
- Exposing FPU/DML declarations through the header couples non-FPU resource code to FPU wrapper discipline in implementations.
- The helper names do not all encode their mutation scope; callers must know which functions clear or rebuild pipe topology and which require acquired resources.
- Extern bounding boxes are mutable shared generation data; consumers must avoid assuming they are immutable constants.

## Test Signals

Kernel builds catch missing prototypes, include-order problems, and type drift. Cross-generation compile coverage is especially important because DCN201/DCN21/DCN30 call these APIs. Runtime validation should exercise all vtable paths declared here through resource-pool construction, stream add/remove, bandwidth validation, pipe split/merge, DSC allocation, DCC cap query, and writeback arbitration.
