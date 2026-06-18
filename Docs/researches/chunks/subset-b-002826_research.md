# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_sh_mask.h lines 4777-7155

## Scope And Purpose

This chunk is a generated AMDGPU MMHUB 9.1 register shift/mask header segment. It defines preprocessor constants for bitfield extraction and composition in MMHUB memory-arbiter, address-normalization/address-decode, power-control, L1 TLB status/performance, and the first L2 SAW control registers. The public interface is a dense set of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no functions, structs, enums, local variables, or executable branches in this range.

The chunk starts mid-way through `MMEA1_DRAM_RD_CLI2GRP_MAP0`, covering masks for client IDs 10-15 after the previous chunk's shifts and earlier masks. It then covers the rest of the `MMEA1` DRAM and IO arbitration/programming block, the MMHUB power-control block `mmhub_pctldec`, L1 TLB status and performance-counter blocks, and ends immediately after the field definitions for `VM_L2_SAW_CNTL2`; the next register comment, `VM_L2_SAW_CNTL3`, appears at the chunk boundary.

This file is paired with `mmhub_9_1_offset.h`. The offset header supplies the register addresses and base indices, while this `_sh_mask.h` header supplies each register's field layout for AMDGPU register helpers and direct mask operations.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The interface is macro-only and is consumed by register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_ENTRY`, and golden-register initialization macros.

Important macro families in this chunk include:

- `MMEA1_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA1_DRAM_WR_CLI2GRP_MAP0/1`: two-bit client-ID-to-group mappings for DRAM read/write clients. Each 32-bit register packs 16 client IDs, with `MAP0` covering CID0-CID15 and `MAP1` covering CID16-CID31. This chunk includes the tail of read `MAP0`, full read `MAP1`, and full write maps.
- `MMEA1_DRAM_RD_GRP2VC_MAP` and `MMEA1_DRAM_WR_GRP2VC_MAP`: three-bit mappings from four arbitration groups to virtual channels for DRAM read/write traffic.
- `MMEA1_DRAM_RD_LAZY`, `MMEA1_DRAM_WR_LAZY`, `MMEA1_DRAM_RD_CAM_CNTL`, `MMEA1_DRAM_WR_CAM_CNTL`, and `MMEA1_DRAM_PAGE_BURST`: queue delay, CAM depth, reorder limit, and page-burst controls for DRAM-side arbitration. These fields affect how grouped memory requests are buffered and issued.
- `MMEA1_DRAM_RD_PRI_*` and `MMEA1_DRAM_WR_PRI_*`: age, queuing, fixed-priority, urgency, and priority quantum fields. These macros define the programmable scheduling policy for low, medium, and high priority DRAM traffic and for priority levels 1-3.
- `MMEA1_ADDRNORM_*`: address normalization base, limit, offset, and hole-control fields. These define normalized address ranges and optional hole behavior before address decode.
- `MMEA1_ADDRDEC_*` and `MMEA1_ADDRDECDRAM_*`: DRAM address-decoder bank/rank/stack/pipe/column/row/chip-select mapping fields. They include bank configuration, misc channel settings, hash enable/selection fields, harvest enable, per-decoder chip-select base addresses, masks, address selection, column selection, and row-mask selection for primary and secondary chip selects.
- `MMEA1_IO_RD_*` and `MMEA1_IO_WR_*`: IO client-to-group maps, combine flush controls, group burst limits, age/queuing/fixed/urgency priority controls, urgency masks, and priority quanta. These mirror the DRAM arbitration controls for IO-side traffic.
- `MMEA1_SDP_*`: SDP arbitration, priority, credit, tag reserve, virtual-credit reserve, and request-control fields. These control arbitration between DRAM/IO paths, reserve resources, and limit or block requests through SDP.
- `MMEA1_MISC`, `MMEA1_LATENCY_SAMPLING`, `MMEA1_PERFCOUNTER_LO/HI`, `MMEA1_PERFCOUNTER0_CFG`, `MMEA1_PERFCOUNTER1_CFG`, and `MMEA1_PERFCOUNTER_RSLT_CNTL`: miscellaneous behavior, latency sampling, and two performance-counter configuration/result fields for the MMEA1 block.
- `MMEA1_EDC_CNT`, `MMEA1_EDC_CNT2`, `MMEA1_DSM_CNTL*`, `MMEA1_CGTT_CLK_CTRL`, `MMEA1_EDC_MODE`, `MMEA1_ERR_STATUS`, and `MMEA1_MISC2`: error-detection counter fields, deterministic/stress-mode or injection selection fields, clock-gating timing/override fields, EDC behavior fields, SDP response error status, and CSGROUP swap/burst-limit controls.
- `PCTL_MISC`, `PCTL_MMHUB_DEEPSLEEP`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_DAGB`: global MMHUB power-control, deep-sleep, override, ignore, and DAGB power-gating field layouts.
- `PCTL0_*`, `PCTL1_*`, and `PCTL2_*`: three repeated power-control instances with RENG RAM index/data/execute fields, misc lock/idle/deepsleep controls, and register-save range/exclusion fields for state-controller save/restore behavior.
- `MC_VM_MX_L1_TLB0_STATUS` through `MC_VM_MX_L1_TLB7_STATUS`: status bits for eight L1 TLB instances, exposing `BUSY` and `FOUND_PARITY_ERRORS`.
- `MC_VM_MX_L1_PERFCOUNTER0_CFG` through `MC_VM_MX_L1_PERFCOUNTER3_CFG`, `MC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, `MC_VM_MX_L1_PERFCOUNTER_LO`, and `MC_VM_MX_L1_PERFCOUNTER_HI`: L1 TLB performance-counter event selection, range end, mode, enable/clear controls, global result selection/triggers, 32-bit low counter value, and high counter/compare fields.
- `VM_L2_SAW_CNTL` and `VM_L2_SAW_CNTL2`: early L2 SAW translation-cache control fields, including L2 cache enablement, fragment processing, PTE/PDE endian swap modes, tag generation, LRU update on write, default-page routing, PDE cache split/effective sizes, identity access, swap-tag-index selection, L1/L2 invalidation controls, per-domain invalidation disable, BigK cache optimization/VMID mode, invalidate mode, and PDE cache effective size.

## Control Flow And State Behavior

This header has no runtime control flow. It is a compile-time register ABI for composing and decoding 32-bit MMIO register values. Runtime behavior happens only in code that includes this header and applies the masks/shifts while reading or writing MMHUB registers.

The `MMEA1` register fields describe persistent hardware configuration for MMHUB memory-client arbitration, address normalization, DRAM chip-select decode, IO arbitration, SDP credits/reserves, clock gating, error reporting, diagnostic/stress mode, and performance counting. Driver writes to these fields remain in the MMHUB register file until reset, power-gating restore, firmware or SMU programming, golden-register initialization, or later driver writes.

The `PCTL*` fields are tied to power management and register save/restore. The `RENG_RAM_*` fields select and write/read RENG microcode or RAM data, `RENG_EXECUTE` triggers execution with error/status bits, `*_MISC` controls register locks, idle thresholds, memory light-sleep enablement, forced power-gating state-controller completion, and deep-sleep behavior, and the `STCTRL_REGISTER_SAVE_*` fields define save ranges and exclusions. These are stateful power-management surfaces and may be sensitive to write ordering and power-state transitions.

The L1 TLB status registers are hardware-owned status. `BUSY` indicates active work in each TLB instance, while `FOUND_PARITY_ERRORS` exposes parity-detection state. The L1 performance-counter registers are mutable counter state controlled by event selection, mode, enable, clear, start/stop triggers, and stop-on-saturate fields.

The `VM_L2_SAW_CNTL*` fields configure translation-cache behavior and invalidation semantics. L2 cache enablement, fragment processing, PDE/PTE swap modes, default-page handling, identity mode, cache sizing, and invalidation bits directly affect MMHUB address translation and fault behavior. The header does not encode access type, reset value, sequencing, volatile status behavior, or whether fields are read-only, sticky, or write-one-to-clear.

## Dependencies And Integration Points

The immediate companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_1_offset.h`. Matching offsets in that header include `mmMMEA1_DRAM_RD_CLI2GRP_MAP0` at `0x0240`, the MMEA1 arbitration/address-decode/SDP/EDC range through `mmMMEA1_MISC2` at `0x034d`, `mmPCTL_MISC` through `mmPCTL2_STCTRL_REGISTER_SAVE_EXCL_SET1` at `0x0380`-`0x039f`, `mmMC_VM_MX_L1_TLB0_STATUS` through `mmMC_VM_MX_L1_PERFCOUNTER_HI` at `0x0588`-`0x059d`, `mmVM_L2_SAW_CNTL` and `mmVM_L2_SAW_CNTL2` at `0x0600`-`0x0601`, and `mmMC_VM_MX_L1_TLB_CNTL` later at `0x0833`.

The most direct AMDGPU integration points are MMHUB v1.7/v1.8 and GMC v9 code paths:

- `amdgpu/mmhub_v1_7.c` includes the MMHUB v1.7 shift/mask variant, which is the related generation-specific consumer for many same-named field contracts. It programs `MC_VM_MX_L1_TLB_CNTL` with `REG_SET_FIELD`, manages MMHUB cache/TLB state, and uses `SOC15_REG_FIELD` for MMEA1 RAS counter reporting.
- `amdgpu/mmhub_v1_8.c` similarly uses `MC_VM_MX_L1_TLB_CNTL` field macros and MMEA1 RAS register entries.
- `amdgpu/mmhub_v9_4.c` uses `mmMMEA1_EDC_CNT`, `mmMMEA1_EDC_CNT2`, `mmMMEA1_ERR_STATUS`, and `SOC15_REG_FIELD(MMEA1_*, ...)` for RAS reporting in a newer MMHUB family with similar MMEA1 error-counter naming.
- `amdgpu/gmc_v9_0.c` contains a golden-register programming entry for `mmMMEA1_DRAM_WR_CLI2GRP_MAP0`, tying the MMEA1 DRAM client-to-group map to GPU initialization defaults.

The macros depend on AMDGPU register-helper naming conventions. `REG_SET_FIELD(value, REG, FIELD, field_value)` and `REG_GET_FIELD(value, REG, FIELD)` require both `REG__FIELD_MASK` and `REG__FIELD__SHIFT` to exist and to describe a contiguous field. `SOC15_REG_FIELD(REG, FIELD)` uses the same macro names for RAS/error metadata. Direct MMIO writes use the matching offset macro from `mmhub_9_1_offset.h`.

## Risks And Edge Cases

- This header is a hardware ABI. A wrong mask or shift can silently produce valid C that programs the wrong arbitration, address-decode, TLB, power-control, error, or performance-counter behavior.
- The chunk starts mid-register. Whole-file reconciliation must connect the earlier `MMEA1_DRAM_RD_CLI2GRP_MAP0` shifts and masks for CID0-CID9 from the previous chunk with CID10-CID15 masks here.
- The MMEA1 client-to-group maps pack two-bit values at every even bit position. Off-by-two shifts can remap a different client ID while still remaining inside the register.
- The address decode fields are dense and repeated across CS0-CS3, secondary chip selects, decoder 0/1, bank/hash, column, row-mask, pipe, stack, subchannel, channel, and bank selectors. Copying a field from the wrong decoder or chip-select register can generate plausible but wrong DRAM interleave behavior.
- Several fields encode address fragments, limits, masks, or selectors rather than byte addresses. Callers must preserve the hardware-specific units expected by each register and should not treat all fields as full physical addresses.
- `MMEA1_EDC_CNT*`, `MMEA1_DSM_CNTL*`, `MMEA1_EDC_MODE`, and `MMEA1_ERR_STATUS` mix diagnostic counts, injection/select controls, bypass/propagation behavior, and clear/status bits. The shift/mask header does not say which bits are safe to write during normal operation.
- `PCTL*_RENG_EXECUTE` and `PCTL*_MISC` fields can affect power-control execution, locks, and deep-sleep/state-controller behavior. Incorrect writes may interfere with save/restore or power gating rather than failing locally.
- Full-width masks such as performance-counter low values or status bitmaps should be handled as unsigned 32-bit quantities. Signed promotion and format-string mistakes can make register dumps misleading.
- Cross-generation MMHUB headers use very similar names. Mixing `mmhub_9_1_sh_mask.h` fields with offsets from another MMHUB variant can compile but target the wrong register layout.

## Test And Validation Signals

There are no direct unit tests for this macro-only chunk. Useful validation signals are compile-time, static, and hardware-facing:

- Build AMDGPU configurations that include the MMHUB 9.1 offset and shift/mask headers and compile the relevant GMC/MMHUB/RAS paths.
- Run static mask/shift checks for this chunk: single-bit masks must equal `1 << shift`; multi-bit masks must be contiguous at the documented shift; repeated map fields should advance by two bits for client groups and by three bits for virtual-channel fields; full-width masks should have shift zero.
- Compare each register comment in this chunk against `mmhub_9_1_offset.h` to ensure a matching `mm*` offset and base index exist in the expected address block.
- Validate golden-register programming and register dumps for `MMEA1_DRAM_WR_CLI2GRP_MAP0`, especially client-group fields that are touched by initialization defaults.
- Exercise MMHUB initialization, suspend/resume, power-gating, deep-sleep, and RAS/error-reporting paths on hardware using this generation. Relevant signals include stable MMEA1 arbitration values, expected PCTL save/restore behavior, correct L1 TLB busy/parity status reporting, and coherent L1 performance-counter clear/enable/read behavior.
- For address-decode fields, useful validation is hardware register-dump comparison against known-good firmware tables and stress tests that cover VRAM interleave/channel/CS configurations.
- For `VM_L2_SAW_CNTL*`, VM/GART stress, TLB invalidation tests, page-fault injection, suspend/resume, and SR-IOV or virtualization scenarios should verify that cache enablement, invalidation, identity-mode, and default-page behavior match the programming guide.

## Chunk Notes For Merge Lane

This chunk covers the second half of the `MMEA1` block, the full `mmhub_pctldec` power-control block, L1 TLB status and performance-counter blocks, and the opening L2 SAW control fields. It begins after the `MMEA1_DRAM_RD_CLI2GRP_MAP0` field list has already started and ends just before `VM_L2_SAW_CNTL3` definitions continue in the next chunk, so whole-file reconciliation should merge both boundaries with adjacent chunk documents.
