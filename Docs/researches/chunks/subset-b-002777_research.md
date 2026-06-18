# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 7086-9431

## Purpose

This chunk is a generated-style register bitfield contract for AMD MMHUB 1.8.0 hardware. It contains preprocessor constants only: each hardware field is exposed as a `*_MASK` and/or `*__SHIFT` macro that downstream AMDGPU code can combine with the matching register offsets from `mmhub_1_8_0_offset.h`.

The selected range covers the tail of the `DAGB4_RDCLI2` field set, the bulk of the `DAGB4` read/write data-address generation block, and the start of the `aid_mmhub_ea_mmeadec0` MMEA decoder register fields through `MMEA0_GMI_WR_PRI_AGE`. These definitions describe how MMHUB clients are assigned to virtual channels, throttled, credited, monitored, mapped into groups, and prioritized for DRAM/GMI traffic. The file does not implement policy itself; it gives the driver the bit positions needed to program or inspect that policy.

## Major Register Families Covered

- `DAGB4_RDCLI2` through `DAGB4_RDCLI15`: per-read-client fields for virtual channel selection, TLB credit checking, high/low urgency thresholds, max/min bandwidth limiting, OSD limiter enablement, and maximum outstanding depth.
- `DAGB4_RD_CNTL`, `DAGB4_RD_GMI_CNTL`, and `DAGB4_RD_ADDR_DAGB`: shared read-side controls for SCLK/window sizing, IO level override/selection, shared virtual-channel count, GMI EA credit/level/burst/lazy timing, address DAGB enablement, jump-ahead mode, self-init control, and `WHOAMI` identity fields.
- `DAGB4_RD_OUTPUT_DAGB_*`, `DAGB4_RD_ADDR_DAGB_*`, and `DAGB4_RD_VC0_CNTL` through `DAGB4_RD_VC7_CNTL`: read-side per-VC burst limits, lazy timers, reset values, increment/idle decays, timeout behavior, VC enablement, weights, channel thresholds, credit counters, and refill credits.
- `DAGB4_RD_CGTT_CLK_CTRL`, `DAGB4_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB4_ATCVM_RD_CGTT_CLK_CTRL`: clock-gating and soft-override fields for the read DAGB, L1 TLB read path, and ATCVM read path.
- `DAGB4_RD_CNTL_MISC`, `DAGB4_RD_TLB_CREDIT`, `DAGB4_RD_RDRET_CREDIT_CNTL`, and `DAGB4_RD_RDRET_CREDIT_CNTL2`: read-path stall gating, credit-reset behavior, TLB credit values, return credit per virtual channel, and combined VC4-VC7 return credit fields.
- `DAGB4_RDCLI_*_PENDING`: compact status bitmaps showing read client pending state at ASK, GO, global-send, TLB, OARB, and OSD stages.
- `DAGB4_WRCLI0` through `DAGB4_WRCLI15`: write-client mirrors of the per-client channel, TLB-credit, urgency, bandwidth, OSD limiter, and max-outstanding fields.
- `DAGB4_WR_CNTL`, `DAGB4_WR_GMI_CNTL`, `DAGB4_WR_ADDR_DAGB`, `DAGB4_WR_DATA_DAGB`, `DAGB4_WR_ADDR_DAGB_*`, `DAGB4_WR_DATA_DAGB_*`, and `DAGB4_WR_VC0_CNTL` through `DAGB4_WR_VC7_CNTL`: write-side shared control, address/data DAGB enablement, per-VC burst/lazy-timer configuration, and virtual-channel credit/refill/threshold behavior.
- `DAGB4_WR_CGTT_CLK_CTRL`, `DAGB4_L1TLB_WR_CGTT_CLK_CTRL`, and `DAGB4_ATCVM_WR_CGTT_CLK_CTRL`: write-side clock-gating control fields.
- `DAGB4_WR_CNTL_MISC`, `DAGB4_WR_TLB_CREDIT`, `DAGB4_WR_DATA_CREDIT`, `DAGB4_WR_MISC_CREDIT`, `DAGB4_WR_OSD_CREDIT_CNTL*`, and `DAGB4_WR_ATOMIC_FIFO_CREDIT_CNTL1`: write-path stall, reset, TLB/data/misc/OSD/atomic FIFO credit configuration, including several per-VC or per-group credit fields.
- `DAGB4_WRCLI_GPU_SNOOP_OVERRIDE*` and `DAGB4_WRCLI_*_PENDING`: write-client snoop override controls and pending-state bitmaps for ASK, GO, global-send, TLB, OARB, OSD, DBUS ASK, and DBUS GO stages.
- `DAGB4_DAGB_DLY`, `DAGB4_CNTL_MISC`, and `DAGB4_CNTL_MISC2`: delay tuning, request counter enables/limits, page-size match fields, return/output allocation knobs, bypass behavior, credit expansion, VC stall disabling, self-init gating, arbitration override, and assorted debugger/disable flags.
- `DAGB4_FATAL_ERROR_*`: fatal error enable/clear/status fields for read and write timeout conditions, missing TC/GC/SDMA data, DBUS-missing conditions, unexpected read return, ATCVM invalidation-vs-request hazards, invalidation FIFO request handling, and client IDs associated with read, write, DBUS, and FIFO error sources.
- `DAGB4_FIFO_EMPTY`, `DAGB4_FIFO_FULL`, `DAGB4_WR_CREDITS_FULL`, and `DAGB4_RD_CREDITS_FULL`: FIFO and credit saturation status bitmaps.
- `DAGB4_PERFCOUNTER_*`: low/high counter values, compare values, event selectors, performance modes, enable/clear fields, result selection, start/stop triggers, global enable/clear, and saturate-stop behavior.
- `DAGB4_L1TLB_REG_RW`: L1 TLB debug/register access command fields, including valid/write control, 7-bit address, 8-bit write data, and 8-bit read data.
- `MMEA0_DRAM_*` and `MMEA0_GMI_*`: memory decoder arbitration maps. The DRAM and GMI families map client IDs 0-31 to four groups, map groups to virtual channels, configure lazy request accumulation, CAM depth and reorder limits, page burst thresholds, priority aging, priority queueing/fixed/urgency behavior, and priority quantum values. The chunk ends after the `MMEA0_GMI_WR_PRI_AGE` masks.

## Important APIs, Types, and Functions

This header range declares no C functions, structs, enums, variables, or callable APIs. Its public interface is the generated macro namespace:

- `*_MASK` values isolate fields inside 32-bit MMHUB registers.
- `*__SHIFT` values define how callers pack field values into those masks or unpack field values from a register read.
- The corresponding register address symbols live in the companion offset header and are consumed by AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and field-update helpers/macros used elsewhere in the driver.

The direct integration point for this generation is `amdgpu/mmhub_v1_8.c`, which includes both `mmhub/mmhub_1_8_0_offset.h` and this mask header. The hand-written MMHUB 1.8 code primarily programs VM, GART, invalidation, fault, clock/power, and RAS behavior; many of the detailed `DAGB4` and `MMEA0` masks in this chunk are hardware-contract data available for bring-up code, diagnostics, register dumps, or future tuning rather than necessarily referenced by name in current C logic.

## Control Flow

There is no runtime control flow in the chunk. Including the header makes constant definitions visible at compile time. Runtime control flow appears only in callers that use these constants while reading, modifying, or writing MMHUB registers.

The typical downstream register-update sequence is:

1. Select the MMHUB 1.8.0 register offset from `mmhub_1_8_0_offset.h`.
2. Read the current 32-bit register value when preserving unrelated fields.
3. Clear the target field with the matching `*_MASK`.
4. Shift the new value by the matching `*__SHIFT`.
5. Mask and OR the shifted value into the register image.
6. Write the final value to the correct MMHUB instance/register.

Status fields use the inverse pattern: read the register, apply the mask, shift the field down, and interpret the result as a bitmap or encoded value. Pending, FIFO, credit-full, fatal-error-status, and performance-counter fields in this chunk are examples of readback-oriented contracts.

## State and Persistence Behavior

The header has no mutable state and persists nothing by itself. The constants describe state stored in MMHUB hardware registers while the GPU is powered and initialized.

Several register families represent long-lived configuration state: client-to-VC routing, bandwidth limit enables and windows, urgency thresholds, maximum outstanding request depths, DAGB enablement, per-VC weights/thresholds/refill credits, lazy timers, request accumulation thresholds, CAM/reorder depths, priority aging coefficients, and priority quantum settings. These values affect memory-fabric scheduling and can persist until device reset, power gating, suspend/resume restore, or explicit reprogramming.

Other families describe transient or event state: pending-stage bitmaps, FIFO empty/full state, credit-full state, fatal-error status, performance-counter low/high values, compare fields, and TLB debug read data. Some fields have clear or reset semantics in hardware, such as fatal error clear bits, performance counter clear bits, and reset/self-init controls. This header does not encode whether a bit is read-only, write-only, write-one-to-clear, self-clearing, sticky, or reserved; callers must follow ASIC documentation and existing driver sequencing.

## Dependencies and Integration Points

- Depends only on C preprocessor inclusion; the include guard and macro spelling are the effective ABI.
- Must stay synchronized with `mmhub_1_8_0_offset.h`, because masks are only meaningful with the matching register offsets and MMHUB generation.
- Integrated by `amdgpu/mmhub_v1_8.c` for MMHUB 1.8 ASIC support, including multi-instance access through SOC15 register helpers and `adev->aid_mask`.
- Ties into AMDGPU GPUVM/GART setup, MMHUB invalidation, RAS/error reporting, register debugging, performance monitoring, and any firmware or bring-up code that inspects MMHUB arbitration state.
- Names reference hardware subblocks rather than Linux objects: `DAGB4` is a data/address generation/arbitration block, `RDCLI`/`WRCLI` are read/write clients, `VC` is virtual channel state, `L1TLB`/`ATCVM` are translation paths, `GMI` is the GPU memory interconnect side, and `MMEA0` is the memory decoder arbitration block for DRAM/GMI routing.

## Risks and Edge Cases

- A wrong mask or shift silently programs the wrong hardware bits. For this chunk, that can alter memory request routing, starvation prevention, outstanding-request limits, clock-gating behavior, credit accounting, or fatal-error handling.
- Repeated register layouts are easy to confuse. `RDCLI` and `WRCLI` fields are mostly parallel, as are DRAM and GMI arbitration maps, but a caller must still use the exact register-specific macro because small field-layout differences can exist across families or ASIC revisions.
- The chunk begins mid-family at `DAGB4_RDCLI2` and ends mid-MMEA priority area after `MMEA0_GMI_WR_PRI_AGE`; neighboring chunks are needed for the complete file-level picture.
- Encoded values are not self-describing. Fields such as urgency levels, aging coefficients, priority quantums, CAM depths, burst limits, and lazy timers need hardware documentation or known-good register tables to determine valid ranges and units.
- Status and control fields share the same macro style. Writing a status or reserved field as though it were a normal configuration field can clear diagnostics, trigger self-clearing behavior, or cause undefined hardware behavior.
- Multi-instance MMHUB support means correct masks are not enough; callers must also target the correct MMHUB/AID instance. A valid bitfield written to the wrong instance can leave another memory hub unconfigured.

## Test Signals

- Build coverage: misspelled or removed macros should fail consumers that include the MMHUB 1.8.0 headers.
- Register readback: after initialization or debug programming, read back `DAGB4_RD_CNTL`, `DAGB4_WR_CNTL`, DAGB per-VC controls, MMEA DRAM/GMI group maps, lazy timers, CAM controls, and priority registers to confirm values land in the expected fields.
- Hardware smoke coverage: GPUVM page-table setup, GART access, SDMA traffic, display/media traffic through MMHUB, peer or GMI traffic, suspend/resume, and GPU reset paths can expose incorrect arbitration, credit, or routing fields indirectly.
- Error diagnostics: `DAGB4_FATAL_ERROR_STATUS*`, pending bitmaps, FIFO full/empty fields, and credit-full registers are strong signals when a field definition or caller usage causes traffic to wedge.
- Performance diagnostics: `DAGB4_PERFCOUNTER_*` and MMEA priority/quantum fields can be used during bring-up to verify that traffic selection and throttling behave as expected.
- RAS/debug integration: MMHUB RAS query/reset paths in `mmhub_v1_8.c` and register dump tooling should continue to compile and report coherent MMHUB state when this generated header is present and synchronized with the hardware offsets.
