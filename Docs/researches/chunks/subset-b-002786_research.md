# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_sh_mask.h lines 1-2453

## Scope And Purpose

This chunk is the opening portion of the AMDGPU MMHUB 2.0.0 register mask header. It is a generated-style hardware contract file: each field in a 32-bit MMHUB register is exposed as a pair of preprocessor constants, `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no C functions, structs, enums, local variables, or executable branches in this range.

The covered source range starts with the MIT-style AMD license and include guard, then defines 2,162 mask/shift macros across 265 register-comment groups. Most of the range belongs to the `mmhub_dagbdec` address block, which describes DAGB0 read/write client arbitration, bandwidth, virtual-channel, TLB-credit, clock-gating, status, performance-counter, and reserved registers. The final part enters the `mmhub_mmea_mmeadec` address block and begins memory/DRAM client grouping and virtual-channel mapping definitions. The chunk ends at line 2453 after the first `MMEA0_DRAM_WR_LAZY__GROUP0_DELAY__SHIFT` macro, so that register's remaining fields are intentionally outside this chunk.

The companion offset header is `mmhub_2_0_0_offset.h`, not a `_d.h` file in this tree. It gives the register offsets and base indices; this header gives the bit layout used to compose or decode the 32-bit values at those offsets.

## Important APIs, Types, And Constants

There are no callable APIs or C types. The public interface is the macro namespace consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15*`, and `RREG32_SOC15*` in files that include this header.

The main constants in this chunk are:

- `DAGB0_RDCLI0` through `DAGB0_RDCLI18`: per-read-client control fields. Every client register uses the same layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.
- `DAGB0_WRCLI0` through `DAGB0_WRCLI18`: matching per-write-client controls with the same virtual-channel, urgency, bandwidth, TLB-credit, and outstanding-request limiter fields.
- `DAGB0_RD_CNTL` and `DAGB0_WR_CNTL`: shared DAGB read/write control-window fields for SCLK frequency, client and virtual-channel max-bandwidth windows, IO level override/compliance, and shared VC count.
- `DAGB0_RD_GMI_CNTL` and `DAGB0_WR_GMI_CNTL`: GMI-facing credit, level, max-burst, and lazy-timer fields.
- `DAGB0_RD_ADDR_DAGB`, `DAGB0_WR_ADDR_DAGB`, and `DAGB0_WR_DATA_DAGB`: enable, jump-ahead, self-init-disable, and `WHOAMI` fields for address/data DAGB paths.
- Output, address-client, and data-client burst/lazy-timer registers: `*_OUTPUT_DAGB_MAX_BURST`, `*_OUTPUT_DAGB_LAZY_TIMER`, `*_ADDR_DAGB_MAX_BURST[0-2]`, `*_ADDR_DAGB_LAZY_TIMER[0-2]`, `*_DATA_DAGB_MAX_BURST[0-2]`, and `*_DATA_DAGB_LAZY_TIMER[0-2]`. These pack 4-bit values for VCs or clients into one 32-bit register.
- `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL` and `DAGB0_WR_VC0_CNTL` through `DAGB0_WR_VC7_CNTL`: per-virtual-channel storage credit, EA credit, max/min bandwidth, OSD limiter, and max outstanding fields.
- `DAGB0_RD_CNTL_MISC` and `DAGB0_WR_CNTL_MISC`: storage-pool credit, EA-pool credit, IO EA credit, legacy cache-coherency mode bits, UTCL2 client ID, and HDP client ID.
- `DAGB0_RD_TLB_CREDIT` and `DAGB0_WR_TLB_CREDIT`: packed TLB0 through TLB5 credit fields.
- Pending/status bitmaps: `DAGB0_RDCLI_*_PENDING`, `DAGB0_WRCLI_*_PENDING`, `DAGB0_WRCLI_DBUS_*_PENDING`, `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL`.
- Write-side data and misc credit controls: `DAGB0_WR_DATA_CREDIT` and `DAGB0_WR_MISC_CREDIT`, including DLOCK VC credits, burst credits, atomic credit, OSD credit, and OSD DLOCK credit.
- `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE` and `_VALUE`: full-width bitmaps controlling GPU snoop override enablement/value per client bit.
- `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, and `DAGB0_CNTL_MISC2`: delay selection, EA VC remapping, bandwidth gap/init cycles, urgency boost/halt, clock-gating disable bits, busy-signal disable bits, swap control, and parity checking.
- `DAGB0_PERFCOUNTER_LO`, `DAGB0_PERFCOUNTER_HI`, `DAGB0_PERFCOUNTER0_CFG` through `2_CFG`, and `DAGB0_PERFCOUNTER_RSLT_CNTL`: performance-counter result, compare, event-select range, mode, enable, clear, start/stop trigger, global enable/clear, and stop-on-saturate fields.
- `DAGB0_RESERVE0` through `DAGB0_RESERVE131`: full-width reserved register masks. These preserve the generated register map alignment against the offset header.
- `MMEA0_DRAM_RD_CLI2GRP_MAP0/1` and `MMEA0_DRAM_WR_CLI2GRP_MAP0/1`: 2-bit client-ID to DRAM group maps for read and write clients 0-31.
- `MMEA0_DRAM_RD_GRP2VC_MAP` and `MMEA0_DRAM_WR_GRP2VC_MAP`: 3-bit mappings from DRAM groups 0-3 to virtual channels.
- `MMEA0_DRAM_RD_LAZY`: DRAM read group delay and request accumulation threshold/timeout/idle-max fields.
- `MMEA0_DRAM_WR_LAZY`: only the opening `GROUP0_DELAY__SHIFT` appears at this chunk boundary; masks and later shifts continue after line 2453.

## Control Flow And State Behavior

This file has no runtime control flow. The preprocessor substitutes constants into callers that perform MMIO register reads, writes, or read-modify-write updates.

Runtime state lives in the GPU MMHUB hardware registers. The DAGB0 client and VC fields configure traffic routing and quality-of-service behavior: virtual-channel selection, urgency thresholds, bandwidth windows, min/max bandwidth limits, outstanding request limits, and TLB-credit accounting. The control registers configure global read/write arbitration windows, GMI burst/lazy behavior, address/data DAGB enablement, and client/VC remapping.

The pending, FIFO, credit-full, and performance-counter registers are observable hardware status or counter state. Some fields are full-width bitmaps where each bit corresponds to a client, queue, or internal busy condition. Counter and result-control fields are stateful: `CLEAR`, `CLEAR_ALL`, `ENABLE`, trigger, and stop-on-saturate bits affect hardware counter accumulation and reset behavior.

Persistence is hardware-local. Values survive only according to MMHUB reset, power-gating, firmware, and driver initialization behavior. This header does not cache values, serialize register access, restore saved state, or protect callers from writing reserved or status-only fields.

## Dependencies And Integration Points

The immediate companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_offset.h`. It places the `mmhub_dagbdec` block at base address `0x68000` and maps this chunk's DAGB0 registers from `mmDAGB0_RDCLI0` offset `0x0000` through `mmDAGB0_RESERVE131` offset `0x00ff`. It then starts `mmhub_mmea_mmeadec` with `mmMMEA0_DRAM_RD_CLI2GRP_MAP0` at `0x0100`, `mmMMEA0_DRAM_RD_LAZY` at `0x0106`, and `mmMMEA0_DRAM_WR_LAZY` at `0x0107`.

In this tree the header is included by `drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c`, which is the MMHUB 2.0 VM/GART/protection-fault implementation, and by `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`, which pulls in MMHUB 2.0.0 register vocabulary alongside DCN 3.0 interrupt register definitions. Direct uses in `mmhub_v2_0.c` are mostly MMVM fields later in this same header, but the include establishes the ASIC-wide field namespace used by MMHUB code.

The same macro families appear in nearby generation headers such as `mmhub_9_1_sh_mask.h`, `mmhub_9_3_0_sh_mask.h`, and `mmhub_3_0_1_sh_mask.h`. Cross-generation similarities are useful for sanity checks, but the exact mask/shift values are generation-specific. For example, later headers can move or remove fields in `DAGB0_RD_CNTL`, so call sites must include the correct header for the target IP block.

## Risks And Edge Cases

- These macros are a hardware ABI. Any incorrect mask or shift can route traffic to the wrong virtual channel, change arbitration policy, alter TLB-credit behavior, or misread status bits while still compiling cleanly.
- Repeated client registers are visually repetitive. Copy/paste or regeneration errors can silently affect only one client, or can use a read-client macro for a write-client register with a same-shaped but wrong hardware target.
- Many registers pack repeated 2-bit, 3-bit, 4-bit, 5-bit, 6-bit, 7-bit, or 8-bit fields. Off-by-one shifts can produce plausible values while programming the wrong client/group/VC.
- Full-width masks such as `0xFFFFFFFFL` should be handled as unsigned 32-bit quantities. Signed promotion or printing through the wrong format can confuse debug output and register-dump comparisons.
- Pending, FIFO, credit, and performance-counter fields may be read-only, sticky, write-one-to-clear, or otherwise side-effectful depending on hardware semantics. The header only names bit positions; it does not encode access type.
- The reserved-register masks preserve map shape, not a promise that software can safely write those registers. Normal code should avoid touching `DAGB0_RESERVE*` unless a hardware programming guide explicitly requires it.
- The chunk boundary splits `MMEA0_DRAM_WR_LAZY`. Merge/reconciliation should combine this document with the next chunk before making whole-file statements about all fields in that register.

## Test And Validation Signals

There are no direct unit tests for this macro-only header chunk. Useful validation is compile-time, static, and hardware-oriented:

- Build AMDGPU configurations that include `mmhub_2_0_0_sh_mask.h`, especially MMHUB 2.0 and DCN 3.0 paths.
- Run static mask/shift consistency checks: single-bit masks should match their shift; multi-bit masks should be contiguous; repeated packed fields should be non-overlapping and cover the intended bit ranges; full-width masks should have shift zero.
- Compare `mmhub_2_0_0_sh_mask.h` against `mmhub_2_0_0_offset.h` so every register-comment group in this chunk has a matching `mm*` offset and `_BASE_IDX`.
- On supported hardware, compare MMHUB register dumps before and after VM/GART initialization, power transitions, and display initialization to confirm only expected MMHUB registers change.
- Exercise MMHUB protection-fault and VM invalidation paths in `mmhub_v2_0.c` for general include coverage, then inspect register dumps if DAGB0/DRAM QoS settings are changed by firmware or driver initialization.
- For performance-counter fields, validate that enabling, clearing, selecting events, and reading high/low counter parts produces monotonic or reset behavior expected by the hardware guide.

## Chunk Notes For Merge Lane

This is the first chunk of a larger `mmhub_2_0_0_sh_mask.h` register mask header. Whole-file research should treat it as the DAGB0 arbitration/QoS/status/performance-counter section plus the beginning of MMEA0 DRAM group mapping, and should defer complete coverage of `MMEA0_DRAM_WR_LAZY` to the following chunk.
