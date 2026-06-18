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
