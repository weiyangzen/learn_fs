# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma7/sdma7_4_2_2_sh_mask.h lines 1-2569

## Scope

This chunk covers the beginning and most of the SDMA7 4.2.2 generated register shift/mask header. The range starts with the license and include guard, then covers the `sdma7_sdma7dec` address block through the `SDMA7_RLC5_MIDCMD_DATA8` field definitions. The next chunk begins with `SDMA7_RLC5_MIDCMD_CNTL`.

The file is a C preprocessor hardware register map. It defines `#define` constants for bit shifts and masks only. It contains no C functions, structs, variables, allocation, locking, runtime branches, or software persistence logic.

## Purpose

The purpose of this chunk is to encode the bit-level ABI for AMD SDMA engine 7 on the 4.2.2 register generation. Each hardware field is represented in the AMD generated style:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.

Consumers combine these definitions with `sdma7_4_2_2_offset.h`, which provides the matching `mmSDMA7_*` register offsets, and with AMDGPU/SOC15 register helpers such as `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY_STR`, `SOC15_REG_GOLDEN_VALUE`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, and `WREG32`. This header supplies field positions and masks; it does not perform MMIO access itself.

## Important Macro Families

### Public SDMA7 Engine Registers

The first portion defines public engine-level SDMA7 controls and status:

- `SDMA7_UCODE_ADDR`, `SDMA7_UCODE_DATA`, and `SDMA7_UCODE_CHECKSUM` describe microcode address/data/checksum access fields.
- `SDMA7_VM_CNTL`, `VM_CTX_LO`, `VM_CTX_HI`, and `VM_CTX_CNTL` describe command and VM context address/control fields, including VMID and privilege bits.
- `SDMA7_ACTIVE_FCN_ID`, `VIRT_RESET_REQ`, and `VF_ENABLE` define SR-IOV/VF identity, reset request, and VF-enable state.
- `SDMA7_CONTEXT_REG_TYPE0` through `TYPE3` and `SDMA7_PUB_REG_TYPE0` through `TYPE3` define register-class bitmaps. These bitmaps enumerate which context/public registers belong to a type group for save/restore, virtualization, diagnostics, or firmware-facing classification.
- `SDMA7_MMHUB_CNTL`, `CONTEXT_GROUP_BOUNDARY`, `GB_ADDR_CONFIG`, and `GB_ADDR_CONFIG_READ` describe MMHUB unit selection and GPU memory tiling/address geometry fields.

Power, clock, and engine behavior are represented by:

- `SDMA7_POWER_CNTL`, with memory power override, light/deep/shutdown sleep enables, and delay fields.
- `SDMA7_CLK_CTRL`, with on-delay, off-hysteresis, reserved bits, and soft clock override bits.
- `SDMA7_CNTL`, with trap, UTC L1, semaphore-wait interrupt, byte-swap, mid-command preemption/world-switch, auto context switch, context-empty, frozen, and IB-preempt interrupt enables.
- `SDMA7_CHICKEN_BITS` and `CHICKEN_BITS_2`, with copy efficiency, stall behavior, write burst tuning, copy overlap, RAW checking, polling retry, QoS, FIFO watermarks, and F32 command delay.

These fields are used by bring-up, golden-register programming, reset, power-management, virtualization, and low-level SDMA scheduling code.

### Status, Diagnostics, RAS, and Performance

The chunk defines several diagnostic/status register layouts:

- `SDMA7_STATUS_REG`, `STATUS1_REG`, `STATUS2_REG`, and `STATUS3_REG` expose engine idle state, ring/IB FIFO fullness, command idle/full state, memory-client idle/stall state, semaphore/interrupt state, command op/status fields, exception idle state, and interrupt queue ID.
- `SDMA7_RB_RPTR_FETCH_HI`, `RB_RPTR_FETCH`, `IB_OFFSET_FETCH`, and `PROGRAM` describe command-fetch observation registers.
- `SDMA7_F32_CNTL`, `FREEZE`, `F32_COUNTER`, and `UNBREAKABLE` expose F32 halt/step/freeze and freeze/preempt state.
- `SDMA7_EDC_CONFIG`, `EDC_COUNTER`, and `EDC_COUNTER_CLEAR` define error-detection enable/interrupt bits, a matrix of single-error-detected counters across SDMA RAM/FIFO structures, and clear controls.
- `SDMA7_ERROR_LOG`, `GPU_IOV_VIOLATION_LOG`, `GPU_IOV_VIOLATION_LOG2`, `EA_DBIT_ADDR_DATA`, and `EA_DBIT_ADDR_INDEX` expose error override/status, virtualization violation address/type/VFID details, and double-bit address data/index capture.
- `SDMA7_PERFMON_CNTL`, `PERFCOUNTER0_RESULT`, `PERFCOUNTER1_RESULT`, and `PERFCOUNTER_TAG_DELAY_RANGE` define performance-counter enable, clear, select, result, and tag-delay range fields.
- `SDMA7_ATOMIC_CNTL` and `ATOMIC_PREOP_*` describe atomic-loop timing, atomic-return interrupt enable, and pre-operation payload words.

These are read mostly for debug, RAS, validation, performance analysis, and reset diagnosis. Some fields are writable configuration or clear controls, but this header does not encode read-only, sticky, write-one-to-clear, or command-on-write semantics.

### UTCL1 Translation, Invalidation, Fault, and XNACK State

The UTCL1 group is the main GPU virtual-memory/fault-facing part of the chunk:

- `SDMA7_UTCL1_CNTL` and `UTCL1_WATERMK` define redo enable/delay, redo watermark, invalidation-ack delay, L2 request credits, virtual-address watermark, and request/page/invalidation/XNACK watermarks.
- `SDMA7_UTCL1_RD_STATUS` and `UTCL1_WR_STATUS` report read/write-side FIFO empty/full state, page fault/null state, L2 idle state, command route/vector state, merge state, and write-pointer polling or write-request FIFO state.
- `SDMA7_UTCL1_INV0`, `INV1`, and `INV2` describe invalidation request control, timeout behavior, invalid-address handling, flush/non-flush idle state, flush type, VMID vectors, and invalidate address high/low fields.
- `SDMA7_UTCL1_RD_XNACK*`, `WR_XNACK*`, and `UTCL1_TIMEOUT` capture XNACK addresses, VMID, vector, XNACK state, and read/write XNACK timeout limits.
- `SDMA7_UTCL1_PAGE` configures VM hole behavior, request type, memory-type usage, and page-table snoop use.

These masks are integration points between SDMA command execution and AMDGPU VM, retry/XNACK, invalidation, and page-fault diagnostics. Wrong fields here can cause misleading fault reports or broken replay/invalidation behavior.

### GFX and PAGE Queue Contexts

The `SDMA7_GFX_*` and `SDMA7_PAGE_*` families define two complete queue-context register layouts. Both contain the same major groups:

- Ring-buffer control: `RB_CNTL`, base/base-hi, read/write pointers, pointer high words, read-pointer writeback address, write-pointer polling address/control, ring size, swap enable, writeback enable/swap/timer, privilege, and VMID.
- Indirect-buffer control: `IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO`, `IB_BASE_HI`, `IB_SIZE`, `IB_SUB_REMAIN`, and `SKIP_CNTL`.
- Queue scheduling/status: `CONTEXT_STATUS`, `STATUS`, `WATERMARK`, `PREEMPT`, `MINOR_PTR_UPDATE`, `DUMMY_REG`, and context-save-area address registers.
- Doorbells: `DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`, including enable/captured, bus-error, data, and aligned offset fields.
- AQL and mid-command state: `RB_AQL_CNTL`, `MIDCMD_DATA0` through `MIDCMD_DATA8`, and `MIDCMD_CNTL` fields for data-valid, copy mode, split state, and allow-preempt.

`SDMA7_GFX_CONTEXT_CNTL` additionally exposes `RESUME_CTX`. These queue-context fields are the core constants used to program and diagnose SDMA rings, IB execution, preemption, doorbell delivery, AQL packet mode, and context switching.

### RLC0 Through RLC5 Queue Contexts

The range covers full `SDMA7_RLC0` through `SDMA7_RLC4` queue-context families and most of `SDMA7_RLC5`, ending at `RLC5_MIDCMD_DATA8`. The RLC queue blocks mirror the same layout as `GFX` and `PAGE`:

- `RLCn_RB_CNTL`, base, pointer, polling, and writeback fields.
- `RLCn_IB_CNTL`, IB base/offset/size/read-pointer fields.
- `RLCn_CONTEXT_STATUS`, doorbell, status, log, watermark, CSA address, IB preempt, AQL, and minor-pointer-update fields.
- `RLCn_MIDCMD_DATA0` through `MIDCMD_DATA8`, with `RLC0` through `RLC4` also including `MIDCMD_CNTL` inside this chunk.

The RLC families are important to KFD/HSA-facing SDMA queues. In `amdgpu_amdkfd_arcturus.c`, SDMA engine base selection includes `mmSDMA7_RLC0_RB_CNTL` for engine 7, using the companion offset header and this register family shape to derive per-queue register offsets.

## Control Flow

There is no executable control flow in this chunk. Its effect is compile-time: code that includes the header gets constants for composing values before writes and decoding values after reads.

The implied runtime flows in consumers are:

1. Select the SDMA7 register offset from the companion offset header.
2. Use a mask/shift pair from this header, usually through AMDGPU register helper macros, to compose or extract a field.
3. Perform the actual register access through SOC15/MMIO helpers.
4. Interpret the resulting hardware state according to the SDMA programming guide and the owning driver sequence.

Examples in this tree include `sdma_v4_0.c`, which includes the SDMA7 offset and mask headers and programs SDMA7 golden register values for `CHICKEN_BITS`, `GB_ADDR_CONFIG`, `GB_ADDR_CONFIG_READ`, and `UTCL1_TIMEOUT`; and `amdgpu_amdkfd_arcturus.c`, which includes the same headers while computing SDMA RLC register bases for engines 0 through 7.

## State and Persistence Behavior

The header owns no software state. All state named here is hardware register state in the SDMA7 block.

Configuration-like state includes microcode access position/data, VF enablement, VM context address/control, power/clock controls, SDMA engine control bits, address-geometry settings, relaxed-ordering policy, UTCL1 invalidation and timeout policy, performance-counter selection, atomic control, ring bases/sizes, pointer writeback/polling addresses, doorbell offsets, CSA addresses, AQL mode, VMID assignment, and queue preemption controls.

Runtime or diagnostic state includes engine idle/full/stall flags, command op/status fields, page fault/null flags, XNACK capture addresses, virtualization violation logs, EDC counters, error logs, physical address capture, doorbell captured/logged data, write-pointer update failure/pending state, context selected/idle/expired/preempted state, mid-command capture data, and performance counter results.

Persistence across GPU reset, suspend/resume, VF reset, or engine reset is hardware- and driver-sequence-specific. The header does not indicate which fields are sticky, reset, restored, read-only, write-one-to-clear, or latched.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register-header ecosystem:

- `sdma7_4_2_2_offset.h` supplies the matching `mmSDMA7_*` addresses and base indexes.
- AMDGPU SOC15 and register helper macros consume `__SHIFT` and `_MASK` definitions to build read/modify/write and decode operations.
- `amdgpu/sdma_v4_0.c` includes this header for SDMA 4.x multi-engine support and SDMA7 golden-register handling.
- `amdgpu/amdgpu_amdkfd_arcturus.c` includes this header for Arcturus KFD SDMA queue/register access, especially RLC queue base calculations.
- KFD/HSA queue management, AMDGPU ring setup, doorbell handling, IB submission, preemption, reset recovery, VM fault handling, SR-IOV, RAS/EDC, performance counters, and power/clock management are the higher-level consumers of these fields.

The SDMA7 mask header should remain paired with its SDMA7 offset header and with sibling SDMA0-SDMA6 4.2.2 headers. The repeated naming is intentional: similar field names exist across engines, but code must use the instance-specific offset namespace when accessing engine 7.

## Risks

- Register layout drift is high impact. A wrong shift or mask can program the wrong ring base, pointer, VMID, doorbell, power bit, interrupt enable, UTCL1 policy, or status-clear bit.
- The file is generated and highly repetitive. `GFX`, `PAGE`, and `RLC0` through `RLC5` blocks are vulnerable to suffix mismatches between register names, field names, and masks.
- The chunk ends mid-family. `SDMA7_RLC5_MIDCMD_CNTL` is outside this range, so reconciliation must merge the following chunk before treating RLC5 mid-command state as complete.
- Many address and offset fields encode alignment in the masks, commonly by starting at bit 2 or bit 5. Consumers that pass raw byte addresses must preserve the alignment rules.
- Doorbell and pointer-polling fields are scheduling-sensitive. Incorrect enable, offset, poll address, or captured/log interpretation can cause missed submissions or stale queue state.
- UTCL1 invalidation, XNACK, and page fields are VM-sensitive. Misprogramming can break fault recovery, replay, invalidation, or diagnostic accuracy.
- Power, clock, relaxed-ordering, chicken, and QoS fields can affect stability and ordering. Blind read/modify/write operations must preserve reserved bits.
- EDC, error, violation, and status fields may be sticky or clear-on-write. The masks alone are not enough to decide safe clearing behavior.

## Test and Validation Signals

Useful validation for consumers of this chunk includes:

- Build AMDGPU with SDMA 4.x and Arcturus/KFD support enabled to catch missing or renamed SDMA7 macros.
- Boot on hardware with SDMA7 4.2.2 registers and verify SDMA engine 7 discovery, golden-register programming, and idle/status reads.
- Exercise SDMA copy/fill workloads on GFX, PAGE, and RLC queues; verify ring base/size, read/write pointer movement, pointer writeback, doorbells, and queue idle transitions.
- Run KFD/HSA workloads that use RLC SDMA queues and AQL mode; validate RLC base calculation, queue VMID, AQL packet size/step, doorbell offset, and context status.
- Test IB submission and preemption paths, checking `IB_*`, `PREEMPT`, `CONTEXT_STATUS`, and mid-command data/control behavior during reset or timeslicing.
- Run VM fault, invalidation, and XNACK/retry scenarios where available; confirm UTCL1 status, captured address/VMID/vector, timeout, and page-state decoding.
- Query RAS/EDC and error logs under stress or fault injection; verify counter decoding, clear behavior, IOV violation reporting, and double-bit address capture.
- Validate suspend/resume, GPU reset, VF reset, and power-management paths for restored or intentionally reinitialized power, clock, VM, ring, doorbell, and UTCL1 state.
- Use performance-counter tests to program event selects, enable/clear counters, and confirm result registers change under SDMA traffic.
