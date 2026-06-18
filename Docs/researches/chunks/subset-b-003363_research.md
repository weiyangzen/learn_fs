# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_sh_mask.h lines 1-2607

## Scope

This chunk covers the opening 2,607 lines of the generated AMD SDMA 4.4.0 shift/mask header. It begins with the include guard and the `sdma0_sdma0dec` address block, then defines bitfield shifts and masks for the public SDMA0 register set, UTCL1 fault/XNACK controls, EDC/RAS counters, performance counters, status/debug registers, and the first queue-context register templates: `GFX`, `PAGE`, `RLC0` through `RLC5`, and the start of `RLC6`.

The file is a C preprocessor register-field map only. It does not define functions, structs, storage, locks, or executable control flow. Its constants are consumed together with `sdma_4_4_0_offset.h` and AMDGPU register helper macros.

## Purpose

The purpose of this header section is to encode the SDMA 4.4.0 hardware ABI at bit granularity. Each field follows the generated AMD naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask.

Consumers use these constants with helpers such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, and `WREG32` to compose writes or decode reads without hard-coding bit positions. The companion offset header supplies register addresses such as `regSDMA0_POWER_CNTL`, `regSDMA0_EDC_COUNTER`, and `regSDMA0_GFX_RB_CNTL`; this header supplies only field layout.

## Important Macro Families

### Global SDMA0 Control, Firmware, Power, and Status

The first section defines fields for SDMA microcode and global control registers:

- `SDMA0_UCODE_ADDR`, `SDMA0_UCODE_DATA`, and `SDMA0_UCODE_CHECKSUM` describe the microcode access and checksum fields.
- `SDMA0_VF_ENABLE` gates virtual-function operation.
- `SDMA0_POWER_CNTL`, `SDMA_POWER_GATING`, `SDMA_PGFSM_CONFIG`, `SDMA_PGFSM_WRITE`, `SDMA_PGFSM_READ`, `SDMA0_POWER_CNTL_IDLE`, `SDMA0_CLK_CTRL`, `SDMA0_CLK_STATUS`, and `SDMA0_ULV_CNTL` expose power gating, clock gating, memory power, idle delay, PGFSM, and ultra-low-voltage status/control fields.
- `SDMA0_CNTL`, `SDMA0_CHICKEN_BITS`, `SDMA0_CHICKEN_BITS_2`, `SDMA0_RD_BURST_CNTL`, `SDMA0_BA_THRESHOLD`, `SDMA0_CRD_CNTL`, and `SDMA0_RELAX_ORDERING_LUT` tune command processing, burst behavior, credits, copy overlap, relaxed ordering, preemption, traps, interrupts, and workarounds.
- `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, `SDMA0_STATUS3_REG`, and `SDMA0_STATUS4_REG` provide detailed idle, FIFO, outstanding request, command, exception, queue, SR-IOV, and polling status fields.

These are integration points for bring-up, reset, suspend/resume, idle detection, power management, queue drain, debugging, and timeout paths.

### Addressing, VM, UTCL1, XNACK, and Invalidation

The UTCL1-related portion defines SDMA virtual-memory and memory-translation status:

- `SDMA0_GB_ADDR_CONFIG` and `SDMA0_GB_ADDR_CONFIG_READ` describe graphics-bank addressing topology fields.
- `SDMA0_UTCL1_CNTL`, `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_RD_STATUS`, and `SDMA0_UTCL1_WR_STATUS` expose translation cache control, read/write queue watermarks, FIFO empty/full states, page fault/null indicators, next-vector fields, merge state, and request-to-L2 idle status.
- `SDMA0_UTCL1_INV0`, `SDMA0_UTCL1_INV1`, and `SDMA0_UTCL1_INV2` encode invalidation command state, timeout handling, VMID vectors, flush type, and invalidation addresses.
- `SDMA0_UTCL1_RD_XNACK*`, `SDMA0_UTCL1_WR_XNACK*`, and `SDMA0_UTCL1_TIMEOUT` capture XNACK addresses, VMID/vector data, XNACK classification, and read/write XNACK timeout limits.
- `SDMA0_UTCL1_PAGE`, `SDMA0_PHYSICAL_ADDR_LO`, and `SDMA0_PHYSICAL_ADDR_HI` describe page fault/request attributes and physical-address reporting.

These fields are relevant when SDMA participates in GPUVM translation, page fault recovery, retry/XNACK handling, invalidation, or address/debug reporting. The header does not encode the protocol sequencing or clear semantics; it only names the fields.

### EDC, RAS, Error, and Diagnostic Counters

The chunk includes the RAS-facing SDMA error counters:

- `CC_SDMA0_EDC_CONFIG` exposes EDC disable control.
- `SDMA0_EDC_COUNTER` packs two-bit single-error-detection counters for `SDMA_MBANK_DATA_BUF0_SED` through `SDMA_MBANK_DATA_BUF15_SED`.
- `SDMA0_EDC_COUNTER2` packs counters for ucode, ring-buffer command, indirect-buffer command, UTCL1, data LUT, split data, memory-write address, and memory-read-return buffers.
- `SDMA0_ERROR_LOG`, `SDMA0_RAS_STATUS`, `SDMA0_EA_DBIT_ADDR_DATA`, and `SDMA0_EA_DBIT_ADDR_INDEX` expose error override/status, ECC/NACK error bits, and double-bit address diagnostic storage.

`amdgpu/sdma_v4_4.c` consumes `SDMA0_EDC_COUNTER` and `SDMA0_EDC_COUNTER2` through `SOC15_REG_FIELD` entries in `sdma_v4_4_ras_fields`. Its RAS path reads those registers per SDMA instance, reports nonzero single-error-detection counts as SDMA uncorrectable errors, and clears the counters by writing zero to both EDC counter registers.

### Performance, Scratch, and Debug Registers

The performance/debug group includes:

- `SDMA0_PERFCNT_PERFCOUNTER0_CFG`, `SDMA0_PERFCNT_PERFCOUNTER1_CFG`, `SDMA0_PERFCNT_PERFCOUNTER_RSLT_CNTL`, `SDMA0_PERFCNT_MISC_CNTL`, `SDMA0_PERFCNT_PERFCOUNTER_LO`, and `SDMA0_PERFCNT_PERFCOUNTER_HI` for event selection, modes, enable/clear bits, triggers, result selection, saturation behavior, counter values, and compare value.
- `SDMA0_F32_CNTL`, `SDMA0_FREEZE`, and `SDMA0_F32_COUNTER` for halting, stepping, resetting, freezing, and observing the internal F32 micro-engine state.
- `SDMA0_SCRATCH_RAM_DATA`, `SDMA0_SCRATCH_RAM_ADDR`, `SDMA0_PUB_DUMMY_REG0` through `SDMA0_PUB_DUMMY_REG3`, and `SDMA0_CONTEXT_GROUP_BOUNDARY` for scratch/dummy/context grouping fields.
- `SDMA0_CE_CTRL` and `SDMA0_ATOMIC_*` for copy-engine and atomic/preop configuration.

These fields support profiling, diagnostics, firmware/micro-engine debugging, and low-level command-engine tuning.

### Queue Context Templates: GFX, PAGE, RLC0-RLC6

From `SDMA0_GFX_RB_CNTL` onward, the chunk defines a repeated queue-context register layout. The complete contexts covered here are `GFX`, `PAGE`, and `RLC0` through `RLC5`; the chunk ends after `SDMA0_RLC6_MIDCMD_DATA3`, so the remainder of the `RLC6` template continues in a later chunk.

Each complete context defines a common set of ring and IB controls:

- `*_RB_CNTL` fields for ring enable, ring size, swap, read-pointer writeback enable/swap/timer, privilege, and VMID.
- `*_RB_BASE`, `*_RB_BASE_HI`, `*_RB_RPTR`, `*_RB_RPTR_HI`, `*_RB_WPTR`, and `*_RB_WPTR_HI` for ring base and read/write pointers.
- `*_RB_WPTR_POLL_CNTL`, `*_RB_WPTR_POLL_ADDR_HI`, and `*_RB_WPTR_POLL_ADDR_LO` for write-pointer polling, polling frequency, idle count, and polling address.
- `*_RB_RPTR_ADDR_HI` and `*_RB_RPTR_ADDR_LO` for read-pointer writeback address and idle status.
- `*_IB_CNTL`, `*_IB_RPTR`, `*_IB_OFFSET`, `*_IB_BASE_LO`, `*_IB_BASE_HI`, `*_IB_SIZE`, and `*_IB_SUB_REMAIN` for indirect-buffer execution state.
- `*_SKIP_CNTL`, `*_CONTEXT_STATUS`, `*_CONTEXT_CNTL` where present, `*_PREEMPT`, and `*_MINOR_PTR_UPDATE` for scheduling, preemption, context switching, and pointer update behavior.
- `*_DOORBELL`, `*_DOORBELL_OFFSET`, `*_DOORBELL_LOG`, and `*_STATUS` for queue doorbell enable/capture, offsets, logged back-end error/data, failed write-pointer updates, and pending updates.
- `*_WATERMARK`, `*_CSA_ADDR_LO`, `*_CSA_ADDR_HI`, `*_AQL_CNTL`, `*_DUMMY_REG`, `*_MIDCMD_DATA0` through `*_MIDCMD_DATA10`, and `*_MIDCMD_CNTL` for queue watermarks, context-save-area addresses, AQL packet handling, dummy storage, and mid-command preemption/resume payloads.

The repeated layout makes it practical for driver code to configure similar queue instances by varying register offsets. It also makes generator or copy/paste errors especially damaging because a wrong suffix can silently program the wrong queue field.

## Control Flow

There is no executable control flow in this header. Runtime control flow is in consumers such as `amdgpu/sdma_v4_4.c` and other AMDGPU SDMA code.

The implied control flow for queue bring-up is:

1. Use the offset header and SDMA instance base computation to locate the target context registers.
2. Program ring base, size, VMID, privilege, swap, writeback, and pointer-polling fields.
3. Program doorbell offset/enable and IB controls if needed.
4. Enable the ring with the `RB_ENABLE` field.
5. During drain, preemption, reset, or timeout handling, read status/context fields and optionally use preempt/freeze/mid-command state fields.

The implied RAS flow in `sdma_v4_4.c` is:

1. For each SDMA instance, calculate the instance register offset from the SDMA0 offsets.
2. Read `regSDMA0_EDC_COUNTER` and `regSDMA0_EDC_COUNTER2`.
3. Extract fields using the masks/shifts from this header.
4. Add nonzero SED values to the uncorrectable-error count and log the field name.
5. Clear counters by writing zero to the EDC counter registers when reset is requested.

## State and Persistence Behavior

This chunk defines hardware register state, not software-owned persistent state. Persistence depends on the SDMA hardware reset domain, firmware policy, SR-IOV mode, power management state, and AMDGPU save/restore paths.

State classes named by this chunk include:

- Programmed engine state: microcode address/data, global control bits, power/clock/ULV fields, burst/credit/order tuning, and PGFSM controls.
- Runtime status: idle bits, FIFO full/empty bits, outstanding request bits, context selected/idle/expired/exception/preempted bits, queue write-pointer update status, and doorbell capture/log state.
- Translation and fault state: UTCL1 read/write status, invalidation state, XNACK addresses/vectors, timeout limits, page attributes, and physical-address report fields.
- Queue state: ring bases, pointers, writeback addresses, polling configuration, IB bases/offsets/sizes, doorbell offsets, CSA addresses, AQL controls, and mid-command save/resume payloads.
- RAS/perf/debug state: EDC counters, RAS status, error log, double-bit diagnostic address storage, performance counter selection/results, scratch RAM, F32 counter, and dummy registers.

The header does not indicate whether a field is read-only, write-one-to-clear, sticky, reset-on-read, or write-zero-to-clear. One known consumer behavior is that `sdma_v4_4.c` clears the two EDC counter registers by writing zero. Other status or control fields require the ASIC programming guide or existing AMDGPU paths for safe access semantics.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/sdma/sdma_4_4_0_offset.h` supplies the matching `reg*` addresses and base indices for these fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c` includes this header directly and uses the EDC counter field macros for SDMA RAS reporting.
- AMDGPU register helpers such as `SOC15_REG_FIELD`, `RREG32`, `WREG32`, `REG_SET_FIELD`, and `REG_GET_FIELD` are the normal mechanism for field extraction and composition.
- SDMA initialization, power management, reset, hang detection, queue scheduling, GPUVM invalidation/fault handling, SR-IOV, debugfs/perf tooling, and RAS reporting are natural consumers of these definitions.
- The SDMA 4.4.0 register layout supports multiple SDMA instances by using SDMA0 offsets plus instance-specific base offsets; the masks in this header are shared across those instances.

## Risks

- Register layout drift: every shift and mask must match SDMA 4.4.0 hardware. A single bad bit definition can corrupt queue setup, VM fault handling, power control, RAS counting, or preemption state.
- Repeated-template mistakes: `GFX`, `PAGE`, and `RLCn` blocks are mechanically similar. A mismatched suffix or mask in one context could silently affect only one queue class.
- Chunk boundary risk: this line range ends in the middle of the `SDMA0_RLC6_*` template. Any merged per-file research must reconcile later chunks before treating RLC6 as complete.
- Ambiguous access semantics: the header exposes masks but not read/write/clear rules. Treating status fields as ordinary writable fields can fail to clear hardware state or clobber adjacent fields.
- Packed counter interpretation: EDC counter fields are two-bit packed values. Incorrect extraction can overcount, undercount, or attribute RAS events to the wrong SDMA internal buffer.
- Queue pointer alignment: several address and pointer fields intentionally mask low bits, for example ring write-pointer poll addresses and IB base addresses. Consumers must pass properly aligned addresses.
- Power and clock controls: misuse of `POWER_CNTL`, `CLK_CTRL`, PGFSM, or ULV fields can leave SDMA inaccessible, prevent idle, or race with firmware-managed power transitions.
- VM/XNACK/invalidation controls: wrong VMID vectors, timeout values, or invalidation address fields can break GPUVM correctness or produce hard-to-debug page fault behavior.
- Doorbell and SR-IOV fields: incorrect doorbell enable/offset or VF controls can route queue updates to the wrong context or expose virtualization isolation bugs.

## Test Signals

Useful validation signals for code consuming this chunk include:

- Compile coverage for `sdma_v4_4.c` and any SDMA 4.4.0 users with no missing or conflicting macro definitions.
- Field composition/extraction checks around representative packed fields: `SDMA0_POWER_CNTL`, `SDMA0_CNTL`, `SDMA0_UTCL1_INV0`, `SDMA0_EDC_COUNTER`, `SDMA0_EDC_COUNTER2`, `SDMA0_GFX_RB_CNTL`, and one `SDMA0_RLCn_RB_CNTL`.
- Hardware or emulator queue bring-up tests that program ring base/size/writeback/doorbell fields, enable the ring, submit an SDMA packet, and verify read/write pointer movement and idle status.
- RAS tests that inject or simulate EDC counter values, confirm `sdma_v4_4.c` reports SDMA uncorrectable counts, and verify reset writes zero to both EDC counter registers for every SDMA instance.
- GPUVM/XNACK tests that exercise SDMA page fault or retry paths and confirm UTCL1 status, invalidation idle, VMID vector, and XNACK address fields decode as expected.
- Suspend/resume, GPU reset, and runtime power tests that confirm programmed queue, power, clock, scratch, EDC, and perf-counter state is either restored or intentionally reinitialized.
- SR-IOV/VF tests that verify `VF_ENABLE`, doorbell capture/logging, active queue ID, and RLC queue context fields remain isolated per virtual function.
