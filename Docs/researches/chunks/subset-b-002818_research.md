# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_4_1_0_sh_mask.h lines 2374-4752

## Scope

This chunk covers a middle section of the generated MMHUB 4.1.0 shift/mask header. It starts inside the `DAGB1_RDCLI0` register definitions, continues through the rest of the `DAGB1` read-side decoder, the `mmhub_pctldec` power-control block, shared MMUTCL2/MMMC aperture registers, and the beginning of the MMVM L2 control/fault block. It ends inside `MMVM_L2_MM_GROUP_RT_CLASSES`, after masks for groups 0 through 26; masks for groups 27 through 31 are outside this chunk.

The file contains preprocessor constants only. There are no C functions, structs, runtime variables, or executable branches in this source range.

## Purpose

`mmhub_4_1_0_sh_mask.h` is a hardware register bitfield contract for AMDGPU's MMHUB 4.1.0 support. Each register field is represented by generated macros of the form:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit field mask.

The paired `mmhub_4_1_0_offset.h` header supplies register offsets such as `regDAGB1_CNTL_MISC2`, `regMMVM_L2_CNTL`, and `regMMVM_L2_PROTECTION_FAULT_STATUS_LO32`; this file supplies field layouts used by `REG_SET_FIELD`, `REG_GET_FIELD`, direct mask checks, and SOC15 MMIO access helpers.

## Important Macro Families

### DAGB1 Read Client and Arbitration Fields

The chunk begins after the first two `DAGB1_RDCLI0` shift macros. The visible part of `DAGB1_RDCLI0`, and the full `DAGB1_RDCLI1` through `DAGB1_RDCLI23` families, define repeated per-read-client policy fields:

- `VIRT_CHAN` selects a virtual channel.
- `CHECK_TLB_CREDIT` gates behavior on TLB credit availability.
- `URG_HIGH` and `URG_LOW` encode urgency thresholds.
- `MAX_BW_ENABLE`/`MAX_BW` and `MIN_BW_ENABLE`/`MIN_BW` encode per-client bandwidth limits or guarantees.
- `OSD_LIMITER_ENABLE` and `MAX_OSD` control outstanding-request limiting.

The `DAGB1_RD_CNTL`, `DAGB1_RD_IO_CNTL`, `DAGB1_RD_GMI_CNTL`, and `DAGB1_RD_ADDR_DAGB` families describe read-side DAGB routing and transaction behavior, including disabled-client bitmaps, IO/GMI virtual-channel enable/map fields, ARB/RETCREDIT forwarding, OSD limiting, address DAGB response behavior, and pipe stall controls.

`DAGB1_RD_ADDR_DAGB_MAX_BURST0/1/2` and `DAGB1_RD_ADDR_DAGB_LAZY_TIMER0/1/2` are packed per-output-DAGB tuning registers. `DAGB1_RD_VC0_CNTL` through `DAGB1_RD_VC5_CNTL`, plus `DAGB1_RD_IO_VC_CNTL` and `DAGB1_RD_GMI_VC_CNTL`, provide virtual-channel enablement and weight fields. `DAGB1_RD_TLB_CREDIT` sets available TLB credit and retry credit values.

`DAGB1_RDCLI_ASK_PENDING`, `GO_PENDING`, `GBLSEND_PENDING`, `TLB_PENDING`, `OARB_PENDING`, `ASK2ARB_PENDING`, `ASK2DF_PENDING`, `OSD_PENDING`, and `ASK_OSD_PENDING` expose read-client pipeline busy state. Several are full-width status bitmaps; `OSD_PENDING` is a single field. `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, and `DAGB1_RD_CREDITS_FULL` expose FIFO and credit saturation signals.

### DAGB1 Error, Clock, Performance, and SDP Fields

`DAGB1_SDP_ERR_STATUS` reports SDMA/SDP error state, including poisoned write, poisoned read-return, bad command, unexpected write-response, and unexpected read-response indicators. It also includes clearing bits for those latched error classes.

`DAGB1_RD_CGTT_CLK_CTRL`, `DAGB1_L1TLB_RD_CGTT_CLK_CTRL`, `DAGB1_SDP_CGTT_CLK_CTRL`, `DAGB1_DAGB_DLY`, `DAGB1_CNTL_MISC`, and `DAGB1_CNTL_MISC2` encode clock-gating, delay, and miscellaneous control. The v4.1.0 driver directly uses `DAGB1_CNTL_MISC2__DISABLE_RDRET_TAP_CHAIN_FGCG_MASK` and `DAGB1_CNTL_MISC2__DISABLE_WRRET_TAP_CHAIN_FGCG_MASK` when toggling medium-grain clock gating.

`DAGB1_PERFCOUNTER0_CFG` through `DAGB1_PERFCOUNTER2_CFG`, `DAGB1_PERFCOUNTER_RSLT_CNTL`, and result low/high fields provide event selection, counter mode, enable/clear strobes, start/stop triggers, any-counter enablement, clear-all, and stop-on-saturate controls.

The SDP-facing families include `DAGB1_SDP_RD_BW_CNTL`, `DAGB1_SDP_PRIORITY_OVERRIDE`, `DAGB1_SDP_RD_PRIORITY`, `DAGB1_SDP_RD_CLI2SDP_VC_MAP`, `DAGB1_SDP_ENABLE`, `DAGB1_SDP_CREDITS`, tag/VCC reserves, `DAGB1_SDP_REQ_CNTL`, `DAGB1_SDP_MISC_AON`, `DAGB1_SDP_MISC`, `DAGB1_SDP_MISC2`, `DAGB1_SDP_ARB_CNTL0/1`, and `DAGB1_SDP_LATENCY_SAMPLING`. These fields govern SDP read bandwidth and priority policy, client-to-VC mapping, enablement, credits, arbitration deadlines, retry/no-OSD handling, and latency sampler configuration.

### PCTL Power-Control Fields

The `mmhub_pctldec` block begins at line 3598. `PCTL_CTRL` packs soft reset, clock mux selection, deep-sleep timers, VDD/GFXOFF qualifiers, XGMI isolation, and service-request controls. `PCTL_MMHUB_DEEPSLEEP_IB`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_IGNORE_DEEPSLEEP_IB` define per-subblock deep-sleep input, override, and power-gating ignore bitmaps.

`PCTL_UTCL2_MISC`, `PCTL_SLICE0_CFG_DAGB_WRBUSY`, `PCTL_SLICE0_CFG_DAGB_RDBUSY`, `PCTL_SLICE0_CFG_DS_ALLOW`, `PCTL_SLICE0_CFG_DS_ALLOW_IB`, `PCTL_SLICE0_MISC`, and the matching `SLICE1` families describe deep-sleep allow/ignore behavior and slice miscellaneous control. Their repeated packed fields are power-state contracts for UTCL2, DAGB0-4, MMA, MME, MMR, RET, SDP, and VML2-facing logic.

`PCTL_RENG_CTRL` and the `PCTL_*_RENG_*`/`PCTL_*_STCTRL_REGISTER_SAVE_*` families define register-engine execution, RAM index/data access, and register-save ranges/exclusion sets for UTCL2 and slices 0/1. `PCTL_STATUS` reports deep-sleep state and power-controller state for UTCL2 and slices. `PCTL_PERFCOUNTER*` and `PCTL_RESERVED_*` provide power-control performance counter and reserved-register field layouts.

### MMMC and Shared MMUTCL2 Fields

The `mmhub_mmutcl2_mmvmsharedpfdec` block defines address and aperture controls that are programmed during MMHUB GART/system aperture setup:

- `MMMC_VM_NB_MMIOBASE`, `MMMC_VM_NB_MMIOLIMIT`, `MMMC_VM_NB_PCI_CTRL`, `MMMC_VM_NB_PCI_ARB`, `MMMC_VM_NB_TOP_OF_DRAM_SLOT1`, `MMMC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MMMC_VM_NB_UPPER_TOP_OF_DRAM2` describe NB/MMIO/PCI/TOM fields.
- `MMMC_VM_FB_OFFSET`, `MMMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB`, and `MMMC_VM_STEERING` define framebuffer offset, default system-aperture page address, and default steering.
- `MMMC_SHARED_VIRT_RESET_REQ` exposes VMC reset request/ack bits.
- `MMMC_VM_CACHEABLE_DRAM_ADDRESS_*`, `MMMC_VM_LOCAL_SYSMEM_ADDRESS_*`, `MMMC_VM_LOCAL_FB_ADDRESS_*`, and `MMMC_VM_LOCAL_FB_ADDRESS_LOCK_CNTL` define cacheable/local address ranges and lock behavior.
- `MMMC_VM_APT_CNTL` encodes aperture translation policy, including direct-system enable, forced uncached memory type, fragment interaction mode, local checks, 2M fragment capping, and local-sysmem aperture policy.
- `MMUTCL2_CGTT_CLK_CTRL`, `MMUTCL2_CGTT_BUSY_CTRL`, `MMUTCL2_HARVEST_BYPASS_GROUPS`, `MMUTCL2_GROUP_RET_FAULT_STATUS`, and `MMMC_SHARED_ACTIVE_FCN_ID` expose shared UTCL2 clock/busy, harvest bypass, group fault, and active function-ID state.

### MMVM L2 Control and Fault Fields

The `mmhub_mmutcl2_mmvml2pfdec` block starts in this chunk and includes:

- `MMVM_L2_CNTL`, with L2 cache enablement, fragment processing, endian swap, default page-out routing, PDE0 tag mode, LRU update, PDE fault classification, identity-access mode, and identity fragment size.
- `MMVM_L2_CNTL2`, with global invalidate controls, per-domain invalidate-disable bits, big-K disable controls, fragment-size disable, VMID passthrough mode, physical address masking, cache invalidation mode, invalidation clock-gating disable, and bank-select reserved CID.
- `MMVM_L2_CNTL3`, with update mode, bank/select, force-miss, cache level, context count, fragment size, cache sharing mode, and cache-size fields.
- `MMVM_L2_CNTL4`, with 4K partition count, physical tap request controls, MM non-real-time and soft-real-time IFIFO active transaction limits, BPM/CG override, foreground clock-gating control, and VFIFO behavior.
- `MMVM_L2_STATUS`, exposing busy flags, context/domain busy flags, and parity-error discovery for PTE and PDE caches.
- `MMVM_DUMMY_PAGE_FAULT_CNTL` and `MMVM_DUMMY_PAGE_FAULT_ADDR_LO32/HI32`, which control and report dummy-page fault behavior.
- `MMVM_INVALIDATE_CNTL`, which provides invalidation mode selection.

The protection-fault families are central to runtime error handling. `MMVM_L2_PROTECTION_FAULT_CNTL` controls clearing/updating the latched fault address, default enables for range/PDE/translation/NACK/dummy/valid/read/write/execute fault classes, per-client no-retry interrupt masks, other-client interrupt behavior, and crash-on-fault bits. `MMVM_L2_PROTECTION_FAULT_CNTL2` adds retry-fault interrupt and active-page-migration PTE behavior. `MMVM_L2_PROTECTION_FAULT_MM_CNTL3/4` expose VML1 read/write no-retry interrupt masks.

`MMVM_L2_PROTECTION_FAULT_STATUS_LO32` decodes latched fault details: more faults, walker error, permission fault bitmap, mapping error, client ID, read/write direction, atomic, VMID, VF flag, VFID, PRT, and uncorrectable-error state. `MMVM_L2_PROTECTION_FAULT_STATUS_HI32` provides `FED`. The fault address/default address and identity aperture families split logical or physical page numbers across low 32-bit and high 4-bit fields.

`MMVM_L2_MM_GROUP_RT_CLASSES` begins at the end of this chunk. It maps groups 0 through 31 to one-bit real-time class fields, but only masks through group 26 are visible here.

## Control Flow

There is no local control flow in the header. Runtime sequencing is in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.c`, which includes both `mmhub_4_1_0_offset.h` and this shift/mask header.

The main v4.1.0 flows using fields from this chunk are:

- `mmhub_v4_1_0_init_system_aperture_regs()` programs system aperture/default-page registers and writes `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_LO32/HI32`; it also enables `MMVM_L2_PROTECTION_FAULT_CNTL2.ACTIVE_PAGE_MIGRATION_PTE_READ_RETRY`.
- `mmhub_v4_1_0_init_cache_regs()` programs `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5` during GART enablement. This chunk supplies the masks for the first four of those registers.
- `mmhub_v4_1_0_disable_identity_aperture()` writes the identity aperture low/high and physical offset registers, using the register offsets paired with the field definitions in this chunk.
- `mmhub_v4_1_0_print_l2_protection_fault_status()` decodes `MMVM_L2_PROTECTION_FAULT_STATUS_LO32` with `REG_GET_FIELD` to print CID, RW, more-faults, walker-error, permission, and mapping-error diagnostics.
- `mmhub_v4_1_0_set_fault_enable_default()` writes `MMVM_L2_PROTECTION_FAULT_CNTL` default fault-enable bits and crash-on-fault bits depending on the requested fault policy.
- `mmhub_v4_1_0_update_medium_grain_clock_gating()` toggles `DAGB1_CNTL_MISC2` tap-chain clock-gating disable masks along with the matching DAGB0 register.

Most other fields in this chunk are passive until used by initialization, debug, clock/power management, profiling, or bring-up code.

## State and Persistence Behavior

The header persists no software state. It names hardware state held in MMIO registers:

- DAGB1 read-client, virtual-channel, bandwidth, SDP, and clock-gating registers persist read fabric policy until reset or reprogramming.
- DAGB1 pending/FIFO/credit/error registers expose transient or latched hardware state; error clear bits are command-style fields.
- Performance-counter registers retain event selection, mode, enable state, and accumulated results until cleared, saturated, reset, or reprogrammed.
- PCTL deep-sleep, override, register-engine, and save-range registers persist low-power policy and save/restore configuration across the relevant power-control flows.
- MMMC aperture and default-page registers persist address-translation windows used by MMHUB memory accesses.
- MMVM L2 control registers persist cache/TLB and invalidation policy; `MMVM_L2_CNTL2` invalidation bits are command-like controls.
- Protection-fault status/address registers latch fault information until cleared or updated according to `MMVM_L2_PROTECTION_FAULT_CNTL`; the default address registers persist fallback page locations.

SR-IOV matters for persistence and ownership. The v4.1.0 driver skips several system-aperture, cache, identity-aperture, and fault-default writes when running as a VF because those registers are host/PF-owned.

## Dependencies and Integration Points

The direct integration point is AMDGPU MMHUB 4.1.0 support:

- `amdgpu/mmhub_v4_1_0.c` includes this header and uses its field names through `REG_SET_FIELD`, `REG_GET_FIELD`, and direct mask operations.
- `mmhub_4_1_0_offset.h` supplies the `reg*` MMIO offsets. These shift/mask macros are not independently sufficient for register access.
- `soc15_common.h` and the SOC15 access helpers provide `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_OFFSET`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.
- Common VM hub code consumes fields initialized by `mmhub_v4_1_0_init()`, including protection-fault status/control offsets and invalidation engine spacing.
- Power-management integration reaches this chunk through `mmhub_v4_1_0_set_clockgating()`, which updates DAGB0/DAGB1 clock-gating masks.
- Diagnostic integration reaches the protection-fault status fields through `amdgpu_mmhub_client_name()` and the `mmhub_client_ids_v4_1_0` CID table.

Because this is a generated hardware definition, updates should come from the AMD register-generation source rather than manual edits to individual masks.

## Risks and Edge Cases

- The chunk starts mid-register. `DAGB1_RDCLI0__VIRT_CHAN__SHIFT` and `CHECK_TLB_CREDIT__SHIFT` are in the preceding chunk, while the remaining `DAGB1_RDCLI0` shifts and all masks are here.
- The chunk ends mid-register. `MMVM_L2_MM_GROUP_RT_CLASSES` masks for groups 27 through 31 are outside this range, so a final merged report must join the next chunk before claiming complete coverage of that register.
- Repeated register families are copy-sensitive. A single incorrect client number in `DAGB1_RDCLI[0-23]`, virtual-channel, pending, or SDP macros could affect one client path while leaving most traffic apparently healthy.
- Field drift in `MMVM_L2_CNTL*` can cause severe GPUVM failures: stale translations, missed invalidations, incorrect default-page routing, bad cache sizing, or page-table walker behavior changes.
- Protection-fault field errors affect both fault policy and diagnostics. Incorrect clear/update bits may hide the first faulting address; incorrect CID/RW masks can misattribute a bad client; incorrect crash-on-fault bits can change recovery behavior.
- `CLIENT_ID_NO_RETRY_FAULT_INTERRUPT` is a wide packed mask and `MMVM_L2_PROTECTION_FAULT_STATUS_LO32.CID` spans bits 9-17. Callers must not assume small client IDs or a single-client-only fault source.
- Several fields are strobe or command style (`CLEAR`, error clear, invalidate, register-engine execute). Treating them as durable settings can clear evidence or trigger hardware work unexpectedly.
- PCTL deep-sleep and register-save fields affect low-power transitions. Bad masks can produce suspend/resume instability that may not appear under normal runtime VM tests.
- Reserved fields such as `PCTL_RESERVED_*` dummy fields should not be repurposed without hardware documentation.

## Test Signals

Useful validation signals for this chunk are hardware-facing and integration-oriented:

- Build coverage of `amdgpu/mmhub_v4_1_0.c` verifies that all `REG_SET_FIELD`/`REG_GET_FIELD` references to `MMVM_L2_CNTL*`, `MMVM_L2_PROTECTION_FAULT_*`, and `DAGB1_CNTL_MISC2` still match generated macro names.
- MMHUB v4.1.0 GART enablement should complete `mmhub_v4_1_0_gart_enable()` without VM faults: aperture setup, TLB setup, L2 cache setup, identity aperture disable, VMID configuration, and invalidation range programming should all succeed.
- GPUVM stress tests that allocate, evict, update page tables, and invalidate VMIDs should not show stale translations or hangs in invalidation wait paths.
- Negative-access or fault-injection tests should produce meaningful `MMVM_L2_PROTECTION_FAULT_STATUS_LO32` logs, including CID, RW, walker error, permission, mapping, and more-faults decoding.
- Toggling fault-default policy through AMDGPU fault handling should show the expected change between default-page routing and crash/no-retry behavior.
- Clock-gating tests on supported hardware should exercise `mmhub_v4_1_0_set_clockgating()` and confirm DAGB1 remains functional with `DAGB1_CNTL_MISC2` read/write return tap-chain FGCG masks enabled and disabled.
- Suspend/resume or runtime power-management tests should watch PCTL status and deep-sleep behavior for hangs, register-save failures, or lost MMHUB aperture/cache configuration.
- Debug/profiling coverage can validate DAGB1 and PCTL performance-counter selection, clear, enable, saturation, and result-read behavior.
