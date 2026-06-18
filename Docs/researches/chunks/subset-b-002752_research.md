# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_0_sh_mask.h lines 4743-7093

## Scope

This chunk covers generated shift and mask macros from the AMD MMHUB 1.0 register mask header. It starts in the tail of `MMEA0_IO_WR_PRI_URGENCY_MASK`, covering only the `CID22` through `CID31` mask values, and then covers the rest of the visible `MMEA0` memory-export/arbitration support fields through `MMEA0_MISC2`. It then enters a large `MMEA1` section covering DRAM client grouping, DRAM and IO priority/arbitration, address normalization and address decoding, SDP arbitration/crediting, latency sampling, performance counters, EDC counters, and the beginning of DSM/error-injection control.

The file is a generated-style C preprocessor hardware ABI map. This chunk defines constants only. There are no functions, structs, storage objects, direct register accesses, loops, conditionals, or local runtime control flow in the covered lines.

## Purpose

The purpose of this section is to provide bit-level field metadata for MMHUB 1.0 registers. Each register field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset of the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate or compose the field.

AMDGPU code consumes these macros through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD`, which paste together `reg##__##field##__SHIFT` and `reg##__##field##_MASK`. The sibling `mmhub_1_0_offset.h` header supplies the actual register addresses, for example `mmMMEA0_EDC_MODE`, `mmMMEA1_ADDRNORM_BASE_ADDR0`, and `mmMMEA1_IO_RD_PRI_URGENCY_MASK`; this file supplies the field packing for values written to or read from those addresses.

## Important Macro Families

### MMEA0 tail: IO urgency, SDP arbitration, diagnostics, and EDC/DSM controls

The opening lines are a partial continuation of `MMEA0_IO_WR_PRI_URGENCY_MASK`, defining one-bit masks for `CID22` through `CID31`. The matching shift definitions and lower client masks are in the previous chunk, so any merged report should treat this as an incomplete register family unless combined with earlier lines.

`MMEA0_IO_RD_PRI_QUANT_PRI1` through `MMEA0_IO_WR_PRI_QUANT_PRI3` define four 8-bit threshold fields per register, repeated for read and write IO arbitration priority quantum settings. These values describe priority thresholds for four client groups across three priority registers.

`MMEA0_SDP_ARB_DRAM` and `MMEA0_SDP_ARB_FINAL` define burst limits, early switch behavior, read-only virtual-channel flags, and error reaction flags such as `ERREVENT_ON_ERROR` and `HALTREQ_ON_ERROR`. These fields describe how MMHUB's SDP path arbitrates DRAM, GMI, and IO traffic and how the final arbiter reacts to hardware error conditions.

`MMEA0_SDP_DRAM_PRIORITY` and `MMEA0_SDP_IO_PRIORITY` pack four read group priorities and four write group priorities into 4-bit fields. `MMEA0_SDP_CREDITS`, `MMEA0_SDP_TAG_RESERVE0/1`, `MMEA0_SDP_VCC_RESERVE0/1`, and `MMEA0_SDP_VCD_RESERVE0/1` define tag/response limits and virtual-channel credit reservations. These registers are stateful hardware throttling contracts: incorrect values can alter request progress, fairness, or deadlock margins.

`MMEA0_SDP_REQ_CNTL` defines request override bits for read, write, atomic, DRAM chain behavior, and inner-domain mode. `MMEA0_MISC` and `MMEA0_MISC2` contain arbitration policy bits for relative priority, return swap mode, early SDP original data, link-manager dynamic mode and thresholds, chip-select favoring, read/write switching, chip-select group swapping, and burst limits.

`MMEA0_LATENCY_SAMPLING` selects two latency samplers across DRAM/GMI/IO, read/write/atomic traffic, and VC fields. `MMEA0_PERFCOUNTER_LO`, `MMEA0_PERFCOUNTER_HI`, `MMEA0_PERFCOUNTER0_CFG`, `MMEA0_PERFCOUNTER1_CFG`, and `MMEA0_PERFCOUNTER_RSLT_CNTL` define performance counter data, compare values, event selectors, modes, enable/clear bits, start/stop triggers, and stop-on-saturation control.

`MMEA0_EDC_CNT` and `MMEA0_EDC_CNT2` expose compact SEC/DED/SED count fields for DRAM read/write command memory, data memory, page memory, IO command/data memory, return tag memory, and GMI paths. `MMEA0_EDC_MODE` defines fault-counting and propagation policy bits such as `COUNT_FED_OUT`, `GATE_FUE`, `DED_MODE`, `PROP_FED`, and `BYPASS`. `MMEA0_ERR_STATUS` exposes SDP read/write response status, read-response data-parity error, clear status, and busy-on-error fields.

`MMEA0_DSM_CNTL`, `MMEA0_DSM_CNTLA`, `MMEA0_DSM_CNTL2`, and `MMEA0_DSM_CNTL2A` are diagnostic/self-test/error-injection controls. They define DSM irritator data, single-write enables, error-injection enables, delay selection bits, and a shared inject delay. `MMEA0_DSM_CNTLB` and `MMEA0_DSM_CNTL2B` appear as comments without field definitions in this span.

`MMEA0_CGTT_CLK_CTRL` defines clock-gating/test controls such as on delay, off hysteresis, soft stall override, light-sleep override, and soft override bits for write, read, return, and register paths.

### MMEA1 DRAM client grouping and DRAM arbitration

The `MMEA1_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA1_DRAM_WR_CLI2GRP_MAP0/1` families map client IDs `CID0` through `CID31` into two-bit group fields for DRAM read and write traffic. `MAP0` covers clients 0-15 and `MAP1` covers clients 16-31. These mappings feed the later group-priority, aging, queueing, fixed-priority, urgency, and quantum controls.

`MMEA1_DRAM_RD_GRP2VC_MAP` and `MMEA1_DRAM_WR_GRP2VC_MAP` map four groups to two-bit virtual-channel identifiers. `MMEA1_DRAM_RD_LAZY` and `MMEA1_DRAM_WR_LAZY` define lazy timer and combined-write/lazy timer fields. `MMEA1_DRAM_RD_CAM_CNTL` and `MMEA1_DRAM_WR_CAM_CNTL` define high/low watermarks, warning watermarks, and high-priority write request thresholds for CAM control. `MMEA1_DRAM_PAGE_BURST` holds read and write page-burst controls.

`MMEA1_DRAM_RD_PRI_AGE`, `MMEA1_DRAM_WR_PRI_AGE`, `MMEA1_DRAM_RD_PRI_QUEUING`, `MMEA1_DRAM_WR_PRI_QUEUING`, `MMEA1_DRAM_RD_PRI_FIXED`, `MMEA1_DRAM_WR_PRI_FIXED`, `MMEA1_DRAM_RD_PRI_URGENCY`, and `MMEA1_DRAM_WR_PRI_URGENCY` define four-group priority coefficients. The urgency registers add per-group urgency mode bits. `MMEA1_DRAM_RD_PRI_QUANT_PRI1/2/3` and `MMEA1_DRAM_WR_PRI_QUANT_PRI1/2/3` define 8-bit quantum thresholds for the same four groups.

### MMEA1 address normalization and address decoding

`MMEA1_ADDRNORM_BASE_ADDR0/1` and `MMEA1_ADDRNORM_LIMIT_ADDR0/1` define address range validity, legacy MMIO hole enable, interleave channel selection, base address, destination fabric ID, socket/die interleave fields, and limit address fields. `MMEA1_ADDRNORM_OFFSET_ADDR1` and `MMEA1_ADDRNORM_HOLE_CNTL` provide high-address offset and DRAM-hole controls.

`MMEA1_ADDRDEC_BANK_CFG` and `MMEA1_ADDRDEC_MISC_CFG` define DRAM/GMI bank masks, bank-group selection, bank-group interleave, VCM enables, pseudo-channel/channel/chip-select/rank masks, and related DRAM/GMI selection fields. The address hash registers `MMEA1_ADDRDECDRAM_ADDR_HASH_BANK0` through `BANK4`, `PC`, `PC2`, `CS0`, and `CS1` define XOR-enable and column/row/NA/bank XOR masks. `MMEA1_ADDRDECDRAM_HARVEST_ENABLE` exposes force-enable/value bits for harvested bank bits.

`MMEA1_ADDRDEC0_*` and `MMEA1_ADDRDEC1_*` repeat two address-decoder instances. Each instance includes base address registers for `CS0` through `CS3` and `SECCS0` through `SECCS3`, address masks for chip-select pairs, geometry config fields for bank groups/rank maps/rows/columns/banks, bank/row bit selectors, low and high column selectors, and rank-map selectors. These macros are especially sensitive because they encode physical memory layout and chip-select decode behavior.

### MMEA1 IO arbitration and urgency masks

`MMEA1_IO_RD_CLI2GRP_MAP0/1` and `MMEA1_IO_WR_CLI2GRP_MAP0/1` mirror the DRAM client-to-group maps for IO read and write traffic. `MMEA1_IO_RD_COMBINE_FLUSH`, `MMEA1_IO_WR_COMBINE_FLUSH`, and `MMEA1_IO_GROUP_BURST` define flush and burst thresholds for grouped IO behavior.

`MMEA1_IO_RD_PRI_AGE`, `MMEA1_IO_WR_PRI_AGE`, queueing, fixed-priority, and urgency registers repeat the four-group coefficient layout for IO. `MMEA1_IO_RD_PRI_URGENCY_MASK` and `MMEA1_IO_WR_PRI_URGENCY_MASK` define one-bit masks for all 32 client IDs. These are full 32-bit client bitmaps; the macro naming produces fields like `CID17_MASK_MASK` because the hardware field name itself ends in `_MASK`.

`MMEA1_IO_RD_PRI_QUANT_PRI1/2/3` and `MMEA1_IO_WR_PRI_QUANT_PRI1/2/3` define the 8-bit group quantum thresholds for IO read and write arbitration.

### MMEA1 SDP, performance, EDC, and DSM controls

`MMEA1_SDP_ARB_DRAM`, `MMEA1_SDP_ARB_FINAL`, `MMEA1_SDP_DRAM_PRIORITY`, `MMEA1_SDP_IO_PRIORITY`, `MMEA1_SDP_CREDITS`, tag reserve, VCC/VCD reserve, `MMEA1_SDP_REQ_CNTL`, `MMEA1_MISC`, and `MMEA1_MISC2` repeat the same SDP arbitration, virtual-channel crediting, request override, link-manager, and chip-select group policy found in the MMEA0 tail.

`MMEA1_LATENCY_SAMPLING`, `MMEA1_PERFCOUNTER_LO/HI`, `MMEA1_PERFCOUNTER0_CFG`, `MMEA1_PERFCOUNTER1_CFG`, and `MMEA1_PERFCOUNTER_RSLT_CNTL` define the second MMEA block's latency sampler and performance counter register fields.

`MMEA1_EDC_CNT` and `MMEA1_EDC_CNT2` expose the same SEC/DED/SED counter layout for DRAM, IO, GMI, and tag/page memories. `MMEA1_DSM_CNTL` defines DSM irritator data and single-write enable fields for command/data/tag/GMI memories. The chunk ends partway through `MMEA1_DSM_CNTLA`; only the initial DRAM page memory, IO command/data memory, and GMI page memory shift definitions plus the first few masks through `IOWR_CMDMEM_DSM_IRRITATOR_DATA_MASK` are present. The rest of `MMEA1_DSM_CNTLA` and later DSM/error-injection registers are cross-chunk references.

## APIs, Types, and Functions

This chunk exports preprocessor macros only. There are no C types or functions.

The effective API is the generated naming contract used by register helpers:

- `REG_FIELD_SHIFT(reg, field)` expands to `reg__field__SHIFT`.
- `REG_FIELD_MASK(reg, field)` expands to `reg__field_MASK`.
- `REG_SET_FIELD(orig_val, reg, field, field_val)` clears `reg__field_MASK` in `orig_val`, shifts `field_val` by `reg__field__SHIFT`, masks it, and ORs it into the result.
- `REG_GET_FIELD(value, reg, field)` masks and right-shifts a packed register value.

That means macro spelling is ABI-significant. A register rename, field rename, missing shift, or missing mask breaks compile-time token pasting in consumers.

## Control Flow

There is no executable control flow in this header chunk. Runtime behavior emerges only in the C files that include it, read or compose register values, and write those values through MMIO helpers such as `RREG32_SOC15` and `WREG32_SOC15`.

The hardware-level sequencing implied by this chunk includes:

- Programming address normalization and address decode fields before memory traffic relies on those ranges.
- Programming client group maps before relying on group-based DRAM/IO priority policy.
- Programming credit/reserve/priority/urgency/quantum fields before enabling or tuning arbitration.
- Enabling, clearing, starting, stopping, and reading performance counters through the cfg/result-control/counter fields.
- Reading EDC and error-status fields after hardware has accumulated fault state, and writing clear/status or injection-related controls only in diagnostic paths.

## State and Persistence Behavior

The macros themselves have no storage and do not persist anything. The state they describe lives in MMHUB hardware registers. Register values are generally persistent until changed by the driver, hardware reset, power-gating/reset sequencing, firmware, or ASIC-specific initialization.

Important state categories represented here are:

- Arbitration and QoS state: group maps, virtual-channel maps, age/queue/fixed/urgency coefficients, priority quantum thresholds, SDP burst limits, and credit reservations.
- Memory topology state: address normalization ranges, holes, interleave fields, bank masks, chip-select base/mask/config/selector fields, column selectors, rank-map selectors, and hash/harvest settings.
- Performance/debug state: latency sampler selectors, counter event/mode/enable/clear fields, result-control start/stop triggers, and counter result fields.
- Reliability/error state: EDC counters, EDC mode, error-status fields, DSM irritator data, single-write enables, and error-injection controls.
- Clock/test override state: clock-gating delay/hysteresis and soft override fields.

Many fields are configuration fields, but some are command or latch-like controls, such as counter clear bits, result control clear/start/stop bits, error status clear bits, and error-injection enables. Consumers must account for hardware side effects when setting them.

## Dependencies and Integration Points

This header is included by MMHUB and related AMDGPU source files, including `amdgpu/mmhub_v1_0.c`, `amdgpu/uvd_v7_0.c`, `amdgpu/vce_v4_0.c`, and display resource code for DCE 12. It is paired with:

- `mmhub/mmhub_1_0_offset.h`, which defines register address macros such as `mmMMEA0_EDC_MODE`, `mmMMEA1_ADDRNORM_BASE_ADDR0`, and `mmMMEA1_IO_RD_PRI_URGENCY_MASK`.
- `mmhub/mmhub_1_0_default.h`, which provides default register values for the same generation.
- `amdgpu/amdgpu.h`, which defines `REG_FIELD_SHIFT`, `REG_FIELD_MASK`, `REG_SET_FIELD`, `REG_GET_FIELD`, and register write/read helper wrappers.
- SOC15 register helpers in AMDGPU code that combine IP block, instance, address macro, and packed value.

The chunk also aligns with later-generation MMHUB mask headers such as `mmhub_1_7_sh_mask.h`, `mmhub_2_0_0_sh_mask.h`, and `mmhub_9_4_1_sh_mask.h`. Those headers preserve many family names but may move fields or rename registers, so code must include the mask header matching the active ASIC generation.

## Risks and Edge Cases

- Bitfield correctness is critical. A wrong shift or mask silently writes the wrong hardware bits, potentially corrupting memory decode, arbitration policy, performance counters, or error handling.
- Address-decoder fields are high risk. Errors in base, mask, selector, row/column, rank-map, hash, or interleave fields can misroute memory requests or create GPU hangs and data corruption.
- QoS and credit fields are performance and forward-progress sensitive. Bad group mappings, urgency masks, credit reservations, or burst limits can starve clients, disturb virtual-channel fairness, or create difficult-to-debug latency spikes.
- Error/DSM fields are hazardous outside diagnostics. Accidentally enabling error injection, DSM irritator data, or single-write modes can produce artificial memory errors or alter fault reporting.
- The chunk contains partial register families at both ends: `MMEA0_IO_WR_PRI_URGENCY_MASK` begins before line 4743, and `MMEA1_DSM_CNTLA` continues after line 7093. Any whole-file synthesis must merge adjacent chunks to avoid treating these partial definitions as complete.
- Field names ending in `_MASK` produce macro names ending in `_MASK_MASK`, for example `MMEA1_IO_RD_PRI_URGENCY_MASK__CID0_MASK_MASK`. This is intentional under the generated naming scheme and should not be mechanically simplified.
- Signedness and width matter. Constants use `L` suffixes and 32-bit masks; consumers should use unsigned 32-bit register values and avoid shifting unbounded field values without the mask applied.
- Generation drift matters. Similar field families in newer MMHUB headers may have different shifts, masks, or register names, such as urgency masking naming in later versions. Copying values across ASIC generations is unsafe.

## Test Signals

Useful validation signals for this chunk are mostly build-time, boot-time, and hardware-behavioral:

- Compile coverage of files including `mmhub_1_0_sh_mask.h`; missing or misspelled macros fail where `REG_SET_FIELD` or `REG_GET_FIELD` token-pastes register and field names.
- Static consistency checks can verify every covered field has both a `__SHIFT` and `_MASK`, that masks match the declared shift/width pattern, and that fields within one register do not overlap unless intentionally aliased.
- Header-pair consistency checks can confirm registers referenced in this chunk have corresponding addresses in `mmhub_1_0_offset.h` and defaults where expected in `mmhub_1_0_default.h`.
- GPU initialization and resume tests should cover MMHUB programming paths, especially memory aperture setup, page-table/GART access, UVD/VCE/display use of MMHUB registers, and VM fault-free operation.
- Memory stress and display/video workloads are useful runtime signals for address normalization, address decoding, and arbitration correctness.
- Performance counter smoke tests should confirm `MMEA0/MMEA1_PERFCOUNTER*_CFG`, result-control, and counter result fields can be programmed, cleared, enabled, and read without hangs.
- RAS/ECC diagnostic tests, where supported by the hardware and test environment, should verify EDC counter reads, error-status clear behavior, and that error-injection controls are not enabled in normal initialization paths.
- Register readback tests can compare programmed values against expected packed values built from the same masks and shifts, especially for high-risk address-decoder and priority/credit registers.

## Unresolved Cross-Chunk References

- The lower part and shift definitions for `MMEA0_IO_WR_PRI_URGENCY_MASK` are in the previous chunk.
- The remaining masks for `MMEA1_DSM_CNTLA`, plus likely `MMEA1_DSM_CNTLB`, `MMEA1_DSM_CNTL2`, and later MMEA1 reliability/control fields, are in the next chunk.
- Whole-file research should reconcile this chunk with adjacent chunks to determine the full MMEA0/MMEA1 register coverage and to avoid double-counting repeated MMEA0/MMEA1 macro families.
