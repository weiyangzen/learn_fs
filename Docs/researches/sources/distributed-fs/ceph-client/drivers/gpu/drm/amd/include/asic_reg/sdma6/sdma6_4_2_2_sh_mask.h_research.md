# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma6/sdma6_4_2_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003399`: lines 1-2569, `Docs/researches/chunks/subset-b-003399_research.md`
- `subset-b-003400`: lines 2570-2956, `Docs/researches/chunks/subset-b-003400_research.md`

## Chunk Research

### subset-b-003399: lines 1-2569

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma6/sdma6_4_2_2_sh_mask.h lines 1-2569

## Scope

This chunk is the first 2,569 lines of AMDGPU's generated SDMA6 4.2.2 register field header. It contains C preprocessor constants only: each register field is described by a `__SHIFT` macro and a matching `_MASK` macro. There are no functions, structs, enums, storage objects, executable branches, or inline helpers in this slice.

The requested range starts at the license/header guard and the `sdma6_sdma6dec` address block. It covers public SDMA6 control/status registers, VM and virtualization fields, UTCL1/XNACK/page-fault related fields, performance/error/IOV fields, the GFX and PAGE queue register sets, RLC queue register sets `RLC0` through `RLC4`, and most of the `RLC5` queue register set. The chunk ends exactly at `SDMA6_RLC5_MIDCMD_DATA8__DATA8_MASK`; `SDMA6_RLC5_MIDCMD_CNTL` and the later `RLC6`/`RLC7` queue blocks are outside this work item.

## Purpose

The file provides bit layout metadata for the sixth SDMA engine instance on ASICs using the SDMA 4.2.2 register map. Driver code combines these masks and shifts with the matching address constants from `sdma6_4_2_2_offset.h` and AMDGPU register helpers to program or decode SDMA hardware registers.

This chunk describes fields for:

- SDMA microcode address/data and checksum registers.
- VM context, active function ID, VF enablement, and virtual reset request registers.
- Context/public register type bitmaps that classify which SDMA registers are context-owned or public.
- Main SDMA control, clock, power, chicken-bit, GB address, burst, freeze, phase quantum, EDC, atomic, and status registers.
- UTCL1 controls, watermarks, read/write status, invalidation registers, XNACK address/vector logging, timeout limits, and page request attributes.
- Error, physical address, GPU IOV violation, ULV, EA double-bit address, credit, performance monitor, and dummy/debug registers.
- Queue programming surfaces for `GFX`, `PAGE`, and `RLC0`-`RLC5`: ring-buffer control/base/read-pointer/write-pointer registers, write-pointer polling, indirect-buffer control/base/size/read-pointer registers, context status, doorbell controls/logs/offsets, context-save-area addresses, preemption, watermark, AQL, minor pointer update, and mid-command data capture.

## Important APIs, Types, and Constants

There are no C APIs or types declared here. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Representative constants include:

- `SDMA6_CNTL__TRAP_ENABLE_MASK`, `SDMA6_CNTL__UTC_L1_ENABLE_MASK`, `SDMA6_CNTL__AUTO_CTXSW_ENABLE_MASK`, and interrupt enable masks for SDMA control.
- `SDMA6_STATUS_REG__IDLE_MASK`, `SDMA6_STATUS_REG__RB_EMPTY_MASK`, `SDMA6_STATUS_REG__INSIDE_IB_MASK`, `SDMA6_STATUS_REG__SEM_RESP_STATE_MASK`, and related engine-idle/stall indicators.
- `SDMA6_UTCL1_CNTL__REDO_ENABLE_MASK`, `SDMA6_UTCL1_RD_STATUS__PAGE_FAULT_MASK`, `SDMA6_UTCL1_WR_STATUS__PAGE_NULL_MASK`, and `SDMA6_UTCL1_INV0__INV_VMID_VEC_MASK`.
- `SDMA6_GPU_IOV_VIOLATION_LOG__VIOLATION_STATUS_MASK`, `...__ADDRESS_MASK`, `...__VF_MASK`, and `...__VFID_MASK`.
- Queue setup fields such as `SDMA6_GFX_RB_CNTL__RB_ENABLE_MASK`, `SDMA6_PAGE_IB_CNTL__IB_ENABLE_MASK`, `SDMA6_RLC0_RB_WPTR_POLL_CNTL__FREQUENCY_MASK`, and `SDMA6_RLC5_DOORBELL__ENABLE_MASK`.
- Address alignment masks such as `SDMA6_GFX_IB_BASE_LO__ADDR_MASK`, `SDMA6_PAGE_RB_RPTR_ADDR_LO__ADDR_MASK`, and the analogous `RLC*` address fields.

The repeated queue blocks are structurally important. `GFX`, `PAGE`, and each `RLCn` queue use nearly identical field layouts for RB/IB setup, doorbells, writeback addresses, status, AQL, and mid-command data. That regularity is relied on by code that derives per-queue offsets instead of hard-coding every queue register.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants that are substituted into AMDGPU register helper calls.

Runtime behavior appears in consumers that combine:

- An address macro such as `mmSDMA6_UTCL1_TIMEOUT` or `mmSDMA6_RLC0_RB_CNTL` from `sdma6_4_2_2_offset.h`.
- A field namespace from this file, for example `SDMA6_RLC0_RB_CNTL`.
- Register read/write or field helpers such as `RREG32`, `WREG32`, `SOC15_REG_OFFSET`, `SOC15_REG_GOLDEN_VALUE`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

The nearby AMDGPU SDMA implementation (`amdgpu/sdma_v4_0.c`) includes this header with the matching offset header and uses the SDMA register namespaces for register lists and golden settings. The KFD Arcturus bridge (`amdgpu/amdgpu_amdkfd_arcturus.c`) includes SDMA0-SDMA7 register headers and computes RLC queue offsets by using the distance between queue register blocks.

## State and Persistence Behavior

The header stores no software state and performs no persistence itself. The fields it names map to SDMA hardware register state while the GPU block is powered and accessible.

Control fields can alter persistent hardware behavior until reset, power-gating loss, or later driver reprogramming. Examples include microcode upload address/data, VM context settings, VF enable/reset fields, SDMA enable/control bits, clock and memory-power controls, UTCL1 redo/invalidation/page controls, ring/IB enable bits, write-pointer polling controls, doorbell enable/offset fields, context-save addresses, AQL settings, and preemption controls.

Status and log fields expose volatile or sticky hardware-observed state. Examples include engine idle/full/stall bits, UTCL1 read/write FIFO and page fault status, XNACK address/vector logs, EDC counters, performance counter results, GPU IOV violation logs, doorbell logs, write-pointer update pending/failure counts, context selected/idle/expired/preempted bits, and mid-command data registers. This header does not encode whether a field is read-only, write-one-to-clear, clear-on-read, sticky, or latched; call sites must follow the hardware register specification.

## Dependencies

Primary dependencies and companions:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma6/sdma6_4_2_2_offset.h` supplies the matching `mmSDMA6_*` addresses and base indices. Its address block starts at base address `0x7c000`, with `mmSDMA6_GFX_RB_CNTL` at offset `0x0080`, `mmSDMA6_PAGE_RB_CNTL` at `0x00d8`, and RLC queue blocks starting at `mmSDMA6_RLC0_RB_CNTL` offset `0x0130`.
- AMDGPU's generated register-field macros expect the exact mask/shift naming convention used here. `REG_SET_FIELD` and `REG_GET_FIELD` form field values by token-pasting the register and field names to these macros.
- SOC15 register access helpers use the offset header and hardware IP instance to map the SDMA6 local register offset into the device register aperture.
- Sibling SDMA headers (`sdma0` through `sdma7`) provide matching layouts for other SDMA engine instances. `amdgpu_amdkfd_arcturus.c` includes all of them because Arcturus exposes multiple SDMA engines.
- `amdgpu/sdma_v4_0.c` includes this header and uses SDMA register names in diagnostic register lists and ASIC-specific golden register tables.

## Integration Points

This chunk sits at the generated hardware-description boundary, not in a high-level Ceph or filesystem path despite the repository prefix. Its practical consumers are AMDGPU SDMA/KFD paths.

Integration points include:

- SDMA initialization and golden setting application, where masks/addresses are used to program timing, polling, UTCL1, GB address, and queue-control registers.
- Queue setup for graphics, page, and KFD/RLC queues, where RB/IB bases, sizes, read/write pointers, VMID/privilege, doorbells, AQL, CSA, and writeback addresses must be encoded exactly.
- Runtime diagnostics and debug register dumps, where status, XNACK, page-fault, doorbell, and mid-command fields are decoded.
- GPU virtualization and SR-IOV support, where active function IDs, VF enablement, virtual reset requests, and IOV violation logs are interpreted.
- Error handling and RAS-adjacent paths, where EDC counters, page fault/null status, error logs, physical address registers, and EA double-bit address registers may be read.

## Risks

- Any incorrect mask or shift silently programs the wrong hardware bits. For queue registers this can corrupt ring base addresses, pointer writeback addresses, VMID/privilege, doorbell routing, AQL packet stepping, or IB execution state.
- Address fields have alignment baked into the masks and shifts, commonly low-bit offsets of `0x2` or `0x5`. Call sites must pass already-compatible addresses and avoid treating masked fields as byte-exact full addresses.
- The repeated queue layout makes copy/paste or generator errors hard to spot: a typo in an `RLCn` field can affect only one queue while the others continue to work.
- This chunk boundary is in the middle of the `RLC5` queue block. Research or reconciliation that assumes complete RLC5 coverage from this chunk alone would miss `SDMA6_RLC5_MIDCMD_CNTL` and all later RLC6/RLC7 fields.
- Status/log fields can have write-sensitive clear semantics, but this header does not distinguish safe read fields from write-one-to-clear or hardware-owned fields.
- The SDMA6 namespace is ASIC-version-specific. Reusing these constants with another SDMA generation or engine instance can misprogram registers even when names look similar.
- Virtualization fields and IOV violation logs are security-sensitive: wrong masks can misidentify a VF, miss a violation, or incorrectly reset/enable functions.

## Test Signals

Useful verification signals for this chunk are mostly compile-time and hardware-runtime oriented:

- AMDGPU builds that include `amdgpu/sdma_v4_0.c` and `amdgpu/amdgpu_amdkfd_arcturus.c` should compile without undefined SDMA6 field macros or macro redefinition warnings.
- Generated-header consistency checks should confirm that every `<REGISTER>__<FIELD>_MASK` in lines 1-2569 has the expected companion `<REGISTER>__<FIELD>__SHIFT`, and that masks align with shifts inside 32-bit registers.
- Cross-check this header against `sdma6_4_2_2_offset.h` so field groups match address groups, especially the `GFX`, `PAGE`, and `RLC0`-`RLC5` queue block spacing.
- Runtime smoke tests on affected AMDGPU hardware should cover driver probe, SDMA microcode load, SDMA ring creation, IB submission, doorbell writes, page queue activity, suspend/resume, and GPU reset.
- KFD tests on Arcturus-like multi-SDMA hardware should exercise queue offsets for SDMA6 RLC queues and verify that queue IDs map to the expected `RLCn` register block.
- Fault or stress tests should monitor UTCL1 page fault/XNACK status, IOV violation logs, EDC counters, and performance counters without adjacent-field corruption after read-modify-write operations.

### subset-b-003400: lines 2570-2956

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma6/sdma6_4_2_2_sh_mask.h lines 2570-2956

## Scope

This chunk covers the tail of the generated SDMA6 4.2.2 shift/mask header. It starts with `SDMA6_RLC5_MIDCMD_CNTL`, then defines the complete field layouts for SDMA engine 6 RLC queues 6 and 7, and ends at the header guard terminator.

The covered register groups are:

- `SDMA6_RLC5_MIDCMD_CNTL` control bits for the queue 5 mid-command save/restore data block.
- `SDMA6_RLC6_*` ring buffer, indirect buffer, context status, doorbell, watermark, context save area, preemption, write-pointer polling, AQL, minor pointer update, and mid-command data/control fields.
- `SDMA6_RLC7_*` with the same layout as RLC6 for the next queue slot.

This is a generated hardware register bitfield map. It defines C preprocessor constants only. There are no functions, structs, storage objects, allocation paths, locks, or executable branches in the chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI for SDMA6 RLC queue programming on the `sdma6_4_2_2` register block. The matching offset header provides register addresses such as `mmSDMA6_RLC6_RB_CNTL` and `mmSDMA6_RLC7_MIDCMD_CNTL`; this mask header provides the field positions and masks used to compose and decode the 32-bit register values.

The definitions follow the generated AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register.

Consumers normally use these with AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `SOC15_REG_OFFSET`, and register offset macros from `sdma6_4_2_2_offset.h`. In the Arcturus KFD path, per-engine/per-queue register addresses are computed from an RLC0 base plus a queue stride, so queue 6 and 7 layouts must remain identical to the lower-numbered RLC queue layouts.

## Important Macro Families

### Ring Buffer Registers

`SDMA6_RLC6_RB_CNTL` and `SDMA6_RLC7_RB_CNTL` define the main queue enable/configuration fields:

- `RB_ENABLE` at bit 0 gates the queue.
- `RB_SIZE` at bits 5:1 stores the ring size encoding.
- `RB_SWAP_ENABLE` controls byte swapping.
- `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, and `RPTR_WRITEBACK_TIMER` configure read-pointer writeback.
- `RB_PRIV` and `RB_VMID` select privilege and VMID context.

The queue address/pointer registers are full-width or alignment-constrained fields:

- `RB_BASE` is the low 32 bits of the ring base, while `RB_BASE_HI` carries a 24-bit high address field.
- `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI` are full-width pointer halves.
- `RB_RPTR_ADDR_LO` reserves bit 0 for `RPTR_WB_IDLE` and stores the aligned writeback address from bit 2 upward; `RB_RPTR_ADDR_HI` is full-width.

Write-pointer polling is controlled by `RB_WPTR_POLL_CNTL`, with `ENABLE`, `SWAP_ENABLE`, `F32_POLL_ENABLE`, a 12-bit `FREQUENCY`, and a 16-bit `IDLE_POLL_COUNT`. The polling address is split across `RB_WPTR_POLL_ADDR_LO` and `_HI`, with the low address aligned at bit 2.

### Indirect Buffer and Queue Progress Registers

`IB_CNTL` exposes `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, and `CMD_VMID`. The associated `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, and `IB_SIZE` fields describe the active indirect buffer and command-progress state. The low IB base starts at bit 5, indicating a 32-byte alignment requirement, while `IB_RPTR` and `IB_OFFSET` use bit 2 alignment.

`SKIP_CNTL` and `IB_SUB_REMAIN` each expose a 20-bit count/size field. These are part of queue progress and context state rather than CPU-owned persistent data.

### Context, Doorbell, and Status Registers

`CONTEXT_STATUS` has the state bits used by queue management code:

- `SELECTED`, `IDLE`, `EXPIRED`, and `EXCEPTION` describe the scheduler-visible state.
- `CTXSW_ABLE` and `CTXSW_READY` describe context-switch readiness.
- `PREEMPTED` and `PREEMPT_DISABLE` expose preemption state.

The doorbell group includes:

- `DOORBELL` with `ENABLE` at bit 28 and `CAPTURED` at bit 30.
- `DOORBELL_OFFSET`, an aligned offset field beginning at bit 2.
- `DOORBELL_LOG`, with `BE_ERROR` and aligned `DATA`.
- `STATUS`, with `WPTR_UPDATE_FAIL_COUNT` and `WPTR_UPDATE_PENDING`.

`WATERMARK` defines separate outstanding read and write thresholds. `CSA_ADDR_LO` and `_HI` provide context save area addressing, with the low address aligned at bit 2.

### Preemption, AQL, Minor Pointer Update, and Mid-command State

`PREEMPT` exposes the single `IB_PREEMPT` request bit. `RB_AQL_CNTL` controls AQL mode with `AQL_ENABLE`, `AQL_PACKET_SIZE`, and `PACKET_STEP`; this is relevant when SDMA queues are used in HSA/KFD-style queueing.

`MINOR_PTR_UPDATE` provides a single `ENABLE` bit. In queue load paths this is used around read/write pointer updates so the hardware observes a coherent pointer transition.

`MIDCMD_DATA0` through `MIDCMD_DATA8` are full-width data registers, and `MIDCMD_CNTL` exposes `DATA_VALID`, `COPY_MODE`, `SPLIT_STATE`, and `ALLOW_PREEMPT`. These fields preserve or describe in-flight command state across context switch, preemption, or dump paths. The chunk includes queue 5's `MIDCMD_CNTL` tail and full mid-command data/control sets for queues 6 and 7.

## Control Flow

There is no local control flow in this header. Runtime behavior is in consumers that include this header and the matching offset header.

The main observed integration path is `amdgpu_amdkfd_arcturus.c`:

- `get_sdma_rlc_reg_offset()` selects the SDMA engine base. For engine 6 it uses `SOC15_REG_OFFSET(SDMA6, 0, mmSDMA6_RLC0_RB_CNTL) - mmSDMA6_RLC0_RB_CNTL`.
- It computes a per-queue offset with `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`. This makes the regular spacing between RLC0 through RLC7 registers a hard dependency.
- `kgd_arcturus_hqd_sdma_load()` disables `RB_ENABLE`, waits for `CONTEXT_STATUS.IDLE`, programs doorbell, ring pointers, ring base, and read-pointer writeback address, then re-enables `RB_ENABLE`.
- `kgd_arcturus_hqd_sdma_dump()` dumps register ranges from `RB_CNTL` through `DOORBELL`, `STATUS` through `CSA_ADDR_HI`, `IB_SUB_REMAIN` through `MINOR_PTR_UPDATE`, and `MIDCMD_DATA0` through `MIDCMD_CNTL`.
- `kgd_arcturus_hqd_sdma_is_occupied()` tests `RB_CNTL.RB_ENABLE`.
- `kgd_arcturus_hqd_sdma_destroy()` clears `RB_ENABLE`, waits for `CONTEXT_STATUS.IDLE`, disables the doorbell, restores enable state, and persists the current read pointer back into the MQD.

Although those consumers often use `SDMA0_RLC0_*` masks after computing a queue-specific register offset, the queue 6 and queue 7 masks in this file must match that layout because they document and enable direct symbolic use of the same hardware fields for SDMA6.

## State and Persistence Behavior

The macros describe hardware register state. They do not persist anything by themselves, but the fields map directly to state that crosses CPU/GPU boundaries:

- Ring base, read/write pointers, pointer writeback addresses, and doorbell offsets bind a queue to GPU-visible memory and doorbell aperture state.
- `RB_ENABLE`, `IB_ENABLE`, `AQL_ENABLE`, `MINOR_PTR_UPDATE`, and `PREEMPT.IB_PREEMPT` are live control bits that affect hardware scheduling and command execution.
- `CONTEXT_STATUS`, `STATUS`, `DOORBELL_LOG`, `WATERMARK`, `IB_SUB_REMAIN`, and mid-command registers expose runtime queue state useful for diagnostics, preemption, and context switching.
- `CSA_ADDR_*` and `MIDCMD_DATA*` are context-save related state. Save/dump paths can rely on these fields to reconstruct or preserve an in-flight SDMA queue.

Alignment masks are part of the state contract. Low address registers that mask off bits 0 or 1 require callers to pass properly aligned addresses; otherwise low bits are silently lost when the value is composed.

## Dependencies and Integration Points

This chunk depends on:

- `sdma6_4_2_2_offset.h` for the matching `mmSDMA6_RLC6_*` and `mmSDMA6_RLC7_*` register addresses. In that file, RLC6 starts at `mmSDMA6_RLC6_RB_CNTL` `0x0340` and RLC7 starts at `mmSDMA6_RLC7_RB_CNTL` `0x0398`.
- SOC15 register helpers and AMDGPU register access macros for translating per-block offsets to MMIO addresses.
- KFD SDMA MQD fields such as `sdmax_rlcx_rb_cntl`, `sdmax_rlcx_doorbell`, `sdmax_rlcx_rb_base`, and read/write pointer fields that are written into the RLC register window.
- AMDGPU/KFD queue lifecycle code that loads, destroys, dumps, or tests SDMA queues.

The direct include sites observed for this exact header are `amdgpu/sdma_v4_0.c` and `amdgpu/amdgpu_amdkfd_arcturus.c`. The chunk is therefore part of both low-level SDMA ASIC metadata and KFD queue-management support for multi-engine Arcturus-class devices.

## Risks

- Field drift between `sdma6_4_2_2_sh_mask.h` and `sdma6_4_2_2_offset.h` would cause register helpers to write valid-looking values to the wrong field or wrong queue.
- The KFD Arcturus path assumes a uniform queue stride derived from RLC0/RLC1. Any irregular spacing for RLC6 or RLC7 would break queue address calculation even if the symbolic RLC6/RLC7 macros are correct.
- `RB_ENABLE`, `DOORBELL.ENABLE`, `MINOR_PTR_UPDATE`, and pointer registers are order-sensitive. Incorrect masks can leave an active queue pointed at stale memory or expose an inconsistent write pointer to hardware.
- Address fields with alignment masks (`RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, `IB_BASE_LO`, `CSA_ADDR_LO`, `DOORBELL_OFFSET`) can silently truncate low bits. Callers must validate alignment before programming hardware.
- Context status and mid-command fields affect timeout, preemption, and debug dump logic. Wrong status masks can cause false idle detection, failed queue teardown, or misleading dumps.
- Because this is generated register metadata, hand edits are high risk. Changes should come from the authoritative ASIC register source unless a silicon documentation erratum requires a local correction.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver runtime checks:

- Kernel build coverage for AMDGPU with Arcturus/KFD support catches missing or malformed macros in the included headers.
- Static comparison against generated register specifications or sibling SDMA engine headers should show that RLC6 and RLC7 field masks match the corresponding RLC0-RLC5 queue layout.
- KFD SDMA queue load/destroy tests should complete without `SDMA RLC not idle` timeout errors.
- Queue occupancy checks should reflect `RB_ENABLE` transitions before and after queue load/destroy.
- Register dumps from `kgd_arcturus_hqd_sdma_dump()` should include coherent `RB_*`, `IB_*`, `CONTEXT_STATUS`, `DOORBELL_*`, `CSA_*`, and `MIDCMD_*` values for queue IDs 6 and 7 on SDMA engine 6.
- Doorbell update tests should show no unexpected `WPTR_UPDATE_FAIL_COUNT`, no stuck `WPTR_UPDATE_PENDING`, and no `DOORBELL_LOG.BE_ERROR`.
- Preemption or context-switch stress should preserve mid-command state and avoid false `CONTEXT_STATUS.EXCEPTION` or stuck `PREEMPTED` state.
