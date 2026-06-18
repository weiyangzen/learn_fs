# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 2559-5106

## Purpose

This chunk is a generated AMD GPU register field header for the GC 12.0.0 SDMA register space. It defines `*_SHIFT` and `*_MASK` constants used by AMDGPU kernel code to pack and unpack bitfields in memory-mapped SDMA control, status, virtualization, performance, cache, fault, and queue registers. The file contains no functions or runtime control flow; its behavior is entirely compile-time exposure of register ABI constants.

The covered range starts at the tail of the `SDMA0_QUEUE7` queue definition, then covers SDMA0 hypervisor/decode, PSP/decode, performance counter, and power-control blocks. It then enters the `SDMA1` block and defines global SDMA1 controls/status registers plus per-queue templates for SDMA1 queues 0 through part of queue 5.

## Important APIs, Types, and Macro Families

- `SDMA0_QUEUE7_*`: remaining queue-7 fields for indirect buffer base/offset/size, doorbell enable/capture/log/offset, CSA address, schedule control, preemption, write-pointer polling, AQL control, context-switch exception status, mid-command save/restore data, MQD base/control, dequeue request, and context status.
- `SDMA0_VM_CTX_*`, `SDMA0_ACTIVE_FCN_ID`, `SDMA0_VIRT_RESET_REQ`, `SDMA0_VM_CNTL`: SDMA0 virtualization and VM context masks, including VF/PF reset request bits and active VF identification.
- `SDMA0_MCU_CNTL`, `SDMA0_IC_*`: microcontroller halt/reset/debug bits and instruction-cache base/control/operation masks, including invalidate, prime, primed, VMID, execute-disable, and MALL policy fields.
- `SDMA0_PERFCNT_*` and `SDMA0_PERFCOUNTER*`: SDMA0 performance counter selector, mode, clear/enable, result-control, low/high counter result, compare, and multi-selector masks.
- `GFX_ICG_SDMA0_CTRL`: SDMA0 power/clock gating override masks for register, pointer, PIO, MCU, copy/serve engines, command fetch, memory request, invalidation, caches, memory channels, performance counters, and hysteresis.
- `SDMA1_*` global registers: second SDMA engine decode start, MCU wakeup, ucode revision, global timestamp, power control, main control, tuning bits, cache policy, fetch offsets, program stream, status registers, freeze/preempt controls, process/global quantum, watchdog, queue status, EDC/ECC, ID/version, atomic controls, DCC controls, UTCL1 translation/cache controls, XNACK/fault state, relaxed ordering, credit/clock gating, IOV violation logs, invalid-address logs, interrupt status, scratch RAM, timestamp capture, queue reset, CE control, and FED/ECC status.
- `SDMA1_QUEUE{0..5}_*` templates: per-queue ring-buffer, indirect-buffer, doorbell, scheduling, AQL, preemption, mid-command, MQD, dequeue, and context-status field masks. The chunk fully covers queues 0 through 4 and continues through the start/middle of queue 5.

There are no C structs, enums, functions, or callable APIs in this range. Consumers include these macros directly in register read/modify/write expressions, usually through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32`, and `RREG32` in nearby driver code.

## Control Flow and Data Flow

Runtime control flow is supplied by code outside this header. The effective data flow is:

1. Driver code reads a 32-bit MMIO register value or prepares a new 32-bit value.
2. A field macro pair identifies the bit offset and bit mask for a hardware field.
3. The caller shifts, masks, inserts, tests, or clears the field.
4. The caller writes the value back to the SDMA register or interprets the readback as queue, fault, power, or performance state.

The per-queue definitions describe repeated SDMA queue state machines. `RB_*` fields configure or observe ring buffers; `IB_*` fields configure indirect-buffer execution; `DOORBELL*` fields connect host/user write-pointer updates to hardware; `AQL_*` fields configure HSA/AQL packet handling; `CONTEXT_SWITCH_STATUS` and `CONTEXT_STATUS` expose preemption, idle, exception, VF, privilege, and pointer-update state.

## State and Persistence Behavior

The header does not allocate or persist state. The state represented by these masks lives in GPU hardware registers and hardware-managed memory structures:

- Ring-buffer bases, read/write pointers, writeback addresses, polling addresses, and MQD bases are persistent hardware programming state until reset, queue teardown, or driver reprogramming.
- Doorbell enable/offset/capture and doorbell log fields reflect host-to-GPU queue notification state and error capture.
- Context status, context-switch status, status registers, XNACK fault registers, invalid-address registers, ECC/FED registers, IOV violation logs, and queue status registers are hardware-observed diagnostic state.
- Performance counter selector/control and counter-result fields persist while enabled and are cleared by explicit clear bits.
- Freeze, preempt, reset, watchdog, quantum, and clock/power gating fields affect ongoing SDMA scheduling and power-management behavior.

Because the constants are compile-time ABI definitions, persistence risks are not in this file itself; they arise when caller code writes incorrect field values or uses the wrong mask for the active ASIC generation.

## Dependencies and Integration Points

This header depends only on the C preprocessor and the AMD register naming convention. It is part of the generated AMDGPU ASIC register set and should be paired with the corresponding address header for GC 12.0.0 registers. Typical integration points are:

- SDMA engine initialization and teardown paths that configure `SDMA1_CNTL`, power control, cache policy, clock gating, ucode, instruction cache, queue rings, MQDs, and doorbells.
- Queue management paths for KFD/AMDGPU compute queues, especially AQL, MQD, VMID, context-switch, preemption, and dequeue handling.
- Virtualization/SR-IOV paths that inspect active VF IDs, VF/PF reset requests, GPU IOV violation logs, and VF context status.
- Fault handling paths for page faults, null/retry timeout XNACKs, invalid addresses, UTCL1 invalidation, and read/write translation status.
- Debug and health paths that poll idle/status bits, ECC/FED status, watchdog state, queue enable status, and active queue IDs.
- Performance monitoring code that selects SDMA performance events, enables/clears counters, and reads 32-bit/64-bit counter values.

## Risks and Edge Cases

- **Generated ABI drift:** A one-bit shift or mask mismatch silently corrupts register programming. This is especially risky for queue base addresses, VMIDs, doorbell offsets, reset bits, and fault-log interpretation.
- **Partial queue coverage:** The chunk starts mid-`SDMA0_QUEUE7` and ends mid-`SDMA1_QUEUE5`; readers must merge adjacent chunks for complete per-file coverage.
- **Repeated queue templates:** Queue macros are mechanically similar. Copy/paste mistakes in consumers can use a queue-0 mask with a queue-3 register or vice versa; the compiler will not catch this because all values are integer constants.
- **Reserved fields:** Several masks expose reserved ranges. Callers should preserve reserved bits during read/modify/write unless hardware documentation says otherwise.
- **Address alignment fields:** Many address fields shift by two and mask low bits off. Callers must provide aligned GPU addresses and split low/high parts consistently.
- **Privilege and virtualization bits:** `VF`, `VFID`, `RB_PRIV`, VMID, IOV log, and PF/VF reset fields affect isolation. Incorrect use can break SR-IOV or leak/misattribute faults.
- **Status-vs-control ambiguity:** Some registers are control writes, some are status readbacks, and some are write-one action bits. The header does not encode access type, so behavior depends on the matching register-address/spec metadata and caller discipline.

## Test Signals

Useful validation for changes around this header is mostly integration and hardware-observation based:

- Build coverage for AMDGPU/KFD code that includes GC 12.0.0 register headers; compile errors catch missing/renamed macros.
- Queue bring-up tests should show SDMA1 ring buffers enabled, valid MQD base/control programming, doorbell updates accepted, and no `WPTR_LT_RPTR`, doorbell, page, or queue-hang exceptions.
- Suspend/resume and GPU reset tests should exercise `FREEZE`, queue reset, context status, and idle/status polling paths.
- SR-IOV testing should validate active VF identification, VF/PF reset request handling, VF context status, and IOV violation log decoding.
- Fault-injection or negative tests should verify page fault, retry timeout, null page, invalid address, and XNACK read/write logs decode to the expected VMID/address/vector fields.
- Performance counter tests should confirm event selection, enable/clear behavior, low/high counter reads, and stop-on-saturate behavior.
- Power-management tests should monitor clock-gating status and confirm clock/power override fields do not leave SDMA stuck non-idle or unavailable.
