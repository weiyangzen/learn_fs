# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 42468-45147

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C code; it publishes `__SHIFT` and `_MASK` constants that AMDGPU, AMDKFD, power-management, and register-debug paths use to compose or decode 32-bit MMIO and indirect-register values. The matching offsets for these fields are provided by companion generated offset headers, especially `gc_10_3_0_offset.h` for GC registers and SDMA register offset headers for similarly named SDMA blocks.

The selected range starts in SDMA3 queue control/status definitions and then moves into the `gccacind` address block for graphics clock/activity/capacitance or power-throttling accounting. Although this repository subtree is under `ceph-client`, this file is AMD GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, allocations, locks, or callbacks in this range. The exposed interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- Consumers combine these constants with register offset macros and helpers such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, and `SOC15_REG_OFFSET`.

Major register groups in this chunk:

- SDMA3 queue reset and enable status: `SDMA3_STATUS5_REG` and `SDMA3_QUEUE_RESET_REQ` expose enable state, active queue IDs, and reset request bits for the GFX, PAGE, and RLC0-RLC7 queues.
- SDMA3 GFX queue registers: `SDMA3_GFX_RB_*`, `SDMA3_GFX_IB_*`, `SDMA3_GFX_CONTEXT_*`, `SDMA3_GFX_DOORBELL*`, `SDMA3_GFX_STATUS`, `SDMA3_GFX_WATERMARK`, `SDMA3_GFX_CSA_ADDR_*`, `SDMA3_GFX_PREEMPT`, `SDMA3_GFX_RB_AQL_CNTL`, `SDMA3_GFX_MINOR_PTR_UPDATE`, and `SDMA3_GFX_MIDCMD_*`. These define ring-buffer enable/size/swap/VMID/read-pointer writeback, base and pointer registers, write-pointer polling, indirect-buffer state, context status, doorbells, preemption, AQL, and mid-command preempt-save data fields.
- SDMA3 PAGE and RLC queues: the same queue-control pattern is repeated for `SDMA3_PAGE_*` and for each `SDMA3_RLC0_*` through `SDMA3_RLC7_*` queue. The RLC queue definitions are particularly relevant to KFD/HSA compute queues and MQD programming.
- GC CAC indirect block: after the `addressBlock: gccacind` marker, the chunk defines `PCC_*`, `PWRBRK_*`, `EDC_*`, `GC_CAC_ID`, `GC_CAC_CNTL`, `GC_CAC_OVR_SEL`, `GC_CAC_OVR_VAL`, many `GC_CAC_WEIGHT_*` registers, and the beginning of `GC_CAC_ACC_*` accumulator registers. These fields describe stall-pattern control, power-brake hysteresis, EDC stretch counters, CAC enable/status/override control, per-block signal weights, and readback accumulators.
- Per-block CAC weights: the weight tables cover many graphics blocks, including BCI, CB, CP, DB, GDS, LDS, PA, PC, SC, SPI, SQ, SX/SXRB, TA/TCP/TD, RMI, EA, UTCL2/ATCL2/router/VML2/walker, CU, UTCL1, GE, PMM, GL2C, GUS, PH, SDMA, SP, GL1C, CHC, SQC, and RLC. Most weight registers pack one or two 16-bit signal weights into a 32-bit word.
- CAC accumulators: the range ends after `GC_CAC_ACC_LDS0` through `GC_CAC_ACC_LDS8` and starts `GC_CAC_ACC_BCI0`; these are full 32-bit `ACCUMULATOR_31_0` readback fields.

Important field families include queue `RB_ENABLE`, `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, `RB_VMID`, `RPTR_WB_IDLE`, pointer/base `ADDR` and `OFFSET` fields, `DOORBELL` `ENABLE`/`CAPTURED` and `DOORBELL_OFFSET`, context `IDLE`/`EXPIRED`/`EXCEPTION`/`CTXSW_*`/`PREEMPTED` state, AQL `PACKET_SIZE`/`PACKET_STEP`/mid-command preemption fields, CAC stall-pattern step and throttle-pattern fields, CAC enable/override/status fields, weight signal fields, and accumulator readback fields.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consumers:

1. ASIC-specific code includes `gc/gc_10_3_0_sh_mask.h` together with compatible offset headers.
2. Driver code chooses a concrete register by ASIC/IP block and instance.
3. The code composes a value with the generated masks and shifts, or decodes a value read from hardware.
4. Register helpers perform MMIO or indirect index/data accesses while surrounding driver code handles locking, reset ordering, queue ownership, and firmware interaction.

For SDMA rings, the driver sequence normally disables a ring, programs ring size/base, initializes read/write pointers and writeback addresses, configures write-pointer polling and doorbells, enables indirect buffers and pointer writeback, then re-enables the ring. In `sdma_v5_2.c`, similar fields are used through `REG_SET_FIELD` and direct shifts for SDMA ring startup, shutdown, doorbell writes, MQD construction, and debug register dumps.

For CAC and power-brake control, the fields are accessed through GC CAC indirect index/data registers. `soc15.c` serializes these indirect accesses with `adev->reg.gc_cac.lock`, and `gfx_v10_0.c` programs Sienna Cichlid power-brake stall patterns with `mmGC_CAC_IND_INDEX`, `ixPWRBRK_STALL_PATTERN_CTRL`, and `PWRBRK_STALL_PATTERN_CTRL__*` shifts.

## State And Persistence Behavior

This file stores no software state and persists nothing by itself. It describes hardware state.

The SDMA3 portion represents live queue and context state: ring enablement, queue reset requests, ring bases, read/write pointers, write-pointer polling locations, read-pointer writeback, doorbell capture state, indirect-buffer pointers, context-save addresses, preemption status, AQL mode, mid-command preemption scratch data, and watermark/status counters. These values are hardware-owned once queues run and are reset or reprogrammed during driver init, GPU reset, suspend/resume, queue eviction/restore, or KFD MQD reload.

The CAC portion represents indirect GC power/accounting state: stall patterns, hysteresis, EDC stretch counters, global CAC control, override selectors/values, per-block signal weights, and accumulators. Some fields are persistent configuration until reset or reprogramming; others are counters, status bits, or override controls whose meaning depends on current clocks, power state, workload, and firmware policy.

The macros do not encode access class. A field may be read-only, write-only, write-one-to-clear, self-clearing, sticky, latched, reserved, or indirect-only according to the hardware specification. Consumers must preserve unrelated and reserved bits when updating mixed-control registers.

## Dependencies And Integration Points

Direct dependencies are the generated offset headers that define the corresponding `mm*`, `reg*`, `ix*`, and base-index symbols. For this GC 10.3.0 header, include users found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`

Important integration points include:

- SDMA engine initialization, shutdown, reset recovery, ring tests, write-pointer submission, and interrupt handling in `sdma_v5_2.c`.
- KFD/HSA compute queue setup and MQD programming, where RLC queue ring-control, doorbell, context-save, AQL, and preemption fields are used to describe user queues.
- Doorbell and NBIO integration, since SDMA doorbell enable/offset fields must match the doorbell aperture and range programmed by NBIO.
- GPU reset, suspend/resume, and runtime power-management paths, because SDMA queue state and CAC configuration can be lost or become stale across power transitions.
- GC CAC indirect access helpers in `soc15.c`, which guard `mmGC_CAC_IND_INDEX`/`mmGC_CAC_IND_DATA` with `adev->reg.gc_cac.lock`.
- GFX 10.3 power-brake setup in `gfx_v10_0.c`, which writes `PWRBRK_STALL_PATTERN_CTRL` through the GC CAC indirect window and combines it with `GC_THROTTLE_CTRL` and DIDT throttle control.
- SMU/power-management code that interprets CAC/EDC signals as part of power, throttling, or telemetry policy.

## Risks And Edge Cases

- Header/offset mismatch is the main structural risk. These untyped constants can compile against the wrong generated offset family while programming an unintended register or field.
- SDMA queue registers are sequencing-sensitive. Enabling `RB_ENABLE` before base, pointer, writeback, doorbell, or polling registers are correct can corrupt queue state or hang the engine.
- Pointer units differ by field. Several low address fields start at bit 2 or bit 5, ring bases may be shifted by more than two bits in consumers, and doorbell offsets are DWORD-oriented. Incorrect shifts can place rings, polling memory, writebacks, or doorbells at the wrong GPU address.
- Ring buffer size fields are encoded sizes, not byte counts. Consumers must use the expected order/log encoding and maintain alignment with firmware or MQD ABI requirements.
- Doorbells are vulnerable to power-state races. `sdma_v5_2.c` contains fallback behavior for missed SDMA doorbells during power gating, so tests that pass only with MMIO write-pointer updates may hide doorbell problems.
- RLC queue fields are replicated across eight queues. Off-by-one register selection or wrong per-queue offset arithmetic can configure a valid but unintended queue.
- Context, preemption, and mid-command fields are hardware/firmware coordinated. Misprogramming `PREEMPT`, `MIDCMD_CNTL`, `DATA_VALID`, `ALLOW_PREEMPT`, or context-save addresses can break queue eviction, reset recovery, or HSA preemption.
- CAC indirect registers require serialized index/data access. Missing the GC CAC lock can interleave index and data writes from different paths and corrupt unrelated power-management state.
- CAC weights and accumulators are generated numeric fields without semantic validation. Wrong weights, overrides, or stall patterns can produce incorrect power estimates, overly aggressive throttling, or misleading telemetry while remaining syntactically valid.
- Full-width masks such as `0xFFFFFFFFL` appear on data and accumulator registers. Full width does not imply safe writeability; many such registers are readback, indirect data windows, or hardware-owned counters.
- The chunk boundary is artificial. It starts after earlier SDMA3 status/scratch/timestamp definitions and ends in the middle of the CAC accumulator list, so adjacent chunks are needed for the complete source-file picture.

## Test Signals

Useful validation is mostly build, static, hardware, and power-management coverage:

- Build coverage for GFX10.3/Vangogh/Sienna Cichlid paths that include `gc_10_3_0_sh_mask.h`, especially `sdma_v5_2.c`, `gfxhub_v2_1.c`, and SMU11 power-management files.
- Generated-header consistency checks that every `__SHIFT` has a matching `_MASK`, masks are aligned to shifts, fields do not overlap within a register except documented aliases/reserved fields, and all register names match compatible offset headers.
- SDMA ring smoke tests that initialize rings, submit copies/fills, advance write pointers through both doorbell and MMIO fallback paths, read back pointers, and verify fences complete.
- KFD queue tests that create and destroy HSA queues using RLC queue MQDs, exercise AQL packet submission, preemption/eviction/restore, and validate doorbell offsets and context-save addresses.
- Reset, suspend/resume, runtime power-gating, and GPU recovery tests while SDMA queues are active, because ring state, pointer writeback, and doorbell capture can be lost or need reprogramming.
- Negative indicators include stalled SDMA fences, write-pointer update failure counts, pending write-pointer updates, incorrect active queue IDs, context status stuck non-idle, doorbell captured/error logs, or preemption never completing.
- CAC/power tests that program power-brake stall patterns, verify GC throttle behavior, read EDC/CAC counters under known workloads, and compare telemetry before and after suspend/resume or GPU reset.
- Locking tests or code review for GC CAC indirect accesses: all index/data pairs should route through serialized helpers or otherwise prove exclusive access.
- Regression signals include unexpected throttling, missing power-brake effect, nonsensical CAC accumulator values, workload-independent counters, or ASIC-specific failures limited to GC 10.3 variants.
