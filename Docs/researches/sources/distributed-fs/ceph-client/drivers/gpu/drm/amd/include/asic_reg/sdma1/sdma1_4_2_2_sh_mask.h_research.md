# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003381`: lines 1-2569, `Docs/researches/chunks/subset-b-003381_research.md`
- `subset-b-003382`: lines 2570-2956, `Docs/researches/chunks/subset-b-003382_research.md`

## Chunk Research

### subset-b-003381: lines 1-2569

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_sh_mask.h lines 1-2569

## Scope

This chunk covers the first 2569 lines of the generated SDMA1 4.2.2 shift/mask header for the `sdma1_sdma1dec` address block. The complete source file has 2956 lines; this chunk starts at the license/header guard and ends at `SDMA1_RLC5_MIDCMD_DATA8__DATA8_MASK`. The remaining `RLC5_MIDCMD_CNTL` and later RLC queue definitions continue in the next chunk.

The chunk contains only C preprocessor definitions. It defines 2123 `#define` lines in the covered range, almost entirely paired `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants. There are no functions, structs, global variables, allocations, or executable statements in this range.

## Purpose

This header is the bitfield map for SDMA engine 1 on the 4.2.2 register layout used by Arcturus-generation AMDGPU paths. Its job is to let driver code compose and decode SDMA1 hardware register values without hard-coded bit numbers. The matching `sdma1_4_2_2_offset.h` file supplies register offsets such as `mmSDMA1_RLC5_MIDCMD_DATA8`; this file supplies the field positions and masks inside those 32-bit registers.

Consumers generally use these constants through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and `SOC15_REG_OFFSET`. The semantics are hardware-defined: the macros describe bit layout, while the owning SDMA/KFD code decides when to write, poll, clear, or preserve fields.

## Important Macro Families

### Global SDMA1 Control and Virtualization

The opening section maps engine-wide control and virtualization-facing registers:

- `SDMA1_UCODE_ADDR` and `SDMA1_UCODE_DATA` expose the microcode address/data access window.
- `SDMA1_VM_CNTL`, `SDMA1_VM_CTX_LO`, `SDMA1_VM_CTX_HI`, and `SDMA1_VM_CTX_CNTL` define command, address, privilege, and VMID fields for SDMA virtual-memory context handling.
- `SDMA1_ACTIVE_FCN_ID`, `SDMA1_VIRT_RESET_REQ`, and `SDMA1_VF_ENABLE` describe PF/VF selection, reset request bits, VF ID fields, and VF enable state.
- `SDMA1_CONTEXT_REG_TYPE0..3` and `SDMA1_PUB_REG_TYPE0..3` are register type/visibility bitmaps. They group public and context registers for firmware, virtualization, or context-save/restore policy rather than configuring one queue directly.

These definitions matter for SR-IOV or KFD contexts because wrong masks can select the wrong VMID/VF, expose the wrong registers to a context image, or mishandle virtual reset bits.

### Public Engine Configuration and Status

The public SDMA1 register fields cover power, clocking, engine control, addressing, queue fetching, status, atomics, UTCL1, and performance counters:

- `SDMA1_MMHUB_CNTL` selects the MMHUB unit ID.
- `SDMA1_POWER_CNTL`, `SDMA1_CLK_CTRL`, `SDMA1_POWER_CNTL_IDLE`, and `SDMA1_ULV_CNTL` define memory power modes, clock on/off hysteresis, idle delays, soft clock overrides, and ultra-low-voltage interrupt/status bits.
- `SDMA1_CNTL` controls trap, UTC L1, semaphore wait interrupt, data/fence swapping, mid-command preemption/world switch, automatic context switch, and context-empty/frozen/IB-preempt interrupts.
- `SDMA1_CHICKEN_BITS`, `SDMA1_CHICKEN_BITS_2`, `SDMA1_GB_ADDR_CONFIG`, and `SDMA1_GB_ADDR_CONFIG_READ` encode copy-engine tuning, burst/watermark behavior, QoS, and graphics-bank address configuration.
- `SDMA1_RB_RPTR_FETCH*`, `SDMA1_IB_OFFSET_FETCH`, `SDMA1_PROGRAM`, `SDMA1_RD_BURST_CNTL`, `SDMA1_HBM_PAGE_CONFIG`, and `SDMA1_SEM_WAIT_FAIL_TIMER_CNTL` cover command-stream fetch offsets, burst sizes, page size, and semaphore timeout behavior.
- `SDMA1_STATUS_REG`, `SDMA1_STATUS1_REG`, `SDMA1_STATUS2_REG`, and `SDMA1_STATUS3_REG` expose idle, FIFO, packet-ready, memory-request, semaphore, interrupt, copy-engine, command-op, queue-id, and exception status fields.
- `SDMA1_FREEZE`, `SDMA1_F32_CNTL`, `SDMA1_F32_COUNTER`, `SDMA1_PHASE0_QUANTUM`, `SDMA1_PHASE1_QUANTUM`, and `SDMA1_PHASE2_QUANTUM` map freeze/preempt controls, F32 halt/step/counter state, and scheduling quantum fields.
- `SDMA1_EDC_CONFIG`, `SDMA1_EDC_COUNTER`, and `SDMA1_EDC_COUNTER_CLEAR` define ECC/EDC enable, interrupt, many single-error-detected counter bits, and a clear trigger.
- `SDMA1_ATOMIC_CNTL`, `SDMA1_ATOMIC_PREOP_LO`, and `SDMA1_ATOMIC_PREOP_HI` define atomic loop timing, return interrupt enable, and 64-bit pre-op payload storage.
- `SDMA1_PERFMON_CNTL`, `SDMA1_PERFCOUNTER0_RESULT`, `SDMA1_PERFCOUNTER1_RESULT`, and `SDMA1_PERFCOUNTER_TAG_DELAY_RANGE` expose two selectable performance counters and range filtering.
- `SDMA1_GPU_IOV_VIOLATION_LOG` and `SDMA1_GPU_IOV_VIOLATION_LOG2` record GPU IOV violation status, address, operation type, VF/VFID, and initiator ID.

This group supplies diagnostic and control bits used by bring-up, reset, interrupt, power-management, and error-handling paths.

### UTCL1, Page Fault, Invalidation, and XNACK Fields

The `SDMA1_UTCL1_*` group is the SDMA engine's L1 translation/cache interface:

- `SDMA1_UTCL1_CNTL` defines redo enable/delay/watermark, invalidation-ack delay, L2 request credits, and virtual-address watermarks.
- `SDMA1_UTCL1_WATERMK` defines request, page-request, invalidation-request, and XNACK watermarks.
- `SDMA1_UTCL1_RD_STATUS` and `SDMA1_UTCL1_WR_STATUS` expose read/write-side FIFO empty/full state, page fault/null state, L2 idle state, CE/F32 routing state, merge state, write-pointer polling, and related status.
- `SDMA1_UTCL1_INV0..2` define invalidation controls and address/VMID vectors, including flush/non-flush idle bits and invalidation address pieces.
- `SDMA1_UTCL1_RD_XNACK0/1`, `SDMA1_UTCL1_WR_XNACK0/1`, and `SDMA1_UTCL1_TIMEOUT` define XNACK address/VMID/vector/status and read/write XNACK timeout limits.
- `SDMA1_UTCL1_PAGE` defines VM hole, request type, MTYPE, and page-table snoop fields.

These fields are important for page fault, retry, invalidation, and GPU virtual-memory behavior. They are status- and timing-heavy, so software must treat them according to the hardware programming guide rather than inferring write semantics from the names alone.

### Queue Register Blocks: GFX, PAGE, and RLC0-RLC5

From `SDMA1_GFX_RB_CNTL` onward, the chunk defines repeated queue-context register layouts. The same field pattern appears for:

- `SDMA1_GFX_*`, the graphics SDMA queue block.
- `SDMA1_PAGE_*`, the page/VM SDMA queue block.
- `SDMA1_RLC0_*` through `SDMA1_RLC5_*`, six RLC queue blocks covered in this chunk.

Each queue block includes the same major register families:

- Ring buffer control: `RB_CNTL` fields for `RB_ENABLE`, `RB_SIZE`, swap enable, read-pointer writeback enable/swap/timer, `RB_PRIV`, and `RB_VMID`.
- Ring buffer addresses and pointers: `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_HI`, and `RB_RPTR_ADDR_LO`. Low address fields are aligned, with low bits masked out where required.
- Write-pointer polling: `RB_WPTR_POLL_CNTL` and `RB_WPTR_POLL_ADDR_*` define enable/swap/F32 poll controls, frequency, idle poll count, and poll address.
- Indirect buffer controls: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, and `IB_SIZE` define enable, swap, inside-IB switch, command VMID, aligned IB address, offset, and size.
- Context and doorbell state: `SKIP_CNTL`, `CONTEXT_STATUS`, `DOORBELL`, `STATUS`, `DOORBELL_LOG`, `DOORBELL_OFFSET`, `CSA_ADDR_LO`, `CSA_ADDR_HI`, and `IB_SUB_REMAIN` expose selection, idle, expired, exception, context-switch, preempted, doorbell enable/capture/log, queue status, watermarks, and context-save-area addresses.
- Preemption and pointer update: `PREEMPT` and `MINOR_PTR_UPDATE` provide IB preemption and controlled pointer update bits.
- AQL and mid-command state: `RB_AQL_CNTL`, `MIDCMD_DATA0..8`, and `MIDCMD_CNTL` define AQL enable/packet sizing, packet step, saved mid-command payload words, data-valid state, copy mode, split state, and preemption allowance.

The chunk ends immediately after the data field for `SDMA1_RLC5_MIDCMD_DATA8`; the corresponding `SDMA1_RLC5_MIDCMD_CNTL` and RLC6/RLC7 blocks are outside this work item.

## Important APIs, Types, and Functions

This chunk itself defines no APIs in the C function or type sense. The important interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset used when encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the field in the 32-bit register value.

The primary local consumer found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c`, which includes `sdma1/sdma1_4_2_2_offset.h` and `sdma1/sdma1_4_2_2_sh_mask.h` alongside the matching SDMA0 and SDMA2-SDMA7 headers. That code computes engine-specific RLC register bases with `SOC15_REG_OFFSET`, then programs or dumps RLC queue registers through the common SDMA register layout.

Even when the direct code path shown there mostly uses SDMA0-named offsets/masks after deriving an engine-relative base, the SDMA1 mask header is still part of the per-engine generated register set and must stay consistent with the SDMA1 offset file and the sibling SDMA engine headers.

## Control Flow and State Behavior

There is no runtime control flow in this header. It affects compiled driver control flow indirectly by defining which bits are set, cleared, tested, or preserved by C code.

Representative runtime flows that depend on these layouts include:

- Queue load: disable `RB_ENABLE`, wait until `CONTEXT_STATUS.IDLE` is observed, program doorbell offset/enabled state, set read/write pointers, install ring base/writeback addresses, then re-enable `RB_ENABLE`.
- Queue dump: iterate contiguous queue register ranges from `RB_CNTL` through doorbell/status/CSA/IB-subremain/minor-pointer/mid-command registers and record raw values for diagnostics.
- Fault and retry handling: read UTCL1 status, invalidation, page, XNACK, and timeout fields to understand translation retry/fault state.
- Power and reset handling: write or poll global power, clock, freeze, preempt, EDC, IOV violation, and status fields during bring-up, reset, or error recovery.

The persistent state represented by these macros lives in hardware registers, not in the header. Some fields are configuration state that persists until reset or reprogramming, such as RB base addresses, VMID, RB size, doorbell offset, AQL control, power/clock settings, and UTCL1 watermarks. Other fields are live or sticky status, such as idle bits, FIFO empty/full indicators, page fault/null state, XNACK state, doorbell captured/log values, EDC counters, IOV violation logs, and preemption/frozen status.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_offset.h` provides SDMA1 register offsets and base indices. Its address block starts at base address `0x6180`, and it maps the same names used here, including RLC5 offsets through `mmSDMA1_RLC5_MIDCMD_DATA8` at `0x0330`.
- Sibling SDMA engine headers (`sdma0` through `sdma7`) provide equivalent per-engine layouts for Arcturus multi-SDMA support.
- Common AMDGPU helpers (`REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `SOC15_REG_OFFSET`) consume the masks and shifts.
- KFD/AMDGPU SDMA queue management uses the queue block fields through MQD-backed values, doorbell programming, pointer updates, context status polling, and register dumps.
- GPU VM/MMHUB paths interact with the VM context and UTCL1/page/XNACK fields.
- Power, reset, diagnostics, virtualization, and SR-IOV/IOV paths interact with the public status, power, EDC, freeze, active function, VF enable/reset, and violation-log fields.

The header must be included as a matched pair with the corresponding SDMA1 4.2.2 offset header. Mixing masks from `sdma1_4_2_2_sh_mask.h` with nearby variants such as `sdma1_4_2_sh_mask.h`, `sdma1_4_0_sh_mask.h`, or `sdma/sdma_4_4_0_sh_mask.h` risks field drift even when many names look identical.

## Risks

- Bitfield drift is high impact. A wrong queue mask can program the wrong RB size, VMID, pointer, doorbell, CSA address, IB address, or AQL field and break SDMA command execution.
- Repeated queue blocks are copy-sensitive. GFX, PAGE, and RLC0-RLC5 share nearly identical layouts, so a generated naming or offset mismatch can silently affect only one queue instance.
- Address alignment masks must be preserved. Fields such as `RB_RPTR_ADDR_LO`, `DOORBELL_OFFSET`, `CSA_ADDR_LO`, and `IB_BASE_LO` intentionally mask low bits; incorrect handling can generate misaligned hardware addresses.
- Polling/status bits are not ordinary software booleans. `CONTEXT_STATUS.IDLE`, FIFO status, page fault, XNACK, EDC, doorbell captured/log, frozen/preempted, and violation-log fields may have hardware-specific clear or latch behavior.
- Virtualization fields are privilege-sensitive. `ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, `VF_ENABLE`, VMID, and GPU IOV violation log masks must not be cross-wired across PF/VF contexts.
- UTCL1/XNACK fields affect GPU VM fault/retry behavior. Bad masks can hide page faults, misidentify a VMID/vector, set bad invalidation controls, or produce unbounded retry/timeout behavior.
- This chunk ends mid-file. A complete per-file report must reconcile this document with the following chunk for `RLC5_MIDCMD_CNTL`, RLC6/RLC7, and any trailing header closure.

## Test and Validation Signals

Useful validation is mostly compile-time plus hardware/driver behavior:

- Build AMDGPU/KFD code that includes the SDMA1 4.2.2 offset and mask headers; this catches renamed, missing, or duplicate macros.
- Run KFD SDMA queue load/unload tests on Arcturus-class hardware and verify RLC queues become idle before programming, then execute after `RB_ENABLE` is restored.
- Exercise doorbell and write-pointer paths, including user write-pointer polling and `MINOR_PTR_UPDATE`, and verify no stuck `WPTR_UPDATE_PENDING` or update-fail counts.
- Dump SDMA RLC registers through the KFD diagnostic path and confirm the register count/ranges align with `RB_CNTL` through `MIDCMD_CNTL` for each queue.
- Run SDMA copy/fill/IB/AQL workloads across SDMA engine 1 and multiple RLC queues to catch RB, IB, VMID, and doorbell field mistakes.
- Exercise GPU VM fault/retry scenarios and validate UTCL1 read/write status, page fault/null, invalidation, XNACK address/VMID/vector, and timeout decoding.
- Validate reset and preemption flows by checking `FREEZE`, `PREEMPT`, `CONTEXT_STATUS`, and mid-command save/restore fields during queue eviction or timeout recovery.
- Check power-management and clock-gating behavior with `POWER_CNTL`, `CLK_CTRL`, `POWER_CNTL_IDLE`, and `ULV_CNTL` fields under suspend/resume and idle workloads.
- Use ECC/EDC and IOV diagnostics where supported to confirm `EDC_COUNTER`, `EDC_COUNTER_CLEAR`, `GPU_IOV_VIOLATION_LOG`, and `GPU_IOV_VIOLATION_LOG2` decode expected hardware events.

### subset-b-003382: lines 2570-2956

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma1/sdma1_4_2_2_sh_mask.h lines 2570-2956

## Scope

This chunk is the tail of the generated AMD SDMA1 4.2.2 shift/mask header. It contains C preprocessor constants only: `__SHIFT` bit positions and `_MASK` field masks for SDMA1 RLC queue registers. The range starts with the final field definitions for `SDMA1_RLC5_MIDCMD_CNTL`, then covers complete repeated register-field blocks for `SDMA1_RLC6_*` and `SDMA1_RLC7_*`, and ends with the file's closing `#endif`.

The file has no functions, structs, storage, locking, callbacks, or direct MMIO access. Its purpose is to describe the bit geometry of hardware registers; companion offset headers provide register addresses, and AMDGPU/KFD code performs the reads and writes.

## Purpose and Register Families

The macros describe the SDMA1 engine's RLC queue slots 6 and 7 on ASICs using the 4.2.2 SDMA register layout, plus the end of queue slot 5 mid-command state. Each RLC queue block exposes the same families of fields:

- Ring-buffer control: `RB_ENABLE`, `RB_SIZE`, ring swap flags, read-pointer writeback enable/swap/timer, privileged mode, and `RB_VMID`.
- Ring-buffer base and pointers: low/high base address fields, read pointer, write pointer, and read-pointer writeback address fields.
- Write-pointer polling: polling enable, swap, F32 polling enable, frequency, idle poll count, and polling address low/high fields.
- Indirect buffer state: IB enable/swap, switch-inside-IB, command VMID, IB read pointer, offset, base low/high, size, and remaining sub-IB size.
- Queue status and control: skip count, context status bits, doorbell enable/captured status, write-pointer update status, doorbell log, watermark limits, doorbell offset, context-save area address, preempt request, dummy register, AQL control, minor pointer update, and mid-command data/control registers.

The repeated `RLC6` and `RLC7` macro names identify two independent queue contexts in the SDMA1 engine. The layout matches nearby `RLC0`-`RLC5` blocks and equivalent SDMA0/SDMA2-SDMA7 generated headers, allowing generic queue code to compute an RLC register offset from queue id.

## Important APIs, Types, and Macros

This header's public interface is the AMD register-field macro convention:

- `SDMA1_RLC<n>_<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit number for a field.
- `SDMA1_RLC<n>_<REGISTER>__<FIELD>_MASK` gives the already-shifted 32-bit field mask.
- The corresponding register addresses are in `sdma1_4_2_2_offset.h` as `mmSDMA1_RLC6_*` and `mmSDMA1_RLC7_*`.

The notable fields in this chunk include `RB_ENABLE`, `RB_SIZE`, `RB_VMID`, `RPTR_WRITEBACK_*`, `DOORBELL__ENABLE`, `DOORBELL_OFFSET__OFFSET`, `CONTEXT_STATUS__IDLE`, `PREEMPT__IB_PREEMPT`, `RB_AQL_CNTL__AQL_ENABLE`, and `MIDCMD_CNTL` fields for valid mid-command data, copy mode, split state, and preemption allowance.

The direct in-tree consumer of this exact header is `amdgpu_amdkfd_arcturus.c`, which includes all `sdma0` through `sdma7` 4.2.2 offset and shift/mask headers. The Arcturus KFD path uses `struct v9_sdma_mqd` queue descriptors and generic RLC0-relative register programming: `get_sdma_rlc_reg_offset()` selects the SDMA engine base from `mmSDMA1_RLC0_RB_CNTL` for engine 1, then adds `queue_id * (mmSDMA0_RLC1_RB_CNTL - mmSDMA0_RLC0_RB_CNTL)`. Therefore these `RLC6` and `RLC7` register definitions correspond to queue ids 6 and 7 even when the code uses RLC0 field names for common layout operations.

## Control Flow and Data Flow

There is no executable control flow in the header. Runtime use is indirect:

1. KFD/AMDGPU builds an MQD for an SDMA queue, including ring buffer base, size, VMID, read/write pointers, doorbell offset, and writeback addresses.
2. `kgd_arcturus_hqd_sdma_load()` computes the engine/queue register offset, disables the queue by clearing `RB_ENABLE`, waits until `CONTEXT_STATUS__IDLE` is set, writes doorbell and pointer registers, toggles `MINOR_PTR_UPDATE` while synchronizing the write pointer, writes base and read-pointer writeback addresses, then sets `RB_ENABLE`.
3. `kgd_arcturus_hqd_sdma_dump()` walks the RLC register windows, including the mid-command data/control range described by this chunk, for diagnostics.
4. `kgd_arcturus_hqd_sdma_is_occupied()` reads the queue's `RB_CNTL` and tests `RB_ENABLE`.
5. `kgd_arcturus_hqd_sdma_destroy()` clears `RB_ENABLE`, waits for `CONTEXT_STATUS__IDLE`, clears the doorbell register, re-enables the ring control register, and saves read-pointer state back into the MQD.

For queue ids 6 and 7 on SDMA1, the same flow lands on the `mmSDMA1_RLC6_*` or `mmSDMA1_RLC7_*` address blocks. Field layout consistency is what makes the RLC0-relative implementation valid.

## State and Persistence

The header itself has only compile-time constants and no persistent software state.

The hardware registers described by the masks hold live queue state:

- Ring-buffer base, size, VMID, privilege, and enable bits define whether the queue can fetch packets and under which VM context.
- Read/write pointers and pointer writeback address fields synchronize software, hardware, and memory-visible queue progress.
- Doorbell offset and doorbell enable/captured bits connect CPU/KFD queue signaling to the hardware queue.
- `CONTEXT_STATUS` bits expose selected, idle, expired, exception, context-switch, preempted, and preempt-disable states used by load/destroy/reset flows.
- IB and mid-command registers describe in-flight indirect-buffer execution and partial command state that may need to be dumped or restored across preemption/debug paths.
- CSA address fields identify context-save storage for queue state.
- AQL fields configure HSA-style packet processing for queues that use AQL semantics.

Persistence across reset, suspend/resume, queue teardown, and process eviction is controlled by AMDGPU/KFD and hardware firmware. This header only defines how software should address individual fields.

## Dependencies and Integration Points

This chunk depends on the generated AMD register database:

- `sdma1_4_2_2_offset.h` provides the matching `mmSDMA1_RLC6_*` and `mmSDMA1_RLC7_*` register offsets.
- Other generated `sdmaN_4_2_2_sh_mask.h` files mirror the same queue layout for sibling SDMA engines.
- AMDGPU register helpers such as `REG_SET_FIELD`, `RREG32`, `WREG32`, and `SOC15_REG_OFFSET` consume the generated constants indirectly through KFD and SDMA engine code.
- `amdgpu_amdkfd_arcturus.c` integrates this register layout with KFD MQD load, dump, occupancy, and destroy operations for Arcturus-class devices.
- `v9_sdma_mqd` is the software persistence format that stores the register images later written into the RLC queue windows.

The chunk closes the header guard, so merge/reconciliation should treat it as the final segment for the file.

## Risks and Edge Cases

- The chunk begins in the middle of the `RLC5_MIDCMD_CNTL` block. The final file-level research should reconcile those first RLC5 lines with the preceding chunk.
- Repeated `RLC6` and `RLC7` blocks are copy/generator sensitive. A wrong prefix, shift, or mask could affect only high-numbered SDMA queues and escape lower-queue testing.
- The RLC0-relative programming path assumes every queue block has identical spacing and compatible field layout. Divergence in `RLC6` or `RLC7` would break queue ids 6 and 7 even if direct macro references are rare.
- Address fields have alignment masks: doorbell offset and CSA/RPTR/poll low addresses use low-bit-zero masks, while IB base low starts at bit 5. Callers must not treat these as arbitrary full-width values.
- Full-width pointer and mid-command data masks use `0xFFFFFFFFL`; code should avoid signed arithmetic assumptions and preserve high/low word ordering.
- Queue enable/disable and idle polling are synchronization-sensitive. Incorrect `RB_ENABLE` or `CONTEXT_STATUS__IDLE` masks can cause timeout, queue corruption, or teardown while hardware is still active.
- Doorbell enable/captured and doorbell log fields are externally visible signaling state. Bad masks can make a queue miss submissions or report misleading backend errors.
- Preemption and mid-command state fields are relevant to context switching and diagnostics. Wrong `MIDCMD_CNTL` masks can misinterpret partially executed command state.

## Test and Validation Signals

Useful validation signals are mostly compile-time plus hardware/KFD integration:

- Build AMDGPU with Arcturus/KFD support so the 4.2.2 SDMA1 offset and shift/mask headers are included and macro names are validated.
- Compare this chunk with `sdma1_4_2_2_offset.h` to confirm every RLC6/RLC7 address has matching field definitions and expected register spacing.
- Run KFD SDMA queue creation and destruction with SDMA1 queue ids 6 and 7, checking that load waits for idle, programs doorbells and pointers, enables the ring, and teardown returns to idle without `-ETIME`.
- Use queue dump paths to verify RLC6/RLC7 register windows include RB, status, CSA, preempt, AQL, minor pointer update, and mid-command registers in the expected order.
- Exercise user write-pointer updates, read-pointer writeback, doorbell submission, and AQL packet queues to catch alignment or mask errors.
- Test preemption, process eviction, GPU reset, and suspend/resume scenarios so context status, CSA, IB, and mid-command fields are observed under non-idle conditions.
- Cross-check against sibling SDMA engine 4.2.2 headers and older `sdma1_4_2` layouts for unintended generator drift, while treating the ASIC register specification as authoritative.
