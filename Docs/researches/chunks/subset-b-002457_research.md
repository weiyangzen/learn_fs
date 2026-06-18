# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 19838-22333

## Purpose

This chunk is a generated AMD GC 10.1.0 shift/mask header slice. It contains C preprocessor constants for register-field bit positions and masks; it has no executable driver logic. AMDGPU and AMDKFD code combine these constants with `gc_10_1_0_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, and `RREG32_SOC15` to program or decode GFX10 graphics, compute, queue, cache, debug, power-management, and render backend registers without open-coded bit numbers.

The requested range starts in the repeated `SPI_RESOURCE_RESERVE_CU_*` family, covers all of `SPI_RESOURCE_RESERVE_EN_CU_0..15`, moves through the `gc_cpphqddec` CP/MQD/HQD queue register block, then covers DIDT/CAC throttling, TCP watchpoint and TCP UTCL/performance-filter registers, GDS per-VMID/GWS/OA/context-switch state, and the beginning of `gc_gfxdec0` depth/color/scissor state. It ends inside `PA_SC_VPORT_SCISSOR_12_TL`, so the complete viewport scissor register family continues in the next chunk.

Although this path is under a local `ceph-client` source mirror, this file is AMD GPU driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, variables, locks, allocations, or exported symbols in this range. The interface is entirely the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field.
- `// addressBlock: ...`: generated boundaries for hardware register decoder blocks.

Major macro families in this chunk are:

- `SPI_RESOURCE_RESERVE_CU_6..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15`: per-CU shader processor resource reservation fields for VGPR, SGPR, LDS, waves, barriers, enable, type mask, queue mask, and reserve-space-only behavior. These describe how SPI can reserve shader resources for selected compute queues or types.
- `SPI_COMPUTE_WF_CTX_SAVE`, `SPI_ARB_CNTL_0`, `SPI_FEATURE_CTRL`, and `SPI_SHADER_RSRC_LIMIT_CTRL`: shader/dispatch control fields for wave context-save activity, arbitration fairness/credits, feature bits, and shader resource limit behavior.
- `CP_HPD_*`, `CP_MQD_*`, and `CP_HQD_*`: command processor high-priority dispatch, MQD base/control, and hardware queue descriptor fields. These include queue active state, VMID, persistent/preload/QoS/context-switch state, pipe/queue priority, quantum, packet queue base/read/write pointers, doorbell control, packet queue control, IB/IQ control, dequeue requests, semaphore/message/atomic state, HQ scheduler/status/control, EOP base/control/pointers/events, CWSR context-save addresses/sizes/offsets, GDS resource state, error reporting, AQL control, suspend offsets, DDID counters, and dequeue status.
- `DIDT_*`, `GC_CAC_*`, `GC_DIDT_*`, `GC_THROTTLE_*`, `GC_EDC_*`, `EDC_PERF_COUNTER`, `PCC_PERF_COUNTER`, `PWRBRK_PERF_COUNTER`, `GC_CAC_IND_*`, and `SE_CAC_IND_*`: dynamic instruction-dependent throttling, current/activity control, electrical design current, power-brake/PCC throttling, threshold/status/overflow, and indirect CAC access fields.
- `TCP_WATCH0..3_*`, `TCP_CNTL2`, `TCP_UTCL0_CNTL1/2`, `TCP_UTCL0_STATUS`, and `TCP_PERFCOUNTER_FILTER*`: texture cache processor address watchpoints, cache/clock/return-order controls, UTCL0 translation/cache invalidation and fault status, and performance-counter filter selection/enables.
- `GDS_VMID0..15_BASE/SIZE`, `GDS_GWS_VMID0..15`, `GDS_OA_VMID0..15`, `GDS_GWS_RESET0/1`, `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, `GDS_OA_RESET`, `GDS_ENHANCE2`, `GDS_OA_CGPG_RESTORE`, and `GDS_*_CTXSW_*`: global data share per-VMID allocation, global wave sync, ordered append, reset/resource reset, clock/power restore, and context-switch counter/status fields.
- `DB_RENDER_CONTROL`, `DB_COUNT_CONTROL`, `DB_DEPTH_VIEW`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_Z_INFO`, `DB_STENCIL_INFO`, depth/stencil read/write bases, HTILE base/size, bounds/clear values, RMI L2 cache controls, `TA_BC_BASE_ADDR*`, `COHER_DEST_BASE*`, and `PA_SC_*`/`CB_*` fields: early graphics render backend state for depth/stencil, HTILE, coherency destinations, window/clip/generic/viewport scissors, target masks, and shader output masks.

The most visible consumers in this tree are GFX10 KFD and AMDGPU paths. `kfd_mqd_manager_v10.c` initializes and updates `struct v10_compute_mqd` fields with `CP_HQD_*` and `CP_MQD_*` shifts/masks. `amdgpu_amdkfd_gfx_v10.c` writes CP HQD registers when loading/unloading queues and programs `TCP_WATCH0_CNTL` fields for debugger watchpoints. `gfx_v10_0.c` uses these fields for KIQ/compute MQD setup, GDS VMID initialization, and debug register dump lists.

## Control Flow

This header has no runtime control flow. Its influence appears after macro expansion in driver code:

1. A GFX10 consumer selects a register offset from the matching offset header.
2. The consumer uses shift/mask macros directly or via helper macros to construct, clear, extract, or test fields.
3. AMDGPU/AMDKFD register helpers write or read the selected MMIO register, often after selecting a GRBM/SRBM instance, VMID, MEC, pipe, or queue.
4. Hardware state machines, firmware, the command processor, shader processor, TCP, GDS, or graphics backend perform the actual work.

Queue setup is the clearest operational path. KFD allocates and fills a v10 MQD, encoding queue size, doorbell offset, base pointers, VMID, priority, AQL mode, EOP size, preload state, and CWSR context-save locations with these masks. `kgd_hqd_load` then selects the target MEC/pipe/queue, streams the MQD/HQD register window from `CP_MQD_BASE_ADDR` through `CP_HQD_PQ_WPTR_HI`, enables the doorbell, seeds write-pointer polling, initializes the EOP fetcher, and activates `CP_HQD_ACTIVE`.

Debugger watchpoints follow a smaller sequence: build TCP and SQ watch control words with VMID, mode, mask, and `VALID`; write the control register disabled; write high/low address registers; then set `VALID` so a partially programmed watchpoint is not exposed.

GDS initialization loops over VMIDs and clears `GDS_VMID*_BASE`, `GDS_VMID*_SIZE`, `GDS_GWS_VMID*`, and `GDS_OA_VMID*` so compute/user VMIDs start with no GDS/GWS/OA access until firmware or driver ownership grants it.

## State And Persistence Behavior

The macros are stateless compile-time constants. The state they describe lives in GPU registers, MQD memory, ring buffers, writeback memory, doorbell aperture state, firmware-owned scheduling structures, and render/queue hardware.

Persistent or semi-persistent state named in this chunk includes:

- MQD/HQD memory and register state for queue base addresses, read/write pointers, queue size, active state, VMID, priority, quantum, doorbells, AQL mode, IB/IQ/EOP rings, semaphore/message status, context-save addresses and stack offsets, suspend offsets, and dequeue status.
- User/debug state for TCP watchpoint address/mask/mode/VMID/valid registers and UTCL0 fault/retry/PRT status.
- Per-VMID GDS, GWS, and OA base/size/ownership state plus reset and context-switch counters.
- Power/throttle state for DIDT, CAC, EDC, PCC, and power-brake counters, thresholds, status, overrides, and indirect tables.
- Graphics pipeline state for depth/stencil buffers, HTILE, DB render overrides, coherency destinations, color target masks, shader output masks, and scissor rectangles.

Reset and persistence are hardware-defined. Some fields are volatile status bits, some are write-one-to-clear or self-clearing requests, some are saved in MQDs across queue eviction/preemption, and some are reset during GPU reset, mode reset, queue teardown, suspend/resume, or power/clock gating. This chunk does not define reset values, legal enum values, ordering constraints, access widths, or ownership rules.

## Dependencies And Integration Points

This generated header must stay synchronized with the GC 10.1.0 register database and the matching offset header. It also depends on shared AMDGPU register helper conventions that token-paste register and field names.

Key integration points include:

- `drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which supplies register offsets matching these field names.
- `drivers/gpu/drm/amd/include/v10_structs.h`, whose `struct v10_compute_mqd` layout mirrors the CP MQD/HQD register window used by the `CP_*` macros in this chunk.
- AMDKFD queue management in `kfd_mqd_manager_v10.c`, `kfd_packet_manager_v9.c`, and `kfd_device_queue_manager_v10.c`, which uses the HQD/MQD/GDS masks to map processes, queues, GDS/GWS/OA resources, and debugger state.
- AMDGPU GFX10 code in `gfx_v10_0.c`, `amdgpu_amdkfd_gfx_v10.c`, `gfxhub_v2_0.c`, and `mxgpu_nv.c`, which programs queues, initializes GDS VMID state, decodes debug registers, handles SR-IOV paths, and exposes KFD callbacks.
- Graphics command streams and clear-state tables that rely on matching DB, CB, PA_SC, and coherency register layouts for render state.
- Hardware firmware/scheduler ownership for HWS/MES, CWSR, AQL queues, CP dequeue/offload paths, GDS save/restore, and power/throttle controls.

The chunk crosses several generated address blocks: the tail of shader/SPI resource definitions, `gc_cpphqddec`, `gc_didtdec`, `gc_gccacdec`, `gc_tcpdec`, `gc_gdspdec`, and the beginning of `gc_gfxdec0`. The merge lane should preserve those boundaries because each block has different owners and validation signals.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask compiles cleanly but can corrupt queue descriptors, route doorbells incorrectly, expose the wrong VMID, disable caches, or program render state incorrectly.
- The file is generated. Manual edits risk divergence from AMD's register database, firmware expectations, silicon documentation, and companion offset headers.
- The requested first line starts in the middle of `SPI_RESOURCE_RESERVE_CU_5`; the register comment and shift definitions are in the previous chunk. This chunk then covers complete `CU_6..15` and enable groups.
- The requested last line stops inside `PA_SC_VPORT_SCISSOR_12_TL`; the remaining `PA_SC_VPORT_SCISSOR_12_TL` masks and later viewport scissor registers are outside this work item.
- CP HQD/MQD fields are sequencing-sensitive. Queue load/unload, dequeue request, EOP fetcher initialization, doorbell enable, write-pointer polling, CWSR state, and active-bit transitions must be ordered correctly and under the right GRBM/SRBM selection.
- Address fields often encode shifted GPU addresses, such as 256-byte or dword alignment. Using raw byte addresses with these masks can silently point queues, EOP buffers, context save areas, depth/stencil buffers, or coherency destinations at the wrong memory.
- Queue size fields encode powers of two. Incorrect values can break write-pointer wrap logic, read-pointer reporting, EOP sizing, or the driver's queue overflow assumptions.
- Watchpoint masks use different address granularities across TCP and SQ. The GFX10 watchpoint code shifts TCP masks by 7 and SQ masks by 6; mixing the definitions can miss or over-trigger debugger traps.
- GDS/GWS/OA fields are per-VMID resources. Bad masks can leak access across processes or leave resources uncleared after process teardown, reset, or firmware scheduling changes.
- DIDT/CAC/EDC/throttle fields affect power, clocks, and stalls. Incorrect values may only show up as performance loss, thermal throttling, intermittent hangs, or board/ASIC-specific failures.
- DB/CB/PA_SC fields are graphics-pipeline state. Incorrect masks can cause depth/stencil corruption, broken clears/decompression, wrong scissor/clipping, missing color exports, or render-target coherency problems.

## Test Signals

Useful validation for this generated header and its consumers includes:

- Build GFX10 AMDGPU/AMDKFD configurations that include `gc_10_1_0_sh_mask.h`; missing or renamed field macros should break queue, KFD, and GFX compilation.
- Mechanically compare this range against the authoritative GC 10.1.0 register database and the matching offset header, especially around address-block boundaries.
- Boot GFX10 hardware with KFD enabled, create/destroy AQL and PM4 compute queues, use doorbells, exercise preemption/dequeue, and verify `CP_HQD_ACTIVE`, read/write pointers, EOP events, and queue priorities via debug dumps.
- Exercise CWSR/debug paths: context save/restore, debugger attach, address watchpoint set/clear, trap VMID selection, and wave state retrieval.
- Validate GDS/GWS/OA allocation and teardown with multiple processes/VMIDs, including reset and suspend/resume paths, checking that per-VMID base/size/resource registers are cleared or restored as expected.
- Run graphics render tests that cover depth/stencil clears, HTILE, decompression, scissor/window/clip rectangles, color target masks, and shader export masks.
- Monitor UTCL/TCP status, GDS protection faults, CP HQD error registers, EOP events, dequeue status, and GPU reset logs for faults that map back to fields in this chunk.
- Run power/performance stress tests across thermal and power limits to catch DIDT/CAC/EDC/throttle field regressions.

## Cross-Chunk Notes

The previous chunk owns the start of `SPI_RESOURCE_RESERVE_CU_5`; this chunk begins with its last mask lines, then covers complete SPI reservation enable groups, CP HQD/MQD queue state, TCP/GDS blocks, and the first part of `gc_gfxdec0`.

The next chunk should continue from `PA_SC_VPORT_SCISSOR_12_TL`, completing that register and the remaining viewport scissor/render backend definitions. A final per-file report should treat this document as one slice of a much larger generated GC 10.1.0 register map rather than as standalone driver logic.
