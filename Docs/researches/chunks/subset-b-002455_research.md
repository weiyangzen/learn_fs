# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 14881-17383

## Scope

This chunk is a generated AMD GC 10.1.0 shift/mask header slice. The requested range spans 2,503 source lines, 2,134 `#define` entries, 1,067 `__SHIFT` definitions, 1,067 matching `_MASK` definitions, and 365 visible register-group comments. It starts at `GCEA_ADDRDEC1_ADDR_MASK_SECCS23` and ends on the `COMPUTE_USER_DATA_0` comment, before that compute user-data register's field definitions appear.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU graphics/compute hardware metadata. It is declarative C preprocessor data for GC 10.1.0 register bitfields, not Ceph or distributed-filesystem logic.

## Purpose

`gc_10_1_0_sh_mask.h` gives AMDGPU and AMDKFD code symbolic bit positions and masks for GC 10.1.0 registers. Consumers combine these constants with companion register offsets from `gc_10_1_0_offset.h` and with MMIO/register helper macros to compose, update, and decode hardware register values without open-coding raw bit numbers.

This chunk covers four major register areas:

- `GCEA_*`: graphics client external/address and I/O arbitration metadata, including address decode selectors, client-to-group mappings, read/write combine flushing, burst control, priority age/queue/fixed/urgency controls, urgency masking, quantized priority, SDP arbitration, credits, tag reserves, and VCC/VCD reserves.
- `TCP_*` and `TCI_*`: texture/cache control and status fields for invalidation, force hit/miss behavior, buffer address hashing, EDC counters, credits, and TCI control.
- `SPI_SHADER_*`: graphics shader program state for pixel, vertex, geometry, export, hull, and local shader stages, including program base addresses, resource words, checksums, user data registers, shader request controls, preferred-priority counters, accumulators, and cross-stage resource words such as GS/VS, ES/GS, and LS/HS.
- `COMPUTE_*`: compute dispatch state, dimensions, starts, thread counts, program resources, VMID, CU enable/static-thread-management masks, temp ring sizing, restart coordinates, tracing, dispatch IDs, request controls, priority accumulators, checksum, relaunch, and wave restore address fields.

## Important APIs, Types, And Macros

There are no callable functions, structs, enums, global variables, allocations, locks, or runtime register accesses in this range. The exported interface is only generated preprocessor constants of the form:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field inside a GC 10.1.0 register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field inside the same register.

Important macro families include:

- `GCEA_ADDRDEC1_*`: chip-select and secondary chip-select address masks, address geometry fields such as bank groups, rows, columns, banks, high-column enable, row/bank/column selection fields, row-map selection, channel bit, and even/odd row-MSB inversion.
- `GCEA_IO_*`: read/write client-to-group maps for 32 client IDs, combine flush controls, group burst enable, priority aging, queueing, fixed priority, urgency thresholds, urgency masks per CID, and priority quantum fields.
- `GCEA_SDP_*`: DRAM and final arbitration weights, urgency override/age/limit thresholds, page-hit sensitivity, per-source DRAM and I/O priorities, credit counts, tag reserve windows, and VCC/VCD reserve fields.
- `TCP_*` and `TCI_*`: invalidation command, busy and last-vmid status, forced cache hit/miss controls, cache sizing/swizzle/hash controls, EOW counts, EDC count, credit count, and TCI miscellaneous control fields.
- `SPI_SHADER_PGM_*_{PS,VS,GS,ES,HS,LS}`: shader program base low/high addresses, resource words for VGPR/SGPR counts, priority, float mode, privilege, DX10 clamp, IEEE mode, scratch/user-SGPR/trap/exception/LDS fields, wave limits, CU enables, WGP or shared VGPR controls, and program checksum fields.
- `SPI_SHADER_USER_DATA_*`: per-stage user-data payload registers. PS, VS, GS, and HS expose 32 user data slots in this slice; ES and LS expose 16 slots.
- `SPI_SHADER_REQ_CTRL_*`, `SPI_SHADER_PREF_PRI_*`, and `SPI_SHADER_USER_ACCUM_*`: shader request grouping, allocation throttling, lock thresholds, preferred-priority counter hierarchy/coefficient fields, and user/preferred contribution accumulators for PS, VS, ESGS, and LSHS.
- `COMPUTE_*`: dispatch initiator bits, dimensions/start/restart registers, thread count split fields, pipeline/perf counter enables, program and dispatch packet addresses, scratch base, program resource words, VMID, resource limits, shader-engine CU enables, static thread-management masks, temp-ring sizing, request controls, accumulators, checksum, relaunch payload/type bits, and wave restore address fields.

The chunk ends after the `COMPUTE_USER_DATA_0` comment only. The `COMPUTE_USER_DATA_0` field definitions are owned by the next chunk.

## Control Flow

This header has no local control flow. Runtime behavior comes from AMDGPU and AMDKFD code that includes this header and writes GC registers or queue descriptors using the generated constants.

Typical usage is:

1. A GC 10.1.0 driver file includes `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
2. Driver code builds a register value by shifting a field value by `<REGISTER>__<FIELD>__SHIFT` and masking with `<REGISTER>__<FIELD>_MASK`, or it passes these constants to AMD register update macros.
3. The value is written to MMIO registers, firmware-visible MQD fields, or command/queue state that the GPU consumes.
4. Hardware graphics, compute, cache, arbitration, and shader-dispatch state machines interpret those bits.

The header does not encode ordering constraints, polling loops, access widths, reset values, clear-on-read/write-one-to-clear behavior, or privilege rules. Those semantics live in the hardware database and in consumers such as `gfx_v10_0.c`, KFD queue/MQD management, gfxhub setup, SDMA setup, and SR-IOV code.

## State And Persistence Behavior

No software state is stored or persisted by this chunk. The named fields describe hardware-visible register state whose lifetime is governed by GC reset, power, queue, VM, and firmware domains.

State described by the chunk includes:

- Address decode and memory-routing configuration in `GCEA_ADDRDEC1_*`, including chip-select geometry and bank/row/column selection. Incorrect values affect how physical addresses are interpreted by the graphics memory path.
- I/O arbitration state in `GCEA_IO_*` and `GCEA_SDP_*`, including client grouping, burst control, priority, urgency, credit, and reserve tuning. These fields affect fairness, latency, and throughput rather than data structure persistence in software.
- Texture/cache state in `TCP_*` and `TCI_*`, including invalidation commands, busy/status readback, credits, hash controls, and EDC counters.
- Graphics shader execution state in `SPI_SHADER_*`, including per-stage program locations, resource allocation, wave limits, CU masks, user data payloads, scratch/trap/exception/LDS fields, and priority accounting.
- Compute dispatch state in `COMPUTE_*`, including dispatch geometry, shader entry point, scratch base, resource usage, VMID, CU targeting, restart coordinates, relaunch/wave-restore support, and tracing/performance enables.

Fields named `STATUS`, `BUSY`, `CNT`, `COUNT`, `CHECKSUM`, `ID`, `THREADGROUP_ID`, or `*_ACCUM_*` are readback or accounting oriented by name. Fields named `CNTL`, `CTRL`, `CFG`, `SEL`, `MASK`, `LIMITS`, `EN`, `ENABLE`, `INITIATOR`, `PREF_PRI`, and `RESOURCE` are configuration oriented by name. Actual read/write permissions and sticky behavior must be taken from the hardware specification and caller context.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this generated header must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which supplies matching register offsets and base-index values.
- AMD's GC 10.1.0 register database and any scripts that generate offset and shift/mask headers.
- Firmware and queue descriptor layouts for GFX10/Navi-class graphics and compute engines, especially where KFD MQD fields mirror hardware register fields.

Direct include sites in this tree include `amdgpu/gfx_v10_0.c`, `amdgpu/gfxhub_v2_0.c`, `amdgpu/nv.c`, `amdgpu/mxgpu_nv.c`, `amdgpu/amdgpu_amdkfd_gfx_v10.c`, `amdgpu/sdma_v5_0.c`, `amdkfd/kfd_mqd_manager_v10.c`, `amdkfd/kfd_device_queue_manager_v10.c`, and `amdkfd/kfd_packet_manager_v9.c`. These consumers use the GC 10.1.0 register contract for graphics initialization, queue setup, KFD compute queue descriptors, VM/gfxhub programming, SDMA integration, SR-IOV virtualization, and runtime register programming.

Behaviorally, this chunk integrates with:

- Graphics pipeline programming for PS, VS, GS, ES, HS, and LS shader stages.
- Compute dispatch and KFD queue setup, including resource words, static CU masks, scratch, temp-ring, VMID, dispatch geometry, and trap/exception controls.
- Cache and memory-system management, including TCP invalidation/status and address decode/arbitration settings.
- Priority, scheduling, and resource allocation controls for graphics and compute waves.
- GPU reset, suspend/resume, firmware bring-up, and virtualization paths that must restore or sanitize hardware state.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but can write the wrong shader resource, dispatch, cache-control, address-decode, or arbitration bit.
- This range starts at a normal register group but ends on a register comment with no fields for `COMPUTE_USER_DATA_0`. The final per-file merge must avoid treating that as an empty register definition.
- `_MASK` macro naming uses the generated AMD convention where field names ending in `MASK` produce names such as `GCEA_ADDRDEC1_ADDR_MASK_SECCS23__ADDR_MASK_MASK`; tooling must not collapse those suffixes.
- Shader resource words are dense and stage-specific. PS, VS, GS, ES, HS, LS, and compute registers share similar field names but not always identical layouts, so cross-stage copy assumptions can corrupt program resource setup.
- Compute resource fields such as `TGID_*_EN`, `TIDIG_COMP_CNT`, `LDS_SIZE`, `EXCP_EN`, `WGP_MODE`, `MEM_ORDERED`, and `FWD_PROGRESS` affect queue ABI and kernel execution semantics. Incorrect values can cause hangs, bad dispatch dimensions, trap mishandling, or silent shader misexecution.
- CU enable/static-thread-management registers are per-shader-engine. Mask mistakes can disable work on valid CUs or target disabled/fused-off units, producing performance loss or dispatch failures.
- Address decode and GCEA arbitration fields can affect memory routing, quality of service, and fairness across clients. These are hardware-tuning registers rather than ordinary software policy knobs.
- Status, command, control, reserved, and readback fields are represented by identical `#define` syntax. Callers need hardware access metadata to avoid writing status or reserved bits incorrectly.
- Cache invalidation and busy/status fields can be sequencing-sensitive. Wrong bit definitions may result in incomplete invalidation, polling the wrong status bit, or over-flushing.

## Test Signals

Useful validation is mostly build-time, generator-level, and hardware-integration oriented:

- Compile or preprocess AMDGPU and AMDKFD GFX10/Navi paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
- Mechanically verify that every complete field in this slice has one `__SHIFT` and one `_MASK` definition, with the explicit end-boundary exception for the `COMPUTE_USER_DATA_0` comment.
- Cross-check field names, shifts, and masks against AMD's authoritative GC 10.1.0 register database and the matching offset header.
- Diff repeated shader-stage families for intentional layout differences across PS, VS, GS, ES, HS, LS, ESGS, LSHS, and compute.
- Exercise KFD queue creation/destruction, MQD initialization, trap handling, scratch/temp-ring allocation, CU-mask programming, and compute dispatch on GC 10.1.0 hardware or emulation.
- Exercise graphics shader pipeline setup across pixel, vertex, geometry, tessellation/hull/local/export paths, including user-data programming and shader checksum/resource registers.
- Run reset, suspend/resume, SR-IOV, and GPU recovery flows while checking that shader, compute, cache, GCEA, and arbitration registers are restored or reinitialized correctly.
- Use register dumps around dispatch and graphics workloads to confirm decode of `COMPUTE_PGM_RSRC*`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE*`, `SPI_SHADER_PGM_RSRC*`, `TCP_STATUS`, and GCEA priority/arbitration fields.

## Chunk Notes For Merge

This document intentionally covers only lines 14881-17383 of `gc_10_1_0_sh_mask.h`. Adjacent chunks must provide earlier GCEA definitions and the `COMPUTE_USER_DATA_0` fields that follow this range. The final per-file research document should treat this source as generated AMD GC 10.1.0 register bitfield metadata used by AMDGPU/AMDKFD, not as handwritten runtime logic.
