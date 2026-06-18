# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_1_sh_mask.h lines 4845-7297

## Chunk Scope

This chunk is a large middle slice of the generated AMD MMHUB 3.0.1 shift/mask header. It covers source lines 4845-7297 and contains only C preprocessor constants for hardware register bitfields, using the generated naming pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

The range starts inside `MMVM_L2_PROTECTION_FAULT_CNTL2`, so the first few visible macros are the trailing masks for that register and the matching shifts are in the previous chunk. It then spans MMVM L2 fault/status controls, MMVM virtual-context programming, TLB invalidation engines, page-table aperture registers, performance counters, shared MMVM/MMUTCL2 aperture controls, and the beginning of ATC L2 performance-counter controls. The range ends inside `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`, so that register is also completed by the next chunk.

This header chunk is not executable C and defines no logic by itself. Its purpose is to provide compile-time bit positions and masks used by AMDGPU MMHUB/GMC code when programming or decoding MMHUB 3.0.1 MMIO registers.

## Purpose And Hardware Area

The visible definitions describe the MMHUB MMUTCL2/MMVM register map for virtual memory translation, fault reporting, cache/TLB invalidation, memory aperture routing, and debug telemetry.

The main hardware areas are:

- MMVM L2 protection-fault reporting and default-address controls, including fault status decoding, logical fault address capture, physical default page address, and context identity apertures.
- MMVM L2 cache, credit, parity, clock-gating, and bank-selection controls, including PTE cache dump access and credit-safety update registers.
- MMVM context programming for contexts 0-15: enable bits, page-table depth/block size, per-fault interrupt/default behavior, page-table base addresses, start/end logical address ranges, and per-context PTE cache fragment/bank fields.
- MMVM invalidate engines 0-17: semaphore, request, acknowledgement, and address-range registers used to invalidate L1/L2 translation caches per VMID or address range.
- MMVM/MMUTCL2 performance counters for L2 and UTCL2 events, including counter select, mode, enable, clear, start/stop trigger, result selection, and low/high counter result fields.
- Shared MMVM/MMUTCL2 registers for PCIe ATS, northbridge/MMIO aperture windows, top-of-DRAM, framebuffer offset, cacheable/local system memory ranges, local framebuffer ranges, virtualization reset/active-function state, clock gating, harvest bypass, and group return fault status.
- Shared virtual-client aperture registers for framebuffer, AGP, system aperture bounds, and L1 TLB control.
- ATC L2 performance-counter read/config/result-control fields at the end of the slice.

Within the driver, the macros are paired with generated register-address headers and consumed by ASIC-specific AMDGPU code through register write/read helpers. They allow callers to compose register values without open-coded bit positions.

## Important Definitions

This chunk defines no functions, structs, unions, enums, inline helpers, storage objects, or exported symbols. The important interface is the macro set.

Each normal field has:

- `...__SHIFT`: the low bit of the field in a 32-bit register value.
- `..._MASK`: the bit mask used to isolate or clear the field.

Important macro families in this slice include:

- Fault controls and capture: trailing `MMVM_L2_PROTECTION_FAULT_CNTL2` masks, `MMVM_L2_PROTECTION_FAULT_MM_CNTL3`, `MMVM_L2_PROTECTION_FAULT_MM_CNTL4`, `MMVM_L2_PROTECTION_FAULT_STATUS`, `MMVM_L2_PROTECTION_FAULT_ADDR_LO32/HI32`, and `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_LO32/HI32`.
- Identity/aperture controls: `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_LOW_ADDR_*`, `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_HIGH_ADDR_*`, and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`.
- L2 cache behavior controls: `MMVM_L2_CNTL4`, `MMVM_L2_CNTL5`, `MMVM_L2_MM_GROUP_RT_CLASSES`, `MMVM_L2_BANK_SELECT_RESERVED_CID`, `MMVM_L2_BANK_SELECT_RESERVED_CID2`, `MMVM_L2_BANK_SELECT_MASKS`, and per-context `MMVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`.
- L2 reliability/debug controls: `MMVM_L2_CACHE_PARITY_CNTL`, `MMVM_L2_PTE_CACHE_DUMP_CNTL`, `MMVM_L2_PTE_CACHE_DUMP_READ`, and `MMVM_L2_GCR_CNTL`.
- Clock/busy controls: `MMVM_L2_CGTT_CLK_CTRL`, `MMVM_L2_CGTT_BUSY_CTRL`, `MMUTCL2_CGTT_CLK_CTRL`, and `MMUTCL2_CGTT_BUSY_CTRL`.
- Credit-safety controls: `MMUTCL2_CREDIT_SAFETY_GROUP_RET_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_NOCDC`, `MMVML2_CREDIT_SAFETY_IH_FAULT_INTERRUPT`, and `MMVML2_WALKER_CREDIT_SAFETY_FETCH_RDREQ`.
- Context controls: `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL` and `MMVM_CONTEXTS_DISABLE`.
- Invalidation engines: `MMVM_INVALIDATE_ENG0_SEM` through `MMVM_INVALIDATE_ENG17_SEM`, `MMVM_INVALIDATE_ENG0_REQ` through `MMVM_INVALIDATE_ENG17_REQ`, `MMVM_INVALIDATE_ENG0_ACK` through `MMVM_INVALIDATE_ENG17_ACK`, and `MMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through `MMVM_INVALIDATE_ENG17_ADDR_RANGE_LO32/HI32`.
- Page-table address programming: `MMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` through `MMVM_CONTEXT15_PAGE_TABLE_BASE_ADDR_LO32/HI32`, plus per-context `PAGE_TABLE_START_ADDR_LO32/HI32` and `PAGE_TABLE_END_ADDR_LO32/HI32`.
- L2/UTCL2 performance counters: `MMMC_VM_L2_PERFCOUNTER0_CFG` through `MMMC_VM_L2_PERFCOUNTER7_CFG`, `MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MMMC_VM_L2_PERFCOUNTER_LO/HI`, `MMUTCL2_PERFCOUNTER0_CFG` through `MMUTCL2_PERFCOUNTER3_CFG`, `MMUTCL2_PERFCOUNTER_RSLT_CNTL`, and `MMUTCL2_PERFCOUNTER_LO/HI`.
- Shared MMVM/MMUTCL2 aperture and virtualization registers: `MMVM_PCIE_ATS_CNTL`, `MMMC_VM_NB_MMIOBASE`, `MMMC_VM_NB_MMIOLIMIT`, `MMMC_VM_NB_PCI_CTRL`, `MMMC_VM_NB_PCI_ARB`, `MMMC_VM_NB_TOP_OF_DRAM_SLOT1`, `MMMC_VM_NB_LOWER_TOP_OF_DRAM2`, `MMMC_VM_NB_UPPER_TOP_OF_DRAM2`, `MMMC_VM_FB_OFFSET`, `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`, `MMMC_VM_STEERING`, `MMMC_SHARED_VIRT_RESET_REQ`, `MMMC_SHARED_ACTIVE_FCN_ID`, `MMUTCL2_HARVEST_BYPASS_GROUPS`, and `MMUTCL2_GROUP_RET_FAULT_STATUS`.
- Shared VC aperture registers: `MMMC_VM_FB_LOCATION_BASE`, `MMMC_VM_FB_LOCATION_TOP`, `MMMC_VM_AGP_TOP/BOT/BASE`, `MMMC_VM_SYSTEM_APERTURE_LOW_ADDR`, `MMMC_VM_SYSTEM_APERTURE_HIGH_ADDR`, and `MMMC_VM_MX_L1_TLB_CNTL`.
- ATC L2 telemetry: `MM_ATC_L2_PERFCOUNTER_LO`, `MM_ATC_L2_PERFCOUNTER_HI`, `MM_ATC_L2_PERFCOUNTER0_CFG`, `MM_ATC_L2_PERFCOUNTER1_CFG`, and the visible start of `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`.

## Control Flow

There is no runtime control flow in this chunk. The C preprocessor expands these macros wherever MMHUB programming code includes the header.

The effective control flow exists in consumers that:

- Compose a register value by shifting a chosen field value by `__SHIFT` and then applying `_MASK`.
- Decode a register read by masking and right-shifting a field.
- Perform read-modify-write updates where `_MASK` clears a field and a shifted value inserts the new hardware setting.
- Program context control, page-table base, and page-table range registers before enabling VM contexts.
- Submit TLB invalidation by programming an engine's address-range registers, request bits, and VMID mask, then polling or checking the matching acknowledgement/semaphore fields.
- Decode `MMVM_L2_PROTECTION_FAULT_STATUS` after a page-walk or permission fault to determine client ID, VMID, VF/VFID, read/write/atomic direction, mapping error, permission faults, walker error, PRT, and whether additional faults are queued.
- Enable, clear, select, start, stop, and read MMVM L2, UTCL2, or ATC L2 performance counters.

Because the file is generated register metadata, the correctness of control flow depends on downstream code following the hardware sequencing rules for the matching MMHUB 3.0.1 register-address definitions.

## State And Persistence Behavior

The header itself has no mutable state, allocates no memory, performs no I/O, and persists no data. All state described here is hardware state in MMHUB/MMUTCL2 registers.

Important state classes described by the macros are:

- Fault state: `MMVM_L2_PROTECTION_FAULT_STATUS` and fault address/default-address registers reflect current or latched protection-fault information until hardware or driver fault-handling paths clear or overwrite it.
- Context state: `MMVM_CONTEXT*_CNTL`, page-table base, start, and end registers define the active GPU virtual address spaces for VM contexts 0-15. These settings persist in hardware until reset, reprogramming, suspend/resume restore, or context teardown.
- Invalidation state: invalidate-engine semaphore/request/ack/address-range registers hold transient synchronization and invalidation commands. Drivers generally expect request bits and acknowledgements to converge before assuming stale translations have been flushed.
- Cache and bank-selection state: L2 fragment size, bank masks, reserved client IDs, GCR, and PTE cache dump controls affect cache behavior, debug visibility, and cache partitioning while the MMHUB block is active.
- Aperture state: shared framebuffer, AGP, system aperture, local system memory, cacheable DRAM, local framebuffer, MMIO, top-of-DRAM, and default-address registers control address routing and fallback behavior.
- Virtualization state: `MMMC_SHARED_VIRT_RESET_REQ` and `MMMC_SHARED_ACTIVE_FCN_ID` expose PF/VF reset and active-function selection bits for SR-IOV or virtualized access paths.
- Clock/power state: `*_CGTT_CLK_CTRL`, `*_CGTT_BUSY_CTRL`, and `MMMC_MEM_POWER_LS` describe clock-gating, busy override, and memory light-sleep timing fields.
- Telemetry state: performance counter config/result registers and low/high counter result fields represent transient debug counters whose values are explicitly selected, cleared, enabled, stopped, or allowed to saturate by consumer code.

Macro definitions are compile-time constants. Register state lifetime and persistence are controlled by MMIO writes, firmware interaction, GPU reset, runtime power management, suspend/resume, and virtualization reset flows outside this header.

## Dependencies And Integration Points

This chunk has only the whole-file include guard and the C preprocessor as direct dependencies. There are no `#include` directives in the visible range.

Practical integration dependencies are implicit:

- The matching `mmhub_3_0_1` register-offset/address header that names the physical MMIO registers corresponding to these fields.
- AMDGPU MMIO helpers and register-field helper macros used by GMC/MMHUB code to write, read, poll, and update register values.
- ASIC-specific VM/MMHUB initialization code that programs contexts, apertures, fault defaults, L2 controls, clock gating, and performance counters in a safe order.
- VM update and eviction paths that program page-table bases/ranges and issue invalidate-engine requests after page-table changes.
- Interrupt/fault-handling code that reads MMVM L2 fault status and fault-address fields and may use invalidation or default-page behavior in response.
- Power-management and reset code that must preserve or restore VM context, aperture, clock-gating, and shared state across suspend/resume, runtime power transitions, and GPU resets.
- Virtualization/SR-IOV integration that depends on PF/VF active-function, reset, per-PFVF cache fragment sizing, and VFID-related fault fields.
- Debug/performance tooling that selects and reads MMVM L2, UTCL2, and ATC L2 performance counter events.

The `// addressBlock:` comments are useful generated grouping markers. In this chunk they separate `mmhub_mmutcl2_mmvml2vcdec`, `mmhub_mmutcl2_mmvml2pldec`, `mmhub_mmutcl2_mmvml2prdec`, `mmhub_mmutcl2_mmvmsharedhvdec`, `mmhub_mmutcl2_mmvmsharedpfdec`, `mmhub_mmutcl2_mmvmsharedvcdec`, `mmhub_mmutcl2_mmatcl2pfcntrdec`, and `mmhub_mmutcl2_mmatcl2pfcntldec`.

## Risks

- Boundary incompleteness: this chunk starts after the first `MMVM_L2_PROTECTION_FAULT_CNTL2` shift/mask definitions and ends before the complete `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL` definition. The final per-file merge should reconcile those registers with adjacent chunks.
- Generated-header drift: any mismatch between these bit masks/shifts, the matching offset header, and the authoritative MMHUB 3.0.1 register specification can compile cleanly but program the wrong hardware bits.
- Semantic ambiguity: masks and shifts do not encode whether fields are read-only, write-one-to-clear, sticky, reset-only, privileged, debug-only, or safe only while a block is idle. Consumers must use hardware documentation and established AMDGPU sequencing.
- VM context hazards: wrong `MMVM_CONTEXT*_CNTL`, page-table base, start, or end programming can cause GPU virtual-address translation failures, data corruption, page faults, or unintended access to default pages.
- Invalidation hazards: missing or incorrect `MMVM_INVALIDATE_ENG*_REQ` bits, address ranges, VMID masks, or acknowledgement polling can leave stale L1/L2 translations resident after page-table updates.
- Fault-handling hazards: mis-decoding `MMVM_L2_PROTECTION_FAULT_STATUS` can attribute faults to the wrong VMID, VFID, client, access type, or fault class, making recovery or diagnostics misleading.
- Aperture hazards: framebuffer, AGP, system aperture, top-of-DRAM, default-address, and local-memory range fields define address routing. Incorrect values can break MMIO/VRAM/system-memory accesses.
- Clock/power hazards: CGTT and light-sleep timing fields can interact with power-gated or clock-gated MMHUB blocks. Incorrect programming can cause hangs, lost register state, or false busy/idle detection.
- Debug/performance side effects: performance-counter clear/enable/result-control fields can disturb in-flight measurements, and PTE cache dump or parity-force fields may be unsafe outside controlled debug or validation flows.
- Virtualization hazards: PF/VF reset and active-function fields are sensitive in SR-IOV environments. Incorrect use can affect the wrong function or expose misleading per-VF state.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, static, and hardware-integration oriented:

- Build AMDGPU code that includes `mmhub_3_0_1_sh_mask.h` with the matching MMHUB 3.0.1 offset header; renamed or missing macros should fail at compile time.
- Static checks can verify that every visible `__SHIFT` has a matching `_MASK`, masks are aligned with their shift positions, and repeated families such as contexts 0-15 and invalidate engines 0-17 remain structurally identical where expected.
- Regeneration diffs should be reviewed against the authoritative MMHUB 3.0.1 register source, especially for VM context, invalidation, fault-status, aperture, and performance-counter fields.
- Hardware smoke tests should cover GPU initialization, VM context setup, page-table base/range programming, basic VRAM/system-memory access, and recovery after GPU reset.
- VM tests should change mappings, issue invalidations, and confirm no stale translations remain for selected VMIDs and address ranges.
- Fault tests should trigger controlled invalid/permission/range faults and verify decoded `MMVM_L2_PROTECTION_FAULT_STATUS` fields, captured fault addresses, interrupt/default-page behavior, and fault-clear sequencing.
- Suspend/resume and runtime power-management tests should verify that MMHUB context, aperture, clock-gating, and memory light-sleep settings are restored or reprogrammed correctly.
- SR-IOV or virtual-function tests should inspect PF/VF reset, active-function, VFID fault attribution, and per-PFVF cache fragment/bank fields where the platform supports them.
- Debug/performance tests can exercise MMVM L2, UTCL2, and ATC L2 counter select/enable/clear/read flows and confirm counter low/high values advance for expected workloads.

## Cross-Chunk Notes

- The previous chunk should contain the start of `MMVM_L2_PROTECTION_FAULT_CNTL2`, including shifts and masks before `OTHER_CLIENT_ID_PRT_FAULT_INTERRUPT_MASK`.
- The next chunk should complete `MM_ATC_L2_PERFCOUNTER_RSLT_CNTL`, including the masks after `STOP_TRIGGER_MASK` if present, and continue with subsequent ATC L2 definitions.
- The final per-file research document should treat this chunk as generated register metadata and should avoid inferring full VM/MMHUB behavior without the matching offset headers and consuming AMDGPU MMHUB/GMC code.
