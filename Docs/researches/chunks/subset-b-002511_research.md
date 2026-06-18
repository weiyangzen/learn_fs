# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 17381-19874

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it exposes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, display, MES, SDMA, and debug/register-dump paths to compose or decode 32-bit hardware register values. The matching register addresses live in the companion GC 11.0.0 offset header, normally `gc_11_0_0_offset.h`.

The selected range starts in the tail of `CP_HQD_PQ_CONTROL`, covers many CP/HQD compute queue, GDS, GUS, and GFX render-state registers, and ends at the start of `PA_SC_VPORT_SCISSOR_9_TL`. Although this repository subtree is under `ceph-client`, this file is AMD GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Consumers pair these macros with `reg*`, `mm*`, or `ix*` offset symbols and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

Major register groups in this chunk:

- CP/HQD queue and MQD state: the range starts with `CP_HQD_PQ_CONTROL` high-bit fields and continues through `CP_HQD_IB_*`, `CP_HQD_IQ_*`, `CP_HQD_DEQUEUE_REQUEST`, offload controls, semaphore/message/atomic pre-op registers, `CP_HQD_HQ_SCHEDULER*`, `CP_HQD_HQ_STATUS*`, `CP_HQD_HQ_CONTROL*`, `CP_MQD_CONTROL`, EOP queue pointers, context-save base/control/size, control-stack and work-group state offsets, GDS resource state, AQL control, PQ write pointers, suspend-state offsets, DDID pointers/counts, and dequeue status.
- TCP watchpoints: `TCP_WATCH0_ADDR_H/L` through `TCP_WATCH3_ADDR_H/L` and `TCP_WATCHn_CNTL` define address, mask, VMID, mode, and valid bits for texture/cache watchpoint style debug matching.
- GDS VMID resources: `GDS_VMID0_BASE/SIZE` through `GDS_VMID15_BASE/SIZE`, `GDS_GWS_VMID0` through `GDS_GWS_VMID15`, and `GDS_OA_VMID0` through `GDS_OA_VMID15` define per-VMID GDS base/size, global wave sync, and ordered-append allocation windows.
- GDS reset and context-switch accounting: `GDS_GWS_RESET*`, `GDS_GWS_RESOURCE_RESET`, `GDS_COMPUTE_MAX_WAVE_ID`, `GDS_OA_RESET_MASK`, `GDS_OA_RESET`, `GDS_CS_CTXSW_STATUS`, `GDS_CS_CTXSW_CNT*`, `GDS_GFX_CTXSW_STATUS`, `GDS_PS_CTXSW_CNT*`, `GDS_GS_CTXSW_CNT*`, `GDS_PS_CTXSW_IDX`, and `GDS_MEMORY_CLEAN`.
- GUS arbitration, QoS, credits, and counters: the `addressBlock: gc_gusdec` section covers IO and DRAM read/write combine flushes, age rates, age coefficients, fixed/urgent priority controls, quantization tables, group-burst controls, SDP arbitration/final controls, tag/VCC/VCD reserves, request controls, miscellaneous/error/latency controls, L1 channel and shader-array command/data counters, and write-response FIFO control.
- Initial GFX render backend state: the `addressBlock: gc_gfxdec0` section starts with DB depth/stencil render controls, count/depth view, render override, HTILE base and high base, depth bounds and clear values, Z/stencil read/write bases and high bases, RMI L2 cache control, TA base address, coherent destination base high/low registers, window and clip scissor state, clip rectangle rules, edge rules, hardware screen offset, color target and shader output masks, generic scissor state, and viewport scissor definitions from viewport 0 through the beginning of viewport 9.

Common field families include queue size, read/write pointer carry and offset, base addresses split into low/high halves, execution disable, cache policy, volatile status, processing/active flags, dequeue requests, context-save policy, AQL enable/packet size, VMID-local resource base and size, reset strobes, context-switch status/counts, priority groups, QoS reserves, error/status bits, depth/stencil mode bits, scissor coordinates, color-output enables, and 256-byte coherent destination bases. Full-width `0xFFFFFFFFL` masks occur on data, pointer, address, counter, and status payload registers.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from driver code and hardware:

1. ASIC-specific code includes `gc/gc_11_0_0_sh_mask.h` with compatible offset headers.
2. The caller selects a concrete GC, CP, GDS, GUS, or GFX register through offset macros.
3. It composes a write value or extracts a read value with the generated masks and shifts.
4. AMDGPU register helpers perform MMIO or indexed accesses, while surrounding code handles queue ownership, firmware/MES coordination, reset ordering, power management, and synchronization.

The CP/HQD fields participate in queue bring-up, MQD programming, MES queue loads, KFD queue creation, queue eviction/restore, AQL dispatch, and preemption/save-state handling. The GDS fields are programmed during VMID resource initialization and cleanup. The GFX DB/PA/CB fields are part of clear-state, render-state setup, display/plane interaction, and debug register dumps. The GUS fields describe hardware arbitration and counters; direct policy sequencing is outside this generated header.

## State And Persistence Behavior

This file stores no software state and persists nothing by itself. It describes GC 11.0.0 hardware state.

The CP/HQD portion describes live queue and MQD state: packet-queue control, IB base/progress, interrupt-queue timing, dequeue requests and status, queue scheduler/status/control words, EOP queue memory, context-save base/size/control, control-stack and work-group save offsets, AQL control, PQ write pointers, suspend-state offsets, and DDID counters. Some fields are driver-programmed configuration, some are firmware-owned or hardware-owned status, and some are action/request bits.

The GDS portion describes per-VMID allocation windows for GDS, GWS, and OA resources plus reset, cleanup, and context-switch accounting state. These registers are reinitialized during device bring-up, VMID setup, GDS resource assignment, reset recovery, and sometimes suspend/resume or context-switch flows.

The GUS portion describes arbitration policy, QoS reserves, combine flush controls, credits, latency sampling, error status, and internal command/data counters. These values may be static tuning, firmware/hardware-owned status, or debug/telemetry counters depending on the register.

The DB/PA/CB portion describes graphics pipeline render state: depth/stencil modes, HTILE/Z/stencil base addresses, depth bounds and clear values, screen/window/generic/viewport scissor rectangles, clip rectangles and edge rules, color target write masks, shader output masks, and coherent destination bases. Some of these are context state saved/restored by command streams or clear-state packets; others are base addresses or hardware status/configuration.

The masks do not encode access class. A field may be read-only, write-only, read/write, write-one-to-clear, self-clearing, sticky, reserved, privileged, or firmware-owned according to the hardware specification. Consumers must preserve unrelated and reserved bits when updating mixed-control registers.

## Dependencies And Integration Points

The direct generated dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which supplies matching register offsets such as `regCP_HQD_PQ_CONTROL`, `regCP_HQD_CTX_SAVE_CONTROL`, `regGDS_VMID0_BASE`, and DB/PA/CB register symbols. This shift/mask header must stay synchronized with that offset header and the ASIC register database.

Observed include and consumer points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`, which includes this header, lists CP/HQD registers for debug/register access, initializes GDS VMID resource registers, and programs CP/MES queue state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`, which builds MQD/HQD values with fields such as `CP_HQD_PQ_CONTROL`, then writes them for MES-managed queue setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c`, which use GC 11 CP/HQD masks for KFD/HSA queue descriptors and queue management.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`, which bridges AMDGPU and AMDKFD GFX11 queue/resource behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c`, which include the GC 11.0.0 masks for SOC21-era register programming or diagnostics.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.c`, which include the header for display/plane register field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx11.h`, where DB/PA/CB render-state registers from this range appear as clear-state entries such as `DB_RENDER_CONTROL`, `PA_SC_SCREEN_SCISSOR_TL`, `CB_TARGET_MASK`, and viewport scissor registers.

Important external integration surfaces are MES firmware, CP microcode, KFD user-mode queue ABI/MQD layout, GPU doorbell apertures, GDS resource allocation, VMID management, graphics command-stream state packets, reset/suspend/resume paths, and debugfs or register-dump tooling.

## Risks And Edge Cases

- Header/offset mismatch is the primary structural risk. These are untyped numeric constants, so pairing this GC 11.0.0 mask header with a different offset family can compile while programming the wrong bits.
- The chunk boundaries are artificial. The range starts after earlier `CP_HQD_PQ_CONTROL` shift definitions and ends after only the first field of `PA_SC_VPORT_SCISSOR_9_TL`; adjacent chunks are needed for complete first and last register definitions.
- CP/HQD queue registers are sequencing-sensitive. Incorrect queue size encoding, pointer carry handling, read-pointer block size, write-pointer mode, cache policy, TMZ, privilege, or KMD queue bits can break queue dispatch, MES scheduling, or KFD queue restore.
- Address fields have alignment and high/low split requirements. Examples include IB bases, EOP bases, context-save bases, Z/stencil/HTILE bases, TA bases, and coherent destination bases. Dropping low-bit shifts or high-half fields can redirect hardware to the wrong GPU address.
- Queue state and status fields are live and may change asynchronously. Polling `PROCESSING_IB`, `ACTIVE`, `QUEUE_IDLE`, dequeue status, DDID counters, or context-save status must handle transitions and timeouts.
- Dequeue, reset, clean, and offload fields can be action-like rather than passive configuration. Misusing them can leave queues stuck, drop work, or corrupt saved context.
- GDS/GWS/OA VMID windows are replicated 16 times. Off-by-one VMID arithmetic can assign resources to the wrong VMID or fail to clear stale allocations after reset or process teardown.
- GUS QoS, priority, and credit fields affect global fabric behavior. Incorrect static tuning can cause starvation, latency spikes, misleading counters, or workload-specific performance regressions without obvious functional failures.
- DB/PA/CB render-state fields interact with user command streams and clear state. Wrong scissor coordinates, clip rules, output masks, or depth/stencil settings can produce rendering corruption while the driver still boots normally.
- Full-width masks are not a writeability guarantee. Many full-width fields are counters, data windows, base payloads, or status registers and may be read-only or hardware-owned.
- Reserved bits and generation-specific field changes must be preserved. Similar register names in GFX9, GFX10, GFX11, and GFX12 have different field layouts in places, so backporting or copy-pasting register programming across generations is risky.

## Test Signals

Useful validation is mostly build, static consistency, hardware smoke, and ASIC-specific regression coverage:

- Build coverage for all files that include `gc_11_0_0_sh_mask.h`, especially `gfx_v11_0.c`, `mes_v11_0.c`, `kfd_mqd_manager_v11.c`, `kfd_device_queue_manager_v11.c`, display files, `sdma_v6_0.c`, `gfxhub_v3_0.c`, and `soc21.c`.
- Generated-header checks that every `__SHIFT` in this slice has a matching `_MASK`, masks align with shifts, fields within a register do not overlap except documented aliases, and every register name matches the GC 11.0.0 offset header.
- MQD/HQD tests that create, run, preempt, evict, restore, and destroy KFD/HSA queues; submit AQL packets; exercise doorbell and write-pointer paths; and verify queue idle/dequeue/status behavior.
- MES queue setup tests that validate programmed `CP_HQD_PQ_CONTROL`, IB, EOP, context-save, AQL, and scheduler/status/control fields against expected MQD contents.
- Reset, suspend/resume, GPU recovery, and runtime power-management tests with active compute queues, because CP/HQD queue state, context-save memory, GDS allocations, and GUS counters/configuration can be lost or stale.
- GDS tests that allocate per-VMID GDS/GWS/OA resources, switch VMIDs, tear resources down, and verify reset/clean status and context-switch counters.
- Graphics clear-state and rendering tests that cover depth/stencil clear/copy/decompress paths, HTILE/Z/stencil base programming, screen/window/generic/viewport scissor rectangles, clip rules, edge rules, color target masks, and shader output masks.
- Display/plane tests that exercise any paths relying on CB/PA/DB field definitions when programming or validating scanout-related GPU state.
- Debug/register-dump tests that read the CP/HQD, GDS, GUS, and GFX registers listed in this slice and decode fields without unknown-register or wrong-mask output.
- Regression indicators include stuck KFD queues, failed MES queue loads, non-idle HQD after drains, context-save timeouts, wrong GDS resource ownership, unexpected GPU resets, rendering clipped to the wrong rectangle, missing color writes, depth/stencil corruption, nonsensical GUS counters, or failures limited to GFX11/SOC21 devices.
