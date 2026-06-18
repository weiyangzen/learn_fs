# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 1-2578

## Purpose

This chunk is generated AMD GC 11.5.0 register bitfield metadata. It contains no executable C code; it exports `#define` constants for hardware register field shifts and masks. Driver code combines these constants with the matching register-offset header and AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to compose and decode 32-bit MMIO register values.

The range covers the beginning of `gc_11_5_0_sh_mask.h`. It opens the include guard, defines the entire `gc_sdma0_sdma0dec` address block, and then starts the `gc_sdma0_sdma0hypdec` block. Functionally, this is the SDMA0 register layout for GC 11.5.0: global SDMA control/status, microcode version/checksum, power and clock-gating control, page/TLB/XNACK fault reporting, EDC/ECC diagnostics, queue reset/status, and the repeated queue register layout for SDMA0 queues 0 through 7. Although this repository path is under `ceph-client`, the file is AMD GPU driver hardware metadata, not filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, allocations, locks, or direct MMIO operations in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the in-register field mask.
- The macros describe fields only; callers need the companion offset definitions to know which MMIO address to access.

Major register groups in this chunk:

- Global SDMA0 control and identity: `SDMA0_DEC_START`, `SDMA0_F32_MISC_CNTL`, `SDMA0_UCODE_VERSION`, `SDMA0_GLOBAL_TIMESTAMP_LO/HI`, `SDMA0_POWER_CNTL`, `SDMA0_CNTL`, `SDMA0_CNTL1`, `SDMA0_ID`, and `SDMA0_VERSION`. These fields cover engine start, F32 wakeup, firmware version, timestamps, light-sleep/deep-sleep control, interrupt enables, byte-swap behavior, preemption, page-fault/null/retry timeout interrupts, and write-pointer polling frequency.
- Workaround, performance, and memory-layout controls: `SDMA0_CHICKEN_BITS`, `SDMA0_CHICKEN_BITS_2`, `SDMA0_GB_ADDR_CONFIG`, `SDMA0_GB_ADDR_CONFIG_READ`, `SDMA0_TILING_CONFIG`, `SDMA0_HASH`, `SDMA0_BA_THRESHOLD`, `SDMA0_CRD_CNTL`, and `SDMA0_RELAX_ORDERING_LUT`. These define burst sizing, 256-byte combine controls, copy overlap/RAW checking, fine-grained clock-gating overrides, address configuration, tiling/hash parameters, bus/address thresholds, credit limits, and relaxed ordering per packet class.
- Global ring/IB fetch helpers: `SDMA0_RB_RPTR_FETCH`, `SDMA0_RB_RPTR_FETCH_HI`, `SDMA0_IB_OFFSET_FETCH`, `SDMA0_PROGRAM`, and `SDMA0_SEM_WAIT_FAIL_TIMER_CNTL`. These expose ring read-pointer fetch offsets, indirect-buffer fetch offsets, a full-width program stream field, and the semaphore wait-fail timer.
- Status and diagnostics: `SDMA0_STATUS_REG`, `SDMA0_STATUS1_REG`, `SDMA0_STATUS2_REG`, `SDMA0_STATUS3_REG`, `SDMA0_STATUS4_REG`, `SDMA0_STATUS5_REG`, `SDMA0_STATUS6_REG`, `SDMA0_QUEUE_STATUS0`, `SDMA0_INT_STATUS`, `SDMA0_FED_STATUS`, `SDMA0_AQL_STATUS`, and `SDMA0_CLOCK_GATING_STATUS`. These fields expose idle/full/stall states, command opcodes, copy-engine status, active queue IDs, WPTR polling exceptions, XNACK events, ECC/FED conditions, AQL signal FIFO state, and clock-gating state.
- Freeze, scheduling, watchdog, and reset controls: `SDMA0_FREEZE`, `SDMA0_PROCESS_QUANTUM0/1`, `SDMA0_GLOBAL_QUANTUM`, `SDMA0_WATCHDOG_CNTL`, `SDMA0_QUEUE_RESET_REQ`, and queue-local preemption/reset fields. These define engine freeze/preempt bits, per-process and global scheduling quantums, hang/command timeout buckets, and per-queue reset requests.
- Error-detection and correction: `SDMA0_EDC_CONFIG`, `SDMA0_EDC_COUNTER`, `SDMA0_EDC_COUNTER_CLEAR`, `SDMA0_UCODE_CHECKSUM`, `SDMA0_UCODE1_CHECKSUM`, and `SDMA0_FED_STATUS`. These cover EDC disable/interrupt control, single/double error flags across ucode, RB/IB command buffers, UTCL1 FIFOs, data LUTs, memory-bank buffers, split buffers, MC write-address FIFOs, and fetch/data/copy metadata paths.
- UTCL1, VM, and page fault/XNACK registers: `SDMA0_UTCL1_CNTL`, `SDMA0_UTCL1_WATERMK`, `SDMA0_UTCL1_TIMEOUT`, `SDMA0_UTCL1_PAGE`, `SDMA0_UTCL1_RD_STATUS`, `SDMA0_UTCL1_WR_STATUS`, `SDMA0_UTCL1_INV0/1/2`, `SDMA0_UTCL1_RD_XNACK0/1`, `SDMA0_UTCL1_WR_XNACK0/1`, `SDMA0_TLBI_GCR_CNTL`, `SDMA0_PHYSICAL_ADDR_LO/HI`, `SDMA0_HOLE_ADDR_LO/HI`, and `SDMA0_EA_DBIT_ADDR_*`. These define translation retry delays, invalidation controls, FIFO watermarks, page attributes, read/write translation status, invalidation request payloads, XNACK fault address/VMID/vector/flags, TLB/GCR command sizing and credits, physical-address reporting, VM hole addresses, and DBIT address indexing.
- Miscellaneous public registers: `SDMA0_ATOMIC_CNTL`, `SDMA0_ATOMIC_PREOP_LO/HI`, `SDMA0_SCRATCH_RAM_DATA/ADDR`, `SDMA0_TIMESTAMP_CNTL`, `SDMA0_PUB_DUMMY_REG0..3`, `SDMA0_F32_COUNTER`, `SDMA0_RLC_CGCG_CTRL`, `SDMA0_CE_CTRL`, and `SDMA0_ERROR_LOG`. These support atomic return interrupt timing, pre-operation data, scratch access, timestamp capture, dummy/debug registers, F32 counters, RLC clock-gating interrupt/hysteresis, copy-engine FIFO/watermark controls, and error logging.
- Queue register templates for `SDMA0_QUEUE0` through `SDMA0_QUEUE7`: each queue has ring-buffer control/base/read-pointer/write-pointer registers, RPTR writeback addresses, indirect-buffer control/base/offset/size/read-pointer registers, skip count, context status, doorbell enable/captured/offset fields, CSA address, schedule control, IB subremain, IB and RB preemption, dummy register, WPTR poll address, AQL control, minor pointer update, mid-command data registers `MIDCMD_DATA0..10`, and `MIDCMD_CNTL`. Queue 0's `CONTEXT_STATUS` includes a `USE_IB` bit that is absent from queues 1 through 7 in this chunk.
- The beginning of the hypervisor/SR-IOV decode block: `SDMA0_UCODE_ADDR`, `SDMA0_UCODE_DATA`, `SDMA0_BROADCAST_UCODE_ADDR`, `SDMA0_BROADCAST_UCODE_DATA`, `SDMA0_VM_CTX_LO/HI`, `SDMA0_ACTIVE_FCN_ID`, `SDMA0_VIRT_RESET_REQ`, and `SDMA0_VM_CNTL`. These describe ucode address/data access, broadcast ucode programming, VM context address registers, active VF/PF identification, virtual reset request bits, and VM command control. The chunk ends at the `SDMA0_F32_CNTL` comment, before that register's fields.

## Control Flow

This header has no runtime control flow. It participates in register access flows through inclusion and macro substitution:

1. GC 11.5.0 driver code includes the matching offset and shift/mask headers.
2. The caller selects a register offset for SDMA0 or an SDMA queue instance.
3. The caller composes or decodes a 32-bit value with these `__SHIFT` and `_MASK` macros, usually through common AMDGPU field helpers or explicit shifts.
4. The caller performs ordered MMIO reads/writes through AMDGPU register accessors while higher-level SDMA, KFD, VM, reset, interrupt, or virtualization code owns sequencing.

The control-flow-sensitive behavior is therefore in the consumers, not the header. For example, queue bring-up code programs base addresses, sizes, VMIDs, doorbells, write-pointer polling, and RPTR writeback before setting `RB_ENABLE`; teardown/reset paths clear enable bits or assert queue reset/preempt bits; interrupt paths use enable/status fields to route page faults, preemption, context-empty, frozen, and ECC/EDC events.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It names bit layouts for hardware state exposed by GC 11.5.0 SDMA0 registers.

The represented hardware state includes:

- Engine-wide configuration such as power management, interrupt enables, byte swapping, preemption policy, page-fault interrupt behavior, light sleep, clock gating, relaxed ordering, address hashing/tiling, and copy-engine controls.
- Firmware and diagnostic state such as ucode version/checksum, F32 instruction pointers/counters, FED/ECC/EDC flags, scratch RAM contents, dummy/debug registers, global timestamps, and error/status logs.
- Translation and memory-state controls such as UTCL1 invalidation, XNACK fault address and VMID, page attributes, TLB/GCR credits, physical-address reporting, VM hole addresses, DBIT address selection, and HBM page configuration.
- Queue state for eight SDMA0 queues: ring buffer base/high addresses, RPTR/WPTR values, read-pointer writeback addresses, IB base/offset/read pointer/size, CSA addresses, doorbell state, schedule IDs and context quantum, AQL packet sizing, minor pointer updates, queue context status, and saved mid-command data.
- Virtualization state at the tail of the chunk, including active function ID, VF/PF reset requests, VM context base address, and ucode programming/broadcast access.

Persistence is hardware-defined. Some fields are configuration that lasts until reset, power-gating, suspend/resume, queue teardown, or explicit reprogramming. Others are live status, hardware-owned pointers, counters, sticky error bits, write-one/self-clearing requests, or transient active-queue state. The masks do not encode read-only versus writable semantics, reset defaults, write-one-to-clear behavior, ordering requirements, or power-domain restrictions.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies the register offsets corresponding to these field masks. The definitions also depend on common AMDGPU register-helper conventions for field packing/unpacking and SOC15 addressing.

Observed and expected integration points include:

- GC 11.5.0 support files such as `amdgpu/gfxhub_v11_5_0.c`, which include this generated mask header for generation-specific register definitions.
- AMDGPU SDMA initialization and ring-management code, which programs queue ring-buffer base, size, VMID, RPTR writeback, write-pointer polling, doorbells, IB controls, AQL controls, and enable bits.
- AMDKFD queue/MQD management paths for SDMA queues. Closely related GC/SDMA generations use `SDMA0_QUEUE0_RB_CNTL__RB_SIZE__SHIFT`, `SDMA0_QUEUE0_RB_CNTL__RB_VMID__SHIFT`, `SDMA0_QUEUE0_RB_CNTL__RPTR_WRITEBACK_ENABLE__SHIFT`, and write-pointer polling fields to build SDMA queue descriptors.
- VM, GFXHUB, and memory-management paths that need SDMA page attributes, UTCL1 invalidation/status, XNACK fault reporting, VMID fields, physical-address reporting, and TLB/GCR controls.
- Interrupt and recovery paths that enable and decode page-fault/null/retry timeout, semaphore wait, context-empty, frozen, IB/RB preempt, CP/MES, ECC/EDC, and copy-engine status events.
- Reset, preemption, and suspend/resume flows that inspect idle/status bits, active queue IDs, queue reset requests, freeze/preempt bits, queue context status, mid-command save data, and WPTR polling exceptions.
- SR-IOV/virtualization flows at the chunk tail that use function-ID, virtual reset, VM context, and broadcast ucode registers to separate PF/VF behavior.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. These masks must be paired with the GC 11.5.0 offsets; using another generation's offsets can compile but write wrong bits.
- The chunk boundary is artificial. It contains a full SDMA0 public decode block, but the hypervisor decode block is only partially present and ends before `SDMA0_F32_CNTL` fields.
- The macros are untyped constants. A mask from one register or queue instance can be accidentally applied to another value without compiler diagnostics.
- Whole-register writes are risky because registers mix configuration bits, enable bits, request bits, live status, counters, sticky errors, reserved fields, and hardware-owned pointer state.
- Queue address fields have alignment-sensitive shifts and masks. RPTR writeback, WPTR poll, CSA, and IB base addresses mask off low address bits; callers must pass correctly aligned GPU or system addresses.
- Queue size fields are encoded values, not necessarily raw byte counts. Incorrect unit conversion can cause ring wrap errors, stale pointers, or SDMA hangs.
- Doorbell offsets are masked and shifted. Wrong offsets can signal the wrong queue or fail to wake SDMA work.
- VMID, privilege, TMZ/preemption, PF/VF, and page-attribute fields affect isolation and fault routing. Incorrect programming can route memory requests to the wrong address space or break secure/virtualized queue behavior.
- Status fields can race with firmware, the scheduler, interrupts, queue teardown, reset, or user-mode doorbells. Consumers must own the relevant queue/engine sequencing before relying on snapshots.
- EDC/ECC/FED/XNACK flags may be sticky or clear-on-write depending on the register semantics, which are not described by the generated mask names.
- Workaround and clock-gating fields can change engine timing, polling behavior, or power state. They should be modified only by generation-specific initialization or validated workaround paths.
- Full-width masks such as `0xFFFFFFFFL` describe data, pointer, timestamp, or stream payload fields, not a guarantee that all values are safe to write.

## Test Signals

Useful validation signals for code using this chunk include:

- Build coverage for GC 11.5.0 include users, catching missing or stale SDMA0 macro names.
- Register trace comparison against known-good GC 11.5.0 SDMA initialization tables for `SDMA0_CNTL`, power/clock-gating controls, relaxed ordering, address configuration, UTCL1 controls, and queue ring registers.
- SDMA queue bring-up tests for queues 0 through 7 that verify ring base/size programming, RPTR/WPTR movement, RPTR writeback, WPTR polling, doorbell wakeups, and IB execution.
- AMDKFD SDMA queue tests for VMID assignment, AQL enable/packet sizing, queue scheduling quantum, context status, preemption, and queue reset.
- Interrupt tests that exercise page fault/null/retry-timeout, semaphore wait, context-empty, frozen, IB/RB preempt, CP/MES, and ECC/EDC/FED paths and verify both enables and status decoding.
- VM fault and XNACK tests that validate UTCL1 read/write status, invalidation commands, fault address/VMID/vector fields, TLB/GCR credits, and page attribute programming.
- Reset and recovery tests that freeze/preempt queues, assert queue reset requests, verify idle/status bits, and reinitialize SDMA0 queues after GPU reset or suspend/resume.
- SR-IOV tests for active function ID, VF/PF reset request bits, VM context address programming, and broadcast ucode access.
- Power-management tests that toggle light sleep and clock-gating paths while confirming SDMA progress, no lost doorbells, and expected clock-gating status.
