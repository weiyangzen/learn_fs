# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002526`: lines 1-2557, `Docs/researches/chunks/subset-b-002526_research.md`
- `subset-b-002527`: lines 2558-5102, `Docs/researches/chunks/subset-b-002527_research.md`
- `subset-b-002528`: lines 5103-7503, `Docs/researches/chunks/subset-b-002528_research.md`
- `subset-b-002529`: lines 7504-9879, `Docs/researches/chunks/subset-b-002529_research.md`
- `subset-b-002530`: lines 9880-12211, `Docs/researches/chunks/subset-b-002530_research.md`
- `subset-b-002531`: lines 12212-14595, `Docs/researches/chunks/subset-b-002531_research.md`
- `subset-b-002532`: lines 14596-17258, `Docs/researches/chunks/subset-b-002532_research.md`
- `subset-b-002533`: lines 17259-19693, `Docs/researches/chunks/subset-b-002533_research.md`
- `subset-b-002534`: lines 19694-22207, `Docs/researches/chunks/subset-b-002534_research.md`
- `subset-b-002535`: lines 22208-24656, `Docs/researches/chunks/subset-b-002535_research.md`
- `subset-b-002536`: lines 24657-27046, `Docs/researches/chunks/subset-b-002536_research.md`
- `subset-b-002537`: lines 27047-29638, `Docs/researches/chunks/subset-b-002537_research.md`
- `subset-b-002538`: lines 29639-32347, `Docs/researches/chunks/subset-b-002538_research.md`
- `subset-b-002539`: lines 32348-34934, `Docs/researches/chunks/subset-b-002539_research.md`
- `subset-b-002540`: lines 34935-37498, `Docs/researches/chunks/subset-b-002540_research.md`
- `subset-b-002541`: lines 37499-39973, `Docs/researches/chunks/subset-b-002541_research.md`
- `subset-b-002542`: lines 39974-42401, `Docs/researches/chunks/subset-b-002542_research.md`
- `subset-b-002543`: lines 42402-44690, `Docs/researches/chunks/subset-b-002543_research.md`

## Chunk Research

### subset-b-002526: lines 1-2557

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 1-2557

## Scope

This chunk is the opening segment of the generated AMD GC 11.0.3 shift/mask header. It contains the copyright/license block, include guard `_gc_11_0_3_SH_MASK_HEADER`, and the beginning of the `gc_sdma0_sdma0dec` address block. The range is entirely C preprocessor metadata: `#define` constants named `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

The chunk covers SDMA0 global/control/status fields from `SDMA0_DEC_START` through `SDMA0_FED_STATUS`, then the per-queue SDMA0 RLC register families for queues 0 through 6, and the beginning of queue 7. The assigned range ends at `SDMA0_QUEUE7_RB_AQL_CNTL__AQL_ENABLE__SHIFT`; the remaining queue 7 AQL, minor pointer, preempt, and mid-command definitions continue after this chunk.

## Purpose

`gc_11_0_3_sh_mask.h` is generated hardware metadata for AMDGPU's GC 11.0.3 ASIC register map. This header does not implement SDMA behavior; it gives driver code stable field positions and bit masks for programming or decoding SDMA0 registers through the matching GC 11.0.3 offset header.

Within this chunk, the purpose is SDMA0 register field interpretation:

- global SDMA0 control bits for traps, interrupts, preemption, protected/TMZ mid-command handling, page-fault notifications, data/fence swapping, and restore behavior;
- SDMA0 status and health fields for idle/full/stall conditions, command state, clock gating, FED state, ECC/EDC counters, XNACK fault metadata, GPU IOV violations, AQL status, and queue reset state;
- UTCL1 page translation/cache-control fields for response mode, redo delay, writeback mode, page options, fault address/vector/status capture, invalidation, and XNACK read/write reporting;
- memory layout and address-translation support fields such as GB address config, tiling config, hash selection, physical address capture, hole address capture, and TLBI/GCR credit controls;
- repeated queue register layouts for SDMA0 queues 0-7, including ring buffer control, ring/IB base addresses and pointers, doorbell programming, context status, schedule quantum, preemption, write-pointer polling, AQL settings, and mid-command save/restore data.

## Important APIs, Types, And Macros

There are no functions, structs, enums, typedefs, storage objects, or inline helpers in this chunk. The exported interface is the generated macro namespace.

The core macro convention is:

- `<REG>__<FIELD>__SHIFT`: the least-significant bit position of a hardware field.
- `<REG>__<FIELD>_MASK`: the field mask in the 32-bit register value.
- Matching register address macros are expected from `gc_11_0_3_offset.h`, commonly named `reg<REG>`.
- Consumers combine these macros with AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask tests, `RREG32`, `WREG32`, and `SOC15_REG_OFFSET`.

Notable SDMA0 global groups in this chunk:

- `SDMA0_CNTL`: trap enable, semaphore-wait interrupt, data/fence swap, mid-command and TMZ mid-command preemption, page retry/null/fault interrupts, CP MES interrupt, world-switch, restore, context-empty, frozen, IB-preempt, and RB-preempt interrupt bits.
- `SDMA0_CHICKEN_BITS` and `SDMA0_CHICKEN_BITS_2`: tuning and workaround fields for stalls, burst sizes, 256-byte combine behavior, raw checks, copy overlap, F32 command delay, ucode buffer behavior, watermarks, clock-gating overrides, and PIO VFID source.
- `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, `SDMA0_STATUS3_REG`, `SDMA0_STATUS4_REG`, `SDMA0_STATUS5_REG`, `SDMA0_STATUS6_REG`, and `SDMA0_FED_STATUS`: status decode fields for idle/full/empty/stall state, command operation state, exception/TLBI/GCR/invalidation idleness, outstanding requests, polling activity, fatal error detection, and per-queue busy/selected state.
- `SDMA0_UTCL1_CNTL`, `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_TIMEOUT`, `SDMA0_UTCL1_PAGE`, `SDMA0_UTCL1_RD_STATUS`, `SDMA0_UTCL1_WR_STATUS`, `SDMA0_UTCL1_INV0`, `SDMA0_UTCL1_INV1`, `SDMA0_UTCL1_INV2`, and `SDMA0_UTCL1_*_XNACK*`: translation-cache, fault, invalidation, queueing, and XNACK field definitions used around SDMA memory translation and retry handling.
- `SDMA0_RELAX_ORDERING_LUT`: relaxed-ordering policy bits for copy, write, fence, poll-memory, conditional execute, atomic, const-fill, PTE/PDE, timestamp, world-switch, read-pointer writeback, write-pointer polling, IB fetch, and RB fetch operations.
- `SDMA0_QUEUE_STATUS0` and `SDMA0_QUEUE_RESET_REQ`: packed four-bit queue status/reset request fields for queues 0-7.
- `SDMA0_GPU_IOV_VIOLATION_LOG` and `SDMA0_GPU_IOV_VIOLATION_LOG2`: violation status, multiple-violation, address, write-operation, VF/VFID, and initiator-id decode fields for virtualization/I/O violation reporting.
- `SDMA0_RLC_CGCG_CTRL`, `SDMA0_CLOCK_GATING_STATUS`, and `SDMA0_POWER_CNTL`: clock/power gating controls and status fields.

Notable per-queue families in this chunk:

- `SDMA0_QUEUE<N>_RB_CNTL` for queues 0-7: ring buffer enable, size, write-pointer polling, swap controls, F32 write-pointer polling, read-pointer writeback, writeback timer, privilege, and VMID fields.
- `SDMA0_QUEUE<N>_RB_BASE`, `_RB_BASE_HI`, `_RB_RPTR`, `_RB_RPTR_HI`, `_RB_WPTR`, `_RB_WPTR_HI`, `_RB_RPTR_ADDR_HI`, `_RB_RPTR_ADDR_LO`: queue ring base, read/write pointer, and read-pointer writeback address fields.
- `SDMA0_QUEUE<N>_IB_CNTL`, `_IB_RPTR`, `_IB_OFFSET`, `_IB_BASE_LO`, `_IB_BASE_HI`, `_IB_SIZE`, `_IB_SUB_REMAIN`: indirect-buffer enable, swap, VMID, privilege, base, size, pointer, and remaining-size fields.
- `SDMA0_QUEUE<N>_CONTEXT_STATUS`: selected, idle, expired, exception, context-switchable, preempt-disable, read-pointer writeback idle, write-pointer update pending, and update-failure-count fields.
- `SDMA0_QUEUE<N>_DOORBELL`, `_DOORBELL_LOG`, `_DOORBELL_OFFSET`: doorbell enable/capture, logged data/error, and aligned doorbell offset fields.
- `SDMA0_QUEUE<N>_CSA_ADDR_LO`, `_CSA_ADDR_HI`, and `_SCHEDULE_CNTL`: context-save-area address fields and global/process/local/context-quantum scheduling fields.
- `SDMA0_QUEUE<N>_PREEMPT`, `_RB_PREEMPT`, `_MINOR_PTR_UPDATE`: IB/RB preemption and minor pointer update controls.
- `SDMA0_QUEUE<N>_RB_AQL_CNTL`: AQL enable, packet size, packet step, mid-command preemption, data restore, and overlap bits. This chunk includes the complete queue 0-6 AQL masks but only the first queue 7 AQL shift line.
- `SDMA0_QUEUE<N>_MIDCMD_DATA0` through `_MIDCMD_DATA10` and `_MIDCMD_CNTL`: mid-command state payload and control fields for data validity, copy mode, split state, and preempt allowance.

Queue 0 has a `USE_IB` field in `SDMA0_QUEUE0_CONTEXT_STATUS`; queues 1-7 in this chunk have the otherwise similar context-status layout without that field. Consumers should use generated field names rather than assuming all queue context words are bit-identical.

## Control Flow

This header has no runtime control flow. Inclusion only makes preprocessor constants available to C translation units.

The implied consumer flow is:

1. Include `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h` for the active GC 11.0.3 hardware path.
2. Compute a register address using a `regSDMA0_*` offset macro plus SOC15 base selection or a per-engine/per-queue offset.
3. Read, write, or read-modify-write the register with AMDGPU register access helpers.
4. Use the shift/mask macros either through `REG_SET_FIELD`/`REG_GET_FIELD` or through direct bit masking.

The KFD SDMA queue load/unload path illustrates how queue fields in this chunk drive real sequencing. `amdgpu_amdkfd_gfx_v11.c` computes an SDMA RLC queue offset, clears `SDMA0_QUEUE0_RB_CNTL__RB_ENABLE_MASK`, polls `SDMA0_QUEUE0_CONTEXT_STATUS__IDLE_MASK`, programs doorbell offset/enable, writes RB read/write pointers and base addresses, toggles `SDMA0_QUEUE0_MINOR_PTR_UPDATE`, and then sets `RB_ENABLE`. The dump path iterates contiguous queue register ranges from `regSDMA0_QUEUE0_RB_CNTL` through mid-command control.

The MQD update path in `kfd_mqd_manager_v11.c` composes `sdmax_rlcx_rb_cntl` with `SDMA0_QUEUE0_RB_CNTL__RB_SIZE__SHIFT`, `RB_VMID__SHIFT`, `RPTR_WRITEBACK_ENABLE__SHIFT`, `RPTR_WRITEBACK_TIMER__SHIFT`, and `F32_WPTR_POLL_ENABLE__SHIFT`; it also encodes doorbell offset and schedule quantum with the corresponding queue 0 macros. Hardware queue instances use queue 0 field names with an offset computed from the selected SDMA engine and queue.

## State And Persistence

The header itself stores no software state and has no persistence behavior. It allocates no memory, performs no I/O, and cannot change hardware.

The state described by the macros is hardware-resident SDMA0 state:

- global control registers persist across ordinary CPU execution until changed by driver, firmware, reset, suspend/resume, or runtime power-management flows;
- queue RB/IB base, pointer, doorbell, schedule, AQL, and context-status registers are the live hardware queue state used by AMDGPU and KFD to submit and manage SDMA work;
- UTCL1/XNACK/fault registers expose transient memory-translation and retry state;
- status, EDC/ECC, GPU IOV, FED, clock-gating, and watchdog fields are diagnostic or policy state used during initialization, error handling, and hang/debug paths.

Because these definitions describe a hardware ABI, persistence concerns are mostly about keeping generated masks synchronized with the actual ASIC register layout and with saved MQD fields. A wrong shift or mask can cause software to persist a malformed queue control word, restore a queue with a bad VMID or address bit alignment, miss a fault/status bit, or poll the wrong idle field.

## Dependencies And Integration Points

This chunk belongs to the generated GC 11.0.3 register-description set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies the matching `regSDMA0_*` register offsets used with these masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_default.h` supplies matching reset/default values for the same ASIC register namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c` includes this header with the GC 11.0.3 offset header and uses generated RLC/FED fields for GC/SDMA fatal-error interrupt handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c` includes this header and uses GC 11.0.3 register names/masks in IMU/RLC RAM golden programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c` uses the SDMA queue register offsets and masks from this register family to load, dump, stop, and inspect KFD SDMA queues.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c` uses queue 0 shift/mask definitions to build the SDMA MQD words later programmed into the selected engine/queue instance.
- SDMA version code such as `sdma_v6_0.c` and adjacent GC 11 files use the same macro style for UTCL1 status, control programming, interrupt/trap setup, and diagnostics, even when the exact include path is selected by ASIC generation.

The integration contract is compile-time but hardware-critical: the offset header chooses the register word, this mask header chooses the field location inside that word, and runtime code assumes both come from the same generated hardware database and ASIC revision.

## Risks And Edge Cases

- Generated-header drift is the main risk. If `gc_11_0_3_sh_mask.h`, `gc_11_0_3_offset.h`, and any default/header consumers are regenerated from different hardware descriptions, code can compile while programming the wrong bits.
- Queue register blocks are repetitive but not perfectly safe to infer manually. Queue 0 has a `USE_IB` context-status bit that the later queues in this chunk do not expose. The chunk boundary also splits queue 7's AQL field list after the first shift definition.
- Address fields have alignment-implied low bits: several low address fields start at bit 2, IB base low starts at bit 5, and doorbell offsets start at bit 2. A consumer that shifts unaligned CPU/GPU addresses incorrectly can silently drop low bits or write invalid queue state.
- Full-width `0xFFFFFFFFL` masks are common for pointer, data, and timestamp registers. Callers must handle 64-bit values by programming paired low/high registers in the documented order; the macros only define the 32-bit pieces.
- Several fields are packed multi-bit status or policy fields rather than booleans, including burst/watermark fields, exception fields, queue status nibbles, command operation status, VMID fields, schedule quantum, and GPUVM invalidation fields. Treating every mask as a single flag would corrupt decode or programming logic.
- Fault and retry fields such as XNACK fault address/vector/status, page retry/null/fault interrupt enables, and UTCL1 invalidation fields affect error handling. Incorrect masks can hide page-fault causes or trigger wrong recovery paths.
- Virtualization and RAS integration depends on exact decode of GPU IOV and FED status fields. A wrong field name or bit position can send poison/error handling to the wrong block or miss an SR-IOV violation.
- The header has no local validation and no semantic comments beyond register names. Many names encode hardware behavior that must be interpreted together with the hardware specification and the matching driver code.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are build, generation, and hardware-integration checks:

- Build AMDGPU with GC 11.0.3 paths enabled so include sites in `gfx_v11_0_3.c`, `imu_v11_0_3.c`, KFD, and SDMA queue code resolve all generated field names.
- Compile-time failures from `REG_SET_FIELD`, `REG_GET_FIELD`, or direct mask uses are the first signal of renamed or missing generated macros.
- Header-regeneration checks should compare this file against the authoritative ASIC register database and verify that offsets, masks, defaults, and queue register ordering stay synchronized.
- KFD SDMA queue tests should create, load, preempt/stop, dump, and destroy SDMA queues, exercising `RB_CNTL`, doorbell, pointer, context-status, schedule, and mid-command fields.
- Suspend/resume and GPU reset tests should verify that SDMA queues and global SDMA control state can be restored without stale pointer, VMID, doorbell, or preemption state.
- SDMA memory fault and retry scenarios should validate UTCL1/XNACK status capture, page-fault interrupt enables, and recovery logs.
- RAS/FED interrupt testing on GC 11.0.3 hardware should validate `RLC_RLCS_FED_STATUS` decode paths that classify SDMA versus GFX fatal-error events.
- SR-IOV or VF test coverage should verify GPU IOV violation logging fields and poison/error handling behavior when virtualization is active.

### subset-b-002527: lines 2558-5102

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 2558-5102

## Scope

This chunk is a generated AMDGPU GC 11.0.3 register field-mask header segment. It contains preprocessor constants only: each hardware field is represented by a `__SHIFT` value and an unshifted `_MASK` value for 32-bit MMIO register composition and decoding. It does not define functions, structs, storage, or executable logic.

The range starts inside the `SDMA0_QUEUE7_RB_AQL_CNTL` definitions, completes the tail of `SDMA0_QUEUE7`, then switches to the `gc_sdma0_sdma1dec` address block and covers nearly all public SDMA1 engine and queue field definitions. It includes SDMA1 engine control/status, VM/UTCL1, RAS/EDC, clock/power/debug, queue reset, and queue templates for `SDMA1_QUEUE0` through the first half of `SDMA1_QUEUE7`. The chunk ends at `SDMA1_QUEUE7_CONTEXT_STATUS__RPTR_WB_IDLE_MASK`; the remaining `SDMA1_QUEUE7` doorbell, schedule, AQL, and mid-command fields are in the next chunk.

## Purpose

The purpose of this header slice is to give GC 11.0.3 AMDGPU code exact bit positions for SDMA ring, queue, interrupt, preemption, AQL, page-translation, error-reporting, and diagnostic registers. The matching register addresses live in `gc_11_0_3_offset.h`; this file supplies the field layout consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and `SOC15_REG_OFFSET`.

Although these are plain C macros, they are part of the low-level hardware ABI between the driver and the GC 11.0.3 SDMA blocks. A correct offset with a wrong mask can still compile but program the wrong hardware bit. This is especially important for SDMA queue bring-up, KFD queue restore, doorbell routing, GPU reset, VM fault handling, and RAS diagnostics.

## Register Families Covered

The opening lines complete the SDMA0 queue-7 AQL/preemption tail: `SDMA0_QUEUE7_RB_AQL_CNTL`, `SDMA0_QUEUE7_MINOR_PTR_UPDATE`, `SDMA0_QUEUE7_RB_PREEMPT`, `SDMA0_QUEUE7_MIDCMD_DATA0..10`, and `SDMA0_QUEUE7_MIDCMD_CNTL`. These fields describe AQL enablement and packet sizing, minor pointer update toggling, ring-buffer preemption request, and mid-command save/restore data validity.

The SDMA1 engine control group begins at `SDMA1_DEC_START` and includes `SDMA1_F32_MISC_CNTL`, `SDMA1_POWER_CNTL`, `SDMA1_CNTL`, `SDMA1_CNTL1`, `SDMA1_CHICKEN_BITS`, and `SDMA1_CHICKEN_BITS_2`. These masks cover trap and interrupt enables, byte-swap controls, mid-command preemption/world-switch support, page retry/null/fault interrupt enables, clock-gating overrides, burst/combine controls, copy overlap, raw hazard checks, freeze behavior, and F32 microcontroller wake or misc control.

The address, topology, and scheduling group includes `SDMA1_GB_ADDR_CONFIG`, `SDMA1_GB_ADDR_CONFIG_READ`, `SDMA1_RB_RPTR_FETCH`, `SDMA1_RB_RPTR_FETCH_HI`, `SDMA1_IB_OFFSET_FETCH`, `SDMA1_PROGRAM`, `SDMA1_PHYSICAL_ADDR_LO/HI`, `SDMA1_GLOBAL_QUANTUM`, `SDMA1_PROCESS_QUANTUM0/1`, `SDMA1_WATCHDOG_CNTL`, `SDMA1_QUEUE_STATUS0`, `SDMA1_QUEUE_RESET_REQ`, `SDMA1_CE_CTRL`, and `SDMA1_CRD_CNTL`. These fields expose memory addressing, queue reset request bits, engine scheduling quantum, watchdog settings, copy-engine control, and command/read-data flow-control state.

The status and diagnostics group includes `SDMA1_STATUS_REG`, `SDMA1_STATUS1_REG`, `SDMA1_STATUS2_REG`, `SDMA1_STATUS3_REG`, `SDMA1_STATUS4_REG`, `SDMA1_STATUS5_REG`, `SDMA1_STATUS6_REG`, `SDMA1_FREEZE`, `SDMA1_INT_STATUS`, `SDMA1_CLOCK_GATING_STATUS`, `SDMA1_FED_STATUS`, `SDMA1_AQL_STATUS`, `SDMA1_ERROR_LOG`, `SDMA1_GPU_IOV_VIOLATION_LOG`, and `SDMA1_GPU_IOV_VIOLATION_LOG2`. These masks decode idle and busy state, FIFO fullness, frozen/preempted status, context-empty state, invalidation and UTCL1 pipeline status, interrupt latches, virtualization violations, command/fetch/decode status, and error type/address surfaces.

The RAS, firmware, scratch, and debug group includes `SDMA1_UCODE_CHECKSUM`, `SDMA1_UCODE1_CHECKSUM`, `SDMA1_EDC_CONFIG`, `SDMA1_EDC_COUNTER`, `SDMA1_EDC_COUNTER_CLEAR`, `SDMA1_EA_DBIT_ADDR_DATA`, `SDMA1_EA_DBIT_ADDR_INDEX`, `SDMA1_SCRATCH_RAM_DATA`, `SDMA1_SCRATCH_RAM_ADDR`, `SDMA1_PUB_DUMMY_REG0..3`, `SDMA1_F32_COUNTER`, `SDMA1_BA_THRESHOLD`, `SDMA1_ID`, `SDMA1_VERSION`, `SDMA1_HASH`, `SDMA1_HBM_PAGE_CONFIG`, `SDMA1_HOLE_ADDR_LO/HI`, and `SDMA1_TILING_CONFIG`. These registers support firmware visibility, EDC counter configuration/clearing, double-bit error address indexing, scratch RAM access, build/version identification, and hardware debug state.

The VM and UTCL1 group includes `SDMA1_ATOMIC_CNTL`, `SDMA1_ATOMIC_PREOP_LO/HI`, `SDMA1_UTCL1_CNTL`, `SDMA1_UTCL1_WATERMK`, `SDMA1_UTCL1_TIMEOUT`, `SDMA1_UTCL1_PAGE`, `SDMA1_UTCL1_RD_STATUS`, `SDMA1_UTCL1_WR_STATUS`, `SDMA1_UTCL1_INV0..2`, `SDMA1_UTCL1_RD_XNACK0..1`, `SDMA1_UTCL1_WR_XNACK0..1`, `SDMA1_RELAX_ORDERING_LUT`, and `SDMA1_TLBI_GCR_CNTL`. These fields control retry/redo behavior, watermarks, page mode and cache policy, invalidation requests, XNACK/fault attributes, relaxed ordering, and GCR/TLB invalidation.

The repeated queue template covers complete `SDMA1_QUEUE0` through `SDMA1_QUEUE6` definitions and the beginning of `SDMA1_QUEUE7`. For queues 0 through 6, each template defines ring-buffer control and pointers (`RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_LO/HI`, `RB_WPTR_POLL_ADDR_LO/HI`), indirect-buffer state (`IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, `IB_SUB_REMAIN`), context and scheduling state (`CONTEXT_STATUS`, `SCHEDULE_CNTL`, `SKIP_CNTL`), doorbell state (`DOORBELL`, `DOORBELL_LOG`, `DOORBELL_OFFSET`), context-save address fields (`CSA_ADDR_LO/HI`), preemption (`PREEMPT`, `RB_PREEMPT`), AQL controls (`RB_AQL_CNTL`), minor pointer updates, dummy registers, and `MIDCMD_DATA0..10` plus `MIDCMD_CNTL`. Queue 7 has the same layout in this chunk through `CONTEXT_STATUS`; its tail follows after line 5102.

## Important APIs, Types, and Macros

This file exposes a generated macro API:

- `<REGISTER>__<FIELD>__SHIFT` gives a field shift inside the register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask before shifting extracted values.
- Register comments such as `//SDMA1_QUEUE0_RB_CNTL` and address-block comments such as `// addressBlock: gc_sdma0_sdma1dec` preserve the generated hardware grouping.

Important runtime consumers include GC 11.0.3-specific files that include `gc/gc_11_0_3_offset.h` and `gc/gc_11_0_3_sh_mask.h`, including `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`. Broader SDMA and KFD paths use the same generated naming pattern for SDMA queue offsets and masks. In `amdgpu_amdkfd_gfx_v11.c`, `get_sdma_rlc_reg_offset()` computes the SDMA1 queue register base from `regSDMA1_QUEUE0_RB_CNTL`, then advances by the queue stride. In `mes_v11_0.c`, SDMA queue reset chooses `regSDMA1_QUEUE_RESET_REQ` for SDMA engine 1 and waits for the requested queue-reset bit to clear.

The macros are normally used through compile-time token concatenation in register helpers. For example, `REG_SET_FIELD(value, SDMA1_QUEUE0_RB_CNTL, RB_ENABLE, 1)` depends on `SDMA1_QUEUE0_RB_CNTL__RB_ENABLE_MASK` and `SDMA1_QUEUE0_RB_CNTL__RB_ENABLE__SHIFT`. Direct masks are also useful for status polling and field clearing when a helper is not used.

## Control Flow

There is no executable control flow in this header. The relevant control flow occurs when consumers program or poll the registers described here.

During queue setup or restore, driver code writes queue ring base addresses, read/write pointers, write-pointer polling addresses, read-pointer writeback addresses, doorbell offset/enable fields, ring size, VMID, privilege, swap, AQL mode, IB enablement, context-save addresses, and scheduling quantum. Queue enablement generally depends on `RB_CNTL__RB_ENABLE`, while readiness and safe teardown depend on `CONTEXT_STATUS` idle and exception fields.

During KFD SDMA queue loading, engine and queue IDs map to an RLC queue register block. The driver disables the queue, waits for idle, writes the saved MQD-backed queue state into the SDMA queue registers, toggles minor pointer updates where needed, restores doorbell and pointer state, and re-enables the ring.

During reset and MES-managed queue recovery, SDMA queue reset writes a bit to `SDMA1_QUEUE_RESET_REQ` for the selected SDMA1 queue and polls until hardware clears it. Engine-wide recovery and diagnostics use `FREEZE`, `STATUS*`, `FED_STATUS`, `INT_STATUS`, `QUEUE_STATUS0`, F32 controls, and queue preemption bits to determine whether SDMA is idle, preempted, reset-complete, or wedged.

During VM fault handling and GFXHUB diagnostics, SDMA1 appears as a GCVM client. `gfxhub_v3_0_3.c` includes the same GC 11.0.3 mask header and names SDMA1 in the GFXHUB client ID table, while the UTCL1/XNACK/status fields in this chunk expose SDMA-side retry, invalidation, and fault state.

## State and Persistence

The macros themselves are immutable compile-time constants and persist only in object code through the bit operations that use them. The hardware registers they describe are volatile MMIO state.

Persistent queue state includes ring base, ring size, VMID, privilege, read/write pointer state, read-pointer writeback location, write-pointer polling location, doorbell offset, AQL settings, context-save address, and scheduling quantum. KFD and MES flows may save or reconstruct this state in MQDs or queue-management packets so queues can survive preemption, eviction, and restore.

Transient state includes idle/full/stall status, doorbell captured/log state, interrupt latches, reset request bits, queue exception bits, EDC counters, XNACK attributes, UTCL1 invalidation busy state, mid-command data validity, F32 counters, and FED/error logs. These values change as DMA packets execute, as faults occur, or as reset/suspend/resume paths manipulate the engine.

## Dependencies and Integration Points

This chunk depends on the GC 11.0.3 generated register set:

- `gc_11_0_3_offset.h` supplies the `regSDMA1_*` and related register addresses that must match these field layouts.
- SOC15 register helpers map the generated offsets into MMIO accesses for the correct IP block and instance.
- Queue-management code in AMDGPU, MES, and KFD depends on the queue template being consistent across SDMA0 and SDMA1 so engine selection can be handled by base-offset arithmetic.
- Doorbell programming depends on `SDMA1_QUEUE*_DOORBELL` and `SDMA1_QUEUE*_DOORBELL_OFFSET` fields matching NBIO doorbell aperture setup.
- VM/cache behavior depends on UTCL1, XNACK, TLBI/GCR, page, timeout, and relaxed-ordering fields matching the hardware.
- RAS and diagnostic paths depend on `FED_STATUS`, `EDC_*`, `ERROR_LOG`, `GPU_IOV_VIOLATION_LOG*`, `STATUS*`, and XNACK fields for meaningful fault attribution.

GC 11.0.3-specific integration is visible in `gfx_v11_0_3.c`, which dispatches RLC FED interrupts to the SDMA RAS block when `SDMA0_FED_ERR` or `SDMA1_FED_ERR` is set in RLC status, and in `imu_v11_0_3.c`, which carries SDMA microcode self-load golden values for both SDMA engines. This chunk supplies the SDMA1-side field vocabulary used by the same generated header family.

## Risks

The main risk is silent hardware misprogramming. A wrong field constant usually does not fail compilation; it writes or decodes the wrong bit at runtime.

High-risk queue fields include `RB_ENABLE`, `RB_SIZE`, `RB_VMID`, `RB_PRIV`, pointer writeback, write-pointer polling, `IB_ENABLE`, doorbell enable/offset, queue reset, and preemption bits. Mistakes can cause queues not to start, missed submissions, writes to the wrong doorbell, corrupted pointers, or hangs while waiting for idle.

Address fields are alignment-sensitive. Low address masks such as `RB_WPTR_POLL_ADDR_LO`, `RB_RPTR_ADDR_LO`, `CSA_ADDR_LO`, `IB_BASE_LO`, and physical or XNACK address fields intentionally omit low bits. Incorrect shifts or masks can corrupt GPU addresses while still producing plausible-looking values.

UTCL1 and XNACK fields are high risk for memory correctness. Bad redo, cache-policy, invalidation, timeout, page, or retry field definitions can lead to stale DMA data, VM fault storms, invalidation hangs, or misleading page-fault attribution.

RAS and reset fields are high risk for recovery. Wrong EDC clear bits, queue reset bits, F32 controls, FED status fields, or context/preemption status masks can hide real faults or make the driver reset the wrong queue/engine.

Because this is generated register-description source, manual edits should be treated as hardware-interface changes. Reserved fields, repeated queue templates, and apparently diagnostic-only masks may be consumed by firmware, register dump tooling, KFD, MES, virtualization, or future workarounds.

## Test Signals

Compile-time signals include successful AMDGPU builds wherever GC 11.0.3 files include this header and wherever `REG_SET_FIELD`, `REG_GET_FIELD`, direct `_MASK`, or direct `__SHIFT` constants name SDMA1 registers.

Runtime SDMA signals include successful probe and resume on GC 11.0.3 ASICs, passing SDMA ring tests on both engines, correct ring read/write pointer movement, working doorbell submissions, successful IB execution, and no queue hangs under copy/fill workloads.

KFD and MES signals include successful SDMA queue creation, load, preemption, reset, restore, and teardown for SDMA1 queues 0 through 7; correct waiting on queue idle/reset completion; and no stale doorbell or MQD state after eviction or GPU reset.

VM and memory-management signals include stable DMA through GART/VRAM mappings, no unexpected UTCL1 invalidation busy timeouts, no retry storms, correct XNACK/page-fault attribution, and clean behavior after suspend/resume.

RAS and diagnostics signals include meaningful dumps for `SDMA1_STATUS*`, `SDMA1_QUEUE*_CONTEXT_STATUS`, `SDMA1_EDC_COUNTER`, `SDMA1_ERROR_LOG`, `SDMA1_FED_STATUS`, `SDMA1_GPU_IOV_VIOLATION_LOG*`, `SDMA1_UTCL1_*_STATUS`, and XNACK registers, plus correct routing of SDMA FED errors to the SDMA RAS handler.

### subset-b-002528: lines 5103-7503

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 5103-7503

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the tail of `SDMA1_QUEUE7_CONTEXT_STATUS` masks and then cover the remaining `SDMA1_QUEUE7_*` doorbell, context-save, scheduling, AQL, preemption, and mid-command fields. The main body covers SDMA0 and SDMA1 hypervisor decode register maps, SDMA performance counter selectors/results, GRBM global graphics status/reset/error/debug registers, CP command-processor debug/status/FIFO/register-queue counters, and the first PA/VGT/IA status fields. The chunk ends after the `IA_UTCL1_STATUS_2__RETRY_DETECTED__SHIFT` macro; its corresponding masks and subsequent PA decode registers continue in the next adjacent chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 11.0.3 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_11_0_3_sh_mask.h` supplies the bit layouts for GC 11.0.3 registers. Driver code pairs these macros with register addresses from the matching `gc_11_0_3_offset.h` header and, where available, generated reset values/defaults. Consumers normally use the constants through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` so they can program or inspect one hardware field without embedding magic bit positions.

This chunk focuses on low-level engine control and observability rather than draw-state programming:

- SDMA queue 7 state for doorbells, doorbell logging, context-save area addresses, schedule IDs and quantum, indirect-buffer preemption, write-pointer polling, AQL packet layout, minor pointer updates, ring-buffer preemption, and mid-command data restore/control.
- SDMA0 and SDMA1 hypervisor-visible register-type bitmaps that classify queue context registers, public SDMA registers, microcode/self-load controls, VM context control, virtual reset requests, F32 thread control, power/clock/debug/status registers, UTCL1/XNACK/invalidation state, GPU IOV violation logs, and queue reset/status hooks.
- SDMA0 and SDMA1 performance counter control/data windows, including performance event selection, modes, enable/clear bits, start/stop trigger fields, result selection, command operation fields, and low/high counter result registers.
- GRBM registers for global busy/clean status by graphics block, soft reset bits, clock-gating delay/idle wait controls, read/write error attribution, interrupt enablement, traps, RSMU access configuration, interrupt-handler credits, UTCL2 invalidation ranges, invalid pipe logging, fence ranges, scratch registers, and asynchronous VF violation data.
- CP registers for CPC/CPF/CP debug indices, busy/stalled/status views, GRBM free-count counters, header dumps, scratch indexed access, ring/read/write pointer state, command queue thresholds and availability, ROQ/STQ/MEQ pointer stats, command index/data access, interrupt debug status, and privilege violation address capture.
- The start of PA/VGT decode status for DMA data/request FIFO depths, draw-init FIFO depth, memory-controller timestamp resolution, and IA UTCL1 busy/fault/retry state.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header, commonly with `mm...` names matching the register base.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, read-modify-write MMIO helpers, debugfs/sysfs/perf counter plumbing, reset/suspend/resume code, or command-stream setup paths.

The main macro families in this slice are:

- `SDMA1_QUEUE7_*`: the last per-queue SDMA1 queue-7 context fields. Address fields such as `CSA_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, and high-word partners describe split GPU/system addresses. Control/status fields include doorbell `ENABLE`/`CAPTURED`, doorbell-log backend error and data bits, schedule identity and quantum, `IB_PREEMPT`, AQL enable/packet/step/preempt/overlap bits, `MINOR_PTR_UPDATE`, `RB_PREEMPT`, and the `MIDCMD_DATA0..10` plus `MIDCMD_CNTL` restore state.
- `SDMA0_*` and `SDMA1_*` hypervisor decode fields: `UCODE_ADDR/DATA`, broadcast ucode windows, `UCODE_SELFLOAD_CONTROL`, VM context address/control, `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `CONTEXT_REG_TYPE0..2`, `PUB_REG_TYPE0..3`, `VM_CNTL`, and `F32_CNTL`. The `CONTEXT_REG_TYPE*` and `PUB_REG_TYPE*` registers are bitmaps naming which SDMA queue/public registers belong to each context or public register type.
- `SDMA[01]_PERFCNT_*` and `SDMA[01]_PERFCOUNTER*`: perf selection/configuration/result macros for two SDMA performance counters and an additional perfcnt result path. These include `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, `CLEAR`, trigger selection, `ENABLE_ANY`, `CLEAR_ALL`, and result counter low/high fields.
- `GRBM_*`: global graphics register-bus manager fields. `GRBM_STATUS*` expose busy/clean state for CP, CPF, CPC, GUI_ACTIVE, RLC, TCP, GL1/GL2, PA, TA, SX, SPI, SC, DB, CB, UTCL, SEDC, PC, PMM, and related blocks. `GRBM_SOFT_RESET` exposes reset bits for CP/RLC/UTCL2/GFX/CPF/CPC/CPG/CAC/CPAXI/EA/SDMA0/SDMA1. Error and violation registers record requester, VF/VFID/VMID, pipe/ME/queue/source IDs, address fragments, TMZ/security-write status, and sticky error bits.
- `CP_*`: command-processor observability and tuning fields. CPC/CPF status and busy/stall registers expose sub-block activity, ROQ/DC/RCIU/TCIU/cache/save-restore/MES/MEC activity, and GRBM free counts. CP global status covers stalled/busy/stat registers, ME/PFP/MEC instruction pointers, context counts, ring-buffer read pointers, write-pointer polling/delay, queue thresholds, availability counters, ROQ/STQ/MEQ stats, debug command index/data access, interrupt assertion bits, and privilege violation capture.
- `VGT_DMA_DATA_FIFO_DEPTH`, `VGT_DMA_REQ_FIFO_DEPTH`, `VGT_DRAW_INIT_FIFO_DEPTH`, `VGT_MC_LAT_CNTL`, and partial `IA_UTCL1_STATUS_2`: the opening PA decode entries for FIFO sizing, timestamp resolution, and input-assembler UTCL1 busy/fault/retry state.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.0.3 register header for the active ASIC generation.
2. Choose the matching register address from `gc_11_0_3_offset.h`.
3. Read an existing register value, prepare a debug/perf access, or construct an MMIO/command-packet write.
4. Use the `__SHIFT`/`__MASK` pairs, usually through register field helpers, to pack a field value or extract status bits.
5. Feed the resulting value into engine bring-up, SDMA queue setup, perf counter programming, GPU reset, power-management, virtualization, debug, or fault-handling logic.

For SDMA queue state, higher-level code programs ring/doorbell/AQL/context-save/preemption fields when creating queues, restoring contexts, handling virtualization, or recovering from a fault. For GRBM and CP status, runtime flows mostly poll or snapshot bits during idle waits, hangs, debug dumps, reset decisions, interrupt handling, and performance diagnostics. For perf counters, consumers select an event/mode, clear and enable counters, optionally gate them with start/stop triggers, then read low/high result registers. This header does not define required ordering, delays, clear-on-read behavior, or reset sequences; those are encoded in AMDGPU engine code and the hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

SDMA queue fields are persistent queue/context state. Doorbell enable/captured state, queue scheduling IDs, context-save area addresses, write-pointer polling addresses, AQL packet controls, ring preemption state, and mid-command restore data can survive as live engine state until overwritten, context-switched, reset, or lost through power gating. Incorrect restore of these fields can resume the wrong command stream, poll the wrong write pointer, corrupt mid-command replay, or send work to the wrong queue identity.

The SDMA `CONTEXT_REG_TYPE*` and `PUB_REG_TYPE*` bitmaps are register-classification maps for hypervisor/context save and public register exposure. Their values affect which queue/public registers participate in context save/restore, virtualization handling, or decode visibility. `VIRT_RESET_REQ`, `ACTIVE_FCN_ID`, GPU IOV violation logs, VM context fields, and VF/VFID/VMID fields are especially sensitive in SR-IOV or virtualized environments because stale or misdecoded state can attribute faults or resets to the wrong function.

GRBM and CP status/error fields are primarily live hardware status or sticky diagnostic state. Busy/clean bits change as engines drain; error, invalid pipe, read/write violation, interrupt debug, and privilege violation fields may remain latched until cleared by the documented sequence. GRBM scratch registers are general full-width scratch state and may be used by firmware, driver diagnostics, or low-level bring-up code. Soft-reset and power-halt fields have direct hardware side effects and should not be treated as passive configuration.

Performance counter fields persist configured event selections, modes, and enable/clear state while counters accumulate. Counter low/high result registers must be read with the correct latching/ordering expectations from the hardware spec; this header only describes bit positions and cannot express atomicity, saturation, or clear semantics.

Reserved fields appear throughout the generated map. Callers should preserve reserved bits during read-modify-write unless a documented full-register write is required. This is particularly important for reset, virtualization, clock/power, and debug registers where undocumented bits can be ASIC- or firmware-sensitive.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_default.h`, when present in the same generated register family, provides default/reset values for many registers.
- AMDGPU SDMA, GFX, CP, reset, power-management, virtualization/SR-IOV, KFD/compute queueing, perf counter, debugfs, and hang-dump paths rely on these bit assignments.
- Common AMDGPU register helpers provide the actual field packing/extraction and MMIO or command-packet access mechanisms.

Integration points include SDMA queue creation and teardown, context save/restore, SDMA AQL and preemption support, ring write-pointer polling, SDMA firmware/microcode load and self-load control, virtual function reset and fault attribution, SDMA and graphics idle waits, GPU reset/hang recovery, GRBM read/write error logging, CP command queue and FIFO diagnostics, CP interrupt debug handling, privilege violation reporting, per-engine performance monitoring, and early PA/VGT/IA status reporting.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bits or decode misleading diagnostics.
- This chunk starts and ends mid-family. It begins with only the last visible `SDMA1_QUEUE7_CONTEXT_STATUS` masks and ends before the masks for `IA_UTCL1_STATUS_2`; file-level conclusions must be merged with adjacent chunks.
- SDMA0 and SDMA1 macro families are nearly symmetric. Generator or copy/paste mistakes can affect one engine only, producing asymmetric queue failures, perf counter readings, or reset behavior.
- Address fields often omit low alignment bits, such as low address words shifted by two bits. Treating these as raw byte addresses can program plausible but wrong addresses for context-save areas, write-pointer polling, VM context state, or trap/error addresses.
- Reset and halt fields have side effects. Misusing `GRBM_SOFT_RESET`, `GRBM_PWR_CNTL2`, `SDMA*_F32_CNTL`, `SDMA*_VIRT_RESET_REQ`, or queue reset hooks can hang the GPU or lose active work.
- Virtualization and security attribution fields are high risk: VF/VFID/VMID/SSRCID/TMZ/security-write bits must be decoded exactly for fault isolation, SR-IOV reset, and security logging.
- Busy/clean/status bits are volatile. Polling code must account for transitions, hardware blocks that may be clock-gated, and sticky error bits that require explicit clearing.
- Counter high/low result registers can be race-prone if read without the documented latching sequence. The shift/mask header cannot describe atomic snapshot requirements.
- Reserved masks are included in many bitmap registers. Full-register writes that do not preserve reserved bits may change undocumented engine behavior.
- CP threshold and availability fields are tightly coupled to command processor queue sizing. Incorrect field widths can make queue diagnostics or tuning appear valid while hiding near-full or stalled conditions.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_0_3_sh_mask.h`, especially GC 11.0.3 SDMA, GFX, CP, reset, virtualization, KFD, debug, and perf counter paths.
- Mechanical comparison against AMD's authoritative GC 11.0.3 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that all registers in this chunk have matching address macros in `gc_11_0_3_offset.h` and expected defaults in the matching default header where generated.
- Static mask/shift sanity checks: masks should align with shifts, full-width data fields should use `0xFFFFFFFFL`, SDMA0/SDMA1 mirrored families should remain structurally aligned, and bitmap fields should not overlap unless documented.
- SDMA queue tests covering doorbell programming, write-pointer polling, AQL packet execution, preemption, context save/restore, queue reset, and mid-command restore after suspend/resume or GPU reset.
- SR-IOV or virtualization tests that trigger virtual reset requests and validate VF/VFID/VMID/SSRCID fault attribution for SDMA, GRBM, and CP paths.
- Perf counter tests that select SDMA events, clear/enable/disable counters, read low/high results, and compare monotonicity or expected activity under controlled DMA workloads.
- Hang/debug dump tests that verify GRBM busy/clean bits, read/write error registers, invalid-pipe logs, CP busy/stalled/status fields, ring/ROQ/STQ/MEQ pointers, and CP interrupt debug bits are decoded coherently.
- Reset and idle-wait tests that exercise `GRBM_STATUS*`, `GRBM_SOFT_RESET`, clock/idle wait fields, CP/SDMA reset bits, and post-reset register restore.
- Runtime warning signals include SDMA queue hangs, lost doorbell updates, wrong queue preemption, bad AQL dispatch, misleading perf counters, failed idle waits, incorrect fault attribution, unexpected privilege/security violation reports, GPU reset loops, or CP/GRBM debug dumps with impossible busy/clean combinations.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002528`. It covers lines 5103-7503 of `gc_11_0_3_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `SDMA1_QUEUE7_CONTEXT_STATUS` and `IA_UTCL1_STATUS_2` families and to place these SDMA/GRBM/CP/PA status definitions in the full GC 11.0.3 register map.

### subset-b-002529: lines 7504-9879

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 7504-9879

Covered source range: lines 7504-9879 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h`

## Purpose

This chunk is a generated AMDGPU GC 11.0.3 register-field shift/mask header section. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. The constants describe bit positions for graphics-core MMIO registers so AMDGPU code can compose, update, and decode 32-bit register values without embedding raw bit arithmetic at call sites.

The range exports 2,187 `#define` lines for 173 distinct registers. Macro names follow the generated AMD convention:

- `REGISTER__FIELD__SHIFT`: starting bit position of a hardware field.
- `REGISTER__FIELD_MASK`: field mask in its final 32-bit register position.

The chunk starts in the middle of `IA_UTCL1_STATUS_2`: the first lines contain the remaining shift definitions and all mask definitions for that register. The preceding part of `IA_UTCL1_STATUS_2` is in the previous chunk. This matters for merge/reconciliation because the complete register report should not treat the missing early shifts as absent from the source file.

## Register Areas Covered

The opening portion finishes front-end, UTCL1, graphics-engine, VGT, PA, and clipping controls:

- `IA_UTCL1_STATUS_2`, `IA_UTCL1_CNTL`, `IA_UTCL1_STATUS`, `WD_UTCL1_CNTL`, and `WD_UTCL1_STATUS` expose UTCL1 fault, retry, PRT, invalidate, bypass, snoop, VMID-reset, MTYPE, LLC no-allocate, and XNACK redo timer fields.
- `WD_CNTL_STATUS`, `WD_QOS`, `CC_GC_PRIM_CONFIG`, `CC_GC_SA_UNIT_DISABLE`, and `CC_GC_SHADER_ARRAY_CONFIG` cover draw-distributor busy state, draw stall, write-disable guards, inactive primitive assembler masks, disabled shader arrays, and inactive WGP masks.
- `GE_RATE_CNTL_1`, `GE_RATE_CNTL_2`, `GE_PRIV_CONTROL`, `GE_STATUS`, `GE2_SE_CNTL_STATUS`, `GE_SPI_IF_SAFE_REG`, and `GE_PA_IF_SAFE_REG` describe graphics-engine pacing, merged HS/GS and LS/ES modes, reset-on-pipeline-change behavior, primitive-group clamping, fine-grain clock-gating override, thread-trace/perf-counter state, GE/SPI safe data, and GE/PA interface safe data.
- `VGT_SYS_CONFIG`, `VGT_GS_MAX_WAVE_ID`, and `VGT_RESET_DEBUG` describe dual-core mode, LS/HS thread group sizing, subgroup count, GS wave ID reporting, and many debug disables for GS, tessellation, WD, prefetch, mesh shader attribute packing, distribution pipes, and patch optimizations.
- `GFX_PIPE_CONTROL` supplies hysteresis and context suspend control fields.
- `PA_CL_CNTL_STATUS`, `PA_CL_ENHANCE`, `PA_CL_RESET_DEBUG`, `PA_SU_CNTL_STATUS`, and `PA_SC_FIFO_DEPTH_CNTL` cover clipping and setup busy state, clip vertex reorder, NGG/primitive-filter behavior, NaN processing, near-clip programming, rate control, inner-edge flags, fine clock-gating disables, and PA-to-SC FIFO depth.

The `gc_sqdec` address block starts at line 7806 and covers shader queue/cache and local data share controls:

- `SQ_CONFIG`, `SQC_CONFIG`, and `SQC_MISC_CONFIG` include instruction/data cache sizing, miss/hit FIFO depth, cache eviction and force-miss modes, per-VMID invalidation disable, SQC clock-gating disables, GL1 clock enable override, and miscellaneous SQC/SPI/SQ fine-grain clock-gating overrides.
- `LDS_CONFIG` defines local data share behavior such as address-out-of-range reporting, wave32 interpolation issue control, and LDS/SQC fine-grain clock-gating overrides.
- `SQ_RANDOM_WAVE_PRI`, `SQ_FIFO_SIZES`, `SQ_ARB_CONFIG`, `SQ_PERF_SNAPSHOT_CTRL`, `SQ_INTERRUPT_AUTO_MASK`, and `SQ_INTERRUPT_MSG_CTRL` describe wave priority randomization, interrupt/thread-trace/export/VMEM FIFO sizing, workgroup arbitration intervals, snapshot timer controls, interrupt auto masks, and interrupt message stalling.
- `SQ_DSM_CNTL` and `SQ_DSM_CNTL2` expose design-for-stress/error-injection knobs for SGPR, LDS, SP, wavefront stall, SPI backpressure, injected delay selection, and single-write forcing.
- `SP_CONFIG`, `SQG_STATUS`, `SQG_GL1H_STATUS`, `SQG_CONFIG`, `SQ_DEBUG_HOST_TRAP_STATUS`, and `CC_GC_SHADER_RATE_CONFIG` cover SP cache/clock/debug control, SQG register busy state, GL1H ACK/XNACK error status, SQG prefetch and XNACK interrupt mask, host-trap pending count, and shader-rate DPFP rate selection.
- `SQ_WATCH{0..3}_ADDR_H`, `SQ_WATCH{0..3}_ADDR_L`, and `SQ_WATCH{0..3}_CNTL` define watchpoint address, mask, VMID, and valid fields.
- `SQ_IND_INDEX`, `SQ_IND_DATA`, and `SQ_CMD` define indirect wave/workitem indexing, indexed data payload, and command fields including mode, VMID check, wave ID, queue ID, and VM ID.

The `gc_shsdec` address block is dominated by shader export/interpolator debug and SPI controls:

- `SX_DEBUG_BUSY`, `SX_DEBUG_BUSY_2` through `SX_DEBUG_BUSY_10`, `SX_DEBUG_BUSY_5` through `SX_DEBUG_BUSY_9`, and `SX_DEBUG_1` provide a very broad busy/valid/free/idle view across SX color write-control queues, DB interface FIFOs, color buffer banks, position buffer banks, scoreboard state, export buffers, shader input/output handshakes, command/address paths, and reserved debug lanes.
- `SPI_PS_MAX_WAVE_ID`, `SPI_GFX_CNTL`, `SPI_DEBUG_READ`, `SPI_DSM_CNTL`, `SPI_DSM_CNTL2`, `SPI_EDC_CNT`, and `SPI_DEBUG_BUSY` define pixel-shader wave ID status, graphics control, debug read data, SPI stress/error injection control, EDC counters, and SPI busy status bits.
- `SPI_CONFIG_PS_CU_EN` and `SPI_PG_ENABLE_STATIC_WGP_MASK` gate pixel-shader CU/WGP enablement and static WGP masks.
- `SPI_WF_LIFETIME_CNTL`, `SPI_WF_LIFETIME_LIMIT_0` through `_5`, `SPI_WF_LIFETIME_STATUS_*`, and `SPI_WF_LIFETIME_DEBUG` define wavefront lifetime counter control, max-count limits, warning enables, status counters, interrupt-sent flags, and debug start-value override. The status registers are sparse by name: this chunk includes `_0`, `_2`, `_4`, `_6`, `_7`, `_9`, `_11`, `_13`, `_14`, `_15`, `_16`, `_17`, `_18`, `_19`, `_20`, and `_21`.
- `SPI_LB_CTR_CTRL`, `SPI_LB_WGP_MASK`, `SPI_LB_DATA_REG`, `SPI_LB_DATA_WAVES`, `SPI_LB_DATA_PERWGP_WAVE_HSGS`, and `SPI_LB_DATA_PERWGP_WAVE_CS` describe load-balancer counter loading, wave selection, clear-on-read, reset, WGP masks, raw counter data, and per-WGP wave counts for HS/GS/CS.
- `SPI_GDS_CREDITS`, `SPI_SX_EXPORT_BUFFER_SIZES`, `SPI_SX_SCOREBOARD_BUFFER_SIZES`, `SPI_CSQ_WF_ACTIVE_STATUS`, and `SPI_CSQ_WF_ACTIVE_COUNT_0` through `_3` define GDS command/data credits, SX export and scoreboard sizing, and active wavefront status/count/event fields.
- `SPIS_DEBUG_READ` and `BCI_DEBUG_READ` expose raw debug data fields.
- `SPI_P0_TRAP_SCREEN_*` and `SPI_P1_TRAP_SCREEN_*` define trap-screen memory-base low/high registers and minimum VGPR/SGPR thresholds for two trap-screen partitions.

The `gc_tpdec` address block covers texture address/data pipe controls:

- `TD_CNTL`, `TD_STATUS`, `TD_POWER_CNTL`, `TD_CNTL2`, and `TD_SCRATCH` expose TD filtering/math options, residency-map overrides, UTC-error VGPR preservation, gather4 modes, RT BVH4 arbiter selection, power-throttle disable, round-to-zero controls, scoreboard depth, formatter power options, LDS return FIFO credit, and scratch storage.
- `TA_CNTL`, `TA_CNTL_AUX`, `TA_CNTL2`, `TA_STATUS`, and `TA_SCRATCH` describe TA-to-SQ XNACK clock gating, aligner/TD FIFO credits, anisotropic filtering and deterministic-mode disables, gather and swizzle behavior, cubemap/array rounding, point-sample acceleration, element-size hashing, coordinate truncation, unlit-quad elimination, FIFO non-empty flags, per-subunit busy bits, aggregate busy state, and scratch storage.

The `gc_gdsdec` address block covers global data share configuration, faults, and reliability state:

- `GDS_CONFIG`, `GDS_CNTL_STATUS`, and `GDS_ENHANCE` expose write-disable/unused fields, GDS/GRBM/DS/GWS/ORD busy state, clamp state, credit busy bits, and enhancement controls.
- `GDS_PROTECTION_FAULT` and `GDS_VM_PROTECTION_FAULT` define fault-detected status plus metadata for GRBM source, SE/SA/WGP/SIMD/wave, GWS/OA/TMZ, VMID, and address.
- `GDS_EDC_CNT`, `GDS_EDC_GRBM_CNT`, `GDS_EDC_OA_DED`, `GDS_EDC_OA_PHY_CNT`, and `GDS_EDC_OA_PIPE_CNT` define single/double error counters and per-ME/pipe/PHY EDC status bits.
- `GDS_DSM_CNTL` and `GDS_DSM_CNTL2` define stress/error-injection controls for GDS memory, input queue, PHY command RAM, PHY data RAM, pipe memory, injection-delay selection, and single-write forcing.

The `gc_rbdec` address block begins at line 9469 and the chunk covers depth-buffer/debug registers through the first fields of `DB_DEBUG5`:

- `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_DEBUG6`, `DB_DEBUG7`, and the beginning of `DB_DEBUG5` cover many DB disable/force/debug knobs: depth/stencil compression disables, full tile fetches, forced depth/stencil reads, HiZ/HiS forcing, fast Z/stencil disables, viewport/Z-plane optimizations, context suspend insertion/deletion, EQAA behavior, TC write-combine controls, clock/debug gating, cache preload, VRS conflict controls, NOZ power savings, OSB deadlock fixes, LQO RAM optimization, and spare bits.
- `DB_ETILE_STUTTER_CONTROL`, `DB_LTILE_STUTTER_CONTROL`, `DB_EQUAD_STUTTER_CONTROL`, and `DB_LQUAD_STUTTER_CONTROL` define interval and timeout fields for tile/quad stutter behavior.
- `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH1`, `DB_FIFO_DEPTH2`, and `DB_FIFO_DEPTH3` define DB internal credits, depth/free/flush watermarks, cacheline availability, and FIFO depths for MI, MCC, QC, equad/etile/lquad/ltile, OSB, OREO, and quad read requests.
- `DB_SUBTILE_CONTROL` defines X/Y subtile encodings for MSAA1, MSAA2, MSAA4, MSAA8, and MSAA16.
- `DB_LAST_OF_BURST_CONFIG`, `DB_RING_CONTROL`, `DB_MEM_ARB_WATERMARKS`, and `DB_EXCEPTION_CONTROL` define burst sizing/timeouts, LOB generation/flush/coalescing/disabling behavior, ring counter control, memory arbitration watermarks, panic disables, auto flush, force summarize, and DTAG watermark fields.

## APIs, Types, and Functions

There are no C functions, types, structs, or enums in this chunk. The API surface is the exported macro namespace. Callers typically use these constants through AMDGPU register helpers rather than directly spelling bit operations:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` clears `REGISTER__FIELD_MASK` and inserts `field_value << REGISTER__FIELD__SHIFT`.
- `REG_GET_FIELD(value, REGISTER, FIELD)` extracts a masked field by applying `REGISTER__FIELD_MASK` and shifting by `REGISTER__FIELD__SHIFT`.
- `RREG32*`, `WREG32*`, `RREG32_SOC15`, `WREG32_SOC15`, and related helpers perform the actual MMIO read/write once an address from the matching GC 11.0.3 offset header has been selected.

The header also supports direct arithmetic patterns such as `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, but the driver convention is to use helper macros where possible to reduce manual mistakes.

## Control Flow and Data Flow

This header has no runtime control flow. Its data flow is compile-time macro substitution:

1. A GC 11.0.3 AMDGPU source file includes `gc/gc_11_0_3_offset.h` for register addresses and `gc/gc_11_0_3_sh_mask.h` for field layout.
2. Driver code selects a register address, often via `SOC15_REG_OFFSET(...)` or a generated register macro from the offset header.
3. Code reads, modifies, or writes a 32-bit register value using AMDGPU helper macros.
4. The helper expands to this header's `__SHIFT` and `_MASK` definitions to isolate the targeted field.

For status registers such as `WD_CNTL_STATUS`, `TD_STATUS`, `TA_STATUS`, `GDS_CNTL_STATUS`, and the `SX_DEBUG_BUSY*`/`SPI_DEBUG_BUSY` groups, the constants are usually read-side decode metadata. For control/debug registers such as `VGT_RESET_DEBUG`, `SQ_CONFIG`, `SQC_CONFIG`, `SPI_WF_LIFETIME_CNTL`, `TA_CNTL_AUX`, `GDS_DSM_CNTL2`, and `DB_DEBUG*`, the constants describe writable fields that can change GPU behavior.

## State and Persistence Behavior

The file itself stores no state. The state is in GPU hardware registers addressed elsewhere. These masks and shifts define how driver-visible state is interpreted and changed:

- Busy/status bits reflect transient hardware state for command distribution, geometry, shader, texture, global-data-share, depth-buffer, and cache/FIFO pipelines.
- Fault/protection fields preserve hardware fault metadata until the underlying register semantics clear or overwrite them; examples include UTCL1 fault/retry/PRT IDs and GDS protection fault address/source fields.
- Debug and control fields can persist in hardware across normal register-programming sequences until reset, context reinitialization, or a later MMIO write changes them.
- Error-injection and DSM controls (`SQ_DSM_*`, `SPI_DSM_*`, `GDS_DSM_*`) are especially stateful because enabling them affects future hardware stress/error behavior rather than merely reporting current state.
- Counter/status registers such as SPI wavefront lifetime status, SPI load-balancer counters, GDS EDC counters, and DB ring counters can have read, clear, or saturation semantics determined by hardware and by the code that programs companion control fields.

## Dependencies and Integration Points

This chunk depends on the rest of `gc_11_0_3_sh_mask.h` for the include guard and complete register-field namespace. It is meaningful only with the companion address header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which supplies the register addresses for these field definitions.

Repository integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`, which includes both `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h` for GC 11.0.3 graphics setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`, which includes this header for GC 11.0.3 GFXHUB register field access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`, which includes this header for IMU-specific GC 11.0.3 register programming.
- Shared AMDGPU register helper infrastructure that expects generated field names to be stable and exactly paired as `REGISTER__FIELD__SHIFT` plus `REGISTER__FIELD_MASK`.

The chunk also integrates with ASIC revision selection for GC 11.0.3 devices. Firmware declarations and display-side ASIC revision checks in nearby AMDGPU/DC code identify this generation, while the actual field-level programming for these GC registers is routed through the generated register headers.

## Risks and Gotchas

- Manual edits are high risk. A wrong mask or shift can compile cleanly but program or decode the wrong hardware bits.
- The chunk starts mid-register for `IA_UTCL1_STATUS_2`; generated-report tooling must merge with the previous chunk to reconstruct the whole register.
- Some fields are read-only status, some are writable controls, and some are clear-on-read/write-one-to-clear or hardware-latched in practice. The mask header does not encode access type, so callers need hardware knowledge and existing driver patterns.
- Many debug fields are negative controls (`DISABLE_*`, `FORCE_*`, `BYPASS_*`). Inverting semantics while composing register values can silently disable critical optimizations, coherency behavior, power management, or reset/workaround logic.
- The `DSM` and `*_ENABLE_ERROR_INJECT` fields are not ordinary tuning bits. Accidentally enabling stress/error-injection paths could produce artificial faults, EDC events, or data corruption symptoms.
- UTCL1, GDS protection fault, and VMID fields are security and fault-diagnostics sensitive. Mis-decoding source IDs, VMIDs, or fault addresses would mislead GPU fault reporting and recovery.
- Repeated or sparse numbered registers are intentional. Examples include `SQ_WATCH0` through `SQ_WATCH3`, multiple `SPI_WF_LIFETIME_STATUS_*` registers with skipped numbers, and `SX_DEBUG_BUSY*` sequences. Tooling should not assume dense numbering.
- A field whose hardware name includes `MASK` would generate `*_MASK_MASK`; this specific chunk has normal `_MASK` suffixes, but the broader generated-header convention must preserve such names.
- Several masks use full-width or high-bit fields such as `0xFFFFFFFFL`, `0xFFFF0000L`, and `0x80000000L`; signedness assumptions in external tooling can corrupt interpretation if values are parsed as signed 32-bit integers.

## Test and Validation Signals

Useful validation for this chunk is mostly build-time and hardware-integration oriented:

- Kernel/driver build coverage for translation units including `gc_11_0_3_sh_mask.h`, especially `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`.
- Static generation checks that every `REGISTER__FIELD_MASK` in the range has a corresponding `REGISTER__FIELD__SHIFT`, with explicit allowance for the chunk-boundary split at `IA_UTCL1_STATUS_2`.
- Static checks that each mask is compatible with its shift and field width, and that repeated groups such as `SQ_WATCH{0..3}`, `SPI_CSQ_WF_ACTIVE_COUNT_{0..3}`, and tile/FIFO depth registers preserve the expected symmetric layouts.
- Runtime smoke on GC 11.0.3 hardware that exercises graphics initialization, shader queue setup, GFXHUB setup, command submission, VM fault reporting, and GPU reset/recovery paths.
- Debugfs or tracing checks that decode busy/fault/status registers without impossible values, especially UTCL1 fault IDs, GDS protection fault metadata, TA/TD busy state, SPI wavefront lifetime counters, and DB watermarks/FIFO depths.
- Negative testing should avoid enabling DSM/error-injection fields outside controlled diagnostics.

## Chunk Boundary Notes

This is chunk 4 of 18 for `gc_11_0_3_sh_mask.h` in the current manifest. It begins at line 7504 with the tail of `IA_UTCL1_STATUS_2` and ends at line 9879 inside `DB_DEBUG5`; the remaining `DB_DEBUG5` fields continue in the next chunk. The final per-file report should reconcile this range with chunks 1-3 and 5-18 for complete GC 11.0.3 register coverage.

### subset-b-002530: lines 9880-12211

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 9880-12211

## Scope

This chunk is a large middle segment of the generated AMD GC 11.0.3 shift/mask header. It contains only C preprocessor `#define` constants for register bit positions (`__SHIFT`) and bit masks (`_MASK`). It declares no functions, structs, enums, storage, initialization tables, or executable code.

The range starts in the tail of `DB_DEBUG5`, covers DB/CB/GB render-backend and color/depth control masks, then moves through three GCEA address blocks (`gc_gceadec`, `gc_gceadec2`, and `gc_gceadec3`). It ends in the `gc_rmi_rmidec` address block at the first mask for `RMI_TCIW_FORMATTER1_CNTL`, so the last register block is intentionally incomplete in this chunk and must be reconciled with the next chunk during the per-file merge.

## Purpose

`gc_11_0_3_sh_mask.h` is generated hardware metadata for AMDGPU GC 11.0.3 ASICs. Its macros define how driver code encodes and decodes bitfields in 32-bit Graphics Core registers. Consumers pair this file with the matching `gc_11_0_3_offset.h` register addresses and, where available, `gc_11_0_3_default.h` reset values.

This chunk's purpose is to expose field-level register layout for:

- Depth Buffer (`DB`) debug, clock-gating override, FIFO depth, and interface control fields.
- Color Buffer (`CB`) hardware-control, DCC, cache-eviction, arbitration, and fine-grain clock-gating fields.
- Graphics backend (`GB`) address configuration, render backend mapping, GPU ID, backend-disable, redundancy, and daisy-chain fields.
- GCEA client-to-group mapping, DRAM/IO arbitration, virtual-channel assignment, laziness/combining, priority, credit, reserve, error, EDC, DSM, probe, and backdoor-credit fields.
- SPI queue/event throttling fields.
- RMI/RMIDE C crossbar, UTC/UTCL1, XNACK, demux, status, FIFO, and TCIW formatter fields.

The header is part of the register-description contract, not a policy module. Hardware programming policy lives in AMDGPU implementation files that use these macros with register access helpers.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register word.
- Consumers typically combine these macros through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and `SOC15_REG_OFFSET`.

Important register groups in this range:

- `DB_DEBUG5`: tail fields for depth-buffer debug/disable controls, including tile-cache preloading, secondary mip tail compression, FLQ/MCC checks, no-Z power savings, VRS conflicts, tile cache prefetch, HTILE harvesting, residency checks, PRT-related Z/S NACK behavior, and spare high bits.
- `DB_FGCG_SRAMS_CLK_CTRL` and `DB_FGCG_INTERFACES_CLK_CTRL`: fine-grain clock-gating override bits for DB SRAMs and DB interfaces to SC, CB export, RMI read/write request paths, tile/wave/free-wave paths, and CB RMI return.
- `DB_FIFO_DEPTH4`: OSB squad, tile, scoreboard, and event FIFO depth fields.
- `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `CC_RB_DAISY_CHAIN`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `GB_ADDR_CONFIG`, and `GB_ADDR_CONFIG_READ`: render-backend disable/redundancy, backend map, GPU ID, pipe/interleave/PKR/SE/RB topology, and readback topology layout.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_HW_CONTROL_3`, and `CB_HW_CONTROL_4`: Color Buffer behavior controls covering compression, metadata, DCC, CMASK/HTILE interaction, hazard/workaround bits, state-machine behavior, event/export handling, and other generated hardware knobs.
- `CB_DCC_CONFIG` and `CB_DCC_CONFIG2`: DCC RAM, meta, pipe/hash, cache, and configuration fields.
- `CB_HW_MEM_ARBITER_RD` and `CB_HW_MEM_ARBITER_WR`: read/write arbitration selection and queue/control masks.
- `CB_FGCG_SRAM_OVERRIDE`, `CHICKEN_BITS`, and `CB_CACHE_EVICT_POINTS`: generated override/debug/cache eviction fields.
- `GCEA_DRAM_*` and `GCEA_IO_*` client/group blocks: read/write `CLI2GRP_MAP0/1` fields map 32 client IDs (`CID0`-`CID31`) into four groups; `GRP2VC_MAP` assigns groups to virtual channels; `LAZY`, `CAM_CNTL`, page/group burst, priority aging, queuing, fixed, urgency, masking, and quantum threshold registers control arbitration policy.
- `GCEA_SDP_*`: final SDP arbitration, DRAM/IO priority, tag/write/read/probe credit limits, virtual-channel tag and VCC/VCD reserves, request controls, backdoor command/data/misc credits, and enable fields.
- `GCEA_MISC`, `GCEA_MISC2`, `GCEA_LATENCY_SAMPLING`, `GCEA_MAM_CTRL`, `GCEA_MAM_CTRL2`, `GCEA_RRET_MEM_RESERVE`, and `GCEA_PROBE_*`: miscellaneous GCEA routing, sampling, MAM memory addressing/latency controls, read-return reserves, probe mapping/filtering, and block/request override fields.
- `GCEA_EDC_CNT`, `GCEA_EDC_CNT2`, and `GCEA_EDC_CNT3`: error-detection/correction count and mask fields for DRAM, GMI, IO, return, SDP, and MAM memories.
- `GCEA_DSM_CNTL`, `GCEA_DSM_CNTLA`, `GCEA_DSM_CNTLB`, `GCEA_DSM_CNTL2`, `GCEA_DSM_CNTL2A`, and `GCEA_DSM_CNTL2B`: DSM irritator, single-write, error-injection, and injection-delay controls across DRAM/GMI/IO/page/MAM memories.
- `GCEA_ERR_STATUS`: SDP response status, data status/parity, clear, busy-on-error, FUE, fatal interrupt, and level interrupt fields.
- `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL`: SPI packet/queue event and export throttle controls.
- `RMI_GENERAL_CNTL`, `RMI_GENERAL_CNTL1`, and `RMI_GENERAL_STATUS`: RMI global controls and status/error fields, including clock gating, write-combine and reorder controls, skid FIFO errors, PRT/XNACK related state, and reserved/status bits.
- `RMI_SUBBLOCK_STATUS0` through `RMI_SUBBLOCK_STATUS3`: UTC external latency FIFO usage, skid FIFO free-space, PRT FIFO usage, and TCIW in-flight counters.
- `RMI_XBAR_CONFIG`, `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_DEMUX_CNTL`, `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, and `RMI_UTC_UNIT_CONFIG`: RMI crossbar arbitration, probe pop/fifo tuning, UTC/XNACK timer behavior, demux arbitration, UTCL1 GPUVM/invalidation/response/permission/perf/EDC controls, and TMZ request enable bits.
- `RMI_TCIW_FORMATTER0_CNTL` and the beginning of `RMI_TCIW_FORMATTER1_CNTL`: TCIW maximum in-flight, reorder-disable, write-combine, and fault-return-data controls. The `FORMATTER1` block continues after line 12211.

## Control Flow

There is no runtime control flow in this chunk. The C preprocessor substitutes constants at compile time.

The implied consumer flow is:

1. Include the GC 11.0.3 offset and shift/mask headers selected by the active ASIC generation.
2. Select a register address from the companion offset header.
3. Construct or decode the register value by applying the field mask and shift, often through `REG_SET_FIELD` or `REG_GET_FIELD`.
4. Read or write the register using SOC15/MMIO helpers or an indirect register path when the register belongs to an indexed block.

For example, a consumer programming a GCEA priority register would preserve unrelated bits, clear a field using `GCEA_*_MASK`, shift the new field value by `GCEA_*__SHIFT`, then write the full 32-bit word. A consumer collecting RMI diagnostics would read a status register and isolate FIFO or error fields using the corresponding `RMI_*_MASK` values.

## State And Persistence

This chunk stores no software state and allocates no memory. All macros are compile-time constants.

The represented state is hardware state:

- DB/CB/GB fields affect or describe render-backend topology, compression/cache behavior, fine-grain clock gating, debug disables, FIFO depths, backend disable maps, and RB redundancy.
- GCEA fields configure and report cross-client arbitration, virtual-channel routing, request batching, credit reserves, page/group burst limits, latency sampling, MAM behavior, EDC accounting, error status, and debug/error-injection state.
- SPI fields affect export throttling and packet/queue event control.
- RMI fields configure and report request crossbar routing, UTC/UTCL1 GPUVM behavior, XNACK/PRT handling, FIFO occupancy/free-space, TCIW formatting, demux arbitration, and error/status signals.

Persistence depends on the hardware register class, not on this header. Values may be reset by GPU reset, suspend/resume, runtime power-state transitions, firmware initialization, or ASIC-specific boot sequences. Some fields are normal policy knobs; others are diagnostic, reserved, debug, or error-injection controls that should not be casually programmed by generic paths.

## Dependencies And Integration Points

This generated header depends on the rest of the GC 11.0.3 register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies the matching register addresses.
- Other GC 11.0.3 generated headers supply defaults and related block metadata where present.
- AMDGPU implementation files include the generated register headers through ASIC-specific or SOC15 paths and use the macros with MMIO helpers, register field helpers, and indirect register access sequences.
- DB/CB/GB masks integrate with graphics initialization, render-backend harvesting/topology setup, compression/DCC policy, and workaround programming.
- GCEA masks integrate with memory fabric/client arbitration, GL2C/XBR/SDP credit tuning, error reporting, and low-level diagnostics.
- RMI and UTC/UTCL1 masks integrate with GPUVM, XNACK/PRT behavior, RMI crossbar configuration, fault handling, and status collection.

The file must remain synchronized with the hardware generator. A mask or shift mismatch can compile cleanly while programming the wrong bitfield at runtime.

## Risks And Edge Cases

- Generated-header drift is the main risk. Offsets, masks, shifts, and defaults must all come from the same GC 11.0.3 hardware database.
- This chunk begins inside `DB_DEBUG5` and ends inside `RMI_TCIW_FORMATTER1_CNTL`; merge/reconciliation must combine adjacent chunks before making whole-file statements about those two register blocks.
- Many fields are debug, workaround, reserved, clock-gating, or error-injection controls. Incorrect writes can cause hangs, performance loss, power regressions, false error reporting, or broken reset/resume behavior.
- GCEA has many repeated read/write and DRAM/IO register families with similar names and bit layouts. Copying a read mask into a write path, or a DRAM field into an IO path, can silently target the wrong policy.
- The `CID0`-`CID31`, `VC0`-`VC7`, and group-indexed macros are dense bitfields. Off-by-one client, group, or virtual-channel indexing errors are plausible even when the masks are correct.
- Some masks cover reserved bits or high-bit status fields. Code should avoid writing reserved fields unless the hardware sequence explicitly requires it.
- RMI/UTCL1 fields touch GPUVM response, fault, invalidate, permission, XNACK, and TMZ behavior. Bad values can surface as page-fault handling failures, retry/XNACK problems, memory-permission bugs, or fault-reporting anomalies.
- EDC and DSM controls include error-injection and irritator fields. These should be isolated to diagnostics, validation, or hardware bring-up paths.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are build, generated-header, and hardware-integration oriented:

- Compile AMDGPU GC 11.0.3 paths that include this header; missing or renamed macros should fail at build time.
- Regenerate the header from the authoritative hardware database and compare the emitted masks/shifts and block ordering.
- Run GPU initialization, reset, suspend/resume, and runtime power-management tests on GC 11.0.3 hardware to catch DB/CB/GB/GCEA/RMI programming drift.
- Exercise graphics workloads that use DCC/compression, render-backend topology, and memory arbitration to expose CB/DB/GB or GCEA policy mistakes.
- Run GPUVM, PRT, XNACK, and fault-handling tests to validate RMI/UTC/UTCL1 field usage.
- Monitor hardware error and EDC counters, interrupt behavior, and fault logs when touching `GCEA_ERR_STATUS`, `GCEA_EDC_*`, `RMI_GENERAL_STATUS`, or DSM injection fields.
- Use low-level register dumps before and after init/resume/reset to verify expected fields are set and reserved bits remain untouched.

### subset-b-002531: lines 12212-14595

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 12212-14595

## Chunk Scope

This chunk is a generated AMD GC 11.0.3 register shift/mask header segment. It contains C preprocessor constants only: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros for memory-mapped GPU registers. There are no functions, structs, enums, callbacks, locks, allocations, runtime branches, or software-owned storage declarations.

The range covers 2,170 `#define` entries: 1,083 shift definitions and 1,087 mask definitions across 198 visible register-group comments and 8 address-block markers. The chunk starts inside the `RMI_TCIW_FORMATTER1_CNTL` group with only the tail mask entries from the previous chunk, then covers complete RMI scoreboard/xbar/status/spare groups, PMM/GCR/UTCL1 control/status groups, shared GCMC and GCVM L2 page-fault/cache controls, ATC L2 controls, GCL2TLB and GPUVA/VMID translation-assist fields, GCMC VM aperture fields, `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL`, `GCVM_CONTEXTS_DISABLE`, and most of the GCVM invalidate-engine semaphore/request/ack families. It ends inside `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32`; the remainder of that range-address family is in the next chunk.

## Purpose

`gc_11_0_3_sh_mask.h` supplies symbolic bitfield definitions for GC 11.0.3 AMDGPU hardware programming. The matching `gc_11_0_3_offset.h` file supplies the register offsets, while this header supplies the bit positions and masks that consumers pass to helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15`.

This slice focuses on request-interface and graphics-VM hardware:

- RMI request-interface controls: scoreboard flush/VMID-invalidation status, xbar arbitration, dynamic clock masks, UTCL1 retry/fault status, RB-to-GLX CID maps, XNACK debug bits, spare/chicken bits, and redundancy controls.
- GCR/PMM/UTCL1 controls: PIO access, page migration monitor control/status, UTCL1 arbitration, bypass, wakeup, invalidation, stall, LRU, hit/miss, and fault-status fields.
- Shared GCMC and GCVM aperture controls: NB MMIO aperture, PCI arbitration, DRAM top, framebuffer offset, system aperture default address, steering, reset requests, memory light sleep, cacheable/local system-memory ranges, local framebuffer range/lock, L2 clock-gating and harvest controls, and group return-fault status.
- GCVM L2 controls: cache enable/mode, PTE/PDE fragment sizes, outstanding request limits, invalidation queue control, dummy/default fault addresses, L2 protection fault policy/status/address registers, identity aperture and physical offset registers, MM group routing classes, reserved-CID bank selection, parity, GCR linkage, walker throttling, PTE cache dump, and credit-safety fields.
- ATC L2 and GCL2TLB controls: ATC L2 cache settings, cache-data readback windows, status, memory light-sleep, SDP port controls, TLB status, and GPUVA/VMID translation-assist request/response fields.
- Per-VMID context and invalidation controls: 16 `GCVM_CONTEXTn_CNTL` groups, context disable bits, 18 invalidation-engine semaphore/request/ack groups, and the start of invalidate address-range groups.

Although the repository path includes `ceph-client`, this file is AMD GPU driver hardware metadata, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no callable APIs or local types. The exported interface is the generated macro namespace.

Key macro families in this chunk:

- `RMI_SCOREBOARD_CNTL`, `RMI_SCOREBOARD_STATUS0`, `RMI_SCOREBOARD_STATUS1`, and `RMI_SCOREBOARD_STATUS2` describe completion and status fields for RB0/RB1 flushes, VMID invalidation progress, requested VMID, UTC/done state, flush type, force-done status, counters, underflow/overflow flags, and timestamp flush completion.
- `RMI_XBAR_ARBITER_CONFIG` and `RMI_XBAR_ARBITER_CONFIG_1` describe arbitration modes, weighted round-robin breaks, stall override/timer fields, and RD/WR weights for RMI xbar arbitration.
- `RMI_CLOCK_CNTRL`, `RMI_UTCL1_STATUS`, `RMI_RB_GLX_CID_MAP`, `RMI_XNACK_DEBUG`, `RMI_SPARE`, `RMI_SPARE_1`, `RMI_SPARE_2`, and `CC_RMI_REDUNDANCY` define dynamic clock busy/wakeup masks, UTCL1 fault/retry/PRT status, CB/DB client-ID routing, per-VMID XNACK debug state, no-fill and reorder spare controls, address masks, arbitration behavior, and redundant lane controls.
- `GCR_PIO_CNTL`, `GCR_PIO_DATA`, `PMM_CNTL`, and `PMM_STATUS` define graphics-cache PIO command/data and page migration monitor enable, mode, stall, trigger, busy, fault, and interrupt-status fields.
- `UTCL1_CTRL_1`, `UTCL1_ALOG`, and `UTCL1_STATUS` cover UTCL1 arbitration/burst settings, clock-gating controls, no-reorder and LRU behavior, line-fragment mode, forced invalidation acknowledgements, page-size controls, request counters, fault IDs, hit/miss counters, and PRT/fault/retry status bits.
- `GCMC_VM_*`, `GCUTCL2_*`, and `GCMC_SHARED_*` macros describe shared VM apertures and global configuration: MMIO base/limit, PCI controls, top-of-DRAM, FB offset, system aperture default address, steering, reset request, memory power, cacheable DRAM range, local system memory and framebuffer ranges, APT controls, lock bits, active function ID, clock-gating busy masks, no-allocate controls, harvest bypass groups, and group return-fault status.
- `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_L2_CNTL4`, and `GCVM_L2_CNTL5` define L2 TLB/cache behavior: enable bits, bank select, fragment size, cache mode, invalidation mode, PTE/PDE fetch and fragment controls, outstanding request limits, walker credits, and cache small/big fragment sizes.
- `GCVM_L2_STATUS`, `GCVM_DUMMY_PAGE_FAULT_*`, `GCVM_INVALIDATE_CNTL`, `GCVM_L2_PROTECTION_FAULT_CNTL`, `GCVM_L2_PROTECTION_FAULT_CNTL2`, `GCVM_L2_PROTECTION_FAULT_MM_CNTL3`, `GCVM_L2_PROTECTION_FAULT_MM_CNTL4`, `GCVM_L2_PROTECTION_FAULT_STATUS`, `GCVM_L2_PROTECTION_FAULT_ADDR_*`, and `GCVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` define fault counters, dummy-page handling, invalidation queue controls, default-page routing, interrupt/crash behavior, CID filtering, status decoding, and fault/default physical address fields.
- `GCVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `GCVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*` define identity-mapping aperture boundaries and offsets.
- `GCVM_L2_MM_GROUP_RT_CLASSES`, `GCVM_L2_BANK_SELECT_RESERVED_CID`, `GCVM_L2_BANK_SELECT_RESERVED_CID2`, `GCVM_L2_CACHE_PARITY_CNTL`, `GCVM_L2_ICG_CTRL`, `GCVM_L2_GCR_CNTL`, `GCVML2_WALKER_*`, `GCVM_L2_PTE_CACHE_DUMP_*`, `GCVM_L2_BANK_SELECT_MASKS`, and `GCVML2_CREDIT_SAFETY_*` define routing class maps, bank selection, parity/test controls, clock-gating, GCR integration, page-walker throttles, diagnostic PTE cache dump controls, and credit-safety settings.
- `GC_ATC_L2_*` macros define ATC L2 cache control, status, cache readback data words, miscellaneous clock-gating, memory light-sleep, and SDP port controls.
- `GCL2TLB_TLB0_STATUS` and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_*` define TLB validity/error status and request/response payload fields for translation assistance.
- `GCMC_VM_FB_LOCATION_*`, `GCMC_VM_AGP_*`, `GCMC_VM_SYSTEM_APERTURE_*`, and `GCMC_VM_MX_L1_TLB_CNTL` define framebuffer, AGP, system aperture, and L1 TLB controls used by VM hub setup.
- `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` provide repeated per-context fields: context enable, page-table depth and block size, range/dummy/PDE0/valid/read/write/execute protection fault interrupt bits, corresponding default-page enable bits, and `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT`.
- `GCVM_CONTEXTS_DISABLE` exposes disable bits for VM contexts 0 through 15 plus corresponding effective `DISABLE_CONTEXT_STATUS` bits.
- `GCVM_INVALIDATE_ENG0_SEM` through `GCVM_INVALIDATE_ENG17_SEM`, `GCVM_INVALIDATE_ENG0_REQ` through `GCVM_INVALIDATE_ENG17_REQ`, and `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK` define the GCVM invalidation engine handshake. Each request word includes per-VMID invalidation bits, `FLUSH_TYPE`, L2 PTE/PDE invalidation selections, L1 PTE invalidation, protection-fault status address clearing, request logging, and a 4K-page-only option.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32`, `GCVM_INVALIDATE_ENG0_ADDR_RANGE_HI32`, and the first field of `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32` begin the optional logical page address range definitions for invalidation engines. The rest of this repeated address-range family belongs to the next chunk.

The generated naming convention is itself part of the API. `REG_SET_FIELD(value, GCVM_INVALIDATE_ENG0_REQ, INVALIDATE_L2_PTES, 1)` depends on both `GCVM_INVALIDATE_ENG0_REQ__INVALIDATE_L2_PTES__SHIFT` and `GCVM_INVALIDATE_ENG0_REQ__INVALIDATE_L2_PTES_MASK` being spelled exactly as generated.

## Control Flow

This header has no software control flow. Runtime sequencing is in the AMDGPU consumers that include the header.

The main direct GC 11.0.3 consumer in this tree is `drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`. It uses this chunk's macros to:

- Build a VM invalidation request in `gfxhub_v3_0_3_get_invalidate_req()` by setting `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0`, `INVALIDATE_L2_PDE1`, `INVALIDATE_L2_PDE2`, `INVALIDATE_L1_PTES`, and `CLEAR_PROTECTION_FAULT_STATUS_ADDR` on `GCVM_INVALIDATE_ENG0_REQ`.
- Decode and print `GCVM_L2_PROTECTION_FAULT_STATUS` fields such as `CID`, `MORE_FAULTS`, `WALKER_ERROR`, `PERMISSION_FAULTS`, `MAPPING_ERROR`, and `RW`.
- Program framebuffer and memory-controller aperture state with `GCMC_VM_FB_LOCATION_BASE`, `GCMC_VM_FB_OFFSET`, and system/AGP aperture registers.
- Initialize L2 cache and TLB controls with `GCVM_L2_CNTL*` and `GCMC_VM_MX_L1_TLB_CNTL`.
- Enable context 0 as the system domain through `GCVM_CONTEXT0_CNTL`.
- Program contexts 1 through 15 through offset-distance writes based on `GCVM_CONTEXT1_CNTL`, setting page-table depth, block size, default-page routing, and retry/no-retry policy.
- Program all 18 invalidation engine address ranges using the `GCVM_INVALIDATE_ENG0_ADDR_RANGE_*` offset family and `eng_addr_distance`.
- Toggle L2 protection fault default behavior through `GCVM_L2_PROTECTION_FAULT_CNTL`.
- Populate `amdgpu_vmhub` offsets and distances from `regGCVM_CONTEXT*`, `regGCVM_INVALIDATE_ENG*`, and `regGCVM_L2_PROTECTION_FAULT_*` offsets, while using this chunk's context fault interrupt masks for `vm_cntx_cntl_vm_fault`.

Other direct include users are `drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c` and `drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`. `imu_v11_0_3.c` includes the same generated mask namespace for IMU/RLC golden-register programming, including `GCVM_CONTEXT0_CNTL` entries.

The header does not encode register ordering, polling delays, read-only/write-one-clear behavior, power-domain access rules, or SR-IOV ownership. Those requirements live in the consuming code and hardware programming guides.

## State And Persistence Behavior

The header persists no software state. It names fields in hardware registers whose values persist according to GC block lifetime: until explicitly rewritten, reset by hardware, restored by firmware/golden-register tables, lost through power gating, or restored during driver resume/reset recovery.

Important represented hardware state includes:

- In-flight request and flush state in RMI scoreboard and xbar registers, including completion, running counters, overflow/underflow conditions, and timestamp flush state.
- Request routing and arbitration state for RMI, GCR, UTCL1, GCUTCL2, and ATC L2, including clock-gating, burst, wakeup, reorder, no-fill, redundancy, and credit-safety behavior.
- Global VM aperture state for MMIO, framebuffer, AGP, system aperture, cacheable DRAM, local system memory, local framebuffer, and default fault address windows.
- GCVM L2 cache/TLB state, including cache enablement, fragment sizes, bank selection, invalidation control, PTE/PDE behavior, parity handling, walker throttling, diagnostic cache dump, and group routing.
- Protection fault state, including sticky or live fault status, fault addresses, default-page addresses, CID filtering, interrupt/default-page policy, and crash-on-fault policy.
- Per-context VMID state in the 16 `GCVM_CONTEXTn_CNTL` registers, including page-table geometry and fault handling policy.
- Invalidation-engine state across 18 engines: semaphore, request, acknowledgement, and address-range register fields.
- Translation-assist state for GPUVA/VMID requests and responses.

`gfxhub_v3_0_3.c` treats many of these registers as driver-managed VM hub state during GART enable/disable and fault policy changes. SR-IOV restrictions are explicit for some identity-aperture and L2 protection-fault programming: the VF path skips those writes because the PF programs them instead.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which provides `reg...`/`mm...` register offsets and offset spacing used with these masks. GC 11.0.3 code also commonly includes default/golden-register data and SOC15 register helper infrastructure.

Observed direct include users in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`

Semantic integration points include:

- AMDGPU VM hub setup, GART aperture programming, context page-table programming, and invalidation request generation.
- VM fault reporting and recovery paths, including protection fault status decoding and default-page/crash policy.
- KFD-facing retry/no-retry behavior, because `GCVM_CONTEXTn_CNTL__RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` controls how memory faults interact with XNACK/no-retry process policy.
- IMU/RLC golden-register initialization and firmware-assisted hardware setup.
- GPU reset, suspend/resume, runtime power management, and SR-IOV PF/VF split ownership.
- Debug and diagnostics that read RMI, UTCL1, ATC L2, TLB, and PTE cache dump state.

The macros depend syntactically only on the C preprocessor, but semantically they are hardware ABI. Mixing this header with a different GC generation's offset header can compile while addressing the wrong register layout.

## Risks And Maintenance Notes

- Generated bitfield drift is high impact. A one-bit shift or mask error can alter VM fault policy, cache invalidation, aperture routing, retry behavior, or low-level request arbitration.
- This chunk has artificial boundaries. It starts at the tail of `RMI_TCIW_FORMATTER1_CNTL` and ends inside `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32`; merge/reconciliation must combine adjacent chunk documents before treating either boundary register family as complete.
- The VM context fields are highly repetitive across 16 contexts. Consumers often program context families by offset distances, so mismatched register spacing or a context-specific field typo can create VMID-dependent failures.
- Invalidation request construction is sensitive. Missing or incorrectly positioned `INVALIDATE_L2_PTES`, PDE bits, `INVALIDATE_L1_PTES`, `FLUSH_TYPE`, or per-VMID bits can leave stale GPU translations after page table updates.
- Fault handling policy is safety-critical. Default-page routing, interrupt enablement, retry/no-retry, and crash-on-fault fields determine whether faults are logged, retried, hidden behind dummy/default pages, or escalated to reset.
- Aperture fields affect global memory routing. Bad framebuffer, AGP, system aperture, local system-memory, or default-address programming can cause incorrect VRAM/host-memory access, spurious VM faults, or silent data exposure.
- Several RMI, UTCL1, ATC, and GCVM fields are named as disables, overrides, force bits, debug controls, spare bits, or test/parity controls. Whole-register writes must preserve unrelated and reserved bits unless hardware documentation or generated defaults explicitly define safe values.
- Status, request, acknowledgement, semaphore, and counter fields are mixed in adjacent groups. The header does not tell whether fields are read-only, write-one-to-clear, self-clearing, sticky, or firmware-owned.
- SR-IOV access restrictions matter. `gfxhub_v3_0_3.c` already avoids some writes from VFs; similar assumptions should be checked before adding new programming against fields in this range.

## Test Signals

Useful validation is build-time, generated-data, and hardware-integration oriented:

- Compile/preprocess GC 11.0.3 paths that include `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h`: `gfxhub_v3_0_3.c`, `gfx_v11_0_3.c`, and `imu_v11_0_3.c`.
- Static consistency checks that every complete field in the full header has matching `__SHIFT` and `_MASK` macros, with explicit exceptions only for chunk-boundary splits.
- Cross-check register names against `gc_11_0_3_offset.h`, especially context distances, invalidation engine distances, and address-range distances used by `amdgpu_vmhub`.
- VM hub runtime tests on GC 11.0.3 hardware: GART enable/disable, VMID context programming, page-table base/start/end setup, page-table updates, VMID invalidation, range invalidation where supported, and acknowledgement polling.
- Fault tests that trigger range, PDE, valid, read, write, execute, dummy-page, retry, and no-retry faults, then verify `GCVM_L2_PROTECTION_FAULT_STATUS` decoding, default-page behavior, interrupt behavior, and fault address reporting.
- Suspend/resume, GPU reset, runtime power-gating, IMU/RLC golden-register restore, and SR-IOV VF/PF tests to confirm ownership and persistence assumptions for GCVM L2/context/aperture registers.
- Stress tests with graphics and compute workloads under VM pressure, BO eviction/migration, userptr, KFD queues, SDMA interaction, and memory oversubscription to catch stale translations, retry storms, unexpected default-page use, or GPU hangs.
- Diagnostic checks for RMI/UTCL1/ATC state: scoreboard counters should not underflow/overflow during normal invalidation traffic, UTCL1 fault/retry status should match induced conditions, and PTE cache dump or translation-assist readbacks should be sampled only under synchronized debug conditions.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 12212-14595 of `gc_11_0_3_sh_mask.h`. Earlier chunks should cover the beginning of `RMI_TCIW_FORMATTER1_CNTL` and preceding RMI/UTCL1 fields. Later chunks should continue the invalidation address-range family beginning at `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32`, then cover page-table base/start/end and subsequent GC 11.0.3 register groups. The final per-file report should treat this file as generated AMD GC 11.0.3 hardware register metadata used by AMDGPU VM, GFX, KFD-facing fault policy, and IMU/golden-register paths.

### subset-b-002532: lines 14596-17258

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 14596-17258

## Purpose

This chunk is generated AMD GC 11.0.3 register bitfield metadata. It contains no executable C code; it exposes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD-adjacent paths, graphics hub setup, interrupt/error handling, command processor setup, and profiling/debug code to compose or decode MMIO register values for this ASIC generation. The matching register offsets are in `gc_11_0_3_offset.h`.

The selected range covers the tail of GCVM invalidation address-range fields, all 16 GCVM context page-table base/start/end address layouts, per-PF/VF PTE cache fragment sizing, several GCVM/ATC/L2/TLB performance-counter blocks, IOMMU and MARC translation controls, shader-program register layouts for PS/GS/HS/LS/ES stages, compute dispatch register layouts, and the beginning of command-processor queue/error control fields. Although this repository path is under `ceph-client`, this source is AMD GPU driver hardware metadata, not filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, memory allocations, or direct I/O operations in this range. The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for that field.
- Consumers combine these masks with `reg<REGISTER>` offsets from `gc_11_0_3_offset.h` and helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

Major register groups in this chunk:

- `GCVM_INVALIDATE_ENG1_ADDR_RANGE_*` through `GCVM_INVALIDATE_ENG17_ADDR_RANGE_*`: per-invalidation-engine low/high logical page range fields. The low word carries an `S_BIT` and low logical-page bits; the high word carries upper logical-page bits. The chunk starts in the middle of the engine 1 low-word definition, while engine 0 and the first engine 1 fields are in the preceding chunk.
- `GCVM_CONTEXT0_*` through `GCVM_CONTEXT15_*`: page-table base, start, and end address fields for each VM context. Base registers split the 64-bit page-directory-entry address into low/high words; start/end registers split logical page numbers into low 32 bits plus a small high field.
- `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `GCVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`: PTE cache fragment-size controls, with small-fragment, big-fragment, and bank-select fields per context.
- `GCVML2_*`, `GCMC_VM_L2_*`, `GCUTCL2_*`, `GC_ATC_L2_*`, and `GCL2TLB_*` performance-counter registers: counter low/high readback, event selection, mode, per-counter configuration, and result-control fields for GCVM L2, UTCL2, ATC L2, and L2 TLB monitor blocks.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVM_IOMMU_*`, `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`, and `GCUTC_TRANSLATION_FAULT_CNTL*`: translation bypass, GPU-host translation enable, IOMMU enable and optimization knobs, MMIO control, GPUVA/VMID translation-assist controls, and default translation-fault physical-page attributes.
- `GCMC_VM_MARC_BASE_*`, `GCMC_VM_MARC_RELOC_*`, `GCMC_VM_MARC_LEN_*`, and `GCMC_VM_MARC_PFVF_MAPPING_*`: MARC aperture base, relocation, length, and PF/VF enable mapping fields for up to 16 windows.
- `SPI_SHADER_*_PS`, `SPI_SHADER_*_GS`, `SPI_SHADER_*_HS`, `SPI_SHADER_PGM_LO/HI_ES`, and `SPI_SHADER_PGM_LO/HI_LS`: graphics shader program resource, checksum, program-address, user-data, request-control, accumulator, and meshlet fields. Resource fields include CU enable masks, VGPR/SGPR sizing, priority, floating-point mode, privilege/debug/trap bits, LDS sizing, exception enables, shared VGPR count, and stage-specific controls.
- `COMPUTE_*`: compute dispatch packet and state fields, including dispatch initiator flags, dimensions, starts/restarts, thread counts, pipeline/perfcount enable, program address, AQL dispatch packet address, scratch base, program resource fields, VMID, resource limits, destination/static thread management by shader engine, temp-ring size, trace enable, dispatch IDs, relaunch payloads, wave restore addresses, user data, dispatch tunnel/end, and reserved scratch registers.
- `CP_CU_MASK_*`, `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CPC_INT_*`, `CP_VIRT_STATUS`, `CP_GFX_ERROR`, `CP{G,C,F}_UTCL1_CNTL`, `CP_AQL_SMM_STATUS`, `CP_RB0_BASE`, `CP_RB_BASE`, and the beginning of `CP_RB0_CNTL`: command processor compute-unit mask programming, EOP queue wait timing, CPC clock-gating sync timing, interrupt address/PASID/VMID payload fields, virtualization status, UTCL1 error bits, UTCL1 control bits, AQL SMM status, ring-buffer base addresses, and initial ring-buffer control fields.

Fields named `RESERVED`, `SH_RESERVED_REG*`, or full-width `DATA` are still part of the generated register contract. They are not evidence that whole-register writes are safe; consumers need hardware-guide context and should preserve undocumented bits unless reset-value programming explicitly requires otherwise.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from driver code that includes it:

1. A GC 11.0.3 consumer includes `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h`.
2. The consumer selects a `reg*` address macro, sometimes using an offset stride for per-VMID or per-engine register arrays.
3. The consumer composes or decodes values with the shift/mask macros.
4. AMDGPU register helpers perform the actual MMIO access while the relevant block initialization, queue setup, VM update, profiling, interrupt, reset, or power-management sequence owns ordering.

Concrete examples in this tree include `gfxhub_v3_0_3_setup_vm_pt_regs()`, which writes `regGCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` with per-VMID offsets, and `gfxhub_v3_0_3_init()`, which derives context and invalidation-engine strides from generated offsets. Generic GFX 11 ring setup code programs `CP_RB0_CNTL` with `REG_SET_FIELD(..., CP_RB0_CNTL, RB_BUFSZ, ...)` and `RB_BLKSZ`, illustrating how this mask namespace is consumed with SOC15 register helpers.

The chunk describes fields needed for GPU VM setup, translation fault behavior, performance-counter programming, shader-stage and compute-dispatch state, and CP queue/error handling. It does not encode legal access order, read-only versus write-only behavior, self-clearing semantics, power-gating requirements, firmware ownership, or reset sequencing.

## State And Persistence Behavior

The file stores no software state and persists nothing. It only names hardware state exposed through GC 11.0.3 registers.

The represented hardware state is broad:

- GCVM context state includes per-VMID page-table root addresses and valid logical address ranges.
- GCVM invalidation state includes per-engine logical-page ranges for targeted TLB/cache invalidation.
- L2, ATC, UTCL2, and TLB performance-counter state includes event selection, modes, configuration, result control, and counter readback values.
- Translation and virtualization state includes VMID bypass masks, GPU-host translation enable, IOMMU enable/optimization/MMIO settings, translation-assist control, default translation-fault page attributes, and MARC aperture mapping for PF/VF access.
- Shader state includes program addresses, resource descriptors, checksums, user SGPR payloads, accumulators, request controls, trap/debug/exception bits, meshlet layout fields, and stage-specific resource sizing for graphics shader stages.
- Compute state includes dispatch dimensions, workgroup/thread counts, shader program/scratch addresses, program resources, VMID, SE/CU targeting, static thread-management masks, temp-ring size, trace controls, relaunch and restore state, and user-data payloads.
- Command-processor state includes CU mask address/policy, EOP wait timing, CPC clock-gating sync timing, interrupt address/PASID metadata, graphics error status bits, UTCL1 control knobs, AQL SMM status, and ring-buffer base/control fields.

Persistence is hardware-defined. Some fields are programmed configuration that should survive until GPU reset, suspend/resume, power-gating, or reinitialization; others are live status, performance counters, interrupt payloads, error latches, or write-trigger controls. The masks alone do not identify volatility or side effects, so driver code must use ASIC-specific sequencing and preserve unrelated bits.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which provides matching `reg*` offsets and address-block placement. For this chunk, relevant address blocks include GCVM/L2 performance and PSP-facing translation blocks, `gc_shdec` shader registers, and the beginning of `gc_cppdec` command-processor registers.

GC 11.0.3-specific include users observed in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`

Integration points include GFXHUB v3.0.3 GART/aperture setup, per-VMID page-table programming, TLB invalidation, VM fault handling, SR-IOV/PF-VF translation aperture setup, GPU-host/IOMMU translation controls, profiling through GCVM/ATC/TLB counters, shader program setup through PM4 packets or firmware-owned programming, compute dispatch packet construction, command-processor ring initialization, CP graphics error reporting, UTCL1 control, GPU reset/recovery, suspend/resume, and golden-register initialization through IMU/RLC tables.

## Risks And Edge Cases

- Header/offset mismatches are the largest correctness risk. These GC 11.0.3 masks must be paired with `gc_11_0_3_offset.h`; using a different GC generation can compile while programming the wrong bits.
- The chunk boundary is artificial. It starts after part of `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32` and ends before the `CP_RB0_CNTL` mask definitions, so adjacent chunks are required for complete per-register coverage.
- These macros are untyped constants. Wrong field/register pairing can silently corrupt VM context state, shader resource descriptors, compute dispatch behavior, CP queue setup, or performance-counter configuration.
- VM page-table and invalidation fields are security and isolation sensitive. Incorrect start/end/base values, PF/VF mappings, bypass masks, IOMMU enablement, or translation-fault defaults can expose memory, fault valid workloads, or mask real GPU faults.
- Many address fields are split low/high and use page-number alignment rather than raw byte addresses. Consumers must shift GPU addresses consistently and avoid truncating high bits.
- Repeated per-context and per-MARC-window registers make indexing errors easy. Off-by-one VMID/window strides can modify another process, VM context, or VF mapping.
- Performance-counter select/config fields can perturb profiling state or produce misleading diagnostics if programmed while counters are running or without clearing/latched-read sequencing.
- Shader and compute resource fields encode compiler/ABI contracts. Incorrect VGPR/SGPR counts, LDS size, user SGPR count, trap/exception/debug bits, wave limit, WGP mode, or CU enable masks can cause hangs, invalid execution, lost traps, or bad debug data.
- `COMPUTE_DISPATCH_INITIATOR` includes cache invalidation, restore, tunnel, wave32, AMP shader, and preemption-related controls. Blindly carrying assumptions from older GC families is risky because this GC 11.0.3 layout differs from earlier headers.
- CP ring-buffer control mixes sizing, trusted-memory-zone state, privilege, cache policy, execution, KMD queue, and read-pointer writeback enable fields. Whole-register writes can disable queues, break writeback, or change security attributes.
- Error/status registers such as `CP_GFX_ERROR` and counter readbacks may be sticky, live, or clear-on-read/write depending on the block; the generated masks do not document side effects.
- Reserved/full-width fields should not be fabricated into writes without hardware-guide reset values.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware smoke/stress coverage:

- Build AMDGPU paths that include `gc_11_0_3_sh_mask.h`, especially `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`.
- Generated-header consistency checks that each field has aligned shift/mask pairs, repeated per-context/per-engine/per-window layouts are regular, and registers in this chunk have matching `reg*` entries in `gc_11_0_3_offset.h`.
- GFXHUB tests that initialize GART and per-VMID page tables, validate base/start/end programming, issue VM invalidations, and confirm expected page-fault reporting under valid and invalid GPUVA accesses.
- SR-IOV and virtualization tests that exercise PF/VF MARC mappings, VMID bypass masks, translation-assist controls, and IOMMU/GPU-host translation enable paths without cross-VM leakage.
- Performance-counter tests that program GCVM L2, UTCL2, ATC L2, and L2 TLB counter select/config/mode registers, run known memory workloads, and verify low/high counter readback changes plausibly.
- Shader and compute dispatch smoke tests covering graphics pipeline creation, trap/debug modes, wave32/64 compute dispatch, scratch/user-data programming, threadgroup dimensions, restart/relaunch state, and thread trace enablement.
- CP queue tests that bring up the graphics ring, verify ring base/read-pointer/write-pointer behavior, exercise KMD and privilege/security settings where applicable, and confirm CP error bits stay clear under normal workloads.
- Suspend/resume, runtime power management, GPU reset, and recovery tests while VM contexts, counters, shader dispatch, and CP queues are active.
- Regression indicators include page faults on valid mappings, missing faults on invalid mappings, corrupted VMID context roots, stuck invalidation acknowledgements, zero or saturated perf counters, shader dispatch hangs, lost trap/debug behavior, CP ring timeouts, unexpected `CP_GFX_ERROR` bits, and failures isolated to GC 11.0.3-class hardware.

### subset-b-002533: lines 17259-19693

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 17259-19693

## Purpose

This chunk is generated AMD GC 11.0.3 register bitfield metadata. It contains no executable C code; it exports `#define` constants for hardware register field shifts and masks. AMDGPU, AMDKFD, MES, IMU, and GFXHUB code combine these constants with matching register offsets from `gc_11_0_3_offset.h` and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to program and decode command processor, shader processor input, and compute HQD state.

The range starts in the `gc_cpdec` command processor decode block, crosses into `gc_spipdec`, and ends inside the beginning of the `gc_cpphqddec` compute HQD decode block. It covers graphics and compute command rings, CP interrupt enables/status, ME/MEC interrupt families, debug and power/EDC controls, VMID/preemption/suspend/DDID state, graphics HQD state, DMA watch registers, SPI scheduling knobs, and the first compute HQD queue/MQD fields. Although this repository path is under `ceph-client`, this file is GPU driver hardware metadata, not filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or direct MMIO operations in this chunk. The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for the same field.
- Consumers pair these macros with `mm*` or `reg*` offset macros from `gc_11_0_3_offset.h`; the masks do not identify register addresses by themselves.

Major register groups in this chunk:

- CP ring control and pointers: `CP_RB{0,1}_CNTL`, `CP_RB_CNTL`, `CP_RB*_BASE`, `CP_RB*_BASE_HI`, `CP_RB*_WPTR`, `CP_RB*_WPTR_HI`, `CP_RB*_RPTR_ADDR`, `CP_RB*_RPTR_ADDR_HI`, `CP_RB_RPTR_WR`, and buffer-size mask registers. These fields describe ring size, block size, secure TMZ state/match, cache policy, kernel queue marking, read/write pointer addresses, and read-pointer writeback control.
- Doorbell and VMID routing: `CP_RB_VMID`, `CP_ME0_PIPE*_VMID`, `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_CLEAR`, and `CP_PQ_STATUS` define VMID ownership, doorbell offset ranges, doorbell enable/update/hit state, and host write-pointer notification behavior.
- Interrupt controls and status: top-level `CP_INT_CNTL`/`CP_INT_STATUS`, per-ring `CP_INT_CNTL_RING{0,1}`/`CP_INT_STATUS_RING{0,1}`, `CPC_INT_CNTL`/`CPC_INT_STATUS`, per-ME/per-pipe `CP_ME{1,2}_PIPE{0..3}_INT_CNTL` and matching status/debug registers, plus `CP_ME_F32_INTERRUPT`, `CP_PFP_F32_INTERRUPT`, `CP_MEC{1,2}_F32_INTERRUPT`, and `CP_MEC{1,2}_F32_INT_DIS`. Fields cover timestamp, opcode, privileged register/instruction, reserved-bit, ECC/EDC, GPF, dequeue, queue-message, IQ timer, wave-restore, and SUA violation signaling.
- CP debug, power, and fault state: `CP_FATAL_ERROR`, `CP_GFX_ERROR` context from the prior boundary, `CP_PWR_CNTL`, `CP_ECC_FIRSTOCCURRENCE*`, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `CP_DEBUG`, `CP_CPF_DEBUG`, `CP_CPC_DEBUG`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL`. These expose clock/power gating overrides, data-poisoning interrupt suppression, debug bus control, privilege-write inhibition, soft reset, and fatal/first-error indications.
- Scheduler, priority, and microcode entry points: ME/ring priority count and priority registers, `CP_PROCESS_QUANTUM`, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_MAX_DRAW_COUNT`, `CP_PFP/ME/MEC*_PRGRM_CNTR_START{,_HI}`, and `CP_PFP/ME/MEC*_INTR_ROUTINE_START{,_HI}`.
- Queue polling and wait timers: `CP_PQ_WPTR_POLL_CNTL`, `CP_PQ_WPTR_POLL_CNTL1`, and `CP_IQ_WAIT_TIME{1,2,3}` define polling periods, active/enable state, queue masks, and retry/wait buckets for IB offload, atomic offload, WRM offload, GWS, queue sleep, wave scheduling, semaphore rearm, dequeue retry, and suspend queue handling.
- VMID, preemption, suspend, and CWSR support: `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CPC_SUSPEND_CTX_SAVE_*`, `CPC_SUSPEND_CNTL_STACK_*`, `CPC_SUSPEND_WG_STATE_OFFSET`, `CPC_SUSPEND_CTX_SAVE_SIZE`, `CPC_OS_PIPES`, `CP_SUSPEND_RESUME_REQ`, and `CP_SUSPEND_CNTL`.
- DDID and HPD blocks: `CPC_DDID_*`, `CP_DDID_*`, `CP_GFX_DDID_*`, and `CP_GFX_HPD_*` provide base addresses, thresholds, size/policy/mode/enable fields, inflight/wptr/rptr/delta counters, high-priority dispatch status/control, and OSPRE fence address/data fields.
- Graphics HQD and MQD state: `CP_GFX_MQD_BASE_ADDR{,_HI}`, `CP_GFX_HQD_ACTIVE`, `CP_GFX_HQD_VMID`, `CP_GFX_HQD_QUEUE_PRIORITY`, `CP_GFX_HQD_QUANTUM`, `CP_GFX_HQD_BASE{,_HI}`, `CP_GFX_HQD_RPTR`, `CP_GFX_HQD_RPTR_ADDR{,_HI}`, `CP_RB_WPTR_POLL_ADDR_*`, `CP_GFX_HQD_CNTL`, `CP_GFX_HQD_DEQUEUE_REQUEST`, `CP_GFX_HQD_MAPPED`, `CP_GFX_HQD_QUE_MGR_CONTROL`, `CP_GFX_HQD_IQ_TIMER`, `CP_GFX_HQD_HQ_STATUS0`, `CP_GFX_HQD_HQ_CONTROL0`, `CP_GFX_MQD_CONTROL`, `CP_HQD_GFX_CONTROL`, and `CP_HQD_GFX_STATUS`.
- DMA watch and status: four `CP_DMA_WATCH{0..3}_ADDR_LO/HI/MASK/CNTL` register groups plus `CP_DMA_WATCH_STAT_ADDR_*` and `CP_DMA_WATCH_STAT` for tagged memory watchpoints, VMID/ATC filters, read/write flags, selected watchpoint ID, and counter/stat address reporting.
- UTCL1 and GCR controls/status: `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, `CPG_UTCL1_STATUS`, `CPC_UTCL1_STATUS`, `CPF_UTCL1_STATUS`, and `CPF_GCR_CNTL` expose CP-side translation/cache error and bypass/status fields.
- SPI decode registers: `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0`, `SPI_ARB_CYCLES_1`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, and `SPI_COMPUTE_WF_CTX_SAVE` define graphics/compute/exp pipeline arbitration, percentage weights, per-VMID debug/accumulation controls, compute queue reset, and wavefront context-save controls.
- Compute HQD decode registers: `CP_HPD_UTCL1_*`, `CP_MQD_BASE_ADDR{,_HI}`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PIPE_PRIORITY`, `CP_HQD_QUEUE_PRIORITY`, `CP_HQD_QUANTUM`, `CP_HQD_PQ_BASE{,_HI}`, `CP_HQD_PQ_RPTR`, `CP_HQD_PQ_RPTR_REPORT_ADDR{,_HI}`, `CP_HQD_PQ_WPTR_POLL_ADDR{,_HI}`, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_HQD_PQ_CONTROL`, `CP_HQD_IB_BASE_ADDR{,_HI}`, `CP_HQD_IB_RPTR`, `CP_HQD_IB_CONTROL`, and the beginning of `CP_HQD_IQ_TIMER`.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by code that includes the generated headers:

1. A GC 11.0.3 path includes `gc/gc_11_0_3_offset.h` and `gc/gc_11_0_3_sh_mask.h`.
2. The caller selects a register address through an `mm*` or `reg*` offset macro, often through `SOC15_REG_OFFSET` or an XCC-aware instance selector.
3. The caller composes or decodes a `u32` register value with `REG_SET_FIELD`, `REG_GET_FIELD`, direct shifts, or direct mask tests using these macros.
4. AMDGPU, AMDKFD, or MES register helpers perform the ordered MMIO writes/reads while the relevant queue, ring, interrupt, reset, or power-management path owns sequencing.

Observed consumers in this tree include GC 11.0.3-specific files such as `amdgpu/gfx_v11_0_3.c`, `amdgpu/imu_v11_0_3.c`, and `amdgpu/gfxhub_v3_0_3.c`. Closely related GC 11 paths show the intended patterns: `gfx_v11_0.c` uses `CP_INT_CNTL*` and `CP_ME*_PIPE*_INT_CNTL` fields to enable/disable CP interrupt sources, and composes `CP_HQD_PQ_CONTROL` before loading ring/HQD state. `mes_v11_0.c` builds MES queue descriptors with `CP_HQD_PQ_CONTROL` and then writes `regCP_HQD_PQ_CONTROL`. AMDKFD MQD managers use `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PQ_CONTROL`, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_HQD_IB_CONTROL`, and `CP_HQD_QUANTUM` to initialize compute queues and context-save/restore state.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names bit layouts for hardware state exposed by GC 11.0.3 registers.

The represented hardware state is broad:

- Ring state includes base addresses, high address words, read/write pointers, writeback addresses, queue size, block size, cache policy, execution enable/disable, privilege, TMZ security mode, and kernel-queue marking.
- Doorbell state includes per-ring and MEC doorbell ranges, per-HQD doorbell offsets, doorbell enable/mode/source/hit bits, and doorbell update status.
- Interrupt state includes masks/enables, pending status, debug assertion state, and fine-grained F32 interrupt source bits for PFP, ME, MEC1, MEC2, ring, and CPC paths.
- Queue and scheduler state includes VMIDs, queue priorities, pipe priorities, process/HQD quantum state, maximum context settings, queue manager control, dequeue requests, IQ timer state, and active/mapped status.
- Suspend/preemption/DDID state includes VMID reset/preempt requests and status, CPC context-save base/size/offset registers, suspend/resume control, DDID ring base/control/count pointers, and HPD fence/reporting fields.
- Error, debug, and maintenance state includes ECC first occurrence, fatal error, EDC configuration, UTCL1 error/status, DMA watchpoint configuration/status, soft reset, SD control, busy hysteresis, and RCIU CAM access.
- SPI scheduling state includes arbitration priorities/cycles, pipe percentage controls, per-VMID user accumulation/debug controls, compute queue reset, and compute wavefront context-save controls.

Persistence is hardware-defined. Some fields are configuration that lasts until reset, power-gating, suspend/resume, queue teardown, or explicit reprogramming. Other fields are live counters/status, sticky error indicators, write-one/self-clearing requests, active queue state, or hardware-owned pointers that change while the GPU is running. The masks themselves do not encode read-only versus writeable semantics, clearing rules, required ordering, or power-domain restrictions.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which supplies the register offsets matching these shift/mask definitions. The definitions also depend on the common AMDGPU register helper macros in the driver tree for field packing/unpacking and SOC15 instance addressing.

Integration points include:

- GC 11.0.3 ASIC support in `amdgpu/gfx_v11_0_3.c`, `amdgpu/imu_v11_0_3.c`, and `amdgpu/gfxhub_v3_0_3.c`.
- Generic GC 11 GFX and MES queue setup paths that program HQD/MQD, CP ring, interrupt, and doorbell registers.
- AMDKFD compute queue creation/update/load/destroy paths. MQD code writes fields such as `CP_HQD_PERSISTENT_STATE__PRELOAD_REQ`, `CP_HQD_PERSISTENT_STATE__QSWITCH_MODE`, `CP_HQD_PQ_CONTROL__QUEUE_SIZE`, `CP_HQD_PQ_CONTROL__NO_UPDATE_RPTR`, `CP_HQD_PQ_CONTROL__SLOT_BASED_WPTR`, `CP_HQD_PQ_CONTROL__QUEUE_FULL_EN`, `CP_HQD_PQ_DOORBELL_CONTROL__DOORBELL_OFFSET`, and `CP_HQD_IB_CONTROL__MIN_IB_AVAIL_SIZE`.
- Interrupt enable/disable and interrupt decode paths for timestamp, privileged access faults, opcode/reserved-bit errors, ECC/EDC, GPF, dequeue, and queue-message events.
- GPU reset, soft reset, VMID reset/preempt, suspend/resume, CWSR, and queue preemption flows.
- Debug/profiling and validation paths for DMA watchpoints, DDID counters, HPD fence reporting, CP debug buses, RCIU CAM reads, SPI arbitration, and compute queue reset.
- Security and virtualization boundaries through VMID fields, privilege bits, TMZ fields, doorbell offsets/ranges, and queue manager controls.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. Pairing `gc_11_0_3_sh_mask.h` with a different GC generation's offset header can compile while writing the wrong bits.
- The chunk boundary is artificial. It begins after the `CP_RB0_CNTL` shift fields and ends before the full `CP_HQD_IQ_TIMER` block is complete; adjacent chunks are needed for the full register-map narrative.
- The macros are untyped constants. Using a mask with the wrong register family, a stale field name, or a wrong generation can silently alter queue execution, interrupt routing, security policy, or reset behavior.
- Several registers mix enable bits, request bits, active/status bits, counters, and configuration. Whole-register writes can accidentally clear status, assert reset/dequeue/preempt requests, disable interrupts, change VMID ownership, or disturb reserved bits.
- Doorbell and pointer fields are alignment-sensitive. For example, read-pointer and write-pointer report/poll address fields start at bit 2 or 3, and doorbell offsets start at bit 2. Incorrect shifting can point hardware at the wrong memory or doorbell slot.
- Queue size fields are encoded sizes, not raw byte counts. AMDKFD/MES/GFX callers derive these from ring sizes; off-by-one or unit mistakes can cause queue wrap, underrun, stale read pointers, or hangs.
- TMZ, privilege, VMID, and KMD queue bits affect isolation. Incorrect programming can expose queues to the wrong address space, make user queues privileged, or break secure-memory matching.
- Interrupt enable/status families are similar but not identical across top-level CP, ring, CPC, and ME/MEC pipe registers. Reusing one register's masks for another can miss sources such as dequeue/SUA or enable unsupported bits.
- Live status such as HQD active, IQ timer active, processing IQ/IB, preempt/dequeue status, DDID inflight counts, and DMA watch stats can race with firmware, scheduler, reset, or user queue activity unless the caller owns the relevant queue selection and synchronization.
- Debug and power fields can override clock gating, soft reset CP subblocks, suppress interrupts, or change busy filtering. These are high-risk outside bring-up, recovery, or validated workarounds.
- Full-width masks such as `0xFFFFFFFFL` often describe pointer/counter/data fields, not necessarily safe write payloads.

## Test Signals

Useful validation signals for code using this chunk include:

- Build coverage for GC 11.0.3 include users, catching missing or mismatched `__SHIFT`/`_MASK` macro names.
- Queue bring-up tests that submit graphics, compute, and MES-managed work on GC 11.0.3 hardware and verify ring write/read pointer progress, doorbell hits, and absence of CP hangs.
- AMDKFD queue tests for AQL and PM4 queues, including queue size encoding, read-pointer reporting, write-pointer polling, doorbell offset programming, CWSR enablement, and queue priority behavior.
- Interrupt tests that enable timestamp, opcode/reserved-bit, privileged access, dequeue, ECC/EDC, GPF, and queue-message paths and confirm expected status bits and interrupt routing.
- Preemption, VMID reset, queue destroy, and suspend/resume tests that watch `CP_HQD_ACTIVE`, dequeue request status, IQ timer state, VMID preempt/status fields, and CWSR save-area programming.
- Security/isolation tests for VMID, TMZ, privilege, and KMD queue fields, especially mixed secure/non-secure queues and user versus kernel queue programming.
- GPU reset/recovery tests that exercise `CP_SOFT_RESET_CNTL`, CP debug/fatal/error state, and reinitialization of CP rings and HQDs after reset.
- DMA watchpoint and DDID/HPD diagnostics that confirm address alignment, VMID filtering, counters, and fence reports behave as decoded by the masks.
- Register trace comparison against known-good GC 11.0.3 hardware initialization tables for CP interrupt, SPI arbitration, HQD, MQD, and doorbell registers.

### subset-b-002534: lines 19694-22207

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 19694-22207

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask register-header segment. It contains preprocessor constants only. Each hardware register field is represented by a `__SHIFT` value and a corresponding `_MASK` value so AMDGPU code can pack and extract 32-bit MMIO, indexed-register, or command-stream register values without hard-coding bit positions.

The requested range contains 2,153 `#define` entries: 1,077 `__SHIFT` constants and 1,076 `_MASK` constants. The mismatch comes from chunk boundaries, not from a semantic register layout: the first line is the final `CP_HQD_IQ_TIMER__ACTIVE_MASK` from a register whose shift definitions are in the previous chunk, and the last line stops inside `PA_SC_VPORT_SCISSOR_9_TL` before its remaining masks.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics-core metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_11_0_3_sh_mask.h` supplies field bit layouts for GC 11.0.3 graphics hardware. Driver code pairs these macros with register offsets from `gc_11_0_3_offset.h` and uses helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` to build or decode register values.

This chunk covers several register families:

- CP HQD/MQD queue metadata for compute queues, including dequeue requests/status, IQ/EOP pointers, offload controls, semaphore messages, MQD control, EOP ring base/control, context-save layout, GDS resource state, AQL controls, PQ write pointer state, suspend-state offsets, DDID counters, and HQD error flags.
- TCP address-watch registers, with four `TCP_WATCHn` slots that split watched addresses into high/low pieces and expose mask, VMID, mode, and valid bits.
- GDS/GWS/OA state, including per-VMID GDS base/size partitions, per-VMID GWS and OA resource ownership, GWS reset masks for resources 0-63, targeted GWS/OA resets, maximum compute wave id, GDS memory-clean control, and context-switch counters/status for CS, GFX, PS, and GS clients.
- RAS signature registers for SX, DB, PA, SC, SPI, CB, and BCI blocks, plus signature control and mask fields.
- GUS arbitration, QoS, credits, counters, and error/status state for IO read/write paths, DRAM paths, SDP links, latency sampling, L1 channel/shader-array counters, FP atomic logging, and write-response FIFO thresholding.
- The beginning of the `gc_gfxdec0` graphics state block, including DB render/depth/stencil/HTILE state, PA screen/window/generic/viewport scissor rectangles, clip rectangles and edge rules, CB target/shader masks, coherency destination bases, and early viewport scissor entries.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or executable branches in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register value.
- Matching register addresses live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`.
- AMDGPU code usually consumes the macros through `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `WREG32*`, `RREG32*`, and command-packet/state-emission helpers.

Important field groups in this chunk include:

- `CP_HQD_DEQUEUE_REQUEST`, `CP_HQD_DEQUEUE_STATUS`, `CP_HQD_EOP_RPTR`, `CP_HQD_EOP_WPTR`, `CP_HQD_EOP_CONTROL`, and `CP_HQD_ERROR`: queue dequeue, suspend, EOP ring, fetcher, semaphore, and per-path error status fields.
- `CP_MQD_CONTROL`, `CP_HQD_CTX_SAVE_*`, `CP_HQD_CNTL_STACK_*`, `CP_HQD_WG_STATE_OFFSET`, and `CP_HQD_SUSPEND_*`: queue descriptor, context-save, control-stack, workgroup-state, and suspend-state layout fields.
- `TCP_WATCH0_*` through `TCP_WATCH3_*`: four address-watch slots with address, mask, VMID, mode, and valid fields. `amdgpu_amdkfd_gfx_v11.c` uses these names when programming address watches for KFD debugging.
- `GDS_VMID0_BASE/SIZE` through `GDS_VMID15_BASE/SIZE`, `GDS_GWS_VMID0` through `GDS_GWS_VMID15`, and `GDS_OA_VMID0` through `GDS_OA_VMID15`: per-VMID GDS, GWS, and ordered-append allocation metadata.
- `GDS_GWS_RESET0`, `GDS_GWS_RESET1`, `GDS_GWS_RESOURCE_RESET`, `GDS_OA_RESET_MASK`, and `GDS_OA_RESET`: resource and pipe reset controls.
- `GUS_IO_*`, `GUS_DRAM_*`, `GUS_SDP_*`, `GUS_MISC*`, `GUS_LATENCY_SAMPLING`, `GUS_ERR_STATUS`, and `GUS_L1_*`: memory-system arbitration/QoS, combining, fixed/aging/queuing/urgency coefficients, group bursts, SDP credit/reserve controls, error reporting, and per-channel/per-shader-array counters.
- `DB_RENDER_CONTROL`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_DEPTH_VIEW`, `DB_Z_INFO`, `DB_STENCIL_INFO`, and DB base/clear registers: depth/stencil/HTILE render-state and metadata fields.
- `PA_SC_*`, `PA_SU_HARDWARE_SCREEN_OFFSET`, `CB_TARGET_MASK`, `CB_SHADER_MASK`, and `COHER_DEST_BASE_*`: graphics setup, clipping/scissor, render target write mask, shader output mask, and coherency destination state.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU and KFD consumers:

1. Select GC 11.0.3 register definitions for the active ASIC.
2. Pair a register address from `gc_11_0_3_offset.h` with a field macro from this header.
3. Use `REG_SET_FIELD` or related helpers to compose a register value, or `REG_GET_FIELD` to decode saved hardware state.
4. Write/read the value through MMIO helpers, indexed register paths, RLC-safe accessors, or command-stream packets as part of queue setup, debug-watch programming, reset, context switch, render-state emission, or diagnostics.

For CP queue state, higher-level code chooses an MQD/HQD slot, writes descriptor and HQD registers, activates doorbell/pointer handling, and requests dequeue/suspend/resume through CP registers. For TCP watches, KFD debug code builds `TCP_WATCH0_CNTL` fields and writes the per-watch address registers using a stride between watch slots. For DB/PA/CB graphics state, command-stream producers or clear-state tables provide the sequencing; this file only names the bit layout.

The file does not encode ordering constraints, wait loops, cache flushes, W1C behavior, read-only/write-only semantics, or hardware side effects. Those semantics are owned by the surrounding AMDGPU code and the hardware programming guide.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- HQD/MQD queue state persists in CP queue registers and/or MQD save areas until overwritten, saved/restored, dequeued, suspended, reset, or lost across power/reset events.
- EOP, IQ, PQ, DDID, and context-save pointer fields represent ring/counter positions or memory offsets. Some are software-programmed, some are hardware-updated, and some are status or control bits around fetcher/dequeue activity.
- TCP watch registers are debug state scoped by watch slot and VMID. The address low field starts at bit 7, so callers must honor address alignment and mask shifting.
- GDS/GWS/OA registers describe partitioning and ownership for VMIDs and engine clients. Reset and clean registers have side effects; status/counter registers can change as queues and shader stages run.
- GUS QoS/arbitration registers tune memory fabric behavior, while error/status, latency sampling, credit, and L1 count registers are observational or diagnostic hardware state.
- DB/PA/CB graphics registers are context state for depth/stencil rendering, HTILE metadata, scissor/clip bounds, viewport state, and render-target write masks. They persist until replaced by later command packets, context restore, clear-state initialization, reset, or suspend/resume reprogramming.

Reserved or `UNUSED` fields appear throughout the range. Callers should preserve them on read-modify-write unless a documented full-register value is being emitted.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which supplies the matching register offsets. This shift/mask header must remain synchronized with that offset header and AMD's authoritative GC 11.0.3 register database.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`, which include the GC 11.0.3 offset and shift/mask headers for this ASIC generation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`, which programs HQD/MQD queue state and uses `TCP_WATCH0_CNTL` field macros for KFD address-watch setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/mes_v11_api_def.h` and `mes_v12_api_def.h`, which carry MES queue/context structures with fields corresponding to TCP watch controls and queue state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx11.h`, which contains default graphics clear-state values for DB render control and PA viewport scissor registers represented in this chunk.
- Common AMDGPU register helpers and SOC15 addressing macros, which perform the actual packing, unpacking, and MMIO/command-stream access.

Behaviorally, the chunk sits at the boundary between kernel queue management, KFD debugging, low-level GDS/GWS resource management, memory-fabric diagnostics/tuning, and graphics render-state programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask will compile cleanly but write or read the wrong hardware bits.
- The range starts and ends mid-register-family. File-level research must merge adjacent chunks before making complete claims about `CP_HQD_IQ_TIMER` or `PA_SC_VPORT_SCISSOR_9_TL`.
- HQD/MQD fields are queue-liveness sensitive. Incorrect dequeue, suspend, EOP, fetcher, PQ, or context-save masks can cause queue hangs, failed preemption, lost completions, bad user-mode queue restore, or invalid memory fetches.
- Address fields often have implicit alignment or unit semantics. Examples include `CP_HQD_CTX_SAVE_BASE_ADDR_LO__ADDR` starting at bit 12, `TCP_WATCHn_ADDR_L__ADDR` starting at bit 7, `DB_HTILE_DATA_BASE__BASE_256B`, and `COHER_DEST_BASE_*__DEST_BASE_256B`.
- TCP watch slot repetition is copy-sensitive. A single watch-slot layout or stride mismatch can break KFD watchpoints only for specific watch IDs.
- GDS/GWS/OA reset and ownership fields can affect inter-queue isolation. Bad VMID base/size, GWS resource, OA resource, or reset masks can leak resources between processes or cause CP GDS allocation errors.
- GUS arbitration/QoS fields can create subtle performance and fairness regressions rather than immediate failures. Bad priority, urgency, credit, or combine-flush definitions may only show under mixed graphics/compute/memory pressure.
- Error/status fields such as `CP_HQD_ERROR`, `GUS_ERR_STATUS`, and RAS signatures can be latched, clear-on-write, or otherwise access-sensitive. The generated masks do not distinguish those semantics.
- DB depth/stencil and HTILE fields interact with compression metadata, cache/coherency protocols, and render state. Wrong masks can present as depth corruption, incorrect fast clears, hangs during decompression/resummarize, or broken read-only depth/stencil views.
- Scissor, cliprect, viewport, and screen/window offset fields are repeated and coordinate-packed. Sign, range, and high-bit mistakes can cause clipped rendering or viewport-specific corruption.
- `CB_TARGET_MASK` and `CB_SHADER_MASK` are packed nibbles for eight targets/outputs. Mispacking can silently drop color channels or write unexpected MRT outputs.

## Test Signals

Useful validation should combine build coverage, generated-data checks, and runtime hardware tests:

- Build AMDGPU with GC 11 support and KFD enabled. Missing or renamed macros should surface in GC 11.0.3 include users, KFD queue/debug code, and common register-helper call sites.
- Mechanically compare this range against the authoritative GC 11.0.3 register database. Check that each complete register in the range has matching `__SHIFT` and `_MASK` entries and that repeated families are structurally consistent.
- Cross-check every register family in this chunk against `gc_11_0_3_offset.h` for matching `reg*` or `mm*` offset definitions.
- Run static mask sanity checks: masks should align with shifts, full-width fields should use `0xFFFFFFFFL`, repeated `GDS_VMIDn`, `GDS_GWS_VMIDn`, `GDS_OA_VMIDn`, `TCP_WATCHn`, `GUS_IO_RD/WR`, and `PA_SC_VPORT_SCISSOR_n` layouts should match expected repetition.
- Exercise KFD queue creation, restore, suspend/preemption, dequeue, and teardown paths. Watch for stuck HQDs, EOP pointer mismatches, failed dequeue status transitions, CP HQD error bits, and GPU reset recovery failures.
- Exercise KFD debugger address watches across all four watch IDs, different VMIDs, aligned and boundary addresses, and watch modes. Expected signals are correct traps and no cross-VMID/watch-slot aliasing.
- Run compute workloads that use GDS/GWS/OA resources and context switching, including multi-process VMID pressure. Watch for `CP_GDS_ALLOC_ERROR`, bad resource cleanup, or incorrect GDS memory-clean completion.
- Run mixed graphics/compute memory-pressure tests and inspect GUS/SDP/GUS_ERR_STATUS diagnostics. Performance regressions, fabric errors, credit stalls, or parity/FUE flags are relevant signals.
- Run depth/stencil, HTILE, depth bounds, fast-clear/decompress/resummarize, Z/stencil read-only, and MSAA depth tests to exercise DB fields in this chunk.
- Run viewport/scissor/cliprect/MRT color-mask rendering tests across multiple viewports and render targets. Expected signals include correct per-target channel masks, correct shader output masking, and no off-by-one or window-offset clipping errors.
- Compare graphics clear-state register dumps against `clearstate_gfx11.h` expectations for DB render control and PA viewport scissor defaults after init/reset.

## Cross-Chunk Notes

The previous chunk owns most of `CP_HQD_IQ_TIMER`; this chunk begins with only `CP_HQD_IQ_TIMER__ACTIVE_MASK`. This chunk then covers complete CP HQD/MQD, TCP watch, GDS/GUS/RAS, and early gfx DB/PA/CB groups until it stops inside `PA_SC_VPORT_SCISSOR_9_TL`. The next chunk should complete that viewport scissor register and continue the remaining viewport/scissor and graphics state metadata. The final per-file research document should reconcile these artificial boundaries before describing the full GC 11.0.3 shift/mask header.

### subset-b-002535: lines 22208-24656

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 22208-24656

## Scope

This chunk covers generated shift and mask macros from the GC 11.0.3 AMD GPU register mask header. The range starts in the viewport-scissor family after earlier `PA_SC_VPORT_SCISSOR_9_TL` definitions, covers a broad group of graphics context-state registers, and ends at the `PA_CL_NGG_CNTL` register comment before its field definitions appear in a later chunk.

The chunk is entirely preprocessor metadata. It defines no C functions, structs, enums, runtime storage, or executable control flow. Its behavior is the field-layout contract used by AMDGPU code and command-stream state programming to compose and decode 32-bit hardware register values for the GC 11.0.3 graphics pipeline.

Major register families in this range are:

- Primitive assembler/scissor/clip viewport state: `PA_SC_VPORT_SCISSOR_9_*` through `PA_SC_VPORT_SCISSOR_15_*`, `PA_SC_VPORT_ZMIN/ZMAX_0..15`, `PA_CL_VPORT_*_0..15`, user clip planes, programmed near clip, `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, and `PA_CL_NANINF_CNTL`.
- Raster and shader-engine routing state: `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, `PA_SC_TILE_STEERING_OVERRIDE`, variable-rate shading register fields, and CP context identity registers (`CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, `CP_VMID`).
- Color/depth/blend state: `CB_RMI_GL2_CACHE_CONTROL`, constant blend color registers, `CB_FDCC_CONTROL`, `CB_COVERAGE_OUT_CONTROL`, `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, `DB_STENCILREFMASK_BF`, `DB_DEPTH_CONTROL`, `DB_EQAA`, `CB_COLOR_CONTROL`, and `DB_SHADER_CONTROL`.
- Pixel-shader input and export state: `SPI_PS_INPUT_CNTL_0..31`, `SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, `SPI_BARYC_CNTL`, temporary scratch-ring/base registers, and shader export format registers.
- Shader export/blend optimizer state: `SX_PS_DOWNCONVERT_CONTROL`, `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, `SX_MRT0_BLEND_OPT..SX_MRT7_BLEND_OPT`, and `CB_BLEND0_CONTROL..CB_BLEND7_CONTROL`.
- Draw and primitive setup state: `GFX_COPY_STATE`, `VGT_DMA_BASE*`, `VGT_DRAW_INITIATOR`, `VGT_EVENT_ADDRESS_REG`, `GE_MAX_OUTPUT_PER_SUBGROUP`, `PA_SU_SC_MODE_CNTL`, line stipple controls, and small/expanded primitive filtering controls.

## Purpose

`gc_11_0_3_sh_mask.h` supplies bit offsets and masks for GC 11.0.3 registers. Each field is expressed as:

- `<REGISTER>__<FIELD>__SHIFT`: the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`: the bit mask covering the field in the 32-bit register value.

Consumers combine these constants with helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 register access helpers, packet-building code, or precomputed context-state tables. Sibling generated headers provide the complementary register addresses and reset/default values, especially `gc_11_0_3_offset.h` and any matching default header for the same ASIC generation.

The purpose of this chunk is to expose the GC 11.0.3 graphics state ABI for viewport transform, clipping, rasterization, pixel-shader interpolation, color/depth export, blending, and primitive filtering. It is the low-level map that lets higher-level driver code and firmware-facing state tables write fields without embedding numeric bit positions at each use site.

## Important Macro Families

### Viewport, Scissor, and Clip Space

The opening section completes viewport scissor definitions for viewports 9 through 15:

- `PA_SC_VPORT_SCISSOR_N_TL` fields define top-left X/Y and `WINDOW_OFFSET_DISABLE`.
- `PA_SC_VPORT_SCISSOR_N_BR` fields define bottom-right X/Y.

The same range defines depth bounds for all 16 viewports via `PA_SC_VPORT_ZMIN_0..15` and `PA_SC_VPORT_ZMAX_0..15`; each uses a full 32-bit payload field because the encoded value is the register's complete data word.

The clip/viewport transform section later defines `PA_CL_VPORT_XSCALE`, `XOFFSET`, `YSCALE`, `YOFFSET`, `ZSCALE`, and `ZOFFSET` for viewports 0 through 15, again as full-register fields. These are paired with `PA_CL_VTE_CNTL`, whose enable bits select whether the viewport transform applies X/Y/Z scale and offset and which vertex XY/Z/W formats are expected.

User clip planes are represented as `PA_CL_UCP_0_X/Y/Z/W` through `PA_CL_UCP_5_X/Y/Z/W`; all are full-register data fields. `PA_CL_PROG_NEAR_CLIP_Z` supplies the full-register programmed near-clip value. `PA_CL_CLIP_CNTL` then controls which user clip planes are enabled, whether they cull only, DirectX clip-space behavior, clip error detection, rasterization kill, linear attribute clipping, near/far Z clip disable, and programmed near-Z enablement.

`PA_CL_VS_OUT_CNTL` describes which vertex-shader side outputs are consumed by downstream graphics stages: clip/cull distance enables, point size, edge flag, render target index, viewport index, kill flag, line width, VRS rate, FSR select, and rate-combiner bypass controls.

`PA_CL_NANINF_CNTL` is a precision/robustness policy register for NaN and infinity handling through viewport transform and VS output paths. It includes discard/retain/convert behavior for XY/Z/W and clip-distance infinity, plus output negative-zero handling.

### Raster, Tiling, VRS, and Context Identity

`PA_SC_RASTER_CONFIG` and `PA_SC_RASTER_CONFIG_1` encode raster backend, packer, scan converter, shader engine, and shader-engine-pair mapping fields. These fields are topology-sensitive and are normally paired with ASIC-specific discovery or golden-setting values.

`PA_SC_SCREEN_EXTENT_CONTROL` controls even/odd slice enables. `PA_SC_TILE_STEERING_OVERRIDE` exposes a manual override for tile steering, including scan-converter count, render-backend count per scan converter, and packer count per scan converter.

The VRS group includes:

- `PA_SC_VRS_OVERRIDE_CNTL`: override rate-combiner mode, VRS rate, VRS surface enable, rate-hint writeback, and feedback override.
- `PA_SC_VRS_RATE_FEEDBACK_BASE`, `_BASE_EXT`, and `_SIZE_XY`: feedback surface address and dimensions.
- `PA_SC_VRS_RATE_CACHE_CNTL`: cache update/flush and flush-done bits.
- `PA_SC_VRS_RATE_BASE`, `_BASE_EXT`, and `_SIZE_XY`: VRS rate image address and dimensions.

`CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, and `CP_VMID` provide small command-processor context fields for perfmon enablement and context identity. `CONTEXT_RESERVED_REG0/1` are full-register data placeholders for reserved context state.

### Color Buffer, Depth Buffer, and Blend Constants

`CB_RMI_GL2_CACHE_CONTROL` defines write/read policies for DCC and color data, L3 bypass bits, and color big-page behavior. These fields affect color-buffer traffic between CB/RMI and GL2 and are performance/coherency sensitive.

`CB_BLEND_RED`, `CB_BLEND_GREEN`, `CB_BLEND_BLUE`, and `CB_BLEND_ALPHA` are full-register constant blend-color components. `CB_FDCC_CONTROL` exposes FDCC/sample-mask tracker and constant-encode/eliminate-FC skip controls. `CB_COVERAGE_OUT_CONTROL` controls coverage output enablement, target MRT/channel selection, and sample count.

The depth/stencil section includes:

- `DB_STENCIL_CONTROL`: front/back stencil fail, zpass, and zfail operation fields.
- `DB_STENCILREFMASK` and `DB_STENCILREFMASK_BF`: front and back-face stencil test value, mask, write mask, and operation value.
- `DB_DEPTH_CONTROL`: stencil enable, depth enable/write enable, depth function, backface enable, stencil read/write controls, z pass/fail controls, and color-write behavior on depth pass/fail.
- `DB_EQAA`: anchor/iteration/mask sample counts, high-quality intersections, incoherent reads, interpolation mode, static anchor associations, alpha-to-mask EQAA disable, overrasterization amount, and post-Z overrasterization.
- `DB_SHADER_CONTROL`: shader depth/stencil export controls, Z order, kill/mask export, depth-before-shader, conservative Z export, primitive ordered pixel shader, pre-shader depth coverage, OREO blend, and intrinsic-rate override fields.
- `CB_COLOR_CONTROL`: dual-quad controls, one-fragment PS invoke, degamma enable, color mode, and ROP3 function.

These macros are central to render-target, depth/stencil, MSAA/EQAA, alpha-to-coverage, and pixel-shader depth-export programming.

### SPI Pixel Shader Inputs and Interpolation

The chunk defines `SPI_PS_INPUT_CNTL_0..31`. Each input-control register has a repeated layout for pixel-shader interpolants:

- `OFFSET` selects the parameter offset.
- `DEFAULT_VAL` and optional `USE_DEFAULT_ATTR1`/`DEFAULT_VAL_ATTR1` select default attribute behavior.
- `FLAT_SHADE`, `ROTATE_PC_PTR`, `PRIM_ATTR`, `PT_SPRITE_TEX`, and `PT_SPRITE_TEX_ATTR1` control interpolation and point-sprite handling.
- `DUP`, `FP16_INTERP_MODE`, `ATTR0_VALID`, and `ATTR1_VALID` control duplicated/half-precision and valid-lane behavior.

Entries 20 through 31 have the same general SPI input-control purpose but fewer point-sprite fields in this generated layout than earlier entries, so consumers must not assume every repeated register has every field by name.

Other SPI registers include:

- `SPI_VS_OUT_CONFIG`: VS export count and primitive-export count.
- `SPI_PS_INPUT_ENA` and `SPI_PS_INPUT_ADDR`: 32-bit enable/address bitmaps for PS inputs.
- `SPI_INTERP_CONTROL_0`: point-sprite override and parameter-shade control.
- `SPI_PS_IN_CONTROL`: number of interpolants, parameter generation, offchip parameter enable, late PC deallocation, primitive interpolants, barycentric optimization disable, and wave32 enable.
- `SPI_BARYC_CNTL`: perspective/linear center and centroid behavior, position float location/ULC, and front-face bit behavior.
- `SPI_TMPRING_SIZE`, `SPI_GFX_SCRATCH_BASE_LO/HI`: scratch/temporary ring sizing and base address fields.
- `SPI_SHADER_IDX_FORMAT`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT`: index, position, depth, and up to eight color export format fields.

### SX and CB Blend State

The SX export/blend group controls downconversion and blend optimization:

- `SX_PS_DOWNCONVERT_CONTROL` has per-MRT format-mapping disable bits.
- `SX_PS_DOWNCONVERT` has per-MRT downconvert format fields.
- `SX_BLEND_OPT_EPSILON` has per-MRT epsilon fields.
- `SX_BLEND_OPT_CONTROL` has per-MRT color/alpha optimization disable bits plus `PIXEN_ZERO_OPT_DISABLE`.
- `SX_MRT0_BLEND_OPT..SX_MRT7_BLEND_OPT` define color source/destination optimization, color combine function, alpha source/destination optimization, and alpha combine function for each MRT.

`CB_BLEND0_CONTROL..CB_BLEND7_CONTROL` define the actual per-MRT blend equation and enablement: color source blend, color combine function, color destination blend, alpha source blend, alpha combine function, alpha destination blend, separate-alpha enable, blend enable, and ROP3 disable.

### Draw, Primitive Setup, and Filtering

`GFX_COPY_STATE` provides per-stage copy-state fields for vertex, hull, tessellation, geometry, pixel, compute, and mesh-like state paths. `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DRAW_INITIATOR`, and `VGT_EVENT_ADDRESS_REG` expose draw-initiation and event-address payload fields. `GE_MAX_OUTPUT_PER_SUBGROUP` controls geometry-engine output limits per subgroup.

`PA_SU_SC_MODE_CNTL` provides culling, face orientation, polygon mode, front/back polygon primitive type, polygon offset enablement, vertex window offset, provoking vertex selection, perspective correction disable, multi-primitive index-buffer enablement, right-triangle gradient reference, quad decomposition mode, and keep-together enablement.

Line and primitive filter controls include:

- `PA_SU_LINE_STIPPLE_CNTL` and `PA_SU_LINE_STIPPLE_SCALE`: line stipple reset, full-length expansion, fractional accumulation, and scale.
- `PA_SU_PRIM_FILTER_CNTL`: primitive-type filter disable bits, expansion enables, expansion constant, and right/bottom exclusion bits.
- `PA_SU_SMALL_PRIM_FILTER_CNTL`: small-primitive filter enablement, primitive-type disables, and 1x MSAA compatibility disable.

The range ends with the `PA_CL_NGG_CNTL` comment only; its field masks are outside this chunk.

## Control Flow and State Behavior

There is no local control flow in this header chunk. The macros are compile-time constants. Runtime behavior arises when driver code, command-stream construction, firmware tables, or clear-state packets write the corresponding MMIO/context registers.

The persistent state is hardware context state rather than C memory. Important hardware-visible state affected through these fields includes viewport transforms and depth ranges, scissor bounds, clip-plane coefficients, shader output/input routing, pixel-shader interpolation controls, blend constants, per-MRT blend equations, depth/stencil and EQAA state, VRS image/feedback base and dimensions, raster topology mapping, primitive filtering, line stipple state, and draw-initiation fields.

Several fields are not plain persistent configuration even though they are represented as masks:

- `PA_SC_VRS_RATE_CACHE_CNTL` includes cache update/flush request and flush-done status semantics.
- `VGT_DRAW_INITIATOR` and event-address registers participate in draw/event sequencing.
- `CP_PIPEID`, `CP_RINGID`, and `CP_VMID` describe command/context identity rather than render-state math.
- Many full-register data fields represent IEEE-like floating-point payloads or addresses, so their masks are `0xFFFFFFFFL` but their meaning is not an arbitrary integer.

Correct programming order is external to this file and belongs to the owning graphics-state setup paths, userspace command-stream ABI, firmware initialization tables, and hardware documentation.

## Dependencies and Integration Points

This chunk depends on the AMD generated-register-header convention:

- `gc_11_0_3_offset.h` provides register offsets/base indices for the same register names.
- Matching default/reset headers or clear-state tables provide initial values.
- AMDGPU helper macros consume the `__SHIFT` and `_MASK` constants to pack and unpack fields.

Direct includes of this exact GC 11.0.3 mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`

Observed source-tree integration signals include `amdgpu/clearstate_gfx11.h`, which contains clear-state values for many registers covered here: viewport scissors and Z ranges, VRS registers, blend constants, stencil state, SPI pixel-shader input controls, blend controls, `PA_SU_SC_MODE_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, and related graphics context registers. This header chunk supplies the field-level metadata for the same hardware state families.

The fields are also part of the broader AMDGPU/KMD interface to userspace graphics drivers. Userspace command buffers may program many of these context registers through packetized state, while kernel-side clear-state and initialization paths ensure known reset values for protected or preloaded state.

## Risks

- Bitfield mistakes have high blast radius. A wrong shift or mask can corrupt adjacent register fields and cause rendering corruption, depth/stencil errors, blend errors, shader input mismatches, hangs, or GPU resets.
- Repeated register families invite copy/paste errors. `PA_CL_VPORT_*_0..15`, `SPI_PS_INPUT_CNTL_0..31`, `SX_MRT*_BLEND_OPT`, and `CB_BLEND*_CONTROL` are mostly regular but not perfectly interchangeable.
- Cross-generation similarity is risky. GC 11.0.0, GC 11.0.3, and later GC 12 headers share many names but can differ in fields or masks. Consumers must pair this file with GC 11.0.3 offsets/defaults and not mix generated generations.
- Full-register masks can hide type-sensitive payloads. Viewport floats, blend constants, clip-plane coefficients, scratch addresses, and VRS surface addresses all use broad masks but require correct value encoding and alignment.
- Topology and cache fields are hardware-configuration sensitive. Raster mapping, tile steering, CB cache policy, and VRS cache controls can affect coherency, performance, or feature correctness if applied without ASIC-specific constraints.
- Some fields have action/status semantics. Treating flush/update/draw/event fields as ordinary retained state can break synchronization or lose status information.

## Test and Validation Signals

Useful validation for this chunk is mostly compile-time and graphics-integration coverage:

- Build AMDGPU with GC 11.0.3 support so direct include users (`gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, `imu_v11_0_3.c`) continue to compile against the macro names.
- Validate clear-state generation and restore paths against `amdgpu/clearstate_gfx11.h`, especially viewport/scissor/Z defaults, SPI input defaults, blend controls, depth/stencil controls, and primitive setup defaults.
- Run graphics workloads that exercise multiple viewports, scissor rectangles, user clip planes, point sprites, flat/perspective interpolation, wave32 PS inputs, MSAA/EQAA, alpha-to-coverage, color/depth writes, and per-MRT blending.
- Exercise VRS paths that program rate images and feedback surfaces, then verify `PA_SC_VRS_RATE_CACHE_CNTL` update/flush behavior through rendered output and any available debug/status hooks.
- Run suspend/resume, GPU reset, and context-switch tests to ensure persistent graphics context state derived from these fields is reinitialized or restored correctly.
- Use render tests with NaN/Inf vertex values and clipping edge cases to validate `PA_CL_NANINF_CNTL`, `PA_CL_CLIP_CNTL`, `PA_CL_VTE_CNTL`, and `PA_CL_VS_OUT_CNTL` behavior.

## Unresolved Cross-Chunk References

This range begins after the definition of `PA_SC_VPORT_SCISSOR_9_TL` has already started in an earlier chunk, so the top-left X shift and related fields for viewport 9 are described there. It ends immediately after the `PA_CL_NGG_CNTL` register comment, leaving that register's actual field layout for the following chunk. The final per-file reconciliation should connect this chunk with neighboring chunks to describe the complete generated GC 11.0.3 register-mask header and its include guards.

### subset-b-002536: lines 24657-27046

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 24657-27046

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask header slice. It contains only C preprocessor constants for hardware register bit positions and masks. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, or executable branches in this range.

The requested lines contain 2,177 `#define` statements: 1,089 `__SHIFT` macros and 1,088 `_MASK` macros. The chunk starts inside the `PA_CL_NGG_CNTL` register group, immediately after the `//PA_CL_NGG_CNTL` comment in the previous line, and ends inside the `SQ_DEBUG` group before `SQ_DEBUG__WAIT_DEP_CTR_ZERO_MASK` on the following line.

Although the path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM graphics-core register metadata and is not Ceph filesystem logic.

## Purpose

`gc_11_0_3_sh_mask.h` describes the bit layout of AMD graphics core 11.0.3 registers. Driver code combines these field definitions with register offsets from the matching offset header and helper macros to construct, update, and decode 32-bit register values without open-coded bit numbers.

This slice covers graphics pipeline state across primitive assembly, rasterization, depth/stencil, color-buffer render targets, PF/VF command controls, GRBM queue selection, PA/SC tuning, and early SQ memory/debug state. It is primarily used by graphics setup, clear-state programming, context state packets, virtualization/control paths, KFD memory configuration, and debug or hang-diagnosis code.

The main register surfaces are:

- PA/SC/VGT frontend and rasterization controls for NGG vertex reuse, over-rasterization, stereo rendering, variable-rate shading, point and line state, tessellation distribution, shader-stage enablement, primitive IDs, event initiation, streamout opaque draw state, polygon offset, centroid/sample locations, conservative rasterization, and NGG/binning behavior.
- DB depth/stencil-related controls for HTILE surface metadata, sample-result compare state, preload windows, and alpha-to-mask behavior.
- CB color target state for render targets 0 through 7, including base addresses, views, format/type/component-swap fields, fragment/sample/compression attributes, DCC/FDCC metadata bases, extended address bits, mip dimensions, swizzle mode, resource type, and pipe-alignment flags.
- PF/VF command and GRBM controls for reserved config data, MEC/ME reset/halt/step/cache-invalidate bits, and GRBM selection of pipe, ME, VMID, queue, and context.
- PA/SC and PA/PH maintenance registers for VRS surface control, out-of-order/packer/binning enhancement knobs, FIFO sizing, wave ID controls, ATM/PKR controls, binner event routing, binner performance thresholds, trap-screen write locks, and PA/PH interface clock/performance controls.
- SQ/SPI-adjacent state for runtime configuration, SQ global busy/wave/fifo status, shader memory bases/configuration, and the beginning of SQ single-step/debug controls.

## Important APIs, Types, And Macros

The only API surface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- `//<REGISTER>` comments mark register boundaries.
- `// addressBlock: gc_pfvf_cpdec`, `gc_pfvf_grbmdec`, `gc_pfvf_padec`, and `gc_pfvf_sqdec` mark generated address-block transitions.

There are no callable functions or C types. Runtime consumers normally use these definitions through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and packet-building paths that token-paste register and field names.

Important PA/SC/VGT/DB families include:

- `PA_CL_NGG_CNTL`, `GE_NGG_SUBGRP_CNTL`, `PA_SC_NGG_MODE_CNTL`, and `VGT_SHADER_STAGES_EN`, which define NGG/primitive-generator enablement, wave32 flags for shader stages, primitive pass-through controls, sub-group sizing, and vertex reuse behavior.
- `PA_SU_OVER_RASTERIZATION_CNTL`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, and `PA_SC_SHADER_CONTROL`, which shape zero-area primitive discard, conservative rasterization, out-of-order modes, scissor interaction, kill/stencil/depth behavior, and pixel-shader routing.
- `PA_STEREO_CNTL`, `PA_STATE_STEREO_X`, and `VGT_DRAW_PAYLOAD_CNTL`, which expose stereo, render-target slice, viewport ID, FSR, primitive payload, draw viewport, VRS-rate, and register RT-index payload fields.
- `PA_CL_VRS_CNTL`, `PA_SC_VRS_SURFACE_CNTL`, and `PA_SC_VRS_SURFACE_CNTL_1`, which describe rate combiner modes, exposed VRS pixels, cmask rate hints, VRS feedback/cache behavior, forced fine-rate controls, SSAA normalization overrides, and VRS spare bits.
- `PA_SU_POINT_SIZE`, `PA_SU_POINT_MINMAX`, `PA_SU_LINE_CNTL`, `PA_SC_LINE_CNTL`, `PA_SC_LINE_STIPPLE`, and `PA_SU_VTX_CNTL`, which cover point/line sizing, stipple, vertex quantization, pixel-center mode, and provoking-vertex details.
- `VGT_TESS_DISTRIBUTION`, `VGT_LS_HS_CONFIG`, and `VGT_TF_PARAM`, which describe tessellation accumulation, patch/input/output control point counts, topology, partitioning, distribution mode, memory type, and related request policy fields.
- `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, `VGT_DMA_NUM_INSTANCES`, `VGT_PRIMITIVEID_EN`, `VGT_PRIMITIVEID_RESET`, `VGT_EVENT_INITIATOR`, `VGT_ESGS_RING_ITEMSIZE`, `VGT_GS_INSTANCE_CNT`, `VGT_GS_MAX_VERT_OUT`, and streamout opaque draw registers, which define draw/index/event/primitive-ID state.
- `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, `DB_ALPHA_TO_MASK`, and `PA_SU_POLY_OFFSET_*`, which represent depth-buffer metadata, compare-state windows, preload rectangles, alpha-to-mask offsets, and polygon depth bias settings.

Important color-buffer families include:

- `CB_COLOR0_BASE` through `CB_COLOR7_BASE` and `CB_COLOR0_DCC_BASE` through `CB_COLOR7_DCC_BASE`, full-width 256-byte-aligned base-address low fields for color surfaces and DCC metadata.
- `CB_COLOR0_VIEW` through `CB_COLOR7_VIEW`, which split slice start, slice max, and mip level.
- `CB_COLOR0_INFO` through `CB_COLOR7_INFO`, which define render target format, number type, component swap, blend clamp/bypass, simple float, round mode, and blend optimizations.
- `CB_COLOR0_ATTRIB` through `CB_COLOR7_ATTRIB`, `CB_COLOR*_FDCC_CONTROL`, `CB_COLOR*_ATTRIB2`, and `CB_COLOR*_ATTRIB3`, which cover fragment counts, FMASK/no-alloc optimizations, compression block sizes, color transform, constant encode controls, FDCC/DCC enable and disable controls, mip0 dimensions, max mip, metadata linearity, swizzle mode, resource type, and pipe alignment.
- `CB_COLOR*_BASE_EXT` and `CB_COLOR*_DCC_BASE_EXT`, which provide the high address bits for base and DCC base programming.

Important control/debug families include:

- `CONFIG_RESERVED_REG0/1`, full-width PF/VF config data placeholders.
- `CP_MEC_CNTL` and `CP_ME_CNTL`, which expose pipe reset, pipe disable, instruction cache invalidate, halt, and step controls for MEC, CE, PFP, and ME engines.
- `GRBM_GFX_CNTL` and `GRBM_NOWHERE`, which provide graphics-register routing fields for pipe, ME, VMID, queue, context, and a discard-style data register.
- `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_ENHANCE_2`, `PA_SC_ENHANCE_3`, `PA_SC_BINNER_CNTL_*`, `PA_SC_BINNER_EVENT_CNTL_0..3`, and `PA_SC_BINNER_PERF_CNTL_*`, which expose a large set of rasterizer/binning overrides, event-to-binner hooks, thread trace markers, pipeline done controls, statistics dumps/resets, and histogram thresholds.
- `PA_SC_P3D_TRAP_SCREEN_HV_LOCK`, `PA_SC_HP3D_TRAP_SCREEN_HV_LOCK`, and `PA_SC_TRAP_SCREEN_HV_LOCK`, each providing a non-privileged write-lock bit for trap-screen registers.
- `PA_PH_INTERFACE_FIFO_SIZE` and `PA_PH_ENHANCE`, which configure PA/PH interface FIFO sizing, clock-gating disables, perf-counter sampling behavior, and PH/SPI/GE throttling.
- `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, and the partial `SQ_DEBUG` group, which describe SQ runtime presence, busy/interrupt busy state, per-shader-array wave levels, register FIFO levels, private/shared memory bases, addressing/alignment/prefetch/cache policy, and debug single-step control fields.

## Control Flow

This header has no runtime control flow. It affects runtime behavior only when C code expands these macros while composing or decoding register values.

The implied driver flow is:

1. Driver code selects a GC 11.0.3 register offset from `gc_11_0_3_offset.h`.
2. It reads, writes, or read-modify-writes the register through AMDGPU SOC15/MMIO helpers or emits the register value into a command stream/state packet.
3. It uses the `__SHIFT` and `_MASK` pair, often through `REG_SET_FIELD` or `REG_GET_FIELD`, to isolate or set the desired field.
4. The hardware PA/SC/VGT/DB/CB/CP/GRBM/SQ blocks perform the actual graphics, command, memory, or debug behavior.

For graphics state, higher-level code programs shader-stage enablement, primitive assembly, tessellation, rasterizer, depth/stencil, sample-location, binner, VRS, and color-target registers in a hardware-defined order. This chunk describes the fields but does not enforce register sequencing, cache flushes, compression transitions, render-target layout rules, or event ordering.

For command/control state, CP and GRBM code can use these fields to halt or step engines, reset pipes, invalidate micro-engine instruction caches, and select a queue/context register aperture. The macros do not encode which bits are write-one, self-clearing, privileged, PF/VF-only, or safe to touch while queues are active.

For SQ state, KFD/AMDGPU paths can program `SH_MEM_CONFIG` and `SH_MEM_BASES` for process memory behavior and read `SQ_DEBUG_STS_GLOBAL*` for hang/debug status. This chunk only names the fields; memory-model, VMID/PASID, trap, and wavefront semantics live in hardware and the surrounding driver.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists only in GPU registers, command-stream state, context state images, firmware-owned queues, render-target memory, metadata surfaces, and debug/status latches.

Graphics state described in this chunk persists until overwritten by a later command stream, clear-state restore, context switch, queue teardown, GPU reset, suspend/resume, power-gating loss, or firmware/hardware context save/restore. That includes shader-stage enablement, tessellation parameters, primitive ID state, event initiators, rasterizer controls, VRS controls, sample locations, polygon offset, binner configuration, and render-target state.

Color-buffer state is especially persistent because it describes memory addresses and layout metadata for active render targets. `CB_COLOR*_BASE`, `CB_COLOR*_BASE_EXT`, `CB_COLOR*_DCC_BASE`, `CB_COLOR*_DCC_BASE_EXT`, `CB_COLOR*_INFO`, and `CB_COLOR*_ATTRIB*` must match the actual backing BO, swizzle mode, format, mip/slice view, compression mode, and synchronization state. Misaligned or stale values can persist across draws until the pipeline state is explicitly changed.

Control/debug state has mixed semantics. CP halt/step/reset/cache-invalidate bits may be command-like or self-clearing, GRBM selection fields route subsequent register accesses, trap-screen lock bits enforce privilege boundaries, and SQ status bits reflect live hardware activity. The generated header does not classify access side effects, so consumers must rely on hardware docs and established driver sequences.

Reserved, spare, and ECO fields occur throughout this range. Consumers should preserve these bits in read-modify-write sequences unless generation-specific documentation or existing driver code explicitly says to write a known value.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_default.h` supplies generated reset/default values where present.
- AMDGPU register helper macros and SOC15 MMIO helpers perform actual field packing, reads, writes, and read-modify-writes.
- Direct include users in this tree include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx11.h` contains clear-state entries for many registers named in this chunk, including `VGT_SHADER_STAGES_EN`, `PA_SC_BINNER_CNTL_*`, and the repeated `CB_COLOR*` render-target groups.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c` programs `SH_MEM_CONFIG`, integrating the SQ memory configuration fields with KFD process/queue behavior.

Runtime integration points include graphics pipeline state emission, clear-state initialization, render-target and DCC programming, VRS and sample-position setup, depth/stencil state, binner and out-of-order rasterization tuning, command processor reset/debug, GRBM register routing, KFD memory configuration, hang diagnosis, and register-dump decoding.

## Risks And Edge Cases

- Generated-header drift is the main risk. An incorrect shift or mask can compile cleanly while setting the wrong hardware bit.
- This work item starts inside `PA_CL_NGG_CNTL` and ends inside `SQ_DEBUG`. The previous chunk owns the register comment for the first group, and the next line after this chunk completes the `SQ_DEBUG__WAIT_DEP_CTR_ZERO` mask.
- Many register families are repeated for render targets 0 through 7. Mechanical similarity makes copy/paste or generated-data errors hard to spot, especially for `CB_COLOR*_INFO`, `CB_COLOR*_FDCC_CONTROL`, `CB_COLOR*_ATTRIB2`, and `CB_COLOR*_ATTRIB3`.
- Color target address and metadata fields are layout-sensitive. Wrong base, high address, DCC base, swizzle, resource type, mip dimensions, or compression bits can corrupt render targets, break resolves, or cause GPU faults.
- Compression and FDCC/DCC controls interact with cache flushing, metadata transitions, and render backend behavior. The masks alone do not describe required synchronization.
- VRS, conservative rasterization, sample-location, centroid, and alpha-to-mask fields can subtly change image correctness. Errors may appear only in specific MSAA, VRS, stereo, or shader-kill combinations.
- `VGT_SHADER_STAGES_EN`, tessellation, NGG, and primitive payload fields are tightly coupled to shader program state. Mismatched wave32, primitive-generation, LS/HS/GS/VS, or pass-through settings can hang draws or produce invalid geometry.
- `CP_MEC_CNTL` and `CP_ME_CNTL` bits affect engine halt, step, reset, and cache invalidation. Accidental writes while queues are active can stall command submission or disturb firmware-managed engines.
- `GRBM_GFX_CNTL` changes the selected pipe/ME/queue/context aperture for following accesses. Stale selection state can make subsequent debug or RLC/CP accesses observe or modify the wrong queue.
- `SQ_DEBUG_STS_GLOBAL*` are live status surfaces. Decoding errors can mislead hang triage by reporting wrong busy, wave-level, or FIFO occupancy values.
- Reserved, spare, and ECO fields appear in DB, PA_SC, PA_PH, and VRS controls. Full-register writes that ignore reserved-bit preservation may introduce generation-specific instability.

## Test Signals

Useful validation is a mix of generated-data checks, build coverage, and hardware exercise:

- Build AMDGPU configurations that include GC 11.0.3 support. Missing or malformed macros should surface in `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, `imu_v11_0_3.c`, KFD GFX11 code, or clear-state-related paths.
- Mechanically compare every `__SHIFT` and `_MASK` in lines 24657-27046 against AMD's authoritative GC 11.0.3 register database.
- Cross-check that each register in this chunk has matching entries in `gc_11_0_3_offset.h` and, where expected, default values in `gc_11_0_3_default.h`.
- Run mask/shift consistency checks: masks should align with shifts, full-width data/address fields should use `0xFFFFFFFFL`, high address extension fields should use the expected low-bit width, and repeated `CB_COLOR0..7` families should remain structurally identical where hardware says they should.
- Boot affected GC 11.0.3 hardware and run graphics tests that exercise MSAA sample locations, VRS, conservative rasterization, tessellation, NGG, primitive ID reset, streamout opaque draws, polygon offset, depth/stencil compare, alpha-to-mask, and stereo/RT-slice state.
- Exercise render-target formats, views, mip/slice ranges, DCC/FDCC compression, extended base addresses, and swizzle/resource-type combinations while checking for corruption, resolve failures, VM faults, or render backend errors.
- Exercise queue halt/reset/debug flows and register-dump tooling that use `CP_MEC_CNTL`, `CP_ME_CNTL`, `GRBM_GFX_CNTL`, and SQ status fields.
- Exercise KFD process/queue creation and memory configuration paths that program `SH_MEM_CONFIG`, including address mode, alignment mode, instruction prefetch, and GL1 icache-use behavior.
- Decode known-good register dumps with these masks and compare against reference tooling, especially for `CB_COLOR*`, PA/SC binner/VRS controls, CP engine controls, GRBM queue selection, and SQ busy/wave/fifo state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002536`. The final per-file research should merge it with neighboring chunks for complete `gc_11_0_3_sh_mask.h` coverage. The previous chunk should provide the line immediately before this slice, including the `//PA_CL_NGG_CNTL` boundary comment, while the next chunk should complete `SQ_DEBUG` with `SQ_DEBUG__WAIT_DEP_CTR_ZERO_MASK` and continue into SQ trap-memory address registers.

### subset-b-002537: lines 27047-29638

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 27047-29638

## Purpose

This chunk is generated AMD GC 11.0.3 register bitfield metadata. It contains 2,134 preprocessor definitions across 426 register names and no executable C. The public contract is a set of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants used by AMDGPU register helpers to compose or decode 32-bit MMIO values for this graphics IP revision.

The range begins at the tail of shader debug/trap address registers (`SQ_SHADER_TBA_*`, `SQ_SHADER_TMA_*`), then covers PF-only command processor, HPD queue, DIDT/EDC, SPI debug, TCP, GDS, UTCL1, PMM/GCR, GC CAC/EDC/throttle, per-SE CAC weighting, PF-only2 SPI compute-unit resource reservation, and a large `gc_gfxudec` command-processor user-data/control section. It ends inside `CP_ME_COHER_CNTL`; the remaining coherency-size/base/status fields continue after this chunk boundary.

Although the repository subtree is named `ceph-client`, this file is AMD GPU driver hardware metadata, not distributed filesystem logic.

## Important APIs, Types, and Macros

This header defines no functions, structs, enums, callbacks, locks, allocations, or runtime variables. Its API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask.
- Address-block comments such as `// addressBlock: gc_pfonly_cpdec` and register comments such as `//CP_DFY_CNTL` preserve the generated hardware grouping.

The companion address metadata for this ASIC lives in `gc_11_0_3_offset.h`. In this tree, exact include users are `amdgpu/gfx_v11_0_3.c`, `amdgpu/imu_v11_0_3.c`, and `amdgpu/gfxhub_v3_0_3.c`. Consumers typically reach these constants through `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15 helpers.

Major register groups in this chunk:

- Shader trap/debug base registers: `SQ_SHADER_TBA_LO/HI`, `SQ_SHADER_TMA_LO/HI`, and the preceding `SQ_DEBUG` tail define trap base/memory address halves and trap enable state.
- PF-only CP decode: `CP_DEBUG_2`, `CP_FETCHER_SOURCE`, and the `CP_DFY_*` register set describe secure/debug override bits, packet/discard controls, DFY address/data windows, burst/tag status, and command size.
- HPD queue decode: `CP_HPD_MES_ROQ_OFFSETS`, `CP_HPD_ROQ_OFFSETS`, and `CP_HPD_STATUS0` expose IQ/PQ/IB offsets, queue state, mapped queue, availability, fetch state, offload checking, freeze, and force-queue controls.
- DIDT/EDC decode: `DIDT_INDEX_AUTO_INCR_EN`, `DIDT_EDC_*`, `DIDT_IND_INDEX`, and `DIDT_IND_DATA` describe dynamic power/thermal throttling, error detection controls, stall patterns, thresholds, status, overflow, rolling power delta, and indirect register access.
- SPI/TCP/GDS/UTCL1/PMM blocks: `SPI_CDBG_*`, `SPI_GDBG_*`, `SPI_RESET_DEBUG`, `SPI_ARB_CNTL_0`, `SPI_FEATURE_CTRL`, `SPI_SHADER_RSRC_LIMIT_CTRL`, `SPI_COMPUTE_WF_CTX_SAVE_STATUS`, `TCP_*`, `GDS_*`, `UTCL1_*`, `GCR_*`, and `PMM_CNTL2` provide shader debug, arbitration, resource-limit, wave context-save, texture-cache, global data-share, L1 translation, and global cache request controls/status.
- GC CAC/EDC/throttle block: `GC_CAC_*`, `SE*_CAC_*`, `GC_EDC_*`, `GC_THROTTLE_*`, `PCC_*`, `PWRBRK_*`, and `DIDT_STALL_PATTERN_*` define activity counter windows, aggregate counters, power/EDC throttle controls, stall-pattern generators, hysteresis, counters, status, overflow, and clock monitor controls.
- CAC weight tables and indirect windows: `GC_CAC_WEIGHT_*`, `SE_CAC_WEIGHT_*`, `GC_CAC_IND_INDEX/DATA`, and `SE_CAC_IND_INDEX/DATA` encode per-block activity weights for CP, EA, UTCL2, GDS, GE, PMM, GL2C, PH, SDMA, RLC, GRBM, TA, TD, TCP, SQ, SP, LDS, SQC, CU, CB/DB, SPI, PA/SC, and related graphics blocks.
- PF-only2 SPI resource reservation: `SPI_RESOURCE_RESERVE_CU_0..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15` reserve VGPR, SGPR, LDS, wave, and barrier resources per CU and enable reservation categories/accumulation behavior.
- GFX user decode command-processor registers: `CP_EOP_DONE_*`, many graphics pipeline statistic counters, scratch registers and atomics, append/fence/GDS atomic preop registers, ME MC read/write address/data registers, semaphore wait/signal addresses, DMA PFP/ME controls and commands, IB/ST command buffer controls, indirect draw/dispatch/index/GDS backup addresses, sample status, and the start of CP ME coherency controls.

## Control Flow

There is no runtime control flow in this header. Runtime control flow belongs to consumers that include this generated metadata:

1. A GFX11.0.3-specific driver file includes `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h`.
2. The code chooses a register offset with generated `reg*`/`mm*` symbols from the offset header.
3. It uses the shift/mask constants in this file to build or decode a 32-bit register value.
4. It reads or writes the register through SOC15 MMIO helpers, indirect register windows, firmware-programmed RLC RAM entries, interrupt handlers, debug paths, or reset/recovery logic.

For this ASIC, `gfx_v11_0_3.c` uses the same generated family to decode RLC FED interrupt status and dispatch RAS handling. `imu_v11_0_3.c` programs RLC RAM golden settings through GC register addresses and masks, including generated debug mask constants outside this specific line range. `gfxhub_v3_0_3.c` uses the GC 11.0.3 mask contract for VM invalidation and fault-status decoding. This chunk supplies adjacent CP, SPI, EDC, CAC, UTCL1, and GFX user-register field layouts that those same include environments can use for initialization, diagnostics, and ASIC workarounds.

## State and Persistence Behavior

The macros themselves have no state and persist nothing. They describe volatile hardware state exposed through GC 11.0.3 MMIO registers.

Some represented registers are durable configuration until reset, suspend/resume, power gating, SR-IOV transition, or explicit driver/firmware reprogramming. Examples include SPI resource reservation, shader trap base addresses, CP debug overrides, UTCL1/GCR controls, CAC/EDC thresholds, throttle controls, command buffer base/size registers, indirect draw/dispatch/index addresses, and CP coherency destination enables.

Other registers are live status or latched diagnostic state. HPD queue state, DIDT/EDC status, TCP status, GCR command status, CAC aggregate counters, EDC/performance counters, overflow bits, throttle status, scratch atomics, append/fence state, CP DMA command status, PFP completion status, and sample activity bits can change as firmware and GPU work progress. The header does not encode read-only, write-one-to-clear, self-clearing, firmware-owned, or reserved-bit semantics, so consumers must use hardware-specific sequencing and preserve unrelated fields on mixed control registers.

Indirect windows such as `DIDT_IND_INDEX/DATA`, `GC_CAC_IND_INDEX/DATA`, and `SE_CAC_IND_INDEX/DATA` have ordering-sensitive state: the index register selects which underlying register the data register targets. Interleaved reads/writes without the driver-side serialization expected by the register access path can decode or update the wrong target.

## Dependencies and Integration Points

Direct dependencies and integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` provides matching register offsets and base indices. This chunk is not useful by itself without the address metadata.
- `amdgpu/gfx_v11_0_3.c` includes this header for GC 11.0.3 RAS/FED interrupt handling and generated register access.
- `amdgpu/imu_v11_0_3.c` includes this header while programming GC 11.0.3 RLC RAM golden register settings used during initialization.
- `amdgpu/gfxhub_v3_0_3.c` includes this header for VM hub setup, invalidation request construction, FB/aperture programming, and protection-fault status decoding.
- Common AMDGPU register helpers (`REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`) consume the generated shift/mask names.
- RAS, debugfs/register dump, firmware, power-management, SR-IOV, KFD/debug, shader trap, performance counter, and GPU reset paths can depend on these field definitions even if a given macro is not referenced by the small GC 11.0.3 wrapper files directly.

The `gc_pfonly_*` and `gc_pfonly2_*` blocks are especially tied to privileged/PF-only access. Driver code must respect virtualization and firmware ownership boundaries; a macro being visible in the header does not imply it is legal for a VF or all runtime paths to write.

## Risks and Edge Cases

- Generated metadata can fail silently if numeric values are wrong. A bad mask or shift usually still compiles but can enable the wrong bit, truncate an address, poll the wrong status, or corrupt a power/throttle policy.
- The chunk has artificial boundaries. It starts after the first `SQ_DEBUG` fields and ends before the rest of the CP ME coherency register family, so complete per-register analysis requires adjacent chunks.
- Register/ASIC mismatches are high risk. Pairing GC 11.0.3 masks with another generation's offset header can compile while accessing different hardware fields.
- PF-only registers must not be treated as ordinary userspace or VF-safe controls. CP debug overrides, DIDT/EDC throttle controls, CAC weights, SPI resource reservation, and coherency controls can affect global GPU behavior.
- Address fields are often split into low/high halves and may have alignment semantics. CP EOP, pipe stats, append, DMA command, IB/ST, doorbell-buffer, indirect draw/dispatch/index, GDS backup, semaphore, and coherency base/size fields can misaddress memory if low-bit masks or shifts are misapplied.
- Indirect register pairs are ordering-sensitive. DIDT and CAC index/data windows can return stale or unintended data if accessed concurrently without the expected locking or hardware access discipline.
- Power and reliability controls have non-obvious side effects. DIDT/EDC, CAC, PCC, PWRBRK, throttle, hysteresis, stall pattern, and clock-monitor fields can change performance, thermal behavior, RAS visibility, or validation reproducibility.
- CP DMA, semaphore, append, scratch atomic, EOP, and coherency fields are synchronization-critical. Incorrect programming can break fence completion, cache flush/invalidation, indirect-buffer execution, draw/dispatch setup, or GPU reset recovery.
- Status bits are live. Queue availability, busy/idle, overflow, throttle, sample activity, completion, and counter fields can race with active GPU work, so tests and diagnostics need stable quiescing or repeated polling.

## Test Signals

Useful validation is mostly build-time, static consistency, and hardware/runtime coverage:

- Build all GC 11.0.3 paths that include `gc_11_0_3_sh_mask.h`, especially `gfx_v11_0_3.c`, `imu_v11_0_3.c`, and `gfxhub_v3_0_3.c`.
- Run generated-header consistency checks: each referenced field has both shift and mask definitions, masks align with shifts, register names match `gc_11_0_3_offset.h`, and artificial chunk boundaries are reconciled by adjacent research chunks.
- Boot/probe GC 11.0.3 hardware and confirm GFX, IMU/RLC RAM programming, gfxhub VM setup, and RAS/FED interrupt paths initialize without register-access faults.
- Exercise VM invalidation and protection-fault reporting through gfxhub workloads; fault status should decode plausible client IDs and permission/mapping bits.
- Run graphics and compute workloads that stress CP EOP fences, indirect draw/dispatch, IB/ST command buffers, CP DMA, semaphores, scratch registers, append buffers, GDS atomic preops, and sample-status reporting.
- Validate suspend/resume, GPU reset, and SR-IOV/PF-VF scenarios, watching for illegal PF-only access, stuck queue/status bits, missing fences, or RLC/CP recovery failures.
- Check power/RAS diagnostics under stress: DIDT/EDC counters and overflows, CAC aggregate and weight readbacks, throttle status, PCC/PWRBRK/DIDT stall pattern behavior, and RAS error paths should be coherent and recoverable.
- Debug/profiling signals include sane SPI resource reservation state, shader trap base address handling, TCP/GDS/UTCL1/GCR status readbacks, CP pipe statistics, scratch atomic behavior, PFP completion status, and CP ME coherency status once adjacent coherency fields are included.

### subset-b-002538: lines 29639-32347

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 29639-32347

## Purpose

This chunk is generated AMD GC 11.0.3 register bitfield metadata. It contains no executable C code; it exports preprocessor constants that describe the `SHIFT` and `MASK` layout of 32-bit graphics-core MMIO registers. Runtime driver code combines these constants with the matching address definitions from `gc_11_0_3_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and table-driven golden-register writers.

The selected range starts in the `CP_ME_COHER_CNTL` field family, then covers graphics frontend, primitive assembly, shader, line/stipple/trap-screen, SQ trace userdata, GDS atomic/GWS/OA/streamout counters, SPI controls, a large `gc_cprs64dec` command-processor RS64/MES/MEC/GFX register block, `gc_gl1dec`, `gc_chdec`, and the start of `gc_gl2dec`. The chunk ends at line 32347 in the middle of `GL2C_CM_CTRL2`; later lines contain the remaining masks for that register and the following GL2C registers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocation sites, or C control structures in this slice. The API is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit used to encode or extract a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the same field.
- Register comments such as `//CP_MES_CNTL` and address-block comments such as `// addressBlock: gc_cprs64dec` group the macros by hardware register and decode block.

Major register families in this chunk:

- CP coherency and indexed draw setup: `CP_ME_COHER_CNTL`, `CP_ME_COHER_SIZE(_HI)`, `CP_ME_COHER_BASE(_HI)`, and `CP_ME_COHER_STATUS` describe CP ME cache/coherency operation ranges and destination-base enable bits for CB/DB/general destinations. `GRBM_GFX_INDEX` exposes instance, SA, and SE selection plus broadcast-write bits used by per-instance register programming.
- Geometry/frontend setup: `VGT_PRIMITIVE_TYPE`, `VGT_INDEX_TYPE`, `GE_MIN_VTX_INDX`, `GE_MAX_VTX_INDX`, `GE_INDX_OFFSET`, `GE_MULTI_PRIM_IB_RESET_EN`, `VGT_NUM_INDICES`, `VGT_NUM_INSTANCES`, `VGT_TF_RING_SIZE`, `VGT_HS_OFFCHIP_PARAM`, `VGT_TF_MEMORY_BASE(_HI)`, `VGT_INSTANCE_BASE_ID`, `GE_CNTL`, `GE_USER_VGPR1..3`, `GE_USER_VGPR_EN`, `GE_STEREO_CNTL`, `GE_PC_ALLOC`, `GE_GS_FAST_LAUNCH_WG_DIM(_1)`, and `VGT_GS_OUT_PRIM_TYPE` describe draw index bounds, tessellation/transform-feedback memory, primitive-group/subgroup sizing, stereo/view controls, and optional user VGPR payloads.
- Raster/trap/screen and shader debug: `PA_SU_LINE_STIPPLE_VALUE`, `PA_SC_LINE_STIPPLE_STATE`, `PA_SC_SCREEN_EXTENT_MIN/MAX`, P3D/HP3D/plain trap-screen enable/coordinate/count registers, `SQ_THREAD_TRACE_USERDATA_0..7`, `SQC_CACHES`, and `TA_CS_BC_BASE_ADDR(_HI)` provide line stipple state, screen extents, trap-screen diagnostics, shader thread-trace userdata, SQC cache validity/busy bits, and texture address base fields.
- GDS, GWS, OA, atomics, and streamout: `DB_OCCLUSION_COUNT*`, `GDS_RD_*`, `GDS_WR_*`, `GDS_WRITE_COMPLETE`, `GDS_ATOM_*`, `GDS_GWS_RESOURCE_CNTL`, `GDS_GWS_RESOURCE`, `GDS_GWS_RESOURCE_CNT`, `GDS_OA_*`, `GDS_STRMOUT_DWORDS_WRITTEN_*`, `GDS_GS_*`, and `GDS_STRMOUT_PRIMS_NEEDED/WRITTEN_*` define low-level GDS read/write windows, atomic operand/result registers, global-wave-sync resource allocation fields, ordered-append ring/counter fields, and streamout statistics.
- SPI controls: `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, `SPI_WAVE_LIMIT_CNTL`, `SPI_GS_THROTTLE_CNTL1/2`, `SPI_ATTRIBUTE_RING_BASE`, and `SPI_ATTRIBUTE_RING_SIZE` describe shader-processor interface behavior including export/GS throttle limits, wave limits, interpolation and parameter-cache policy, LDS/CU grouping, attribute-ring address/size, and related workaround or clock/perf controls.
- `gc_cprs64dec`: this is the densest block. It defines RS64/MES/MEC/GFX command-processor control and debug fields, including program-counter starts, interrupt/vector addresses, machine-status/cause/bad-address/IP/cycle/time/instret identity-style registers, scratch index/data, instruction pointers, icache and dcache operation controls, pipe priorities and process quantum, doorbell controls, general-purpose registers, local/instruction/scratch aperture base/mask/control registers, perf counters, pending interrupts, interrupt data slots, and 16 dcache aperture base/mask/control triplets for MES, MEC, and GFX RS64 paths.
- MES and MEC control highlights: `CP_MES_CNTL` and `CP_MEC_RS64_CNTL` contain invalidate-icache, pipe reset, pipe active, halt, and step fields. `CP_MES_DC_OP_CNTL`, `CP_MEC_DC_OP_CNTL`, and `CP_GFX_RS64_DC_OP_CNTL` expose dcache invalidate, completion, bypass, and in the GFX RS64 case volatile/writeback control bits. `CP_MES_DOORBELL_CONTROL1..6` expose doorbell offset/enabled/hit bits for scheduling and queue wakeup.
- GFX RS64-specific fields: `CP_GFX_CNTL`, `CP_GFX_RS64_INTERRUPT0/1`, `CP_GFX_RS64_INTR_EN0/1`, paired `MIP`, `MTIMECMP`, GP, instruction-pointer, pending-interrupt, and dcache aperture families describe two GFX RS64 contexts/lanes plus their local memory windows and interrupt state.
- `gc_gl1dec`: `GL1_ARB_CTRL`, `GL1_DRAM_BURST_MASK`, `GL1_ARB_STATUS`, `GL1_DRAM_BURST_CTRL`, `GL1I_GL1R_REP_FGCG_OVERRIDE`, `GL1C_CTRL`, `GL1C_STATUS`, `GL1C_UTCL0_CNTL2`, `GL1C_UTCL0_STATUS`, `GL1C_UTCL0_RETRY`, and `GL1C_CTRL2` describe GL1 arbitration, burst policy, fine-grain clock-gating overrides, GL1 cache force-hit/miss/no-fill modes, GL2 request/data credits, tag/tracker/FIFO busy and stall diagnostics, UTCL0 fault/retry/PRT state, snoop/burst/big-page behavior, and inflight limits.
- `gc_chdec`: `CH_ARB_CTRL`, `CH_DRAM_BURST_MASK`, `CH_ARB_STATUS`, `CH_DRAM_BURST_CTRL`, `CHA_CHC_CREDITS`, `CHA_CLIENT_FREE_DELAY`, `CHI_CHR_REP_FGCG_OVERRIDE`, `CH_VC5_ENABLE`, `CHC_CTRL`, `CHC_STATUS`, `CHCG_CTRL`, and `CHCG_STATUS` describe channel-hub arbitration, memory/IO burst-gather policy, client/free-delay knobs, virtual-channel enablement, clock-gating overrides, request/data credits, virtual FIFO and tracker stalls, and VC0/VC1 busy/full status.
- `gc_gl2dec` start: `GL2C_CTRL`, `GL2C_CTRL2`, `GL2C_STATUS`, `GL2C_ADDR_MATCH_MASK`, `GL2C_ADDR_MATCH_SIZE`, `GL2C_WBINVL2`, `GL2C_SOFT_RESET`, `GL2C_CM_CTRL0`, `GL2C_CM_CTRL1`, `GL2C_CM_STALL`, and the first part of `GL2C_CM_CTRL2` cover L2 cache sizing, writeback and latency FIFOs, metadata/compression cache behavior, hit-under-miss/probe/fill policy, writeback/invalidate status, soft reset, address-match filtering, compression-manager hash/burst/recompression controls, and the beginning of partial-write/VRS/DCC-error-detection controls.

## Control Flow

This header has no direct runtime control flow. Its indirect operational flow is:

1. A GC 11.0.3 driver file includes `gc/gc_11_0_3_offset.h` and `gc/gc_11_0_3_sh_mask.h`.
2. The driver selects a register address from the offset header, for example `regGRBM_GFX_INDEX`, `regCP_MES_CNTL`, `regCP_MEC_RS64_CNTL`, `regCP_GFX_RS64_DC_OP_CNTL`, `regGL1C_CTRL`, or `regGL2C_CTRL2`.
3. The driver composes or decodes a value using these field masks through `REG_SET_FIELD`, `REG_GET_FIELD`, or table masks.
4. The value is sent to hardware through SOC15 register access, IMU/RLC RAM programming, MES scheduling setup, KFD queue management, GFX reset, cache invalidation, or diagnostic paths.

Observed integration in this source tree includes `amdgpu/gfx_v11_0_3.c`, `amdgpu/imu_v11_0_3.c`, and `amdgpu/gfxhub_v3_0_3.c` including this exact GC 11.0.3 mask header. Shared GC 11 paths such as `amdgpu/gfx_v11_0.c`, `amdgpu/mes_v11_0.c`, and `amdgpu/amdgpu_amdkfd_gfx_v11.c` show how the same macro families are used: `GRBM_GFX_INDEX` selects SE/SA/instance routing, `CP_MES_CNTL` starts/stops and resets MES pipes, `CP_MEC_RS64_CNTL` resets/halt/activates MEC pipes, and `CP_GFX_RS64_DC_OP_CNTL` drives dcache invalidation with polling for completion.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes hardware-visible register state. Persistence, latching, read-only/write-only behavior, and self-clearing behavior are defined by the GPU hardware and by the driver sequences that use these macros.

The represented hardware state includes CP coherency operation ranges, selected graphics instances through `GRBM_GFX_INDEX`, frontend draw parameters, GE/VGT/tessellation and transform-feedback state, raster/trap-screen diagnostics, SQ trace userdata, SQC cache state, GDS/GWS/OA resources and counters, streamout counters, SPI throttle and attribute-ring state, MES/MEC/GFX RS64 program counters, machine and interrupt state, pipe reset/active/halt state, doorbell hit/enables, local memory aperture mappings, dcache/icache operation bits, GL1/CH/GL2 cache and fabric arbitration configuration, busy/stall status bits, and compression-manager policy.

Some fields are persistent configuration until reset or reprogramming, such as aperture bases/masks, cache policy, burst controls, pipe priorities, and GL1/GL2 cache sizing. Others are live or sticky status, such as `*_STATUS` busy/stall flags, doorbell hit bits, timer-expired bits, dcache invalidate completion bits, GDS write-complete flags, and counter registers. Some are command-like strobes or self-clearing control bits, including cache invalidation, writeback/invalidate, soft reset, pipe reset, and error-status clear controls. This generated header does not encode those semantics, so consumers must preserve reserved/unrelated bits and follow the ASIC-specific sequencing in the owning driver code.

## Dependencies And Integration Points

The immediate companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which supplies the `reg*` addresses and base indices for the same register names. Reset/default values are supplied by sibling generated default headers and by golden-register tables.

Important integration points:

- `amdgpu/gfx_v11_0_3.c` includes this header for GC 11.0.3-specific GFX/RAS handling. The file reads RLC FED status registers and uses `REG_GET_FIELD`, demonstrating the expected field-decoding contract for this ASIC.
- `amdgpu/imu_v11_0_3.c` includes this header and programs an IMU/RLC RAM golden table. The table includes neighboring GC registers such as GCEA, GCVM, GB, and PSP-debug entries; this chunk's GL/CP/GDS/SPI fields use the same mask/address pairing mechanism.
- `amdgpu/gfxhub_v3_0_3.c` includes the same GC 11.0.3 headers for GFXHUB VM/cache setup. Although many VM fields live outside this chunk, it depends on the same generated-mask namespace.
- `amdgpu/gfx_v11_0.c` uses `GRBM_GFX_INDEX` field macros to select shader engines/arrays/instances, `CP_GFX_RS64_DC_OP_CNTL` to invalidate GFX RS64 dcache, and `CP_MEC_RS64_CNTL` to reset, halt, and activate MEC pipes.
- `amdgpu/mes_v11_0.c` uses `CP_MES_CNTL` field macros when loading, activating, halting, and resetting MES firmware pipes.
- `amdgpu/amdgpu_amdkfd_gfx_v11.c` uses `GRBM_GFX_INDEX` to steer KFD/compute register access to the desired SE/SA/instance.
- Hardware or firmware validation tooling can also consume the generated `SHIFT`/`MASK` pairs to compare against register databases, decode dumps, and validate golden settings.

## Risks And Edge Cases

- Header/offset mismatch is high risk. These GC 11.0.3 masks must be paired with the matching GC 11.0.3 offset/default definitions; cross-generation names often look similar while field positions differ.
- The chunk boundary is artificial. It begins after `CP_ME_COHER_CNTL__DEST_BASE_0_ENA__SHIFT` and ends before the remaining `GL2C_CM_CTRL2` masks, so the final per-file merge must reconcile adjacent chunks before describing those registers as complete.
- Dense control registers such as `CP_MES_CNTL`, `CP_MEC_RS64_CNTL`, `CP_GFX_RS64_DC_OP_CNTL`, `SPI_CONFIG_CNTL_1`, `GL1C_CTRL`, `CHC_CTRL`, and `GL2C_CTRL2` mix command, status, reset, clock-gating, cache, and workaround bits. A wrong shift or mask can reset the wrong pipe, leave firmware halted, break cache invalidation, corrupt attribute-ring setup, or change fabric/cache policy.
- Repeated register families are vulnerable to copy or generation errors. The MES/MEC/GFX RS64 GP registers, interrupt data slots, local aperture triplets, and `CP_*_DC_APERTURE0..15_*` families must remain internally consistent.
- Visible `SPARE`, `UNUSED`, `CHICKEN_BITS`, and full-width masks do not mean arbitrary writes are safe. Consumers need reset-default masks and read-modify-write discipline to avoid reserved or debug-only bits.
- `GRBM_GFX_INDEX` controls register broadcast versus targeted instance writes. Misprogramming it can accidentally broadcast a per-instance operation or only update one SE/SA/instance, causing asymmetric state and hard-to-debug hangs or performance anomalies.
- Cache/fabric status fields can be live and timing-sensitive. Polling `GL1C_STATUS`, `CHC_STATUS`, `CHCG_STATUS`, `GL2C_STATUS`, or dcache completion bits needs proper timeouts and reset handling in consumers.
- GDS/GWS/OA and streamout counters are attribution-sensitive. Misdecoded masks can report incorrect resource ownership, wrong atomic operand/result data, or misleading streamout/occlusion counts.
- GL2 compression-manager fields affect DCC/recompression/partial-write behavior. Incorrect use of the partial `GL2C_CM_CTRL2` fields visible in this chunk can surface as DCC corruption, VRS regressions, stale metadata, or performance cliffs.

## Test Signals

Useful validation is mostly generated-header consistency, build coverage, and hardware integration:

- Build AMDGPU, AMDKFD, MES, IMU, GFXHUB, and display paths that include `gc_11_0_3_sh_mask.h` with `gc_11_0_3_offset.h`.
- Generated-header checks should verify every visible `__SHIFT` has its intended `_MASK`, masks align with shifts, register field masks do not overlap except documented aliases/full-register fields, and register names have matching offsets in `gc_11_0_3_offset.h`.
- Static comparison against the authoritative GC 11.0.3 register database should focus on repeated CP RS64 aperture families, doorbell controls, pipe-control bits, GL1/CH/GL2 cache controls, and the partial `GL2C_CM_CTRL2` boundary.
- MES firmware load/start/stop/reset tests should exercise `CP_MES_CNTL`, doorbell controls, process quantum, interrupt, scratch, and program-counter fields.
- GFX reset and queue tests should exercise `CP_MEC_RS64_CNTL`, `CP_GFX_RS64_DC_OP_CNTL`, local aperture setup, icache/dcache invalidation, and polling for invalidate completion.
- KFD compute queue tests should cover `GRBM_GFX_INDEX` instance steering and GDS/GWS resource behavior under multi-SE/SA configurations.
- Graphics tests should stress indexed draws, primitive restart, tessellation, transform feedback, stereo, line stipple, screen extents, GS fast launch, SPI wave throttling, and attribute-ring programming.
- Cache/fabric tests should inspect GL1, CH, and GL2 busy/stall counters and status after reset, suspend/resume, heavy memory traffic, metadata/DCC workloads, writeback/invalidate, and soft reset sequences.
- Debug and reliability tests should validate occlusion/streamout counters, SQ thread trace userdata, GDS atomics/OA behavior, and fault/status decoding without writing reserved or debug-only fields in production paths.

### subset-b-002539: lines 32348-34934

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 32348-34934

## Scope

This chunk covers generated shift and mask macros from the GC 11.0.3 AMD GPU register header. It begins in the tail of `GL2C_CM_CTRL2`, then spans register field layouts for:

- GL2C control, load-balancer counters, discard-stall control, and GL2A arbitration/address-match controls.
- `gc_gl1hdec` GL1H arbitration, credit, burst, and status registers.
- `gc_perfddec` performance counter data registers for CP, GRBM, GE, PA, SPI, PC, SQ/SQG, SX, GCEA, GDS, TA/TD/TCP, GL2, GL1, CH, CB/DB, RLC/RMI/GCR, PH, UTCL1, CHA, and GUS blocks.
- `gc_perfsdec` performance counter selector/control registers, CP latency/window/draw filtering controls, GRBM busy-mask selectors, GE/PA/SPI/PC/SQ/SQG/SX/GCEA/GDS selectors, SQ thread trace buffer/control/status registers, and TCP performance counter filters.

The chunk is a preprocessor-only hardware description. It defines no C functions, structs, enums, storage, or executable control flow. Its contract is the exact bit layout used by AMDGPU code and debug/performance tooling when composing, writing, reading, or decoding GC 11.0.3 MMIO registers.

## Purpose

Each register field is represented by two macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for encoding or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit field mask for isolating that field.

These macros are intended to be used with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. Register addresses live in the matching `gc_11_0_3_offset.h`; reset/default values live in the matching default header. This file supplies only the per-field bit layout.

The most important behavior represented by this chunk is performance/debug instrumentation. It describes how to select performance events, gate them by shader stage, VMID, draw windows, command processor state, TCP request attributes, and thread trace masks, and how to read low/high counter data registers. It also contains a smaller amount of GL2/GL1 cache/arbitration configuration metadata.

## GL2C, GL2A, and GL1H Register Fields

The opening lines finish `GL2C_CM_CTRL2`, including masks for read burst timing, VRS disable, compression-ratio skipping, NBC indirect disables, partial-write optimization modes, recompression disable, and DCC compression-key error detection/clear behavior.

`GL2C_CTRL3` and `GL2C_CTRL4` provide broad GL2 cache-control metadata:

- Metadata memory type/coherency, no-fill, next-line prefetch, bank-linear hash mode/enable, 256-byte hash enable, set-group linear hash enable, and dGPU shared mode.
- Priority controls for HTILE, FMASK, DCC/CMASK, and SQC traffic.
- Writeback/write-read behavior such as force-read-on-write, writeback optimization enable/burst count, sector-full write marking, uncached-write atomic handling, read bypass as UC, and force MTYPE UC.
- Clock-gating and safe-mode controls such as `FGCG_OVERRIDE`, `CM_MGCG_MODE`, `MDC_MGCG_MODE`, `TAG_MGCG_MODE`, `CORE_MGCG_MODE`, `EXECUTE_MGCG_MODE`, and `FED_SAFE_MODE`.
- External access and protocol controls such as IO channel enable, SPA channel enable, EA read-size/GMI/NACK controls, source FIFO priority, writeback FIFO stall enable, flush-set counter mask disable, and no-write-ack-to-hit-queue.

The GL2C load-balancer counter group includes `GL2C_LB_CTR_CTRL`, `GL2C_LB_DATA0..3`, and `GL2C_LB_CTR_SEL0/1`. These fields control counter start/load/clear, select four events, optionally divide them, and read the resulting 32-bit counter values.

`GL2C_DISCARD_STALL_CTRL` provides a limit/window/drop-next/enable layout for discard-stall throttling. `GL2A_ADDR_MATCH_CTRL`, `GL2A_ADDR_MATCH_MASK`, and `GL2A_ADDR_MATCH_SIZE` describe address-match disabling, masks, and max-count sizing. `GL2A_PRIORITY_CTRL`, `GL2A_CTRL`, and `GL2A_RESP_THROTTLE_CTRL` describe priority disables, return arbitration timing, burst staying, FGCG override, credit safe values, write-combine timeout, address column-bit removal, internal return bypass, and response throttle credits for GL1/channel paths.

The `gc_gl1hdec` block contains `GL1H_ARB_CTRL`, `GL1H_GL1_CREDITS`, `GL1H_BURST_MASK`, `GL1H_BURST_CTRL`, and `GL1H_ARB_STATUS`. These fields cover request/source/return fine-grain clock gating disables, GL1 request credits, burst-mask selection, burst-timer value, burst-in-flight counter, and stall status.

## Performance Counter Data Registers

The `gc_perfddec` portion is mostly readout storage for performance counters. The simple `*_PERFCOUNTER*_LO` and `*_PERFCOUNTER*_HI` macros define full-width 32-bit low/high fields named `PERFCOUNTER_LO`, `PERFCOUNTER_HI`, or a variant such as `PERFCOUNTER0_LO`. These pairs form 64-bit counter values when read in the correct order by consumers.

Covered blocks include:

- Command processor families: `CPG`, `CPC`, `CPF`, plus latency statistics data for CPF/CPG/CPC.
- Global graphics and shader engine front-end: `GRBM`, `GRBM_SE0..3`, `GE1`, `GE2_DIST`, and `GE2_SE`.
- Geometry/raster/front-end units: `PA_SU`, `PA_SC`, `PA_PH`, `SPI`, and `PC`.
- Shader and shader-global counters: `SQ_PERFCOUNTER0..7_LO` and `SQG_PERFCOUNTER0..7_LO/HI`.
- Pixel/export/shared-data paths: `SX`, `GCEA`, `GDS`, `TA`, `TD`, `TCP`, `CB`, `DB`, `CHC`, `CHCG`, `CHA`, and `GUS`.
- Cache, memory, and control paths: `GL2C`, `GL2A`, `GL1C`, `GL1A`, `GL1H`, `UTCL1`, `RLC`, `RMI`, and `GCR`.

Most of these registers expose only a single full-register data field. They are semantically dependent on the selector/configuration registers in `gc_perfsdec`; incorrect selector programming will still produce syntactically valid reads but meaningless or misleading counter values.

## TCP Counter Filters

`TCP_PERFCOUNTER_FILTER`, `TCP_PERFCOUNTER_FILTER2`, and `TCP_PERFCOUNTER_FILTER_EN` describe request filtering for TCP performance counters. The filter value includes buffer/flat/dimension fields, data and number format fields, software mode, sample count, opcode type, SLC/DLC/GLC coherency attributes, compression enable, and request mode. The corresponding enable register has one bit per filter dimension.

This split means consumers must program both a filter value and the enable mask. A filter field set in `TCP_PERFCOUNTER_FILTER` has no effect unless its enable bit is set in `TCP_PERFCOUNTER_FILTER_EN`. Conversely, leaving enable bits set while changing only part of the filter can silently narrow or broaden captured traffic.

## Performance Counter Select and Control Registers

The `gc_perfsdec` block provides the programming side for the data registers:

- CP selectors include `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, and `CPF_PERFCOUNTER*` select layouts with `PERF_SEL`, `PERF_SEL1`, `SPM_MODE`, and counter-mode fields.
- `CP_PERFMON_CNTL` exposes overall performance monitor state, SPM performance monitor state, enable mode, and sample enable.
- `CPF_TC_PERF_COUNTER_WINDOW_SELECT`, `CPG_TC_PERF_COUNTER_WINDOW_SELECT`, and `CPC_TC_PERF_COUNTER_WINDOW_SELECT` select indexed thread/transaction-counter windows with `ALWAYS` and `ENABLE` controls.
- `CPF_LATENCY_STATS_SELECT`, `CPG_LATENCY_STATS_SELECT`, and `CPC_LATENCY_STATS_SELECT` select latency statistic indexes and expose `CLEAR` and `ENABLE` command bits.
- `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` describe draw-window filtering and draw/object counting.

`GRBM_PERFCOUNTER0_SELECT` and `GRBM_PERFCOUNTER1_SELECT` select global GRBM counter events and user-defined busy/clean masks for DB, CB, TA, SX, SPI, SC, PA, GRBM, CP, GDS, BCI, RLC, TCP, GE, UTCL2, EA, and RMI. The `GRBM_SE0..3_PERFCOUNTER_SELECT` variants select per-shader-engine events and busy masks for DB/CB/TA/SX/SPI/SC/PA/BCI/RMI/UTCL1/TCP/GL1CC/GL1H/PC/SEDC. `GRBM_PERFCOUNTER0_SELECT_HI` and `GRBM_PERFCOUNTER1_SELECT_HI` extend global busy masks for UTCL1, GL2CC, SDMA, CH, PH, PMM, GUS, GL1CC, and GL1H.

The GE, PA, SPI, PC, SX, GCEA, and GDS selector families share a repeated layout: primary selectors use `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE` or `SPM_MODE`, and per-selector `PERF_MODE` fields; companion `SELECT1` registers usually provide `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`. Some later counters have only one selector and mode. This repetition is an important ABI shape for generic performance counter setup code.

## SQ, SQG, and Thread Trace

The SQ/SQG section defines:

- `SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT` and `SQG_PERFCOUNTER0_SELECT` through `SQG_PERFCOUNTER7_SELECT`, each with event selection and counter mode fields.
- `SQG_PERFCOUNTER_CTRL` and `SQ_PERFCOUNTER_CTRL`, which gate counters by shader stage (`PS`, `GS`, `HS`, `CS`) and can disable performance collection for specific ME/pipe combinations.
- `SQG_PERFCOUNTER_CTRL2` and `SQ_PERFCOUNTER_CTRL2`, which provide force-enable and VMID enable masks.
- `SQG_PERF_SAMPLE_FINISH`, which exposes sample-finish status.

Thread trace registers are more stateful:

- `SQ_THREAD_TRACE_BUF0_BASE/SIZE` and `SQ_THREAD_TRACE_BUF1_BASE/SIZE` define trace buffer base low bits, high base bits, and size fields.
- `SQ_THREAD_TRACE_CTRL` selects tracing mode, all-VMID mode, GL1 performance capture, interrupt enable, double buffering, high-water/low-water behavior, SPI/SQ stall behavior, utility timer, wave-start mode, real-time frequency, sync-count markers/draws, auto-flush behavior, and draw event enable.
- `SQ_THREAD_TRACE_MASK` selects SIMD, WGP, shader array, wave type include mask, and non-detail shader-data exclusion.
- `SQ_THREAD_TRACE_TOKEN_MASK` selects token exclusion, execution token inclusion, BOP event token inclusion, register inclusion/exclusion, instruction exclusion, and full register detail.
- `SQ_THREAD_TRACE_WPTR` reports the trace write pointer and active buffer id.
- `SQ_THREAD_TRACE_STATUS` reports finish-pending, finish-done, write-error, busy, and owner VMID state.
- `SQ_THREAD_TRACE_STATUS2` reports full buffers, lost packets, buffer issue status, buffer issue, and write-buffer full state.
- Draw, marker, HP3D, and dropped counters expose full 32-bit count fields.

These definitions are sensitive because trace setup crosses memory allocation, VMID ownership, interrupt behavior, and GPU pipeline stalling. The header does not enforce alignment, buffer lifetime, ownership, or sequencing; it only provides field positions.

## GCEA, SX, and GDS Tail

The tail of this chunk covers GCEA performance selectors and mode/config registers, then SX and GDS selector families. `GCEA_PERFCOUNTER2_SELECT`, `GCEA_PERFCOUNTER2_SELECT1`, and `GCEA_PERFCOUNTER2_MODE` support four event selectors with compare modes and compare values. `GCEA_PERFCOUNTER0_CFG` and `GCEA_PERFCOUNTER1_CFG` provide range-style `PERF_SEL`/`PERF_SEL_END`, performance mode, enable, and clear bits. `GCEA_PERFCOUNTER_RSLT_CNTL` selects which performance counter result is controlled and provides start/stop trigger masks, enable-any, clear-all, and stop-all-on-saturate bits.

The SX and GDS selectors follow the common event/mode shape. `SX_PERFCOUNTER0/1_SELECT` include two event selectors plus modes, while `SX_PERFCOUNTER2/3_SELECT` define one event selector and mode. `SX_PERFCOUNTER0/1_SELECT1` add selectors two and three. `GDS_PERFCOUNTER0..3_SELECT` each expose `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`. This chunk ends immediately before `GDS_PERFCOUNTER0_SELECT1`, so the final merged file report must connect this section with the following chunk for the remaining GDS selector companion registers.

## Control Flow and State Behavior

There is no C control flow in this header. The runtime behavior occurs in AMDGPU/KFD/display consumers that include this generated ASIC header and write/read the associated MMIO registers through SOC15 register helpers.

The persistent state affected by these macros is hardware state:

- Cache/arbitration controls persist in GL2C/GL2A/GL1H registers until reset or reprogramming.
- Performance selectors, filters, monitor state, latency selectors, and draw windows persist while profiling is active and determine which hardware events increment data counters.
- Counter data registers hold hardware-maintained values and may require explicit clear/start/stop sequencing depending on the owning block.
- Thread trace buffer base/size/control/mask/token settings persist for a trace session; status and write-pointer registers reflect asynchronous hardware progress.
- Clear, load, start, stop, enable, request, and status bits are command-like or latch-like even though the header exposes them as plain masks.

Because these macros are raw field constants, the header cannot validate legal event IDs, valid mode values, buffer alignment, VMID ownership, polling order, counter read ordering, or whether a register is safe to program while the block is busy.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header naming convention:

- `gc_11_0_3_offset.h` supplies the matching `reg...`/`mm...` register addresses for these field names.
- A matching default header supplies reset/default values for many of the same registers.
- AMDGPU register helpers in `soc15.h`/related headers consume `__SHIFT` and `_MASK` definitions through `REG_SET_FIELD` and `REG_GET_FIELD`.

Direct GC 11.0.3 include users in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`, which includes the offset and mask headers for GC 11.0.3-specific GFX/RAS handling.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`, which includes the same ASIC headers for GFXHUB programming.
- `drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`, which uses GC 11.0.3 register definitions for IMU/RLC programming tables.

The specific performance and trace macro families are also part of the broader AMDGPU performance/debug ABI. Sibling generation files (`gc_11_0_0_sh_mask.h`, GC 9/10/12 headers, and older GCA headers) contain similar names with generation-specific layouts. Consumers must pair GC 11.0.3 masks with GC 11.0.3 offsets and defaults; similar register names from another ASIC generation are not interchangeable.

## Risks

- A wrong shift or mask can program the wrong hardware bit. In this chunk, the likely failures include corrupt performance captures, missed or excessive profiling interrupts, forced stalls, broken trace buffer ownership, cache/arbitration regressions, or invalid counter reads.
- Repeated selector families are typo-prone. GE, PA, SPI, PC, SQ, SQG, SX, GDS, and GRBM selectors use near-identical layouts, but there are deliberate variations in field names, number of selectors, busy-mask coverage, and high-selector registers.
- Status and command fields look like ordinary bitfields. Misusing `CLEAR`, `START`, `STOP`, `LOAD`, `ENABLE`, `FINISH_*`, buffer-full, or clear-all bits can drop diagnostic data or leave profiling hardware in an active state.
- Thread trace fields can affect execution. Stall-enable, interrupt-enable, double-buffer, high-water, low-water, auto-flush, and VMID fields must be sequenced with buffer allocation and ownership rules outside this header.
- Performance counters are not self-describing. Event selector values are hardware-defined; compile success only proves the bit layout exists, not that the selected event is legal or meaningful.
- Cross-generation copy/paste is risky. The same macro families appear in many GC/GCA headers with different masks, extra fields, or older field names such as `PERFCOUNTER_SELECT` instead of `PERF_SEL`.

## Test and Validation Signals

Useful validation for this chunk is mostly compile-time and hardware-integration level:

- Build coverage for GC 11.0.3 AMDGPU sources that include `gc/gc_11_0_3_sh_mask.h`; this catches missing, renamed, or syntactically invalid macros.
- Static checks can verify that every field has a matching `__SHIFT` and `_MASK`, repeated selector families remain internally consistent, and masks do not overlap unexpectedly within a register.
- Register programming tests should exercise performance monitor enable/disable, CP latency statistics selection/clear, draw-window filters, TCP filter enable/value pairing, and low/high counter reads.
- Profiling/debug tooling should validate that SQ/SQG/SX/GDS/GCEA/GRBM event selection produces expected counter movement under known workloads.
- Thread trace validation should allocate trace buffers, program base/size/control/masks, start and finish trace capture, poll `SQ_THREAD_TRACE_STATUS*`, inspect write pointers, and verify dropped/error counters under both normal and near-full-buffer conditions.
- Reset, suspend/resume, and GPU recovery tests should confirm that persistent performance/debug/cache-control registers are restored or cleared by the owning driver paths and do not leak stale profiling state.

## Unresolved Cross-Chunk References

This chunk starts after the `GL2C_CM_CTRL2` definition began in an earlier chunk and ends in the middle of the GDS performance selector family, immediately before `GDS_PERFCOUNTER0_SELECT1`. Later chunks should cover the remaining GDS selector companion registers and any subsequent performance/debug definitions. The final per-file report should merge this with adjacent chunks to describe the full `gc_11_0_3_sh_mask.h` generated header, its include guard, all address blocks, and complete repeated register families.

### subset-b-002540: lines 34935-37498

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 34935-37498

## Scope

This chunk covers generated shift and mask macros from the GC 11.0.3 AMD GPU register mask header. It starts in the middle of the `GDS_PERFCOUNTER3_SELECT` family and ends at the `RLC_CLK_COUNT_REFCLK_MSB` register comment, just before that register's field definitions in the next chunk. The covered range includes:

- Performance counter selector fields for GDS, TA, TD, TCP, GL2C, GL2A, GL1C, CHC, CHCG, CB, DB, RLC, RMI, GCR, PA_PH, UTCL1, GL1A, GL1H, CHA, and GUS blocks.
- CB filtering fields for render-backend performance counter filtering.
- RLC streaming performance monitor (SPM), accumulator, ring buffer, RSPM request/response, and pause/status fields.
- GDFLL and GRTAVFS dynamic frequency/voltage and EDC hysteresis fields.
- Hypervisor, SR-IOV, RLC virtualization, doorbell, semaphore, scheduler, interrupt, microcode, scratch, and memory access fields.
- Pipe steering, harvest/user configuration, shader-array, primitive, render-backend, RMI redundancy, and TCC disable masks.
- Command processor hypervisor microcode, instruction-cache, data-cache, and MES/MEC/GFX RS64 memory-bound fields.
- GRBM hypervisor selection/data registers and per-VF framebuffer aperture fields.
- RLC core control, status, timers, legacy interrupts, clock-gating, power-gating delay, GPU clock counters, GPM thread reset/cache invalidation, and GPM CP DMA completion fields.

The file is purely a generated hardware register bitfield map. It defines preprocessor constants only: no C functions, structs, variables, storage, or executable control flow live in this chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU driver code and GC 11.0.3 hardware registers. Each covered field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate or compose that field.

Driver code combines these constants with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The sibling `gc_11_0_3_offset.h` file supplies register addresses such as `regRLC_SPM_PERFMON_CNTL`, `regRLC_GPU_IOV_VF_ENABLE`, `regCP_HYP_PFP_UCODE_ADDR`, `regGRBM_GFX_INDEX_SR_SELECT`, and `regGCMC_VM_FB_SIZE_OFFSET_VF0`; this file supplies the field positions and masks for those addresses.

## Important Macro Families

### Performance Counter Selection

The first half of the chunk is dominated by performance counter selector definitions. These families share a regular encoding:

- `*_PERFCOUNTER0_SELECT` often contains `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`.
- `*_PERFCOUNTER0_SELECT1` often adds `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`.
- Later counters in the same block may be narrower and expose only `PERF_SEL` plus `PERF_MODE`, depending on the hardware block.

The covered blocks include GDS, TA, TD, TCP, GL2C, GL2A, GL1C, CHC, CHCG, CB, DB, RLC, RMI, GCR, PA_PH, UTCL1, GL1A, GL1H, CHA, and GUS. The consistent 10-bit selector masks such as `0x000003FFL` and mode fields in the upper nybbles reflect hardware-controlled event selection, counter mode, and multi-event packing.

`CB_PERFCOUNTER_FILTER` is more specialized. It defines enable/selector fields for operation, format, clear, MRT, sample count, and fragment count filters. This lets profiling or debug code restrict color-buffer performance counter samples by render-backend operation shape, not just choose the event source.

GUS adds separate mode/configuration/result-control registers (`GUS_PERFCOUNTER2_MODE`, `GUS_PERFCOUNTER0_CFG`, `GUS_PERFCOUNTER1_CFG`, and `GUS_PERFCOUNTER_RSLT_CNTL`) with flags for counter mode, mode 32/32+32/64, filter enables, math operation selection, increment behavior, clamp, and level/packet-style control.

### RLC Streaming Performance Monitor and Accumulator

The `RLC_SPM_*` block describes the streaming performance monitor path owned by RLC. Important registers include:

- `RLC_SPM_PERFMON_CNTL`, with ring mode, GFX clock count disable, and sample interval fields.
- `RLC_SPM_PERFMON_RING_BASE_LO/HI`, `RLC_SPM_PERFMON_RING_SIZE`, `RLC_SPM_RING_WRPTR`, and `RLC_SPM_RING_RDPTR`, which define the memory ring buffer and producer/consumer pointers used for streamed samples.
- `RLC_SPM_SEGMENT_THRESHOLD` and `RLC_SPM_PERFMON_SEGMENT_SIZE`, which divide global and shader-engine sample streams into segments.
- `RLC_SPM_GLOBAL_MUXSEL_*` and `RLC_SPM_SE_MUXSEL_*`, which address and write mux selection RAMs for global and per-SE sampling sources.
- `RLC_SPM_ACCUM_DATARAM_*`, `RLC_SPM_ACCUM_SWA_DATARAM_*`, `RLC_SPM_ACCUM_CTRLRAM_*`, and `RLC_SPM_ACCUM_CTRLRAM_ADDR_OFFSET`, which expose accumulator data/control RAM access.
- `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, `RLC_SPM_ACCUM_MODE`, thresholds, requested sample counts, data RAM write count, and 32-bit counter region selectors.
- `RLC_SPM_PAUSE`, `RLC_SPM_STATUS`, `RLC_SPM_GFXCLOCK_LOWCOUNT`, `RLC_SPM_GFXCLOCK_HIGHCOUNT`, and `RLC_SPM_MODE`, which support pausing, status polling, clock count capture, and mode control.

Several fields are command-like strobes rather than durable configuration. For example, `RLC_SPM_ACCUM_CTRL__StrobeStartAccumulation`, `StrobeResetPerfMonitors`, `StrobeStartSpm`, `StrobeRearmAccum`, and `StrobePerfmonSampleWires` trigger actions in hardware. `RLC_SPM_ACCUM_STATUS` exposes completion, overflow, armed, FIFO empty, idle, pending rearm, and aborted state that consumers should poll or use for diagnostics.

### RSPM Request/Response Access

The `RLC_SPM_RSPM_*` and `RLC_SPM_SE_RSPM_*` fields define low-level request/response windows for RSPM operations. They expose request low/high data, request operation, returned data, returned operation/status, command fields, and command acknowledgement. These definitions are integration points for debug/performance paths that need indirect access to RSPM state and must respect busy/ack sequencing.

### Dynamic Frequency, Voltage, and EDC Hysteresis

The `GDFLL_*` and `GDFLL_SE_*` blocks provide EDC hysteresis control/status masks. They define maximum hysteresis counts and observed EDC/hysteresis status.

The `GRTAVFS_*`, `GRTAVFS_SE_*`, and `RTAVFS_*` blocks provide register-address, write-data, read-data, control, status, target-frequency, target-voltage, soft-reset, PSM, and clock-control fields for real-time adaptive voltage/frequency scaling. Key fields include:

- `SET_WR_EN` and `SET_RD_EN` command bits with status bits `RTAVFS_WR_ACK` and `RTAVFS_RD_DATA_VALID`.
- `TARGET_FREQUENCY` plus `REQUEST`.
- `TARGET_VOLTAGE` plus `VALID`.
- `RESETN_OVERRIDE`, PSM count/sample enable, and forced clock mux selection.

These fields describe hardware state that is usually coordinated with SMU/power-management policy. Incorrect writes can request the wrong frequency/voltage state or desynchronize indirect register accesses.

### Hypervisor, SR-IOV, and RLC Virtualization

The `gc_hypdec` portion defines masks for virtual function enablement, scheduling, doorbells, timers, semaphores, interrupt routing, microcode/scratch access, and SDMA/VM busy status. Important groups include:

- `GFX_PIPE_PRIORITY`, selecting high-priority graphics pipe behavior.
- `RLC_GPU_IOV_VF_ENABLE`, with `VF_ENABLE` and `VF_NUM` fields for SR-IOV function state.
- `RLC_GPU_IOV_CFG_REG*`, scheduler block metadata, command type/execute, function IDs, context size/location/offset, VM busy status, active function ID, and function-32 control/reset.
- `RLC_SDMA0_STATUS` through `RLC_SDMA7_STATUS` and matching busy-status registers for virtualization-visible SDMA state.
- `RLC_RLCV_TIMER_*` and `RLC_PACE_TIMER_STAT`, defining virtualized timer values, enable bits, auto-rearm, clear bits, and synchronized status.
- `RLC_GPU_IOV_VF_DOORBELL_STATUS`, `_SET`, `_CLR`, and `RLC_GPU_IOV_VF_MASK`, representing doorbell status and masks for VFs plus the PF bit.
- `RLC_HYP_SEMAPHORE_0..3`, exposing small `CLIENT_ID` fields for hypervisor-side synchronization.
- `RLC_GPU_IOV_INT_STAT`, `RLC_IH_COOKIE`, `RLC_IH_COOKIE_CNTL`, `RLC_GPU_IOV_INT_DISABLE`, `RLC_GPU_IOV_INT_FORCE`, and `RLC_GPU_IOV_SMU_RESPONSE`, which connect RLC virtualization state with interrupt handling and SMU responses.
- `RLC_HYP_RLCG_UCODE_CHKSUM`, `RLC_HYP_RLCP_UCODE_CHKSUM`, and `RLC_HYP_RLCV_UCODE_CHKSUM`, which expose microcode checksum fields.
- `RLC_GPU_IOV_UCODE_ADDR/DATA`, `RLC_GPM_UCODE_ADDR/DATA`, `RLC_PACE_UCODE_ADDR/DATA`, RLC IRAM/DRAM/ARAM accessors, LX6 scratch/IRAM/DRAM accessors, SRM accessors, and PACE/GPM scratch windows.

These macros back privileged flows. Many are only meaningful in PF, hypervisor, or firmware-loading contexts and should not be treated as ordinary graphics queue configuration.

### Pipe Steering, Harvesting, and User Configuration

`GL2_PIPE_STEER_0..3`, `GL1_PIPE_STEER`, and `CH_PIPE_STEER` map graphics pipes to GL2/GL1/cache channels. Each GL2 register packs four pipe-to-channel mappings for two quadrants, with 3-bit channel fields spaced every four bits. GL1 and CH steering use 2-bit fields per pipe.

`GC_USER_SHADER_ARRAY_CONFIG`, `GC_USER_PRIM_CONFIG`, `GC_USER_SA_UNIT_DISABLE`, `GC_USER_RB_REDUNDANCY`, `GC_USER_RB_BACKEND_DISABLE`, `GC_USER_RMI_REDUNDANCY`, `CGTS_USER_TCC_DISABLE`, and `GC_USER_SHADER_RATE_CONFIG` provide mask fields for harvested/disabled WGPs, primitive units, shader arrays, render backends, RMI repair, TCC disable state, and shader rate configuration. These registers are tied to fuse/harvest topology and user-visible graphics configuration. Wrong field programming can expose disabled units, hide valid units, or misroute traffic.

### Command Processor Hypervisor and Instruction/Data Cache Fields

The `gc_cphypdec` block defines command processor microcode and cache fields. It includes:

- Hypervisor and non-hypervisor PFP/ME/MEC address/data ports (`CP_HYP_PFP_UCODE_ADDR/DATA`, `CP_PFP_UCODE_ADDR/DATA`, `CP_HYP_ME_UCODE_ADDR/DATA`, `CP_ME_RAM_RADDR/WADDR/DATA`, `CP_HYP_MEC1/2_UCODE_ADDR/DATA`, and `CP_MEC_ME1/2_UCODE_ADDR/DATA`).
- Microcode checksum registers for PFP, ME, and MEC engines.
- PFP, ME, CPC, MES, MEC, and GFX RS64 instruction-cache/data-cache base low/high registers, bounds, VMID, cache policy, address clamp, execute disable, invalidation, invalidation-complete, prime, and primed bits.

Observed driver integration includes `amdgpu/gfx_v11_0.c`, which writes `regCP_HYP_PFP_UCODE_ADDR` while loading/querying PFP firmware state. The masks in this chunk describe how those address/data/checksum and cache-control registers are encoded for GC 11.0.3.

### GRBM Hypervisor and Per-VF Aperture Fields

The `gc_grbm_hypdec` block defines indirect selection/data fields for graphics register broadcast manager state:

- `GRBM_GFX_INDEX_SR_SELECT` selects index and PF/VF side through `VF_PF`.
- `GRBM_GFX_INDEX_SR_DATA` carries instance, shader array, shader engine, WGP, and broadcast flag fields.
- `GRBM_GFX_CNTL_SR_SELECT` and `GRBM_GFX_CNTL_SR_DATA` expose GRBM control selection/data.
- `GC_IH_COOKIE_0_PTR` and `GRBM_SE_REMAP_CNTL` define interrupt-cookie pointer and shader-engine remapping fields.

The `gc_gcvmsharedhvdec` block defines `GCMC_VM_FB_SIZE_OFFSET_VF0` through `VF15`, each with `VF_FB_SIZE` and `VF_FB_OFFSET` fields. These per-VF framebuffer aperture fields are part of virtualization memory partitioning.

### RLC Core Control, Timers, and Clock Counts

The `gc_rlcdec` block begins with `RLC_CNTL`, defining RLC enable, central queue enable, RLCM enable, SRM enable, clock-counter enable, sleep disable, save-and-restore enable, safe-mode enable, and invalidation behavior. Other covered RLC core fields include:

- `RLC_F32_UCODE_VERSION`, with version, breakpoint, and load-status fields.
- `RLC_STAT`, exposing request type, sleep, WFI, 3D-full, command-queue available, GFX clock off, and GPM idle state.
- `RLC_REFCLOCK_TIMESTAMP_LSB/MSB` and `RLC_GPU_CLOCK_COUNT_LSB/MSB`.
- `RLC_GPM_TIMER_INT_0..4`, `RLC_GPM_TIMER_CTRL`, and `RLC_GPM_TIMER_STAT`, providing five timer intervals, enable bits, auto-rearm bits, interrupt-clear bits, and synchronized status bits.
- `RLC_GPM_LEGACY_INT_STAT` and `RLC_GPM_LEGACY_INT_CLEAR`, covering SPP PVT interrupt changes, CP/RLC invalidation-pending changes, EOF, power-gating control changes, and a store/load timer expiry status.
- `RLC_INT_STAT`, with last CP/RLC interrupt ID and pending bit.
- `RLC_MGCG_CTRL` and `RLC_CLK_CNTL`, controlling medium-grain clock gating and clock-gating override domains.
- `RLC_JUMP_TABLE_RESTORE`, `RLC_PG_DELAY_2`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, and `RLC_UCODE_CNTL`.
- `RLC_GPM_THREAD_RESET`, `RLC_GPM_CP_DMA_COMPLETE_T0/T1`, and `RLC_GPM_THREAD_INVALIDATE_CACHE`, defining per-thread reset, DMA completion, and cache-invalidation command/status bits.
- `RLC_CLK_COUNT_GFXCLK_LSB/MSB` and `RLC_CLK_COUNT_REFCLK_LSB`. The chunk ends at the `RLC_CLK_COUNT_REFCLK_MSB` comment, so its actual field macros belong to the next chunk.

## Control Flow and State Behavior

This header has no runtime control flow. It affects driver behavior at compile time by determining how C code composes and decodes 32-bit MMIO register values.

The persistent state described by this chunk is hardware state, not software state in the header. Important hardware state includes performance counter event selection, RLC SPM ring base/size/pointers, accumulator RAM and status, RTAVFS target frequency/voltage requests, VF enablement and per-VF framebuffer aperture state, hypervisor semaphores and doorbell status, CP microcode address/data/checksum ports, CP cache base/bound/control registers, GRBM instance selection, harvest/pipe steering state, RLC enable/status/timers/interrupt state, and clock counters.

Some fields are latched status bits, some are sticky interrupt/status bits, and some are write-one or strobe-style command bits. Examples include SPM accumulator strobes, RTAVFS read/write enable bits, RLC timer interrupt-clear bits, doorbell set/clear fields, instruction-cache invalidate/prime bits, GPM thread reset and cache-invalidate bits, and GPU clock capture. Consumers must use the sequencing rules in the owning AMDGPU code and hardware specification; the macros alone do not encode ordering, polling, or timeout policy.

## Dependencies and Integration Points

The chunk depends on the generated AMD register-header convention:

- `gc_11_0_3_offset.h` supplies register addresses and base indices for the names defined here.
- `gc_11_0_3_default.h` supplies reset/default values where available.
- AMDGPU register helper macros consume `__SHIFT` and `_MASK` definitions to build register values without hard-coded bit positions.

Observed or implied integration points in this source tree include:

- `amdgpu/gfx_v11_0.c`, which writes command processor hypervisor microcode address registers such as `regCP_HYP_PFP_UCODE_ADDR` during GFX initialization/firmware handling.
- GFX RLC initialization paths across `gfx_v*_0.c`, which use `RLC_CNTL__RLC_ENABLE_F32_MASK`-style definitions to enable, stop, or query RLC firmware state.
- KFD and queue-management code for GFX 11, which includes GC 11 register headers and relies on CP/MEC/MES register definitions when configuring compute queues and firmware-visible queues.
- Virtualization and SR-IOV code paths that pair `RLC_GPU_IOV_*`, per-VF `GCMC_VM_FB_SIZE_OFFSET_VF*`, `GRBM_*_SR_*`, and doorbell/status masks with PF/VF scheduling and partitioning.
- Performance/debug tooling paths that configure block-local perf counters and RLC SPM through selector, muxsel, ring, accumulator, and status registers.

Cross-generation similarity is high but not exact. For example, older GC 9/10 headers expose similar RLC GPM timer and SPM fields with different layouts, and GC 12 changes some CP and RLC doorbell/cache fields. Consumers must include the matching GC 11.0.3 offset/mask/default set.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can write unrelated hardware fields, causing hangs, incorrect performance data, lost interrupts, firmware load failure, bad VF partitioning, or graphics/compute misconfiguration.
- Repeated performance counter families are easy to corrupt mechanically. Many blocks share similar names and layouts, but some counters omit `PERF_SEL1`, `CNTR_MODE`, or secondary select fields.
- RLC SPM and accumulator fields include both RAM address/data windows and strobe/status fields. Treating strobe bits as persistent configuration or missing busy/done/overflow polling can produce incomplete samples or deadlock debug flows.
- Virtualization fields are privilege-sensitive. Incorrect `VF_ENABLE`, `VF_NUM`, per-VF framebuffer aperture, doorbell, scheduler, or semaphore fields can break PF/VF isolation or scheduling.
- Power and frequency fields are not ordinary debug knobs. RTAVFS target frequency/voltage, PSM, soft-reset, and clock-control fields must remain coordinated with SMU and power-management policy.
- CP microcode and cache-control fields can affect firmware execution. Incorrect address widths, checksum handling, cache base/bounds, VMID, execute-disable, invalidate, or prime bits can prevent PFP/ME/MEC/MES firmware from running correctly.
- Harvest and steering fields must match actual hardware topology. Exposing disabled WGPs/RBs/TCCs or changing GL2/GL1/CH steering incorrectly can misroute traffic or cause hard-to-debug rendering faults.
- The chunk ends mid-family at `RLC_CLK_COUNT_REFCLK_MSB`; a final merged report must connect this document to the next chunk for the remaining clock-count and RLC doorbell fields.

## Test and Validation Signals

Useful validation is primarily build and integration coverage:

- Build AMDGPU, KFD, and display code paths that include `gc/gc_11_0_3_sh_mask.h`; this catches missing or renamed macros.
- GFX firmware-load tests should cover PFP/ME/MEC/MES address/data/checksum fields and CP instruction-cache/data-cache invalidation/prime behavior.
- RLC bring-up, suspend/resume, reset, and clock-gating tests should exercise `RLC_CNTL`, `RLC_STAT`, `RLC_MGCG_CTRL`, `RLC_CLK_CNTL`, timers, legacy interrupt status/clear, GPM thread reset, and clock counters.
- Performance-counter validation should verify block-local event selection for GDS/TA/TD/TCP/GL*/CH*/CB/DB/RLC/RMI/GCR/PA_PH/UTCL1/CHA/GUS and confirm CB filter fields restrict events as expected.
- RLC SPM tests should verify ring base/size/pointers, muxsel programming, accumulator mode/control/status, overflow reporting, pause/resume, and sample clock counts.
- SR-IOV validation should exercise VF enablement, function selection, per-VF framebuffer size/offset, doorbell set/clear/mask, scheduler state, SDMA busy/status, and interrupt cookie paths.
- Power-management or SMU-coordinated tests should confirm RTAVFS frequency/voltage requests, read/write acknowledge bits, and EDC hysteresis status do not regress.

## Unresolved Cross-Chunk References

This chunk starts after `GDS_PERFCOUNTER3_SELECT` has already begun and therefore does not include that register's comment or all of its field definitions. It also ends exactly at the `RLC_CLK_COUNT_REFCLK_MSB` comment and does not include the `COUNTER` shift/mask for that register or the following `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, and `RLC_RLCG_DOORBELL_CNTL` fields. The merge/reconciliation lane should stitch this chunk to adjacent chunks to describe complete register families.

### subset-b-002541: lines 37499-39973

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 37499-39973

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for 32-bit register packing and decoding. There are no functions, structs, enums, global variables, includes, allocations, locks, callbacks, loops, or branches in this range.

The selected lines cover a large RLC and RLCS register-map span. The range begins in the tail of `RLC_CLK_COUNT_REFCLK_MSB` and then defines fields for RLC clock counters, multiple RLC doorbell endpoints, graphics power gating, clock gating, GPM/SRM control, UTCL1 fault/status reporting, shader profiler/SPP state, residency counters, graphics interrupt-handler client status, RLC Xtensa-style control/interrupt vectors, CPAXI doorbell monitoring, SMU/RLC command mailboxes, IMU bootload controls, and the start of the `gc_rlcsdec` address block. It ends at the first shift macro for `RLC_RLCS_GPM_LEGACY_INT_DISABLE`; that register's masks continue in the adjacent following chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 11.0.3 graphics IP block and is not Ceph filesystem logic.

## Purpose

`gc_11_0_3_sh_mask.h` supplies bit layouts for GC 11.0.3 registers. AMDGPU code pairs these field definitions with register address macros from the companion `gc_11_0_3_offset.h` header, then uses helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to manipulate MMIO registers without hard-coded bit positions.

This chunk's purpose is to describe the RLC control-plane surface:

- RLC clock measurement and capture fields for GFXCLK, REFCLK, GPU clock counters, SPM clock counters, and capture-valid/status bits.
- Doorbell range/control/status/data windows for several RLC clients: `RLC_RLCG`, `RLC_RLCV`, `RLC_RLCP`, and `RLC_XT`, plus CPAXI doorbell monitor control/status/data fields.
- Graphics power-gating, clock-gating, light-sleep/deep-sleep, WGP power status, dynamic/static WGP power-gating masks, per-WGP limits, power-brake controls, memory sleep, and residency counters.
- GPM and SRM command/control surfaces, including thread priorities/enables, GPM general scratch registers, SRM index-control address/data slots, SRM command status, SRM GPM command/abort fields, and RLC save/restore helper registers.
- UTCL1 translation control and diagnostics for GPM threads and SPM, including XNACK redo timers, drop/bypass/invalidate/fragment-limit/force-snoop controls, busy/stall indicators, translated request error VMID, and split error addresses.
- RLC shader profiling/SPP fields for profile enablement, SSF capture, thresholds, inflight reads, global shader ID selection, private counters, PBB override information, CAM access, and SPP reset/stall/status.
- RLC interrupt and fault monitoring, including FED status, graphics IH client buffers, PACE interrupts, legacy GPM interrupts, CP status invalidation, firewall violation, FED/EDC event clears, and GRBM idle/busy interrupt control.
- RLC firmware/embedded-controller handshakes, including SMU safe-mode mailboxes, RLCV command, SMU messages/arguments, IMU bootload address/size/misc/reset-vector fields, bootload status, bootload ID status bitmaps, and IMU voltage-change controls.
- The RLCS decoder block for exception/auxiliary register addresses, clock/deep-sleep controls, GPM state, aborted power-down sequence reporting, IOV command/status fields, WGP reads, CP/SPM interrupt information, DSM trigger, GRBM soft reset, and KMD log scratch fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register addresses live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` with names such as `regRLC_PG_CNTL`, `regRLC_RLCG_DOORBELL_CNTL`, `regRLC_SMU_SAFE_MODE`, `regRLC_IMU_MISC`, `regRLC_RLCS_GPM_STAT`, and `regRLC_RLCS_GRBM_SOFT_RESET`.

Major macro families in this slice are:

- Clock and residency: `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, `RLC_GPU_CLOCK_32`, `RLC_CAPTURE_GPU_CLOCK_COUNT_*`, `RLC_GPU_CLOCK_COUNT_*`, `RLC_GPU_CLOCK_COUNT_SPM_*`, and `RLC_*_RESIDENCY_{CNTR_CTRL,EVENT_CNTR,REF_CNTR}`. Control fields include run/reset/sample, enable/reset/ack/overflow, event select for PCC, and full-width event/reference counter data.
- Power and clock gating: `RLC_PG_CNTL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, `RLC_CGCG_RAMP_CTRL`, `RLC_CGCG_CGLS_CTRL_3D`, `RLC_CGCG_RAMP_CTRL_3D`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_PG_DELAY`, `RLC_PG_DELAY_3`, `RLC_WGP_STATUS`, `RLC_PG_ALWAYS_ON_WGP_MASK`, `RLC_MAX_PG_WGP`, `RLC_AUTO_PG_CTRL`, `RLC_STATIC_PG_STATUS`, `RLC_MEM_SLP_CNTL`, `RLC_RLCS_SOC_DS_CNTL`, `RLC_RLCS_GFX_DS_CNTL`, `RLC_RLCS_GFX_DS_ALLOW_MASK_CNTL`, `RLC_RLCS_POWER_BRAKE_CNTL`, and `RLC_RLCS_POWER_BRAKE_CNTL_TH1`.
- Doorbells and monitoring: `RLC_RLCG_DOORBELL_*`, `RLC_RLCV_DOORBELL_*`, `RLC_RLCP_DOORBELL_*`, `RLC_XT_DOORBELL_*`, and `RLC_CPAXI_DOORBELL_MON_*`. These expose lower/upper range fields, per-doorbell modes, doorbell ID and ID enable bits, per-doorbell valid bits, and low/high captured data words.
- GPM/SRM and scratch state: `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, `RLC_GPM_GENERAL_0..16`, `RLC_GPM_INT_DISABLE_TH0`, `RLC_GPM_INT_FORCE_TH0`, `RLC_GPM_INT_STAT_TH0`, `RLC_GPR_REG1/2`, `RLC_SRM_CNTL`, `RLC_SRM_GPM_COMMAND_STATUS`, `RLC_SRM_INDEX_CNTL_ADDR_0..7`, `RLC_SRM_INDEX_CNTL_DATA_0..7`, `RLC_SRM_STAT`, `RLC_SRM_GPM_COMMAND`, and `RLC_SRM_GPM_ABORT`.
- UTCL1 and translation errors: `RLC_GPM_UTCL1_CNTL_0..2`, `RLC_SPM_UTCL1_CNTL`, `RLC_UTCL1_STATUS`, `RLC_UTCL1_STATUS_2`, `RLC_SPM_UTCL1_ERROR_1/2`, and `RLC_GPM_UTCL1_TH0/TH1/TH2_ERROR_1/2`. These cover XNACK retry tuning, cache/TLB invalidation-style controls, fault/retry/PRT identifiers, busy/stall indicators, translated request error classes, VMID, and address fragments.
- SPP and profiling: `RLC_SPP_CTRL`, `RLC_SPP_SHADER_PROFILE_EN`, `RLC_SPP_SSF_CAPTURE_EN`, `RLC_SPP_SSF_THRESHOLD_*`, `RLC_SPP_INFLIGHT_RD_*`, `RLC_SPP_PROF_INFO_*`, `RLC_SPP_GLOBAL_SH_ID`, `RLC_SPP_GLOBAL_SH_ID_VALID`, `RLC_SPP_STATUS`, `RLC_SPP_PVT_STAT_*`, `RLC_SPP_PVT_LEVEL_MAX`, `RLC_SPP_STALL_STATE_UPDATE`, `RLC_SPP_PBB_INFO`, `RLC_SPP_RESET`, `RLC_SPP_CAM_*`, and `RLC_SPP_CAM_EXT_*`.
- Interrupt/fault/status: `RLC_RLCS_FED_STATUS_0/1`, `RLC_PACE_INT_STAT`, `RLC_PACE_INT_DISABLE`, `RLC_FIREWALL_VIOLATION`, `RLC_CP_STAT_INVAL_STAT`, `RLC_CP_STAT_INVAL_CTRL`, `RLC_GFX_IH_CLIENT_CTRL`, `RLC_GFX_IH_ARBITER_STAT`, `RLC_GFX_IH_CLIENT_SE_STAT_L/H`, `RLC_GFX_IH_CLIENT_SDMA_STAT`, `RLC_GFX_IH_CLIENT_OTHER_STAT`, `RLC_RLCS_IH_SEMAPHORE`, `RLC_RLCS_IH_COOKIE_SEMAPHORE`, `RLC_RLCS_CP_INT_CTRL_*`, `RLC_RLCS_CP_INT_INFO_*`, `RLC_RLCS_SPM_INT_CTRL`, `RLC_RLCS_SPM_INT_INFO_*`, `RLC_RLCS_EDC_INT_CNTL`, and `RLC_RLCS_GPM_LEGACY_INT_STAT`.
- Firmware, IMU, and RLCS decoder: `SMU_RLC_RESPONSE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `RLC_RLCV_COMMAND`, `RLC_SMU_MESSAGE*`, `RLC_SMU_COMMAND`, `RLC_SMU_ARGUMENT_1..5`, `RLC_IMU_BOOTLOAD_ADDR_HI/LO`, `RLC_IMU_BOOTLOAD_SIZE`, `RLC_IMU_MISC`, `RLC_IMU_RESET_VECTOR`, `RLC_RLCS_EXCEPTION_REG_1..4`, `RLC_RLCS_CGCG_REQUEST/STATUS`, `RLC_GPM_STAT`, `RLC_RLCS_GPM_STAT`, `RLC_RLCS_ABORTED_PD_SEQUENCE`, `RLC_RLCS_DIDT_FORCE_STALL`, `RLC_RLCS_IOV_*`, `RLC_RLCS_WGP_*`, `RLC_RLCS_GRBM_*`, `RLC_RLCS_BOOTLOAD_STATUS`, `RLC_RLCS_BOOTLOAD_ID_STATUS1/2`, `RLC_RLCS_IMU_VIDCHG_CNTL`, `RLC_RLCS_KMD_LOG_CNTL1/2`, and related auxiliary registers.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.0.3 register headers for the active ASIC generation.
2. Use a matching register address macro from `gc_11_0_3_offset.h`.
3. Read an existing register value, prepare a write value, or decode a debug/status snapshot.
4. Use the `__SHIFT` and `__MASK` pairs, normally through register field helpers, to set or extract a field.
5. Issue the MMIO read/write or consume the decoded result in RLC bring-up, power management, firmware boot, doorbell setup, hang recovery, perf/debug plumbing, or virtualization/error handling.

For power-management flows, driver code reads or updates fields such as `RLC_PG_CNTL__GFX_POWER_GATING_ENABLE_MASK`, `RLC_PG_CNTL__SMU_HANDSHAKE_DISABLE_MASK`, `RLC_MEM_SLP_CNTL__RLC_MEM_LS_EN_MASK`, residency counter enables, and RLC/RLCS GPM status bits while enabling/disabling RLC-managed power features or waiting for power transitions. For boot flows, driver code polls `RLC_RLCS_BOOTLOAD_STATUS` fields such as bootload completion and uses IMU address/size/reset-vector fields around firmware loading. For interrupt and fault flows, code snapshots FED/IH/UTCL1/firewall/GRBM/CP/SPM fields and may write clear or disable masks. The header does not encode required sequencing, timeouts, posting reads, clear-on-write behavior, or reset delays.

## State And Persistence Behavior

The macros are stateless and persist nothing. They describe state owned by GPU hardware, firmware, and AMDGPU's runtime register programming.

RLC power-control fields are persistent hardware configuration until overwritten, reset, or lost through a relevant power state. `RLC_PG_CNTL`, clock-gating controls, WGP masks, memory sleep controls, deep-sleep allow masks, and power-brake controls directly affect whether graphics blocks can be power-gated, clock-gated, slowed down, or held active. Incorrect values can leave the graphics engine powered when it should idle, gate clocks while work is active, or block the SMU/RLC handshake path.

Doorbell range/control/data registers define live notification routing for multiple RLC clients. Range fields use aligned lower/upper address fragments, while control fields select per-doorbell modes and optional doorbell IDs. Captured data registers and valid bits are diagnostic state that can remain latched until cleared or overwritten by hardware. Misprogrammed ranges or IDs can route notifications to the wrong RLC client or make firmware appear unresponsive.

GPM/SRM general registers, KMD log controls, scratch-style data fields, auxiliary register address fields, SRM index-control slots, and R2I controls are generic RLC-owned state. Some are used by firmware command engines, profiling support, diagnostics, or save/restore paths. Because they are full-width or address-like fields, preserving ownership boundaries matters: host code should not assume unused-looking scratch registers are free unless the RLC firmware interface documents them.

UTCL1 status and error registers represent live or sticky memory-translation events for SPM and GPM threads. Fault, retry, PRT, VMID, UTCL1 ID, and translated address fragments are diagnostic state used to attribute translation failures. These fields may be volatile during ongoing traffic and may require a documented clear sequence outside this header.

SPP/profiling registers maintain profiler mode, selected shader IDs, thresholds, capture enablement, private level counters, CAM access, and reset/stall state. These settings can perturb profiling or debug collection if left configured across suspend/resume, GPU reset, or context transitions.

Residency counters and GPU clock counters accumulate event/reference data while enabled. Their reset/enable acknowledgements and overflow bits indicate hardware state transitions. The header cannot express counter latching or atomic high/low read requirements, so consumers must follow the hardware programming sequence when sampling.

Firmware and IMU registers are high-risk state. Bootload address/size, reset vector, safe-mode commands, SMU command/argument mailboxes, bootload status, bootload ID status, and voltage-change request/ack bits participate in firmware control and power/voltage transitions. Stale or malformed values can hang RLC boot, wedge SMU communication, or report the wrong firmware-load state.

Reserved fields appear throughout this generated map. Runtime read-modify-write code should preserve reserved bits unless the hardware sequence explicitly requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register family remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies the matching `reg...` addresses and base indices for the fields defined here.
- AMDGPU register helpers and SOC15 accessors provide the actual field packing/extraction and MMIO access.
- `drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c` and neighboring generation files use the same RLC field families for RLC power gating, SMU handshake disablement, bootload polling, memory sleep, and graphics bring-up/teardown flows.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.h` defines RLC firmware-related identifiers, including SPP/CAM firmware ID concepts that correspond to profiler and RLC firmware state exposed in this chunk.
- Power-management, reset, suspend/resume, GPU hang recovery, debugfs/register-dump, RAS/fault reporting, SR-IOV/IOV handling, KFD/compute interaction, and shader profiling paths all integrate with this register surface.

Practical integration points include enabling/disabling RLC-managed GFX power gating, configuring SMU handshake behavior, validating RLC bootload completion, programming RLC memory sleep, collecting residency statistics, routing and validating RLC doorbells, reporting UTCL1 translation faults, using SPP profiling controls, clearing graphics IH/RLC legacy interrupts, commanding SRM/GPM save/restore operations, and decoding RLCS GRBM idle/busy or soft-reset state during reset recovery.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but can write the wrong hardware bit or decode misleading power/fault state.
- This chunk starts and ends mid-family. It begins after the `RLC_CLK_COUNT_REFCLK_MSB` register comment and ends before the masks for `RLC_RLCS_GPM_LEGACY_INT_DISABLE`; final file-level research must merge adjacent chunks for those partial families.
- Many register families are structurally repeated: RLCG/RLCV/RLCP/XT doorbells, GPM UTCL1 thread controls/errors, residency counter controls, graphics IH client status per SE/SDMA group, and bootload ID bitmaps. Single-bit generator mistakes in one repeated family can create client-specific failures that are hard to spot.
- Address and range fields often omit alignment bits or split addresses across low/high registers. Treating masked fields as raw byte addresses can program plausible but wrong doorbell ranges, IMU bootload locations, exception/auxiliary addresses, or UTCL1 error addresses.
- RLC power-gating and clock-gating fields have side effects. Incorrect `RLC_PG_CNTL`, deep-sleep allow masks, WGP power masks, memory sleep controls, or power-brake fields can cause GPU hangs, missed idle transitions, high idle power, or failed resume.
- Doorbell control and CPAXI monitor fields affect live notification paths. Misdecoded doorbell IDs, modes, or match-clear behavior can make firmware commands look lost or can clear diagnostic evidence too early.
- Interrupt and fault status fields may be sticky or write-one-to-clear depending on the register. The shift/mask header cannot express clear semantics, so blindly writing masks can drop evidence or fail to clear an interrupt.
- UTCL1 and FED status fields are high-value diagnostics for memory and fabric failures. Misattributing VMID, UTCL1 ID, SDMA/FED source, or translated address bits can send debugging toward the wrong process or engine.
- Firmware/IMU mailboxes are sequencing-sensitive. Polling the wrong bootload bit, using the wrong size mask, or writing safe-mode/voltage-change fields without the expected handshake can wedge firmware bring-up.
- Counter sampling is race-prone. GPU clock and residency high/low or event/reference counters need hardware-defined latching behavior; masks alone do not make reads atomic.
- Reserved fields are large in several registers. Full-register writes that do not preserve reserved bits can change undocumented ASIC or firmware behavior.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware/runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_11_0_3_sh_mask.h`, especially GC 11 RLC, GFX, power-management, reset, debug, profiling, and firmware paths.
- Mechanical comparison against AMD's authoritative GC 11.0.3 register database to verify every `__SHIFT` and `__MASK` value in lines 37499-39973.
- Cross-check that every complete register family in this chunk has a matching address macro in `gc_11_0_3_offset.h`; note that a `gc_11_0_3_default.h` file was not present in this checkout.
- Static shift/mask sanity checks: masks align with shifts, full-width data fields use `0xFFFFFFFFL`, repeated doorbell/residency/UTCL1/IH families remain structurally consistent, and reserved masks cover the intended unused bits without overlapping named fields.
- RLC boot tests that load firmware and poll `RLC_RLCS_BOOTLOAD_STATUS`, `RLC_RLCS_BOOTLOAD_ID_STATUS1/2`, IMU bootload address/size, and reset-vector fields without timeout.
- Power-management tests that enable and disable GFX power gating, memory light sleep/deep sleep, SMU handshake behavior, clock-gating ramps, WGP power transitions, power-brake events, and residency counters across suspend/resume and GPU reset.
- Doorbell tests that validate RLCG/RLCV/RLCP/XT doorbell range, ID, valid, and captured-data fields under firmware command traffic and CPAXI monitor match/clear scenarios.
- Fault-injection or stress tests that trigger UTCL1 translated request errors, FED errors, firewall violations, graphics IH buffer overflow/protocol errors, CP/SPM interrupts, and GRBM idle/busy interrupt paths, then confirm decoded VMID/source/address/status fields are coherent.
- Shader profiling/SPP tests that toggle profile enablement, shader ID selection, SSF capture thresholds, CAM access, PVT counters, stall-state update, and reset fields while verifying expected profiler output.
- Hang/debug dump tests that collect RLC GPM/RLCS GPM status, GRBM idle/busy state, soft reset fields, CP invalidation status, KMD logs, and legacy interrupts during known idle, busy, reset, and fault conditions.
- Runtime warning signals include RLC boot timeouts, failed SMU safe-mode handshakes, GPU reset loops, high idle power, doorbell command loss, stuck residency counters, incorrect IH/fault attribution, impossible GPM status combinations, failed memory sleep restore, or shader profiling data that remains stale after reset.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002541`. It covers lines 37499-39973 of `gc_11_0_3_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial clock-count and `RLC_RLCS_GPM_LEGACY_INT_DISABLE` families and to place these RLC/RLCS definitions in the full GC 11.0.3 register map.

### subset-b-002542: lines 39974-42401

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 39974-42401

## Scope

This chunk is a generated AMD GC 11.0.3 shift/mask register-header segment. It contains preprocessor constants only: each hardware register field is represented by a `__SHIFT` macro and a matching `__MASK` macro used by AMDGPU register helpers to pack and unpack 32-bit register values. There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, branches, or direct MMIO operations in this range.

The selected lines start in the middle of `RLC_RLCS_GPM_LEGACY_INT_DISABLE`, immediately after the first field shift from the preceding chunk. They then finish the tail of the `gc_rlc_rlcsdec` register-field map, cover the full visible `gc_pfvfdec_rlc`, `gc_pwrdec`, and `gc_pspdec` address-block sections, and enter the `gc_gfx_imu_gfx_imudec` block. The chunk ends after the first two `GFX_IMU_DPM_CONTROL` shifts; the remaining `GFX_IMU_DPM_CONTROL` masks and later GFX IMU RAM fields continue in the next adjacent chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM register metadata for the GC 11.0.3 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gc_11_0_3_sh_mask.h` supplies bit layouts for GC 11.0.3 registers. Driver code pairs these macros with register addresses from the matching `gc_11_0_3_offset.h` header and uses helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to set or decode a named field without embedding raw bit positions and masks.

This chunk concentrates on RLC/RLCS control and telemetry, power-clock gating controls, PSP-visible graphics debug/security windows, and graphics IMU mailboxes and interrupt plumbing:

- RLC/RLCS global power-management interrupt, graphics-command-response, UTCL2 override, IMU/RLC message, telemetry, RAM-access, doorbell-fence, SDMA interrupt, clock-gating, memory-power, IH, and decode-end fields.
- RLC PF/VF decode fields for safe mode, streaming performance monitor sampling and interrupt reporting, command-submission instruction-buffer address/length, CP scheduler masks, EOF/spare interrupt counters, and PACE/RLCV spare interrupt state.
- Graphics power decode fields for CGTT/CGCG/ICG/MGCG controls across TCC, SPI, VGT, IA, WD, GS/NGG, PA, SC, SQ, TA, DB, CB, CP, CPF, CPC, RLC, GCEA, GL1/GL2, CHI/CHR, GUS, PH, UTCL1, and LDS/CHC/CHCG blocks.
- PSP decode fields for CP MES/MEC/GFX RS64 debug-memory indexed access, CPG/CPC PSP debug control, GRBM IOV error FIFO, GRBM security and CAM/HYP_CAM indexed data, and first RLC firmware-log violation address capture.
- Graphics IMU decode fields for 48 C2P mailbox messages, mailbox access controls, power-management IRQ control, MP1/RLC mutex and command/data/status exchange, SOC request path, VF control, telemetry, scratch registers, timestamp offset registers, core/PIC interrupt masks/levels/edges/priorities/status, interrupt-handler metadata, VID change, clock bypass, clock control, doorbell control, RLC clock-gating/throttle/reset-vector/override, and the beginning of DPM accumulator control.

## Important APIs, Types, And Macros

There are no callable APIs or C data types. The public surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field low-bit position.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the field.
- Register address symbols live in companion generated headers, usually as `mm...` constants in `gc_11_0_3_offset.h`.
- Consumers normally combine address macros and shift/mask macros through AMDGPU register helpers, MMIO read/modify/write paths, firmware message code, reset flows, virtualization handling, perf monitoring, and debug dumps.

The main macro families in this slice are:

- `RLC_RLCS_*`: RLCS-side controls for source IDs, `GCR_DATA_0..3` phase payloads, `GCR_STATUS` busy/out-count/response tag, perfmon clock state, UTCL2 GPA/VF and permission overrides, IMU-to-RLC and RLC-to-IMU mailbox data/control/toggle bits, telemetry current/voltage/temperature, mutex acquire state, gfxoff/deep-sleep status, IMU RAM address/data request toggles, GFX doorbell fence acknowledgement, SDMA interrupt auto-ack/status/info, PMM CGCG control, graphics memory power control and RM control, interrupt-handler context/ring/VM/source/VF metadata, and `RLC_RLCS_DEC_END`.
- `RLC_*` in `gc_pfvfdec_rlc`: `RLC_SAFE_MODE`, SPM sample and memory-controller controls, SPM interrupt control/status/info, CSIB address and length, CP scheduler bitmap, EOF interrupt status/count, spare interrupt counters, and PACE/RLCV spare interrupt state.
- `CGTT_*`, `CGTX_*`, `CGTS_*`, `ICG_*`, `GFX_ICG_*`, `*_CGTT_*`, `*_CLK_CTRL`, and `*_MGCG_OVERRIDE`: power and clock gating fields. These typically expose override, disable, delay, threshold, hysteresis, force-on, and per-subblock gating controls for graphics front-end, shader, texture, LDS, cache, primitive, color/depth, command-processor, RLC, GL1/GL2, and UTCL1 blocks.
- `CP_*_DM_INDEX_*`, `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, `GRBM_*`, and `RLC_FWL_FIRST_VIOL_ADDR`: PSP-facing indexed debug-memory controls, PSP debug enable/index fields, GRBM IOV/security/CAM data windows, hypervisor CAM data windows, and first firmware-log violation address capture.
- `GFX_IMU_C2PMSG_*`: 48 full-width command-to-power mailbox registers, plus access-control bitmaps that gate who may read or write groups of C2P messages.
- `GFX_IMU_*` mailbox, status, telemetry, scratch, timestamp, interrupt, IH, power, and RLC-interaction registers: full-width data/status fields, request/ack/change/done toggles, mutex request/acquire bits, VF enable/ID state, telemetry current/voltage/temperature, scratch data, GTS timestamp offset low/high words, PIC interrupt mask/level/edge/priority/status, IH context/ring/VM/source/VF metadata, VID-change request/ack/data/source fields, clock-bypass/divider/cooldown fields, doorbell fence override/status, RLC reset-vector exit source, and DPM accumulator start/reset fields.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.0.3 register address and shift/mask headers for the active ASIC generation.
2. Read a hardware register, prepare a register write value, or assemble an indexed/debug access payload.
3. Use the generated `__SHIFT` and `__MASK` pairs, often through field helpers, to pack one field into a register value or extract one field from a status value.
4. Write the value through AMDGPU MMIO/indexed-register paths, mailbox paths, reset/power-management routines, PSP/RLC/IMU message code, or debug/perf reporting code.
5. For status paths, decode returned bits into idle-wait decisions, interrupt handling, telemetry, virtualization attribution, power-state decisions, or diagnostic output.

For the RLC/RLCS and GFX IMU message registers, higher-level control flow is handshake-oriented: one side writes data/control registers, toggles a change/request bit, and polls or receives an indication through done/ack/status bits. For SPM and DPM counters, software configures sampling or accumulation, starts or resets counting, then reads status/result fields. For clock/power gates, code applies masks as part of ASIC bring-up, power-management transitions, firmware sequencing, or debug overrides. This header does not define required ordering, polling intervals, reset defaults, clear-on-read behavior, or firmware ownership rules.

## State And Persistence Behavior

The macros are stateless and persist nothing. They describe stateful hardware registers owned by the GPU, firmware, PSP, RLC, IMU, power-management logic, virtualization fabric, and AMDGPU runtime.

RLC/RLCS message, mutex, RAM-access, doorbell-fence, and status fields represent live firmware and hardware coordination state. Toggle fields such as `CHGTOG`, `DONETOG`, `REQTOG`, and `ACKTOG` are especially order-sensitive: missing an edge or writing a stale toggle value can make a mailbox or RAM transaction appear stuck. Status bits such as `ALLOW_GFXOFF`, `ALLOW_FA_DCS`, `DISABLE_GFXCLK_DS`, `PWR_DOWN_ACTIVE`, and `RLC_ALIVE` are volatile and should be decoded as snapshots rather than persistent software state.

The PF/VF RLC decode registers include virtualization- and interrupt-facing state. Safe-mode, scheduler, EOF, spare interrupt, and SPM fields may influence or report behavior across physical and virtual functions. Fields that count or latch interrupt events can require explicit clear sequences not expressible in a shift/mask header.

Clock-gating and memory-power registers persist programmed power policy until firmware or driver code changes them, or until reset/power gating restores defaults. Many fields are overrides or disables rather than passive status. Incorrect full-register writes can force clocks on, disable low-power states, or gate clocks while a block is active.

PSP debug, GRBM security, CAM, HYP_CAM, and firmware-log violation registers are sensitive diagnostic and isolation state. Indexed access windows depend on a correct index/data sequence. IOV, security, and violation fields may be sticky or privilege-controlled, and stale values can misattribute a security or virtualization fault.

GFX IMU C2P mailbox, RLC command, SOC request, VF control, telemetry, scratch, GTS offset, interrupt-controller, IH, VID-change, clock, doorbell, and reset-vector fields describe live communication and power-management state. Scratch and timestamp offset registers can act as persistent firmware/driver rendezvous storage while the IMU is running. Interrupt mask/level/edge/priority state persists configured routing until changed, and `GFX_IMU_PIC_INT_STATUS` exposes volatile pending status bits. The chunk-ending `GFX_IMU_DPM_CONTROL` fields are incomplete here; the masks and result counters are in the next chunk.

Reserved masks appear throughout the chunk. Callers should preserve reserved bits during read-modify-write unless the hardware programming sequence explicitly requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register family remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` supplies matching register addresses.
- The matching generated default/reset-value header, where present, supplies expected defaults for many of these registers.
- AMDGPU common register helpers provide field packing/extraction and MMIO/indexed-register access.
- RLC, GFXOFF, clock/power management, PSP, SR-IOV, interrupt handling, perf/telemetry, debugfs, hang-dump, and reset code depend on the exact field positions.

Key integration points include RLC firmware mailbox handling, IMU/RLC command exchange, RLC RAM indexed access, SDMA-to-RLC interrupt acknowledgement, SPM sampling and interrupt reporting, command-submission instruction-buffer setup, CP scheduler and EOF signaling, graphics clock-gating programming, memory-power control, PSP debug-memory access, GRBM IOV/security fault reporting, GRBM CAM/HYP_CAM inspection, IMU C2P mailbox communication with power firmware, MP1/IMU mutex handling, SOC request forwarding, VF control in virtualized environments, telemetry collection, timestamp calibration, IMU interrupt routing, IMU-originated IH packets, VID-change requests, doorbell fence override/status, RLC reset-vector selection, and DPM accumulation.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but can write a different hardware field or decode misleading state.
- This chunk starts and ends mid-register family. `RLC_RLCS_GPM_LEGACY_INT_DISABLE__GC_CAC_EDC_EVENT_CHANGED__SHIFT` is in the previous chunk, and `GFX_IMU_DPM_CONTROL` masks are in the next chunk. File-level analysis must reconcile adjacent chunks.
- Toggle-based handshakes are easy to misuse. `CHGTOG`/`DONETOG`, `REQTOG`/`ACKTOG`, and request/ack fields need edge-aware consumers; simply writing a constant field value can deadlock communication.
- Clock-gating and memory-power fields are high-impact side-effect registers. Bad masks can cause hangs, excessive power draw, failed gfxoff entry, or blocks being gated while active.
- Virtualization and security registers need exact VF/VFID/source attribution. Misdecoded PF/VF, CAM, HYP_CAM, IOV, or violation-address fields can send reset or fault handling to the wrong function.
- Indexed debug windows require correct index/data sequencing. Mixing up CP MES, MEC, GFX RS64, GRBM CAM, and HYP_CAM indices can return plausible but unrelated data.
- Full-width mailbox, scratch, and data registers use `0xFFFFFFFFL`; partial writes through the wrong helper can lose firmware payload bits.
- Interrupt mask/level/edge/priority programming is persistent. Incorrect priority or polarity fields can hide IMU events, create repeated interrupts, or route IH packets with wrong source/context metadata.
- Address and timestamp high/low register pairs can be race-prone if read or written without documented latching or ordering. The shift/mask header cannot express atomicity requirements.
- Reserved fields are numerous. Writes that fail to preserve reserved bits may change undocumented firmware or ASIC behavior.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_0_3_sh_mask.h`, especially RLC, GFXOFF, power-management, PSP, virtualization, interrupt, and telemetry paths.
- Mechanical comparison against AMD's authoritative GC 11.0.3 register database for every `__SHIFT` and `__MASK` in lines 39974-42401.
- Cross-checks that each register comment in this chunk has a corresponding address macro in `gc_11_0_3_offset.h` and, where expected, a default/reset value in the generated default header.
- Static shift/mask sanity checks: masks align with shifts, fields in the same register do not overlap unless documented, full-width data fields use `0xFFFFFFFFL`, low/high address pairs have consistent widths, and reserved masks fill only unused bits.
- RLC/IMU mailbox tests that send messages both directions and verify change/done/request/ack toggles, mutex acquire behavior, status transitions, and timeout handling.
- RLC RAM-access and GCR tests that validate request/ack completion, phase data packing, busy/out-count status, and response tags.
- GFXOFF and power-management tests that exercise `ALLOW_GFXOFF`, deep-sleep disable, graphics memory power control, clock-gating overrides, VID change, DPM accumulator start/reset, and post-resume restore.
- SPM and telemetry tests that configure sampling/interrupts, collect current/voltage/temperature data, and verify interrupt status/info fields under controlled workloads.
- PSP/debug tests that use CP MES/MEC/GFX RS64 indexed access and GRBM CAM/HYP_CAM windows, validating index/data sequencing and privilege restrictions.
- SR-IOV tests that trigger VF reset, IOV/security errors, doorbell fence behavior, and violation logging, then confirm source/VF/VM attribution.
- Interrupt tests that vary IMU PIC mask, level, edge, priority, status, and IH metadata fields, then confirm expected interrupt routing and clearing.
- Runtime warning signals include stuck RLC/IMU mailbox toggles, failed gfxoff entry, unexpected power draw, SDMA/RLC interrupt timeouts, missing telemetry, wrong PSP debug data, repeated IMU interrupts, invalid VF attribution, GRBM security violations with impossible source IDs, or GPU reset loops after clock/power programming.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002542`. It covers lines 39974-42401 of `gc_11_0_3_sh_mask.h`. The final per-file research should merge it with adjacent chunks to complete the partial `RLC_RLCS_GPM_LEGACY_INT_DISABLE` and `GFX_IMU_DPM_CONTROL` families and to place the RLC/RLCS, PF/VF RLC, power decode, PSP decode, and GFX IMU definitions in the full GC 11.0.3 register map.

### subset-b-002543: lines 42402-44690

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 42402-44690

## Scope

This chunk is the final generated shift/mask segment of the AMD GC 11.0.3 graphics register header. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` macro and a matching `__MASK` macro for 32-bit register composition and decoding. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the middle of `GFX_IMU_DPM_CONTROL` with the `BUSY_MASK` shift and the full mask set for that register. They then cover GFX IMU counters, RLC RAM windows, fence/debug/reset/isolation/timer/fuse/RAM/bootloader fields, GC and SE CAC accumulator and transition-table fields, the full `grtavfsind` RTAVFS register block from `RTAVFS_REG0` through `RTAVFS_REG194`, and the `sqind` shader-queue debug and wave-state registers. The chunk ends at the `SQ_WAVE_EXEC_HI` field definitions and the file's closing `#endif`.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 11.0.3 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gc_11_0_3_sh_mask.h` supplies bit layouts for GC 11.0.3 registers. Driver code pairs these macros with register addresses from the matching `gc_11_0_3_offset.h` header and uses register helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` to write or decode individual fields without open-coded bit positions.

This chunk focuses on low-level firmware/power/debug register metadata rather than packet parsing or normal filesystem control flow:

- GFX IMU controls for DPM accumulation, RLC RAM indexed access, fence logging, core control/status, power-good/reset/isolation sequencing, timers, fuse overrides, data/instruction RAM windows, interrupt-handler gasket state, and PSP-decoded bootloader address/size fields.
- GC CAC and SE CAC fields for block/signal selection, threshold programming, per-block 32-bit accumulators, stall/release/power-break lookup tables, fixed-pattern counters, and hardware LUT update status.
- RTAVFS fields for adaptive voltage/frequency sensing: zone start/stop counts, zone enable bitmaps, voltage/frequency pairs, guardband zone selection, CPO averaging/divider weights, ripple-counter controls and readouts, target/current frequency count overrides, PI/binary-search voltage code outputs, stop/debug states, and final scaled/count status.
- SQ indexed fields for local shader-queue debug status/control, wave active/idle slots, wave execution mode/status/trap state, VGPR/LDS allocation, instruction-buffer wait counters, program counter, flat scratch base, hardware IDs, POPS packer state, scheduling mode, shader cycle count, trap temporary registers, `M0`, and `EXEC` masks.

## Important APIs, Types, And Macros

There are no callable APIs or C data types in this chunk. The interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register address macros are expected in `gc_11_0_3_offset.h`.
- Consumers normally combine these constants with AMDGPU MMIO/indexed-register helpers, debug dump helpers, power-management code, reset code, firmware load code, and performance/fault instrumentation.

The main macro families are:

- `GFX_IMU_DPM_*`: accumulator control and count fields. `GFX_IMU_DPM_CONTROL` includes `ACC_RESET`, `ACC_START`, and `BUSY_MASK`; `GFX_IMU_DPM_ACC` and `GFX_IMU_DPM_REF_COUNTER` expose 24-bit counts.
- `GFX_IMU_RLC_RAM_*`: indexed RLC RAM access metadata. `GFX_IMU_RLC_RAM_INDEX` carries `INDEX`, `RLC_INDEX`, and `RAM_VALID`, while high/low address and data registers expose address and 32-bit data windows.
- `GFX_IMU_FENCE_*`, `GFX_IMU_PROGRAM_CTR`, and `GFX_IMU_CORE_*`: fence enable/logging fields, fence log initiator/address fields, program counter state, core reset/stall/debug/break controls, and core status/fault reporting.
- `GFX_IMU_PWROK*`, `GFX_IMU_RESETn`, `GFX_IMU_GFX_RESET_CTRL`, `GFX_IMU_AEB_OVERRIDE`, `GFX_IMU_VDCI_RESET_CTRL`, and `GFX_IMU_GFX_ISO_CTRL`: power-good, reset, valid/reset override, VDCI reset, and isolation bits that participate in graphics power and reset sequencing.
- `GFX_IMU_TIMER[0-2]_*`: three timer blocks with start/stop, clear, up/down, pulse, PWM, timestamp mode, saturation, compare auto-increment, compare interrupt enable, compare values, and current value fields. This chunk defines compare slots `CMP0`, `CMP1`, and `CMP3`; no `CMP2` appears in this generated segment.
- `GFX_IMU_FUSE_CTRL`, `GFX_IMU_D_RAM_*`, `GFX_IMU_GFX_IH_GASKET_CTRL`, and PSP-decoded `GFX_IMU_RLC_BOOTLOADER_*`/`GFX_IMU_I_RAM_*`: fuse divider override/done bits, data/instruction RAM address/data fields, IH gasket reset/buffer status, and RLC bootloader address/size fields.
- `GC_CAC_*` and `SE_CAC_*`: CAC ID/threshold selection plus many `GC_CAC_ACC_*` 32-bit accumulator registers for CP, EA, UTCL2 router/VML2/walker/ATCL2, GDS, GE, PMM, GL2C, PH, SDMA, CHC, GUS, and RLC blocks. `SE_CAC_*` provides the shader-engine CAC selector and threshold fields.
- Transition and update tables: `RELEASE_TO_STALL_LUT_*`, `STALL_TO_RELEASE_LUT_*`, `STALL_TO_PWRBRK_LUT_*`, `PWRBRK_STALL_TO_RELEASE_LUT_*`, `PWRBRK_RELEASE_TO_STALL_LUT_*`, `FIXED_PATTERN_PERF_COUNTER_*`, and `HW_LUT_UPDATE_STATUS`.
- `RTAVFS_REG0` through `RTAVFS_REG194`: generated AVFS register fields. Early registers define zone start/stop counts and enables, mid-range registers define per-zone CPO average divider values and 64 CPO ripple counter snapshots, and late registers define override controls, voltage-code status, run/save/restore/debug-stop controls, scaled final counts, FSM state, and ripple-count readback.
- `SQ_DEBUG_STS_LOCAL`, `SQ_DEBUG_CTRL_LOCAL`, and `SQ_WAVE_*`: SQ debug and wave-state fields for active/valid/idle slots, floating-point mode, exception/trap state, scalar and vector condition flags, allocation bases/sizes, wait counters, PC, scratch, HW IDs, scheduling, shader cycle count, temporary registers, and execution masks.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 11.0.3 register header for the active ASIC generation.
2. Select the matching register address from `gc_11_0_3_offset.h`.
3. Read or construct a 32-bit register value.
4. Use the `__SHIFT`/`__MASK` pair, typically through field helpers, to pack a new field or decode a hardware snapshot.
5. Write the value through MMIO or indexed-register access, or report the decoded value through debug, performance, reset, or power-management paths.

For GFX IMU fields, higher-level code may sequence reset/power/isolation bits, load or inspect IMU/RLC RAM windows, arm fence logging, control the IMU core, program timers, or provide PSP-visible bootloader location metadata. For CAC and RTAVFS fields, runtime paths configure counters, thresholds, transition lookup tables, and AVFS measurement/control registers, then poll completion/status fields. For SQ fields, debug and wave-inspection flows select a shader-queue indexed register and decode wave state for hang analysis, trap handling, debugger integration, or diagnostics.

The header does not encode required ordering, polling intervals, clear-on-read behavior, reset defaults, side effects, or atomic snapshot rules. Those semantics live in the AMDGPU engine code, firmware protocols, and hardware programming guide.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware state owned by the GPU, firmware, and the AMDGPU driver.

GFX IMU state is sensitive because many fields directly affect hardware sequencing. Core reset/stall/debug controls, power-good/reset/isolation bits, VDCI reset bits, fuse overrides, and IH gasket reset fields are not passive status fields. Incorrect writes can hold graphics blocks in reset, isolate the wrong interface, hide power-good transitions, or prevent interrupt delivery. RLC RAM and IMU instruction/data RAM fields are indexed windows into device-owned RAM; their address/index/data values persist as device state until overwritten, reset, or power-gated.

Fence logging, program counter, core status, and fault fields are diagnostic state. Some bits are live and volatile, while others may be sticky until cleared by a documented sequence. The header cannot distinguish live, sticky, write-one-to-clear, or read-only semantics; callers must preserve reserved bits and follow the register spec.

CAC and RTAVFS state is both configuration and measurement. CAC thresholds, block/signal selections, transition LUT entries, fixed-pattern counters, and hardware LUT update status affect or expose power/performance classification. RTAVFS zone boundaries, enable masks, CPO weights, ripple counters, voltage/frequency codes, override selects, run-loop controls, retention-save/restore controls, and stop/debug controls participate in adaptive voltage/frequency behavior. Misprogramming these fields can produce unstable clocks/voltages, bad power telemetry, misleading performance counters, or failed save/restore of retained AVFS data.

SQ wave registers represent live shader execution state. `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, wait counters, PC, scratch pointers, HW IDs, temporary trap registers, `M0`, and `EXEC` masks can change while waves execute. Debug code must capture them with the correct wave selection and stabilization procedure; reading them without quiescing or selecting the intended wave can produce inconsistent snapshots.

Reserved fields appear throughout the chunk, especially in RTAVFS registers. Any read-modify-write consumer should preserve reserved bits unless the authoritative programming sequence explicitly requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.3 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` provides the matching register address symbols.
- AMDGPU common register helpers provide field extraction/composition and MMIO or indexed-register access.
- GFX IMU, RLC, PSP/firmware load, interrupt handling, reset, graphics-off, clock/power management, CAC, AVFS, shader debug, hang-dump, KFD/compute debugging, and trap/debugger paths are the likely consumers.

Important integration points include:

- IMU/RLC bring-up and firmware/bootloader handoff through `GFX_IMU_RLC_BOOTLOADER_ADDR_*`, `GFX_IMU_RLC_BOOTLOADER_SIZE`, `GFX_IMU_I_RAM_*`, and `GFX_IMU_D_RAM_*`.
- Reset and power sequencing through `GFX_IMU_CORE_CTRL`, `GFX_IMU_CORE_STATUS`, `GFX_IMU_PWROK*`, `GFX_IMU_GFX_RESET_CTRL`, `GFX_IMU_VDCI_RESET_CTRL`, and `GFX_IMU_GFX_ISO_CTRL`.
- Debug and fault reporting through IMU fence logs, program counter, core fault fields, IH gasket status, CAC counters, RTAVFS FSM/status fields, and SQ wave/trap state.
- Power/performance management through CAC accumulators, stall/release and power-break LUTs, fixed-pattern counters, hardware LUT update status, and RTAVFS control/readout registers.
- Shader hang analysis and debugging through `SQ_DEBUG_STS_LOCAL`, wave slot bitmaps, `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, allocation/wait/PC/scratch/HW-ID registers, trap temporary registers, and `EXEC`/`M0` state.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bit or decodes misleading diagnostics.
- The chunk starts mid-register at `GFX_IMU_DPM_CONTROL`; the missing `ACC_RESET` and `ACC_START` shift definitions are in the previous adjacent chunk. This document is chunk-scoped and final file-level research must merge adjacent chunks.
- This chunk closes the header at `#endif`; it has no following adjacent chunk for SQ definitions. The final file report should note that `SQ_WAVE_EXEC_HI` is the terminal macro family in this generated header.
- GFX IMU reset, isolation, fuse, core-control, and VDCI fields have direct side effects. Treating them as ordinary debug bits can hang the graphics pipeline, lose interrupt delivery, or break firmware handoff.
- Indexed RAM windows require correct index/address/data sequencing. Reusing `GFX_IMU_RLC_RAM_INDEX`, `GFX_IMU_D_RAM_ADDR`, or `GFX_IMU_I_RAM_ADDR` without respecting alignment and validity bits can read or modify the wrong internal RAM location.
- Timer fields are repeated across timers 0, 1, and 2 and are easy to update asymmetrically. The generated absence of `CMP2` in this slice should not be "filled in" by assumption without checking the register database.
- CAC accumulator families are long and repetitive. Copy/generator mistakes can silently map a counter for one block, such as SDMA, GE, GL2C, UTCL2, or PH, to the wrong mask.
- Transition LUT fields use narrow packed entries with different widths across release/stall and power-break tables. Using the wrong table's field width can corrupt neighboring entries.
- RTAVFS fields are power-management critical and include many reserved masks. Full-register writes that fail to preserve reserved bits can destabilize AVFS behavior or retention/debug state.
- SQ wave state is volatile and selected through indexed register access. Debuggers and hang-dump code must account for wave selection, halted/running state, and potentially inconsistent snapshots across PC/status/trap/EXEC reads.
- Trap and exception fields can affect security and fault triage. Misdecoding `SQ_WAVE_TRAPSTS`, privilege bits, scratch state, or HW IDs can attribute a fault to the wrong queue, VMID, wave, or shader engine.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_11_0_3_sh_mask.h`, especially GC 11.0.3 GFX IMU, RLC, PSP, power-management, reset, AVFS/CAC, SQ debug, KFD, and hang-dump paths.
- Mechanical comparison against AMD's authoritative GC 11.0.3 register database for every `__SHIFT` and `__MASK` value in lines 42402-44690.
- Cross-check that every register family in this chunk has a matching address macro in `gc_11_0_3_offset.h`.
- Static mask/shift sanity checks: masks should align with shifts, full-width data registers should use `0xFFFFFFFFL`, packed LUT fields should not overlap, repeated timer and RTAVFS patterns should stay structurally consistent, and reserved masks should cover only documented reserved bits.
- IMU bring-up tests that validate RLC bootloader address/size programming, IMU instruction/data RAM access, core reset/stall release, program counter movement, and absence of fatal/core access errors.
- Reset and power tests that exercise `PWROK`, reset, isolation, VDCI, fuse override, fence, IH gasket, and graphics-off/GFX reset sequences with post-reset register restore.
- CAC and AVFS tests that program thresholds/LUTs, trigger hardware LUT updates, validate done/error/error-step fields, read fixed-pattern counters and accumulators, and compare RTAVFS voltage/frequency/ripple-counter outputs against expected telemetry.
- Suspend/resume and runtime power-management tests that cover RTAVFS save/restore and retention reset fields, timer state, and IMU/RLC RAM accessibility across power transitions.
- SQ debug tests that capture wave active/idle slots, mode/status/trap state, allocation metadata, wait counters, PC, scratch pointers, HW IDs, temporary registers, `M0`, and `EXEC` masks under controlled compute workloads.
- Hang/debug dump tests that verify SQ busy bits, fault/trap bits, wave status, and PC/EXEC snapshots are internally coherent and correspond to the selected wave and queue.
- Runtime warning signals include GPU reset loops, failed GFXOFF entry/exit, IMU core fatal errors, PSP access errors, broken interrupt handling, bad AVFS voltage/frequency behavior, CAC update errors, unstable clocks, misleading performance telemetry, and SQ dumps with impossible active/idle/trap combinations.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002543`. It covers lines 42402-44690 of `gc_11_0_3_sh_mask.h`. The final per-file research should merge it with previous chunks to complete the partial `GFX_IMU_DPM_CONTROL` register and place the GFX IMU, CAC, RTAVFS, and SQ terminal definitions in the full generated GC 11.0.3 register map.
