# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002586`: lines 1-2452, `Docs/researches/chunks/subset-b-002586_research.md`
- `subset-b-002587`: lines 2453-4938, `Docs/researches/chunks/subset-b-002587_research.md`
- `subset-b-002588`: lines 4939-7413, `Docs/researches/chunks/subset-b-002588_research.md`
- `subset-b-002589`: lines 7414-9893, `Docs/researches/chunks/subset-b-002589_research.md`
- `subset-b-002590`: lines 9894-12404, `Docs/researches/chunks/subset-b-002590_research.md`
- `subset-b-002591`: lines 12405-12418, `Docs/researches/chunks/subset-b-002591_research.md`

## Chunk Research

### subset-b-002586: lines 1-2452

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 1-2452

## Scope

This chunk covers the opening section of the generated GC 12.1.0 register offset header. It starts with the AMD MIT-style license and include guard, then defines SDMA-related register address macros for:

- `SDMA0` public/control decode block `CHIP_XCD_gfxip_xcc_gfx_cpwd_sdma_sdmadec`, base address `0x4980`.
- `SDMA0` hypervisor decode block `sdmahypdec`, base address `0x3e200`.
- `SDMA0` PSP, performance-select, performance-data, and power decode blocks.
- The beginning of `SDMA1` public/control decode block `sdmadec:1`, base address `0x6180`.

The range contains 2,399 `#define reg...` lines: 1,268 for `regSDMA0...` and 1,131 for `regSDMA1...`. Each real register offset is paired with a `<register>_BASE_IDX` macro. Lines 1-2452 end in the middle of the `regSDMA1_SDMA_QUEUE9_MIDCMD_DATA*` family; the next chunk continues that queue block.

## Purpose

This header is a hardware register ABI map for AMD GC 12.1.0 SDMA engines. It supplies register offsets, not field encodings. Driver code combines these offsets with:

- `gc/gc_12_1_0_sh_mask.h` for field shifts and masks.
- SOC15 access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, `SOC15_REG_ENTRY_STR`, and `REG_SET_FIELD`.
- Per-instance offset logic in SDMA, KFD, and debug paths.

The values are offsets in the generated AMD register namespace. The `_BASE_IDX` macro chooses the register aperture/base table index used by SOC15 accessors: most SDMA0/SDMA1 public queue/control registers in this chunk use base index `0`, while hypervisor, PSP, performance, and power sub-blocks use base index `1`.

## Important Macro Families

The first SDMA0 public block begins at line 28. It defines global SDMA engine registers including decode start, microcode revision, global timestamp, power/control/chicken/cache controls, status registers, watchdog, queue status, SDMA ID/version, atomic controls, DCC, UTCL1 controls and status, freeze controls, error logs, dummy registers, RLC clock-gating control, IOV violation logs, interrupt status, invalid address reporting, scratch RAM access, queue reset/dequeue requests, CE control, RAS/poison status, and MEMHUB control.

The largest part of the chunk is the repeated SDMA queue register layout. For `SDMA0`, queues 0 through 9 are fully present. Each queue has a regular stride: `regSDMA0_SDMA_QUEUE1_RB_CNTL - regSDMA0_SDMA_QUEUE0_RB_CNTL == 0x3c`. The per-queue family includes:

- Ring buffer control/base/read pointer/write pointer registers: `RB_CNTL`, `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`.
- Read-pointer writeback address registers: `RB_RPTR_ADDR_LO/HI`.
- Indirect buffer state: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, `IB_SIZE`, and `IB_SUB_REMAIN`.
- Doorbell state: `DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`.
- Context save area and scheduling/preemption state: `CSA_ADDR_LO/HI`, `SCHEDULE_CNTL`, `PREEMPT`, `CONTEXT_SWITCH_STATUS`, and `CONTEXT_STATUS`.
- Write-pointer polling and AQL controls: `RB_WPTR_POLL_ADDR_LO/HI`, `RB_AQL_CNTL`, and `MINOR_PTR_UPDATE`.
- Mid-command resume state: `MIDCMD_CNTL` and `MIDCMD_DATA0` through `MIDCMD_DATA10`.
- Utilization and wait-threshold registers, MQD base/control registers, and dummy registers.

After the SDMA0 public queue block, the hypervisor decode section provides VM and virtualization-facing SDMA0 registers: `SDMA_VM_CTX_LO/HI`, `SDMA_ACTIVE_FCN_ID`, `SDMA_VM_CTX_CNTL`, `SDMA_VIRT_RESET_REQ`, context/public register type maps, `SDMA_VM_CNTL`, `SDMA_MCU_CNTL`, and instruction-cache base/control registers. These are the privileged engine-control offsets used when the PF/hypervisor side needs to manage SDMA context, virtual reset, register exposure, or SDMA MCU state.

The PSP decode section in this range has `regSDMA0_SDMA_MCU_DM_FROM_RST_ADDR_OFFSET`. The performance select/data blocks define selector/configuration and result registers for six SDMA performance counters, including `SDMA_PERFCNT_PERFCOUNTER*_CFG`, `SDMA_PERFCOUNTER*_SELECT`, `SDMA_PERFCOUNTER*_SELECT1`, and `SDMA_PERFCOUNTER*_LO/HI`. The power decode section contains `regSDMA0_GFX_ICG_SDMA_CTRL`.

The SDMA1 public block mirrors SDMA0 with an offset delta of `0x600` for the public `BASE_IDX 0` region. For example, `regSDMA0_SDMA_CNTL` is `0x000d`, while `regSDMA1_SDMA_CNTL` is `0x060d`; `regSDMA0_SDMA_QUEUE0_RB_CNTL` is `0x0200`, while `regSDMA1_SDMA_QUEUE0_RB_CNTL` is `0x0800`. Within this chunk, SDMA1 global public registers and queues 0 through most of queue 9 are present, ending at `regSDMA1_SDMA_QUEUE9_MIDCMD_DATA3`.

## APIs, Types, and Functions

This file defines no C types, functions, variables, or inline helpers. Its public API is the generated macro namespace:

- `regSDMA0_*` and `regSDMA1_*` register-offset constants.
- Matching `regSDMA0_*_BASE_IDX` and `regSDMA1_*_BASE_IDX` base-index constants.

The API contract is compile-time name stability and numeric accuracy. Higher-level code assumes these macros can be used directly in SOC15 register helpers and in arithmetic that depends on register layout regularity.

## Control Flow and State Behavior

There is no executable control flow in this header. Runtime behavior appears only in consumers that use these constants to read or write MMIO registers.

The hardware state described by this chunk is substantial. It includes SDMA firmware/control state, queue ring base and pointer state, indirect-buffer state, doorbell routing, context-save addresses, scheduling/preemption state, mid-command replay state, MQD state, utilization counters, VM context state, virtual reset state, performance counter setup/results, interrupt/status/error reporting, UTCL1 translation/cache state, RAS and poison status, and power/clock-gating state.

Several covered registers represent persistent engine or queue configuration until reset or reprogramming, such as ring base addresses, doorbell offsets, VM context, MQD base, performance counter select registers, and watchdog settings. Others are volatile status/counter registers, such as timestamp, queue status, UTCL1 read/write status, error logs, utilization registers, performance counter result registers, RAS status, and poison info. Some are command-like control points where write sequencing matters, such as queue reset/dequeue request, virtual reset request, freeze trigger, minor pointer update, preempt, and MCU control.

## Dependencies and Integration Points

Observed includes of this header in the source tree include `amdgpu/sdma_v7_1.c`, `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/gfxhub_v12_1.c`, `amdgpu/imu_v12_1.c`, `amdgpu/mes_v12_1.c`, `amdgpu/soc_v1_0.c`, and `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`. These files include the companion `gc_12_1_0_sh_mask.h` when they need field-level composition.

`amdgpu/sdma_v7_1.c` is the clearest consumer. It includes this header, defines `SDMA1_REG_OFFSET 0x600`, and builds an SDMA register dump list with `SOC15_REG_ENTRY_STR(GC, 0, regSDMA0_...)`. The SDMA v7.1 resume/stop paths read and write `regSDMA0_SDMA_QUEUE0_RB_CNTL`, `IB_CNTL`, pointer registers, polling-address registers, doorbell registers, `MINOR_PTR_UPDATE`, `WATCHDOG_CNTL`, `UTCL1_CNTL`, `UTCL1_PAGE`, and `MCU_CNTL` through `sdma_v7_1_get_reg_offset()`.

`amdgpu/sdma_v7_1.c` also initializes SDMA MQD images using the same register family: it composes `sdmax_rlcx_rb_cntl`, ring base, polling address, read-pointer writeback address, IB control, doorbell offset, doorbell enable, AQL control, dummy register, and CSA address fields. That MQD data later becomes firmware-visible queue state rather than direct MMIO writes.

`amdgpu/amdgpu_amdkfd_gfx_v12_1.c` depends on regular register spacing. Its `get_sdma_rlc_reg_offset()` computes the SDMA engine base with `SOC15_REG_OFFSET(..., regSDMA0_SDMA_QUEUE0_RB_CNTL)` or `regSDMA1_SDMA_QUEUE0_RB_CNTL`, then computes an RLC queue offset with `queue_id * (regSDMA0_SDMA_QUEUE1_RB_CNTL - regSDMA0_SDMA_QUEUE0_RB_CNTL)`. Its SDMA HQD dump code assumes a contiguous dump range from `regSDMA0_SDMA_QUEUE0_RB_CNTL` to `regSDMA0_SDMA_QUEUE0_CONTEXT_STATUS`.

`amdkfd/kfd_mqd_manager_v12_1.c` uses the sibling shift/mask definitions for fields in registers whose offsets are defined here. Its SDMA MQD update path programs queue size, VMID, read-pointer writeback enable/timer, MCU write-pointer polling, queue base, rptr/wptr backing addresses, doorbell offset, and schedule quantum. This ties the generated offset namespace to KFD compute queue creation and update.

## Risks

- Numeric drift in any `regSDMA*_...` value can route MMIO reads/writes to the wrong hardware register. The likely results include engine hangs, broken queue submission, lost doorbells, invalid context save/restore, bad performance data, or failed reset/recovery.
- The repeated queue layout invites arithmetic dependencies. Consumers assume queue stride `0x3c` and SDMA1 public offset delta `0x600`; changing one queue macro without preserving the pattern would break KFD queue dumps and RLC queue offset calculation.
- Base-index drift is subtle. A correct offset with the wrong `_BASE_IDX` can use the wrong SOC15 aperture, especially around the split between public `BASE_IDX 0` registers and hypervisor/performance/power `BASE_IDX 1` registers.
- The chunk ends mid-family at `regSDMA1_SDMA_QUEUE9_MIDCMD_DATA3`. Any final merged per-file report must connect this chunk with the following chunk before making complete claims about SDMA1 queue9 or later SDMA1 hypervisor/performance blocks.
- Queue pointer and doorbell registers have strict sequencing requirements in consumers. For example, SDMA v7.1 sets `MINOR_PTR_UPDATE` before reducing write pointers and toggles doorbell enable/offset based on ring mode. The offsets alone do not encode these ordering constraints.
- Virtualization-related registers such as VM context, active function ID, virtual reset request, public/context register-type maps, and MCU controls are privilege-sensitive. Misuse can affect PF/VF isolation or leave SDMA state inconsistent across reset paths.
- Performance counter selector/result offsets must match the companion masks. A mismatch between `gc_12_1_0_offset.h` and `gc_12_1_0_sh_mask.h` can silently program one counter while decoding another.

## Test and Validation Signals

Useful validation is mostly compile, bring-up, and hardware integration coverage:

- Build AMDGPU and KFD paths that include `gc/gc_12_1_0_offset.h`; this catches missing or renamed macros used by SDMA v7.1, GFX 12.1, MES, GFXHUB, IMU, SOC, and KFD code.
- Exercise SDMA v7.1 ring bring-up and shutdown. The path should disable/enable `RB_CNTL` and `IB_CNTL`, program RB/IB base and pointer registers, configure read-pointer writeback and write-pointer polling, set `MINOR_PTR_UPDATE`, program doorbells, and unhalt `MCU_CNTL`.
- Run KFD SDMA queue creation/update and SDMA HQD dump tests. These validate that queue stride and SDMA0/SDMA1 engine offset arithmetic still match the generated register layout.
- Validate bare-metal and SR-IOV VF behavior. SDMA v7.1 uses different write-pointer/doorbell behavior for VF mode, and the hypervisor decode offsets in this chunk are part of virtualized SDMA management.
- Check SDMA reset, preemption, watchdog, UTCL1, and error-reporting paths through GPU reset/recovery and memory fault tests.
- Use performance/debug tests that select and read SDMA performance counters to ensure the selector/result offsets in this header match the companion field definitions.

### subset-b-002587: lines 2453-4938

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 2453-4938

## Scope

This chunk is a generated AMD GC 12.1.0 register-offset header segment. It contains C preprocessor register-address macros and matching `_BASE_IDX` macros only; there are no functions, structs, enums, storage objects, locks, allocation paths, or executable branches in this range. Although the repository path is under a `ceph-client` source mirror, the content is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP.

The selected range starts at the tail of `SDMA1_SDMA_QUEUE9` state, then covers SDMA1 virtualization, PSP/reset handoff, performance, and power-control register addresses. It continues through GRBM global graphics management, command-processor public debug/status registers, PA/VGT and shader compute-dispatch registers, GC CAC/EDC power-throttle controls, GC-EA/SDP arbitration and error controls, GCR controls, CP graphics-ring and queue state, HQD queue descriptors, GFXDEC0 graphics context controls, PF/VF and PF-only virtualization windows, GFXU EOP/statistics/scratch/indirect-buffer registers, and ends in the CP RS64/MES/MEC register block at `regCP_CPC_IC_OP_CNTL`.

## Purpose

`gc_12_1_0_offset.h` maps symbolic GC 12.1.0 register names to numeric register offsets used by AMDGPU code. These addresses pair with field definitions in `gc_12_1_0_sh_mask.h`; callers use the offset macro to select the register and the shift/mask header to pack or extract individual fields. The `_BASE_IDX` companion macros select the register aperture/base bank used by AMD register access helpers.

This chunk provides offsets for several high-risk driver surfaces:

- SDMA1 queue 9 metadata: mid-command data words, utilization counters, wait threshold, MQD base/control, context status, and dummy registers.
- SDMA1 privileged blocks: VM context, active function ID, virtual reset, context/public register type maps, instruction-cache base/control, PSP reset-data offset, six performance-counter selectors/results, and clock-gating control.
- GRBM and CP global management: busy/stall/status registers, soft reset, clock/power controls, trap/read/write/IOV error reporting, scratch registers, queue FIFO availability, command-index/data windows, ring read/write pointers, privilege-violation addresses, and debug data ports.
- PA/VGT/GE/WD front-end status and UTCL1 controls, including DMA FIFO depths, pipe control, shader-array unit disables, and reset debug.
- Shader/compute context registers: dispatch dimensions, start/restart coordinates, thread counts, program address/resource registers, VMID/resource limits, temporary ring size, thread trace, dispatch IDs, DDID/checksum/interleave, per-SE destination/static-thread controls, 32 compute user-data registers, relaunch/wave-restore addresses, dispatch tunnel/end, and preallocated CR/DB buffer size.
- GC CAC/EDC/DIDT/PCC/PWRBRK power instrumentation: aggregate power counters, thresholds, stretch/throttle controls, stall patterns, hysteresis, weighted-data multipliers, soft controls, and per-block activity weights.
- GC-EA CPWD/SDP arbitration, credit reservation, backdoor credit/data controls, invalid-opcode and poison/parity error injection/logging, plus SDP enable.
- CP ring, queue, HQD, MQD, doorbell, VMID, suspend/resume, DDID, HPD, watchpoint, DMA, EOP, IB, statistics, and interrupt/fence registers.
- Virtualization-specific PF/VF and PF-only windows, including unmapped queue registers, GRBM GFX selector, CP DFY debug/fetcher controls, HPD status/ROQ offsets, GCR target controls, and PF-only CAC/EDC controls.
- RS64 CP firmware register addresses for RLC, MES, and MEC microcontroller paths: machine trap vectors, interrupt enables/pending/status, program counters, GP registers, local instruction/scratch apertures, and interrupt data registers.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. The interface is the generated macro contract:

- `reg<NAME>` expands to the GC 12.1.0 register offset for `NAME`.
- `reg<NAME>_BASE_IDX` selects the register base index. In this chunk, index `0` is used for many CPWD/public blocks and index `1` for SDMA privileged/perf blocks, PF/VF or PF-only apertures, GFXU, CAC/EDC, and RS64 ranges.
- Companion field-level constants are expected in `gc_12_1_0_sh_mask.h`.
- AMDGPU register helpers and packet emitters use these symbols for MMIO reads/writes, indirect register access, PM4 command construction, queue setup, debug dumps, suspend/resume, reset, and virtualization paths.

Prominent macro families include `regSDMA1_SDMA_*`, `regGRBM_*`, `regCP_*`, `regCPC_*`, `regCPF_*`, `regCPG_*`, `regVGT_*`, `regGE_*`, `regWD_*`, `regIA_*`, `regCOMPUTE_*`, `regGC_CAC_*`, `regGC_EDC_*`, `regEDC_*`, `regDIDT_*`, `regPCC_*`, `regPWRBRK_*`, `regGC_EA_CPWD_*`, `regGCR_*`, `regRLC_*`, `regSCRATCH_REG*`, and RS64-specific `regCP_RLC_*`, `regCP_MES_*`, and `regCP_MEC_*`.

The chunk also contains intentional aliases where multiple symbolic names share one offset, such as `regCP_RB0_RPTR`/`regCP_RB_RPTR`, `regCOMPUTE_RELAUNCH`/`regCOMPUTE_RELAUNCH_STATE_PAYLOAD`, `regCOMPUTE_STATIC_THREAD_MGMT_SE*`/`regCOMPUTE_DESTINATION_EN_SE*`, `regCP_DDID_*`/`regCPC_DDID_*`, `regCP_HQD_DMA_OFFLOAD`/`regCP_HQD_OFFLOAD`, `regCP_HQD_HQ_SCHEDULER*`/`regCP_HQD_HQ_STATUS*` or `CONTROL*`, and low/high aliases for append, atomic, ring, and MQD registers. These aliases are part of the generated hardware naming surface and should not be deduplicated without checking call-site semantics.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied driver flow is:

1. Select GC 12.1.0 ASIC support and include this offset header.
2. Choose a symbolic `reg...` offset for the relevant engine or block.
3. Use the matching `_BASE_IDX` and AMDGPU register-access helper to address the correct MMIO or indirect aperture.
4. Optionally combine the offset with field masks from `gc_12_1_0_sh_mask.h`.
5. Read status/debug registers, write control/configuration registers, emit PM4 packets, initialize queues, program compute dispatch state, collect counters, or perform reset/preemption/virtualization operations.

Runtime sequencing is defined outside this generated header. For example, queue setup must program MQD/ring/doorbell/pointer registers in the order required by CP or SDMA hardware; reset and preemption paths must coordinate status polling and quiescence; performance-counter paths must select/configure counters before reading low/high result registers; EOP and fence programming must compose address/data pairs correctly; and RS64 microcontroller registers require firmware-aware sequencing.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They name hardware registers whose state is owned by the GPU, firmware, and AMDGPU runtime.

Several groups represent persistent or semi-persistent GPU context state:

- SDMA queue and CP/HQD/MQD registers hold queue descriptors, base addresses, read/write pointers, VMIDs, priorities, quantum, dequeue state, doorbell controls, EOP buffers, IB pointers, and context-save locations. These values survive for the lifetime of a queue and are rebuilt during queue creation, suspend/resume, reset recovery, and preemption.
- `COMPUTE_*` registers represent compute dispatch and shader ABI state: program addresses, resource limits, user data, dispatch dimensions, restart coordinates, scratch bases, thread management, and relaunch/wave-restore metadata.
- GRBM, CP, PA/VGT, GCR, GC-EA, and CAC/EDC controls are global block configuration or status. Some are passive readback points; others have side effects such as soft reset, invalidation, error injection, throttle control, or command/debug-data access.
- Counter and statistics pairs such as SDMA perf counters, CAC/EDC power deltas, CP pipe statistics, shader invocation counters, primitive counters, and EOP/fence registers are live hardware state. Low/high pairs must be read and interpreted using the hardware's latching rules, not as ordinary independent variables.
- PF/VF and PF-only blocks expose virtualization-sensitive state. Unmapped queues, doorbells, privilege violations, active function IDs, IOV error FIFOs, virtual reset requests, and PF-only debug/configuration registers can affect or reveal multi-function GPU state.

Because this is an offset header, it cannot describe volatility, read-to-clear behavior, write-one-to-clear bits, alignment requirements, or register ordering constraints. Call sites must apply the hardware programming guide and surrounding AMDGPU helper contracts.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register family remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h` supplies field shifts and masks for these register names.
- Other AMDGPU GC 12.1.0 generated headers and firmware interfaces provide defaults, packet definitions, and engine-specific programming sequences.
- AMDGPU MMIO, indirect-register, and PM4 helper layers consume the `reg...` and `_BASE_IDX` symbols.

Likely integration points include SDMA ring/MQD setup, CP graphics and compute queue initialization, KFD/MES queue scheduling, GPU reset and preemption, suspend/resume context save, command submission, EOP fence signaling, doorbell programming, VMID assignment and reset, performance counter collection, debugfs/register dumps, RAS/ECC or error-injection diagnostics, virtualization/PF-VF isolation, power throttling and clock/power management, GCR/cache controls, and hang diagnosis through busy/stall/status registers.

## Risks And Edge Cases

- Generated-offset drift is the primary risk. A wrong numeric offset or `_BASE_IDX` compiles cleanly but can read or write the wrong hardware register.
- This chunk begins and ends mid-family. It starts after earlier SDMA1 queue 9 definitions and ends at the first `CP_CPC_IC_OP_CNTL` line after the MEC RS64 block; adjacent chunks are required for complete per-file conclusions.
- Aliased register names share offsets intentionally. Naive duplicate-removal or mechanical renaming can break call sites that depend on semantic names for different engines, phases, or access modes.
- Split address and data pairs are common: base addresses, read/write pointer report addresses, EOP/fence addresses, command-buffer bases, watchpoint addresses, suspend-context-save bases, and RS64 GP/local apertures. High/low mismatches can point hardware at the wrong memory or corrupt queue state.
- Queue, HQD, MQD, doorbell, VMID, dequeue, and preemption registers are synchronization-sensitive. Misprogramming can wedge queues, lose interrupts, corrupt ring pointers, or break GPU reset recovery.
- PF/VF and PF-only address blocks are security-sensitive. Accidentally exposing PF-only debug/configuration registers to VF paths could affect isolation or leak privileged state.
- Debug/index/data register pairs such as CP/GRBM/GCR/CAC indirect windows are stateful. Concurrent or unordered accesses can select the wrong index or read stale data if callers do not serialize appropriately.
- Counter low/high registers and status registers may be volatile, latched, or clear-on-read depending on hardware rules not expressed here. Test code should avoid assuming ordinary memory semantics.
- Error-injection and reset controls, including GC-EA poison/parity injection, GRBM/CP soft reset, SDMA virtual reset, and VMID reset/preempt registers, have side effects and should be gated to diagnostic or recovery paths.
- Performance and throttle controls in CAC/EDC/DIDT/PCC/PWRBRK families can affect clocks, stalls, and power behavior. Incorrect offsets may manifest as performance loss or thermal/power anomalies rather than immediate functional failure.
- Reserved, dummy, spare, and `NOWHERE` registers are present. Their symbolic existence does not make arbitrary writes safe.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU GC 12.1.0 files that include `gc_12_1_0_offset.h`.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database for every offset and `_BASE_IDX` in lines 2453-4938.
- Cross-checks that registers in this chunk have matching field definitions in `gc_12_1_0_sh_mask.h` where fields are expected.
- Static checks for paired low/high registers, contiguous repeated families, intentional alias groups, and correct base-index transitions at address-block boundaries.
- Runtime queue tests covering SDMA1 queue state, CP ring setup, HQD/MQD programming, doorbell updates, EOP fence signaling, IB submission, dequeue/preemption, and VMID reset.
- Compute dispatch tests that exercise user-data registers, dispatch dimensions, scratch bases, resource limits, restart/relaunch, wave restore, and per-SE static thread controls.
- Suspend/resume and GPU reset tests that restore queue state, context-save buffers, ring pointers, CP/SDMA/GRBM status, and RS64 firmware-facing registers.
- Performance and diagnostics tests that configure SDMA counters, CP pipe stats, shader invocation counters, CAC/EDC power counters, throttle status, and debug index/data ports.
- Virtualization tests for active function ID, virtual reset, PF/VF unmapped queues, doorbell banks, privilege violation addresses, IOV errors, and PF-only register access controls.
- Error-path tests for UTCL1 errors, GC-EA invalid opcode/parity/poison logs, ECC first occurrence, fatal CP errors, read/write error registers, and stall/busy status dumps.
- Warning signals include GPU hangs during queue initialization or preemption, bad fences/EOP completion, wrong ring pointers, broken compute dispatch, missing interrupts, impossible busy/stall dumps, malformed performance counters, virtualization isolation failures, or unexpected throttling/power behavior.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002587`. It covers lines 2453-4938 of `gc_12_1_0_offset.h`; the merge/reconciliation lane should combine it with adjacent chunks to complete the full generated GC 12.1.0 offset-header analysis.

### subset-b-002588: lines 4939-7413

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 4939-7413

## Scope

This chunk is a generated AMD GC 12.1.0 register-offset header segment. It contains C preprocessor constants only: each hardware register has a `reg...` macro containing the register offset and a matching `reg..._BASE_IDX` macro selecting the register base aperture. There are no functions, structs, enums, includes, variables, locks, allocations, callbacks, or executable branches in this range.

The selected range begins inside a command-processor RS64 address family, immediately after `regCP_CPC_IC_OP_CNTL_BASE_IDX`, and then covers multiple address blocks:

- CP graphics RS64 interrupt, local data/instruction/scratch apertures, general-purpose registers, instruction pointers, pending interrupts, and 16 data-cache aperture slots for each of two aperture banks.
- CH and GLARB arbitration/control blocks for graphics fabric request steering and credit/status tracking.
- CP/GRBM/GE/CH/GLARB/RLC/GCR/CHA performance counter data registers and matching select/control registers, including RLC streaming performance monitor (SPM) setup.
- XVMIN write-data access.
- RLC hypervisor, CP hypervisor, GRBM hypervisor, RLC core, RLCS, PF/VF RLC, power, PSP/security, CP PSP debug/data-mover, CH power, GFX IMU, GFX IMU PSP, GRBMH, and the first PA/GE/CC registers in the next address block.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP and is not Ceph filesystem logic.

## Purpose

`gc_12_1_0_offset.h` gives AMDGPU code symbolic names for GC 12.1.0 register offsets. Callers combine these offsets with base-index metadata, generated field definitions from the matching shift/mask header, and AMDGPU MMIO, indirect-register, PM4, firmware, debug, or reset helpers. The result is that ASIC-specific code can address hardware registers without embedding raw offsets throughout driver logic.

This chunk maps mostly control-plane registers rather than render-state registers. Its main purpose is to expose the register addresses used to initialize, monitor, virtualize, debug, and power-manage the GC command, RLC, arbitration, performance, and IMU subsystems.

Notable functional areas are:

- CP RS64 graphics microcontroller state: interrupt enables, exception status, local base/mask/aperture registers, local instruction and scratch regions, performance-count control, machine interrupt/time compare style registers, general-purpose registers, instruction pointers, pending interrupt state, and data-cache aperture base/mask/control tuples.
- CH/GLARB arbitration and fabric configuration: arbitration controls, DRAM burst masks/controls, status, client credits, free-delay controls, FGCG/MGCG overrides, hash configuration, pipe steering, AID selection, and memory-disable user controls.
- Performance monitoring: low/high counter readout registers, select registers, latency-stat select/data registers, draw-object/window counters, GRBM/GE/RLC/GCR/CHA/CHC/GLARB counter families, and RLC SPM ring, mux, accumulation, pause/status, timestamp, and RSPM request/response registers.
- RLC virtualization and hypervisor control: VF enable/mask/status, SDMA status and busy state, VM busy state, scheduling block and active function ID, doorbell status set/clear, semaphores, virtual reset request, SMU/RLC response registers, VFI command/status/address/data windows, and PF/VF-facing RLC safe-mode and interrupt registers.
- CP hypervisor and firmware memory windows: PFP/ME/MEC microcode address/data/checksum/version registers, instruction-cache base/control registers, MES/MEC/GFX RS64 instruction/data base and bound aliases, and context-range limits.
- RLC core and RLCS control: RLC control/status, firmware versions, active masks, clock/timestamp counters, GPM timer and interrupt registers, RAS/MCA interrupt control, power-gating and clock-gating controls, GPM/SRM/SRS/SRM state, SPP private state, residency counters, IH client status, LX6/XT core state, doorbell monitors, SMU message/argument registers, and IMU bootload handoff registers.
- RLCS service block: decode start/end, exception dump registers, fence, CG/DS controls, power-gating status, bootload status, general-purpose registers, KMD logging controls, GCR data/status, RLC-IMU mailbox and RAM access, SDMA interrupt status, FED/security status, and UTCL2/SE snapshots.
- PSP/security access: GC_EA CPWD security-level and SDP error registers, GRBM source-ID and CAM programming, IOV range enables, security control, firewall violation address capture, UTC bypass control, and CP/MES/MEC/GFX RS64 indexed data-mover debug windows.
- GFX IMU control and firmware interface: C2P message mailboxes 0-47, access controls, MP1/RLC/SOC mailboxes, mutexes, VF control, scratch registers, GTS offset and firmware timestamp registers, interrupt controller and IH controls, fuse/clock/doorbell/DPM controls, RLC RAM windows, fence logging, core power/reset/isolation controls, timers, data/instruction RAM access, bootloader address/size, and gasket control.
- GRBMH and PA tail registers: high-level GRBMH control/status/soft-reset/read-error/clocking/sync registers and the start of the PA block containing GE rate controls, shader-array configuration, and SE control/status.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `reg<NAME>` expands to the GC 12.1.0 register offset used by AMDGPU register access paths.
- `reg<NAME>_BASE_IDX` expands to the base-index selector for that register. In this slice, CPWD/RLC/IMU/PSP style blocks mostly use base index `1`, while GRBMH and PA/GE tail registers use base index `0`.
- Field-level shift and mask constants live in the companion `gc_12_1_0_sh_mask.h` header, not in this offset header.
- Default/reset values, when generated for this ASIC family, are expected in matching default headers.

The chunk contains about 1200 register-offset macros, excluding the paired `_BASE_IDX` definitions. Large repeated or alias-prone families include:

- `regCP_GFX_RS64_*`: RS64 graphics-side local memories, interrupts, performance controls, GP registers, instruction pointers, pending interrupts, and data-cache aperture tables.
- `regCH*`, `regCHA*`, `regCHC*`, `regCHI*`, `regGLARB*`, `regGLARBA*`, `regGLARBC*`, `regGLARBI*`: arbitration, credit, clock-gating override, hash, pipe-steering, and fabric-local power/memory controls.
- `reg*_PERFCOUNTER*_LO/HI`, `reg*_PERFCOUNTER*_SELECT*`, `reg*_LATENCY_STATS_*`, `regRLC_SPM_*`: performance data, counter muxing, streaming monitor ring/segment/mux/accumulator controls, and SPM status.
- `regRLC_GPU_IOV_*`, `regRLC_VFI_*`, `regRLC_RLCS_IOV_*`: GPU IOV and virtualization state, command/status windows, scheduling, VF masks, and SDMA/VM busy indicators.
- `regCP_HYP_*` plus legacy aliases such as `regCP_PFP_UCODE_ADDR`, `regCP_ME_RAM_RADDR`, `regCP_ME_RAM_WADDR`, and `regCP_ME_RAM_DATA`: CP firmware and RAM windows exposed under both hypervisor and non-hypervisor names.
- `regRLC_*`: the largest family in the chunk, covering RLC core control, GPM/SRM/SRS/SPP state, clock/power gating, RAS/MCA, residency counters, doorbells, SMU messages, IMU bootload, and low-level firmware status.
- `regRLC_RLCS_*`: RLCS decode/service, bootload, logging, mailbox, RAM, power, interrupt, FED, and snapshot registers.
- `regGFX_IMU_*`: IMU mailboxes, scratch, timers, interrupts, bootloader, core control/status, power/reset/isolation, RLC RAM, and D/I-RAM access.
- `regGRBM*` and `regGRBMH*`: GRBM hypervisor indexed state, source-ID/security CAMs, remap controls, and GRBMH control/status/reset.
- `regGE_*` and `regCC_GC_SHADER_ARRAY_CONFIG`: early graphics-engine and shader-array configuration offsets at the end of the chunk.

Some offsets intentionally have multiple symbolic names. For example, `0x5814` is both `regCP_HYP_PFP_UCODE_ADDR` and `regCP_PFP_UCODE_ADDR`; `0x5816` is shared by `regCP_HYP_ME_UCODE_ADDR`, `regCP_ME_RAM_RADDR`, and `regCP_ME_RAM_WADDR`; `0x5850/0x5851` are both MES instruction-cache base names and `MIBASE` aliases; `0x5870/0x5871` are both MEC data-cache base names and `MDBASE` aliases; and `0x4e6c` is both `regRLC_GPM_STAT` and `regRLC_RLCS_GPM_STAT`. These aliases are part of the generated register database and can reflect different programming-model names for the same hardware offset.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied AMDGPU flow is:

1. ASIC discovery selects GC 12.1.0 register headers for the device.
2. A driver path chooses a symbolic register, its `_BASE_IDX`, and usually a companion field mask/shift from `gc_12_1_0_sh_mask.h`.
3. The offset is passed to an MMIO accessor, indirect indexed register helper, firmware programming sequence, PM4 packet builder, debug dump path, or register save/restore table.
4. Hardware state changes, status is sampled, or a diagnostic/control operation is triggered according to the target block's protocol.

Important implied sequences include:

- RS64 CP setup programs local base/mask/aperture registers, data/instruction bounds, scratch windows, interrupt enable/status registers, and instruction-cache/data-cache controls before or during microcontroller execution.
- Performance setup first programs select/mux/window registers, then starts or enables counters through performance-monitor controls, then reads low/high counter registers or RLC SPM output rings and accumulation memories.
- RLC and RLCS firmware flows use address/data register pairs for microcode, RAM, scratch, command, and mailbox windows; status and fence registers are polled by driver or firmware sequencing outside this header.
- GPU IOV and PF/VF flows use VF masks, scheduling registers, active function IDs, virtual reset requests, doorbell status set/clear registers, and VFI command/status windows to coordinate virtualization state.
- Power and clock management flows use RLC, CGTT, ICG, GRBM, GFX IMU, and residency-counter registers to gate clocks, request power transitions, measure residency, and coordinate with SMU/MP1.
- PSP/security flows use GRBM CAM/source-ID and security/firewall registers to configure allowed access ranges and capture violation addresses.
- IMU boot and communication flows use bootloader address/size registers, D/I-RAM access, C2P mailboxes, RLC/IMU mutex and mailbox registers, timers, interrupt controller controls, and reset/isolation controls.

The header does not define ordering constraints, polling conditions, delays, locking, register side effects, or firmware ownership. Those are supplied by AMDGPU code, platform firmware, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They name hardware registers whose contents are volatile GPU state.

CP RS64 and CP hypervisor registers represent firmware-visible command-processor state. Local base/mask/aperture, instruction/data bounds, scratch, cache base/control, and microcode window registers persist only as programmed hardware state and may be reset, reloaded, or saved/restored during GPU reset, suspend/resume, virtualization transitions, or firmware reload.

Performance counter registers are live measurement state. Select registers and monitor controls configure what is counted, low/high readout registers expose running or latched counters, and SPM ring/mux/accumulator registers persist sampling configuration and buffer pointers. Counter values, write pointers, status bits, and accumulation RAM contents can change while engines are active.

RLC/RLCS state is firmware-owned control state. It includes power-gating, clock-gating, GPM/SRM/SRS/SPP, interrupt, doorbell, SMU message, GCR, IMU mailbox, bootload, and residency state. Some registers are commands or acknowledgments with side effects; others are volatile status, counters, or firmware scratch/general-purpose storage.

GPU IOV and security registers persist virtualization and access-control state for PF/VF operation. VF enables, masks, scheduling state, active function IDs, doorbell status, security CAMs, IOV ranges, and firewall violation capture registers can affect isolation boundaries and may need strict restore semantics after reset or FLR.

GFX IMU registers hold mailbox, scratch, firmware timestamp, timer, interrupt, DPM, fence, RAM, bootloader, power, reset, and isolation state. Several are producer/consumer communication surfaces between driver, RLC, IMU firmware, SOC/MP1, and PSP. Treat them as firmware-owned unless the surrounding sequence documents direct host writes.

CH/GLARB/GRBMH/PA tail registers hold fabric arbitration, pipe steering, clocking, reset, status, and shader-array/GE configuration. Misprogramming can persist until reset and affect routing, performance, or visibility of graphics shader arrays and SE state.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register set remaining internally consistent:

- `gc_12_1_0_sh_mask.h` supplies field positions and masks for many registers named here.
- Other generated GC 12.1.0 headers may provide defaults, enumeration-like values, and additional address regions outside this chunk.
- AMDGPU register helpers, MMIO accessors, indirect register helpers, PM4 packet emitters, debugfs/register-dump code, firmware load code, reset code, power-management code, virtualization code, and RAS/error paths consume these offsets.

Key integration points include:

- GFX/CP firmware setup for PFP, ME, MEC, MES, and GFX RS64 microcode/RAM windows.
- Command submission and scheduling paths that depend on CP interrupt status, pending interrupt state, local memory windows, and scheduler-related RLC/IOV registers.
- RLC firmware loading, boot sequencing, safe mode, power-gating, clock-gating, SPM, thread trace, SPP, SMU messaging, and IMU bootload handoff.
- SR-IOV/PF/VF management paths that inspect or update VF enable/mask, VM/SDMA busy status, active function ID, scheduling block, virtual reset, VFI access, and doorbell state.
- PSP/security paths that configure GRBM source-ID/CAM/IOV ranges, SDP security maps, and firewall violation capture.
- Profiling and diagnostics paths that configure CP/GRBM/GE/CH/GLARB/RLC/GCR/CHA counters and RLC SPM buffers/muxes.
- Power-management paths that interact with CGTT, ICG, RLC residency counters, SMU command/argument registers, GFX IMU DPM controls, and power/reset/isolation controls.
- Interrupt handling paths through RLC IH cookies/status, RLC GFX IH client state, GFX IMU PIC/IH controls, and GRBMH status/read-error registers.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong offset or base index compiles cleanly but can direct an MMIO write to the wrong hardware register.
- This chunk starts and ends mid-file and mid-family. It begins after a prior CP CPC instruction-cache macro and ends in the first PA block, so adjacent chunks are needed for complete file-level conclusions.
- Alias registers can confuse audits. Shared offsets such as CP microcode/RAM names, MES/MEC base aliases, and `regRLC_GPM_STAT`/`regRLC_RLCS_GPM_STAT` must be validated as intentional aliases, not duplicate-generation errors.
- Base-index mismatches matter. Most CPWD/RLC/IMU/PSP registers here use base index `1`, while GRBMH/PA registers use base index `0`; using the wrong base aperture could target a different register space.
- Address/data window registers require sequencing. Microcode RAM, IMU RAM, SRM/SRS/SPM indirect RAM, SERDES, SOC, VFI, and CAM access patterns usually require write-address then read/write-data ordering, busy polling, or firmware arbitration that this header cannot express.
- Command, reset, safe-mode, interrupt-force/clear, doorbell, virtual-reset, fence, power-gating, clock-gating, and SMU-message registers can have side effects. Treating them as passive configuration or dump-only state can disrupt firmware or active queues.
- Performance counters and SPM state are volatile. Low/high counter reads can tear if the caller does not follow the hardware read protocol; SPM ring base/size/write-pointer state can corrupt profiling output if programmed while running.
- Virtualization and security registers are isolation-sensitive. Incorrect VF masks, active function IDs, IOV ranges, source-ID CAM data, or firewall controls can leak access across PF/VF boundaries or block required firmware/driver access.
- Power and clock controls interact with firmware ownership. Direct writes to CGTT/ICG/RLC/IMU power registers outside coordinated sequences can hang graphics, break residency accounting, or race SMU/MP1.
- IMU/RLC mailbox registers are concurrency-sensitive. Mutex, status, command, and scratch/mailbox registers may require strict producer/consumer handshakes between host, RLC, IMU, PSP, and SOC firmware.
- Repeated families are easy to validate incompletely: 48 IMU C2P messages, 16 IMU scratch registers, multiple SPM mux/data windows, multiple performance-counter banks, and SDMA0-7 IOV status registers need index-by-index checks.

## Test Signals

Useful validation is mostly generated-data consistency plus targeted AMDGPU build/runtime coverage:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_offset.h`, especially GC 12.1.0 CP, RLC, firmware, power, virtualization, performance, debug, reset, and interrupt paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database for every `reg...` offset and `reg..._BASE_IDX` in lines 4939-7413.
- Static checks that every non-alias offset has the expected paired `_BASE_IDX`, aliases are intentional, and repeated families remain monotonic and correctly spaced.
- Cross-checks that registers named in this chunk have matching shift/mask definitions where fields are expected, and defaults where generated.
- Firmware load and reset tests covering PFP/ME/MEC/MES/GFX RS64 microcode windows, RLC boot, IMU bootloader address/size, RLC safe mode, and reset recovery.
- SR-IOV or virtualization tests covering VF enable/mask, active function ID, VM/SDMA busy status, virtual reset, VFI command/status, PF/VF doorbells, and security/IOV range behavior.
- Profiling tests covering CP/GRBM/GE/CH/GLARB/RLC/GCR/CHA counters, latency stats, RLC SPM ring setup, mux programming, pause/status handling, and low/high counter consistency.
- Power-management tests covering RLC power/clock gating, CGTT/ICG controls, SMU command/message paths, residency counters, IMU DPM controls, and suspend/resume restore.
- Interrupt/debug tests covering RLC IH cookies, GFX IH client status, IMU PIC/IH state, GRBMH read-error/status, CP pending interrupts, and firmware mailbox status.
- Security diagnostics covering GRBM source-ID/CAM programming, SDP security maps, firewall first-violation address capture, and PSP/CP indexed debug windows.

Runtime warning signals include GPU hangs during firmware boot or reset, failed RLC/IMU mailbox handshakes, bad SPM samples, impossible counter values, broken VF isolation, unexpected firewall violations, missing or stuck interrupts, power-gating or clock-gating stalls, GRBMH read errors, and register dumps showing inconsistent base-index interpretation.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002588`. It covers lines 4939-7413 of `gc_12_1_0_offset.h`. The final per-file research should merge this with adjacent chunks to complete the surrounding CP RS64/CPWD register families before line 4939 and the PA/graphics-state address blocks after line 7413.

### subset-b-002589: lines 7414-9893

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 7414-9893

## Scope

This chunk is a generated AMD GC 12.1.0 register-offset header segment. It contains C preprocessor constants only: `reg*` macros name graphics-core hardware register offsets, and paired `reg*_BASE_IDX` macros identify the SOC15 base-index slot used by AMDGPU register-address helpers.

The requested range contains 1,200 register-offset macros and 1,200 `_BASE_IDX` macros. The range starts on `regGE_SE_CNTL_STATUS_BASE_IDX`, whose offset macro is immediately before this chunk, and ends on `regWGS_COMPUTE_PIPELINESTAT_ENABLE`, whose `_BASE_IDX` macro is immediately after this chunk. Those artificial chunk boundaries should be reconciled when the final per-file document is assembled.

Although this source tree is rooted under a local `ceph-client` mirror, this file is AMDGPU DRM graphics metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_12_1_0_offset.h` supplies named MMIO/register offsets for AMD GC 12.1.0 graphics hardware. Driver code includes this header so ASIC-specific paths can address registers by stable symbolic names instead of copying numeric offsets into source files.

This chunk covers the shader engine and user-config/control portions of the GC register map:

- Tail GE/PA debug and safety controls preceding the SQ decoder block.
- SQ/SQC/SQG shader-queue configuration, debug, watchpoint, timeout, UTCL0 retry, PIT/WS, and indirect-index/data registers.
- SX and SPI shader processor interface debug, CU mask, wave lifetime, shader program, user-data, accumulator, arbiter, context-save, queue-reset, and DIDT control registers.
- Texture/depth/render/backend control blocks: TD, TA, DB, CB, GB, and RMI debug/status/arbitration/cache/FIFO/configuration registers.
- UTCL1, TCP, and PF-only TCP registers for L1 translation/cache behavior, invalidation, XNACK/retry handling, hashing masks, credit, thrashing, congestion, and watchpoints.
- The large `gfxdec0` user/context register space containing DB depth/stencil state, PA viewport/scissor/clip/rasterization state, SPI pixel-shader input state, SX blend optimization, CB render-target state, VGT/GE/NGG controls, HiZ/HiS controls, and multisample sample-location state.
- PF/VF and PF-only/second PF-only windows for PA/SQ/SPI/UTCL1/TCP controls, including virtualization-visible debug/trap/runtime controls and privileged resource-reserve controls.
- GFXU user-config registers for tessellation/offchip/ring resources, trap-screen controls, thread-trace userdata, SQC caches, occlusion counters, SPI attribute rings, and compute workgroup scheduler controls.
- The beginning of the WGS compute-dispatch register sequence for dispatch initiator, dimensions, starts, thread counts, and pipeline-stat enable.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable branches in this range. The public interface is the generated macro contract:

- `regNAME` gives the encoded register offset within the selected GC address space.
- `regNAME_BASE_IDX` gives the SOC15 base-index selector for that offset. In this chunk, 402 base-index entries are `0` and 798 are `1`.
- Address-block comments identify the generated hardware block and base address, such as `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_sqdec` at `0x8c00`, `gfxdec0` at `0x28000`, `gfxudec` at `0x30000`, and `comp_wgsdec` at `0x31a00`.
- Consumers combine these macros with AMDGPU register helpers such as SOC15 `RREG32*`/`WREG32*` paths, field helpers, indirect register access, command-stream register writes, and ASIC-specific save/restore code.
- Bitfield layouts are intentionally not present here; they are supplied by the companion GC 12.1.0 shift/mask header (`gc_12_1_0_sh_mask.h`) and by higher-level driver sequences.

Important macro families in this chunk include:

- `SQ_*`, `SQC_*`, and `SQG_*`: shader queue configuration, GL1/UTCL0 status, wave/prioritization controls, performance snapshot, interrupt masking, watch registers, timeout status, SQC PIT/WSM controls, and indirect index/data commands.
- `SPI_*`: shader processor interface controls spanning debug, CU masks, wave lifetime, scratch status, `SPI_SHADER_PGM_*`, `SPI_SHADER_USER_DATA_*`, `SPI_SHADER_USER_ACCUM_*`, arbiter percentages, compute queue reset, context-save, DIDT, resource reserve, attribute ring, and group-launch controls.
- `DB_*`: depth/stencil render control, Z/stencil surface bases, HTILE, depth bounds, shader/depth/stencil controls, occlusion counters, debug/status/FIFO/watermark/arbiter controls, and summarizer state.
- `PA_*` and `SC_*`: viewport, scissor, cliprect, user clip-plane, raster, VRS, binner, HiZ/HiS, anti-aliasing, conservative rasterization, point/line/stipple, polygon offset, trap-screen, and screen-extent controls.
- `CB_*`: blend constants, target masks, shader masks, color-control registers, per-render-target color base/view/attrib/FDCC/info state, memory info, cache control, and hardware/memory-arbiter controls.
- `TA_*`, `TD_*`, `TCP_*`, `TXA_*`, `UTCL1_*`, and `GCRD_*`: texture address/data and texture cache path control, invalidation/status/credits, set-hash masks, UTCL1 identity/hash/status, target-disable and credit-safe registers, XNACK/retry timers, and TCP watchpoints.
- `RMI_*`, `GB_*`, and `CC_*`: render backend/raster-memory-interface routing, scoreboard, crossbar, UTC/UTCL1, backend map/address configuration, GPU ID, backend disable, and redundancy controls.
- `VGT_*`, `GE_*`, and `WGS_*`: tessellation/offchip/ring resources, NGG/output controls, and compute dispatch/workgroup scheduler programming.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU/KFD consumers:

1. The active ASIC path includes GC 12.1.0 offset and shift/mask headers.
2. Driver code selects a symbolic `reg*` macro and the matching `_BASE_IDX` through SOC15-aware helpers.
3. For field-level programming, code combines the offset from this file with masks/shifts from `gc_12_1_0_sh_mask.h`.
4. The register is read, written, polled, or emitted into a command stream by higher-level graphics, compute, VM, debug, reset, or power-management code.
5. The higher-level sequence supplies ordering, privilege, polling, reset, and side-effect rules; this generated header only supplies addresses.

For shader setup, command streams and context state program SPI shader program addresses/resources, user-data slots, PS input controls, accumulators, and SQ/SQC/SQG controls. For graphics render state, context programming writes DB, PA/SC, CB, SX, GE, and VGT registers for depth/stencil, viewport/scissor/raster, blend/color target, NGG, tessellation, sample, and binner behavior. For cache/translation paths, driver code uses TCP/UTCL1/RMI/GCRD offsets for invalidation, retry, XNACK, identity mode, hash masks, target disable, and status/error handling.

## State And Persistence Behavior

The macros themselves hold no runtime state and persist nothing. They describe hardware-visible state:

- SQ/SQC/SQG and SPI registers affect shader scheduling, trap/watch behavior, interrupt delivery, shader program resources, scratch/user-data programming, wave lifetime limits, and compute context-save/reset flows.
- DB/CB/PA/SC/SX/VGT/GE registers are graphics context state. They are programmed by command streams or context setup and may be saved/restored, shadowed, reset, or rebuilt depending on the GPU mode and ring/context ownership.
- TCP/UTCL1/RMI/GCRD registers expose cache and translation behavior: invalidation, XNACK retry, hashing, identity mode, credits, target disable, status, and watchdog/debug state. These values can be reset-sensitive and may need reprogramming after GPU reset, suspend/resume, or virtualization transitions.
- PF/VF, PF-only, and PF-only2 blocks partition what can be accessed from virtualized or privileged contexts. The `_BASE_IDX` value is part of this partitioning; an otherwise correct offset can reach the wrong aperture if the base index is wrong.
- GFXU and WGS user-config state includes ring base/size registers, offchip/tessellation parameters, trap-screen state, occlusion counters, attribute rings, thread-trace userdata, SQC cache controls, and compute dispatch/workgroup scheduler setup.

This offset header does not encode whether a register is read-only, write-only, write-one-to-clear, clear-on-read, privileged, indexed, broadcast, shadowed, saved/restored, or safe for read-modify-write. Those semantics must come from the hardware specification and the AMDGPU code that uses the macros.

## Dependencies And Integration Points

This file depends on consistency with AMD's authoritative GC 12.1.0 register database and companion generated headers in the same directory, especially `gc_12_1_0_sh_mask.h`.

Observed include users in this source tree include GC 12.1.0 graphics, memory hub, MES, SDMA, IMU, SOC, and KFD paths such as `gfx_v12_1.c`, `gfxhub_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `imu_v12_1.c`, `sdma_v7_1.c`, and `soc_v1_0.c`.

Primary integration points are:

- AMDGPU SOC15 register helpers, which combine register offsets and `_BASE_IDX` selectors into MMIO addresses for the current GC instance/XCC.
- Graphics pipeline state setup and command submission, which use DB/CB/PA/SC/SX/VGT/GE/SPI offsets for render target, depth/stencil, viewport, scissor, blend, sample, shader, NGG, and tessellation state.
- Shader program and debug paths, which use SQ/SQC/SQG/SPI offsets for program resource registers, user data, traps, watchpoints, wave controls, indirect SQ access, and status polling.
- KFD and compute scheduling paths, which care about compute queue reset, context-save, wavefront context status, WGS dispatch registers, CU masks, resource reservation, and TCP/SQ/SPI watchpoint facilities.
- VM/cache/translation paths, which use TCP/UTCL1/RMI/GCRD offsets for invalidation, retry/XNACK behavior, hashing, target disable, identity mapping, and status.
- SR-IOV/virtualization paths, where PF/VF and PF-only block boundaries determine which software component may touch PA/SQ/SPI/UTCL1/TCP controls.
- Performance, diagnostics, and recovery paths that read status/debug/FIFO/watermark/occlusion/thread-trace counters or reinitialize state after GPU reset.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong numeric offset or base index compiles cleanly but can target the wrong hardware register.
- The chunk boundaries are artificial. `regGE_SE_CNTL_STATUS_BASE_IDX` lacks its offset macro inside the chunk, and `regWGS_COMPUTE_PIPELINESTAT_ENABLE` lacks its `_BASE_IDX` inside the chunk.
- `BASE_IDX` mismatches are as dangerous as offset mismatches because the same encoded offset can refer to a different physical aperture under SOC15 helpers.
- Large repeated families are copy-sensitive: viewport/scissor registers 0-15, user clip planes, PS input controls 0-31, shader user-data slots 0-31, CB color targets 0-7, TCP hash masks, watchpoint slots 0-3, SPI resource reserve entries 0-15, occlusion counters 0-3, thread-trace userdata 0-7, and WGS XYZ dimensions/starts/thread counts must preserve exact naming and stride.
- Shader program/resource and user-data offsets are execution-critical. A single bad offset can produce shader hangs, wrong descriptors, trap/debug failures, broken context save/restore, or missed wave control.
- DB/CB/PA/SC/SX/VGT/GE offsets are render-correctness sensitive. Errors can manifest as corrupt depth/stencil, wrong viewports or scissors, bad MSAA/VRS behavior, broken blending, invalid render target programming, missing occlusion counts, or GPU hangs during draws.
- TCP/UTCL1/RMI/GCRD mistakes can cause stale translations, invalid cache invalidation, XNACK retry failures, incorrect identity mappings, or backpressure/deadlock symptoms rather than immediate compile failures.
- PF/VF and PF-only register placement is security- and reliability-sensitive under virtualization. Programming a privileged-only register from the wrong path can break isolation or reset recovery.
- Status/debug registers may have side effects not represented here. Consumers must not infer read/write safety from the existence of an offset macro.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime testing:

- Build AMDGPU with GC 12.1.0 support and KFD enabled. Missing or renamed macros should surface in ASIC-specific include users.
- Mechanically compare this line range against the authoritative GC 12.1.0 register database, checking both offset values and `_BASE_IDX` values.
- Cross-check repeated families for count and stride consistency: SPI shader user-data slots, PS input controls, PA viewport/scissor state, CB color target blocks, TCP hash masks, watchpoint slots, resource reserve entries, thread-trace userdata, occlusion counters, and WGS XYZ registers.
- Verify that the split boundary macros are completed by adjacent chunks during final reconciliation.
- Run graphics render tests that stress depth/stencil, viewport/scissor, cliprects, VRS, MSAA sample locations, blending, color targets, HiZ/HiS, NGG, tessellation, and occlusion queries. Relevant signals include correct pixels, no CP/GC hangs, and plausible occlusion counter values.
- Run shader and debug workloads that exercise PS/GS/HS/LS program resources, user data, accumulators, traps, wave watchpoints, SQ indirect access, and thread trace. Watch for shader faults, invalid trap behavior, and unexpected SQ/SPI status.
- Run KFD compute queue, preemption/context-save, queue reset, and multi-process workloads. Watch for stuck waves, context-save timeouts, broken CU masking/resource reservation, and bad WGS dispatch dimensions.
- Run VM/cache stress with frequent memory mappings, invalidations, XNACK/retry activity, and suspend/resume or GPU reset. Relevant signals include no stale data, no retry storms, clean reset recovery, and sane TCP/UTCL1/RMI status.
- Exercise SR-IOV/PF-VF environments where available to validate PF/VF and PF-only register access boundaries.

## Cross-Chunk Notes

The previous chunk owns the offset macro for `regGE_SE_CNTL_STATUS`; this chunk begins with its `_BASE_IDX`, then covers GE/PA tail registers, SQ/SQC/SQG, SX/SPI, TD/TA/DB/CB/RMI/UTCL1/shader program/TCP/gfxdec0/PF-VF/PF-only/GFXU groups. The next chunk should provide `regWGS_COMPUTE_PIPELINESTAT_ENABLE_BASE_IDX` and continue the WGS compute-dispatch register sequence.

### subset-b-002590: lines 9894-12404

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 9894-12404

## Scope

This chunk covers a late slice of the generated AMD GC 12.1.0 register offset header. It starts inside the `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_comp_wgsdec` compute WGS block, immediately after earlier compute dispatch dimension/start/thread registers, and ends in the `gfx_se_sqind` indirect SQ index block after `ixSQ_WAVE_TTMP7`.

The range contains 2,391 preprocessor definitions: 1,215 register or indirect-index constants and 1,176 matching `_BASE_IDX` constants. It is pure hardware metadata. There are no C functions, structs, enums, storage objects, include dependencies, locks, allocations, sysfs/debugfs entries, or executable branches in this chunk.

Major covered areas are:

- WGS compute dispatch, program, scratch, static-thread-management, relaunch, user-data, interrupt, RS64 microcontroller, suspend/resume, aperture, cache, scratch, latency, metadata, and status registers.
- Shader-engine GL1/GL1X arbitration, compression, UTCL, clock/power, CAC, DIDT/EDC, and power-estimation registers.
- Shader-engine performance counter low/high data registers and selector/control registers for GE2, GRBMH, PA, SPI, PC, SQ, SQG, SX, TA, TD, TCP, GL1C/GL1XC, CB, DB, RMI, PA_PH, UTCL1, WGS, GL1A, and GL1XA.
- SQ thread-trace buffer, mask, token, write-pointer, halt, restore, status, and counter registers.
- Per-block clock-gating and clock-control registers for SPI, PC, VGT/GS/NGG, PA, SQ/SQG/SP, SX, TA, TD, DB, CB, RMI, SE CAC, PA_PH, TCP, LDS, UTCL1, GRBMH, SC, GL1C/GL1A, and GL1XC/GL1XA.
- User topology and remap registers for GL1 pipe steering, hash config, shader-array config, RB backend disable, RMI redundancy, shader-rate config, WGP/RB remapping, and system aperture default address.
- GCVM, GCMC, GCUTC, GCUTCL2, GCVML2, GC ATC L2, and GC L2TLB address blocks for aperture location, L2 translation/cache control, page faults, contexts, invalidate engines, page-table ranges, performance counters, ATS/IOMMU controls, per-VF framebuffer apertures, and PSP/hypervisor-visible translation controls.
- `gfx_se_sqind` indirect indexes for wave debug/status, program counter, allocation, exception, trap, scratch, hardware ID, scheduler, XNACK, performance snapshot, and TTMP register reads.

Although this tree is under a `ceph-client` source mirror, this file is AMDGPU graphics hardware register metadata and does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to provide the compile-time address ABI between GC 12.1.0 driver code and graphics/compute/translation hardware. Each ordinary register is represented by:

- `reg<REGISTER>`, the SOC15-style register offset.
- `reg<REGISTER>_BASE_IDX`, the register aperture/base selector used by AMDGPU register helpers.

This chunk also includes `ixSQ_*` constants. Those are not MMIO register offsets in the same style as `reg...`; they are indirect SQ wave/debug indexes consumed through SQ indirect access helpers. In local GC 12 code, `gfx_v12_0.c` uses `wave_read_ind()` with indexes such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_HW_ID1`, `ixSQ_WAVE_HW_ID2`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, and related wave state indexes when collecting wavefront state.

The companion `gc_12_1_0_sh_mask.h` file supplies bit shifts and masks for many of these register names, and `gc_12_1_0_default.h` supplies generated reset/default values where available. This offset header only names addresses and base indices.

## Important Macro Families

### WGS Compute and WGS Decoder State

The chunk begins in the middle of WGS compute dispatch state. Covered compute registers include `regWGS_COMPUTE_PERFCOUNT_ENABLE`, program pointer registers `regWGS_COMPUTE_PGM_LO/HI`, dispatch packet and scratch base registers, program resource registers, VMID, resource limits, static thread management or destination-enable aliases for shader engines, temporary ring size, restart coordinates, thread trace enable, dispatch IDs, request control, user accumulators, shader checksum, dispatch interleave, relaunch and wave restore address registers, prescaled dimensions, and 16 `regWGS_COMPUTE_USER_DATA_*` registers.

The subsequent `wgsdec` block exposes broader WGS firmware and scheduler state: interrupt info/context IDs, error/endian state, generated base address, WGS clock control, ME1 microcode address/data/checksum ports, suspend context-save base/size/stack/workgroup-state controls, OS pipes, suspend/resume requests, DDID base/control, RS64 program counter/vector/interrupt/control registers, machine interrupt enable/pending registers, data/instruction cache controls, timer compare registers, GP registers, indexed data-memory access, local/instruction/scratch apertures, RS64 perfcount and exception state, code/data base and bounds, interrupt status/free counts, ME1 pipe priority controls, IC base/control, ucode version, busy/stall/status registers, scratch index/data, latency statistics, TC performance counter window selection, metadata base/control, IQ timers, halt hysteresis, and RS64 thread control.

These names are integration points for compute dispatch setup, firmware loading, suspend/resume, diagnostic register dumps, performance monitoring, and low-level scheduler state inspection. The header does not define sequencing for those operations; it only supplies the offsets used by driver or firmware-facing code.

### Shader-Engine Arbitration, Power, CAC, and DIDT

The GL1 and GL1X decoder ranges define arbitration controls, DRAM burst masks/controls, status registers, replica fine-grain clock-gating overrides, credit/free-delay registers, compression mode, compressor overrides, and UTCL0 control/status/retry windows.

The `pfonly_secacdec`, `pwrdec`, `sc_pwrdec`, and `gl1_pwrdec` ranges cover shader-engine cost/activity and power behavior: `regSE_CAC_CTRL_*`, CAC soft override/value/window registers, `regDIDT_EDC_*` throttle/threshold/stall/status/overflow/power-delta/performance-counter registers, CAC weight tables for LDS, TCP, SQ, SP, SQC, CU, UTCL1, GL1C, and SPI, indirect CAC index/data access, and per-block clock-gating controls. These registers are typically tied to power-management policy, EDC protection, telemetry, and golden-register programming rather than ordinary queue submission.

### Performance Counters and Thread Trace

The `perfddec` block supplies low/high result registers for many shader-engine counters: GE2, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, TD, TCP, GL1C, GL1XC, CB, DB, RMI, PA_PH, UTCL1, WGS, GL1A, and GL1XA. The `perfsdec` block supplies the paired selector/control registers for those counters, including secondary `SELECT1` registers where a block supports multiple packed selections or modes.

Important related control names include `regTCP_PERFCOUNTER_FILTER`, `regTCP_PERFCOUNTER_FILTER2`, `regTCP_PERFCOUNTER_FILTER_EN`, `regTCP_PERFCOUNTER_SET_DEFINE`, `regCB_PERFCOUNTER_FILTER`, `regRMI_PERF_COUNTER_CNTL`, `regSQG_PERFCOUNTER_CTRL`, `regSQG_PERFCOUNTER_CTRL2`, `regSQG_PERF_SAMPLE_FINISH`, `regSQ_PERFCOUNTER_CTRL`, and `regSQ_PERFCOUNTER_CTRL2`.

The same performance selector range includes SQ thread trace registers: buffer sizes and base addresses for two buffers, trace control, shader mask, token mask, write pointer, halt, power-off restore, status/status2, draw and marker counters for GFX and HP3D, dropped counter, and finish-done debug. These offsets are central to profiling and debug flows that collect wave or instruction activity.

### Clock Gating, Topology, and Remap

The power and hypervisor-adjacent shader-engine ranges define a large set of clock controls: `regGFX_ICG_*`, `regCGTT_*`, `regSQ_*_CLK_CTRL`, `regICG_*`, `regDB_CGTT_CLK_CTRL_0`, GL1/GL1X MGCG overrides, and GL1/GL1X clock controls. These names are used when initializing clock-gating policy, overriding clock gating for debug, or applying ASIC-specific golden settings.

Topology and remap state includes `regGL1_PIPE_STEER_LSB/MSB`, `regGL1_HASH_CFG`, `regGC_USER_SHADER_ARRAY_CONFIG`, `regGC_USER_RB_BACKEND_DISABLE`, `regGC_USER_RMI_REDUNDANCY`, `regGC_USER_SHADER_RATE_CONFIG_1`, `regGRBMH_WGP_SA0_REMAP_CNTL`, `regGRBMH_WGP_SA1_REMAP_CNTL`, `regGRBMH_RB_SA0_REMAP_CNTL`, and `regGRBMH_RB_SA1_REMAP_CNTL`. These registers describe harvested or remapped units and memory/cache routing. They must match the real ASIC topology.

### GCVM, GCMC, UTCL2, ATC L2, and L2TLB Translation Blocks

The second half of the chunk is dominated by graphics VM and translation-cache registers. It includes:

- `gcvmsharedpfdec` and `gcvml2pfdec` registers for system aperture defaults, active function ID, UTCL2 busy/group fault status, L2 control/status, dummy page fault, invalidation control, protection-fault control/status/address/default address, identity apertures, physical offset, group RT classes, bank-selection, parity, ICG, GCR control, walker throttling/debug, GPUVA VMID translation-assist request/response, credit-safety controls, UTCL2 FED VMID/ACK state, IH fault interrupt controls, and TLB retry/status registers.
- `gcvmsharedvcdec` and `gcvml2vcdec` registers for framebuffer, AGP, and system aperture base/top/low/high addresses, MX L1 TLB control, 16 VM context controls, context disable, invalidate-engine semaphores/requests/acks for engines 0-17, invalidate address ranges, context page-table base/start/end registers for contexts 0-15, per-PF/VF PTE cache fragment sizes, PCIe atomic support, retry-on-atomic control, and performance-counter data/config/result-control registers.
- `gcvml2prdec`, `gcatcl2prdec`, `gcl2tlbprdec`, `gcvml2pldec`, `gcatcl2pldec`, and `gcl2tlbpldec` registers for ATS, northbridge MMIO and DRAM windows, steering, XGMI/LFB/GPUIOV, host mapping, cacheable/local/LPDDR address ranges, APT control, ATC L2 control/cache-data/status/debug/bank/fault state, L2TLB TMZ/mtype/framebuffer-compression/retry-timeout/reserved-space status, and performance counters.
- Hypervisor/PSP-facing shared, VML2, ATC L2, and L2TLB registers: per-VF framebuffer size/offset for VF0-VF7 in this chunk, local framebuffer offset/start/end/lock control, translation bypass by VMID, secure master, IOMMU host translation enable/control/performance optimization, GPUVA translation assist control, translation fault controls, compression overrides, router control, miscellaneous control, and TLB CAM ECC control.

These blocks are integration points for GFXHUB/VM initialization, page-table programming, TLB invalidation, fault handling, ATS/IOMMU enablement, SR-IOV partitioning, XGMI and host-memory apertures, and VM performance monitoring.

### SQ Indirect Wave Indexes

The final `gfx_se_sqind` block defines indirect SQ indexes, not paired `reg..._BASE_IDX` offsets. Covered indexes include local debug status/control, wave active/valid/idle state, wave mode/status/privileged state, GPR/LDS/DVGPR allocation, instruction-buffer status/debug/flush, performance snapshot data and PC, exception flags, trap control, scratch base, hardware IDs, scheduler mode, XNACK state/mask, PC low/high, and TTMP0-TTMP7.

These constants are consumed through indirect SQ debug accessors, such as the GC 12 wave dump path in `gfx_v12_0.c`. They are mostly diagnostic/debugger-facing and should not be treated as direct MMIO offsets.

## Control Flow

There is no runtime control flow in this header chunk. Its effect is compile-time symbol substitution:

1. GC 12.1.0-aware code includes this offset header with matching shift/mask/default headers.
2. Driver code passes `reg...` constants and their `_BASE_IDX` values into SOC15/IP register access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, `SOC15_REG_OFFSET`, or higher-level AMDGPU helpers.
3. Debug code passes `ixSQ_*` constants to SQ indirect access routines instead of direct MMIO helpers.
4. Hardware and firmware implement the behavior behind each address. This generated file does not encode ordering, polling, permission, volatility, or reset rules.

## State and Persistence Behavior

The header stores no software state and persists nothing. It names hardware-visible state that can be persistent, volatile, sticky, self-clearing, read-only, write-only, write-one-to-clear, indexed, or firmware-owned depending on the specific register.

Important state represented by this chunk includes WGS dispatch and user-data state, WGS firmware/microcode/suspend context, WGS apertures and caches, performance counter selections and results, SQ thread-trace buffers and status, clock-gating policy, CAC/DIDT/EDC thresholds and telemetry, topology/remap/harvest state, GCVM apertures and contexts, page-table base/start/end ranges, invalidate engine semaphores/requests/acks, protection-fault status and addresses, GPUVA translation-assist request/response windows, ATC L2 and L2TLB fault/status/cache/debug state, per-VF framebuffer aperture state, IOMMU/ATS/XGMI/host-mapping controls, and SQ wave debug state.

Persistence is hardware-defined. Configuration registers may survive until reprogramming, power gating, suspend/resume, GPU reset, or ASIC reset. Counters and status registers change as workloads execute. Fault and interrupt status can be sticky. Invalidation, translation-assist, microcode, indexed RAM/data, and thread-trace registers usually require strict sequencing in the consuming code.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention and must stay synchronized with the rest of the GC 12.1.0 generated set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h` for bitfield shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_default.h` for reset/default values where generated.
- GC 12 driver code that includes `gc/gc_12_1_0_offset.h`; locally `soc_v1_0.c` includes this header as part of the GC 12.1.0 register namespace.
- `gfx_v12_0.c`, which demonstrates the `ixSQ_*` integration pattern by collecting wave state with `wave_read_ind()`.
- GFXHUB/VM code paths for page tables, context ranges, invalidation, fault handling, ATS/IOMMU, and aperture programming. Some nearby local examples for related GCVM names appear in golden-register code such as `imu_v11_0_3.c`; GC 12.1.0 consumers use the matching generation's offsets.
- Profiling and debug tooling paths that program performance counter selectors/results and SQ thread trace.
- Power-management, clock-gating, and golden-register initialization paths for CGTT/ICG/CAC/DIDT/EDC controls.
- Virtualization/SR-IOV paths that rely on per-function IDs, per-VF framebuffer apertures, VM partitioning, translation bypass, secure/PSP controls, and host/XGMI apertures.

## Risks and Edge Cases

- Offset or `_BASE_IDX` drift compiles cleanly but can redirect MMIO reads/writes to unrelated hardware state. In these register families, that can cause queue hangs, VM faults, wrong page-table programming, lost invalidation acks, bad profiling data, firmware failures, or GPU reset problems.
- The chunk starts mid-address-block. The first full WGS compute registers, including dispatch initiator, dimensions, start coordinates, and thread counts, are immediately before this range. A final per-file report must merge adjacent chunks before making complete WGS compute claims.
- Many register families are mechanically repetitive but not identical. Performance counters differ by block and counter number; some have `SELECT1`, filters, set definitions, or result-control registers while others do not.
- WGS microcode, suspend/resume, RS64, indexed memory, and cache registers are sequencing-sensitive. The offset header does not say which writes are commands, which statuses must be polled, or which paths are firmware-owned.
- Clock, CAC, DIDT, and EDC controls can affect power, throttling, and stability. Treating them as ordinary debug knobs risks performance regressions, false telemetry, or hardware protection issues.
- Thread-trace and SQ indirect indexes are diagnostic paths. Confusing `ixSQ_*` indexes with direct `reg...` offsets, or using the wrong indirect selector, can return misleading wave state or perturb debug flows.
- GCVM context and invalidation blocks are dense and high impact. A wrong context base/start/end, invalidate request/ack, aperture, fault, or translation-assist offset can produce memory corruption, stale translations, page faults, or VM timeout recovery.
- Per-VF framebuffer and GPUIOV/XGMI/IOMMU controls are privilege-sensitive. Incorrect programming can break isolation, expose the wrong aperture, or leave a VF with inconsistent memory visibility.
- ATC L2 and L2TLB fault/status/debug registers mix performance, debug, translation, and fault-handling concerns. Misaddressed writes can hide real faults or corrupt ATS/TLB behavior.
- The chunk ends inside the SQ indirect index list. Later indexes after `ixSQ_WAVE_TTMP7` are outside this chunk and must be reconciled by the next chunk before summarizing all SQ indirect coverage.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus runtime GPU coverage:

- Build AMDGPU with GC 12.1.0 support enabled. Missing or renamed macros should surface in files that include `gc_12_1_0_offset.h` and matching mask/default headers.
- Mechanically compare this range against the authoritative GC 12.1.0 register database, verifying every `reg...` offset has the intended `_BASE_IDX` and that `ixSQ_*` indexes are not given base-index companions.
- Cross-check this offset chunk against `gc_12_1_0_sh_mask.h` and `gc_12_1_0_default.h` so field/default definitions reference valid register names.
- Exercise compute dispatch and shader workloads that cover WGS program/user-data/resource/scratch/VMID state, suspend/resume, queue restart/relaunch, and WGS status/error paths.
- Run profiler/performance-counter tests for GE2, GRBMH, PA, SPI, PC, SQ/SQG, SX, TA/TD/TCP, GL1C/GL1XC, CB/DB, RMI, PA_PH, UTCL1, WGS, GL1A, and GL1XA counters, including filter and result-control registers.
- Validate SQ thread trace and wave-state dumps on GC 12 hardware, checking buffer programming, write pointers, halt/status bits, dropped counters, and `ixSQ_*` wave readback fields.
- Run clock-gating, power-gating, suspend/resume, and golden-register tests that cover CGTT/ICG, CAC, DIDT, EDC, and GL1/GL1X power registers.
- Exercise VM bring-up and memory-management tests: context creation/destruction, page-table base/start/end programming, TLB invalidation engines 0-17, fault injection/reporting, dummy-page handling, identity aperture paths, ATS/IOMMU toggles where supported, and page-table walker throttling/debug.
- Exercise SR-IOV or partitioned-GPU validation where available: active function ID, per-VF framebuffer size/offset, host/XGMI apertures, translation bypass, secure/PSP controls, and local framebuffer lock behavior.
- Use register dumps on matching GC 12.1.0 hardware to confirm key block ranges align with the generated comments: WGS around base `0x31a00`/`0x31c00`, shader-engine performance data/select ranges around `0x34000`/`0x36000`, power controls around `0x3c000`, VM/UTCL2 PF/VC ranges around `0xa000`-`0xa5e0`, privileged/PL/HV/PSP ranges around `0x35380`-`0x3fa00`, and SQ indirect indexes from base `0x0`.

## Cross-Chunk Notes

This document is intentionally limited to lines 9894-12404. The first line is a `_BASE_IDX` companion for `regWGS_COMPUTE_PIPELINESTAT_ENABLE`, whose register offset is immediately before the chunk. The chunk also starts after the beginning of the WGS compute address block and ends before the full `gfx_se_sqind` indirect index table is complete. The merge/reconciliation lane should combine this with adjacent chunks before producing the final per-file research for `gc_12_1_0_offset.h`.

### subset-b-002591: lines 12405-12418

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h lines 12405-12418

## Scope

This chunk is the final slice of AMD's generated GC 12.1.0 register-offset header. It covers the tail of the `gfx_se_sqind` indirect shader-queue register namespace and the closing `#endif` for `_gc_12_1_0_OFFSET_HEADER`.

The exact register-offset macros in this range are:

- `ixSQ_WAVE_TTMP8` through `ixSQ_WAVE_TTMP15`, with offsets `0x0274` through `0x027b`.
- `ixSQ_WAVE_M0`, with offset `0x027d`.
- `ixSQ_WAVE_EXEC_LO` and `ixSQ_WAVE_EXEC_HI`, with offsets `0x027e` and `0x027f`.

This source file is hardware metadata for AMDGPU GC 12.1.0 devices. It contains preprocessor constants only; there are no functions, structs, variables, locks, allocation paths, or executable control flow in the requested lines.

## Purpose

The purpose of this chunk is to publish the indirect SQ wave-state indices needed to read selected live wavefront registers on GC 12.1.0 hardware. The `ix` prefix marks these as indirect register indices rather than ordinary `reg*` MMIO offsets. Driver code selects a wave through `regSQ_IND_INDEX`, writes one of these indices into the SQ indirect `INDEX` field, and reads or auto-increments through `regSQ_IND_DATA`.

The covered values describe per-wave architectural/debug state:

- `TTMP8`-`TTMP15`: trap temporary scalar registers visible through the SQ wave debug path.
- `M0`: the per-wave scalar register used by shader instructions for LDS/GDS and address-related operations, exposed for debug collection.
- `EXEC_LO` and `EXEC_HI`: the low and high halves of the wave execution mask, indicating active lanes in the wavefront.

Together with the preceding lines in the same `gfx_se_sqind` block, these constants allow AMDGPU debug and diagnostic paths to capture wave PC, status, allocation, exception, scheduling, trap, and execution-mask state.

## Important APIs, Types, And Macros

The exported interface is a set of untyped C preprocessor constants:

- `ixSQ_WAVE_TTMP8` = `0x0274`
- `ixSQ_WAVE_TTMP9` = `0x0275`
- `ixSQ_WAVE_TTMP10` = `0x0276`
- `ixSQ_WAVE_TTMP11` = `0x0277`
- `ixSQ_WAVE_TTMP12` = `0x0278`
- `ixSQ_WAVE_TTMP13` = `0x0279`
- `ixSQ_WAVE_TTMP14` = `0x027a`
- `ixSQ_WAVE_TTMP15` = `0x027b`
- `ixSQ_WAVE_M0` = `0x027d`
- `ixSQ_WAVE_EXEC_LO` = `0x027e`
- `ixSQ_WAVE_EXEC_HI` = `0x027f`

The main consumer pattern is visible in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.c`. Its `wave_read_ind()` helper writes `regSQ_IND_INDEX` using `SQ_IND_INDEX__WAVE_ID__SHIFT` and `SQ_IND_INDEX__INDEX__SHIFT`, then reads `regSQ_IND_DATA`. `gfx_v12_1_read_wave_data()` uses `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, and `ixSQ_WAVE_M0` from this tail section while building type-4 wave debug data. Nearby helpers such as `wave_read_regs()` use the same indirect mechanism with `SQ_IND_INDEX__AUTO_INCR_MASK` for ranges of per-thread or per-wave registers.

The header is included by multiple GC 12.1.0 driver units, including `gfx_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `imu_v12_1.c`, `gfxhub_v12_1.c`, `soc_v1_0.c`, and `sdma_v7_1.c`. Not every include uses these exact wave offsets, but all depend on the same generated register namespace being synchronized with the matching `gc_12_1_0_sh_mask.h` field definitions and GC 12.1.0 silicon register database.

## Control Flow

This chunk has no direct runtime control flow. Runtime behavior comes from consumers that perform SQ indirect register reads:

1. Driver code selects the target graphics instance/XCC through SOC15 helpers such as `GET_INST(GC, xcc_id)`.
2. For a wave read, the driver writes `regSQ_IND_INDEX` with the target wave ID and one of the `ixSQ_WAVE_*` indices from this header.
3. The hardware SQ indirect path latches that selection.
4. The driver reads `regSQ_IND_DATA`, which returns the selected wave register value.
5. Higher-level debug code appends the value to a wave-state buffer for user-visible diagnostics or GPU debugging.

In `gfx_v12_1_read_wave_data()`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, and `ixSQ_WAVE_M0` are interleaved with other wave-state indices such as `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, allocation registers, exception flags, trap control, and scheduling mode. The function also warns if `simd != 0` because GC 12 encodes SIMD selection through the instance field in the surrounding `select_se_sh` path, not through the local SIMD argument.

## State And Persistence Behavior

These macros do not store software state and do not persist anything by themselves. They identify live hardware wavefront state inside the shader queue:

- `TTMP8`-`TTMP15` reflect trap temporary registers for the selected wave and are meaningful mainly when trap/debug state exists for that wave.
- `M0` reflects the selected wave's scalar `M0` value at the moment of the indirect read.
- `EXEC_LO` and `EXEC_HI` reflect the selected wave's current lane execution mask at the moment of capture.

The values returned through `regSQ_IND_DATA` are transient. They can change as the wave executes, stalls, traps, completes, or is invalidated. Persistence is hardware-defined and tied to wave residency rather than kernel-driver storage. If a selected wave slot is idle or changes between selection and read, consumers must rely on surrounding validity/status fields, such as `ixSQ_WAVE_STATUS` and `ixSQ_WAVE_VALID_AND_IDLE`, to interpret the data.

## Dependencies And Integration Points

This chunk depends on AMD's generated GC 12.1.0 register metadata. It must remain consistent with:

- `gc_12_1_0_sh_mask.h`, which defines bit positions and masks for `regSQ_IND_INDEX`, `regSQ_IND_DATA`, and related GC 12.1.0 registers.
- AMDGPU SOC15 register helpers such as `WREG32_SOC15()` and `RREG32_SOC15()`, which perform the actual MMIO accesses.
- The SQ indirect register protocol, especially the relationship between `regSQ_IND_INDEX`, `SQ_IND_INDEX__WAVE_ID__SHIFT`, `SQ_IND_INDEX__INDEX__SHIFT`, `SQ_IND_INDEX__WORKITEM_ID__SHIFT`, `SQ_IND_INDEX__AUTO_INCR_MASK`, and `regSQ_IND_DATA`.
- GC 12.1.0 wave debug collection in `gfx_v12_1.c`, which uses `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, and `ixSQ_WAVE_M0` directly.
- Cross-version AMDGPU wave debug implementations in `gfx_v12_0.c`, `gfx_v11_0.c`, `gfx_v10_0.c`, and earlier GFX files, which use similarly named `ixSQ_WAVE_*` constants but may differ in exact offsets for some registers.

The path is under a `ceph-client` source mirror, but the file is AMD GPU driver metadata and has no distributed filesystem behavior.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong numeric index can compile cleanly and return the wrong wave register, causing misleading debug dumps or broken GPU fault analysis.
- These offsets are ASIC-specific. Reusing GC 12.1.0 values on another generation can be wrong even when macro names match. For example, nearby generated headers show generation differences for `ixSQ_WAVE_M0` between some GC/GCA families.
- The wave-state data is volatile. Reading `EXEC`, `M0`, or `TTMP` fields without checking wave validity can report stale or irrelevant data from an idle slot.
- Indirect SQ reads require correct selection sequencing. Incorrect wave ID, XCC/instance, shader engine, shader array, or SIMD selection can silently read a different wave than intended.
- The chunk boundary hides the preceding `TTMP0`-`TTMP7`, PC, status, exception, allocation, and scheduling offsets. Whole-file analysis should merge this chunk with the previous `gfx_se_sqind` chunk before making full claims about wave debug coverage.
- Manual edits are high risk because this file is generated from AMD register definitions. Divergence from the authoritative register database or sibling shift/mask header can break low-level diagnostics without producing ordinary compile-time type errors.

## Test Signals

Useful validation signals include:

- Build AMDGPU with GC 12.1.0 support enabled. Missing or renamed macros should fail in `gfx_v12_1.c` and other GC 12.1.0 units that include this header.
- Mechanically compare this tail block against AMD's authoritative GC 12.1.0 register database and adjacent generated headers such as `gc_12_0_0_offset.h` or `gc_11_0_0_offset.h`, while allowing expected ASIC-generation differences.
- Run GPU wave-state/debug dump paths on GC 12.1.0 hardware and verify that `EXEC_LO`, `EXEC_HI`, and `M0` fields appear in the expected order in type-4 wave data.
- Exercise GPU fault, hang, trap, or debug capture flows where active wave masks and scalar state are inspected; incorrect offsets would show implausible execution masks, mismatched PC/status correlation, or unusable trap temporary values.
- Check kernel logs for warnings around wave selection, especially the `simd != 0` warning in the GC 12.1 wave data path, because incorrect selection can make otherwise correct indices appear broken.

## Cross-Chunk Notes

This is the final chunk of `gc_12_1_0_offset.h`. The final per-file research document should combine it with earlier chunks that define the rest of the GC 12.1.0 offset namespace, especially the immediately preceding `gfx_se_sqind` lines containing `ixSQ_WAVE_TTMP0`-`TTMP7`, `ixSQ_WAVE_PC_LO/HI`, wave status, allocation, trap, exception, and scheduling offsets.
