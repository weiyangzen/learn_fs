# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002504`: lines 1-2573, `Docs/researches/chunks/subset-b-002504_research.md`
- `subset-b-002505`: lines 2574-5127, `Docs/researches/chunks/subset-b-002505_research.md`
- `subset-b-002506`: lines 5128-7584, `Docs/researches/chunks/subset-b-002506_research.md`
- `subset-b-002507`: lines 7585-9915, `Docs/researches/chunks/subset-b-002507_research.md`
- `subset-b-002508`: lines 9916-12288, `Docs/researches/chunks/subset-b-002508_research.md`
- `subset-b-002509`: lines 12289-14934, `Docs/researches/chunks/subset-b-002509_research.md`
- `subset-b-002510`: lines 14935-17380, `Docs/researches/chunks/subset-b-002510_research.md`
- `subset-b-002511`: lines 17381-19874, `Docs/researches/chunks/subset-b-002511_research.md`
- `subset-b-002512`: lines 19875-22323, `Docs/researches/chunks/subset-b-002512_research.md`
- `subset-b-002513`: lines 22324-24720, `Docs/researches/chunks/subset-b-002513_research.md`
- `subset-b-002514`: lines 24721-27318, `Docs/researches/chunks/subset-b-002514_research.md`
- `subset-b-002515`: lines 27319-30049, `Docs/researches/chunks/subset-b-002515_research.md`
- `subset-b-002516`: lines 30050-32601, `Docs/researches/chunks/subset-b-002516_research.md`
- `subset-b-002517`: lines 32602-35135, `Docs/researches/chunks/subset-b-002517_research.md`
- `subset-b-002518`: lines 35136-37567, `Docs/researches/chunks/subset-b-002518_research.md`
- `subset-b-002519`: lines 37568-40147, `Docs/researches/chunks/subset-b-002519_research.md`
- `subset-b-002520`: lines 40148-41664, `Docs/researches/chunks/subset-b-002520_research.md`

## Chunk Research

### subset-b-002504: lines 1-2573

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

### subset-b-002505: lines 2574-5127

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 2574-5127

## Scope

This chunk is a generated AMDGPU GC 11.0.0 register field-mask header segment. It contains preprocessor constants only: each field is represented by a `__SHIFT` value and/or an unshifted `MASK` value used by AMDGPU register helpers. The matching register offsets live in `gc_11_0_0_offset.h`, default reset values live in `gc_11_0_0_default.h`, and runtime code includes this header through GC 11 graphics, SDMA, MES, display, and KFD paths.

The range starts in the middle of `SDMA1_CNTL` field definitions, covers most of the public SDMA1 control/status and queue register layouts, repeats the SDMA1 RLC queue template for queues 0 through 7, then ends at the beginning of the SDMA hypdec microcode-control address blocks (`gc_sdma0_sdma0hypdec` and `gc_sdma0_sdma1hypdec`). Because the range begins mid-register, `SDMA1_CNTL__TRAP_ENABLE_MASK` is present in this chunk while the corresponding `TRAP_ENABLE__SHIFT` is immediately before the chunk boundary.

## Purpose

The purpose of this header slice is to give the GC 11 AMDGPU driver exact bit positions for SDMA1 engine control, status, virtual-memory translation, interrupt/error reporting, doorbell, ring-buffer, indirect-buffer, AQL, preemption, and microcode-control registers. These definitions keep low-level MMIO programming readable and let code use helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15_IP`, and `WREG32_SOC15_IP` instead of open-coded bit constants.

Although this chunk names `SDMA1_*` registers, much of the SDMA v6 runtime code programs both SDMA engines through instance arithmetic. `sdma_v6_0.c` uses `sdma_v6_0_get_reg_offset()` to start from `regSDMA0_*` offsets and add `SDMA1_REG_OFFSET` for instance 1, while KFD queue-loading code explicitly computes SDMA1 queue bases with `SOC15_REG_OFFSET(SDMA1, 0, regSDMA1_QUEUE0_RB_CNTL)`. The SDMA0 and SDMA1 field layouts must therefore remain equivalent where shared instance code uses the SDMA0 macro names for both engines.

## Register Families Covered

The `SDMA1_CNTL`, `SDMA1_CNTL1`, `SDMA1_CHICKEN_BITS`, and `SDMA1_CHICKEN_BITS_2` definitions describe engine-wide enable, interrupt, swap, mid-command preemption, world-switch, page-fault, clock-gating override, burst/combine, copy-overlap, raw-check, and polling behavior. Runtime users enable traps and preemption interrupt behavior through `REG_SET_FIELD(..., SDMA0_CNTL, TRAP_ENABLE, ...)` and use equivalent register layouts when targeting SDMA1 by offset.

The address/topology and fetch group includes `SDMA1_GB_ADDR_CONFIG`, `SDMA1_GB_ADDR_CONFIG_READ`, `SDMA1_RB_RPTR_FETCH`, `SDMA1_RB_RPTR_FETCH_HI`, `SDMA1_IB_OFFSET_FETCH`, `SDMA1_PROGRAM`, `SDMA1_PHYSICAL_ADDR_LO`, `SDMA1_PHYSICAL_ADDR_HI`, `SDMA1_GLOBAL_QUANTUM`, `SDMA1_TILING_CONFIG`, `SDMA1_TLBI_GCR_CNTL`, and `SDMA1_TIMESTAMP_CNTL`. These fields expose ring/IB fetch offsets, memory physical-address plumbing, global scheduling quantum, tiling configuration, and TLB/GCR invalidation controls.

The status and diagnostics group includes `SDMA1_STATUS_REG`, `SDMA1_STATUS1_REG`, `SDMA1_STATUS2_REG`, `SDMA1_STATUS3_REG`, `SDMA1_STATUS4_REG`, `SDMA1_STATUS5_REG`, `SDMA1_STATUS6_REG`, `SDMA1_QUEUE_STATUS0`, `SDMA1_INT_STATUS`, `SDMA1_CLOCK_GATING_STATUS`, `SDMA1_AQL_STATUS`, `SDMA1_FED_STATUS`, and `SDMA1_ERROR_LOG`. These masks decode idle bits, ring/IB command fullness, context-empty state, copy-engine stalls, UTCL1 FIFO state, interrupt latches, queue reset state, command/fetch/decode status, and error address/type information. `sdma_v6_0.c` exposes many of these registers in `sdma_reg_list_6_0[]` for debug/register dump paths and polls `SDMA*_STATUS_REG__IDLE_MASK` during idle waits.

The RAS, EDC, and microcode group includes `SDMA1_UCODE_CHECKSUM`, `SDMA1_UCODE1_CHECKSUM`, `SDMA1_EDC_CONFIG`, `SDMA1_EDC_COUNTER`, `SDMA1_EDC_COUNTER_CLEAR`, `SDMA1_EA_DBIT_ADDR_DATA`, `SDMA1_EA_DBIT_ADDR_INDEX`, `SDMA1_SCRATCH_RAM_DATA`, `SDMA1_SCRATCH_RAM_ADDR`, `SDMA1_PUB_DUMMY_REG0..3`, and `SDMA1_F32_COUNTER`. These fields are used for firmware checksum visibility, single/double error counters, counter clearing, error-address indexing, scratch RAM access, and public dummy/debug state.

The freeze, scheduling, and watchdog group includes `SDMA1_FREEZE`, `SDMA1_PROCESS_QUANTUM0`, `SDMA1_PROCESS_QUANTUM1`, `SDMA1_WATCHDOG_CNTL`, `SDMA1_QUEUE_RESET_REQ`, `SDMA1_CE_CTRL`, and `SDMA1_CRD_CNTL`. Runtime code freezes/preempts engines around reset paths, halts/unhalts the F32 microcontroller, sets queue hang watchdogs, and configures per-process quantum. Incorrect masks here directly affect reset recovery and queue scheduling fairness.

The UTCL1 and memory-translation group includes `SDMA1_UTCL1_CNTL`, `SDMA1_UTCL1_WATERMK`, `SDMA1_UTCL1_TIMEOUT`, `SDMA1_UTCL1_PAGE`, `SDMA1_UTCL1_RD_STATUS`, `SDMA1_UTCL1_WR_STATUS`, `SDMA1_UTCL1_INV0..2`, `SDMA1_UTCL1_RD_XNACK0..1`, and `SDMA1_UTCL1_WR_XNACK0..1`. `sdma_v6_0_gfx_resume_instance()` programs UTCL1 response mode, redo delay, default read/write L2 cache policy, and `LLC_NOALLOC`. The status and XNACK fields expose FIFO empty/full state, L2 interface idleness, invalidation busy state, retry attributes, VMID/client ID, address, sideband data, and page-fault retry behavior.

The queue template is repeated for `SDMA1_QUEUE0` through `SDMA1_QUEUE7`. Each queue has ring-buffer control and base/pointer registers (`RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_LO/HI`, `RB_WPTR_POLL_ADDR_LO/HI`), indirect-buffer controls (`IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, `IB_SUB_REMAIN`), context and scheduling state (`CONTEXT_STATUS`, `SCHEDULE_CNTL`, `SKIP_CNTL`), doorbell controls (`DOORBELL`, `DOORBELL_LOG`, `DOORBELL_OFFSET`), context-save address fields (`CSA_ADDR_LO/HI`), preemption (`PREEMPT`, `RB_PREEMPT`), AQL controls (`RB_AQL_CNTL`), minor pointer updates, dummy registers, and `MIDCMD_DATA0..10` plus `MIDCMD_CNTL` for mid-command preemption state.

The final hypdec section maps SDMA microcode address/data registers: `SDMA0_UCODE_ADDR`, `SDMA0_UCODE_DATA`, `SDMA0_BROADCAST_UCODE_ADDR`, `SDMA0_BROADCAST_UCODE_DATA`, `SDMA0_F32_CNTL`, and the first `SDMA1_UCODE_ADDR` fields. `sdma_v6_0_get_reg_offset()` treats the hypdec range specially with `SDMA0_HYP_DEC_REG_START`, `SDMA0_HYP_DEC_REG_END`, and `SDMA1_HYP_DEC_REG_OFFSET`, so these offsets and masks are part of the firmware/microcontroller control path rather than the ordinary public SDMA register spacing.

## Important APIs, Types, and Macros

This file defines no C functions, structs, or runtime variables. Its public API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit shift for a field within a 32-bit MMIO register value.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask.
- Register comments such as `//SDMA1_QUEUE0_RB_CNTL` and address-block comments such as `// addressBlock: gc_sdma0_sdma0hypdec` preserve generated hardware grouping.

Important consumers include `sdma_v6_0.c`, which initializes rings, doorbells, read/write pointer writeback, UTCL1 policy, watchdogs, F32 halt/reset, and SDMA idle/preemption behavior; `amdgpu_amdkfd_gfx_v11.c`, which computes SDMA RLC queue register bases for engine 0 and engine 1 and loads/restores KFD SDMA queues; and `kfd_mqd_manager_v11.c`, which builds `struct v11_sdma_mqd` values using queue-field shifts for `RB_CNTL`, `DOORBELL_OFFSET`, and `SCHEDULE_CNTL`.

The helper contract is compile-time concatenation. For example, `REG_SET_FIELD(rb_cntl, SDMA0_QUEUE0_RB_CNTL, RB_SIZE, rb_bufsz)` depends on `SDMA0_QUEUE0_RB_CNTL__RB_SIZE_MASK` and `SDMA0_QUEUE0_RB_CNTL__RB_SIZE__SHIFT`. Equivalent `SDMA1_QUEUE*_...` definitions are required when code names SDMA1 directly or when generated tables and register dump tooling decode engine 1.

## Control Flow

There is no executable control flow in this header. The control flow appears in the consumers that program the registers described here.

During SDMA resume, `sdma_v6_0_gfx_resume_instance()` programs queue 0 for each SDMA instance: ring size and privilege in `RB_CNTL`, read/write pointer registers, write-pointer polling addresses, read-pointer writeback addresses, ring base, minor pointer update, doorbell enable/offset, watchdog count, UTCL1 response/cache policy, F32 halt/reset, `RB_ENABLE`, and `IB_ENABLE`. For instance 1, the same flow reaches SDMA1 by adding the SDMA1 public-register offset.

During KFD SDMA queue creation, `kfd_mqd_manager_v11.c::update_mqd_sdma()` encodes queue size, VMID, read-pointer writeback, write-pointer polling, doorbell offset, and scheduling quantum into a `v11_sdma_mqd`. `amdgpu_amdkfd_gfx_v11.c` then computes the SDMA RLC queue register block, disables `RB_ENABLE`, waits for `CONTEXT_STATUS__IDLE`, writes doorbell and pointer/base registers, toggles `MINOR_PTR_UPDATE`, and finally re-enables `RB_ENABLE`.

During reset and diagnostics, SDMA code freezes engines with `SDMA*_FREEZE__FREEZE_MASK`, halts/resets F32 with `SDMA*_F32_CNTL` bits, checks idle through `SDMA*_STATUS_REG__IDLE_MASK`, triggers queue preemption via queue `PREEMPT` registers, and exposes status/UTCL1/XNACK/queue registers through register dump lists.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware registers they describe are volatile MMIO state that is reset, reprogrammed on driver init/resume, or restored through MQD state for KFD queues.

Some SDMA state is deliberately persistent across normal queue operation. Ring base addresses, read/write pointers, read-pointer writeback addresses, write-pointer polling addresses, doorbell offsets, VMID fields, queue scheduling quantum, AQL mode, and context-save addresses remain live until the queue is disabled, reset, or replaced. KFD SDMA queues persist part of this state in `struct v11_sdma_mqd` so queues can be loaded, saved, restored, and debugged.

Other fields are transient latches or status surfaces. Idle/full/stall bits, interrupt status, XNACK/fault attributes, EDC counters, error logs, frozen/preempted status, context status, doorbell captured/log bits, and mid-command data reflect hardware progress or faults and can change as DMA packets execute. Reset and suspend/resume paths must clear or reinitialize the right subset without losing required queue pointer state.

## Dependencies and Integration Points

This chunk depends on the GC 11 generated register ecosystem:

- `gc_11_0_0_offset.h` provides `regSDMA1_*`, `mmSDMA1_*`, and queue register addresses matching these field layouts.
- `gc_11_0_0_default.h` provides reset/default values for many registers in this chunk, including SDMA1 controls, status registers, queue controls, AQL controls, and mid-command data registers.
- AMDGPU SOC15 helpers perform MMIO reads/writes using the generated offsets and these masks.
- KFD `v11_sdma_mqd` layout mirrors many queue registers here, so MQD save/restore must stay aligned with the queue register template.
- NBIO doorbell range setup must match `SDMA*_QUEUE*_DOORBELL` and `DOORBELL_OFFSET` programming.
- VM/cache behavior depends on UTCL1 page, invalidation, timeout, and XNACK field definitions.
- RAS/debugfs/register-dump paths depend on status, EDC, error log, and XNACK masks for meaningful diagnostics.

Important cross-file integration is visible in `sdma_v6_0.c`: `sdma_v6_0_get_reg_offset()` maps public SDMA instance 1 by adding `0x600`, but maps hypdec registers through a separate `0x20` per-instance adjustment. That makes the transition at the end of this chunk especially sensitive; public SDMA queue fields and hypdec microcode fields are adjacent in the source header but use different address mapping logic.

## Risks

The main risk is silent hardware misprogramming. These constants compile into bit operations; a wrong mask or shift can still compile cleanly while enabling the wrong queue bit, writing a truncated address, polling the wrong status, or decoding the wrong fault.

High-risk fields include queue `RB_CNTL` fields such as `RB_ENABLE`, `RB_SIZE`, `RB_VMID`, writeback enable/timer, pointer polling, swap, and privilege, because they directly control DMA queue execution. Doorbell enable and offset fields are also high risk: an incorrect offset can cause missed queue submissions or writes to the wrong doorbell aperture.

Pointer and address masks are sensitive because most low address fields are alignment-shifted. `RB_BASE`, `IB_BASE_LO`, `CSA_ADDR_LO`, `RB_RPTR_ADDR_LO`, `RB_WPTR_POLL_ADDR_LO`, `PHYSICAL_ADDR_LO`, and XNACK/fault address fields must preserve the documented low-bit alignment semantics. Wrong shifts can corrupt GPU addresses even if the upper 32-bit registers are correct.

UTCL1 fields are high risk for memory correctness. Bad `RESP_MODE`, cache policy, page size, physical-address, invalidation, timeout, or XNACK decoding fields can produce stale reads/writes, incorrect retry behavior, VM fault storms, or misleading fault attribution.

Freeze, preemption, mid-command, and F32 control fields affect reset and recovery. Errors here can leave queues stuck non-idle, fail to save/restore mid-command state, prevent preemption interrupts, or wedge the SDMA firmware thread during suspend/resume or GPU reset.

Because this is generated hardware-description source, manual edits are risky. Seemingly unused queue templates for queues 1 through 7, reserved fields, dummy registers, and diagnostic fields can still be required by KFD, MES, firmware, register dumps, out-of-tree tools, or future ASIC workarounds.

## Test Signals

Compile-time signals include successful AMDGPU/KFD builds wherever `REG_SET_FIELD`, `REG_GET_FIELD`, direct `__SHIFT` constants, or direct `MASK` constants reference GC 11 SDMA names. Missing or renamed macros normally fail at compile time; wrong numeric values usually require runtime testing.

Strong runtime signals are successful probe and resume of GC 11 ASICs using SDMA v6, passing `amdgpu_ring_test_helper()` for each SDMA instance, correct SDMA ring read/write pointer behavior, working doorbell submissions, no SDMA queue hangs under copy/fill workloads, and clean suspend/resume and GPU reset recovery.

KFD-specific signals include successful creation, load, preemption, restore, and teardown of SDMA queues on both SDMA engines; correct `v11_sdma_mqd` programming; valid doorbell offsets; and no timeouts while waiting for `SDMA*_QUEUE*_CONTEXT_STATUS__IDLE_MASK`.

Memory-management signals include stable VM-copy workloads, no unexpected UTCL1 invalidation busy hangs, no XNACK retry storms, correct page-fault attribution in register dumps, and no stale-data symptoms after cache-policy or invalidation-sensitive workloads.

Diagnostic signals include sane SDMA register dumps for `STATUS*`, `UTCL1_*_STATUS`, `RD_XNACK*`, `WR_XNACK*`, `EDC_COUNTER`, `ERROR_LOG`, `AQL_STATUS`, `CLOCK_GATING_STATUS`, queue doorbell logs, and mid-command data. RAS/error-injection testing should show counters and clear bits behaving as expected without persistent EDC or DBIT error latches after recovery.

### subset-b-002506: lines 5128-7584

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 5128-7584

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C logic; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, display, and SDMA code to compose or decode 32-bit MMIO register values for this graphics IP generation. The companion register addresses and base indices live in `gc_11_0_0_offset.h`, while reset/default values are in `gc_11_0_0_default.h`.

The selected range starts in the `gc_sdma0_sdma1hypdec` block after `SDMA1_UCODE_ADDR`, covers SDMA performance counter selectors and data windows, GRBM global status/control/debug registers, command processor status and queue/ring debug registers, primitive assembler/geometry frontend controls, shader queue controls, shader/SX/SPI debug and lifetime registers, and ends in the middle of the texture pipe `TA_CNTL_AUX` mask definitions. Although this repository subtree is named `ceph-client`, this file is AMD GPU driver hardware metadata, not distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, callbacks, locks, or allocations in this range. The exported interface is a generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field low bit.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Consumers combine these with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` macros from `gc_11_0_0_offset.h`, usually through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Major register groups in this chunk:

- SDMA1 hypervisor/microcode controls: `SDMA1_UCODE_DATA`, `SDMA1_BROADCAST_UCODE_ADDR`, `SDMA1_BROADCAST_UCODE_DATA`, and `SDMA1_F32_CNTL`. These expose microcode indirect address/data fields, broadcast thread selection, F32 halt, per-thread checksum-clear/reset/enable bits, and thread priorities. The chunk starts after the `SDMA1_UCODE_ADDR` shift/mask pair, so the full SDMA1 microcode address register is split with the preceding chunk.
- SDMA0 and SDMA1 performance control and data blocks: `SDMA*_PERFCNT_PERFCOUNTER*_CFG`, `SDMA*_PERFCNT_PERFCOUNTER_RSLT_CNTL`, `SDMA*_PERFCNT_MISC_CNTL`, `SDMA*_PERFCOUNTER*_SELECT`, `SDMA*_PERFCOUNTER*_SELECT1`, `SDMA*_PERFCNT_PERFCOUNTER_LO/HI`, and `SDMA*_PERFCOUNTER{0,1}_LO/HI`. These provide event selector ranges, counter/performance modes, enable/clear bits, start/stop triggers, stop-on-saturate, command op fields, dual/four-way event selectors, and low/high counter readback fields.
- GRBM control/status block: `GRBM_CNTL`, `GRBM_SKEW_CNTL`, `GRBM_STATUS`, `GRBM_STATUS2`, `GRBM_STATUS3`, `GRBM_STATUS_SE0` through `GRBM_STATUS_SE5`, `GRBM_SOFT_RESET`, `GRBM_GFX_CLKEN_CNTL`, `GRBM_WAIT_IDLE_CLOCKS`, read/write error registers, interrupt/trap registers, UTCL2 invalidation range registers, fence ranges, scratch registers, and `VIOLATION_DATA_ASYNC_VF_PROG`. These macros describe top-level graphics busy/idle status, per-SE clean/busy state, CP/SDMA/RLC/TCP/UTCL2/EA/RMI request pending bits, soft-reset strobes, clock-gating waits, fault addresses/status, trap watch data/address masks, and scratch storage.
- Command processor decode block: `CP_CPC_*`, `CP_CPF_*`, `CP_STALLED_STAT*`, `CP_BUSY_STAT*`, `CP_STAT`, header dumps for ME/PFP/MEC, instruction pointers, `CP_CSF_STAT`, `CP_CNTX_STAT`, `CP_ME_PREEMPTION`, ring read pointers, write-pointer delay/polling, ROQ/STQ/MEQ thresholds and availability, command index/data indirect registers, queue status registers, debug indirect registers, and `CP_PRIV_VIOLATION_ADDR`. These expose CP pipeline busy/stall visibility, firmware/header diagnostics, queue/ring backpressure state, preemption state, and privileged violation address capture.
- Primitive assembler / geometry frontend block: `VGT_*`, `IA_UTCL1_*`, `WD_*`, `CC_GC_*`, `GE_*`, `GFX_PIPE_CONTROL`, `PA_CL_*`, `PA_SU_CNTL_STATUS`, and `PA_SC_FIFO_DEPTH_CNTL`. The fields cover FIFO depth reporting, MC latency thresholds, UTCL1 invalidation/status, work distributor controls and QoS, shader array and SA unit disable masks, geometry engine rate and status, pipe controls, safe-register flags, clipping enhancements, scan-converter limits, and primitive configuration.
- Shader queue block: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQG_STATUS`, `SQ_FIFO_SIZES`, `SQ_DSM_CNTL*`, `SP_CONFIG`, `SQ_ARB_CONFIG`, `SQ_DEBUG_HOST_TRAP_STATUS`, `SQG_GL1H_STATUS`, `SQG_CONFIG`, `SQ_PERF_SNAPSHOT_CTRL`, `CC_GC_SHADER_RATE_CONFIG`, `SQ_INTERRUPT_*`, four SQ watchpoint address/control sets, `SQ_IND_INDEX`, `SQ_IND_DATA`, and `SQ_CMD`. These define CU/simd mode flags, cache and LDS configuration, arbitration and prioritization, trap/debug status, GL1H/SQG status, shader-rate configuration, auto-masking and interrupt message controls, watchpoint address/mode/VMID fields, and indirect SQ command dispatch fields.
- Shader/SX/SPI block: `SX_DEBUG_1`, `SPI_PS_MAX_WAVE_ID`, `SPI_GFX_CNTL`, `SPI_DSM_CNTL*`, `SPI_EDC_CNT`, `SPI_CONFIG_PS_CU_EN`, `SPI_WF_LIFETIME_CNTL`, lifetime limit/status registers, `SPI_LB_*`, `SPI_GDS_CREDITS`, export/scoreboard buffer sizing, CSQ wavefront active status/counts, and P0/P1 trap-screen base/mask/GPR minimum registers. These support shader export debug options, wave ID tracking, lifetime monitoring and warning status, load-balancer wave counts, GDS credit configuration, buffer sizing, active wavefront counters, and trap-screen memory/GPR filters.
- Texture pipe start: `TD_STATUS`, `TD_SCRATCH`, `TA_CNTL`, and `TA_CNTL_AUX`. These include TD busy/scratch fields, TA credit controls, XNACK clock-gating disable, and many texture address/filtering behavior toggles. The chunk ends at `TA_CNTL_AUX__DETERMINISM_WRITEOP_READFMT_DISABLE_MASK`; remaining `TA_CNTL_AUX` masks and `TA_CNTL2` continue in the next chunk.

Field naming is descriptive. `*_LO`/`*_HI` are counter or pointer halves, `*_STATUS` and `*_STAT` expose live hardware state, `*_CNTL` and `*_CONFIG` program behavior, `*_SCRATCH_REG*` hold general scratch values, `*_ADDR`/`*_WD`/`*_MSK` describe trap/watch address and data matching, and indirect pairs such as `CP_CMD_INDEX`/`CP_CMD_DATA`, `CP_DEBUG_CNTL`/`CP_DEBUG_DATA`, `SQ_IND_INDEX`/`SQ_IND_DATA`, and SDMA microcode address/data registers require ordered accesses by the consumer.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU, AMDKFD, SDMA, display, MES, IMU, and GFX11 initialization/debug/profiling code:

1. A consumer includes `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`.
2. The consumer selects the register offset with the `mm*` macro and base index.
3. It builds or decodes a 32-bit register value using the `__SHIFT` and `_MASK` constants in this file.
4. It performs MMIO reads/writes or indirect index/data accesses through the driver register helpers while firmware, interrupts, reset code, power-management code, profiling tools, or debugfs paths coordinate the actual sequencing.

The chunk describes fields needed for SDMA performance counting, GRBM idle/fault inspection, CP queue and ring diagnostics, geometry/frontend control, SQ/SPI watchpoints and lifetime monitoring, and texture pipe configuration. It does not encode valid enum values, legal state transitions, read/write permissions, timeout policies, reset ordering, interrupt routing, or power-gating constraints; those must come from the consuming driver code and the hardware programming guide.

## State And Persistence Behavior

This file stores no software state and persists nothing by itself. It describes hardware state exposed through GC 11.0.0 registers.

The represented hardware state includes SDMA microcode address/data windows and F32 thread controls, SDMA perf counter selector/configuration and readback state, global GRBM busy/idle/fault/trap/scratch state, CP pipeline stall/busy/queue/ring/preemption diagnostics, primitive assembler and geometry frontend configuration, SQ watchpoint/interrupt/indirect command state, SPI wavefront lifetime counters and warnings, shader export debug controls, and the start of texture pipe configuration.

Persistence is hardware-defined. Some fields are durable configuration until GPU reset, suspend/resume, power gating, or driver reprogramming; some are live status bits that change as work progresses; some are latched fault or violation records; some are command/action bits such as reset, invalidate, clear, load, halt, or indirect command fields; and some are readback data windows owned by hardware or firmware. The macros do not identify access class, so consumers must preserve reserved and unrelated bits on mixed-control registers and must not infer that a full-width `0xFFFFFFFFL` field is always safe to write.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides the matching register offsets and base indices. `gc_11_0_0_default.h` provides default values for the same register generation, and firmware loaded by GFX11/MES/IMU paths supplies part of the behavior behind CP, RLC, MEC, MES, IMU, and SDMA state.

Observed include users of this generated shift/mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c`

Integration points include GFX11 ASIC initialization, SDMA setup and performance monitoring, GFX/MES/IMU firmware loading and control, KFD queue and MQD setup, display plane programming that needs GC register definitions, GPU reset/recovery, idle-wait and hang diagnostics, debugfs/register dumps, trap/watchpoint handling, shader profiling, performance-counter tools, and runtime power-management paths that must reprogram or validate volatile GC state.

## Risks And Edge Cases

- Header/offset mismatches are the primary generated-metadata risk. Pairing `gc_11_0_0_sh_mask.h` with another IP generation's offset header can compile but access the wrong register or field.
- The macros are untyped integer constants. Wrong register names, stale masks, or incorrect shifts can silently program a different bitfield, especially in dense status/control registers such as GRBM, CP, SQ, SPI, and TA controls.
- The chunk has artificial boundaries. It starts after `SDMA1_UCODE_ADDR` and ends before all `TA_CNTL_AUX` masks are present, so adjacent chunks are required for complete per-register coverage.
- Indirect register pairs require strict ordering. SDMA microcode address/data, CP command/debug index/data, and SQ indirect index/data accesses can return or update the wrong target if consumers interleave accesses without serialization.
- Status registers are live and often race with hardware progress. GRBM/CP/SQ/SPI busy, pending, clean, active, and stall bits can change between reads; timeout loops need appropriate polling, barriers, and power-state awareness.
- Soft reset, trap, invalidate, clear, load, halt, and warning/status bits may be self-clearing, sticky, write-one-to-clear, write-only, or firmware-owned. The macro file does not distinguish these semantics.
- Performance counters can produce false zeros or saturation if event selectors, enable/clear/start ordering, stop triggers, clock gating, per-instance filters, or workload placement do not match the active engine.
- CP queue/ring diagnostics and preemption fields are firmware- and scheduler-sensitive. Reading stale pointers or issuing commands during reset, preemption, MES ownership changes, or GPU recovery can misdiagnose hangs.
- Watchpoints and trap-screen registers involve address masks, VMID/context fields, and GPR thresholds. Incorrect preservation or programming can break debugging, raise unexpected traps, or miss intended memory events.
- Texture pipe and shader determinism/optimization disables in `TA_CNTL_AUX`, `SX_DEBUG_1`, and related controls can affect correctness, performance, or validation reproducibility; they should be changed only through known ASIC workarounds or documented debug paths.

## Test Signals

Useful validation is mostly build, static, and hardware/profiling coverage:

- Build coverage for all GFX11, SDMA v6, MES v11, IMU v11, display, and KFD files that include `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`.
- Generated-header consistency checks that each field has matching `__SHIFT` and `_MASK` definitions, masks align with shifts, and register names match entries in `gc_11_0_0_offset.h`.
- Static checks for non-overlapping fields within each register, except documented aliases or full-width data/status registers.
- SDMA perf counter smoke tests that clear/configure/start counters, run known SDMA copy/fill workloads, stop/read low/high values, and verify plausible nonzero or monotonic counter behavior.
- GPU idle/reset tests that poll GRBM and per-SE status before and after queue drains, soft resets, GPU recovery, suspend/resume, and runtime power transitions.
- CP diagnostics tests covering ring pointer readback, queue threshold/availability status, preemption visibility, header dumps, stalled/busy status, and privileged violation capture under controlled workloads.
- SQ/SPI debug tests for watchpoints, interrupt auto-mask behavior, indirect SQ commands, lifetime warning/status bits, active wavefront counters, and shader-rate or CU mask configuration.
- Geometry/frontend and texture-pipe validation using graphics workloads that exercise VGT, IA/WD/GE/PA, TA, and TD paths, with regression signals such as hangs, unexpected busy bits, bad primitive output, texture sampling differences, or validation-only determinism failures.
- Negative/regression indicators include counters stuck at zero or saturation, GRBM idle waits timing out, CP queue pointers not advancing, unexpected traps or violation addresses, watchpoints failing to trigger, lifetime interrupts firing unexpectedly, and failures isolated to specific GC 11.0.0 ASICs or firmware revisions.

### subset-b-002507: lines 7585-9915

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 7585-9915

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it publishes C preprocessor constants that describe the shift and mask layout of 32-bit graphics-core MMIO registers. Runtime AMDGPU and AMDKFD code pairs these constants with the matching register offset macros from `gc_11_0_0_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and golden-register programming helpers.

The selected range starts at the tail of texture-addressing control metadata, then covers GDS control/status and fault/EDC fields, render-backend depth/color block controls, global backend/address configuration, and two GCEA address-block regions for memory/IO arbitration, SDP credits, MAM controls, EDC counters, and diagnostic/error-injection controls. The final lines end inside `GCEA_DSM_CNTL2A`, so that register is only partially visible in this chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, dynamic allocations, callbacks, locks, or local includes in this slice. The exposed API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the same field.
- Register comments such as `//GDS_CNTL_STATUS` or `//GCEA_SDP_ARB_FINAL` group the field macros by hardware register.
- Address-block comments such as `// addressBlock: gc_gdsdec`, `gc_rbdec`, `gc_gceadec`, and `gc_gceadec2` group related register families.

Major register families in this chunk:

- Texture address tail: the chunk begins with remaining `TA_CNTL_AUX` masks, then defines `TA_CNTL2` point-sample acceleration, coordinate truncation, and unlit-quad elimination fields, plus `TA_STATUS` FIFO-empty and busy bits and a full-width `TA_SCRATCH` field.
- GDS decode block: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ENHANCE`, `GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`, `GDS_EDC_CNT`, `GDS_EDC_GRBM_CNT`, `GDS_EDC_OA_DED`, `GDS_DSM_CNTL`, `GDS_EDC_OA_PHY_CNT`, `GDS_EDC_OA_PIPE_CNT`, and `GDS_DSM_CNTL2` describe global data share busy state, clamp/status bits, auto-increment/restore behavior, protection-fault attribution, VM fault attribution, ECC/EDC counters, per-ME/pipe/physical/PQ EDC reporting, and diagnostic scan/error-injection controls.
- Render backend/depth block: `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_DEBUG5`, `DB_DEBUG6`, and `DB_DEBUG7` expose many ASIC workaround, bypass, panic, clock-gating, conflict, coherency, VRS, HTILE, DTT, OSB, and test controls. Stutter, credit, watermark, FIFO-depth, last-of-burst, memory-arbiter, exception, and fine-grain clock-gating registers describe depth-buffer pipeline timing, resource limits, and error handling.
- RB/GB/CB configuration: `CC_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `CC_RB_DAISY_CHAIN`, `GB_ADDR_CONFIG_READ`, `CB_HW_CONTROL_4`, `CB_HW_CONTROL_3`, `CB_HW_CONTROL`, `CB_HW_CONTROL_1`, `CB_HW_CONTROL_2`, `CB_DCC_CONFIG`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, `CB_FGCG_SRAM_OVERRIDE`, `CHICKEN_BITS`, and `CB_CACHE_EVICT_POINTS` cover render-backend enablement/harvesting, address tiling geometry, daisy-chain wiring, color-buffer hardware queues, DCC cache sizing, arbitration, SRAM clock-gating override, and cache eviction thresholds.
- GCEA DRAM/IO arbitration: DRAM and IO read/write `CLI2GRP_MAP0/1` registers map client IDs 0 through 31 into four groups. `GRP2VC_MAP`, `LAZY`, `CAM_CNTL`, page/group burst limits, priority age/queueing/fixed/urgency coefficients, urgency masking, and quantization threshold registers define how those groups are assigned virtual channels and how request age, urgency, accumulation, reorder depth, and burst behavior affect arbitration.
- GCEA SDP controls: `GCEA_SDP_ARB_FINAL` defines DRAM/GMI/IO burst limits, burst multiplier, read-only virtual-channel flags, error event/halt behavior, burst stretch, and DRAM/GMI read/write throttles. `GCEA_SDP_IO_PRIORITY`, `GCEA_SDP_CREDITS`, tag reserve, and VCC reserve registers define final SDP priority and credit reservation policy.
- GCEA miscellaneous/MAM/EDC/DSM: `GCEA_MISC` selects relative priority modes, early write-return behavior, link-manager thresholds, command-stream preference, and write-to-read switching policy. `GCEA_LATENCY_SAMPLING` selects sampler traffic domains, operation classes, and virtual-channel masks. `GCEA_MAM_CTRL2` and `GCEA_MAM_CTRL` configure MAM/ARAM/DBIT tracking, flush behavior, interrupt generation, ring-buffer sizing, and address high bits. `GCEA_EDC_CNT` and `GCEA_EDC_CNT2` expose SEC/DED/SED counters for DRAM, GMI, IO, return-tag, page, and MAM memories. `GCEA_DSM_CNTL`, `GCEA_DSM_CNTLA`, and `GCEA_DSM_CNTL2` define DSM irritator data, single-write controls, and error-injection enable/delay fields; `GCEA_DSM_CNTL2A` begins in this chunk and continues after line 9915.

Most constants use the generated `0x...L` literal form. Several fields are full-width masks such as `TA_SCRATCH__SCRATCH_MASK`, `DB_DEBUG7__SPARE_BITS_MASK`, and `CHICKEN_BITS__SPARE_MASK`; full-width masks are still just packing definitions and do not imply that all bits are safe to write.

## Control Flow

This header has no runtime control flow. Its operational flow is indirect:

1. GC 11 code includes `gc/gc_11_0_0_sh_mask.h` with the corresponding `gc/gc_11_0_0_offset.h`.
2. A driver path chooses a register address using `reg*` offset macros, for example `regGDS_CONFIG`, `regDB_DEBUG4`, `regCB_DCC_CONFIG`, `regGCEA_SDP_ARB_FINAL`, `regGCEA_MISC`, or `regGCEA_DSM_CNTL2A`.
3. The code composes or decodes register values using the shift/mask macros from this header through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD`.
4. The result is read from or written to hardware with SOC15 register helpers, firmware tables, golden-register programming, queue setup, reset, power-management, or debug/error paths.

Known consumers in this tree include `amdgpu/gfx_v11_0.c`, `amdgpu/gfxhub_v3_0.c`, `amdgpu/sdma_v6_0.c`, `amdgpu/mes_v11_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/imu_v11_0_3.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdkfd/kfd_mqd_manager_v11.c`, `amdkfd/kfd_device_queue_manager_v11.c`, and `display/amdgpu_dm/amdgpu_dm_plane.c`. For this chunk specifically, `gfx_v11_0.c` reads `TA_CNTL2__TRUNCATE_COORD_MODE`, uses `GB_ADDR_CONFIG` fields to derive render-backend layout, and exposes `regGDS_PROTECTION_FAULT` in debug register lists; IMU golden tables program `regGCEA_SDP_ARB_FINAL` with masks/value pairs.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes bit positions for hardware state owned by the GPU.

The represented hardware state includes texture-addressing status, GDS busy/fault/EDC/diagnostic state, DB pipeline debug/workaround bits, depth-buffer credits/watermarks/FIFO depths, RB/CB/GB harvesting and tiling configuration, DCC cache configuration, arbitration queues and weights, GCEA client grouping and virtual-channel mapping, SDP credit reservation, MAM/ARAM tracking state, and GCEA EDC counters/error-injection knobs.

Persistence depends on the underlying register semantics, not on this header. Some fields are configuration that remains until reset, suspend/resume restore, power-gating restore, firmware reinitialization, or explicit reprogramming. Some are live status bits, sticky fault indicators, hardware-owned counters, diagnostic strobes, write-one-to-clear fields, or test/error-injection fields. The header does not encode read-only/write-only, self-clearing, latched, privileged, broadcast, per-instance, golden-default, or reserved-bit behavior, so call sites must preserve unrelated fields and follow ASIC programming-guide ordering.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides the actual register offsets and base indices. In that file, this chunk's registers are represented by entries such as `regGDS_CONFIG`, `regDB_DEBUG`, `regDB_DEBUG4`, `regCB_DCC_CONFIG`, `regGCEA_SDP_ARB_FINAL`, `regGCEA_MISC`, and `regGCEA_DSM_CNTL2A`.

This generated metadata integrates with:

- AMDGPU GC 11 initialization and reset code, especially `gfx_v11_0.c`, which reads and writes many GC fields through `REG_SET_FIELD`/`REG_GET_FIELD`.
- GFX hub VM/cache code in `gfxhub_v3_0.c`; that file mostly uses neighboring VM macros, but it is compiled in the same GC 11 register namespace and demonstrates the expected shift/mask helper pattern.
- IMU/RLC firmware and golden-register setup in `imu_v11_0.c` and `imu_v11_0_3.c`, where `regGCEA_SDP_ARB_FINAL` is programmed by table-driven mask/value writes.
- KFD/MES/MQD paths for compute queue setup and scheduling, which include the same GC 11 generated header and rely on consistent field definitions across CP, GDS, and shader-related register families outside and around this chunk.
- Display/plane code that includes GC 11 masks for tiling/address configuration interoperability with DCC, render-backend, and memory layout metadata.
- Hardware diagnostics and debugfs-style paths that expose or decode `GDS_PROTECTION_FAULT`, busy/status, EDC, and DSM/error-injection registers.

The chunk is part of a larger generated header. Adjacent chunks are required for the complete `TA_CNTL_AUX` definition before line 7585 and the complete `GCEA_DSM_CNTL2A`/later GCEA definitions after line 9915.

## Risks And Edge Cases

- Header/offset mismatch is the main integration risk. Using GC 11.0.0 masks with a different GC offset header can compile but program wrong fields or wrong registers.
- The constants are untyped preprocessor macros. Field misuse can silently corrupt unrelated bits in control registers, especially debug/workaround, arbitration, and error-injection registers with dense bit layouts.
- Reserved and spare fields are explicitly present, including `UNUSED`, `SPARE`, `CHICKEN_BITS`, and full-width debug/scratch definitions. Call sites must not infer that a visible mask is safe to set on production hardware.
- GDS protection-fault and VM-protection-fault fields are attribution-sensitive. Misdecoded SE/SA/WGP/SIMD/wave/VMID/address fields can send debugging, fault recovery, or telemetry down the wrong path.
- EDC and DSM registers are reliability-sensitive. Incorrect counter decoding, single-write/irritator settings, or error-injection enables can hide real memory errors or create artificial faults during normal operation.
- DB and CB debug/control registers include many ASIC workaround, bypass, panic, coherency, clock-gating, and cache behavior bits. Small mistakes may only surface as hangs, depth/stencil corruption, DCC corruption, VRS artifacts, power regressions, or workload-specific performance cliffs.
- GB address and backend fields drive tiling and render-backend topology. Incorrect masks or stale assumptions around `GB_ADDR_CONFIG`, backend disabling, daisy-chain fields, or `GB_ADDR_CONFIG_READ` can break memory layout, RB harvesting, or address calculations.
- GCEA arbitration knobs can create starvation or severe latency/bandwidth regressions. Client-to-group maps, group-to-VC maps, urgency masking, priority coefficients, CAM depths, and burst limits need ASIC-specific defaults and workload validation.
- `GCEA_SDP_ARB_FINAL` includes error event/halt and throttle bits. Golden-register values or firmware tables that mask the wrong bits can alter final fabric behavior for DRAM, GMI, or IO traffic.
- The chunk boundary is artificial. `TA_CNTL_AUX` is only a tail fragment and `GCEA_DSM_CNTL2A` is only the first six shift fields here, so the later merge lane must reconcile adjacent chunks before producing a whole-file report.

## Test Signals

Useful validation is mostly generated-header consistency, build coverage, and hardware smoke/regression coverage:

- Build AMDGPU, AMDKFD, MES, SDMA, display, and IMU/RLC paths that include `gc_11_0_0_sh_mask.h` together with `gc_11_0_0_offset.h`.
- Generated-header checks that every visible `__SHIFT` has the intended matching `_MASK`, masks align with shifts, fields do not overlap within a register except documented aliases/full-register fields, and register names match offset-header entries.
- Static comparison against the authoritative generated register database for GC 11.0.0, especially for replicated DRAM/IO client maps, urgency masks, quantization thresholds, and DSM/EDC counter layouts.
- Golden-register programming tests for `regGCEA_SDP_ARB_FINAL` and neighboring IMU/RLC tables, verifying mask/value pairs leave reserved bits and non-targeted fields unchanged.
- GPU bring-up, reset, suspend/resume, runtime power-management, and SR-IOV tests that exercise DB/CB/GB/GDS/GCEA state initialization and restoration.
- GDS tests covering queue use of global data share, GWS/OA interactions, protection faults, VM protection faults, EDC counter reporting, and diagnostic/error-injection paths on controlled hardware.
- Graphics tests stressing depth/stencil, HTILE, VRS, DCC, render-backend harvesting, tiling, MSAA/subtile layouts, cache eviction, and last-of-burst behavior; failures can appear as corrupted depth/color output, hangs, or workload-specific performance regressions.
- Memory and fabric performance tests for DRAM, GMI, and IO traffic to catch GCEA client grouping, virtual-channel assignment, priority, urgency, CAM, lazy accumulation, burst, and throttle mistakes.
- Fault-injection and reliability tests for GCEA and GDS EDC/DSM controls, with explicit checks that injected errors are reported only in the expected SEC/DED/SED counters and that production paths leave injection disabled.

### subset-b-002508: lines 9916-12288

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 9916-12288

## Scope

This chunk covers generated shift and mask macros from `gc_11_0_0_sh_mask.h` for a GC 11.0.0 AMD GPU register header. The lines span the tail of one `GCEA_DSM_CNTL2A` definition and then register field layouts for several GC address blocks:

- `gc_gceadec3`: GCEA error/status, GL2C crossbar credit, probe, EDC, and SDP fields.
- `gc_spipdec2`: SPI queue/event and throttle control fields.
- `gc_rmi_rmidec`: RMI request/return path, UTC/UTCL1 controls, scoreboard, xbar, formatter, and spare/debug fields.
- `gc_pmmdec`: GCR PIO and PMM control/status fields.
- `gc_utcl1dec`: UTCL1 bypass, allocation logging, and busy/status fields.
- `gc_gcvmsharedpfdec`: physical-function shared GCMC aperture, VM aperture, GCUTCL2, and GCVML2 register fields.
- `gc_gcvml2pfdec`: physical-function VM L2 cache, protection fault, identity aperture, throttle, cache dump, translation assist, bank selection, and credit-safety fields.
- `gc_gcvmsharedvcdec`: virtual-client shared aperture and L1 TLB fields.
- `gc_gcvml2vcdec`: per-context VM controls and invalidate-engine semaphore/request fields.

The chunk exports preprocessor constants only. It defines no C functions, structs, storage, or executable control flow. Its behavior is the ABI-like contract that lets driver code build, update, and decode SOC15 MMIO register values without hard-coded bit positions.

## Purpose

The header gives bitfield metadata for GC 11.0.0 registers. Every field appears as a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used when encoding or extracting a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate that field in a 32-bit register value.

These macros are consumed by register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. Address values and reset defaults live in sibling generated files such as `gc_11_0_0_offset.h` and `gc_11_0_0_default.h`; this file supplies only field positions and masks.

The largest functional area in this chunk is graphics VM setup and invalidation. It defines the field contract used by the GFXHUB layer to configure VM L2 cache policy, page table depth, identity aperture behavior, protection fault handling, and TLB/cache invalidation requests.

## Important Macro Families

### GCEA and SPI

The GCEA section contains masks for GL2C crossbar and error-handling controls. Notable registers include:

- `GCEA_GL2C_XBR_CREDITS` and `GCEA_GL2C_XBR_MAXBURST`, which describe DRAM/IO read and write credit limits, reserves, max bursts, and combiner flush behavior.
- `GCEA_PROBE_CNTL` and `GCEA_PROBE_MAP`, which describe probe request/response delay, filtering, channel address mapping to right-side GL2C instances, and interleave size.
- `GCEA_ERR_STATUS`, whose fields expose SDP read/write response status, data status, dataparity error, fatal interrupt controls, busy-on-error behavior, and clear/status bits.
- `GCEA_MISC2`, `GCEA_RRET_MEM_RESERVE`, `GCEA_EDC_CNT3`, and `GCEA_SDP_ENABLE`, which describe request blocking, arbitration priority, virtual-channel reservation, EDC counters, and SDP write mux enablement.

The SPI portion is small and defines `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL` fields for queue/event behavior and export throttling.

### RMI and UTCL1

The `gc_rmi_rmidec` block defines the return memory interface and its connection to UTCL1. Important groups include:

- `RMI_GENERAL_CNTL` and `RMI_GENERAL_CNTL1`: demux, skid FIFO, ordering, clock-gating, and protocol options.
- `RMI_GENERAL_STATUS` and `RMI_SUBBLOCK_STATUS0..3`: busy bits and FIFO occupancy/free-space counters for demux, xbar, scoreboard, TCIW formatters, return formatters, consumer FIFOs, and skid/probe FIFOs.
- `RMI_XBAR_CONFIG`, `RMI_XBAR_ARBITER_CONFIG`, and `RMI_XBAR_ARBITER_CONFIG_1`: xbar mux override, arbiter modes, stalls, timer overrides, and round-robin weights.
- `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_DEMUX_CNTL`, and `RMI_TCIW_FORMATTER0/1_CNTL`: probe combine/depth limits, demux arbitration overrides, write combine windows, max inflight requests, reorder disable, and all-fault-return-data bits.
- `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, `RMI_UTC_UNIT_CONFIG`, and `RMI_UTCL1_STATUS`: XNACK timing, VM permission mode, response/fault modes, invalidation controls, cache/FIFO reductions, snoop/ack controls, TMZ request enablement, and fault/retry/PRT status.
- `RMI_SCOREBOARD_CNTL` and `RMI_SCOREBOARD_STATUS0..2`: RB flush completion, VMID invalidation progress, running/snapshot counters, underflow/overflow flags, timestamp flush status, and CP VMID invalidation state.
- `RMI_RB_GLX_CID_MAP` and `RMI_SPARE*`: client-id mapping for CB/DB paths and spare knobs for no-fill behavior, reorder bypass, early ack, XNACK return override, address masks, and clock-gating disables.

The standalone `gc_utcl1dec` block then defines `UTCL1_CTRL_1`, `UTCL1_ALOG`, and `UTCL1_STATUS`, which provide broader UTCL1 bypass controls, forced invalidation/all-done bits, page-size selection, allocation logging controls, and hit/miss/invalidation busy signals.

### PMM and GCR PIO

The PMM block provides `GCR_PIO_CNTL`, `GCR_PIO_DATA`, `PMM_CNTL`, and `PMM_STATUS` fields. These cover PIO index/write/read controls, GCR data payload, PMM timeout and force controls, timeout actions, state, and status/error flags. Consumers can use these masks to drive low-level performance or power-management monitor access paths.

### Shared VM Aperture and Memory Policy

The `gc_gcvmsharedpfdec` and `gc_gcvmsharedvcdec` blocks define memory aperture and address-range fields:

- PF/shared fields: top-of-DRAM slots, TOM2 lower/upper enable/ranges, framebuffer offset, system aperture default address LSB/MSB, VM steering, memory power light-sleep setup/hold, cacheable DRAM range, local sysmem range, APT controls, local FB range, FB-address lock, FB no-alloc policy, GCUTCL2 harvest bypass/fault status, and GCUTCL2 clock/busy controls.
- VC/shared fields: framebuffer base/top, AGP top/bottom/base, system aperture low/high, and `GCMC_VM_MX_L1_TLB_CNTL` fields for L1 TLB enablement, system access mode, unmapped aperture access, advanced driver model, ECO bits, and memory type.

These fields are part of the GPU memory-controller programming surface and are paired with offset/default definitions in sibling generated headers.

### GCVM L2, Faults, and Translation Assist

The `gc_gcvml2pfdec` block is the densest part of this chunk. It describes:

- `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_L2_CNTL4`, and `GCVM_L2_CNTL5`: VM L2 enablement, fragment processing, PTE/PDE endian modes, cache split/effective sizes, invalidate controls, PDE cache size, cache associativity, force-miss bits, tap physical-request controls, IFIFO transaction limits, fragment sizing, walker priority client id, walker noalloc/MTYPE enables, and clock-gating options.
- `GCVM_L2_STATUS`: L2 busy, context-domain busy vector, and parity error flags for 4K/bigK PTE caches and PDE caches.
- `GCVM_DUMMY_PAGE_FAULT_*`: dummy page fault enable, address mode, compare MSBs, and low/high address components.
- `GCVM_L2_PROTECTION_FAULT_CNTL`, `GCVM_L2_PROTECTION_FAULT_CNTL2`, `GCVM_L2_PROTECTION_FAULT_MM_CNTL3/4`, `GCVM_L2_PROTECTION_FAULT_STATUS`, and fault address/default address registers: controls for clearing and updating fault status, default enable bits for fault classes, retry/no-retry interrupt selection by client id, crash-on-fault bits, active migration PTE handling, retry fault interrupt enable, fault source fields, VMID/VF/VFID, PRT flag, and recorded logical/default physical page addresses.
- `GCVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `GCVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`: identity-mapped aperture bounds and physical offset.
- `GCVM_L2_MM_GROUP_RT_CLASSES`, `GCVM_L2_BANK_SELECT_RESERVED_CID*`, `GCVM_L2_BANK_SELECT_MASKS`: routing and bank selection metadata.
- `GCVM_L2_CACHE_PARITY_CNTL`, `GCVM_L2_ICG_CTRL`, `GCVM_L2_CGTT_BUSY_CTRL`: parity forcing/checking and clock/busy override fields.
- `GCVML2_WALKER_*_THROTTLE_*`: macro/micro walker throttle time and fetch limit fields.
- `GCVM_L2_PTE_CACHE_DUMP_CNTL` and `GCVM_L2_PTE_CACHE_DUMP_READ`: PTE cache dump selection and data readout.
- `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*` and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_*`: explicit translation-assist request fields for address, VMID, VFID/VF, GPA, permissions, client id, request bit, and response fields for translated address, permissions, fragment size, snoop/SPA/IO/TMZ/no-PTE/MTYPE/memlog/NACK/noalloc/ACK.
- `GCUTCL2_CREDIT_SAFETY_*` and `GCVML2_*_CREDIT_SAFETY_*`: credit values and update bits for return, invalidation, fault interrupt, and walker fetch paths.

### GCVM Contexts and Invalidation Engines

The `gc_gcvml2vcdec` block defines repeated `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` macros. Each context has the same field layout:

- Enablement and page-table shape: `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, and `PAGE_TABLE_BLOCK_SIZE`.
- Retry controls: `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` and `RETRY_OTHER_FAULT`.
- Interrupt/default enable bits for range, dummy page, PDE0, valid, read, write, and execute protection faults.

The chunk then defines `GCVM_CONTEXTS_DISABLE`, a bitmap that disables contexts 0 through 15, followed by `GCVM_INVALIDATE_ENG0_SEM` through `GCVM_INVALIDATE_ENG17_SEM` semaphore bits. It also defines invalidate request layouts for engines 0 through 9 within this line range. Each request includes per-VMID invalidate bits, flush type, invalidation of L2 PTEs and PDE0/PDE1/PDE2, L1 PTE invalidation, protection-fault-status-address clear, request logging, and 4K-only invalidation.

## Control Flow and State Behavior

This header does not execute any control flow and persists no software state. It is a compile-time description of hardware state layout. Runtime control flow appears in consumers that include this header. For example, `amdgpu/gfxhub_v2_0.c` and `amdgpu/gfxhub_v2_1.c` use `REG_SET_FIELD` with `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_CONTEXT0_CNTL`, and `GCVM_INVALIDATE_ENG0_REQ` to configure GFXHUB VM behavior, issue invalidations, and derive context/invalidation register distances. Those consumers read and write hardware MMIO registers through SOC15 helper macros.

The persistent state affected by these macros is hardware state, not C memory in this header. Important persistent hardware-visible state includes VM context enable bits, retry/default fault policy, L2 cache configuration, fault status latches, dummy/default fault addresses, identity apertures, invalidate request/semaphore state, FIFO/scoreboard busy flags, and performance/debug counters. Some fields are command-like or write-one/control bits, such as invalidate requests, clear fault status fields, forced invalidation toggles, or update bits for credit-safety registers. Consumers must respect hardware sequencing and polling rules from the corresponding driver code and hardware documentation.

## Dependencies and Integration Points

This chunk depends on the naming convention shared by generated AMD ASIC register headers:

- `gc_11_0_0_offset.h` supplies `reg...`, `mm...`, and base-index address constants for the same register names.
- `gc_11_0_0_default.h` supplies reset/default values, such as defaults for `GCVM_L2_CNTL`, `GCVM_CONTEXT0_CNTL`, `GCVM_INVALIDATE_ENG0_REQ`, `GCEA_ERR_STATUS`, and `RMI_GENERAL_STATUS`.
- Register helper macros in the AMDGPU DRM driver consume the `__SHIFT` and `_MASK` constants to safely compose bitfields.

Observed integration points in the source tree include:

- `amdgpu/gfxhub_v2_0.c` and `amdgpu/gfxhub_v2_1.c`, which program GFXHUB VM L2, contexts, and invalidate requests using these GCVM macros.
- `amdgpu/imu_v11_0_3.c`, which lists golden/default-like GCVM register programming values.
- `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdkfd/kfd_device_queue_manager_v11.c`, and `amdkfd/kfd_mqd_manager_v11.c`, which include this GC 11 mask header for queue/KFD interactions.
- `display/amdgpu_dm/amdgpu_dm_plane.c`, which includes the header for GC 11 display-plane related register field access.
- Earlier or sibling ASIC generations reuse similar register names, so edits must not assume a field layout is portable across GC versions. For example, GC 12 headers contain similar names but may shift fields differently.

## Risks

- Bitfield accuracy is critical. A wrong shift or mask can write unrelated hardware bits, causing VM faults, cache coherency failures, invalidation hangs, interrupts being missed or over-triggered, or GPU reset.
- Repeated context and invalidate-engine macro families are easy to update inconsistently. Engines and contexts have mostly identical layouts; one typo in a repeated mask may affect only a subset of VMIDs or invalidation engines.
- Cross-generation similarity is a trap. Code that includes `gc_11_0_0_sh_mask.h` must pair it with matching GC 11.0.0 offsets/defaults. Similar GC 12 or GC 10 names cannot be blindly mixed.
- Some fields represent status/clear, semaphore, toggle, or request semantics. Treating them as ordinary persistent configuration bits can lose fault logs, force stale invalidations, or break synchronization with hardware.
- This generated header contains no validation logic. Compile success only proves macro names and syntax are present, not that hardware programming sequences are correct.

## Test and Validation Signals

Useful validation for this chunk is mostly integration-level:

- Build coverage for AMDGPU/KFD/display sources that include `gc/gc_11_0_0_sh_mask.h`; this catches missing or renamed macros.
- Compile-time references in `gfxhub_v2_0.c` and `gfxhub_v2_1.c` should continue to resolve for `GCVM_L2_*`, `GCVM_CONTEXT*`, and `GCVM_INVALIDATE_ENG*_REQ` fields.
- Runtime VM tests should exercise GPU VM setup, context programming, page table depth/block-size handling, invalidation paths, and retry/no-retry fault behavior.
- Fault-injection or fault-observation tests should verify `GCVM_L2_PROTECTION_FAULT_STATUS`, fault address registers, retry/PRT interrupts, and GCEA/RMI error status reporting.
- Suspend/resume and reset tests should verify that persistent hardware state programmed from these macros is saved, restored, or reinitialized by the owning GFXHUB/GMC code.
- Debug/performance validation can inspect RMI busy/status, UTCL1 allocation logging, PTE cache dump controls, and credit-safety update paths when diagnosing hangs or VM pressure.

## Unresolved Cross-Chunk References

This chunk starts after earlier `GCEA_DSM_CNTL2A` definitions have already begun, and it ends mid-family after `GCVM_INVALIDATE_ENG9_REQ`; later chunks should cover invalidate request engines beyond 9 and any following GCVM registers. The final merged per-file report should connect this chunk with earlier/later chunks to describe the full generated header, include guards, any preceding register families, and remaining invalidate engine definitions.

### subset-b-002509: lines 12289-14934

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 12289-14934

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It has no executable C control logic; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, MES, SDMA, display, GFXHUB, and SOC21 code to compose and decode 32-bit MMIO register values. The companion offset and base-index definitions live in `gc_11_0_0_offset.h`.

The selected range covers GCVM invalidate engines and VM context address registers, GCVM L2/UTC performance counter controls, SR-IOV/MARC virtualization address controls, shader-program resource registers for pixel/geometry/hull/local shader stages, and the front half of compute dispatch state. Although the subtree is under `ceph-client`, this header is AMD graphics hardware metadata, not distributed-filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, allocations, locks, callbacks, or direct MMIO helpers in this range. The exposed interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding in-register bit mask.
- Consumers pair these masks with `reg<REGISTER>` and `reg<REGISTER>_BASE_IDX` symbols from `gc_11_0_0_offset.h`, then use AMDGPU helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Major register families in this chunk:

- `GCVM_INVALIDATE_ENG10_REQ` through `GCVM_INVALIDATE_ENG17_REQ` complete the per-engine GCVM invalidate request set that started in an earlier chunk. Each request has a 16-bit `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, invalidation selects for L2 PTEs/PDE0/PDE1/PDE2 and L1 PTEs, plus `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY`.
- `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK` define per-VMID acknowledgement and semaphore bits for invalidate engines 0-17.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through engine 17 provide invalidation address-range low/high masks. Low halves use bit 12 alignment (`0xFFFFF000L`), while high halves expose a 24-bit high address field.
- `GCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_*` through `GCVM_CONTEXT15_PAGE_TABLE_BASE_ADDR_*`, then matching `START_ADDR_*` and `END_ADDR_*`, define per-VMID page-table base and virtual address aperture registers. Low halves are aligned from bit 12; high halves expose the upper physical or virtual address bits.
- `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `GCVM_L2_CONTEXT0` through `CONTEXT15` variants define small-page and big-page PTE cache fragment sizes plus bank selection.
- `GCVML2_PERFCOUNTER2_*`, `GCMC_VM_L2_PERFCOUNTER_*`, `GCUTCL2_PERFCOUNTER_*`, `GCVML2_PERFCOUNTER2_*_SELECT/SELECT1/MODE`, `GCMC_VM_L2_PERFCOUNTER0-7_CFG`, and `GCUTCL2_PERFCOUNTER0-3_CFG` expose GCVM L2 and UTC L2 performance counter result, select, mode, enable, clear, trigger, and saturate controls.
- `GCMC_VM_FB_SIZE_OFFSET_VF0` through `VF15` define per-virtual-function framebuffer size and offset fields for SR-IOV style partitioning.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID` and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` define VMID translation-bypass/GPA-mode masks and a translation-assist enable bit.
- `GCMC_VM_MARC_BASE_*`, `GCMC_VM_MARC_RELOC_*`, `GCMC_VM_MARC_LEN_*`, and `GCMC_VM_MARC_PFVF_MAPPING_0-15` define 16 MARC windows with base, relocation, length, enable, readonly, and PF/VF mapping fields. Low base/reloc/length fields are page-aligned from bit 12; high fields use 20-bit masks.
- `GCUTC_TRANSLATION_FAULT_CNTL0/1` defines the default physical page address and IO/SPA/SNOOP attributes used for translation-fault fallback behavior.
- `SPI_SHADER_PGM_RSRC4_PS`, `SPI_SHADER_PGM_CHKSUM_PS`, `SPI_SHADER_PGM_RSRC3_PS`, `SPI_SHADER_PGM_LO/HI_PS`, `SPI_SHADER_PGM_RSRC1_PS`, `SPI_SHADER_PGM_RSRC2_PS`, `SPI_SHADER_USER_DATA_PS_0-31`, `SPI_SHADER_REQ_CTRL_PS`, and `SPI_SHADER_USER_ACCUM_PS_0-3` define pixel shader program base, resource sizing, CU enablement, trap/checksum/image flags, user SGPR payloads, request throttling, and accumulator contribution fields.
- Geometry/tessellation shader families mirror the same pattern: `SPI_SHADER_PGM_*_GS`, `SPI_SHADER_USER_DATA_GS_0-31`, `SPI_SHADER_GS_MESHLET_DIM`, `SPI_SHADER_GS_MESHLET_EXP_ALLOC`, `SPI_SHADER_REQ_CTRL_ESGS`, `SPI_SHADER_USER_ACCUM_ESGS_*`, `SPI_SHADER_PGM_*_ES`, `SPI_SHADER_PGM_*_HS`, `SPI_SHADER_USER_DATA_HS_0-31`, `SPI_SHADER_REQ_CTRL_LSHS`, `SPI_SHADER_USER_ACCUM_LSHS_*`, and `SPI_SHADER_PGM_LO/HI_LS`.
- `COMPUTE_DISPATCH_INITIATOR` starts the compute dispatch register set with shader enable, partial-threadgroup, ordering, cache invalidation, tunnel, restore, wave32, AMP shader, and preemption-disable fields.
- `COMPUTE_DIM_*`, `COMPUTE_START_*`, and `COMPUTE_NUM_THREAD_*` describe grid dimensions, starting coordinates, and full/partial thread counts per X/Y/Z dimension.
- `COMPUTE_PGM_LO/HI`, `COMPUTE_DISPATCH_PKT_ADDR_*`, `COMPUTE_DISPATCH_SCRATCH_BASE_*`, `COMPUTE_PGM_RSRC1/2/3`, `COMPUTE_VMID`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_DESTINATION_EN_SE0-3`, `COMPUTE_STATIC_THREAD_MGMT_SE0-7`, `COMPUTE_TMPRING_SIZE`, `COMPUTE_REQ_CTRL`, `COMPUTE_RELAUNCH*`, `COMPUTE_WAVE_RESTORE_ADDR_*`, `COMPUTE_USER_DATA_0-15`, `COMPUTE_DISPATCH_TUNNEL`, `COMPUTE_DISPATCH_END`, and `COMPUTE_NOWHERE` define compute shader program address/resources, dispatch packet and scratch pointers, VMID, occupancy limits, CU masks, thread-management masks, temporary-ring sizing, request throttling, relaunch/restore payloads, user data, and dispatch termination/data sink registers.

The chunk has 2,646 source lines, 2,070 `#define` lines, 1,033 shift macros, 1,037 mask macros, and 562 register/comment sections.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by driver code and the hardware blocks:

1. GC 11 code includes `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`.
2. The driver selects a register using a `reg*` offset and base-index macro from the offset header.
3. It composes or extracts register fields with the shift/mask macros in this header, commonly through `REG_SET_FIELD` or `REG_GET_FIELD`.
4. SOC15 MMIO helpers perform the actual read or write, while the GFXHUB VM walker, GCVM L2/UTCL2, shader front-end, compute scheduler, firmware/MES, KFD queue management, and GPU hardware define the ordering and side effects.

The chunk describes fields needed for TLB/cache invalidation request/ack handling, VM context programming, per-PF/VF virtualization windows, performance counter configuration, shader program state, and compute dispatch setup. It does not encode the sequencing for VM context updates, invalidate polling, shader upload, command submission, ring scheduling, memory barriers, reset handling, or preemption.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state in GC 11 registers.

The represented state includes invalidate-engine request bits and acknowledgements, invalidate address ranges, per-context page-table bases and virtual apertures, PTE cache fragment sizing, GCVM/UTCL2 performance counter selectors/results, virtual-function framebuffer partitioning, translation bypass/assist controls, MARC remap windows and PF/VF visibility, translation fault defaults, shader code base addresses, shader resource declarations, user data registers, shader request scheduling controls, compute grid dimensions, dispatch packet/scratch/program pointers, compute VMID, occupancy/CU routing controls, temporary ring sizing, restart/relaunch/restore data, and dispatch-end payloads.

Persistence is hardware-defined. Some fields are durable configuration until reset or power-gating, such as page-table bases, VM apertures, MARC windows, shader resource registers, and compute resource limits. Some fields are live hardware-owned status or counter values, such as invalidate acknowledgements and performance counter results. Some bits act like action requests or clears, such as invalidate requests, `CLEAR`, `CLEAR_ALL`, relaunch events, fault-status clear, or log/capture style bits. The masks do not state read-only, write-only, sticky, self-clearing, write-one-to-clear, or reserved-bit semantics; consumers must follow the GC 11 programming guide and preserve unrelated fields during read-modify-write operations.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`. Representative matching offsets include `regGCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`, `regGCMC_VM_MARC_BASE_LO_0`, `regSPI_SHADER_PGM_RSRC4_PS`, and `regCOMPUTE_DISPATCH_INITIATOR`.

Observed include sites in this tree include `amdgpu/gfx_v11_0.c`, `amdgpu/gfxhub_v3_0.c`, `amdgpu/mes_v11_0.c`, `amdgpu/sdma_v6_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/soc21.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdkfd/kfd_device_queue_manager_v11.c`, `amdkfd/kfd_mqd_manager_v11.c`, `display/amdgpu_dm/amdgpu_dm_plane.c`, and `amdgpu/amdgpu_display.c`. That inclusion pattern matches the register families in this chunk: GFXHUB VM management, queue/MQD and MES dispatch state, shader setup, reset/firmware support, display/GFX integration, and SDMA/SOC-level register access.

Important integration points are VMID/context initialization, page table base/start/end programming, TLB invalidation and ACK polling, page-fault/default-address setup, SR-IOV PF/VF framebuffer/MARC isolation, GCVM performance telemetry, shader program resource setup for graphics pipelines, KFD/MES compute queue state, command processor dispatch packets, scratch memory programming, preemption/relaunch/restore, thread trace/debug controls, and GPU reset/suspend/resume flows that must restore hardware state.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. Pairing `gc_11_0_0_sh_mask.h` with a different GC revision's offset header can compile while addressing the wrong bits.
- The range starts at the tail of `GCVM_INVALIDATE_ENG9_REQ` and ends after `COMPUTE_NOWHERE`; adjacent chunks are required for complete first-family context and for later registers in the same generated header.
- The macros are untyped constants. Accidentally mixing `GCVM_CONTEXTn`, `GCMC_VM_MARC_*_n`, shader-stage suffixes (`PS`, `GS`, `HS`, `LSHS`, `ESGS`), or compute resource registers can silently program the wrong VMID, VF window, shader stage, or dispatch resource.
- Address fields are alignment-sensitive. Many low halves begin at bit 12 or expose only high bits, so consumers must shift and mask page-aligned GPU addresses correctly.
- Invalidate request/ack sequencing is concurrency-sensitive. Drivers must avoid losing requests, must poll the correct engine/VMID ACK bits, and must handle timeouts or protection-fault clear/log bits without racing other VM work.
- VM context and MARC fields are security-sensitive. Incorrect PF/VF mapping, translation bypass, GPA mode, readonly, default fault address, or aperture limits can break isolation or route memory accesses unexpectedly.
- Performance counter fields include enables, clears, trigger controls, compare modes, and saturate behavior. Writing a full-width mask as a literal value can clear or stop counters instead of only selecting events.
- Shader program resource fields encode ABI-sensitive compiler and pipeline metadata: VGPR/SGPR counts, scratch, LDS, user SGPR counts, trap presence, exception enables, FP mode, WGP mode, CU enablement, meshlet dimensions, and image operation flags. Wrong values can cause shader hangs, invalid waves, memory faults, or bad rendering.
- Compute dispatch fields combine hardware-owned state and software-programmed state. VMID, scratch/program addresses, thread counts, CU masks, relaunch payloads, and wave restore addresses must match queue/MQD state and command processor expectations.
- Full-width `0xFFFFFFFFL` data masks do not imply safe blind writes. Many are addresses, user data, counters, checksums, or payload registers whose interpretation depends on stage, queue, firmware, or dispatch context.
- Reserved fields and stage-specific aliases should be preserved unless the relevant ASIC documentation explicitly requires a value.

## Test Signals

Useful validation is primarily build coverage, generated-header consistency, and hardware/driver smoke testing:

- Build AMDGPU, AMDKFD, MES, display, SDMA, GFXHUB, and SOC21 code that includes `gc_11_0_0_sh_mask.h` with `gc_11_0_0_offset.h`.
- Generated-header checks that every field's `__SHIFT` has a matching `_MASK`, masks align to shifts, and register names in this slice have matching `reg*` and `reg*_BASE_IDX` entries in `gc_11_0_0_offset.h`.
- Static checks for non-overlapping fields within each register, excluding deliberate aliases or full-width payload registers.
- VM tests that program context page-table base/start/end registers for multiple VMIDs, issue TLB/cache invalidations, poll the correct `GCVM_INVALIDATE_ENGn_ACK` bits, and verify stale translations are not observed.
- Fault-handling tests that exercise protection-fault clear/log paths, translation default address attributes, and invalid aperture accesses under normal and SR-IOV configurations.
- SR-IOV or partitioning tests that vary `GCMC_VM_FB_SIZE_OFFSET_VFn`, MARC base/reloc/length, readonly, and PF/VF mapping registers, then verify isolation and expected address translation.
- GCVM/UTCL2 performance-counter tests that configure event selects, enable/clear counters, use start/stop triggers, and confirm low/high result reads are monotonic or saturate as expected.
- Graphics pipeline tests that load PS/GS/HS/LS shader programs with varied resource declarations, user data, traps, scratch, LDS, CU masks, meshlet dimensions, and request-control settings, then check rendering correctness and absence of GPU hangs.
- Compute/KFD/MES tests that initialize MQDs, set compute dispatch initiator, grid dimensions, thread counts, VMID, scratch/program addresses, resource limits, CU masks, temporary ring size, user data, relaunch/restore fields, and dispatch-end payloads, then submit kernels and validate completion.
- Reset, suspend/resume, runtime power management, and GPU recovery tests while VM contexts and compute queues are active, because page tables, invalidate engines, MARC mappings, shader state, and compute dispatch state may need restoration.
- Regression indicators include invalidate timeouts, stale VM translations, unexpected protection faults, bad PF/VF isolation, incorrect performance-counter values, shader compile/run mismatches, failed KFD queue bring-up, stuck compute waves, incorrect scratch accesses, GPU reset during dispatch, or failures isolated to one shader stage or VMID.

### subset-b-002510: lines 14935-17380

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 14935-17380

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it exposes preprocessor constants that describe where each field lives inside a 32-bit GPU MMIO register. Driver code pairs these `__SHIFT` and `_MASK` macros with register offsets from `gc_11_0_0_offset.h` and then uses AMDGPU/KFD helpers to compose, write, read, and decode command-processor, shader-processor-interface, and queue-descriptor registers.

The selected range starts with two shader reserved data registers, then covers most of the `gc_cppdec` command-processor decode block, the `gc_spipdec` SPI scheduling/debug subset, and the start of the `gc_cpphqddec` HQD block. The dominant concerns are CP ring-buffer setup, VMID/preemption/reset, interrupt and ECC reporting, doorbell ranges and hit state, draw/dispatch ID buffering, suspend/resume state-save layout, DMA watchpoints, UTCL1 fault/status fields, SPI arbitration/debug fields, and the first part of per-HQD queue setup. Although the repository path is under `ceph-client`, this file is AMD GPU hardware register metadata, not Ceph or filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, callbacks, allocations, or direct MMIO accesses in this chunk. The only API surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's in-register mask.
- Full-width masks such as `0xFFFFFFFFL` represent data, pointer, address, timestamp, counter, status, or debug payload fields, not necessarily safe write masks.
- Consumers normally combine these macros with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` definitions from `gc_11_0_0_offset.h`, plus helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and KFD MQD layout code.

Major register groups in this chunk:

- `SH_RESERVED_REG0` and `SH_RESERVED_REG1` are full-width reserved shader register payloads.
- `CP_CU_MASK_*` defines compute-unit mask address and policy fields used when CP-side CU masks are installed or selected.
- `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CP_PROCESS_QUANTUM`, `CP_IQ_WAIT_TIME1/2/3`, and CP/CPC/CPF busy hysteresis registers describe CP timing, scheduler retry, quantum, clock-gating, and busy-detection thresholds.
- `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, and `CPC_INT_CNTX_ID` describe CPC interrupt metadata: address high bits, interrupt type, VMID, queue ID, PASID, bypass-PASID, enable/status bits, and context ID.
- `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0/1`, and `CP_INT_STATUS_RING0/1` provide graphics ring interrupt enable/status bits for resume, suspend, DMA watch, VM doorbell writes, ECC, general protection faults, write-pointer poll timeouts, busy/empty/idle transitions, privilege violations, opcode errors, timestamp events, reserved-bit errors, and generic interrupts.
- `CP_ME1/ME2_PIPE[0-3]_INT_CNTL` and matching `INT_STATUS` registers replicate the compute-pipe interrupt enable/status map for MEC pipes, including completion-query status, dequeue request, ECC, SUA violation, GPF, write-pointer poll timeout, privilege/register/opcode errors, timestamp, reserved-bit, and generic interrupts.
- `CP_ME_F32_INTERRUPT`, `CP_PFP_F32_INTERRUPT`, `CP_MEC1_F32_INTERRUPT`, `CP_MEC2_F32_INTERRUPT`, `CP_MEC1_F32_INT_DIS`, and `CP_MEC2_F32_INT_DIS` define F32 firmware/EDC interrupt and disable bits for ME/PFP/MEC front ends.
- `CP_GFX_ERROR`, `CP_FATAL_ERROR`, `CP_ECC_FIRSTOCCURRENCE*`, `GB_EDC_MODE`, and `CC_GC_EDC_CONFIG` describe CP/GC error attribution, fatal-error behavior, first ECC occurrence reporting, and EDC configuration/disabling.
- `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, and `CPG/CPC/CPF_UTCL1_STATUS` cover UTCL1 retry timers, invalidate/drop/fragment/snoop/permission modes, force-no-execute behavior, detected faults/retries/PRT events, and per-event UTCL1 IDs.
- `CP_RB0_*`, generic `CP_RB_*`, and `CP_RB1_*` define graphics ring buffer base, high address, control, read-pointer writeback address, read/write pointers, buffer-size masks, VMID mapping, active state, doorbell range, doorbell clear/status, and write-pointer poll address fields.
- `CP_RB_DOORBELL_RANGE_*`, `CP_MEC_DOORBELL_RANGE_*`, `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_CLEAR`, `CP_RB_STATUS`, and `CP_PQ_STATUS` describe doorbell aperture limits, doorbell modes, offsets, source/schedule-hit/enable/hit bits, and queue status reporting.
- `CP_ME0/ME1/ME2_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME*_PIPE*_PRIORITY`, and `CP_RING*_PRIORITY` define priority counters and per-pipe/ring priority selectors.
- `CP_RB_VMID`, `CP_ME0_PIPE*_VMID`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, and `CP_VMID_STATUS` encode VMID binding, queue reset masks, preempt requests, virtualization command fields, and preempt status for DE/CE.
- `CP_PFP/ME/MEC*_PRGRM_CNTR_START*` and `CP_PFP/ME/MEC*_INTR_ROUTINE_START*` define microcontroller program-counter and interrupt-routine entry-point fields.
- `CP_CONTEXT_CNTL` and `CP_MAX_CONTEXT` describe maximum geometry-engine and pipe-context counts.
- `CP_PWR_CNTL`, `CP_CPC_DEBUG`, `CP_SD_CNTL`, `CP_SOFT_RESET_CNTL`, and `CP_CPC_GFX_CNTL` expose power/debug/reset/control bits that affect CP/CPC/CPF behavior and debug paths.
- `CP_PQ_WPTR_POLL_CNTL` and `CP_PQ_WPTR_POLL_CNTL1` control write-pointer polling period, active/enabled state, one-shot behavior, and queue masks.
- `CPC_SUSPEND_CTX_SAVE_*`, `CPC_SUSPEND_CNTL_STACK_*`, `CPC_SUSPEND_WG_STATE_OFFSET`, `CPC_OS_PIPES`, `CP_SUSPEND_RESUME_REQ`, and `CP_SUSPEND_CNTL` describe context-save base/size/offsets, OS pipe masks, suspend/resume requests, resume lock, and ACE suspend activity.
- `CPC_DDID_*`, `CP_DDID_*`, and `CP_GFX_DDID_*` define draw/dispatch ID buffer base, control, VMID selection, policy/mode/enable, in-flight count, read/write pointers, and delta-report counts.
- `CP_GFX_HPD_*`, `CP_GFX_MQD_*`, and `CP_GFX_HQD_*` define graphics high-priority dispatch queue state: mapped/available/forced queue state, OSPRE fence address/data, index mutex, MQD base/control, HQD active/VMID/priority/quantum/base/pointers/read-pointer writeback/write-pointer poll, doorbell control, dequeue request, mapping, queue-manager control, IQ timer, HQ status/control, and GFX HQD ring control.
- `CP_HQD_GFX_CONTROL` and `CP_HQD_GFX_STATUS` provide message/status fields for HQD graphics control.
- `CP_DMA_WATCH[0-3]_*`, `CP_DMA_WATCH_STAT_ADDR_*`, and `CP_DMA_WATCH_STAT` define four DMA watchpoints, including address/mask, VMID or any-VMID selection, read/write watch enables, and trap status attribution by VMID, queue ID, client ID, pipe, watch ID, and direction.
- `CP_PFP_JT_STAT` and `CP_MEC_JT_STAT` report jump-table loaded and write-mask state.
- `CPG_RCIU_CAM_*` describes indexed CAM programming fields for address/mask/value phases and per-pipe enable/skip-write behavior.
- `CP_GPU_TIMESTAMP_OFFSET_*`, `CP_SDMA_DMA_DONE`, `CP_PFP_SDMA_CS`, `CP_ME_SDMA_CS`, and `CPF_GCR_CNTL` provide timestamp offset, SDMA completion/arbitration, and GCR command fields.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_*`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, and `SPI_COMPUTE_WF_CTX_SAVE` define SPI arbitration, workload pipe percentages for graphics/HP3D/CS pipes, per-VMID accumulation/debug/trap controls, compute queue reset, and compute wavefront context-save control/status.
- The final `gc_cpphqddec` section starts generic HQD definitions: `CP_HPD_UTCL1_*`, MQD base address, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, pipe/queue priority, quantum, PQ base/read-pointer/read-pointer report/write-pointer poll addresses, doorbell control, and the beginning of `CP_HQD_PQ_CONTROL` through `UNORD_DISPATCH__SHIFT`.

## Control Flow

This header has no runtime control flow. It is a declarative map from generated register-field names to bit positions and masks. Runtime flow is supplied by AMDGPU, AMDKFD, firmware, and hardware:

1. GC 11 driver code includes `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`.
2. The caller selects an MMIO register offset and composes field values with the corresponding shift and mask macros.
3. Driver helpers perform read-modify-write, raw reads, raw writes, queue-descriptor initialization, or status decoding.
4. The CP, CPC, CPF, CPG, MEC, PFP, SPI, HQD, doorbell, VM, UTCL1, and interrupt hardware blocks define the actual state transitions, ordering, completion, and error behavior.

Important runtime flows represented by the fields include graphics-ring setup, queue/MQD setup, doorbell enablement, write-pointer polling, read-pointer writeback, VMID reset/preempt, suspend/resume context-save, interrupt enable/status handling, ECC/EDC/fatal-error reporting, DMA watchpoint trapping, UTCL1 invalidate/status handling, SDMA arbitration from CP microcontrollers, SPI compute queue reset and wavefront context-save initiation, and HQD persistent-state/priority/quantum programming. None of those sequences, timeouts, memory barriers, lock ordering, or firmware handshakes are encoded here.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes hardware state that may be programmed, sampled, or action-triggered by driver code.

State represented in this chunk includes ring-buffer bases and high address bits, ring buffer sizes, read/write pointers, read-pointer writeback addresses, write-pointer poll addresses and periods, VMID/IB VMID/VQID selections, doorbell offsets and hit/enabled state, queue active/mapped/available/idle/dequeue/preempt bits, CP/MEC/PFP firmware entry points, interrupt enables/status, ECC/EDC first-occurrence bits, UTCL1 fault and retry status, process and HQD quantum settings, context-save memory layout, DMA watchpoint configuration and trap attribution, timestamp offsets, debug CAM entries, SPI arbitration/pipe allocation, and HQD persistent state.

Persistence is hardware-defined. Some fields are stable configuration until reset, queue teardown, or power-gating; some are live counters or pointers updated by hardware; some are sticky status or interrupt bits; some are command strobes such as reset, preempt, invalidate, suspend, resume, capture, clear, or context-save initiation. The masks do not indicate read-only, write-only, self-clearing, sticky, write-one-to-clear, privileged, or reserved semantics. Consumers must follow the GC 11 programming sequences and preserve unrelated bits in mixed-purpose registers.

## Dependencies And Integration Points

The direct companion header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides matching `mm*` register offsets and base-index symbols. `gc_11_0_0_default.h` provides default values for some registers. The generated header must remain synchronized with the ASIC register database for GC 11.0.0.

Observed in-tree users include GC 11 KFD queue management code, especially `amdkfd/kfd_device_queue_manager_v11.c` and `amdkfd/kfd_mqd_manager_v11.c`, which include the GC 11 offset and shift/mask headers and use fields such as `CP_HQD_PERSISTENT_STATE`, `CP_HQD_QUANTUM`, `CP_HQD_PQ_CONTROL`, and `CP_HQD_PQ_DOORBELL_CONTROL` when initializing MQDs and queues. Broader integration points are AMDGPU graphics-ring initialization, KFD compute queue creation, MQD programming, doorbell aperture setup, GPU reset/recovery, preemption, VMID management, interrupt service paths, ECC/EDC reporting, suspend/resume, runtime power management, wavefront context save/restore, debug/profiling tools, and hardware validation diagnostics.

The chunk crosses address blocks. Code that touches the CP decode block should not assume the SPI or HQD fields share the same indexing, privilege, or reset semantics. The final lines stop in the middle of `CP_HQD_PQ_CONTROL`; adjacent chunks are required for its complete mask set and for the remaining generic HQD queue registers.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. Combining `gc_11_0_0_sh_mask.h` with offsets from another GC revision can compile cleanly while targeting incorrect bits.
- This chunk is pure macro data, so all type, range, alignment, and sequencing checks must happen in callers. A bad shift/mask choice can misprogram a ring, VMID, doorbell, interrupt, or queue descriptor without compiler help.
- The selected range starts and ends at chunk boundaries, not logical register-family boundaries. It begins after prior shader fields and ends before the rest of `CP_HQD_PQ_CONTROL`; complete HQD analysis requires the next chunk.
- Many address fields encode alignment in their masks, for example low bits omitted for ring bases, writeback addresses, doorbells, context-save bases, fence addresses, and DMA watch addresses. Callers must program aligned GPU addresses and preserve required low-bit semantics.
- Doorbell, write-pointer polling, and read-pointer writeback fields are ordering-sensitive. Missing write memory barriers, stale writeback memory, wrong doorbell offset, or an incorrect range limit can make queues appear idle, stuck, or spuriously active.
- VMID reset/preempt/status, suspend/resume, and context-save fields describe multi-stage hardware operations. Polling code must handle in-flight transitions and timeout paths rather than treating a single status read as final.
- Interrupt enable/status fields are heavily replicated across rings and MEC pipes. Copy/paste mistakes between ring0/ring1, ME1/ME2, or pipe0-3 can route or mask the wrong event.
- ECC/EDC/fatal-error and UTCL1 error bits can be sticky or hardware-owned. Blind writes using full masks risk clearing diagnostic state, suppressing faults, or hiding fatal conditions.
- Debug, chicken, power, clock, soft-reset, and CAM fields can affect global CP behavior. These should generally be programmed only by ASIC-specific initialization or recovery code that knows required defaults.
- DMA watchpoint fields can trap reads/writes across VMIDs. Incorrect `ANY_VMID`, mask, or address setup can miss the intended access or generate excessive traps.
- SPI debug/trap and wavefront context-save fields interact with per-VMID scheduling and debugger behavior. Incorrect use can stall VMIDs, trap unintended waves, or leave context-save busy bits set.
- The `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PQ_DOORBELL_CONTROL`, and partial `CP_HQD_PQ_CONTROL` fields are consumed by KFD MQD setup. Queue-size, no-update-rptr, unordered-dispatch, TMZ, cache-policy, privilege, and KMD-queue bits must match the queue type and memory policy.

## Test Signals

Useful validation is mostly generated-header consistency, build coverage, and hardware queue smoke testing:

- Build AMDGPU and AMDKFD code that includes `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`, including GC 11 KFD MQD and device queue manager files.
- Generated-header checks that every `__SHIFT` in this slice has the expected `_MASK`, that masks align with shifts, and that register names have matching entries in `gc_11_0_0_offset.h`.
- Static checks for overlapping fields within a register, while allowing full-width data/status aliases and known reserved fields.
- Ring bring-up tests that program `CP_RB0`, generic `CP_RB`, and `CP_RB1` base/control/read-pointer/write-pointer/writeback fields, submit graphics work, and verify read-pointer progress and idle/active transitions.
- Doorbell tests that cover range limits, offsets, enable/hit bits, clear bits, write-pointer polling, and read-pointer writeback updates.
- KFD queue/MQD tests on GC 11 hardware that validate `CP_HQD_PERSISTENT_STATE`, priority, quantum, PQ base, PQ control, doorbell control, and VMID programming through real compute dispatch completion.
- Interrupt tests that enable selected CP/CPC/MEC pipe events, trigger controlled events such as dequeue, timestamp, write-pointer poll timeout, or invalid opcode where feasible, and verify status bits and ISR routing.
- VMID reset/preempt and suspend/resume tests that force queue preemption or suspend, poll status, verify context-save memory layout, and confirm queues resume without lost progress.
- UTCL1 and VM fault tests that exercise fault/retry/PRT status, invalidate sequencing, and error-halt reporting without stale translations.
- ECC/EDC diagnostic tests that confirm first-occurrence and F32 interrupt/disabling paths report the expected block and do not mask unrelated errors.
- DMA watchpoint tests that arm each watch register for read/write and VMID/any-VMID modes, then verify trap attribution fields and status writeback addresses.
- SPI scheduler/debug tests that validate arbitration/pipe-percentage programming, per-VMID debug trap controls, compute queue reset, and wavefront context-save busy/done behavior.
- Regression indicators include stuck ring write pointers, unchanged read-pointer writeback, doorbell hits without queue progress, unexpected queue idle/active mismatch, missing or storming interrupts, false privilege/opcode errors, EDC counter growth, UTCL1 fault/retry status after drains, failed KFD queue creation, GPU reset during queue teardown, or compute wavefront context-save that never clears busy.

### subset-b-002511: lines 17381-19874

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

### subset-b-002512: lines 19875-22323

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 19875-22323

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it publishes `__SHIFT` and `_MASK` constants for packing and decoding 32-bit graphics context, shader, rasterizer, color-buffer, depth-buffer, VRS, and draw-control registers. Driver code combines these constants with register offsets from companion generated headers such as `gc_11_0_0_offset.h` and register helpers such as `REG_SET_FIELD`, `FIELD_GET`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`.

Although the repository subtree is under `ceph-client`, this file is AMDGPU hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, locks, allocations, or global variables in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.

Major register groups in this chunk:

- Viewport scissor and depth ranges: the slice starts inside `PA_SC_VPORT_SCISSOR_9_TL`, then defines `PA_SC_VPORT_SCISSOR_9_BR` through `PA_SC_VPORT_SCISSOR_15_BR`, with `TL_X`, `TL_Y`, `BR_X`, `BR_Y`, and `WINDOW_OFFSET_DISABLE` masks. It also defines `PA_SC_VPORT_ZMIN_0`/`ZMAX_0` through `ZMIN_15`/`ZMAX_15`, all as full-width viewport depth values.
- Raster/scissor routing and context IDs: `PA_SC_RASTER_CONFIG`, `PA_SC_RASTER_CONFIG_1`, `PA_SC_SCREEN_EXTENT_CONTROL`, `PA_SC_TILE_STEERING_OVERRIDE`, `CP_PERFMON_CNTX_CNTL`, `CP_PIPEID`, `CP_RINGID`, `CP_VMID`, and `CONTEXT_RESERVED_REG0/1`.
- Variable rate shading and rate-surface metadata: `PA_SC_VRS_OVERRIDE_CNTL`, `PA_SC_VRS_RATE_FEEDBACK_BASE`, `PA_SC_VRS_RATE_FEEDBACK_BASE_EXT`, `PA_SC_VRS_RATE_FEEDBACK_SIZE_XY`, `PA_SC_VRS_RATE_CACHE_CNTL`, `PA_SC_VRS_RATE_BASE`, `PA_SC_VRS_RATE_BASE_EXT`, and `PA_SC_VRS_RATE_SIZE_XY`. These expose VRS override combiner/rate bits, feedback writeback enable, VRS surface enable, 256-byte base-address fields, XY extents, and cache policy knobs.
- Color/depth fixed-function state: `CB_RMI_GL2_CACHE_CONTROL`, `CB_BLEND_RED/GREEN/BLUE/ALPHA`, `CB_FDCC_CONTROL`, `CB_COVERAGE_OUT_CONTROL`, `DB_STENCIL_CONTROL`, `DB_STENCILREFMASK`, and `DB_STENCILREFMASK_BF`.
- Viewport transform and user clip planes: `PA_CL_VPORT_XSCALE`, `XOFFSET`, `YSCALE`, `YOFFSET`, `ZSCALE`, and `ZOFFSET` are repeated for viewport indices 0-15. `PA_CL_UCP_0_X/Y/Z/W` through `PA_CL_UCP_5_X/Y/Z/W` define full-width user clip plane coefficients, followed by `PA_CL_PROG_NEAR_CLIP_Z`.
- Shader-processor pixel-input setup: `PA_RATE_CNTL` and `SPI_PS_INPUT_CNTL_0` through `SPI_PS_INPUT_CNTL_31`. The PS input controls pack parameter `OFFSET`, default values, flat shading, primitive attribute selection, duplication, FP16 interpolation, and attribute-valid bits; entries 0-19 also include point-sprite texture fields while later entries omit those fields.
- Shader export and interpolation configuration: `SPI_VS_OUT_CONFIG`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, `SPI_BARYC_CNTL`, `SPI_TMPRING_SIZE`, `SPI_GFX_SCRATCH_BASE_LO/HI`, `SPI_SHADER_IDX_FORMAT`, `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT`.
- Shader export/color blend optimization: `SX_PS_DOWNCONVERT_CONTROL`, `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT`, and `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL`.
- Draw and primitive assembly state: `GFX_COPY_STATE`, point size/radius registers, `VGT_DMA_BASE_HI`, `VGT_DMA_BASE`, `VGT_DRAW_INITIATOR`, `VGT_EVENT_ADDRESS_REG`, and `GE_MAX_OUTPUT_PER_SUBGROUP`.
- Depth, clipping, rasterization, and primitive filtering: `DB_DEPTH_CONTROL`, `DB_EQAA`, `CB_COLOR_CONTROL`, `DB_SHADER_CONTROL`, `PA_CL_CLIP_CNTL`, `PA_SU_SC_MODE_CNTL`, `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, `PA_SU_LINE_STIPPLE_CNTL`, `PA_SU_LINE_STIPPLE_SCALE`, `PA_SU_PRIM_FILTER_CNTL`, and `PA_SU_SMALL_PRIM_FILTER_CNTL`.
- The chunk ends at the first field of `PA_CL_NGG_CNTL` (`VERTEX_REUSE_OFF__SHIFT`); the remaining `PA_CL_NGG_CNTL` masks and following PA registers belong to the next chunk.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consumers:

1. ASIC-specific code includes `gc/gc_11_0_0_sh_mask.h` with compatible GC 11 offset headers.
2. Driver or command-submission code selects a concrete register offset for the GC block and ASIC instance.
3. The code composes values using the generated masks/shifts or decodes hardware state read from MMIO, indirect registers, command processor state, or saved context images.
4. Surrounding driver paths handle sequencing, locking, reset, suspend/resume, command-stream packet construction, firmware cooperation, and user-mode API validation.

For draw and graphics state, these masks are normally consumed indirectly through PM4 context-register packets or clear-state tables rather than by ad hoc MMIO writes. For example, `clearstate_gfx11.h` contains initial values for many registers in this exact range, including VRS rate registers, all `SPI_PS_INPUT_CNTL_*` registers, pixel input masks, blend controls, depth controls, and clipping/rasterization controls.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes hardware-visible state that is programmed by the kernel driver, firmware, or command streams and then lives in GPU context state until changed, reset, or restored.

The viewport, scissor, Z range, VRS, SPI interpolation, SX/CB blend, DB depth/stencil, PA clipping, and VGT draw fields represent graphics pipeline state. Some fields are part of per-context state saved/restored by the command processor or initialized through clear-state images; others are programmed by kernel initialization or command buffers. Values can be lost or reset across GPU reset, suspend/resume, graphics context teardown, or power transitions unless reloaded by the appropriate driver/firmware path.

The base-address style fields, such as VRS rate/feedback bases and VGT DMA base fields, encode hardware address fragments rather than arbitrary CPU pointers. Their persistence and coherency depend on GPU virtual-memory setup, command submission lifetime, cache policy fields, and reset handling. Full-width masks such as `0xFFFFFFFFL` on viewport floats, clip-plane coefficients, blend constants, and scratch/base fields mean "all bits in the register are payload," not that every payload is valid in every hardware mode.

The macros do not encode access class. Fields may be read-only, write-only, write-one-to-clear, self-clearing, sticky, reserved, context-save-only, command-packet-only, or MMIO-accessible depending on the hardware specification and offset header.

## Dependencies And Integration Points

Direct dependencies are the matching generated GC 11 offset and hardware-definition headers. Include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c`

Important integration points include:

- GFX11 initialization, register access self-tests, reset, clock/power management, interrupt setup, and ring command emission in `gfx_v11_0.c`.
- Clear-state programming in `clearstate_gfx11.h`, which provides reset/default graphics context values for many registers covered by this slice.
- Command stream construction for graphics context registers, including `PACKET3_SET_CONTEXT_REG` and related PM4 packets. The header defines the bit layout; packet builders and user-mode drivers decide when specific fields are emitted.
- Graphics pipeline state supplied by Mesa/ROCm/user command buffers and validated by kernel command submission, especially SPI pixel inputs, blend controls, depth/stencil state, viewport transforms, VRS, and clip/rasterization controls.
- Display-plane and DCN integration through `amdgpu_dm_plane.c`, which includes this header for GPU-side surface/format/rate-control definitions used around display scanout and graphics/display interop.
- KFD and MES integration, which include the same GC11 mask header for queue, shader, and context-state programming even when this particular slice is more graphics-state heavy than compute-queue heavy.

## Risks And Edge Cases

- Header/offset mismatch is the main structural risk. These untyped constants can compile with the wrong generated offset family and silently target incorrect bit positions or registers.
- The chunk starts and ends mid-register-family: it begins after the first `PA_SC_VPORT_SCISSOR_9_TL` field and ends before the complete `PA_CL_NGG_CNTL` block. Adjacent chunks are required for a complete per-file view.
- Context-register sequencing matters. Programming dependent SPI, PA, DB, CB, SX, and VGT fields out of order can produce malformed rendering, hangs, or stale context state even though each field value is syntactically valid.
- Repeated register families are off-by-one prone: 16 viewport transforms, 16 viewport Z ranges, 32 PS input controls, eight MRT blend-optimization registers, and eight CB blend-control registers all share nearly identical layouts.
- Not all repeated PS input controls are identical. `SPI_PS_INPUT_CNTL_0` through `_19` include point-sprite texture fields, while `_20` through `_31` omit them; code that assumes a uniform 32-entry layout can write nonexistent/reserved bits.
- Address and size fields have hardware units. VRS base registers use 256-byte granularity, VRS size fields use packed X/Y maxima, VGT event addresses expose low address bits only, and base high registers often expose a limited number of upper bits.
- Cache-policy fields in `PA_SC_VRS_RATE_CACHE_CNTL` and `CB_RMI_GL2_CACHE_CONTROL` affect coherency and performance. Wrong policies can cause stale VRS rate reads, incorrect color/DCC behavior, or workload-specific performance regressions.
- VRS combiner/rate fields interact with primitive, vertex, HTILE, and sample-rate sources outside this exact chunk. Misprogramming can produce visible shading-rate artifacts while passing basic rendering tests.
- `DB_SHADER_CONTROL`, `DB_DEPTH_CONTROL`, `DB_EQAA`, and stencil-ref fields affect early/late Z, stencil operations, coverage export, over-rasterization, and color-write behavior. Small bit errors can look like application bugs rather than driver faults.
- Full-width float/payload registers do not validate format. Viewport, clip-plane, point-size, blend-constant, scratch, and export-format fields rely on higher-level state validation.
- Reserved-bit preservation is caller-owned. The masks expose named fields but do not force read-modify-write discipline or prevent writes to undocumented bits.

## Test Signals

Useful validation is mostly build, static, command-stream, and hardware rendering coverage:

- Build coverage for GC11 users that include `gc_11_0_0_sh_mask.h`, especially `gfx_v11_0.c`, `clearstate_gfx11.h`, KFD/MES files, SDMA v6, display DM, and SOC21 paths.
- Generated-header consistency checks that every `__SHIFT` has a matching `_MASK`, masks are aligned to their shifts, fields do not overlap within a register except documented aliases, and register names match the compatible offset header.
- Clear-state validation that `clearstate_gfx11.h` register order and default values match GC11 context-register offsets for all covered state blocks.
- Graphics conformance and piglit/dEQP-style tests covering multiple viewports/scissors, viewport depth ranges, user clip planes, point sprites, flat/centroid/sample interpolation, FP16 interpolation, VRS rate surfaces, blend constants, per-MRT blend modes, alpha-to-coverage, depth/stencil operations, EQAA/MSAA behavior, and conservative/early-depth interactions.
- Command-stream tests or traces that exercise all 32 `SPI_PS_INPUT_CNTL_*` entries and verify the different point-sprite field availability between low and high entries.
- Reset, suspend/resume, and GPU recovery tests while graphics queues are active, because context state and clear-state reload must restore the registers described here.
- Negative indicators include render corruption limited to one MRT, viewport, or PS input slot; VRS artifacts; unexpected depth/stencil pass/fail results; stuck graphics fences after state-heavy draws; VM faults on VRS or VGT base-address programming; or failures limited to GC11 ASICs.

### subset-b-002513: lines 22324-24720

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 22324-24720

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C logic; it exposes `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, display, MES, SDMA, IMU, and SOC21 support code to compose or decode 32-bit GC register values. The matching register addresses live in companion generated offset headers, especially `gc_11_0_0_offset.h`.

The range is mostly graphics context state for primitive assembly, scan conversion, variable-rate shading, render targets, color compression, queue targeting, shader memory setup, and command processor debug controls. It starts inside the `PA_CL_NGG_CNTL` definition, then covers many context-register masks, moves through `gc_pfvf_cpdec`, `gc_pfvf_grbmdec`, `gc_pfvf_padec`, and `gc_pfvf_sqdec`, and ends at the beginning of `gc_pfonly_cpdec` `CP_DEBUG_2` shift definitions. Although the repository path is under `ceph-client`, this header is AMD GPU driver hardware metadata and has no Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, global variables, allocations, locks, or persistence APIs in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask.
- Consumers combine these with `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and packet-building code that writes context registers.

Major register families in this range:

- Primitive, tessellation, and NGG setup: `PA_CL_NGG_CNTL`, `VGT_HOS_MAX_TESS_LEVEL`, `VGT_HOS_MIN_TESS_LEVEL`, `VGT_ENHANCE`, `IA_ENHANCE`, `VGT_DMA_SIZE`, `VGT_DMA_MAX_SIZE`, `VGT_DMA_INDEX_TYPE`, `WD_ENHANCE`, `VGT_PRIMITIVEID_EN`, `VGT_DMA_NUM_INSTANCES`, `VGT_PRIMITIVEID_RESET`, `VGT_EVENT_INITIATOR`, `VGT_DRAW_PAYLOAD_CNTL`, `VGT_ESGS_RING_ITEMSIZE`, `VGT_REUSE_OFF`, `VGT_GS_MAX_VERT_OUT`, `GE_NGG_SUBGRP_CNTL`, `VGT_TESS_DISTRIBUTION`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TF_PARAM`, and `VGT_GS_INSTANCE_CNT`.
- Rasterizer, scanner, anti-aliasing, and VRS state: `PA_SU_OVER_RASTERIZATION_CNTL`, `PA_STEREO_CNTL`, `PA_STATE_STEREO_X`, `PA_CL_VRS_CNTL`, `PA_SU_POINT_SIZE`, `PA_SU_POINT_MINMAX`, `PA_SU_LINE_CNTL`, `PA_SC_LINE_STIPPLE`, `PA_SC_MODE_CNTL_0`, `PA_SC_MODE_CNTL_1`, `PA_SC_CENTROID_PRIORITY_0/1`, `PA_SC_LINE_CNTL`, `PA_SC_AA_CONFIG`, `PA_SU_VTX_CNTL`, clip/discard adjust registers, the `PA_SC_AA_SAMPLE_LOCS_*` matrix, `PA_SC_AA_MASK_*`, `PA_SC_SHADER_CONTROL`, `PA_SC_BINNER_CNTL_0/1/2`, `PA_SC_CONSERVATIVE_RASTERIZATION_CNTL`, `PA_SC_NGG_MODE_CNTL`, `PA_SC_VRS_SURFACE_CNTL`, and `PA_SC_VRS_SURFACE_CNTL_1`.
- Depth and polygon state: `DB_HTILE_SURFACE`, `DB_SRESULTS_COMPARE_STATE0/1`, `DB_PRELOAD_CONTROL`, `DB_ALPHA_TO_MASK`, and the `PA_SU_POLY_OFFSET_*` scale/offset/clamp registers.
- Stream-out and opaque draw state: `VGT_STRMOUT_DRAW_OPAQUE_OFFSET`, `VGT_STRMOUT_DRAW_OPAQUE_BUFFER_FILLED_SIZE`, and `VGT_STRMOUT_DRAW_OPAQUE_VERTEX_STRIDE`.
- Color buffer render-target state: repeated `CB_COLOR0` through `CB_COLOR7` register groups for `BASE`, `VIEW`, `INFO`, `ATTRIB`, `FDCC_CONTROL`, `DCC_BASE`, `BASE_EXT`, `DCC_BASE_EXT`, `ATTRIB2`, and `ATTRIB3`. These include format, number type, component swap, blend optimization, slice/mip view, fragment count, destination alpha forcing, DCC/FDCC block sizing, independent block flags, compression-disable bits, and high address-extension fields.
- Virtualization-safe CP and GRBM targeting: under `gc_pfvf_cpdec`, `CONFIG_RESERVED_REG0/1`, `CP_MEC_CNTL`, and `CP_ME_CNTL`; under `gc_pfvf_grbmdec`, `GRBM_GFX_CNTL` and `GRBM_NOWHERE`.
- PA/PH implementation and performance controls: under `gc_pfvf_padec`, `PA_SC_ENHANCE*`, binner override/flag/DSM/tile-steering/FIFO/wave-table/event/timeout/performance controls, trap-screen hypervisor locks, `PA_PH_INTERFACE_FIFO_SIZE`, and `PA_PH_ENHANCE`.
- Shader queue and memory controls: under `gc_pfvf_sqdec`, `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_DEBUG`, `SQ_SHADER_TBA_LO/HI`, and `SQ_SHADER_TMA_LO/HI`.
- Privileged command-processor debug: the chunk starts `gc_pfonly_cpdec` with `CP_DEBUG_2` shift fields such as `CHIU_NOALLOC_OVERRIDE`, `RCIU_SECURE_CHECK_DISABLE`, packet-injector disable, context-done copy-state disable, NOP discard disable, DC interleave/clock/broadcast controls, and hardware detect disable fields. The chunk boundary ends before the corresponding `CP_DEBUG_2` masks.

## Control Flow

This header has no runtime control flow. The runtime pattern is:

1. ASIC-specific code includes `gc/gc_11_0_0_sh_mask.h` with a matching offset header.
2. Driver code selects a register offset or packet context-register slot.
3. A register value is built with these masks/shifts, usually through `REG_SET_FIELD` or direct shifts when constructing MQDs and default state.
4. Surrounding code writes the value through MMIO, SOC15 helpers, MES/CP packets, firmware-loaded MQDs, or display modifier/tiling paths.

Observed consumers in this tree include `gfx_v11_0.c`, `soc21.c`, `mes_v11_0.c`, `sdma_v6_0.c`, `amdgpu_amdkfd_gfx_v11.c`, `kfd_device_queue_manager_v11.c`, `kfd_mqd_manager_v11.c`, `imu_v11_0.c`, `amdgpu_display.c`, and `display/amdgpu_dm/amdgpu_dm_plane.c`.

Typical flows are GFX initialization programming default `SH_MEM_CONFIG` and `SH_MEM_BASES`; KFD queue-manager code building per-process shader memory policy; KFD MQD code encoding CP HQD and SDMA queue fields adjacent to the same generated namespace; SOC21 selecting GRBM pipe/ME/VMID/queue targets through `GRBM_GFX_CNTL`; GFX golden settings programming PA/VRS registers such as `PA_SC_VRS_SURFACE_CNTL_1`; and display code negotiating DCC-capable framebuffer modifiers that must stay compatible with the render-target DCC/FDCC fields in this generated family.

## State And Persistence Behavior

The file persists no software state. It describes hardware state stored in GC registers or context images.

Many fields in the PA/VGT/DB/CB families are graphics context state: they are programmed per draw, per pipeline state object, or through clear-state/context images, and they can be saved/restored by command processor context switching. Color buffer base, DCC base, extension, view, format, and compression fields describe GPU memory addresses and surface metadata that remain meaningful only while the relevant BOs, tiling metadata, and VM mappings are valid.

`SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_SHADER_TBA_*`, and `SQ_SHADER_TMA_*` are process or VMID-sensitive shader execution state. They are initialized for graphics and compute contexts and may be rewritten on process activation, queue load, trap setup, reset recovery, or suspend/resume.

GRBM and CP control fields affect register access routing and command-processor engine state. Their values are transient control state and must be restored to a safe broadcast or default target after targeted writes. PA/PH enhancement, binner, FIFO, VRS, and performance registers are hardware configuration knobs that may be set by golden-register programming or ASIC-specific setup, and may be lost across reset or power transitions.

The macros do not encode access permissions or side effects. Some described fields are read-only status, some are write-only controls, some are privileged-only, some are context registers, and some are self-clearing or reserved according to hardware documentation outside this header.

## Dependencies And Integration Points

Direct dependencies are generated offsets and default-state files for the same ASIC generation, especially `gc_11_0_0_offset.h`, plus consumers that understand SOC15 register addressing and packet context-register ranges.

Key integration points:

- `gfx_v11_0.c` includes this header for GFX11 bring-up, golden register programming, shader memory defaults, GRBM indexing, CP/ME/MEC control, HQD/MQD programming, interrupt enablement, and reset paths.
- `soc21.c` uses `GRBM_GFX_CNTL` field masks to select pipe, ME, VMID, and queue before writing `regGRBM_GFX_CNTL`.
- `amdgpu_amdkfd_gfx_v11.c` and `kfd_device_queue_manager_v11.c` use `SH_MEM_CONFIG` and `SH_MEM_BASES` fields for KFD process memory policy and LDS/shared/private aperture setup.
- `kfd_mqd_manager_v11.c` uses the same generated mask style for CP HQD/MQD, SDMA MQD, doorbell, queue-size, context-save, and AQL fields used by user-mode compute queues.
- `mes_v11_0.c` builds MES and HQD control values and shares the same generated field contract for queue reset, queue activation, persistent state, doorbells, and VMID assignment.
- `sdma_v6_0.c` includes this header because GFX11 SDMA queue fields live in the generated GC namespace; SDMA ring initialization and KFD SDMA MQD construction depend on compatible mask definitions.
- `amdgpu_dm_plane.c` and `amdgpu_display.c` integrate with DCC/FDCC surface metadata exposed to userspace through DRM format modifiers. The CB DCC/FDCC fields in this chunk must agree with the modifier policy advertised for GC 11.0.0.
- `clearstate_gfx11.h` contains clear-state entries for context registers such as `VGT_SHADER_STAGES_EN` and `CB_COLOR0_INFO`, which depend on the same hardware register layout.
- `imu_v11_0.c` and firmware-loading paths depend on generated GC register definitions when building initialization microcode or golden programming sequences.

## Risks And Edge Cases

- Header/offset mismatch is the main structural risk. These untyped macros can compile with the wrong offset family and silently program the wrong register or field.
- This chunk starts and ends at artificial boundaries: `PA_CL_NGG_CNTL` is incomplete at the beginning, and `CP_DEBUG_2` has only shift definitions here. Adjacent chunks are required for a complete register audit.
- Context register fields must preserve reserved bits and respect packet/register address class. A value that is syntactically valid with `_MASK` can still be invalid for a context register, privileged register, or read-only status field.
- GRBM targeting is fragile. A stale `GRBM_GFX_CNTL` pipe/ME/VMID/queue selection can direct later register writes to one queue or VMID instead of broadcast state.
- `SH_MEM_BASES` and `SH_MEM_CONFIG` are VM/process sensitive. Wrong private/shared base, address mode, alignment mode, or instruction prefetch values can break shader memory addressing, trap handling, or KFD queues.
- Trap base/address fields split low and high address bits; `SQ_SHADER_TBA_HI__TRAP_EN` shares the high register with address bits. Misplaced shifts can corrupt trap address or enable state.
- Render-target address fields are unit-scaled, such as `BASE_256B` and high extension fields. Treating them as byte addresses can point CB or DCC metadata at the wrong memory.
- DCC/FDCC fields are tightly coupled to tiling, display modifiers, userspace metadata, and compression capabilities. Advertising incompatible DCC modifiers or programming inconsistent independent-block/max-block fields can cause corruption, scanout rejection, or decompression failures.
- VRS and AA sample-location masks are dense packed fields. Bad packing can produce rendering artifacts without obvious kernel errors.
- CP debug and disable fields can alter hardware detection, packet injection, broadcast, clocking, NOP discard, or context-copy behavior. These are privileged controls and should not be changed without ASIC-specific validation.
- Full-width masks such as `0xFFFFFFFFL` do not imply safe arbitrary writes; they may represent data payloads, address fragments, status, or hardware-owned counters.

## Test Signals

Useful validation is mostly build, generated-header consistency, and hardware behavior:

- Build coverage for GFX11/SOC21 paths that include `gc_11_0_0_sh_mask.h`, especially `gfx_v11_0.c`, `soc21.c`, `mes_v11_0.c`, `sdma_v6_0.c`, `amdgpu_amdkfd_gfx_v11.c`, KFD v11 queue/MQD code, display plane code, and IMU code.
- Generated-header checks that every complete field has matching `__SHIFT` and `_MASK`, masks align with shifts, fields do not overlap unexpectedly within a register, and register names match `gc_11_0_0_offset.h`.
- GFX ring and compute ring smoke tests that initialize queues, submit packets, complete fences, reset queues, and survive GPU reset or suspend/resume.
- KFD tests that create, run, preempt, evict, restore, and destroy user queues across multiple VMIDs, with trap/debug paths exercising `SQ_SHADER_TBA/TMA` and `SH_MEM_*` state.
- Display modifier tests for GC 11.0.0 DCC scanout and rendering: linear, DCC, DCC retile, 64B/128B independent blocks, 4K-or-larger modes, page flips, and BO import/export metadata.
- Graphics rendering tests that cover tessellation, GS/NGG, stream-out, primitive ID reset, VRS, MSAA/sample locations, conservative rasterization, depth/stencil, polygon offset, color compression, and all eight color render targets.
- Reset and power-transition tests that confirm golden PA/VRS/PH settings, shader memory defaults, GRBM broadcast state, queue state, and CB/DCC programming are restored correctly.
- Negative signals include GPU hangs during draw or queue activation, failed fences, wrong VMID/queue register targeting, KFD trap failures, corrupted render targets, DCC scanout rejection, VRS/AA artifacts, unexpected CP/MES reset behavior, or ASIC-specific regressions isolated to GC 11.0.0/SOC21 devices.

### subset-b-002514: lines 24721-27318

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 24721-27318

## Scope

This chunk is part of AMD's generated GC 11.0.0 register shift/mask header. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `_MASK` value used by AMDGPU register helpers to pack or decode 32-bit MMIO and command-stream register values. There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or executable branches in this range.

The requested range contains 2,598 lines, 2,131 `#define` statements, and 445 generated comment lines. It starts mid-register at the `CP_DEBUG_2` mask definitions; the corresponding `CP_DEBUG_2` shift macros are in the previous chunk. It then covers complete register families across queue debug, dynamic power/throttle accounting, SPI/TCP/GDS/UTCL1/GCR controls, CAC/EDC weighting, CU resource reservation, user/config CP registers, draw statistics, scratch/atomic/DMA/semaphore controls, graphics coherency, RLC performance counters, GRBM indexing, and the first VGT/GE draw-state registers. It ends at the `//PA_SC_SCREEN_EXTENT_MIN_0` marker before that register's field macros, which belong to the next adjacent chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for GC 11.0.0 graphics IP. It is not Ceph filesystem code.

## Purpose

`gc_11_0_0_sh_mask.h` supplies symbolic bit layouts for GC 11.0.0 hardware registers. Driver code combines these macros with register offsets from `gc_11_0_0_offset.h` and helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` so it can manipulate named fields without hard-coded bit positions.

This chunk focuses on several hardware domains:

- Command processor and queue/debug controls: `CP_DEBUG_2`, `CP_FETCHER_SOURCE`, HPD queue offset/status registers, CP append/fence/atomic/semaphore/DMA registers, PFP indirect-buffer/load controls, scratch access, EOP-done event/data controls, draw/dispatch/index indirect addresses, sample status, and ME coherency controls.
- DIDT, EDC, CAC, PCC, PWRBRK, and throttle accounting: global and per-shader-engine counter aggregation, rolling power delta, dynamic thresholds, hysteresis, stretch counters, throttle controls/status, clock monitor control, and many generated weight registers used by power estimation and throttling logic.
- SPI and shader front-end state: wave debug stall controls, trap configuration, export arbitration weights, feature controls, shader resource limit controls, compute wavefront context-save status, and per-CU resource reservation and enable masks.
- Texture/cache/memory front-end blocks: TCP invalidate/status/control/debug-index/data registers, GDS enhance and OA restore controls, UTCL1 controls, FIFO sizing, GCRD target disable and credit-safe fields, and GCR command/status/general controls.
- Graphics user/config state: CP pipe-stat address and performance counters, scratch registers and atomic operations, DMA command descriptors, IB2/ST buffer state, DB base/buffer fields, GDS backup address, RLC GPM performance counters, GRBM instance selection, primitive/index type, VGT/GE draw setup, tessellation factor ring/base fields, GE grouping, stereo, user VGPRs, fast GS launch dimensions, GS output primitive type, and line stipple state.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the same field.
- `// addressBlock: ...` comments identify the generated hardware register block for following register comments.
- `//<REGISTER>` comments mark register groups that correspond to address macros in the companion offset header.

The major generated address blocks and register families in this slice are:

- `gc_pfonly_cpdec` tail: `CP_DEBUG_2` masks and `CP_FETCHER_SOURCE`.
- `gc_pfonly_cpphqddec`: `CP_HPD_MES_ROQ_OFFSETS`, `CP_HPD_ROQ_OFFSETS`, and `CP_HPD_STATUS0` queue state, mapped-queue, availability, pending-transfer, offload-check, freeze, and force fields.
- `gc_pfonly_didtdec`: DIDT indirect index/data and EDC controls, throttle controls, thresholds, stall patterns, status, overflow, and rolling-power-delta fields.
- `gc_pfonly_spidec`: SPI graphics debug wave stall/trap fields, arbitration controls, shader resource limit controls, and compute wavefront context-save status fields.
- `gc_pfonly_tcpdec`: TCP invalidation, status, control, and debug index/data fields.
- `gc_pfonly_gdsdec`: GDS enhance and OA clock/power-gating restore fields.
- `gc_pfonly_utcl1dec`: UTCL1 control, invalidation disable, FIFO sizing, per-SA GCRD target disable, and credit-safe fields.
- `gc_pfonly_pmmdec`: GCR general control, command/status, spare, and PMM control fields.
- `gc_sedcdec`: SEDC GL1/GL2 override controls.
- `gc_pfonly_gccacdec`: the largest portion of this chunk, covering GC/SE CAC aggregation counters, EDC/throttle controls and status, stall-pattern controls for EDC/PCC/PWRBRK/DIDT, hysteresis/performance counters, many `GC_CAC_WEIGHT_*` and `SE_CAC_WEIGHT_*` registers, clock monitor control, and indirect CAC index/data accessors.
- `gc_pfonly2_spidec`: `SPI_RESOURCE_RESERVE_CU_0` through `_15` and `SPI_RESOURCE_RESERVE_EN_CU_0` through `_15`, giving per-CU VGPR/SGPR/LDS/thread-group reservation and enable fields.
- `gc_gfxudec`: user/config graphics registers, including CP event/fence/stat counters, scratch/atomic append state, CP DMA descriptors, semaphore waits/signals, IB2/ST buffers, EOP done controls, draw/dispatch/index indirect addresses, ME coherency, RLC performance counters, GRBM indexing, VGT primitive/index/count/state registers, and GE grouping/user/stereo/resource controls.

Representative high-risk field groups include address fragments such as `*_ADDR_LO`, `*_ADDR_HI`, `*_BASE`, `*_BASE_HI`, `*_BASE_256B`, and `*_HI_256B`; command/control bits such as `ENABLE`, `RESET`, `STALL`, `FORCE`, `FREEZE`, `WAIT`, `EXEC_COUNT`, `DISABLE_*`, and `AUTO_INCR`; status/counter fields such as `BUSY`, `IDLE`, `STATUS`, `COUNT`, `OVERFLOW`, `PEND_TXFER`, and `THROTTLE_LEVEL`; and reserved fields that callers must not treat as portable feature bits.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 11.0.0 register header for the active ASIC/IP version.
2. Choose the matching register offset from `gc_11_0_0_offset.h`.
3. Use a `__SHIFT`/`_MASK` pair directly, or through `REG_SET_FIELD`/`REG_GET_FIELD`, to compose or decode a 32-bit register value.
4. Read, write, poll, or emit that value through AMDGPU MMIO helpers or PM4 command packets.
5. Let the underlying CP, SPI, TCP, GDS, UTCL1, GCR, CAC/EDC, RLC, GRBM, VGT, or GE hardware block act on the programmed bits or report status through them.

The runtime sequencing is owned by the surrounding driver and firmware-facing paths, not by this generated header. For example, CP DMA command registers need correct source/destination address and command programming before execution; semaphore wait/signal registers need ordering against producer and consumer queues; coherency registers need pairing with cache management and command submission rules; CAC/EDC throttle registers need power-management sequencing; and VGT/GE draw-state registers need coherent draw-packet setup. This file describes bit positions only and does not encode waits, flushes, write-one-to-clear behavior, read side effects, or reset ordering.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware register state that is volatile, generation-specific, and controlled by AMDGPU driver code, firmware, command processors, and the GPU itself.

State represented in this chunk includes:

- Queue and command-processor state: HPD queue availability/state, append/fence counters, scratch register storage, atomic pre-operation data, semaphore addresses, CP DMA descriptors, IB2/ST buffer pointers and sizes, EOP done event/data context, draw/dispatch/index indirect addresses, sample status, and ME coherency ranges.
- Power and throttle state: DIDT/EDC controls, rolling power deltas, dynamic thresholds, stretch counters, CAC aggregate windows and GFXCLK-cycle counters, per-block CAC weights, PCC/PWRBRK/DIDT stall patterns, throttle status, overflow counters, and EDC hysteresis state.
- Debug and status state: SPI trap and wave-stall controls, TCP status and debug data, GCR command/status, GDS restore fields, RLC GPM performance counters, GRBM graphics instance selection, and CP pipe-stat/performance counters.
- Draw and geometry state: primitive and index type, vertex index bounds and offsets, number of indices/instances, tessellation-factor ring and memory base, HS offchip parameters, GE grouping and stereo controls, user VGPR data/enables, fast GS launch dimensions, GS output primitive type, and line stipple state.

Persistence depends on the hardware block. Some fields are context or queue state that persists until rewritten, context-switched, or restored after reset. Some are live status snapshots or counters. Some registers are command-like or side-effecting, especially DMA, semaphore, EOP, atomic, and append-related registers. Some power-management fields may be initialized from golden settings or firmware-managed sequences and then preserved across normal operation until power-gating, reset, suspend/resume, or reinitialization.

The header does not distinguish read-only, write-only, sticky, clear-on-read, write-one-to-clear, pulse, or reserved fields. Consumers must rely on hardware documentation and established AMDGPU programming sequences. Reserved and generation-specific bits should generally be preserved during read-modify-write unless a documented full-register value is being emitted.

## Dependencies And Integration Points

This chunk must remain synchronized with the GC 11.0.0 generated register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h` supplies matching `mm*` register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h` supplies generated default/reset values where present.
- AMDGPU GC 11 driver code, KFD integration, power-management code, reset/suspend/resume paths, debug tooling, and firmware-facing command paths rely on these field names matching the register database.
- Neighbor generation headers such as `gc_10_3_0_sh_mask.h`, `gc_10_1_0_sh_mask.h`, and other GC 11 variants expose similar families with generation-specific field layouts. Mixing a GC 11.0.0 mask with another generation's offset may compile but program the wrong hardware bits.

Functional integration points include CP queue management, CP DMA packet execution, semaphore/fence/EOP signaling, scratch and atomic operations, shader wave debug and trap controls, texture/cache invalidation and status collection, GDS restore behavior, UTCL1/GCR controls, CAC/EDC/PCC/PWRBRK power throttling, RLC performance monitoring, GRBM instance targeting, primitive assembly, indexed/indirect draw setup, tessellation-factor storage, geometry engine grouping, stereo routing, user VGPR handoff, and line stipple state.

Because these are untyped preprocessor macros, integration relies on exact token spelling. A consumer using `REG_SET_FIELD(value, CP_ME_COHER_CNTL, DB_DEST_BASE_ENA, x)` depends on the existence and correctness of both `CP_ME_COHER_CNTL__DB_DEST_BASE_ENA__SHIFT` and `CP_ME_COHER_CNTL__DB_DEST_BASE_ENA_MASK`.

## Risks And Edge Cases

- The range begins mid-register. This chunk contains only the `CP_DEBUG_2` mask lines; the corresponding shift lines and register comment are owned by the previous chunk.
- The range ends at a register marker. `PA_SC_SCREEN_EXTENT_MIN_0` has no field macros in this chunk; its `X`/`Y` shift and mask definitions are in the next chunk.
- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but programs or decodes the wrong hardware bits, causing hangs, lost fences, bad status reporting, broken throttling, corrupted draws, or performance regressions.
- Address fields often encode high/low halves or hardware-aligned units, such as 256-byte base units. Treating these as raw byte addresses or failing to preserve high bits can target the wrong GPU memory.
- CP DMA, semaphore, append, atomic, EOP, and indirect draw registers are sequencing-sensitive. Misordered writes or incorrect field packing can trigger work early, wait forever, corrupt command-visible memory, or signal the wrong fence.
- CAC/EDC/PCC/PWRBRK/DIDT fields affect power estimation and throttling. Incorrect weights, thresholds, hysteresis, stall patterns, or overflow handling can create silent performance cliffs, unstable throttling, or thermal/power-limit behavior that only appears under specific workloads.
- Repeated families invite generator or copy errors. Per-SE CAC counters and weights, per-CU SPI resource reservation registers, and repeated CP counter/address pairs should remain structurally consistent where hardware requires it.
- Debug/status fields can be volatile or latch side effects. Driver diagnostics should avoid assuming that every status field is stable across reads or safe to write through a generic read-modify-write path.
- Reserved fields appear throughout this generated map. Full-register writes that do not preserve undocumented bits can break generation-specific behavior.
- The file does not encode hardware access permissions. Some fields may be privileged, PF-only, debug-only, read-only, or firmware-owned even though the macros are available to all C consumers that include the header.

## Test Signals

Useful validation is mostly build coverage, generated-data consistency checks, and hardware runtime coverage:

- Build AMDGPU and KFD configurations that include GC 11.0.0 support. Missing or renamed macros should surface in graphics, compute, reset, power-management, debug, and command-submission code.
- Mechanically compare this range against AMD's authoritative GC 11.0.0 register database and verify that every register in the chunk has matching offsets in `gc_11_0_0_offset.h` and defaults in `gc_11_0_0_default.h` where generated.
- Run static mask sanity checks: masks should align with their shifts, full-width data fields should use `0xFFFFFFFFL`, high/low address pairs should have expected widths, repeated per-SE/per-CU/per-counter groups should be consistent, and reserved masks should not be consumed as feature flags.
- Exercise CP DMA copy/fill paths, semaphore wait/signal paths, EOP fence signaling, scratch/atomic operations, append buffers, indirect draw/dispatch/index addresses, and ME coherency programming on GC 11 hardware.
- Exercise power and throttling workloads that stress EDC/CAC/PCC/PWRBRK/DIDT controls and watch for unexpected throttle levels, overflow counters, unstable clocks, performance regressions, or thermal/power-limit anomalies.
- Test graphics workloads covering indexed and indirect draws, primitive type/index type changes, tessellation, GS/fast-launch paths, stereo state, line stipple, multi-instance draws, and geometry-engine subgroup controls.
- Inspect debugfs/register dumps for decoded HPD queue status, SPI trap/wave controls, TCP status, GCR status, CAC/EDC counters, RLC GPM counters, GRBM index selection, CP pipe stats, VGT counters, and GE controls. Known-good dumps should decode consistently with hardware documentation.
- Stress suspend/resume, GPU reset, runtime power management, queue teardown/restart, and hang recovery paths. Warning signals include CP/ME/PFP timeouts, bad fence completion, semaphore waits that never resolve, corrupted output buffers, false idle detection, bad performance-counter values, and workload-specific rendering corruption.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002514`. The final per-file report for `gc_11_0_0_sh_mask.h` should merge this with adjacent chunks before making whole-file statements.

The previous chunk owns the beginning of `CP_DEBUG_2`, including its register comment and shift macros. This chunk resumes with `CP_DEBUG_2` masks and then covers complete generated families through `PA_SC_LINE_STIPPLE_STATE`. The next chunk owns the field definitions for `PA_SC_SCREEN_EXTENT_MIN_0` and subsequent rasterizer/screen-extent registers.

### subset-b-002515: lines 27319-30049

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 27319-30049

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, debug, profiling, and power/reset paths to compose or decode 32-bit graphics-core register values. The corresponding register addresses are provided by the companion GC 11.0.0 offset header.

The selected range starts in primitive-assembler/screen-space controls, then covers SQ/SQC trace and cache control, GDS and streamout accounting, SPI setup/throttle controls, a large RS64 command-processor block for MES/MEC/GFX microcontrollers, GL1/CH/GL2 cache and arbitration controls, GL1H controls, and the beginning of the GC performance counter data block. Although the repository root is named `ceph-client`, this source file is AMD GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, allocations, locks, or callbacks in this range. The only exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field in a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for that field.
- Consumers combine these field macros with matching `reg*` or `mm*` offset symbols and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

Major register families in this chunk:

- PA/SC screen and trap registers: `PA_SC_SCREEN_EXTENT_MIN_0`, `PA_SC_SCREEN_EXTENT_MAX_0`, `PA_SC_SCREEN_EXTENT_MIN_1`, `PA_SC_SCREEN_EXTENT_MAX_1`, and P3D/HP3D/general `PA_SC_*TRAP_SCREEN*` registers define 16-bit X/Y extents, trap X/Y coordinates, trap occurrence counters, and pre-shader trap enable/force bits.
- SQ/SQC and texture-address setup: `SQ_THREAD_TRACE_USERDATA_0` through `_7` carry full-width thread-trace userdata, `SQC_CACHES` selects instruction/data cache invalidation targets and exposes completion, and `TA_CS_BC_BASE_ADDR(_HI)` defines a compute-shader border-color base address split across low and high parts.
- DB/GDS/streamout state: `DB_OCCLUSION_COUNT[0-3]_{LOW,HI}` expose query counters; `GDS_RD_*` and `GDS_WR_*` provide direct and burst read/write data windows; `GDS_ATOM_*` defines atomic operation parameters and return data; `GDS_GWS_RESOURCE*` and `GDS_OA_*` expose global-wave-sync and ordered-append resource state; `GDS_STRMOUT_DWORDS_WRITTEN_*`, `GDS_GS_*`, and `GDS_STRMOUT_PRIMS_*` expose streamout and geometry-shader accounting.
- SPI controls: `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, `SPI_WAVE_LIMIT_CNTL`, `SPI_GS_THROTTLE_CNTL1`, `SPI_GS_THROTTLE_CNTL2`, `SPI_ATTRIBUTE_RING_BASE`, and `SPI_ATTRIBUTE_RING_SIZE` define shader-processor input arbitration, event enable bits, power-save disables, vertex/PS timing, wave granularity, GS/PS throttling, and attribute-ring base/size.
- `addressBlock: gc_cprs64dec`: RS64 command-processor registers for MES, MEC, and GFX engines. This includes program-counter starts, trap/vector addresses, interrupt enables/status, instruction pointers, scratch/indexed scratch windows, RISC-V-like status/cause/bad-address/cycle/time/ISA/vendor/hart registers, cache base and invalidate controls, process quantum, doorbell controls, general-purpose registers, local data/instruction/scratch apertures, performance counter controls, pending interrupts, interrupt data slots 16-31, and DC aperture base/mask/control windows 0-15.
- GFX RS64 dual-engine state: `CP_GFX_RS64_*` repeats interrupt, local aperture, dcache, perfcount, pending-interrupt, GP, instruction-pointer, and DC aperture fields for engine selectors `0` and `1`, with `CP_GFX_CNTL` selecting/configuring the active graphics engine.
- `addressBlock: gc_gl1dec`: `GL1_DRAM_BURST_MASK`, `GL1_ARB_STATUS`, `GL1I_GL1R_REP_FGCG_OVERRIDE`, `GL1C_STATUS`, and `GL1C_UTCL0_*` cover GL1 arbitration/burst behavior, fine-grain clock-gating overrides, GL1C stall/busy status, UTCL0 VM response and invalidation controls, fault/retry/PRT detection, and retry counts.
- `addressBlock: gc_chdec`: `CH_ARB_CTRL`, `CH_DRAM_BURST_*`, `CHA_CHC_CREDITS`, `CHA_CLIENT_FREE_DELAY`, `CHI_CHR_REP_FGCG_OVERRIDE`, `CH_VC5_ENABLE`, `CHC_*`, and `CHCG_*` define channel arbitration, memory/IO burst behavior, credits, client-free delay, clock-gating overrides, status/stall counters, and channel-cache controls.
- `addressBlock: gc_gl2dec`: `GL2C_CTRL`, `GL2C_CTRL2`, `GL2C_CTRL3`, and `GL2C_CTRL4` define L2 cache sizing, FIFOs, hashing, priority, writeback, metadata, coherency, read/write, MGCG, and EA/NACK behavior. `GL2C_WBINVL2`, `GL2C_SOFT_RESET`, `GL2C_CM_*`, `GL2C_LB_*`, `GL2C_DISCARD_STALL_CTRL`, and `GL2A_*` cover writeback-invalidate done state, halt-for-reset, compression-manager settings, L2 bank/load-balance counters, discard throttling, address-match controls, priority disabling, and response throttling.
- `addressBlock: gc_gl1hdec`: `GL1H_ARB_CTRL`, `GL1H_GL1_CREDITS`, `GL1H_BURST_MASK`, `GL1H_BURST_CTRL`, and `GL1H_ARB_STATUS` cover GL1 hub arbitration, credits, burst sizing, clock-gating disable bits, and busy/illegal-request status.
- `addressBlock: gc_perfddec`: the chunk begins the performance data decode block with `CPG`, `CPC`, `CPF`, `GRBM`, per-SE GRBM, and `GE1` low/high counter and latency-stat data registers.

Important field themes include `ADDR`, `BASE`, `MASK`, `CNTL`, `STATUS`, `ACTIVE`, `RESET`, `HALT`, `STEP`, `INSTR_PNTR`, `INT`, `PENDING_INTERRUPT`, `INVALIDATE_*`, `*_COMPLETE`, `CACHE_POLICY`, `VMID`, `APERTURE`, `DOORBELL`, `PRIORITY`, `CREDIT`, `BUSY`, `STALL`, `FAULT_DETECTED`, `RETRY_DETECTED`, `ENABLE`, `SIZE`, `DATA`, `COUNTER`, and full-width `0xFFFFFFFFL` payload/counter windows.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by include users and hardware:

1. GC 11 code includes this shift/mask header together with the matching GC 11 offset header.
2. Driver code chooses a concrete register offset for the ASIC instance and block.
3. The field macros here are used to pack a new register value, update selected bits with read-modify-write helpers, or decode a value read from hardware.
4. AMDGPU helpers perform the actual MMIO or indirect access while higher-level GFX, KFD, reset, queue, and power-management code provides ordering, locking, timeout, and firmware sequencing.

The RS64 command-processor fields participate in firmware bring-up and recovery sequences: program-counter/vector registers are programmed, instruction and data caches are invalidated or primed, pipe reset/active/halt/step bits are toggled or polled, doorbell controls are configured, and instruction pointers or pending interrupt registers are sampled for diagnostics. In this tree, neighboring GC 11 and GC 12 GFX code references these same families through `SOC15_REG_ENTRY_STR`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` for debug register lists, MEC/MES pipe reset, cache invalidation, firmware memory setup, and hang analysis.

The cache and memory-system registers describe control surfaces rather than procedures. GL1/CH/GL2 users must decide when it is safe to halt, reset, invalidate, throttle, alter arbitration/credit settings, or sample status. The `GL2C_WBINVL2__DONE` and RS64 `*_INVALIDATE_*_COMPLETE` bits are examples of completion/status signals that polling code can use after issuing an action bit elsewhere.

## State And Persistence Behavior

This file stores no software state and persists nothing by itself. It describes hardware state in GC 11.0.0 registers.

The represented state includes screen extents and trap counters, thread-trace userdata, SQC cache invalidation target/completion bits, compute border-color base addresses, DB occlusion query counters, GDS direct/burst data windows, GDS atomic operands/results, GWS/OA allocation and queue state, streamout/GS counters, SPI arbitration and throttling controls, RS64 firmware control/status registers, local data/instruction/scratch apertures, command-processor GP registers, per-engine interrupt and pending-interrupt state, GL1/CH/GL2 cache configuration, arbitration and credit settings, TLB/fault/retry status, L2 writeback-invalidate and soft-reset status, L2 load-balance/perf counter data, and GC perfcounter readback values.

Persistence is hardware-defined. Some fields are configuration that remains until reset, GPU reset, suspend/resume, runtime power transition, or explicit reprogramming. Some are action strobes or self-clearing requests, such as invalidation, clear/load/start, reset, halt-for-reset, release-all, or retry increment fields. Some are live hardware-owned status or counters that can change asynchronously while shaders, queues, firmware, or cache pipelines are running. Full-width `DATA`, `COUNTER`, `PERFCOUNTER_LO/HI`, and `*_INT` fields are untyped payload windows here; full-width masks do not imply that writes are safe.

The macros do not encode read-only, write-only, write-one-to-clear, sticky, self-clearing, reserved, privileged, or indirect-only semantics. Consumers must preserve unrelated bits in mixed-control registers and follow the hardware programming guide for ordering, polling, and reset behavior.

## Dependencies And Integration Points

The direct companion dependency is the generated GC 11.0.0 offset header, normally `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides the matching `reg*`, `mm*`, and base-index symbols. Generated default and enum headers may provide reset values or event selectors, but this chunk only defines bit positions and masks.

Important integration points include:

- AMDGPU GFX 11 initialization, reset, hang-dump, and debug paths that include GC 11 register metadata and list command-processor, SQC, GL1/GL2, and performance registers.
- AMDKFD/MES scheduling and queue-management paths, because `CP_MES_*`, `CP_MEC_RS64_*`, doorbell, local aperture, pending interrupt, and process-quantum fields describe firmware-controlled command scheduling state.
- Firmware loading and recovery, where program-counter starts, vector registers, instruction pointers, GP registers, cache invalidation controls, and pipe reset/active/halt bits are used to start, stop, inspect, or recover RS64 firmware engines.
- Cache/TLB and VM integration, especially `SQC_CACHES`, `GL1C_UTCL0_*`, GL2 writeback/invalidate, GL2 coherency/hash/metadata controls, VMID fields, local aperture masks, and fault/retry/PRT status bits.
- GDS and streamout integration in graphics queue packet emission and resource allocation. Similar GDS/GWS macros are used by older/newer GFX paths to program per-VMID GDS/GWS state and packet payloads.
- Profiling and telemetry integration: thread-trace userdata, SPI event enables, GL2 load-balance counters, CP/GRBM/GE perfcounter low/high registers, and latency-stat data registers are read by debugfs, perf, RGP, or internal diagnostics.
- Power and clock-gating policy: `FGCG`/`MGCG` override fields, power-save disable fields, burst/credit/throttle controls, and cache clock-gating modes can interact with SMU policy, golden settings, runtime power management, and ASIC-specific workarounds.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. These constants are untyped and can compile while targeting the wrong GC revision or register block if paired with incompatible offsets.
- The chunk boundaries are artificial. It starts after the first lines of `PA_SC_SCREEN_EXTENT_MIN_0` and ends immediately after `GE1_PERFCOUNTER3_HI`; adjacent chunks are needed for complete source-file coverage.
- RS64 control bits are sequencing-sensitive. Misusing `*_PIPE*_RESET`, `*_ACTIVE`, `HALT`, `STEP`, program-counter, vector, cache-invalidate, or local-aperture fields can leave MES/MEC/GFX firmware stopped, executing from the wrong address, or reporting misleading instruction pointers.
- Cache invalidation fields require polling and timeout handling. `SQC_CACHES__COMPLETE`, RS64 `*_INVALIDATE_*_COMPLETE`, and `GL2C_WBINVL2__DONE` can race with in-flight work if issued without drains, fences, or reset sequencing.
- Full-width register fields are ambiguous. `DATA`, `INT`, `PERFCOUNTER`, `PENDING_INTERRUPT`, GP, scratch, GDS read/write, and aperture base/mask fields may be readback, write payload, hardware-owned status, or action windows depending on the register.
- GDS/GWS/OA registers mix allocation state, queue head state, counters, and action bits such as `RELEASE_ALL`; an incorrect write can release resources or corrupt synchronization visible to graphics or compute queues.
- Address, base, mask, and aperture fields are alignment- and unit-sensitive. Splitting addresses across low/high registers, using field masks as byte masks, or ignoring implicit address shifts can place firmware, scratch, border color, GDS, or local apertures incorrectly.
- GL1/CH/GL2 cache and arbitration knobs affect global memory-system behavior. Wrong credit, burst, priority, coherency, hash, volatile, metadata, NACK, or force-miss settings can cause severe performance regressions, stale data, replay storms, GPU hangs, or failures only under specific workloads.
- Fault and retry bits in `GL1C_UTCL0_STATUS` and retry counters are live status. Tests must tolerate transitions and clear/observe semantics rather than assuming a stable snapshot.
- Reserved, unused, and chicken-bit fields appear throughout the chunk. Driver code should preserve such bits unless an ASIC-specific workaround explicitly requires changing them.
- Perfcounter low/high pairs are not necessarily atomic. Readers need a stable sampling method, especially for counters that can roll over between `LO` and `HI` reads.

## Test Signals

Useful validation is mostly build, generated-header consistency, hardware smoke, reset, and profiling coverage:

- Build GC 11 AMDGPU, AMDKFD, KFD/MES, and SMU-adjacent code that includes `gc_11_0_0_sh_mask.h` with the matching offset header.
- Generated-header checks that every field has a `__SHIFT` and `_MASK`, masks align with shifts, fields for each register do not overlap except documented aliases/reserved fields, and register names in this slice exist in the GC 11 offset header.
- RS64 firmware bring-up tests that program MES/MEC/GFX program-counter/vector registers, invalidate/prime caches, toggle pipe reset bits, poll active/halt/instruction-pointer state, and verify firmware queues accept work after reset and resume.
- MES/KFD queue tests that exercise doorbell setup, process quantum, pending-interrupt handling, local scratch/data/instruction apertures, queue preemption, eviction/restore, and GPU reset recovery.
- Cache and VM tests that issue SQC invalidations, GL2 writeback/invalidate, GL1 UTCL0 invalidation/fault/retry paths, and workloads that stress VM faults, PRT, retry/XNACK-like behavior, and coherency between shader, CP, and memory clients.
- GDS/streamout tests that allocate GDS/GWS/OA resources, issue atomics and streamout/GS workloads, verify counters/readback data, and ensure resource release/reset paths do not leak or corrupt per-VMID state.
- Graphics pipeline tests that vary PA/SC extents/trap screen behavior, occlusion queries, SPI attribute-ring sizing, wave limits, GS throttling, and shader trace userdata collection.
- Profiling tests that enable thread trace and performance counters, sample CP/GRBM/GE/GL2 low/high pairs, and compare monotonicity or workload sensitivity against known workloads.
- Reset, suspend/resume, runtime power-gating, and GPU recovery tests while graphics/compute queues and profiling are active, because RS64 state, GDS counters, cache configuration, and perfcounter state can be lost or become stale.
- Regression indicators include MES or MEC firmware failing to leave reset, stuck instruction pointers, incomplete cache invalidation, unexpected GL1/GL2 busy or stall bits, increased VM fault/retry status, GDS/GWS deadlocks, nonsensical performance counters, or failures isolated to GC 11 hardware.

### subset-b-002516: lines 30050-32601

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 30050-32601

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it exports preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU and AMDKFD code to compose, preserve, write, and decode memory-mapped graphics-core registers for this ASIC generation. The companion register-address definitions live in `gc_11_0_0_offset.h`.

The selected range is centered on graphics-core performance-monitoring registers. It starts in the tail of the `gc_gfxdec` performance counter data registers, switches into the `gc_perfsdec` address block, and then defines selector/control fields for command-processor, GRBM, geometry, rasterizer, shader, cache, texture, GDS, GCEA, and thread-trace performance facilities. The path is under a Ceph source mirror, but this file is AMD GPU hardware metadata rather than filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, locks, allocations, or direct MMIO operations in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Callers combine these macros with `reg*`/`mm*` address macros from `gc_11_0_0_offset.h` and low-level helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent register programming helpers.

Major register groups in this chunk:

- Counter value registers: low/high 32-bit halves for many performance counters, including `GE2_DIST`, `GE2_SE`, `PA_SU`, `PA_SC`, `SPI`, `PC`, `SQ`, `SQG`, `SX`, `GCEA`, `GDS`, `TA`, `TD`, `TCP`, `GL2C`, `GL2A`, `GL1C`, `CHC`, `CHCG`, `CB`, `DB`, `RLC`, `RMI`, `GCR`, `PA_PH`, `UTCL1`, `GL1A`, `GL1H`, `CHA`, and `GUS`. Most expose full-width `PERFCOUNTER_LO` or `PERFCOUNTER_HI` masks.
- Command-processor performance selection: `CPG_PERFCOUNTER*_SELECT`, `CPC_PERFCOUNTER*_SELECT`, and `CPF_PERFCOUNTER*_SELECT` fields select event IDs and counter modes, with `SPM_MODE` fields for streaming performance monitoring paths.
- Global performance monitor control: `CP_PERFMON_CNTL` defines `PERFMON_STATE`, `SPM_PERFMON_STATE`, `PERFMON_ENABLE_MODE`, and `PERFMON_SAMPLE_ENABLE`.
- CP windowing and latency selectors: `CPF_TC_PERF_COUNTER_WINDOW_SELECT`, `CPG_TC_PERF_COUNTER_WINDOW_SELECT`, `CPC_TC_PERF_COUNTER_WINDOW_SELECT`, and the corresponding `*_LATENCY_STATS_SELECT` registers define index, enable, clear, and always-on bits for transaction counter windows and latency-stat windows.
- Draw-window counters: `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` define draw/object counting and window enable/clear/object filters.
- GRBM selectors: `GRBM_PERFCOUNTER0_SELECT`, `GRBM_PERFCOUNTER1_SELECT`, per-shader-engine selectors `GRBM_SE0_PERFCOUNTER_SELECT` through `GRBM_SE6_PERFCOUNTER_SELECT`, and high selector registers expose event selection plus many busy/clean user-defined mask bits for DB, CB, geometry, texture, shader, scan converter, PA, RLC, BCI, TCP, UTCL1, GL1, SEDC, and RMI style blocks.
- Per-block performance counter selectors: repeated `*_PERFCOUNTERn_SELECT` and `*_SELECT1` layouts for `GE1`, `GE2_DIST`, `GE2_SE`, `PA_SU`, `PA_SC`, `SPI`, `PC`, `SQ`, `SQG`, `SX`, `GDS`, `TA`, `TD`, `TCP`, and the start of `GL2C`. These expose event slots (`PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`) and counter/performance modes (`CNTR_MODE`, `PERF_MODE`, `PERF_MODE1`, `PERF_MODE2`, `PERF_MODE3`).
- TCP filtering: `TCP_PERFCOUNTER_FILTER`, `TCP_PERFCOUNTER_FILTER2`, and `TCP_PERFCOUNTER_FILTER_EN` define texture-cache performance-filter fields for buffer/flat/dimensional operations, data and number formats, swizzle mode, sample count, opcode type, GLC/SLC, compression, and address mode matching.
- SQ/SQG controls: `SQ_PERFCOUNTER_CTRL`, `SQG_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_CTRL2`, `SQG_PERFCOUNTER_CTRL2`, and `SQG_PERF_SAMPLE_FINISH` expose shader-stage enables, ME/pipe disable masks, force-enable/VMID-enable controls, and sample-finish status.
- Shader thread trace: `SQ_THREAD_TRACE_BUF0_BASE/SIZE`, `SQ_THREAD_TRACE_BUF1_BASE/SIZE`, `SQ_THREAD_TRACE_CTRL`, `SQ_THREAD_TRACE_MASK`, `SQ_THREAD_TRACE_TOKEN_MASK`, `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_STATUS2`, draw/marker counters, and `SQ_THREAD_TRACE_DROPPED_CNTR` define buffer placement, trace capture mode, token filtering, selected SIMD/WGP/SA/wave types, write pointer state, ownership/busy/error status, buffer-full/lost-packet flags, and trace accounting counters.
- GCEA result/control registers: `GCEA_PERFCOUNTER2_SELECT`, `GCEA_PERFCOUNTER2_SELECT1`, `GCEA_PERFCOUNTER2_MODE`, `GCEA_PERFCOUNTER0_CFG`, `GCEA_PERFCOUNTER1_CFG`, and `GCEA_PERFCOUNTER_RSLT_CNTL` select GCEA events and configure/clear performance result handling.

The requested line range ends at `GL2C_PERFCOUNTER0_SELECT1__PERF_MODE3__SHIFT`; the corresponding `GL2C_PERFCOUNTER0_SELECT1` masks are immediately after the chunk boundary and must be covered by the next chunk.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior comes from GC 11 driver code that includes the generated offset and mask headers:

1. A GC 11.0.0 consumer includes `gc/gc_11_0_0_offset.h` and `gc/gc_11_0_0_sh_mask.h`.
2. The consumer selects the register address from the offset header and the field layout from this mask header.
3. It builds register values with shifts/masks or decodes readback values from MMIO.
4. AMDGPU/AMDKFD register helpers perform the actual direct or indexed register access while the relevant GFX, KFD, RLC, MES, debug, profiling, or firmware path owns sequencing.

The chunk describes how performance counters, filters, thread-trace buffers, and performance control/status registers are encoded. It does not describe when profiling can be enabled, how counters are reserved between clients, how power-gated blocks are awakened, or which writes are safe while the GPU is executing. Those rules live in the consuming driver code, firmware contracts, and hardware programming guide.

## State And Persistence Behavior

The file stores no software state and persists nothing. It only names bit ranges for hardware state.

The hardware state represented here is mostly profiling and debug state:

- Counter data registers hold live or latched low/high counter values for many graphics sub-blocks.
- Selector registers persist chosen event IDs and counter modes until reset, power transition, or reprogramming.
- `CP_PERFMON_CNTL` controls global perfmon/SPM enable and sample state.
- CP draw-window and latency selectors gate what draws, windows, and latency-stat buckets are counted.
- GRBM selectors and user-defined busy masks influence global-busy performance observations.
- TCP filters restrict texture/cache performance events to matching request attributes.
- SQ/SQG controls select shader stages, VMIDs, and ME/pipe participation in shader performance sampling.
- SQ thread-trace buffer registers hold GPU buffer base/size, write pointer, capture mode, token inclusion/exclusion, and status/error/full/lost-packet indicators.
- GCEA registers select and control geometry/command-engine-adjacent counter result handling.

Persistence is hardware-defined. Some fields are ordinary configuration, some are read-only counters or status, some are clear/enable bits, and some can be sticky until explicitly cleared or until reset. The macros alone do not identify access type, reset value, side effects, or ownership, so callers must preserve unrelated bits and follow hardware-specific ordering.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which supplies the matching register offsets and base indices. Pairing this mask file with another generation's offset header is unsafe even when names overlap.

Observed GC 11.0.0 include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.c`

Integration points include GFX 11 initialization, KFD debug/profiling support, MES scheduling interaction, RLC/IMU golden-register programming, performance counter reservation and sampling, shader thread tracing, GPU reset/recovery, suspend/resume, runtime power management, and hardware validation. Related semantic definitions for thread-trace token types and modes appear in generation-wide enum headers, while this chunk supplies the GC 11.0.0 register packing.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. These names are similar across GC generations, but field widths and bit positions can change.
- The macros are untyped integer constants. Misusing a mask with the wrong register can compile cleanly while corrupting profiling control or decoding the wrong hardware state.
- Many counter data registers use `0xFFFFFFFFL` full-width masks. Those often represent readback counters, not safe whole-register write values.
- Low/high counter halves can race with live counter increments. Consumers that need coherent 64-bit values may need hardware latching, stop/sample controls, or retry logic outside this header.
- Selector registers pack several event slots and modes into one word. Whole-register writes can unintentionally change another selected event, mode, SPM setting, or reserved field.
- `CP_PERFMON_CNTL` and SQ/SQG control bits affect global profiling state. Incorrect sequencing can disturb other profiling clients, lose samples, or leave counters enabled during reset/power transitions.
- Thread-trace buffer base/size fields are hardware-facing GPU addresses and sizes. Incorrect address alignment, size encoding, double-buffer configuration, or VMID selection can lead to lost packets, write errors, full buffers, or traces owned by the wrong VMID.
- `SQ_THREAD_TRACE_STATUS`/`STATUS2` fields include busy, owner, write-error, buffer-full, packet-lost, and buffer-issue indicators. Ignoring those fields can make trace data look valid when it is incomplete.
- TCP filter fields are split between value registers and enable bits. Programming only the filter value or only the enable mask can yield unexpectedly broad or narrow sampling.
- GRBM and per-SE masks expose a large number of user-defined busy-mask bits. Incorrect masks can make global-busy metrics misleading and hide or exaggerate unit activity.
- The chunk boundary cuts through `GL2C_PERFCOUNTER0_SELECT1`; the masks for the final four shift fields are outside this work item. Merge/reconciliation must combine adjacent chunks for a complete per-file view.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware/profiling behavior:

- Build coverage for GC 11 AMDGPU, AMDKFD, MES, IMU, SOC21, and display paths that include `gc_11_0_0_sh_mask.h`.
- Generated-header checks that every field has coherent shift/mask pairs, masks do not overlap within a register except documented aliases, and every register in this chunk has a matching offset entry in `gc_11_0_0_offset.h`.
- Static checks that code uses the GC 11.0.0 offset and mask headers together and does not combine same-named fields from older `gc_9_*`, `gc_10_*`, or `gca/gfx_*` headers.
- Performance-counter smoke tests that program representative CP, GRBM, SQ/SQG, SPI, PC, TCP, GDS, and cache counter selectors, run known workloads, stop/sample counters, and verify nonzero/plausible low/high readback.
- Coherency tests for low/high counter reads under load, especially where counters can roll over while being sampled.
- TCP filter tests that toggle individual filter-enable bits and verify matching workloads affect only the intended filtered counters.
- Shader thread-trace tests that program buffer base/size, trace masks, token masks, double-buffer/high-water controls, collect traces, and assert that status/error/full/lost-packet fields match the captured data.
- Reset, suspend/resume, and runtime power-management tests while profiling or thread tracing is active, checking that counters are disabled or restored according to driver policy and do not hang after recovery.
- Regression signals include saturated or permanently zero counters, bad high/low counter stitching, unexpected `SQ_THREAD_TRACE_STATUS` write errors, buffer-full/lost-packet flags during small traces, VMID ownership mismatches, profiling interference between clients, and hangs isolated to GC 11 performance-monitoring paths.

### subset-b-002517: lines 32602-35135

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 32602-35135

## Purpose

This chunk is a generated AMD GC 11.0.0 register field mask header segment. It defines `__SHIFT` and `_MASK` constants for bitfields in Graphics Core registers so C driver code can construct, read, and modify register values without hard-coded bit positions. The lines in this chunk contain 2,138 `#define`s under 386 register/comment headings and span several hardware areas: graphics cache/color/depth/performance counters, RLC streaming performance monitor and accumulation controls, GRTAVFS/RTAVFS voltage-frequency interface registers, CP microcode/cache base registers, and a large RLC control/power-management/profiling section.

The file itself has no executable code. Its purpose is ABI-like register metadata for ASIC-specific driver paths that include `gc/gc_11_0_0_sh_mask.h` and pair these field definitions with address definitions from `gc_11_0_0_offset.h`.

## Important APIs, Types, and Macros

There are no functions or C types in this chunk. The exported interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: right-shift amount for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask in the 32-bit register value.

Major macro groups in this chunk:

- Performance counter select fields for `GL2C`, `GL2A`, `GL1C`, `GL1A`, `GL1H`, `CHC`, `CHCG`, `CHA`, `CB`, `DB`, `RMI`, `GCR`, `PA_PH`, `UTCL1`, and `GUS`. These mostly expose `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, `COUNTER_MODE`, and `PERF_MODE*` fields. `CB_PERFCOUNTER_FILTER` adds operation, format, clear, MRT, sample-count, and fragment-count filter selectors.
- RLC SPM/perfmon macros such as `RLC_SPM_PERFMON_CNTL`, `RLC_SPM_PERFMON_RING_BASE_LO/HI`, `RLC_SPM_RING_WRPTR/RDPTR`, `RLC_SPM_PERFMON_SEGMENT_SIZE`, mux select registers, accumulation dataram/ctrlram accessors, `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, `RLC_SPM_ACCUM_MODE`, request/return RSPM registers, `RLC_SPM_RSPM_CMD`, and `RLC_SPM_RSPM_CMD_ACK`.
- RLC general perf and IOV counters: `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER0/1_SELECT`, and `RLC_GPU_IOV_PERF_CNT_*` address/data/control fields.
- GRTAVFS/RTAVFS fields in `gc_grtavfs_grtavfs_dec`, `gc_grtavfs_se_grtavfs_dec`, and `gc_grtavfsdec`, including target frequency, target voltage, request/valid bits, soft reset, PSM count/sample enable, register address/data, and clock select controls.
- CP hypervisor and firmware-facing fields in `gc_cphypdec`, including PFP/ME/MEC microcode address/data registers, ME RAM address/data registers, CP instruction-cache base/control/op registers, MES instruction/data base and bounds, RS64 data cache bases, and MEC data/instruction bounds. The `CP_*_IC_BASE_CNTL` fields expose VMID, address clamp, execute-disable, and cache policy settings.
- RLC control and state macros from `gc_rlcdec`, including `RLC_CNTL`, firmware version, busy status, refclock/GPU clock captures, GPM timers and interrupt status/clear/disable/force controls, GPM thread reset/priority/enable/cache-invalidate fields, RLCG/RLCV doorbell range/control/status/data registers, clock gating/power gating controls, serdes masks/status/control/data, SRM indexed command/data windows, UTCL1 controls/status/error capture, semaphores, PACE timer/interrupt controls, CP stat invalidation, and shader profiling controls such as `RLC_SPP_CTRL`, `RLC_SPP_SHADER_PROFILE_EN`, and `RLC_SPP_SSF_CAPTURE_EN`.

## Control Flow

This header contributes no direct control flow. Runtime control flow occurs in consumers that:

1. Include this header and the matching offset header.
2. Read a 32-bit MMIO register with helpers such as `RREG32_SOC15`.
3. Compose or extract fields via driver macros such as `REG_SET_FIELD` and `REG_GET_FIELD`, which depend on this file's `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` symbols.
4. Write the resulting value back with helpers such as `WREG32_SOC15`.

The chunk's register groups imply several hardware workflows:

- Performance monitoring selects a block counter source with `*_PERFCOUNTER*_SELECT*`, optional filters, modes, and RLC SPM mux/accumulation routing before sampling into rings or counters.
- RLC SPM setup programs ring base/size, mux selection, accumulation mode, thresholds, and sample counts, then observes status bits such as done, overflow, FIFO empty, and sequence-in-progress.
- CP microcode/cache setup writes microcode address/data or instruction-cache base/control fields and uses invalidate/prime operation bits to manage CP instruction caches.
- RLC power and clock management programs timers, clock count capture, power-gating enables/delays, auto power gating, clock-gating overrides, serdes commands, and doorbell handling.
- UTCL1 error/status flows expose busy, retry/fault/PRT detection, VMID, and address capture fields that consumers can poll or log during GPU memory translation faults.

## State and Persistence Behavior

The macros are compile-time constants and do not store state themselves. The state described by this chunk lives in GPU registers and firmware-accessible hardware blocks:

- Performance counter and SPM registers persist only as hardware register configuration until reset, suspend/resume reinitialization, ASIC reset, or driver reprogramming.
- Ring base, size, read/write pointer, mux select, and accumulation fields define where sampled performance data is written and how samples are segmented. Incorrect values can persist long enough to corrupt profiling output or cause invalid memory accesses by the hardware perf monitor path.
- CP microcode address/data and instruction-cache base/control registers affect firmware instruction memory/cache behavior. These are normally initialized by gfx/CP startup and resume flows.
- RLC power-management, timer, doorbell, and clock-gating fields persist as hardware control state and directly affect runtime power behavior, interrupt pacing, and RLC firmware communication.
- Status registers such as `RLC_STAT`, `RLC_GPM_TIMER_STAT`, `RLC_SPM_STATUS`, `RLC_UTCL1_STATUS`, `RLC_RLCG_DOORBELL_STAT`, and `RLC_RLCV_DOORBELL_STAT` expose volatile hardware state. Clear bits in interrupt/timer controls usually have side effects when written by consumers.

## Dependencies and Integration Points

This chunk is tightly coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides the matching `reg...` register addresses and base indexes.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.
- GC 11 driver files that include this header, including `amdgpu/gfx_v11_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdgpu/mes_v11_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/soc21.c`, `amdkfd/kfd_device_queue_manager_v11.c`, and `amdkfd/kfd_mqd_manager_v11.c`.
- CP firmware and MES setup paths. For example, gfx code sets `CP_PFP_IC_BASE_CNTL` fields such as `VMID`, `CACHE_POLICY`, `EXE_DISABLE`, and `ADDRESS_CLAMP` while configuring instruction-cache base behavior.
- Profiling/performance tooling paths that depend on the SPM, block performance counter, and shader profiling field layouts.
- Power management and clock-gating paths, especially RLC power-gating, CGCG/CGLS, serdes, SMU clock request, and PACE timer/interrupt controls.

## Risks and Edge Cases

- Generated header drift is the primary risk. If masks or shifts do not match the GC 11.0.0 hardware spec or the paired offset header, every consumer using `REG_SET_FIELD` can silently program the wrong bits.
- Similar register names across ASIC generations make accidental cross-generation reuse dangerous. Several fields are close to older GC/GFX versions but not identical; for example, shader profile fields in GC 11 have a reserved bit where older generations had VS-specific naming.
- Some paired select registers use non-obvious mode ordering. `CB_PERFCOUNTER0_SELECT1`, `DB_PERFCOUNTER*_SELECT1`, `RMI_PERFCOUNTER*_SELECT1`, and `PA_PH_PERFCOUNTER*_SELECT1` place `PERF_MODE3` at bits 27:24 and `PERF_MODE2` at bits 31:28, while other blocks may name mode fields in ascending order. Consumers should use field macros instead of assuming layout by suffix.
- Reserved masks are large in many RLC power/clock registers. Read/modify/write paths must preserve reserved bits unless the programming guide explicitly requires zeroing them.
- CP microcode and instruction-cache control fields are high impact. Incorrect `VMID`, base, bounds, `EXE_DISABLE`, cache policy, or invalidate/prime usage can break command processor firmware execution.
- RLC SPM ring base/size and accumulation controls can affect DMA-like hardware writes and profiling collection. Bad base/size, segment, or mux settings can produce bogus profiling data or hardware faults.
- Doorbell range/control fields for RLCG/RLCV must match queue/doorbell allocation policy; enabling an incorrect doorbell ID or range risks lost or misrouted firmware notifications.
- UTCL1 status/error fields combine fault type, VMID, and address fragments. Diagnostics must combine `_ERROR_1` and `_ERROR_2` correctly and account for volatile status.
- Interrupt clear/force/disable registers can have write-side effects. Tests and debug code should not treat every field as ordinary persistent configuration.

## Test Signals

Useful verification signals for this chunk are mostly build-time, register-programming, and hardware-observation based:

- Full AMDGPU build coverage for files including `gc_11_0_0_sh_mask.h`; missing or renamed macros should fail compilation in GC 11 paths.
- Static checks that every `REG_SET_FIELD(x, REGISTER, FIELD, value)` reference has matching `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions in the selected ASIC header.
- Cross-check generated masks against `gc_11_0_0_offset.h` register coverage and against adjacent generated headers (`gc_11_0_0_default.h`, newer GC 11.x headers) for expected deltas.
- Runtime smoke tests for gfx init/resume/reset paths, especially CP instruction-cache setup and RLC firmware startup, because those paths use high-impact CP/RLC fields.
- Performance counter tests that program GL/CB/DB/RMI/GUS/PA_PH/UTCL1 counters and verify plausible counter deltas under known workloads.
- SPM profiling tests that validate ring base/size programming, write pointer movement, accumulation done/overflow status, and sample interval behavior.
- Power-management tests that exercise RLC power gating, clock gating, PACE timers, SMU clock request, and serdes busy/status polling through suspend/resume and reset.
- Fault-injection or debug tests that verify UTCL1 fault/retry/PRT status and error address/VMID capture decode correctly.

### subset-b-002518: lines 35136-37567

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 35136-37567

## Scope

This chunk is a generated AMDGPU GC 11.0.0 shift/mask header segment. It contains C preprocessor constants only: for each hardware register field, `REGISTER__FIELD__SHIFT` gives the bit position and `REGISTER__FIELD_MASK` gives the encoded mask. The matching register offsets are in `gc_11_0_0_offset.h`, and defaults are in the generated GC default header. Driver code combines these masks with `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and firmware/golden-register tables to program or inspect GC 11 hardware.

The range starts in the shader profiling processor area with `RLC_SPP_SSF_THRESHOLD_1` and ends at the first field group for `ICG_GL1C_CLK_CTRL`. It spans three generated address-block areas: the tail of the main RLC block, the complete `gc_rlcsdec` RLC sequencer/control block, the compact `gc_pfvfdec_rlc` PF/VF RLC block, and the beginning of `gc_pwrdec` graphics power/clock-gating controls.

## Purpose

The purpose of this header slice is to define the bitfield contract for GC 11 RLC, RLC sequencer, firmware messaging, interrupt, residency, doorbell, IMU, SPM, and clock-gating registers. These macros are not optional documentation; they are the source-level ABI used by AMDGPU, KFD, MES, IMU, display, gfxhub, SDMA, and SOC initialization code when writing packed MMIO values.

The main covered register families are:

- RLC SPP profiling and capture fields: shader-type thresholds, inflight read address/data, shader IDs, CAM hit/lock/conflict state, PVT counters, stall updates, PBB override info, reset bits, and SPP CAM access.
- RLC doorbell interfaces: `RLC_RLCP_DOORBELL_*` and `RLC_XT_DOORBELL_*` range, mode, ID enable, valid-status, and data fields for four doorbells each.
- RLC residency counters: power, clock, deep-sleep, ultra-low-voltage, PCC, and general counter reset/enable/ack/overflow fields plus event/reference data counters.
- RLC graphics interrupt client status: SE, SDMA, UTCL2, and PMM interrupt masks, clear bits, buffer levels, loading, overflow, and protocol-error latches.
- RLC SPM and microcontroller support: global/SE delay indirect address/data, SPM thread trace interrupt enable, GPU clock counter LSB/MSB, LX6 run/reset/debug controls, XT interrupt vectors, and XT fault/status fields.
- RLC/SMU/IMU firmware communication: safe-mode command/message/response fields, RLCV and SMU command/message registers, SMU response and arguments, IMU bootload address/size/misc/reset-vector fields, RLCS IMU/RLC message mailboxes, telemetry, mutex, RAM access, and doorbell fence fields.
- `gc_rlcsdec` sequencing and power management: CGCG request/status, SOC/GFX deep-sleep masks, GPM power/clock/light-sleep/power-gating status, aborted power-down sequence, DIDT stall, IOV state, soft reset, WGP status, CP/SPM/SDMA interrupt controls, bootload status, power brake controls, GRBM idle/busy latches, general scratch registers, GCR data/status, UTCL2 override controls, PMM CGCG, and graphics memory/power-management controls.
- `gc_pfvfdec_rlc` PF/VF-facing RLC fields: `RLC_SAFE_MODE`, SPM sample/memory-controller configuration, SPM interrupt state, CSIB address/length, CP scheduler bits, EOF/spare/PACE/RLCV spare interrupt fields.
- `gc_pwrdec` graphics clock/power controls: TCC disable masks, CGTT controls for GS/NGG, PA, SC, SQG, TA, DB, CB, CP/CPF/CPC, SQ ALU/TEX/LDS WGP force bits, ICG controls for SP/GCEA/GL1H/GL1C, and MGCG overrides for GL1I/GL1R and CHI/CHR.

## Important APIs, Types, and Functions

This header defines no functions, structs, enums, or persistent variables. Its API is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` is the low bit for a packed field.
- `REGISTER__FIELD_MASK` is the full field mask after shifting.
- Full-register data fields such as `*_DATA_MASK`, `*_CMD_MASK`, `*_ARG_MASK`, and many scratch/general registers use `0xFFFFFFFFL`.
- Reserved fields are named and masked, which lets register-generation tools and driver reviewers see which bits must be preserved or avoided.

The macros are consumed through common AMDGPU register helpers. `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` depends on both the shift and mask names. `REG_GET_FIELD(value, REGISTER, FIELD)` uses the same pair to decode status bits. Raw writes use masks directly where only a bit needs setting; for example `gfx_v11_0_set_safe_mode()` writes `RLC_SAFE_MODE__CMD_MASK` and `1 << RLC_SAFE_MODE__MESSAGE__SHIFT`, then polls `REG_GET_FIELD(..., RLC_SAFE_MODE, CMD)`.

Important direct include consumers for `gc_11_0_0_sh_mask.h` in this tree include `amdgpu/gfx_v11_0.c`, `amdgpu/mes_v11_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, KFD queue/MQD managers, display plane/display code, gfxhub, SDMA, and SOC21 initialization. This chunk also pairs with register-offset macros such as `regRLC_SAFE_MODE`, `regRLC_RLCS_*`, `regCGTT_*`, and `regICG_*`.

## Control Flow

There is no executable control flow in the header. Runtime control flow appears in the consumers that build, write, read, poll, or preserve register values:

- Safe-mode entry/exit writes the `RLC_SAFE_MODE` command/message fields and waits for the command bit to clear. Wrong masks here can make safe-mode handshakes time out or make later register programming race active RLC firmware.
- Firmware and IMU bring-up paths write IMU/RLC RAM, bootload, reset-vector, mailbox, and message-control fields. The `RLC_IMU_*` and `RLC_RLCS_IMU_*` groups define the bit layout for bootload addresses, firmware size, cold-boot and voltage-change exits, request/done/change toggles, RAM request/ack toggles, and telemetry.
- RLC/RLCS power sequencing uses CGCG request/status, deep-sleep allow/busy masks, GPM status, GRBM idle/busy status, WGP status, power brake, and memory-power-control fields. Control flow is usually poll-and-wait: request a transition, read status, and only proceed when busy/changing bits settle.
- Interrupt handling and diagnostic paths use the RLC graphics interrupt client status fields, CP/SPM/SDMA interrupt ack/status/info registers, EOF/spare interrupts, and legacy GPM interrupt disable/status fields. The masks distinguish pending, ack, auto-ack-active, last-client, buffer overflow, and protocol-error state.
- Doorbell control flow programs lower/upper doorbell address ranges, per-doorbell modes, optional doorbell IDs, and valid/status/data latches. These registers are part of firmware/microcontroller command delivery rather than normal user queue doorbells.
- SPP profiling flow enables capture/threshold/state in earlier lines and this chunk provides threshold pairs, PVT histogram counters, CAM/tag access, profile information, stalls, and resets used by profiling/debug code.
- Clock-gating and power-control flow sets or clears soft overrides, stall overrides, on-delay/off-hysteresis controls, force-WGP-on bits, TCC disable masks, and MGCG/ICG override bits. These fields are typically used during ASIC initialization, golden-register setup, power-management transitions, or hardware workarounds.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The hardware state they describe is volatile MMIO state with several persistence scopes:

- Safe-mode, RLCV, SMU, and mailbox registers represent handshakes between the kernel driver, RLC firmware, SMU, IMU, and microcontrollers. Values are transient but can block boot, reset, gfxoff, or power-management transitions if a request/done/ack bit is misencoded.
- Residency event/reference counters and GPU clock counters accumulate hardware activity until reset, overflow, or device reset. Their `RESET`, `ENABLE`, `RESET_ACK`, `ENABLE_ACK`, and `COUNTER_OVERFLOW` bits are part of the measurement protocol.
- SPP CAM, PVT histogram, profiling, global shader ID, and stall/reset fields expose debug/profiling state that can persist until explicit reset bits or profiling disable paths clear it.
- Interrupt status, buffer overflow, protocol error, pending, and changed bits are latched diagnostic state. Some are cleared by writing the matching clear/ack mask; others are sampled by firmware or debug code.
- RLCS general registers and auxiliary registers are scratch or address fields visible to firmware and driver diagnostics. They may survive until overwritten by firmware, reset recovery, or explicit initialization.
- IMU/RLC RAM data/address/control fields represent firmware-accessible memory windows. Their contents and toggles matter across bootload and runtime firmware messaging sequences.
- Clock-gating, deep-sleep, memory light-sleep/deep-sleep, and power-gating override bits affect persistent device operating mode until a later power-management operation or reset changes them.

## Dependencies and Integration Points

This chunk depends on the generated GC 11 register ecosystem: `gc_11_0_0_offset.h` for register addresses, `gc_11_0_0_default.h` for reset/default values, SOC15 register access helpers, firmware binaries for RLC/MES/IMU behavior, and AMDGPU/KFD code that chooses when each field is programmed.

Important integration points include:

- `amdgpu/gfx_v11_0.c` for RLC safe-mode handshakes, graphics initialization, power-management, clock-gating, and reset flows.
- `amdgpu/imu_v11_0.c` for IMU firmware loading and RLC RAM/golden-setting programming that relies on IMU/RLC register fields.
- `amdgpu/mes_v11_0.c` and KFD queue management for compute/MES operation that runs alongside RLC, SPM, interrupt, doorbell, and scheduler state.
- `amdgpu/amdgpu_amdkfd_gfx_v11.c` and KFD MQD/device queue manager code for GC 11 compute setup, debug, and queue lifecycle paths that include RLC-safe operations and status polling.
- Display, gfxhub, SDMA, and SOC21 initialization code, which include this header because GC 11 masks are shared across VM, display plane, SDMA, and SOC-level setup paths.
- Firmware-mediated features: RLC/SMU messages, IMU/RLC message mailboxes, RLCV commands, SRM/GPM commands, power-brake notifications, graphics memory power controls, and IOV status.

Because the field macros are generated, many integration failures are indirect. A bad field may compile cleanly, then surface only as a firmware timeout, unacknowledged interrupt, broken gfxoff/deep-sleep transition, failed IMU bootload, or invalid diagnostic counter.

## Risks

The main risk is silent bitfield drift. Shift and mask constants are plain preprocessor numbers, so incorrect values usually do not cause compile failures if the macro names still exist. A wrong mask can clear reserved bits, fail to set a request bit, sample the wrong status bit, or write a value into an adjacent control field.

High-risk areas in this chunk are:

- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, and `RLC_SMU_SAFE_MODE`, because safe-mode sequencing gates register programming during initialization, reset, and power transitions.
- IMU bootload and IMU/RLC message fields, because incorrect request, done, change, ack, RAM address, bootload size, or reset-vector fields can prevent firmware startup or block IMU/RLC communication.
- RLCS CGCG, deep-sleep, GPM, WGP, GRBM idle/busy, and power-brake fields, because incorrect masks can leave the device stuck in a power transition, falsely report idle, or disable important clock/power gating.
- Interrupt and status groups, because bad ack/clear masks can lose interrupts or leave latched overflow/protocol-error state uncleared.
- Doorbell range/control/status/data groups, because mode, ID enable, and address-range fields control microcontroller-visible doorbell delivery.
- Clock-gating and MGCG/ICG override registers, because forcing or stalling the wrong clock domain can cause hangs, performance regressions, excessive power, or missed workaround behavior.
- Reserved masks, especially in generated control registers, because writing through an imprecise mask may modify undocumented hardware bits.

Manual edits to this file are especially risky. The correct source of truth is the AMD register database/generator that produced the offset, default, and shift/mask headers together. If one header is regenerated without the others, `REG_SET_FIELD` and `REG_GET_FIELD` can address the correct register but encode the wrong field layout.

## Test Signals

Compile-time signals are limited to missing or renamed macros in AMDGPU/KFD/MES/IMU consumers. Successful compilation does not validate numeric masks.

Runtime validation should focus on GC 11 hardware or a hardware-backed test environment. Strong signals include successful GPU probe, RLC and IMU firmware load, safe-mode enter/exit without timeout, MES startup, KFD process and queue creation, suspend/resume, GPU reset recovery, and stable gfxoff/deep-sleep transitions.

Power and clock-gating signals include no regressions in golden-register application, no hangs during CGCG/MGCG/ICG enablement, sane residency counters, expected counter reset/enable acknowledgements, and stable performance/power telemetry. Firmware signals include successful IMU/RLC mailbox exchange, bootload status reaching completion, no stuck request/done/ack toggles, and valid telemetry fields.

Interrupt and diagnostic signals include correct CP/SPM/SDMA interrupt acknowledgement, no unexpected RLC graphics IH buffer overflow or protocol-error latches, sensible GRBM idle/busy and GPM status under workload and idle transitions, and working SPM/thread-trace/profiling paths. Doorbell-specific signals include valid RLCP/XT doorbell status transitions and no firmware command-delivery timeouts.

### subset-b-002519: lines 37568-40147

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 37568-40147

## Scope

This chunk is part of AMDGPU's generated GC 11.0.0 register bitfield header. It contains C preprocessor definitions for hardware register field shifts and masks, not executable functions. The definitions are consumed by the driver through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and indirect-register accessors, together with matching register offsets from the sibling `gc_11_0_0_offset.h` header.

The chunk starts in the middle of the `ICG_GL1C_CLK_CTRL` bitfield group and then covers several address blocks: front-end/interconnect clock-gating controls, `gc_hypdec`, `gc_pspdec`, `gc_gfx_imu_gfx_imudec`, `gc_gfx_imu_gfx_imu_pspdec`, and `gccacind`.

## Purpose

The header gives the GC 11 driver a single source of truth for bit layouts in 32-bit GPU registers. Each register field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position.
- `<REGISTER>__<FIELD>_MASK`, the already-positioned bit mask.

This lets driver code update fields without embedding magic constants, and it keeps ASIC-specific bit encodings separate from higher-level logic in the gfx, KFD, power-management, RLC, PSP, and virtualization paths.

## Important Register Families

- Clock-gating and idle-clock override registers: `ICG_GL1C_CLK_CTRL`, `ICG_GL1A_CTRL`, `ICG_CHA_CTRL`, `GUS_ICG_CTRL`, `CGTT_PH_CLK_CTRL0..3`, `GFX_ICG_GL2C_CTRL`, `GFX_ICG_GL2C_CTRL1`, `ICG_LDS_CLK_CTRL`, `ICG_CHC_CLK_CTRL`, `ICG_CHCG_CLK_CTRL`, `RLC_BUSY_CLK_CNTL`, and `RLC_CLK_CNTL`. These define software override bits, on-delay fields, off-hysteresis fields, and per-subblock clock override bits.
- Hypervisor/virtualization register fields under `gc_hypdec`: `GFX_PIPE_PRIORITY`, `GRBM_GFX_INDEX_SR_SELECT`, `GRBM_GFX_INDEX_SR_DATA`, `GRBM_GFX_CNTL_SR_SELECT`, `GRBM_GFX_CNTL_SR_DATA`, `GRBM_SE_REMAP_CNTL`, `RLC_GPU_IOV_*`, `RLC_HYP_SEMAPHORE_*`, `RLC_RLCV_TIMER_*`, `RLC_PACE_*`, and SDMA status mirrors. These describe VF/PF selection, shader-engine remapping, VM busy state, doorbell status, IOV scheduler state, timer status, and scratch/ucode address-data windows.
- PSP/security-facing register fields under `gc_pspdec`: `CP_MES_DM_INDEX_*`, `CP_MEC_DM_INDEX_*`, `CP_GFX_RS64_DM_INDEX_*`, `CPG_PSP_DEBUG`, `CPC_PSP_DEBUG`, GRBM CAM and hypervisor CAM fields, and `RLC_FWL_FIRST_VIOL_ADDR`. These support firmware/debug access, privilege/TMZ override controls, CAM remapping, and first firewall violation reporting.
- GFX IMU fields under `gc_gfx_imu_gfx_imudec`: 48 `GFX_IMU_C2PMSG_*` mailboxes, mailbox access-control registers, IMU/RLC command and data registers, message-status handshakes, IMU status, interrupt controller mask/level/edge/priority/status bits, interrupt ID, IH controls, power-management interrupt request, telemetry, scratch registers, timestamp/offset registers, clock/reset/isolation controls, three timer blocks, fuse controls, and IMU data RAM access.
- GFX IMU PSP-visible RAM fields under `gc_gfx_imu_gfx_imu_pspdec`: `GFX_IMU_I_RAM_ADDR` and `GFX_IMU_I_RAM_DATA`.
- GC CAC indirect fields under `gccacind`: `GC_CAC_ID`, `GC_CAC_CNTL`, many `GC_CAC_ACC_*` accumulator registers for CP, EA, UTCL2 router/VML2/walker, GDS, GE, PMM, GL2C, PH, SDMA, CHC, GUS, and RLC blocks, plus stall/power-break LUT fields, fixed-pattern performance counters, and `HW_LUT_UPDATE_STATUS`.

## APIs, Types, and Functions

This chunk defines no C types or functions. Its public API is the macro naming contract used by AMDGPU register helpers:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` expands against `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- `REG_GET_FIELD(value, REGISTER, FIELD)` reads using the same pair.
- MMIO helpers such as `WREG32_SOC15(GC, inst, reg, value)` and `RREG32_SOC15(GC, inst, reg)` use offset macros from `gc_11_0_0_offset.h`; these mask macros are the field-level companion.
- Indirect CAC access is mediated through `GC_CAC_IND_INDEX`/`GC_CAC_IND_DATA` style register windows in the broader driver. The `GC_CAC_ACC_*`, LUT, and counter masks in this chunk define the payload layout after the indirect index selects a CAC register.

## Control Flow and State Behavior

There is no local control flow. The runtime flow appears in callers that include this header:

1. Driver code selects a register by using a `reg*`, `mm*`, or `ix*` offset macro from the generated offset header.
2. It reads a 32-bit register value or creates one from zero.
3. It applies these `*_MASK` and `*_SHIFT` macros through field helpers.
4. It writes the updated value to MMIO or to an indirect data window.

The state represented by these macros lives entirely in GPU hardware registers and firmware-visible register windows. Persistent effects depend on the register family:

- Clock-gating override bits affect hardware clock behavior until reset, power-gating transition, firmware reprogramming, or driver reinitialization.
- RLC/GPU IOV fields represent virtualization state, VF/PF doorbell state, scheduler blocks, VM busy state, scratch windows, timer enable/status bits, and microcode access windows.
- GFX IMU registers model firmware mailbox state, command/data handshakes with RLC, interrupt controller configuration, timers, reset and isolation controls, telemetry, scratch registers, and instruction/data RAM access.
- GC CAC accumulator and LUT fields represent power/activity counter state and transition tables accessed through an indirect register interface.

## Dependencies and Integration Points

- Depends on generated offset headers for register addresses. This file only describes bit layouts.
- Integrates with AMDGPU's common bitfield helpers; the macro naming must match the helper token-pasting pattern exactly.
- Integrated by GC 11 code paths such as gfx v11 and KFD support, and by shared SOC15 register read/write helpers for MMIO access.
- The RLC/GPU IOV definitions are integration points with SR-IOV and hypervisor flows; wrong masks can expose or hide VF/PF state incorrectly.
- PSP/security and CAM definitions integrate with firmware debug, protected register access, TMZ/secure overrides, and firewall violation reporting.
- GFX IMU mailbox, interrupt, timer, reset, and RAM definitions integrate with firmware boot, power management, RLC coordination, interrupt routing, and telemetry.
- GC CAC definitions integrate with power-management/CAC activity accounting and indirect register access through index/data windows.

## Risks

- Mask/shift drift from the hardware specification is high impact. A one-bit error can program an adjacent control bit, especially in clock, reset, isolation, security, or virtualization registers.
- Some fields are full-register masks (`0xFFFFFFFFL`) and must not be treated as bounded small fields by callers.
- Reserved fields are explicitly defined in several registers. Callers should preserve reserved bits on read-modify-write unless the hardware spec requires a literal value.
- `GFX_IMU_PIC_INT_*` definitions contain many single-bit interrupt fields. Mismapping an interrupt mask, level, edge, priority, or status bit can cause missing interrupts or interrupt storms.
- Mailbox/status registers use handshake bits such as busy, done, change-toggle, and done-toggle. Callers must preserve protocol ordering; these macros do not enforce sequencing.
- RLC and IMU RAM address fields are shifted and masked address windows, not arbitrary byte pointers. Unaligned or out-of-range programming can target the wrong firmware memory word.
- GC CAC LUT fields pack several small pattern entries into one register. Incorrect packing can destabilize stall/release or power-break behavior.
- The file is generated; manual edits risk diverging from upstream generated register headers and should be avoided unless regenerating from the authoritative register database.

## Test and Validation Signals

- Build signal: any renamed or missing macro should fail compilation in code using `REG_SET_FIELD`/`REG_GET_FIELD` with GC 11 registers.
- Static review signal: field helper expansion should reference both `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT`; register groups should remain paired with matching offset-header entries.
- Runtime smoke signal: GC 11 ASIC initialization should complete without hangs in gfx/RLC/PSP/IMU setup paths.
- Power-management signal: clock-gating toggles, RLC busy-clock controls, CAC activity counters, and fixed-pattern counters should behave consistently across suspend/resume and runtime power transitions.
- Virtualization signal: SR-IOV paths should correctly report VF/PF enablement, VM busy status, SDMA busy/status mirrors, doorbell set/clear state, and scheduler block state.
- Firmware/IMU signal: mailbox commands should complete without stuck busy bits, IMU/RLC status should progress through expected alive/done states, interrupt status should clear, and timer compare interrupts should fire only when enabled.
- Security/debug signal: PSP debug override and firewall violation fields should only be used in intended privilege contexts, with readback matching expected bit positions.

### subset-b-002520: lines 40148-41664

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 40148-41664

## Scope

This chunk is the tail of a generated AMD GC 11.0.0 shift/mask register header. It contains only C preprocessor constants for register bit positions and masks, plus generated register/address-block comments. There are no functions, structs, enums, global variables, allocations, locks, loops, branches, or direct MMIO operations in this range.

The requested lines contain 1,251 `#define` statements: 618 `__SHIFT` macros and 633 `_MASK` macros. The chunk starts in the middle of the `HW_LUT_UPDATE_STATUS` register, covers the full `secacind` and `grtavfsind` address blocks visible here, enters the `sqind` address block, and ends at the header guard `#endif` after `SQ_WAVE_EXEC_HI`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata. It is unrelated to Ceph filesystem protocol, persistence, or distributed-storage behavior.

## Purpose

`gc_11_0_0_sh_mask.h` describes the bit layout of AMD Graphics Core 11.0.0 registers. Driver code combines these macros with matching register offsets from `gc_11_0_0_offset.h` and AMDGPU helper macros to construct, update, and decode 32-bit hardware register values without open-coded bit positions.

This chunk covers three broad hardware surfaces:

- Hardware LUT update status and shader-engine CAC selection/threshold fields.
- RTAVFS controls and status for adaptive voltage/frequency scaling, CPO/ripple-counter measurement, voltage-code PI control, power-state-monitor measurement, FSM timing, debug stops, retention save/restore, and override/readback paths.
- SQ indexed debug and wave-state registers used to inspect wave activity, wave execution mode/status, trap status, register/LDS allocation, instruction-buffer counters, program counter, scratch state, hardware identity, scheduling mode, temporary trap registers, M0, and EXEC masks.

## Important APIs, Types, And Macros

The generated macro namespace is the only interface:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- `// addressBlock: ...` comments mark generated register address spaces.
- `//<REGISTER>` comments mark generated register groups.

There are no callable APIs or C types here. Runtime users normally reach these constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indexed-register access helpers, and generation-specific GFX/KFD/power-management code that includes this header with the matching offset header.

Important register families in this chunk include:

- `HW_LUT_UPDATE_STATUS` fields for table 1 through table 5 completion, error, and error-step reporting. The chunk begins after the matching shift macros, so only masks are visible here.
- `SE_CAC_ID` and `SE_CAC_CNTL` in `secacind`, selecting CAC block/signal IDs and a 16-bit CAC threshold.
- `RTAVFS_REG0..4` zone start/stop counters for five AVFS zones, followed by `RTAVFS_REG5..14` zone enable bitmaps.
- `RTAVFS_REG15..18` voltage/frequency points, each splitting a frequency count and voltage code into 16-bit fields.
- `RTAVFS_REG19..24` guard-band and per-zone CPO average-divider controls, including final divider fields and reserved high bits.
- `RTAVFS_REG25..30` reserved and zone intercept registers.
- `RTAVFS_REG31..42` CPO clock divider and FSM timing counters for startup, idle, CPO reset/start/stop, ripple-counter start/done, final-result readiness, voltage-code readiness, target-voltage readiness, and wait-for-ack.
- `RTAVFS_REG43..48` PI-controller tuning: lookup-table `KP/KI` nibbles, binary-search and hardware-calibration selection, voltage-regulator enable/bleed/override controls, anti-windup, PI shift/error controls, PI min/max voltage-code bounds, loop iteration count, and error threshold.
- `RTAVFS_REG49..53` PSM controls and readbacks for VDD and VREG min/max and average measurement paths.
- `RTAVFS_REG54..117` CPO0 through CPO63 start/stop counters.
- `RTAVFS_REG118..120` CPO enable bitmaps and CPO average-divider controls.
- `RTAVFS_REG121` AVFS zone-in-use bits and a high-nibble error code.
- `RTAVFS_REG122..185` CPO0 through CPO63 ripple-count readbacks.
- `RTAVFS_REG186..187` target/current frequency-count overrides and override-select bits.
- `RTAVFS_REG188..194` reserved bits, PI/binary-search voltage-code readback, regulator status, RLC request ignore, ripple-counter output select, run-loop control, CPO weight save/restore, retention reset, FSM debug stop points, scaled/final CPO counts, FSM state, and full-width ripple-count read.
- `SQ_DEBUG_STS_LOCAL` and `SQ_DEBUG_CTRL_LOCAL` for SQ local busy state, wave level, sub-block busy flags, and a small debug-control payload.
- `SQ_WAVE_ACTIVE` and `SQ_WAVE_VALID_AND_IDLE` wave-slot bitmaps.
- `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, and `SQ_WAVE_TRAPSTS`, which expose wave floating-point mode, exception enables, trap-after-instruction behavior, wave end, FP16 overflow, performance disable, scalar condition code, priority, privilege, trap/thread-trace flags, export/exec/VCC zero state, barrier/thread-group state, halt/trap/valid/ECC/fatal/idle/scratch state, exception vectors, save-context, illegal instruction, out-of-bounds buffer, host trap, wave start/end, performance snapshot, and UTC error fields.
- `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, and `SQ_WAVE_IB_STS` for VGPR allocation, LDS/shared-VGPR allocation, and outstanding export/LGKM/VM/VS counters.
- `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_IB_DBG1`, `SQ_WAVE_FLUSH_IB`, `SQ_WAVE_FLAT_SCRATCH_LO/HI`, `SQ_WAVE_HW_ID1/2`, `SQ_WAVE_POPS_PACKER`, `SQ_WAVE_SCHED_MODE`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_SHADER_CYCLES`, `SQ_WAVE_TTMP0/1/3..15`, `SQ_WAVE_M0`, and `SQ_WAVE_EXEC_LO/HI`.

## Control Flow

This header has no runtime control flow. It influences behavior only when compiled C code expands these constants while preparing or decoding register values.

The implied driver flow is:

1. A GC 11.0.0 consumer selects a register offset from the matching offset header.
2. It reads, writes, or read-modify-writes the register through SOC15/MMIO or indexed-register helpers.
3. It uses the `__SHIFT` and `_MASK` pair, often via `REG_SET_FIELD` or `REG_GET_FIELD`, to isolate or compose the target field.
4. GPU hardware, firmware, RLC/SMU/power-management logic, or SQ debug machinery performs the actual operation.

For RTAVFS, higher-level control paths configure zones, CPO enable masks, divider values, voltage/frequency points, PI-loop parameters, PSM measurement paths, overrides, and run/debug controls. Hardware state machines then update in-use/error/status fields and CPO/ripple-count readbacks. This header does not encode sequencing rules, stabilization delays, RLC ownership, SMU coordination, or register side effects.

For SQ wave inspection, debug code selects indexed SQ state and reads wave activity, mode/status/trap state, allocation counters, PC, scratch pointers, hardware IDs, temporary trap registers, M0, and EXEC masks. This chunk defines the decode layout but not how waves are selected, halted, flushed, resumed, or synchronized with traps and thread tracing.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent or volatile state exists only in GPU registers, indexed SQ state, firmware-managed control state, and hardware latches/counters.

RTAVFS-related hardware state includes zone start/stop counters, zone enable masks, voltage/frequency points, guard bands, CPO average dividers, FSM timing counters, PI coefficients and bounds, regulator/override enables, PSM measurement state, CPO start/stop windows, CPO enable bitmaps, ripple-count readbacks, error codes, target/current frequency overrides, control bits for running the loop and saving/restoring CPO weights, retention reset, debug stop points, FSM state, and final/scaled CPO count outputs. Some fields are configuration values, some are live status bits, and some are hardware-updated counters or readbacks.

SQ-related hardware state includes local busy indicators, active/idle wave-slot masks, per-wave mode/status/trap state, VGPR/LDS allocation, outstanding instruction-buffer counters, PC, flat scratch address, wave hardware identity, scheduling and POPS state, shader-cycle count, TTMP scratch registers, M0, and EXEC masks. These values are per-wave or per-SQ debug state and can change while shader execution is active.

This generated header does not identify reset values, write-one-to-clear fields, clear-on-read behavior, read-only versus writeable fields, locking requirements, power-gating persistence, or firmware ownership. Consumers must preserve reserved bits during read-modify-write unless hardware documentation or existing AMDGPU sequences explicitly say otherwise.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.0.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h` supplies matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h` supplies generated defaults where available.
- AMDGPU helper macros and SOC15 indexed/MMIO accessors provide the actual bitfield and register operations.
- GFX 11, KFD, RLC, debug, power-management, and SMU-adjacent code are the likely runtime consumers for these register layouts.
- Neighboring GC generation headers expose similar families, but field widths and positions are generation-specific and should not be assumed interchangeable.

Important integration surfaces are GPU power/voltage management, AVFS tuning and diagnostics, CPO/ripple-counter calibration, RLC/firmware interactions around AVFS ownership, GPU hang/debug tooling, wave trap handling, shader debugger support, thread tracing, register-dump decoding, and postmortem analysis of wave allocation/status.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong mask or shift can compile cleanly while reading or programming the wrong hardware bit.
- The chunk starts mid-register: `HW_LUT_UPDATE_STATUS` shift definitions and earlier table-zero context are in a previous chunk.
- RTAVFS has many repeated register families. Off-by-one mistakes across `RTAVFS_REG54..117` CPO start/stop counters or `RTAVFS_REG122..185` ripple counters would target the wrong CPO instance while looking mechanically valid.
- Several RTAVFS fields are control-sensitive: voltage overrides, regulator enables, low-power mode, PI disable/anti-windup, binary-search selection, run-loop, RLC request ignore, CPO weight save/restore, and retention reset. Misuse can destabilize clocks/voltage or break power-management handoff.
- Reserved masks are frequent. Full-register writes that do not preserve reserved fields can corrupt undocumented hardware state.
- Status/readback fields may be sampled while hardware is changing. Debug and diagnostics should account for transient in-use, busy, FSM, ripple-count, and wave-status values.
- SQ wave fields are highly execution-sensitive. Reading active wave status without proper halt/selection/synchronization can produce inconsistent PC, EXEC, trap, allocation, and counter values.
- Wave trap and exception fields overlap debugger, KFD, user-mode queue, thread-trace, and fault-reporting behavior. Incorrect decoding can misattribute illegal instructions, buffer out-of-bounds events, host traps, save-context events, UTC errors, or fatal halt conditions.
- `SQ_WAVE_TTMP2` is absent from the visible TTMP sequence, so consumers must not assume contiguous macros exist for every TTMP index in this chunk.
- The file ends at `#endif`; later chunk merging should treat this as the terminal chunk for this header, not a partial continuation.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware-level integration:

- Build AMDGPU/KFD configurations that include GC 11.0.0 support. Missing or malformed macros should surface as compile failures in GFX 11, KFD, debug, or power-management code.
- Compare every visible shift and mask against AMD's authoritative GC 11.0.0 register database.
- Cross-check that visible register groups have matching entries in `gc_11_0_0_offset.h` and, where applicable, `gc_11_0_0_default.h`.
- Run mechanical mask checks: masks should align with shifts, full-width data/readback fields should use `0xFFFFFFFFL`, 16-bit paired counters should split at bit 16, repeated CPO/ripple families should be structurally consistent, and reserved fields should not overlap named fields.
- Exercise AVFS/power-management flows on affected hardware: clock/voltage changes, low-power transitions, SMU/RLC handoff, CPO calibration, ripple-counter reads, override paths, retention save/restore, and debug stop/run-loop behavior.
- Inspect runtime logs and register dumps for `RTAVFS_REG121` error codes, FSM state, zone-in-use bits, target/current frequency override behavior, PSM min/max/average readbacks, and CPO/ripple counter plausibility.
- Exercise shader debugging and hang-diagnosis paths that read SQ wave active/idle masks, mode/status/trap state, allocation, PC, scratch, hardware ID, TTMP, M0, and EXEC registers.
- Validate trap and exception reporting with workloads that trigger illegal instruction, buffer out-of-bounds, host trap, save-context, performance snapshot, wave start/end, and UTC error paths where supported.
- Decode known-good GC 11.0.0 register dumps using these masks and compare against reference tools, especially for RTAVFS repeated arrays and SQ wave state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002520`. The final per-file research should merge it with neighboring chunks for complete `gc_11_0_0_sh_mask.h` coverage. The previous chunk owns the beginning of `HW_LUT_UPDATE_STATUS`; this chunk owns the terminal `secacind`, `grtavfsind`, and `sqind` tail through the header guard.
