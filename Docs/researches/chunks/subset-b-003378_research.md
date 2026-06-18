# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_2_sh_mask.h lines 1-2560

## Scope

This chunk covers the first 2,560 lines of AMDGPU's generated SDMA0 4.2 shift/mask header. It starts at the license and include guard, covers the `sdma0_sdma0dec` address block, and ends at the `//SDMA0_RLC5_DUMMY_REG` comment. The actual `SDMA0_RLC5_DUMMY_REG` shift and mask definitions continue after this chunk.

The chunk contains 2,125 `#define` entries across roughly 410 register names. It is declarative hardware ABI data only: there are no C functions, structs, variables, allocations, locks, branches, loops, register reads, or register writes in this section.

The covered register families are:

- SDMA0 public/global registers for firmware upload, VM context, SR-IOV/VF state, context-register classification, public-register classification, MMHUB, power, clock, control, status, EDC, atomics, UTCL1, performance counters, GPU IOV violation logging, and debug/dummy registers.
- SDMA0 GFX queue context registers, including ring buffer, indirect buffer, doorbell, context status, preemption, AQL, write-pointer polling, CSA address, and mid-command state.
- SDMA0 PAGE queue context registers with the same ring/IB/doorbell/status/preemption/AQL/mid-command layout as GFX.
- SDMA0 RLC queue context registers for `RLC0` through `RLC4`, each repeating the same queue-control layout.
- The beginning of the `RLC5` queue context register block, through the `SDMA0_RLC5_PREEMPT` definitions and the following `SDMA0_RLC5_DUMMY_REG` marker.

Although the repository path is under a `ceph-client` mirror, this file section is AMD GPU SDMA register metadata. It has no Ceph or distributed-filesystem runtime behavior.

## Purpose

`sdma0_4_2_sh_mask.h` provides symbolic bit positions for SDMA0 4.2 hardware registers. Each hardware field normally appears as a generated pair:

- `SDMA0_<REGISTER>__<FIELD>__SHIFT`, the least-significant bit index of the field.
- `SDMA0_<REGISTER>__<FIELD>_MASK`, the mask for isolating or composing that field in a 32-bit register value.

Consumers pair this mask header with `sdma0_4_2_offset.h`, which supplies the matching `mmSDMA0_*` register offsets. AMDGPU code then uses the macros directly or through helper patterns such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_ENTRY_STR`, `RREG32`, `WREG32`, and SDMA instance-offset wrappers. The offset header tells the driver where a register lives; this header tells it how to interpret or construct each register value.

This header section is also part of the stable ABI between generated ASIC register data, the SDMA v4 driver, KFD queue-management code, firmware-loading paths, debug register dumping, and power/reset flows. The values must match the SDMA0 4.2 hardware specification and the generated offset/default headers.

## Important Macro Families

### Public SDMA0 Control, VM, and SR-IOV Registers

The chunk starts with basic control and virtualization registers:

- `SDMA0_UCODE_ADDR` and `SDMA0_UCODE_DATA` define the microcode upload address/data fields. SDMA v4 firmware-loading paths write the matching offsets while loading engine firmware.
- `SDMA0_VM_CNTL`, `SDMA0_VM_CTX_LO`, `SDMA0_VM_CTX_HI`, and `SDMA0_VM_CTX_CNTL` define VM command, context address, privilege, and VMID fields.
- `SDMA0_ACTIVE_FCN_ID`, `SDMA0_VIRT_RESET_REQ`, and `SDMA0_VF_ENABLE` expose active VF identification, virtual reset request bits, and VF enable state.
- `SDMA0_CONTEXT_REG_TYPE0..3` classify context registers, including GFX ring, IB, doorbell, context, AQL, minor pointer, and mid-command state registers.
- `SDMA0_PUB_REG_TYPE0..3` classify public SDMA registers, including firmware, VM, context type, power, clock, control, status, UTCL1, performance, IOV, and dummy-register groups.

These fields are used to describe register ownership and context/public accessibility as much as ordinary configuration. SR-IOV and VM-related masks are isolation-sensitive because they affect which virtual function or VM context the SDMA engine attributes work to.

### Power, Clock, Engine Control, and Status

The public-control area defines the main SDMA operating controls:

- `SDMA0_MMHUB_CNTL` toggles MMHUB-related behavior.
- `SDMA0_CONTEXT_GROUP_BOUNDARY` names the context group boundary field.
- `SDMA0_POWER_CNTL`, `SDMA0_CLK_CTRL`, and `SDMA_POWER_GATING` define idle, memory power, light-sleep, clock gating, soft-override, automatic clock, interrupt, hysteresis, and finite-state-machine control fields.
- `SDMA0_CNTL` includes trap enablement, semaphore wait interrupt enablement, freeze-on-read-pointer configuration, context-empty interrupt enablement, F32 control, mid-command preemption, auto context-switch enablement, command restart behavior, and semantic version fields.
- `SDMA0_CHICKEN_BITS`, `SDMA0_CHICKEN_BITS_2`, `SDMA0_RD_BURST_CNTL`, `SDMA0_HBM_PAGE_CONFIG`, and `SDMA0_CRD_CNTL` provide hardware workaround/tuning fields for copy mode, burst behavior, HBM page behavior, command processing delay, and memory request credits.
- `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, and `SDMA0_STATUS3_REG` expose activity, outstanding work, blocked/idle status, program counter state, context-empty flags, page fault indicators, MC read/write idle state, command operation status, previous VM command, exception idle state, and queue-id diagnostics.

AMDGPU `sdma_v4_0.c` includes this header and lists many of these status registers in `sdma_reg_list_4_0` for debug collection. The same source uses public power, clock, timeout, page, and queue registers in golden settings, suspend/resume, reset, firmware, interrupt, and ring-control paths.

### EDC, Atomics, Performance, Error, and Debug Registers

Reliability and diagnostic fields include:

- `SDMA0_EDC_CONFIG`, `SDMA0_EDC_COUNTER`, and `SDMA0_EDC_COUNTER_CLEAR`, covering ECC/EDC interrupt enables, injection enables, block ID, error counts by memory/FIFO, and counter clear state.
- `SDMA0_ATOMIC_CNTL`, `SDMA0_ATOMIC_PREOP_LO`, and `SDMA0_ATOMIC_PREOP_HI`, defining atomic request control and pre-operation payload fields.
- `SDMA0_ERROR_LOG`, `SDMA0_EA_DBIT_ADDR_DATA`, and `SDMA0_EA_DBIT_ADDR_INDEX`, exposing error override/status and double-bit error address access.
- `SDMA0_PERFMON_CNTL`, `SDMA0_PERFCOUNTER0_RESULT`, `SDMA0_PERFCOUNTER1_RESULT`, and `SDMA0_PERFCOUNTER_TAG_DELAY_RANGE`, exposing two performance counter selectors, enable/clear bits, count results, tag-delay low/high ranges, and read/write selection.
- `SDMA0_UCODE_CHECKSUM`, `SDMA0_ID`, `SDMA0_VERSION`, `SDMA0_PROGRAM`, `SDMA0_F32_CNTL`, `SDMA0_F32_COUNTER`, `SDMA0_FREEZE`, and `SDMA0_PUB_DUMMY_REG0..3`, providing firmware, identity, version, program/debug, F32, freeze, and scratch-style surfaces.

These masks support debug and health reporting rather than data movement directly. Status and clear fields require careful handling because the mask header does not encode whether a status bit is sticky, read-only, write-one-to-clear, or command-like.

### UTCL1 Translation, Invalidation, and XNACK State

The UTCL1 group describes SDMA address-translation behavior:

- `SDMA0_UTCL1_CNTL` covers redirection, request limiting, stall behavior, inhibit controls, translation action, ATC/VTC behavior, page-break controls, and response mode.
- `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_RD_STATUS`, and `SDMA0_UTCL1_WR_STATUS` expose outstanding read/write watermarks, FIFO usage, credit counts, request IDs, starvation, and invalid request status.
- `SDMA0_UTCL1_INV0`, `SDMA0_UTCL1_INV1`, and `SDMA0_UTCL1_INV2` define invalidate request type, flush type, address, VMID vector, and no-flush VMID vector fields.
- `SDMA0_UTCL1_RD_XNACK0/1` and `SDMA0_UTCL1_WR_XNACK0/1` log read/write XNACK address, VMID, vector, and XNACK state.
- `SDMA0_UTCL1_TIMEOUT` and `SDMA0_UTCL1_PAGE` define read/write XNACK limits and page behavior fields such as VM hole, request type, MTYPE, and PT snoop use.

This is one of the most correctness-sensitive areas in the chunk. It interacts with GPUVM, IOMMU/MMHUB translation, retry/XNACK behavior, page fault diagnosis, and invalidation ordering. A mask error here can misdecode a faulting address or VMID, invalidate the wrong address range, or program translation behavior incorrectly.

### Address Configuration, Ordering, Physical Address, and IOV Violation Logging

Address and ordering registers include:

- `SDMA0_GB_ADDR_CONFIG` and `SDMA0_GB_ADDR_CONFIG_READ`, which describe the number of pipes, banks, shaders, shader engines, tile pipes, pipe interleave size, row size, and related address geometry.
- `SDMA0_RELAX_ORDERING_LUT`, which maps SDMA packet classes such as copy, write, fence, poll memory, conditional execute, atomic, constant fill, PTE/PDE, timestamp, world switch, read-pointer writeback, write-pointer poll, IB fetch, and RB fetch to relaxed-ordering behavior.
- `SDMA0_PHYSICAL_ADDR_LO` and `SDMA0_PHYSICAL_ADDR_HI`, which expose valid/dirty/physical-valid bits and physical address fields.
- `SDMA0_GPU_IOV_VIOLATION_LOG`, which records violation status, multiple-violation state, address, write operation, VF flag, VFID, and initiator ID.
- `SDMA0_ULV_CNTL` and `SDMA0_POWER_CNTL_IDLE`, which define ultra-low-voltage and idle-delay behavior.

These fields integrate with memory-controller address decoding, ordering rules, SR-IOV violation diagnostics, and power-management policy. Relaxed ordering and IOV masks are especially easy to misuse because the fields are packed by command class rather than by a single on/off feature.

### GFX and PAGE Queue Contexts

The `SDMA0_GFX_*` and `SDMA0_PAGE_*` blocks define nearly identical queue context layouts:

- `*_RB_CNTL` has ring enable, ring size, swap enable, read-pointer writeback enable/swap/timer, privilege, and VMID fields.
- `*_RB_BASE`, `*_RB_BASE_HI`, `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, and `*_RB_WPTR_HI` define ring base and read/write pointer state.
- `*_RB_WPTR_POLL_CNTL` and `*_RB_WPTR_POLL_ADDR_{HI,LO}` define write-pointer polling enablement, byte swapping, F32 polling, frequency, idle poll count, and polling address.
- `*_RB_RPTR_ADDR_{HI,LO}` define read-pointer writeback address and idle state.
- `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_{LO,HI}`, `*_IB_SIZE`, and `*_IB_SUB_REMAIN` define indirect-buffer enablement, swapping, inside-IB switching, command VMID, base, pointer, offset, size, and remaining sub-command size.
- `*_SKIP_CNTL`, `*_CONTEXT_STATUS`, `*_DOORBELL`, `*_STATUS`, `*_DOORBELL_LOG`, `*_WATERMARK`, `*_DOORBELL_OFFSET`, `*_CSA_ADDR_{LO,HI}`, `*_PREEMPT`, `*_DUMMY_REG`, `*_RB_AQL_CNTL`, `*_MINOR_PTR_UPDATE`, `*_MIDCMD_DATA0..8`, and `*_MIDCMD_CNTL` define queue diagnostics, doorbell behavior, context-save address, preemption, AQL packet settings, pointer update behavior, and mid-command replay/preemption state.

The GFX queue is the primary SDMA ring used by the graphics driver for DMA copy/fill work. The PAGE queue supports page-related SDMA work. The repeated layout lets code and firmware save, restore, initialize, and inspect queue state with predictable field names, but also makes copy/prefix mistakes difficult to catch by compilation alone.

### RLC0-RLC5 Queue Contexts

`SDMA0_RLC0_*` through `SDMA0_RLC4_*` repeat the same queue context layout as GFX/PAGE. The chunk then begins `SDMA0_RLC5_*` and includes its ring buffer, write-pointer polling, IB, context status, doorbell, status, doorbell log, watermark, doorbell offset, CSA address, IB sub-remaining, and preempt fields. The actual `SDMA0_RLC5_DUMMY_REG` field definitions and later RLC5 mid-command/AQL/minor-pointer fields are outside this chunk.

KFD queue-management code relies on the RLC queue field geometry when constructing SDMA MQDs. For example, v9 MQD setup composes `sdmax_rlcx_rb_cntl` with `SDMA0_RLC0_RB_CNTL__RB_SIZE__SHIFT`, `RB_VMID__SHIFT`, `RPTR_WRITEBACK_ENABLE__SHIFT`, and `RPTR_WRITEBACK_TIMER__SHIFT`, programs doorbell offset with `SDMA0_RLC0_DOORBELL_OFFSET__OFFSET__SHIFT`, and enables inside-IB switching with `SDMA0_GFX_IB_CNTL__SWITCH_INSIDE_IB_MASK`.

RLC queue fields are runtime-critical because they describe user or compute queue state: ring address, pointer writeback address, VMID, doorbell, preemption, context-switch readiness, and pending mid-command state.

## APIs, Types, and Functions

This chunk defines no callable APIs, C types, or functions. Its exported interface is the generated macro namespace. The important "API" contract is naming and value consistency:

- every complete field in this chunk should have a matching `__SHIFT` and `_MASK` macro;
- the macro prefix must match the register name in `sdma0_4_2_offset.h`;
- queue-family prefixes such as `GFX`, `PAGE`, and `RLC0` through `RLC5` must not be mixed accidentally;
- the field values must match the SDMA0 4.2 register database and neighboring generated headers.

The header does not provide reset values, register addresses, access permissions, read/write side effects, polling timeouts, sequencing rules, or ownership rules. Those semantics come from the matching offset/default headers, SDMA v4 driver code, KFD MQD code, firmware, and ASIC documentation.

## Control Flow

There is no executable control flow in this header. Runtime use happens externally and usually follows this pattern:

1. SDMA or KFD code selects a register offset from `sdma0_4_2_offset.h` or a saved MQD field corresponding to the hardware register layout.
2. The caller reads a current register value, starts from a default/golden value, or builds a saved context value.
3. It composes or extracts fields with the `__SHIFT` and `_MASK` macros, often through register helper macros or direct shifts.
4. It writes the value to SDMA hardware, stores it into an MQD/context image, or decodes it for debug/diagnostic output.

The order of definitions follows the generated register database, not an initialization sequence. In real driver flow, firmware upload, golden-register programming, ring setup, doorbell programming, VM configuration, interrupt/trap enablement, power gating, suspend/resume, reset recovery, and KFD queue activation each use different subsets of these masks.

## State and Persistence Behavior

This chunk owns no software state and persists nothing by itself. It names fields whose state lives in SDMA0 hardware registers, firmware-visible context state, or KFD/AMDGPU queue context images.

Represented persistent or semi-persistent configuration state includes firmware address/data programming, VM context address and VMID controls, VF enablement, ring base addresses, ring sizes, read-pointer writeback addresses, doorbell offsets, queue privilege/VMID, IB base/size/control, AQL configuration, relaxed-ordering policy, address geometry, power/clock gating settings, UTCL1 translation controls, performance-counter selection, and RLC/GFX/PAGE context-save addresses.

Represented volatile, status, or command-like state includes SDMA idle/outstanding indicators, program counter/state bits, context status, read/write pointer values, write-pointer poll state, doorbell capture and log data, watermark counts, UTCL1 FIFO/credit/XNACK/invalidation status, error counters, EDC clear bits, performance-counter results, preemption bits, minor pointer update enablement, mid-command valid/split/preempt state, and GPU IOV violation logs.

Reset, suspend/resume, engine reset, function-level reset, SR-IOV transitions, and firmware reloads determine how much of this state persists. The masks alone do not say which fields are read-only, write-one-to-clear, sticky, context-saved, firmware-owned, or safe to change while a queue is active.

## Dependencies and Integration Points

The direct generated-header dependency is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma0/sdma0_4_2_offset.h`, which supplies the matching `mmSDMA0_*` offsets and base indices for the fields defined here.

Important integration points observed in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c`, which directly includes `sdma0_4_2_offset.h` and `sdma0_4_2_sh_mask.h`. It uses SDMA0 register names for debug register lists, golden settings, firmware loading, ring and IB control, read/write pointer handling, doorbells, traps, interrupts, reset, power management, and engine status checks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v9.c` and related KFD MQD managers, which use SDMA RLC/GFX field shifts and masks to build and restore SDMA queue descriptors for compute queues.
- The matching SDMA1 and SDMA2-SDMA7 generated headers, which mirror this structure for other SDMA instances. Multi-instance SDMA code relies on these headers staying aligned where hardware instances share a layout.
- AMDGPU SOC15 register helpers, firmware-loading infrastructure, KFD queue scheduling, GPUVM/MMHUB translation paths, RAS/debug register collection, and SR-IOV handling.

The source is ASIC-generation-specific. Similar `SDMA0_*` names exist in older and newer generated headers, but field locations and available registers can differ. Code must include the SDMA0 4.2 offset/mask pair together rather than mixing masks from a different SDMA generation or instance.

## Risks and Edge Cases

- Bitfield drift is high impact. Wrong shifts or masks can compile cleanly while programming the wrong queue control bit, VMID, doorbell, pointer address, power-gating control, or translation field.
- Register-family prefix mistakes are easy. `GFX`, `PAGE`, and `RLC0` through `RLC5` repeat nearly identical names and layouts; using the wrong prefix can target the wrong queue context.
- Queue enable, ring size, base address, read/write pointer, writeback address, and doorbell fields are core command-submission state. Incorrect masks can hang SDMA, corrupt queue pointers, write back to the wrong memory, or lose doorbell updates.
- VMID, privilege, UTCL1, physical-address, XNACK, and invalidation fields affect memory isolation and fault handling. Misprogramming them can cause stale translations, wrong fault attribution, or access under the wrong VM context.
- SR-IOV fields such as active function ID, VF enable, virtual reset request, and IOV violation logging are virtualization-sensitive. Incorrect decoding can hide isolation faults or reset/report the wrong function.
- Power and clock gating fields are timing-sensitive. Changing masks or using them outside the expected SDMA power sequence can produce intermittent hangs or wake/sleep failures.
- Status and clear fields need hardware-specific semantics. EDC counters, error logs, violation logs, UTCL1 state, doorbell captured bits, and context status may be sticky or side-effectful; generic read-modify-write logic can lose diagnostics.
- Relaxed-ordering LUT bits affect ordering by packet class. Treating the LUT as a single feature toggle can weaken ordering for commands that require stricter behavior.
- The chunk ends at a register boundary marker, not a complete RLC5 block. `SDMA0_RLC5_DUMMY_REG` and the rest of RLC5 continue in the next chunk, so the merge lane must join adjacent reports before describing the full RLC5 context.

## Test Signals

Useful validation signals for this generated header section include:

- Build coverage for `amdgpu/sdma_v4_0.c` and KFD MQD managers that reference `SDMA0_*` field macros, catching renamed or missing generated symbols.
- Generated-header consistency checks against the authoritative SDMA0 4.2 register database: every complete field in this range should have a matching shift/mask pair, and every register should have a matching offset in `sdma0_4_2_offset.h`.
- Compile or static checks that GFX, PAGE, and RLC queue register groups preserve the expected repeated layout where hardware specifies identical fields.
- SDMA firmware-load tests that exercise `UCODE_ADDR`, `UCODE_DATA`, and `UCODE_CHECKSUM` behavior on SDMA v4 hardware.
- SDMA ring smoke tests for copy/fill operations, validating ring base/size, read/write pointer, pointer writeback, IB control, doorbell, and idle/status fields.
- KFD SDMA queue tests that create, checkpoint, restore, and preempt SDMA queues, verifying RLC MQD fields, VMID assignment, doorbell offset, context status, and inside-IB switching.
- GPUVM/MMHUB stress with page faults, invalidations, and XNACK/retry paths to validate UTCL1 status, invalidate, timeout, and XNACK field decoding.
- Suspend/resume, GPU reset, and SR-IOV reset tests to confirm SDMA public and queue-context state is restored or intentionally reinitialized.
- Power-management tests covering idle, clock gating, light sleep, and power gating to catch incorrect `POWER_CNTL`, `CLK_CTRL`, `POWER_CNTL_IDLE`, `ULV_CNTL`, and `SDMA_POWER_GATING` masks.
- Error-injection and diagnostics for EDC, GPU IOV violation, doorbell logging, and UTCL1 fault state, confirming status bits are decoded and cleared according to hardware rules.

## Cross-Chunk Notes

This report covers only lines 1-2560 of the 2,992-line source file. The chunk starts at the top of the header and ends after the `SDMA0_RLC5_PREEMPT` field definitions, with the `SDMA0_RLC5_DUMMY_REG` comment as the final line. The following chunk must cover the remaining RLC5 definitions, later queue/register fields, and the closing include guard before the full-file report is reconciled.
