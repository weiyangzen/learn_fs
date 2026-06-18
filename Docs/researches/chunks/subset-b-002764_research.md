# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 14144-16497

## Scope And Purpose

This chunk is a generated AMDGPU MMHUB 1.7 register bitfield header slice. It contains preprocessor constants only: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` definitions for the `MMEA1` register range. There are no functions, structs, storage objects, loops, branches, or runtime side effects in this source range.

The macros describe how software should encode and decode 32-bit MMHUB MMIO register values for the second memory-management engine aperture/range (`MMEA1`). The covered register families span GMI request grouping and arbitration, address normalization and address decode, IO request grouping and priority, SDP arbitration and credit controls, miscellaneous local controls, latency/performance counter controls, RAS/EDC counters, and diagnostic/error-injection controls. These definitions are meant to be paired with register offset macros from `mmhub_1_7_offset.h` and access helpers in AMDGPU MMHUB code.

The chunk begins in the tail of `MMEA1_GMI_RD_CLI2GRP_MAP1` and ends after `MMEA1_DSM_CNTL2`. Adjacent chunks are needed for a complete whole-register view of the first and last registers.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this range. The interface is the macro namespace consumed by C code through register-field helpers such as `SOC15_REG_FIELD()` and read/modify/write code.

Important macro groups in this chunk:

- `MMEA1_GMI_RD_CLI2GRP_MAP1`, `MMEA1_GMI_WR_CLI2GRP_MAP0`, and `MMEA1_GMI_WR_CLI2GRP_MAP1`: two-bit client-ID-to-group mappings. `CID0` through `CID31` are packed at two-bit intervals, allowing read/write GMI request clients to be assigned to one of four groups.
- `MMEA1_GMI_RD_GRP2VC_MAP` and `MMEA1_GMI_WR_GRP2VC_MAP`: three-bit group-to-virtual-channel selectors for four GMI groups.
- `MMEA1_GMI_RD_LAZY` and `MMEA1_GMI_WR_LAZY`: request accumulation and lazy dispatch controls. The fields include per-group delays plus `REQ_ACCUM_THRESH`, `REQ_ACCUM_TIMEOUT`, and `REQ_ACCUM_IDLEMAX`.
- `MMEA1_GMI_RD_CAM_CNTL` and `MMEA1_GMI_WR_CAM_CNTL`: per-group CAM depth and reorder-limit fields, plus `REFILL_CHAIN` and `PAGEBASED_CHAINING` control bits.
- `MMEA1_GMI_PAGE_BURST`: read/write page burst low/high limits for GMI paths.
- `MMEA1_GMI_RD_PRI_*` and `MMEA1_GMI_WR_PRI_*`: age, queuing, fixed priority, urgency, urgency masking, and quantum priority layouts. These fields tune how GMI reads and writes age, queue, mask urgent clients, and map request groups into priority classes.
- `MMEA1_ADDRNORM_*`: base/limit/offset and mega-base/mega-limit fields for normalized address ranges. These macros also define DRAM/GMI hole controls, non-power-of-two channel configuration, global controls, and masking controls.
- `MMEA1_ADDRDEC_*`: bank config, misc config, harvest enable masks, per-address-decoder base addresses, address masks, address config, address select fields, column select fields, and row/rank/misc select fields for decoder instances 0, 1, and 2. The naming covers normal and secondary chip-select forms such as `CS01`, `CS23`, `SECCS01`, and `SECCS23`.
- `MMEA1_IO_RD_CLI2GRP_MAP*` and `MMEA1_IO_WR_CLI2GRP_MAP*`: IO client-ID-to-group mappings that mirror the GMI two-bit-per-client scheme for IO read and write traffic.
- `MMEA1_IO_RD_COMBINE_FLUSH` and `MMEA1_IO_WR_COMBINE_FLUSH`: flush controls for IO request combining, including `GROUPx_FLUSH` fields and a `FORCE_COMBINE_FLUSH` bit.
- `MMEA1_IO_GROUP_BURST`, `MMEA1_IO_RD_PRI_*`, and `MMEA1_IO_WR_PRI_*`: IO-side burst, aging, queueing, fixed priority, urgency, urgency masking, and priority quantum layouts.
- `MMEA1_SDP_ARB_DRAM`, `MMEA1_SDP_ARB_GMI`, and `MMEA1_SDP_ARB_FINAL`: scheduler/arbitration fields for DRAM, GMI, and final arbitration. Fields include read/write priority, round-robin enable bits, no-starve controls, write-combine controls, and starve thresholds.
- `MMEA1_SDP_{DRAM,GMI,IO}_PRIORITY`, `MMEA1_SDP_CREDITS`, `MMEA1_SDP_TAG_RESERVE*`, `MMEA1_SDP_VCC_RESERVE*`, `MMEA1_SDP_VCD_RESERVE*`, and `MMEA1_SDP_REQ_CNTL`: request-class priorities, credit limits, tag and virtual-channel reserve fields, and request mode controls.
- `MMEA1_MISC`: operational and debug control bits for channel masks, urgent propagation, timeout or stall behavior, write-combine behavior, and clock/power related toggles.
- `MMEA1_LATENCY_SAMPLING`: latency sampling control, address/source matching, mode selection, and threshold/counter fields for observing MMHUB request latency.
- `MMEA1_PERFCOUNTER_LO`, `MMEA1_PERFCOUNTER_HI`, `MMEA1_PERFCOUNTER0_CFG`, `MMEA1_PERFCOUNTER1_CFG`, and `MMEA1_PERFCOUNTER_RSLT_CNTL`: 64-bit performance counter result fields and control fields for event selection, modes, enable/clear, trigger selection, global enable, global clear, and stop-on-saturation behavior.
- `MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2`: two-bit packed error counters for SEC, DED, and SED events across DRAM read/write command memory, write data memory, return tag memory, IO command/data memory, GMI command/page/data memory, and MAM D0-D3 memories.
- `MMEA1_DSM_CNTL` and `MMEA1_DSM_CNTLA`: diagnostic single-write/DSM irritator data controls for command, data, page, return-tag, IO, GMI, and MAM-related memories.
- `MMEA1_DSM_CNTLB`: present only as a register comment in this line range; no fields are defined in this chunk.
- `MMEA1_DSM_CNTL2`: diagnostic error-injection enables and injection-delay selectors for DRAM, return-tag, GMI command, and GMI write data memories, plus a shared `INJECT_DELAY` field.

## Control Flow And State Behavior

This header chunk has no local control flow. Its contribution is compile-time substitution: consumers include the header, combine a register offset with a mask/shift pair, and then read, write, or decode a hardware register.

Runtime state is entirely in the GPU MMHUB hardware. The `MMEA1` registers described here influence how MMHUB routes and prioritizes memory traffic, how addresses are normalized and decoded, how SDP arbitration allocates credits and reserves tags/virtual channels, how performance and latency sampling are configured, and how RAS diagnostic counters or injection controls are interpreted.

Persistence is hardware-defined. Programmed arbitration, priority, address-decode, diagnostic, and performance-counter values can persist until overwritten by driver/firmware, reset by GPU reset, cleared by counter-control bits, or lost during power-gating/suspend/resume depending on the register block. The header does not cache values, manage ownership, serialize access, or provide restore sequencing.

The most visible consumer in this source tree is `drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c`. That file includes both `mmhub_1_7_offset.h` and this mask header, then builds RAS error counter tables with `SOC15_REG_ENTRY(MMHUB, 0, regMMEA1_EDC_CNT*)` and `SOC15_REG_FIELD(MMEA1_EDC_CNT*, ...)`. The field macros from this chunk therefore become metadata for extracting packed SEC/DED/SED counts from EDC counter registers.

## Dependencies And Integration Points

This chunk depends on matching MMHUB 1.7 register address definitions. The mask header alone cannot access hardware; it must be paired with `regMMEA1_*` offsets and base-index macros in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`.

Primary integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` includes `mmhub/mmhub_1_7_sh_mask.h`, `mmhub/mmhub_1_7_offset.h`, `soc15_common.h`, and `soc15.h`. Register access is routed through SOC15 helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and table helpers such as `SOC15_REG_ENTRY` and `SOC15_REG_FIELD`.
- The `MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2` fields are used by the MMHUB RAS error-query table. Entries name memory blocks such as `MMEA1_DRAMRD_CMDMEM`, `MMEA1_GMIRD_CMDMEM`, `MMEA1_GMIWR_DATAMEM`, and `MMEA1_MAM_D0MEM`, then associate each with SEC/DED/SED field masks from this chunk.
- Adjacent generated MMHUB headers provide equivalent `MMEA0`, `MMEA2`, and later `MMEA1_EDC_CNT3` definitions. The C consumer treats these ranges as a repeated hardware pattern, so consistency across generated macro names matters.
- GMI and IO grouping/priority fields are integration surfaces for firmware or driver initialization code that programs request classes. Even when not directly referenced by current C code in this repository snapshot, these macros document the hardware ABI used by register dumps, bring-up scripts, diagnostics, or future MMHUB tuning paths.
- Performance counter and latency sampling fields integrate with MMHUB debug/perf tooling. A caller must use the offset header to select `regMMEA1_PERFCOUNTER*` or `regMMEA1_LATENCY_SAMPLING`, and then use these masks to preserve unrelated bits during read-modify-write.
- DSM and error-injection fields are diagnostic/RAS-facing. They should only be used by carefully gated test paths, because they can deliberately perturb hardware memory structures.

## Risks And Edge Cases

- Hardware contract drift is the main risk. These constants must match the MMHUB 1.7 register specification exactly; an incorrect mask or shift can silently program the wrong arbitration class, decode the wrong address bits, corrupt performance counter configuration, or misreport RAS error counts.
- This chunk starts mid-register and ends before the next DSM register family is complete. Line 14144 is already inside `MMEA1_GMI_RD_CLI2GRP_MAP1`, and line 16497 ends with `MMEA1_DSM_CNTL2`. The merge lane should avoid treating this chunk as a complete `MMEA1` description.
- Many fields are tightly packed two-bit or three-bit values. Callers must mask and shift unsigned 32-bit values; signed arithmetic or host-width assumptions can break high-bit fields such as `0xC0000000L`, `0xFC000000L`, and `0xFF000000L`.
- Several register families have read and write variants with nearly identical field names. Mechanical edits can easily swap `RD` and `WR`, `GMI` and `IO`, or `DRAM` and `GMI`, which would compile but alter the wrong traffic path.
- `MMEA1_ADDRDEC*` macros are repetitive across decoder instances and chip-select pairs. Incorrectly mixing `ADDRDEC0`, `ADDRDEC1`, or `ADDRDEC2` fields, or `CS01` versus `CS23`, could produce invalid address interleave or harvesting behavior.
- RAS counters are packed into two-bit fields. Saturation, clear-on-read, or clear-by-control semantics are not described in the header; consumers must follow the MMHUB RAS code and hardware specification when accumulating or clearing counts.
- Performance counter and latency-sampling configuration can be destructive to in-flight debug sessions. The result-control fields include clear and stop-on-saturation bits, so callers should preserve unrelated fields and coordinate with other performance tooling.
- DSM and error-injection fields deliberately alter memory diagnostic behavior. Accidentally enabling injection or single-write irritator controls can create artificial SEC/DED/SED events or destabilize the MMHUB path during normal operation.

## Test And Validation Signals

There are no direct unit tests for these preprocessor definitions. Practical validation is integration and hardware oriented:

- Build coverage for `drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c` with this header included, especially the RAS table entries that use `SOC15_REG_FIELD(MMEA1_EDC_CNT, ...)` and `SOC15_REG_FIELD(MMEA1_EDC_CNT2, ...)`.
- Static generation checks can verify that every `_MASK` aligns with its matching `__SHIFT`, that repeated `CID` mappings advance by two bits, that group-to-VC fields advance by three bits, and that full-width result fields use shift zero with `0xffffffffL`.
- Cross-header checks should compare `MMEA1_*` mask names against `regMMEA1_*` offsets in `mmhub_1_7_offset.h`; missing offset/mask pairs indicate incomplete generation or a register that cannot be accessed symbolically.
- RAS runtime validation should confirm that MMHUB v1.7 error-query paths report expected SEC/DED/SED counters for `MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2`, and that clear paths do not leave stale counts.
- Register-dump or debugfs validation can exercise performance counter and latency sampling fields by programming event selection, clearing counters, reading low/high result registers, and confirming that unrelated bits remain unchanged.
- Hardware bring-up or firmware validation should cover GMI/IO arbitration programming, address normalization/address decode layouts, and SDP credit/reserve settings under memory stress, suspend/resume, and GPU reset.

## Chunk Notes For Merge Lane

This is one chunk of a very large generated MMHUB 1.7 mask header. Merge with adjacent chunks before producing final whole-file conclusions, especially because this chunk begins after the start of `MMEA1_GMI_RD_CLI2GRP_MAP1` and stops before subsequent DSM/control families. The source-tree-aligned output for this item is this chunk document only.
