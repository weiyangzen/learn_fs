# Research: subset-b-003346

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_1_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_1_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_d.h

## Purpose

`oss_3_0_d.h` is a generated AMDGPU register-address header for the OSS 3.0 hardware block family. It exports symbolic MMIO and indexed-register offsets for interrupt handling, semaphore/virtualization, SRBM, security/key or client registers, SDMA engines and contexts, and HDP/XDP host-data-path registers. It contains no executable code; it gives driver code stable names for hardware addresses.

The include guard is `OSS_3_0_D_H`. Macro prefixes distinguish address spaces:

- `mm*` names are memory-mapped register offsets used by normal MMIO register access helpers.
- `ix*` names are indexed-register offsets, notably for a client/key/session/security-style register block.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or mutable variables. The API is a flat set of `#define`s mapping symbolic register names to numeric offsets.

Major address groups include:

- `mmIH_*`: IH VMID LUTs, ring buffer control/base/read/write pointers, writeback pointer address registers, interrupt control/status, perf counters, debug, DSM matching, doorbell read pointer, VF/virtual reset status, and level/incomplete-interrupt controls.
- `mmSEM_*`, `mmSDMA_CONFIG`, `mmSDMA1_CONFIG`, `mmUVD_CONFIG`, `mmVCE_CONFIG`, and `mmCP_CONFIG`: semaphore and client-configuration registers around the `0xf90` range.
- `mmSRBM_*`, `mmSYS_GRBM_*`, and `mmCC_*`: SRBM control/status/reset/debug/read-error/firewall/interrupt/perf/CAM/domain/virtualization and backend-disable/redundancy registers.
- `ixDH_TEST`, `ixKHFS*`, `ixKSESSION*`, `ixKSIG*`, `ixEXP*`, `ixLX*`, `ixCLIENT0` through `ixCLIENT4`, `ixKEFUSE*`, `ixHFS_SEED*`, `ixRINGOSC_MASK`, and `ixSPU_PORT_STATUS`: indexed-register space entries for key/session/client-related hardware state.
- `mmSDMA0_*` and `mmSDMA1_*`: public SDMA engine registers, perf counters, debug/freeze/phase/power/VM/atomic registers, and repeated GFX/RLC0/RLC1 ring-buffer, IB, doorbell, watermark, context, and mid-command address ranges.
- `mmHDP_*` and `mmHDP_XDP_*`: host-data-path cache, nonsurface, tiling, memory IO, VF, direct-to-HDP, P2P mailbox/BAR, XDP configuration, busy/sticky/debug, and high BAR address registers.

Notable offset patterns:

- IH registers occupy `0xe00` through `0xe4b`.
- SEM/client configuration appears around `0xf90` through `0xf9f`.
- Core SRBM registers appear around `0x390` through `0x3b9`, with perf registers at `0x7c00` and domain/virtualization windows at `0xfa00` and above.
- SDMA0 public/context ranges begin around `0x3400`; SDMA1 begins around `0x3600`. RLC0/RLC1 context ranges are offset blocks for each engine.
- HDP appears around `0xb00`/`0xbc9` and XDP-related HDP registers around `0xc00` through `0xc44`.

## Control Flow And Data Flow

This header has no direct control flow. It participates in driver control flow as address data:

1. Driver code selects a symbolic register offset, for example `mmIH_RB_CNTL`, `mmSRBM_STATUS`, `mmSDMA0_GFX_RB_WPTR`, or `mmHDP_XDP_D2H_FLUSH`.
2. It combines the offset with an MMIO access helper and, when needed, field macros from a matching `*_sh_mask.h` header.
3. It reads or writes the GPU register.
4. Higher-level control flow waits on status bits, writes reset bits, posts doorbells, updates read/write pointers, configures VM context, or flushes host data paths.

The file's layout mirrors hardware initialization and service paths: IH addresses support interrupt-ring initialization and servicing; SRBM addresses support global block selection/status/reset; SDMA addresses support microcode, rings, IBs, doorbells, VM, and context switching; HDP/XDP addresses support CPU/host-visible memory coherency and P2P/BAR operations.

## State And Persistence Behavior

The header stores no software state. Each constant identifies a hardware register whose value persists in the device across ordinary driver reads/writes until changed by driver code, firmware, reset, power transitions, or hardware activity.

Stateful hardware represented by these addresses includes:

- Interrupt state: IH ring pointers, overflow/status, interrupt masks and incomplete-interrupt counters.
- Global routing and reset state: SRBM graphics selection, busy status, soft reset, read/firewall error latches, and domain address mappings.
- Security/client indexed state: key/session/client/fuse/seed-like indexed registers exposed through `ix*` constants.
- DMA state: SDMA engine control, queue rings, IB pointers, doorbells, VM context, atomics, context status, preemption, and perf counters.
- Host data path state: HDP cache/nonsurface metadata, memory IO transaction status, VF enablement, XDP flush/bar/P2P mappings, busy/sticky/debug flags, and high BAR address bits.

Because the constants are part of the driver-to-hardware ABI, the persistent behavior is in the hardware side effects of reads and writes performed by consumers.

## Dependencies And Integration Points

This header has no include dependencies beyond the C preprocessor. It is designed to be included by AMDGPU ASIC code together with compatible field-layout headers, such as `oss_3_0_sh_mask.h` or related OSS 3.0.x mask headers.

Integration points include:

- Register access helpers that expect `mm*` offsets.
- Indexed-register access helpers for `ix*` offsets.
- AMDGPU interrupt handler code for IH register setup and servicing.
- SRBM helpers for block idleness, read-error/firewall reporting, domain address setup, graphics selection, virtualization, and reset.
- SDMA initialization and ring-management code for SDMA0/SDMA1 public and context registers.
- HDP/XDP cache flush, memory IO, P2P, BAR, and VF handling paths.
- Generated-register build or sync processes that keep `*_d.h` address headers aligned with `*_sh_mask.h` field headers.

## Risks And Edge Cases

- Address constants must match the exact ASIC generation. A wrong address can corrupt unrelated device state even when the field masks are correct.
- SDMA0/SDMA1 and GFX/RLC0/RLC1 address blocks are highly repetitive but offset differently. Incorrectly substituting one block for another can route commands to the wrong engine or queue.
- The `ix*` indexed-register macros are in a different access space than `mm*` macros. Using the wrong accessor class can fail silently or access unintended hardware.
- Register offsets alone do not encode access semantics. Some registers are read-only, write-only, write-one-to-clear, latch-on-read, or require ordering/delay rules defined outside this file.
- The header is OSS 3.0 while the paired work item also includes an OSS 3.0.1 mask file. Consumers must verify that the address generation and mask generation are compatible for the target ASIC.
- HDP/XDP and SRBM virtualization registers affect host-visible memory routing and VF state. Mistakes can create coherency, isolation, or reset issues.

## Test Signals

Useful validation signals are mostly compile-time and hardware-integration tests:

- AMDGPU builds for ASICs using OSS 3.0 address headers, catching missing or renamed macros.
- Register-database diffing against the canonical AMD-generated source for OSS 3.0.
- Probe and boot on matching hardware with successful IH setup, no spurious interrupts, and correct SRBM status polling.
- SDMA0 and SDMA1 ring tests that exercise GFX, RLC0, and RLC1 contexts, doorbells, IB submission, VM context setup, and preemption.
- GPU reset, suspend/resume, and power-management tests that touch SRBM, SDMA, and HDP state.
- HDP cache flush/memory coherency tests, especially around CPU-visible buffers and P2P/BAR paths.
- SR-IOV/VF tests that validate VF enable/reset/status and memory IO routing when virtualization is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/oss_3_0_d.h -->
