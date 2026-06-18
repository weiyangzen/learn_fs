# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 1-2573

## Scope

This chunk is the opening segment of the generated AMDGPU GC 11.0.0 shader-mask header. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` constant and a matching `MASK` constant. The paired register-address definitions live in the matching GC 11 offset/default headers; runtime code consumes these names through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, and `SOC15_REG_OFFSET`.

The range covers the `gc_sdma0_sdma0dec` address block from `SDMA0_DEC_START` through all SDMA0 engine-global registers and the complete SDMA0 RLC queue register layout for queues 0 through 7. It then begins `gc_sdma0_sdma1dec`, covering `SDMA1_DEC_START`, F32 wakeup, global timestamp, power control, and the start of `SDMA1_CNTL`. The chunk has no functions or structs; its API surface is the generated macro namespace used by SDMA, KFD, MES, GFX, display, and SOC21 code for GC 11 ASICs.

## Purpose

The purpose of this header slice is to encode GC 11 SDMA register bit layouts in stable macro names so driver code does not hand-code numeric bit positions. SDMA is the system DMA engine used for copy, paging, user queues, context switching, doorbells, and KFD compute-side DMA queues. The masks in this chunk define how the driver enables queues, programs ring and indirect-buffer pointers, configures doorbell offsets, controls preemption, decodes idle/fault/error status, and programs UTCL1 memory-translation behavior.

This is a source-level contract between generated register data and driver code. For example, `sdma_v6_0.c` builds queue and MQD control words with `SDMA0_QUEUE0_RB_CNTL__RB_SIZE__SHIFT`, `SDMA0_QUEUE0_RB_CNTL__RPTR_WRITEBACK_ENABLE__SHIFT`, `SDMA0_QUEUE0_RB_CNTL__RPTR_WRITEBACK_TIMER__SHIFT`, and `SDMA0_QUEUE0_RB_CNTL__F32_WPTR_POLL_ENABLE__SHIFT`; toggles `SDMA0_QUEUE0_DOORBELL__ENABLE` with `REG_SET_FIELD`; sets `SDMA0_UTCL1_CNTL` `RESP_MODE` and `REDO_DELAY`; applies `SDMA0_UTCL1_PAGE__LLC_NOALLOC_MASK`; and checks `SDMA0_STATUS_REG__IDLE_MASK` for idle detection. KFD's v11 MQD manager uses the same queue masks to construct `struct v11_sdma_mqd` contents for user SDMA queues. MES v11 uses `regSDMA0_QUEUE_RESET_REQ`/`regSDMA1_QUEUE_RESET_REQ` and the queue reset bit positions defined here to reset individual SDMA queues.

## Register Families Covered

The engine-global SDMA0 registers cover core enablement, timing, topology, power, status, error accounting, memory translation, and diagnostics. Important groups include:

- Entry and power controls: `SDMA0_DEC_START`, `SDMA0_F32_MISC_CNTL`, `SDMA0_POWER_CNTL`, `SDMA0_CNTL`, and `SDMA0_CNTL1`. These fields gate wakeup, low-power behavior, trap/interrupt enables, endian or swap behavior, mid-command preemption, page fault/null/retry interrupts, context-empty and frozen interrupts, and ring/IB preemption interrupts.
- Static and diagnostic controls: `SDMA0_CHICKEN_BITS`, `SDMA0_CHICKEN_BITS_2`, `SDMA0_RLC_CGCG_CTRL`, `SDMA0_CLOCK_GATING_STATUS`, `SDMA0_CE_CTRL`, `SDMA0_CRD_CNTL`, `SDMA0_FED_STATUS`, `SDMA0_AQL_STATUS`, and dummy/scratch/timestamp registers. These expose clock-gating overrides/status, data-combine behavior, scheduler/credit tuning, command-execution state, and miscellaneous debug state.
- Topology and configuration: `SDMA0_GB_ADDR_CONFIG`, `SDMA0_GB_ADDR_CONFIG_READ`, `SDMA0_TILING_CONFIG`, `SDMA0_HBM_PAGE_CONFIG`, and `SDMA0_GLOBAL_QUANTUM`. These describe pipe/interleave/PKR/SE/RB topology and global scheduling quanta visible to SDMA.
- Runtime status: `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, `SDMA0_STATUS3_REG`, `SDMA0_STATUS4_REG`, `SDMA0_STATUS5_REG`, and `SDMA0_STATUS6_REG`. These expose idle bits, ring and IB command/full/empty state, MC read/write idle state, context-empty state, packet readiness, semaphore and interrupt stalls, world-switch/preemption state, queue-manager statuses, memory-return/cache statuses, and F32/CE details.
- Watchdog, freeze, reset, and scheduling support: `SDMA0_FREEZE`, `SDMA0_PROCESS_QUANTUM0`, `SDMA0_PROCESS_QUANTUM1`, `SDMA0_WATCHDOG_CNTL`, `SDMA0_QUEUE_STATUS0`, and `SDMA0_QUEUE_RESET_REQ`. These are the hardware control surface for queue hang detection, freezing, per-process quantum values, queue selection/status, and per-queue reset requests.
- EDC and error reporting: `SDMA0_EDC_CONFIG`, `SDMA0_EDC_COUNTER`, `SDMA0_EDC_COUNTER_CLEAR`, `SDMA0_ERROR_LOG`, `SDMA0_EA_DBIT_ADDR_DATA`, and `SDMA0_EA_DBIT_ADDR_INDEX`. These fields count and clear single/double-bit events across command FIFO, UTCL1, data buffers, split data, descriptor buffers, page queues, and other SDMA sub-blocks.
- Addressing and atomics: `SDMA0_PHYSICAL_ADDR_LO/HI`, `SDMA0_HOLE_ADDR_LO/HI`, `SDMA0_ATOMIC_CNTL`, and `SDMA0_ATOMIC_PREOP_LO/HI`. These fields describe physical address windows, VM holes, and atomic pre-operation behavior.

The UTCL1 portion is a high-risk memory-translation and fault surface. `SDMA0_UTCL1_CNTL` includes request enable/disable, redo delay, response mode, LRU, queue depth, and invalidation mode fields. `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_TIMEOUT`, and `SDMA0_UTCL1_PAGE` define pressure and page policy behavior, including request type, memory type, snoop/I/O selection, read/write L2 policy, DMA page size, broadcast use, physical-address selection, and LLC no-allocate behavior. `SDMA0_UTCL1_RD_STATUS` and `SDMA0_UTCL1_WR_STATUS` expose detailed fault status: XNACK, unsupported request, permission fault, dummy page, page null, retry timeout, atomic-return fault, SRIOV/VMID/client source, doorbell and writeback fault status, GCR retry status, and virtual/physical mode status. `SDMA0_UTCL1_INV0/1/2` define invalidation address, VMID, request type, ack, and sequence behavior. `SDMA0_UTCL1_RD_XNACK*` and `WR_XNACK*` capture XNACK addresses, VMIDs, vectors, and XNACK classification.

The queue section repeats a consistent register template for `SDMA0_QUEUE0` through `SDMA0_QUEUE7`. Each queue has:

- Ring buffer controls and pointers: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_HI/LO`, and `RB_WPTR_POLL_ADDR_HI/LO`. These define queue enablement, queue size, VMID, privilege, write-pointer polling, endian/swap behavior, read-pointer writeback, and the GPU/CPU-visible pointer addresses.
- Indirect-buffer controls and pointers: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, and `IB_SUB_REMAIN`. These control IB enablement, command VMID, base alignment, size, offsets, and remaining sub-IB size.
- Doorbell and scheduling controls: `DOORBELL`, `DOORBELL_LOG`, `DOORBELL_OFFSET`, `SCHEDULE_CNTL`, `SKIP_CNTL`, `CONTEXT_STATUS`, and `MINOR_PTR_UPDATE`. These fields connect queue submission to the NBIO doorbell aperture, record doorbell errors/data, assign global/process/local IDs, set context quantum, indicate selected/idle/expired/exception/context-switchable state, and allow safe write-pointer rewinds.
- Context save and preemption: `CSA_ADDR_LO/HI`, `PREEMPT`, `RB_PREEMPT`, `RB_AQL_CNTL`, `MIDCMD_DATA0..10`, and `MIDCMD_CNTL`. These fields are used for context-save area addresses, IB/ring preempt requests, AQL packet mode, mid-command preempt/restore/overlap control, and restoring in-flight mid-command state.

The trailing SDMA1 section starts the second SDMA instance's decode block. It mirrors the SDMA0 naming and bit layout for the first few registers and begins `SDMA1_CNTL` with the same trap, semaphore, swap, mid-command preempt, page-fault interrupt, context-empty, frozen, IB-preempt, and RB-preempt fields.

## Important APIs, Types, and Macros

This header defines no runtime APIs in the C function sense. Its important interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the right shift for a field in a 32-bit register value.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for the field.
- Register comments such as `//SDMA0_QUEUE0_RB_CNTL` and address-block comments such as `// addressBlock: gc_sdma0_sdma0dec` preserve the generated hardware grouping.

The driver helpers concatenate these names. `REG_SET_FIELD(value, SDMA0_QUEUE0_DOORBELL, ENABLE, 1)` depends on `SDMA0_QUEUE0_DOORBELL__ENABLE_MASK` and `SDMA0_QUEUE0_DOORBELL__ENABLE__SHIFT`; `REG_SET_FIELD(temp, SDMA0_UTCL1_CNTL, RESP_MODE, 3)` depends on the corresponding UTCL1 field definitions; and direct bit construction in MQD setup depends on the `__SHIFT` values for `RB_SIZE`, `RB_VMID`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_TIMER`, `F32_WPTR_POLL_ENABLE`, `DOORBELL_OFFSET`, and `SCHEDULE_CNTL`.

Important type-level consumers are `struct v11_sdma_mqd` in KFD/SDMA queue setup and `struct amdgpu_ring`/`struct amdgpu_mqd_prop` in SDMA ring initialization. The header does not define those types, but its bit positions determine the values stored into MQD fields such as `sdmax_rlcx_rb_cntl`, `sdmax_rlcx_rb_base`, `sdmax_rlcx_rb_wptr_poll_addr_lo/hi`, `sdmax_rlcx_rb_rptr_addr_lo/hi`, `sdmax_rlcx_doorbell_offset`, `sdmax_rlcx_sched_cntl`, and `sdmax_rlcx_rb_aql_cntl`.

## Control Flow

There is no executable control flow in this generated header. The control flow appears in consumers:

1. SDMA initialization/resume programs queue registers. `sdma_v6_0` writes `SDMA0_QUEUE0_MINOR_PTR_UPDATE`, ring read/write pointer registers, doorbell enable/offset, watchdog count, UTCL1 response/page policy, `RB_CNTL`, and `IB_CNTL`. These writes happen per SDMA instance and are translated through `sdma_v6_0_get_reg_offset()` so the `SDMA0` register template can address multiple engines.
2. MQD creation constructs persistent queue descriptors. `sdma_v6_0_mqd_init()` and KFD v11 `update_mqd_sdma()` build the MQD ring-control word and doorbell/schedule fields using this chunk's queue shifts. Later KFD load/destroy paths write those MQD values into live SDMA RLC queue registers.
3. Queue loading and teardown wait on hardware state. `hqd_sdma_load_v11()` disables `RB_ENABLE`, polls `SDMA0_QUEUE0_CONTEXT_STATUS__IDLE_MASK`, writes base/pointer/doorbell registers, and then sets `RB_ENABLE`. `hqd_sdma_destroy_v11()` clears `RB_ENABLE`, waits for idle, disables the doorbell, snapshots read pointers, and may re-enable the ring control field.
4. Idle and reset paths decode status and queue reset bits. `sdma_v6_0_is_idle()` and `sdma_v6_0_wait_for_idle()` use `SDMA0_STATUS_REG__IDLE_MASK`. MES v11 selects `regSDMA0_QUEUE_RESET_REQ` or `regSDMA1_QUEUE_RESET_REQ`, writes `1 << queue_id`, then polls until the same bit clears.
5. Fault/diagnostic paths use register dump lists and status masks. SDMA code exposes UTCL1 read/write status and XNACK registers in debug dump tables, while KFD dump paths iterate over the queue register ranges from `RB_CNTL` through `MIDCMD_CNTL`.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware registers they describe are volatile MMIO state, reprogrammed during device initialization, queue creation/load, suspend/resume, GPU reset, and queue reset.

Some values become persistent driver-visible queue state. MQD fields built with these masks are stored in memory and can survive across queue unload/reload until explicitly updated. Queue base addresses, read/write pointer addresses, doorbell offsets, VMID, RB size, context quantum, CSA address, AQL mode, and mid-command state all depend on this chunk's bit definitions. If a queue is destroyed or preempted, KFD snapshots SDMA read pointers back into the MQD so it can later resume from the correct location.

Other state is hardware-latched until cleared or reset. EDC counters, error logs, UTCL1 fault status, XNACK address/vector capture, doorbell logs, context status, queue reset request bits, and mid-command data registers are examples. Power-management and reset paths are expected to reapply control fields after the hardware loses state. Status bits such as `IDLE`, `RB_EMPTY`, `CONTEXT_EMPTY`, `INSIDE_IB`, `PREV_CMD_IDLE`, and UTCL1 fault bits are transient observations of hardware progress.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register ecosystem:

- Matching GC 11 offset headers define `regSDMA0_*`, `regSDMA1_*`, and defaults such as `regSDMA0_QUEUE0_RB_AQL_CNTL_DEFAULT`.
- AMDGPU SOC15 MMIO helpers perform reads/writes using those offsets and this header's field masks.
- SDMA v6.0 code is the main runtime consumer for GC 11 SDMA instance setup, queue programming, idle waits, context-empty interrupt handling, and MQD initialization.
- KFD v11 code consumes the queue masks for user SDMA queues, MQD allocation/update, queue load/destroy, occupancy checks, and HQD dumps.
- MES v11 integrates through SDMA queue reset request registers when resetting SDMA queues by engine and queue id.
- SOC21/GFX/display and related GC 11 paths include this header because SDMA register definitions are part of the broader GC 11 register namespace.

Important cross-boundary assumptions include the reuse of `SDMA0_QUEUE0_*` field macros as a template for all SDMA engines and queues, the coupling between doorbell offsets and NBIO doorbell-range programming, the coupling between ring pointer writeback fields and writeback memory allocations, and the coupling between UTCL1 page policy fields and VM/cache behavior. KFD and MES also assume queue ids map directly to the queue reset bit positions exposed by `QUEUE_RESET_REQ`.

## Risks

The main risk is silent hardware misprogramming. These constants compile into register read-modify-write sequences and MQD values; a wrong shift or mask can enable the wrong bit, corrupt adjacent fields, or decode the wrong status without producing a build error.

High-risk fields in this chunk include:

- `SDMA0_QUEUE*_RB_CNTL`: controls queue enablement, size, VMID, privilege, write-pointer polling, read-pointer writeback, and swap behavior. Errors can break queue launch, corrupt pointer handling, or assign work to the wrong VMID.
- `SDMA0_QUEUE*_DOORBELL` and `DOORBELL_OFFSET`: wrong bits can leave queues unnotified, route notifications to the wrong doorbell, or hide doorbell bus errors.
- `SDMA0_QUEUE*_CONTEXT_STATUS`: KFD load/destroy paths poll idle bits; an incorrect mask can cause false idle, timeout, or queue teardown while hardware is still active.
- `SDMA0_QUEUE_RESET_REQ`: MES writes `1 << queue_id` and polls for clear. Bit drift can reset the wrong queue or wait on a bit that never clears.
- `SDMA0_STATUS_REG__IDLE_MASK`: SDMA IP idle checks and suspend/reset sequencing depend on this bit.
- `SDMA0_UTCL1_CNTL`, `SDMA0_UTCL1_PAGE`, and UTCL1 fault/XNACK status: incorrect fields can cause VM retry behavior, cache policy, LLC allocation, or fault attribution regressions.
- `SDMA0_CNTL`: trap/page-fault/preempt/context-empty/frozen interrupt bits affect scheduler and recovery behavior.
- `MIDCMD_*`, `PREEMPT`, and `RB_PREEMPT`: wrong preemption fields can corrupt context switch or mid-command restore state.

Generated headers also carry many reserved and diagnostic fields. Removing apparently unused definitions can break out-of-tree tools, register dump decoders, or future workarounds. Manual edits are especially risky because this file should match AMD's authoritative register database and its paired offset/default headers.

## Test Signals

Compile-time signals include successful AMDGPU/KFD builds wherever `gc_11_0_0_sh_mask.h` is included. Renamed or missing macros generally fail at compile time in SDMA v6.0, KFD v11, MES v11, GFX v11, SOC21, and display code. Numeric mistakes, however, usually require runtime validation.

Strong runtime signals are successful probe and resume of GC 11 devices, SDMA ring bring-up, KFD user SDMA queue creation, queue load/unload, doorbell submission, and clean GPU reset/suspend/resume. SDMA idle waits should not time out, queue reset requests should clear, and KFD queue destroy/load should observe expected `CONTEXT_STATUS` idle behavior.

Memory-management and fault signals include stable VM retry/XNACK behavior, no unexpected page-fault/null/retry-timeout interrupts, sane UTCL1 read/write status dumps, and correct fault attribution for VMID/client/source fields. Workload signals include large DMA copies, paging operations, user-mode SDMA queues, preemption, AQL mode where applicable, and workloads that exercise ring write-pointer polling and read-pointer writeback. Diagnostic signals include coherent EDC counters, doorbell logs, mid-command state dumps, and SDMA status register dumps across normal operation and induced reset paths.
