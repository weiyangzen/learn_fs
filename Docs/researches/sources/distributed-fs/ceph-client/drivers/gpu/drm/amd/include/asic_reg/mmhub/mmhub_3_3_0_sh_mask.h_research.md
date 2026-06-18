# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002813`: lines 1-2363, `Docs/researches/chunks/subset-b-002813_research.md`
- `subset-b-002814`: lines 2364-4742, `Docs/researches/chunks/subset-b-002814_research.md`
- `subset-b-002815`: lines 4743-6722, `Docs/researches/chunks/subset-b-002815_research.md`

## Chunk Research

### subset-b-002813: lines 1-2363

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_sh_mask.h lines 1-2363

## Purpose

This chunk is the first portion of the generated MMHUB 3.3.0 shift/mask header used by the AMDGPU driver. It defines C preprocessor constants for bit positions and bit masks in MMHUB hardware registers, with this range focused on the `mmhub_dagbdec` address block and specifically the `DAGB0` data/address global block (DAGB) read/write client arbitration, bandwidth, credit, status, and initial performance counter fields.

The file has no executable logic, storage, or type definitions. Its purpose is to provide exact register-field encodings for `REG_SET_FIELD()`, `REG_GET_FIELD()`, direct mask composition, and register read/modify/write paths in the MMHUB v3.3 code. The paired offset header gives register addresses; this header gives the bit layout inside those registers.

## Important APIs, Types, And Macros

The public surface is entirely macro constants:

- Include guard: `_mmhub_3_3_0_SH_MASK_HEADER`.
- Repeated field encoding pattern: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.
- Read client registers: `DAGB0_RDCLI0` through `DAGB0_RDCLI30`.
- Write client registers: `DAGB0_WRCLI0` through `DAGB0_WRCLI30`.
- Read and write global DAGB controls: `DAGB0_RD_CNTL`, `DAGB0_WR_CNTL`, `DAGB0_RD_IO_CNTL`, `DAGB0_WR_IO_CNTL`, `DAGB0_RD_GMI_CNTL`, `DAGB0_WR_GMI_CNTL`.
- DAGB topology and clock controls: `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_DATA_DAGB`, `DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_WR_CGTT_CLK_CTRL`, `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_WR_CGTT_CLK_CTRL`.
- Per-client burst/timer packing registers: `DAGB0_*_MAX_BURST0..3` and `DAGB0_*_LAZY_TIMER0..3` for read address, write address, and write data paths.
- Virtual-channel controls: `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC5_CNTL`, `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC5_CNTL`, plus IO/GMI VC controls.
- Credit/status/override registers: TLB credits, storage pool credits, write data and atomic FIFO credits, pending busy bitmaps, no-allocate overrides, GPU snoop overrides, FIFO/credit full and empty status.
- Miscellaneous controls: `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, `DAGB0_CNTL_MISC2`.
- Performance counter start of range: `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, and the beginning of `DAGB0_PERFCOUNTER0_CFG` through `ENABLE_MASK` at line 2363. The rest of the performance counter configuration is outside this chunk.

The most common client field layout appears in every `DAGB0_RDCLI*` and `DAGB0_WRCLI*` macro family:

- `VIRT_CHAN`: 3-bit virtual channel selector.
- `CHECK_TLB_CREDIT`: single-bit TLB-credit gating.
- `URG_HIGH` and `URG_LOW`: urgency thresholds.
- `MAX_BW_ENABLE` and `MAX_BW`: maximum bandwidth limiter enable/value.
- `MIN_BW_ENABLE` and `MIN_BW`: minimum bandwidth reservation enable/value.
- `OSD_LIMITER_ENABLE` and `MAX_OSD`: outstanding-request limiter enable/value.

## Control Flow

There is no runtime control flow in this header. Control flow is created by code that includes it, notably `drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c`, which includes both `mmhub_3_3_0_offset.h` and this shift/mask header. That implementation uses the constants through AMDGPU register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and offset variants.

For this chunk, the effective control pattern is:

1. A caller reads or prepares a 32-bit MMHUB register value.
2. The caller uses a `*_MASK` to clear, test, or isolate a field.
3. The caller uses a `*__SHIFT` to position field values, usually indirectly through `REG_SET_FIELD()` or `REG_GET_FIELD()`.
4. The caller writes the composed value back to the MMHUB register.

For example, clock-gating and light-sleep control paths in `mmhub_v3_3.c` use fields from this header such as `DAGB0_CNTL_MISC2__DISABLE_RDRET_TAP_CHAIN_FGCG_MASK` and `DAGB0_CNTL_MISC2__DISABLE_WRRET_TAP_CHAIN_FGCG_MASK` when enabling or disabling fine-grain clock gating behavior.

## State And Persistence Behavior

The header itself is stateless and persistent only as source-code metadata. The state it describes lives in MMHUB hardware registers:

- Client arbitration state: virtual-channel assignment, urgency thresholds, bandwidth windows, outstanding depth limits, and TLB-credit checks.
- DAGB routing/configuration state: read address, write address, and write data DAGB enablement, jump-ahead behavior, self-initialization disablement, `WHOAMI`, and write/read jump mode where defined.
- Clock and power state: CGTT on-delay, off-hysteresis, light-sleep assertion hysteresis, minimum memory-gated light sleep, CGLS/LS disables, and busy overrides.
- Credit state: TLB credits, storage pool credits, write data burst credits, atomic credits, data FIFO credits, and atomic FIFO credits.
- Diagnostic state: pending busy bitmaps, FIFO empty/full masks, credit fullness masks, delay injection selector fields, parity controls, and performance counter fields.

Any values programmed with these macros persist in device registers until reset, reprogramming, power-state transitions, or firmware/hardware ownership changes. Driver initialization, suspend/resume, GPU reset, power-management, and fault-recovery paths must assume register contents can change across those events and reapply required programming.

## Dependencies And Integration Points

Primary integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c` includes this header for MMHUB 3.3 register-field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_offset.h` supplies the matching register offsets. The shift/mask constants are only meaningful when paired with the corresponding `reg*` address macros.
- SOC15 register helpers in AMDGPU provide the read/write abstraction and field manipulation contracts.
- Client-ID tables in `mmhub_v3_3.c` align with the read/write client index space exposed here, especially the `DAGB0_RDCLI*` and `DAGB0_WRCLI*` per-client register families.
- MMHUB power, clock-gating, VM, fault, and performance paths rely on consistent field names across generated ASIC headers.

The macro naming is hardware-generated and tightly coupled to the AMD register specification. It is not a stable userspace API.

## Risks And Edge Cases

- Bitfield drift risk: any incorrect shift or mask can silently program the wrong hardware field. This can affect memory translation, client arbitration, power management, or fault handling.
- Cross-header coupling: using masks from this header with offsets from a different MMHUB generation can compile but target incompatible bit layouts.
- Partial-chunk boundary: line 2363 stops in the middle of `DAGB0_PERFCOUNTER0_CFG`; later performance counter fields and later address blocks are intentionally outside this research chunk.
- Repetition risk: the large `RDCLI*`, `WRCLI*`, burst, and lazy-timer families are mechanically repeated. Manual edits are high risk because a single outlier may be hard to notice in review.
- Register ownership risk: some fields are diagnostics or overrides (`*_BUSY_OVERRIDE`, `*_NOALLOC_OVERRIDE`, `*_GPU_SNOOP_OVERRIDE`, parity controls). Setting them outside hardware-recommended sequences can mask hangs, change cache/coherency behavior, or suppress useful error signaling.
- Width risk: all masks are expressed as 32-bit `L` constants. Callers should treat them as 32-bit register values and avoid signed arithmetic assumptions.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-behavior oriented:

- Build coverage for MMHUB v3.3 targets: the generated macros must compile when included by `mmhub_v3_3.c`.
- Register programming review: `REG_SET_FIELD()` and `REG_GET_FIELD()` uses should resolve to the intended mask/shift pair and not to a similarly named field from another ASIC header.
- Power-management tests: clock-gating and light-sleep paths should toggle the expected `DAGB0_CNTL_MISC2` and `*_CGTT_CLK_CTRL` bits without regressions in suspend/resume or runtime power transitions.
- GPU reset and VM initialization tests: reset paths should reinitialize DAGB/L1TLB-related fields needed after hardware reset.
- Fault and hang diagnostics: pending-busy, FIFO status, parity, and credit-full registers should remain readable and meaningful in debug dumps.
- Performance counter tests: counter low/high and counter configuration fields should expose coherent counter values once the rest of the `DAGB0_PERFCOUNTER*` macros from later lines are included by the final merged research.

## Chunk Scope Notes

The source file is larger than this work item. This document covers only lines 1-2363, which comprise the file prologue and most of the `mmhub_dagbdec` `DAGB0` register-field definitions up through the start of `DAGB0_PERFCOUNTER0_CFG`. Later `DAGB0` perf fields, SDP fields, and MMHUB MMU/L1TLB/L2TLB address blocks are outside this chunk and should be reconciled by the later merge lane with their corresponding chunk documents.

### subset-b-002814: lines 2364-4742

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_sh_mask.h lines 2364-4742

## Scope And Purpose

This chunk is part of AMDGPU's generated MMHUB 3.3.0 register field mask header. It contains no executable functions, C types, or storage; its API is a large set of preprocessor constants that pair hardware register fields with `*_MASK` and `*__SHIFT` values. Driver code uses those constants with matching register-address definitions from `mmhub_3_3_0_offset.h` and the AMDGPU register helpers to read, modify, and write MMHUB registers safely.

The range starts at the tail of `DAGB0_PERFCOUNTER0_CFG` and then covers the rest of the `DAGB0` SDP and performance-counter fields, PCTL power/deepsleep controls, L1 TLB status and performance/fault registers, standalone-walker VM controls, ATC L2 controls, normal VM L2 controls, protection fault reporting, PTE-cache debug access, credit-safety controls, and VM context control registers `MMVM_CONTEXT0_CNTL` through the beginning of `MMVM_CONTEXT7_CNTL`.

The content is hardware-facing register metadata. Its practical purpose is to make field extraction and field insertion exact for MMHUB virtual-memory bring-up, page-table walk/cache configuration, TLB invalidation and fault handling, display VMID setup, power gating, clock gating, performance counters, and low-level diagnostics. The file is under a Ceph source mirror path, but the code here is Linux AMDGPU driver register metadata, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no callable APIs or structs in this chunk. The important interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted raw bit mask in the 32-bit register.
- AMDGPU callers commonly use `REG_SET_FIELD(value, REGISTER, FIELD, new_value)` and `REG_GET_FIELD(value, REGISTER, FIELD)`, which depend on these exact macro names and values.
- The companion offset header supplies register addresses such as `regMMVM_L2_CNTL`, `regMMVM_CONTEXT0_CNTL`, `regMM_ATC_L2_MISC_CG`, and `regDAGB0_L1TLB_REG_RW_3_3`; this header only supplies the bit layout.

Major register families in this chunk:

- `DAGB0_PERFCOUNTER*_CFG`, `DAGB0_PERFCOUNTER_RSLT_CNTL`, and `DAGB0_L1TLB_REG_RW` expose DAGB performance-counter event selection, start/stop triggers, enable/clear controls, and L1 TLB register read/write controls.
- `DAGB0_SDP_*` describes the SDP interface: bandwidth throttles, priority overrides, read/write VC priority maps, client-to-VC mapping, enable, tag/response credits, VC reserve pools, error status, request policy, link-manager behavior, arbitration, clock gating, and latency-sampling controls.
- `PCTL_*` covers MMHUB power control: deep-sleep controls and overrides, page-gating ignore masks, slice busy/deepsleep allow masks, UTCL2/slice misc bits, register-engine execution and RAM access, state-save ranges/exclusion sets, status, and PCTL performance counters.
- `MMMC_VM_MX_L1_*` covers L1 TLB status for TLB instances 0-7, L1 perf counters, and TLS0 protection fault status/address fields.
- `MMVM_L2_SAW_*` defines standalone-walker L2 cache and context controls, page-table base/start/end registers, context-disable masks, and pipe-busy status fields.
- `MM_ATC_L2_*` defines address-translation cache controls: translation request sizing, invalidate/cache modes, cache data readout, status, clock/memory light sleep, and SDP port control.
- `MMVM_L2_*` defines the main MMHUB VM L2 cache, invalidation, dummy-page fault, protection-fault, identity aperture, bank selection, parity, clock-gating, GCR, PTE-cache dump, group realtime-class, and credit-safety fields.
- `MMVM_CONTEXT[0-7]_CNTL` defines per-VMID context enablement, page-table geometry, retry behavior, and per-fault interrupt/default-page routing bits.

## Control Flow

This header has no runtime control flow of its own. It affects caller control flow by defining the field names used by AMDGPU MMHUB setup and diagnostics code.

The primary consumer is `drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c`, which includes `mmhub_3_3_0_offset.h` and this `mmhub_3_3_0_sh_mask.h`. Typical flows are:

1. Read a 32-bit MMIO register with `RREG32_SOC15(MMHUB, 0, reg...)` or an offset variant.
2. Use `REG_SET_FIELD` or explicit mask operations to change a field defined in this header.
3. Write the result back with `WREG32_SOC15(...)`.
4. Use derived register distances such as `regMMVM_CONTEXT1_CNTL - regMMVM_CONTEXT0_CNTL` to iterate VM contexts with the same field layout.

Concrete integration examples in `mmhub_v3_3.c` include enabling the system domain with `MMVM_CONTEXT0_CNTL__ENABLE_CONTEXT`, selecting `PAGE_TABLE_DEPTH`, and disabling retry permission/invalid faults; configuring VMID contexts with `MMVM_CONTEXT1_CNTL` fields; initializing the main L2 cache through `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5`; programming standalone-walker context state through `MMVM_L2_SAW_CONTEXT0_CNTL` and `MMVM_L2_SAW_CNTL4`; and controlling MMHUB ATC clock/memory gating with `MM_ATC_L2_MISC_CG__ENABLE_MASK` and `MM_ATC_L2_MISC_CG__MEM_LS_ENABLE_MASK`.

The display resource files for DCN 3.5 and DCN 3.5.1 also include this header and use the MMHUB field namespace through generated register/shift/mask tables, especially for VMID register setup via `DCN20_VMID_MASK_SH_LIST`.

## State And Persistence Behavior

The header itself persists no state. The state described by these macros lives in MMHUB hardware registers and persists according to hardware reset, power-gating, suspend/resume, firmware, and driver reinitialization behavior.

State classes represented in this chunk include:

- VM context state: whether a context is enabled, page-table depth/block size, fault retry policy, and per-fault routing to interrupt or default page.
- VM L2 cache state: L2 cache enablement, fragment processing, PDE/PTE cache behavior, bank selection, invalidation controls, parity checking/injection, PTE-cache dump selection, and clock/light-sleep controls.
- Fault state: dummy-page fault addresses, L2 protection-fault status, faulting address, default fault address, client ID, RW class, walker/mapping/permission indicators, and sticky/more-fault style status bits.
- Address-translation cache state: ATC L2 translation request limits, invalidate modes, cache update modes, memory power/light-sleep bits, and status.
- Power-control state: deepsleep override, ignore, allow, busy, register-save, and PCTL status bits for UTCL2 and MMHUB slices.
- DAGB/SDP state: priority, bandwidth, VC mapping, credits, error latches, arbitration policy, request blocking, and clock-gating behavior.
- Observability state: performance-counter selection and result controls, latency-sampling fields, L1 TLB status fields, SAW pipe-busy state, and PTE-cache dump data.

Some fields are controls that remain programmed until another driver write or hardware reset. Others are status-only or sticky status, and this header does not encode access semantics such as read-only, write-one-to-clear, self-clearing, or latch-on-read. Callers must pair the masks with hardware documentation and established AMDGPU sequencing.

## Dependencies And Integration Points

This chunk depends only on the C preprocessor, AMDGPU's generated register-header naming convention, and the generic AMDGPU register helpers. It is meaningful only when included with the matching MMHUB 3.3.0 offset definitions and with helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Important integration points are:

- `amdgpu/mmhub_v3_3.c`: the main ASIC-specific MMHUB implementation for VM invalidation, GART enable/disable, L1 TLB setup, L2 cache setup, VM context configuration, standalone-walker setup, fault reporting, and ATC clock/memory gating.
- `amdgpu_vmhub` setup: `mmhub_v3_3_init()` records MMHUB register offsets and context/engine distances, then stores fault-enable masks composed from `MMVM_CONTEXT1_CNTL__*_FAULT_ENABLE_INTERRUPT_MASK` values.
- DCN 3.5/3.5.1 display resource code: includes the same MMHUB masks for generated VMID register descriptors used by display-side VM context handling.
- Power-management paths: fields in `PCTL_*`, `MM_ATC_L2_MISC_CG`, `MM_ATC_L2_MEM_POWER_LS`, `MMVM_L2_CGTT_CLK_CTRL`, and `DAGB0_SDP_CGTT_CLK_CTRL` connect MMHUB register layout to clock gating, light sleep, and deep-sleep behavior.
- Fault and debug paths: protection-fault status/address/default-address macros, PTE-cache dump macros, performance counters, latency sampling, and L1 TLB status fields support diagnostics and post-fault logging.

Because these names are generated and shared by many ASIC versions, small naming or value drift can break code that is otherwise source-compatible across MMHUB generations. The v3.3 implementation also uses a local alias for `regDAGB0_L1TLB_REG_RW_3_3`, so DAGB L1 TLB register access in this generation is particularly tied to the offset/mask pairing.

## Risks And Edge Cases

The primary risk is silent hardware misconfiguration. A bad shift or mask can make `REG_SET_FIELD` clear or set the wrong bits while preserving a valid C build. In this chunk, high-impact fields include `MMVM_CONTEXT*_CNTL` enable/fault bits, `MMVM_L2_CNTL*` cache and bank-selection fields, `MMVM_L2_PROTECTION_FAULT_CNTL*` default/interrupt/crash behavior, `MM_ATC_L2_CNTL*` cache/invalidation modes, and SDP credit/priority controls.

VM fault policy is especially sensitive. Incorrect defaults can turn expected page-fault interrupts into default-page redirects, suppress retry behavior, or trigger crash-on-fault behavior unexpectedly. The context registers repeat the same field layout for many VMIDs, so one wrong common field definition can affect all user VM contexts.

Cache and invalidation controls have broad blast radius. Incorrect values in `MMVM_L2_CNTL2` invalidation bits, bank selection, PTE/PDE cache mode fields, or ATC invalidate mode can leave stale translations visible to the GPU, causing memory corruption, VM faults, or device hangs that may only reproduce under page-table updates, GPU reset, virtualization, or display memory pressure.

The chunk contains many repetitive generated blocks. `PCTL_SLICE0_*` and `PCTL_SLICE1_*`, L1 TLB status registers 0-7, performance counters, `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT7_CNTL`, credit-safety groups, and register-save range/exclusion sets are vulnerable to copy/generation mistakes. A single inconsistent suffix or mask width could affect only one slice, context, or counter, making failures hardware- and workload-specific.

Power and clock controls need sequencing beyond what the header can express. Fields for deepsleep, light sleep, clock-gating disable, busy override, register-save ranges, and SDP/PCTL status are not safe to toggle arbitrarily. Callers need to respect IP block idle state, display use, firmware ownership, and suspend/resume ordering.

The requested line range has two boundary artifacts: line 2364 is only the final `DAGB0_PERFCOUNTER0_CFG__CLEAR_MASK` macro from a register that begins earlier, and line 4742 stops in the middle of the `MMVM_CONTEXT7_CNTL` mask list. The final per-file reconciliation should merge neighboring chunks before drawing conclusions about completeness of either register definition.

## Test Signals

Useful validation is mostly integration and hardware oriented:

- Build coverage for MMHUB 3.3.0 users should compile `mmhub_v3_3.c`, DCN 3.5, and DCN 3.5.1 with this header included. Missing or renamed macros should fail at compile time in `REG_SET_FIELD`, direct-mask, or generated register-table code.
- GART/MMHUB initialization should enable system and user VM contexts, program L2 cache controls, configure standalone walker state, disable identity apertures, and complete VM invalidation requests without hangs or timeout messages.
- VM fault tests should report coherent `MMVM_L2_PROTECTION_FAULT_STATUS` fields, fault addresses, client IDs, read/write classes, and `MORE_FAULTS`/walker/mapping/permission indicators.
- Page-table update stress should not show stale translations after invalidation, unexpected default-page hits, or GPUVM memory corruption. This is the strongest signal for L2/ATC invalidation and cache-field correctness.
- Suspend/resume, runtime power management, display hotplug, and clock-gating tests should not leave MMHUB, ATC L2, PCTL, or DAGB/SDP blocks stuck busy or unable to wake.
- Performance and diagnostic paths should be able to select/clear/read DAGB, PCTL, and L1 perf counters; latency sampling and PTE-cache dump controls should show expected ready/data behavior when supported.
- Regression symptoms from bad constants include GART enable failure, VMID setup failure, GPU page faults with wrong CID/RW decoding, display VMID faults, hangs during invalidation, faults redirected to the wrong default page, broken ATC light-sleep toggling, or slice-specific behavior differences between slice0 and slice1.

## Cross-Chunk Notes

Earlier chunks of `mmhub_3_3_0_sh_mask.h` define the beginning of the DAGB and L1 TLB register field namespace, including the start of `DAGB0_PERFCOUNTER0_CFG`. Later chunks complete `MMVM_CONTEXT7_CNTL` and continue with additional MMHUB 3.3.0 register masks. The final per-file document should treat the complete header as a generated register-layout contract for MMHUB 3.3.0 rather than as standalone algorithmic code.

### subset-b-002815: lines 4743-6722

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_sh_mask.h lines 4743-6722

## Scope

This chunk is the final generated shift/mask section of the AMDGPU MMHUB 3.3.0 register mask header. It contains only C preprocessor constants plus generated register/address-block comments. There are no functions, structs, enums, variables, allocations, locks, branches, loops, or direct MMIO accesses in this range.

The range starts in the tail of `MMVM_CONTEXT7_CNTL`, covers complete `MMVM_CONTEXT8_CNTL` through `MMVM_CONTEXT15_CNTL`, and then covers VM context disable bits, 18 invalidation-engine semaphore/request/ack/address-range families, page-table base/start/end address fields for contexts 0-15, per-PF/VF PTE cache fragment-size fields, VM L2/MMUTCL2/ATC/MML2TLB performance-counter fields, shared VM aperture/system-memory controls, IOMMU and translation-fault fallback controls, GPUVA/VMID translation-assist request/response fields, TLB status/TMZ controls, and the closing `#endif`.

Although the repository path is under a `ceph-client` source mirror, this file is AMD GPU MMHUB hardware register metadata, not distributed filesystem logic.

## Purpose

The purpose of this chunk is to publish bit-level field metadata for MMHUB 3.3.0 VM and MMUTCL2 registers. Each register field uses the AMD generated-header convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`: the 32-bit mask for extracting or composing the field.

The sibling `mmhub_3_3_0_offset.h` header provides register addresses such as `regMMVM_CONTEXT0_CNTL`, `regMMVM_INVALIDATE_ENG0_REQ`, `regMMVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32`, and `regMMUTCL2_TRANSLATION_BYPASS_BY_VMID`. This mask header provides the field packing used by AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and offset variants.

## Important Macro Families

### VM context control and context disable

The opening lines are a partial continuation of `MMVM_CONTEXT7_CNTL`, containing only the later protection-fault mask definitions. The complete definitions for context 7 start in the previous chunk.

`MMVM_CONTEXT8_CNTL` through `MMVM_CONTEXT15_CNTL` repeat the VM context-control layout: `ENABLE_CONTEXT`, page-table depth and block size, retry behavior for permission/invalid-page and other faults, and interrupt/default handling for range, dummy-page, PDE0, valid, read, write, and execute protection faults. `MMVM_CONTEXTS_DISABLE` provides one disable bit for each VM context 0-15.

These fields are core VM setup ABI. In `amdgpu/mmhub_v3_3.c`, the driver programs context control with `REG_SET_FIELD(..., MMVM_CONTEXT0_CNTL, ...)` and `REG_SET_FIELD(..., MMVM_CONTEXT1_CNTL, ...)`, then derives the shared VM-fault enable mask from `MMVM_CONTEXT1_CNTL__*_PROTECTION_FAULT_ENABLE_INTERRUPT_MASK`.

### TLB invalidation engines

`MMVM_INVALIDATE_ENG0_SEM` through `MMVM_INVALIDATE_ENG17_SEM` define the single-bit semaphore field for each invalidation engine.

`MMVM_INVALIDATE_ENG0_REQ` through `MMVM_INVALIDATE_ENG17_REQ` define the invalidation request payload: a 16-bit per-VMID invalidate bitmap, flush type, L2 PTE/PDE0/PDE1/PDE2 invalidation bits, L1 PTE invalidation, protection-fault status-address clearing, and 4K-page-only invalidation. `MMVM_INVALIDATE_ENG0_ACK` through `MMVM_INVALIDATE_ENG17_ACK` expose the matching per-VMID ack bitmap and semaphore ack bit.

`MMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through engine 17 define optional address-range fields for range-limited invalidation. Low registers contain `S_BIT` and low logical-page-address bits; high registers contain the high logical-page-address field.

`mmhub_v3_3.c` uses the engine-0 names as the base template, then computes `eng_distance` and `eng_addr_distance` from adjacent offset-header registers so one implementation can address multiple engines. That makes the uniform mask layout in this chunk part of the runtime invalidation contract.

### VM context page-table address ranges

For contexts 0-15, the chunk defines:

- `MMVM_CONTEXT*_PAGE_TABLE_BASE_ADDR_LO32/HI32`: page-directory entry low and high halves.
- `MMVM_CONTEXT*_PAGE_TABLE_START_ADDR_LO32/HI32`: logical page-number start low and high fields.
- `MMVM_CONTEXT*_PAGE_TABLE_END_ADDR_LO32/HI32`: logical page-number end low and high fields.

The base-address fields are full 32-bit halves. Start/end low halves are full 32-bit logical page numbers, while high halves use the low 4 bits. These fields back the GPU VM page-table root and valid virtual-address aperture programmed by MMHUB initialization and resume code.

### PTE fragment-size controls

`MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` defines four-bit fragment-size fields for VMIDs 1-7 and 13-15. `MMVM_L2_CONTEXT0_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` through `CONTEXT15` provide per-context fragment-size variants with `FRAGMENT_SIZE` and `SYSTEM_ACCESS_MODE` fields. These influence how the VM L2 caches page-table fragments and how system access mode is represented for a context.

### VM L2, MMUTCL2, ATC, and MML2TLB performance counters

The `mmhub_mmutcl2_mmvml2pldec` and `mmhub_mmutcl2_mml2tlbpldec` blocks define performance-counter configuration registers:

- `MMMC_VM_L2_PERFCOUNTER0_CFG` through `7_CFG`.
- `MMUTCL2_PERFCOUNTER0_CFG` through `3_CFG`.
- `MM_ATC_L2_PERFCOUNTER0_CFG` and `1_CFG`.
- `MML2TLB_PERFCOUNTER0_CFG` through `3_CFG`.

Each config family follows the same pattern: event selection start/end fields, performance mode, enable bit, and clear bit. The corresponding result-control registers select a counter, specify start/stop triggers, enable any counter, clear all counters, and stop all counters on saturation. Result registers expose low 32 counter bits and high/compare-value fields.

These fields are debug/performance instrumentation ABI. They do not count anything by themselves; runtime code must program event selectors, clear/enable counters, trigger collection, and read result registers.

### Shared VM aperture, system-memory, and clock/power fields

The `mmhub_mmutcl2_mmvmsharedpfdec` and `mmhub_mmutcl2_mmvmsharedvcdec` blocks define shared VM configuration fields, including NB MMIO base/limit, PCI control/arbitration, top-of-DRAM slot fields, FB offset, system-aperture default address halves, VM steering, shared virtualization reset request, memory power light-sleep controls, cacheable DRAM and local system-memory address start/end fields, aperture control, local FB address start/end and lock, FB location base/top, AGP top/bottom/base, and system aperture low/high addresses.

`MMUTCL2_CGTT_CLK_CTRL` and `MMUTCL2_CGTT_BUSY_CTRL` define clock-gating and busy-status behavior for MMUTCL2. `MMMC_SHARED_ACTIVE_FCN_ID`, `MMMC_VM_FB_NOALLOC_CNTL`, `MMUTCL2_HARVEST_BYPASS_GROUPS`, and `MMUTCL2_GROUP_RET_FAULT_STATUS` expose active function, LLC/no-allocate behavior, harvest bypass, and group return-fault status.

`MMVM_PCIE_ATS_CNTL` controls PCIe ATS behavior with `ATC_ATS_BLOCK_CLIENTID` and `ATC_ATS_BLOCK_CLIENTID_EN`, while `MMMC_VM_MX_L1_TLB_CNTL` controls L1 TLB enable, system access, invalidation, fragment processing, and local work-item/group behavior.

### IOMMU, translation fallback, and GPUVA/VMID translation assist

`MMUTCL2_TRANSLATION_BYPASS_BY_VMID` defines per-VMID translation-bypass and GPA-mode bitmaps. `MMVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, `MMVM_IOMMU_CONTROL_REGISTER`, and `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER` expose GPU-host translation, IOMMU enable, and performance optimization enable bits.

`MMUTC_TRANSLATION_FAULT_CNTL0/1` define the default physical page address and attributes used for translation faults: low address bits, high address bits, IO, SPA, and snoop flags. `MMUTCL2_VSCH_POWER_STATUS` exposes a powered-down status bit.

`MMUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL` enables the translation-assist path. Request registers carry address bits, VMID, VFID, VF flag, GPA mode, read/write/execute permission request bits, client ID, and request bit. Response registers return translated address bits, permission bits, fragment size, snoop/SPA/IO/TMZ attributes, no-PTE indication, memory type, memlog, NACK status, LLC no-allocate, and ACK.

### TLB status, TMZ, and credit safety

`MML2TLB_TLB0_STATUS` exposes busy, parity-error, and aperture-fault status bits. `MML2TLB_TMZ_CNTL` defines TMZ modulation. `MMUTCL2_L2TLB_CREDIT_SAFETY_FETCH_RDREQ` exposes a credit value and write bit for L2 TLB fetch read-request credit safety.

## APIs, Types, and Functions

This chunk exports preprocessor macros only. There are no C APIs, normal types, or callable functions.

The effective API is the generated naming contract used by AMDGPU register helpers:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg__field__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg__field_MASK`.
- `REG_SET_FIELD(orig, reg, field, value)` clears the field mask in `orig`, shifts `value` by the field shift, masks it, and ORs it into the result.
- `REG_GET_FIELD(value, reg, field)` masks and right-shifts a register value.

Because those helpers token-paste macro names, spelling is ABI-significant. A missing shift, missing mask, renamed register token, or renamed field token becomes a compile-time break in consumers.

## Control Flow

There is no executable control flow in the header. Runtime sequencing is supplied by AMDGPU MMHUB code that includes this file with `mmhub_3_3_0_offset.h`.

The hardware-level flow implied by the macros is:

1. Program VM context control and page-table base/start/end address registers for context 0 and user VM contexts.
2. Program shared apertures, FB/AGP/system-memory ranges, L1/L2 TLB controls, ATS/IOMMU controls, and fallback fault addresses as required by the ASIC initialization path.
3. Issue TLB invalidations through an invalidation engine by setting address-range registers when needed, composing an `MMVM_INVALIDATE_ENG*_REQ` value, and polling or checking `MMVM_INVALIDATE_ENG*_ACK`.
4. Use performance-counter config/result fields only in debug or profiling paths.
5. Read status/fault/power fields and clear or reprogram related state according to hardware sequencing rules outside this header.

## State and Persistence Behavior

The macros themselves hold no state. They describe MMIO-backed hardware state in MMHUB 3.3.0.

Persistent or semi-persistent hardware configuration represented here includes VM context enable/depth/block/fault policy, context-disable bits, page-table roots and virtual address ranges, PTE cache fragment sizes, system/local/FB/AGP aperture ranges, L1 TLB controls, ATS/IOMMU controls, translation-bypass bitmaps, translation-fault default page attributes, clock-gating controls, and credit-safety settings. These values generally persist until driver reprogramming, reset, suspend/resume restore, power-gating loss, firmware action, or ASIC reset.

Transient or side-effecting state includes invalidation request/ack/semaphore fields, clear bits, performance-counter clear/enable/result controls, busy/status bits, power-status bits, return-fault status, and translation-assist request/response handshake fields. The mask definitions do not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, or sequencing-sensitive; consumers must follow the hardware specification and existing MMHUB code.

## Dependencies and Integration Points

This chunk is paired with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_offset.h`, which supplies matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_3_0_default.h`, where default/reset values are represented for this generation.
- AMDGPU SOC15 register helpers and field helpers from the surrounding driver tree.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c`, which includes this mask header and its offset/default siblings. That source uses the VM context, invalidation-engine, address-range, and fault-enable macros in MMHUB setup, GART setup, VM invalidation, and VM hub descriptor initialization. Similar MMHUB generations, such as 4.1.0 and 4.2.0, use analogous macro families, but field presence and bit positions must remain matched to the active ASIC generation.

## Risks and Edge Cases

- Bitfield drift is high impact. Incorrect shifts or masks can silently program wrong VM context, invalidation, aperture, ATS/IOMMU, or TLB fields, causing GPU VM faults, stale translations, hangs, or memory corruption.
- The chunk begins mid-register. `MMVM_CONTEXT7_CNTL` is incomplete here; the previous chunk owns the shifts and earlier masks. Whole-file research must merge adjacent chunks before treating context 7 as fully described.
- Invalidation engine families are repeated 18 times with identical field layouts. A one-engine typo can break only specific invalidation paths or rings, making failures workload-dependent.
- Request/ack semantics are sequencing-sensitive. Incorrect `PER_VMID_INVALIDATE_REQ`, flush type, L1/L2/PDE invalidation bits, range fields, or ack polling can leave stale TLB entries or spin waiting for an ack that never matches.
- VM page-table address fields are safety-critical. Wrong page-directory base or start/end aperture values can route GPU virtual addresses to the wrong physical pages or expose invalid ranges.
- Shared aperture and FB/AGP/system ranges are platform-sensitive. Bad values can misclassify local memory, system memory, cacheable DRAM, MMIO, or AGP apertures.
- Translation bypass, GPA mode, GPU-host translation, and IOMMU enable fields affect virtualization and passthrough behavior. Incorrect per-VMID bitmaps can bypass translation for the wrong context or force the wrong address mode.
- Performance-counter fields include clear and enable bits. Debug code must avoid leaving counters enabled unintentionally or clearing state that another diagnostic path expects.
- Translation-assist request/response fields implement a handshake. Consumers must treat `REQ`, `ACK`, `NACK`, permission, no-PTE, and attribute bits as protocol state, not as ordinary passive configuration.

## Test Signals

Useful validation signals are build-time, generated-header consistency, and hardware VM behavior:

- Build AMDGPU with MMHUB 3.3 support enabled. Direct consumers in `mmhub_v3_3.c` should compile, especially token-pasted uses of `MMVM_CONTEXT*_CNTL` and `MMVM_INVALIDATE_ENG*_REQ`.
- Mechanical header checks should verify every complete field in this chunk has both `__SHIFT` and `_MASK`, masks align with shifts and widths, and fields inside one register do not overlap unexpectedly.
- Offset/mask consistency checks should pair registers in this chunk with matching names in `mmhub_3_3_0_offset.h`.
- GPU boot, suspend/resume, and reset tests should cover MMHUB VM context programming, GART setup, aperture setup, and restoration of context/page-table registers.
- VM stress workloads should exercise many VMIDs, page-table updates, evictions, and invalidations; stale translations, VM faults, or hangs are strong signals of bad invalidation or context-field definitions.
- Range-limited invalidation tests should verify `MMVM_INVALIDATE_ENG*_ADDR_RANGE_LO32/HI32` packing and `INVALIDATE_4K_PAGES_ONLY` behavior where hardware supports it.
- Virtualization and IOMMU tests should cover translation-bypass-by-VMID, GPA mode, GPU-host translation, and translation-assist request/response behavior.
- Performance-counter smoke tests should program VM L2, MMUTCL2, ATC L2, and MML2TLB counters, clear/enable them, trigger collection, read low/high results, and verify stop-on-saturate behavior where available.

## Cross-Chunk Notes

The previous chunk contains the beginning of `MMVM_CONTEXT7_CNTL`. This chunk reaches the end of `mmhub_3_3_0_sh_mask.h` and closes the include guard, so there is no following chunk for this source file. The final per-file report should reconcile context-control coverage across chunks 2 and 3 and avoid treating the partial context-7 masks at this chunk boundary as a complete register definition.
