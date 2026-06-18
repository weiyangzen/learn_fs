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
