# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_1_sh_mask.h

## Purpose

`oss_3_0_1_sh_mask.h` is a generated AMDGPU register-field header for the OSS 3.0.1 hardware block family. It does not implement executable logic; it exports C preprocessor constants that describe bit masks and bit shifts for interrupt handling, semaphore/virtualization, SRBM routing/status/reset, SDMA engines and queues, and HDP/XDP host-data-path registers. The companion address header supplies register offsets, while this file supplies the field layout within those registers.

The include guard is `OSS_3_0_1_SH_MASK_H`. All exported names are `#define`s following the generated AMD register pattern:

- `REGISTER__FIELD_MASK` is the already-positioned bit mask for the field.
- `REGISTER__FIELD__SHIFT` is the right-shift amount for encoding or decoding that field.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or global variables. The public API is the macro namespace consumed by AMDGPU MMIO helpers and bitfield helpers. Major exported groups are:

- `IH_*`: interrupt handler VMID-to-PASID LUT entries, ring-buffer control/base/read/write pointers, interrupt enable/rearm, level/status bits, performance counters, DSM match fields, and version fields.
- `SEM_*`: semaphore memory-client interface credits, performance counters, VF/PF reset and active function state, mailbox routing, mailbox data/control, and internal status/EDC/chicken-bit controls.
- `SRBM_*`, `SYS_GRBM_*`, and `CC_*`: SRBM control, graphics ring addressing selector fields, timeout/status/busy bits, soft reset targets, debug snapshot/read-error/firewall/interrupt fields, performance-counter fields, CAM remap fields, domain address windows, virtualization controls, and backend-disable/redundancy fields.
- `SDMA0_*` and `SDMA1_*`: two largely parallel SDMA engine field families, including microcode address/data, power and clock control, global engine control, tiling/hash, public status, CE status, perf counters, freeze/F32 debug, phase quanta, power gating FSM, EDC, VM context, active function/VF controls, atomic controls, ATCL1 translation/invalidation/XNACK fields, and repeated GFX/RLC0/RLC1 context ring/IB/doorbell/mid-command fields.
- `HDP_*` and `HDP_XDP_*`: host-data-path cache, nonsurface, tiling, memory IO, VF, direct-to-HDP flush/bar-update, P2P mailbox/BAR, XDP-to-HDP memory-client, host/sideband, debug, busy/sticky, and high-address BAR fields.

The macro layout also includes a few generated names with doubled semantic `MASK` text, such as `SRBM_INT_CNTL__RDERR_INT_MASK_MASK`, `SRBM_DSM_TRIG_MASK0__DSM_TRIG_ADDR_MASK_MASK`, and `HDP_XDP_HDP_MC_CFG__HDP_MC_CFG_MC_STALL_ON_BUF_FULL_MASK_MASK`. These are not typos in this research output; they reflect hardware field names that themselves contain `MASK`.

## Control Flow And Data Flow

This header has no runtime control flow. Driver control flow appears in consumers that include it, select a register address from an `*_d.h` header, and compose register values from these masks and shifts before writing MMIO. Typical data flow is:

1. Select the relevant register address macro, for example an `mmIH_RB_CNTL`, `mmSRBM_SOFT_RESET`, `mmSDMA0_GFX_RB_CNTL`, or `mmHDP_MISC_CNTL` offset from an address header.
2. Encode fields by shifting a value by `REGISTER__FIELD__SHIFT` and masking with `REGISTER__FIELD_MASK`, or by using local AMDGPU helper macros that perform the same operation.
3. Write the composed value through the GPU MMIO path.
4. Read status or counter registers and decode fields by masking with `REGISTER__FIELD_MASK` and shifting right by `REGISTER__FIELD__SHIFT`.

Important behavioral clusters visible from the fields:

- IH ring setup and interrupt service depend on coordinated `IH_RB_CNTL`, base pointer, read pointer, write pointer, overflow, writeback, and interrupt-enable fields.
- SRBM status and reset flows use busy/request bits to determine idle state, then assert per-block reset bits in `SRBM_SOFT_RESET` for blocks such as BIF, DC, SDMA, IH, MC, SEM, VMC, UVD, VCE, ACP, ISP, and related units.
- SDMA setup flows configure microcode, memory power, clock delays, ring buffers, IB execution, doorbells, VM context, context-switch/preemption state, and ATCL1 translation/invalidation support. The GFX, RLC0, and RLC1 context register groups are structurally repeated for each SDMA engine.
- HDP flows control CPU/host-visible GPU memory access, cache invalidation, write combining, nonsurface tiling metadata, memory IO transactions, VF routing, and XDP P2P/BAR flush behavior.

## State And Persistence Behavior

The header stores no state in memory or on disk. Its constants describe persistent hardware register state that lives in the GPU until modified by the driver, firmware, reset, or power-management transitions. Several macro groups map directly to stateful hardware:

- Ring-buffer state: IH and SDMA read/write pointers, base addresses, writeback addresses, polling controls, and overflow/status bits.
- Virtualization state: `*_VF_ENABLE`, `*_ACTIVE_FCN_ID`, `*_VIRT_RESET_REQ`, VMID/PASID fields, VFID fields, and HDP/SRBM memory-IO VF routing.
- Reset and busy state: SRBM busy/status fields and soft-reset bits, plus SDMA freeze/F32 and context-status flags.
- MMU/translation state: SDMA VM context address/control, ATCL1 watermarks, invalidation, XNACK address/VMID fields, and timeout limits.
- Host cache/path state: HDP cache invalidation, nonsurface metadata, outstanding request counters, P2P BAR/mailbox mappings, and XDP sticky/busy status.

Because this is a hardware ABI description, field values are effectively part of the kernel-driver-to-ASIC contract. Any incorrect mask or shift can cause persistent device misconfiguration until a later corrective write or reset.

## Dependencies And Integration Points

This file depends only on the C preprocessor and can be included without additional headers. It is intended to be paired with an address definition header for the same or compatible ASIC generation, especially `oss_3_0_d.h` and nearby `oss_3_0_1_d.h`/versioned generated headers when present.

Integration points include:

- AMDGPU register-access helpers that take `mm*` offsets and bitfield masks/shifts.
- Interrupt-handler initialization and IRQ service code for IH ring setup and overflow/status handling.
- SRBM code that selects graphics instances, polls block idleness, handles read/firewall errors, and triggers soft resets.
- SDMA engine initialization, ring creation, doorbell setup, VM/ATC support, context switching, preemption, atomics, and perf/debug paths.
- HDP flush/cache invalidation and BAR/P2P paths used by CPU-visible GPU memory access.
- SR-IOV or virtualization flows through VF/PF enable, active-function, reset-request, VFID, and memory-IO fields.

## Risks And Edge Cases

- The file is generated hardware ABI data. Manual edits are risky because consumers rarely validate masks at compile time and a single wrong bit can break interrupts, resets, DMA, cache coherency, or virtualization isolation.
- The SDMA0 and SDMA1 families are intentionally near-duplicates. Copy/paste or generation drift between engines can cause one DMA engine to behave differently from the other.
- Address and mask headers must be version-compatible. Using OSS 3.0.1 masks with the wrong register-address generation can silently target the wrong field or register.
- Several fields touch reset, firewall, memory IO, and VF routing. Incorrect writes may affect global GPU state or peer/VF access rather than only the calling context.
- Reserved and generated `VOID`/`RESERVED` fields appear in multiple register-type masks. Consumers should avoid setting reserved bits unless the hardware programming guide explicitly requires preserved values.
- Many address fields are aligned and expose low-bit shifts, such as ring pointers and base addresses. Failing to enforce alignment before applying masks can truncate addresses.
- Some fields are write-one-to-clear or acknowledgement-style by convention, such as interrupt ack, sticky status, and clear fields. Consumers need register-specific semantics beyond the mask itself.

## Test Signals

Useful validation signals for changes involving this header are hardware and driver-behavior oriented:

- Compile coverage for AMDGPU configurations that include OSS 3.0.1 headers; missing or renamed macros should fail quickly.
- Boot/probe tests on matching ASICs that verify IH initialization, no interrupt storms, and correct ring writeback behavior.
- SDMA ring tests for both SDMA0 and SDMA1, including GFX, RLC0, and RLC1 queues, doorbells, IB execution, preemption, and context switching where supported.
- GPU reset and suspend/resume tests that exercise `SRBM_SOFT_RESET`, busy/status polling, HDP cache invalidation, and SDMA power/clock gating.
- SR-IOV/VF tests for VF enable/reset, active-function reporting, VFID fields, HDP memory IO routing, and firewall-error reporting.
- Memory-coherency tests that require HDP flush/invalidate, write-combine, nonsurface, and P2P BAR behavior.
- Register-generation diff checks against AMD's canonical register database for OSS 3.0.1 to catch accidental drift.
