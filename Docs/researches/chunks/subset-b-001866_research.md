# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 2401-4862

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for display-controller MMIO registers. Consumers pair these `__SHIFT` and `_MASK` macros with the matching register offsets from `dcn_3_1_5_offset.h` so generic register helpers can read, write, update, poll, and acknowledge individual hardware fields.

The requested range starts inside the `DC_PERFMON2` field family, covers DMU/IHC interrupt routing, DMU and DMCUB control/status/mailbox fields, DWB writeback and color-processing fields, then ends at the beginning of the `DC_PERFMON3` field family. The range has 2,153 `#define` macros: 1,074 shift definitions and 1,079 mask definitions. The mismatch is from artificial chunk boundaries and a few register comments whose companion fields fall in adjacent chunks.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The chunk's interface is its generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a field within a 32-bit MMIO register.
- `<REGISTER>__<FIELD>_MASK`: the field mask before shifting or after alignment, depending on the register-helper macro being used.
- Register-family comment markers such as `//DMCUB_CNTL` and address-block markers such as `// addressBlock: dce_dc_dmu_dmcub_dispdec`; these are generated documentation aids, not C constructs.

Major macro families in this slice:

- `DC_PERFMON2_*` tail: performance counter state, perfmon control, count-off interrupt control, current-value status/ack fields, and high/low counter value selection.
- `DC_GPU_TIMER_*`: display pipe start-position fields for vupdate, vstartup, vready, flip, flip-away, no-lock vupdate, readback selection, and nominal vsync positions.
- `*_INTERRUPT_DEST` fields under `dce_dc_dmu_ihc_dispdec`: interrupt destination selectors for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DCHUB perf counters, DPP perf counters, MPC, OPP, OPTC, OTG0-OTG5, DIG, I2C/DDC/HPD, DIO, DCIO, HPD, AZ audio, AUX, DSC, and HPO.
- `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, `DMCU_SMU_INTERRUPT_CNTL`, `ZSC_*`, and `DMU_MISC_ALLOW_DS_FORCE`: DMU clock, memory power, SMU interrupt, zero-shutter/sleep-control, and display-pipe/DMCUB enable fields.
- `DOMAIN*_PG_CONFIG` and `DOMAIN*_PG_STATUS`: power-gating control and status fields for selected display power domains, plus `DC_IP_REQUEST_CNTL`.
- `DMCUB_*`: DMCUB memory-region base/top/offset/high fields, code-window enable fields, interrupt enable/ack/type/context fields, fault addresses, security/memory controls, inbox/outbox ring pointers and sizes, timers, scratch registers, core control, GPINT data paths, low-speed wake interrupt enable, processor ID, and soft reset.
- `DWB_*` top fields: writeback clock/memory power, frame-capture mode and flow control, capture window/source sizing, update control, CRC control/masks/values, output format/alpha/depth control, backpressure counters, host read control, overflow status/counters, soft reset, and debug selection.
- `DWB_HDR_*`, `DWB_GAMUT_REMAP*`, and `DWB_OGAM_*`: HDR multiplier, gamut remap matrix format and coefficients, output gamma mode/LUT access/control, RAM A and RAM B start/end/offset parameters for B/G/R channels, and piecewise-linear region descriptors for regions 0 through 33.
- `DC_PERFMON3_*` beginning: WB-local perf counter control, counted-value type, counter state, perfmon control, and the first `PERFMON_CNTL2` fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD display code:

1. DCN 3.1.5 resource, IRQ, and DMUB code includes `dcn_3_1_5_offset.h` and this `dcn_3_1_5_sh_mask.h` file.
2. Register-list macros paste symbolic register names into offset names and field names. For example, DCN resource code uses `SR(...)`, `SRI(...)`, and related macros, while DMUB code uses `DMUB_SR(...)` and `DMUB_SF(...)`.
3. Offset helpers build absolute register addresses from the offset header and DCN base segments. Field helpers such as `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` expand to the macros in this header.
4. Driver code later applies `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and wait/poll helpers to manipulate individual fields in the correct hardware order.

The field macros do not encode sequencing requirements. Consumers still need to handle clock and memory power enablement, power-domain transitions, DMCUB reset and boot order, DMCUB ring-buffer initialization, interrupt masking and acknowledgement, writeback programming, color LUT programming, and perf-counter start/stop sequencing.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state:

- Perfmon state covers selected counter state, event/countoff behavior, interrupt status/ack bits, and 48-bit or split high/low counter-value readback.
- GPU timer and IHC interrupt-destination fields control where display timing and block interrupts are routed, including per-pipe vblank/vupdate/flip sources and block-specific interrupts.
- DMU, power-gating, and clock fields represent display block enablement, memory power state, deep-sleep controls, DMCUB availability, and selected power-domain requests/status.
- DMCUB fields represent persistent firmware-facing setup while the display microcontroller is running: memory windows, code-window top addresses and enables, inbox/outbox base/size/rptr/wptr rings, scratch state, GPINT payloads, timer values, fault addresses, interrupt routing, reset status, and security controls.
- DWB fields represent writeback configuration and live capture state: frame-capture geometry, output packing, CRC capture, overflow/backpressure status, host read state, memory power, and soft reset.
- DWB color fields represent programmable writeback color transforms: HDR scale, gamut-remap matrices, output gamma LUT host access, active RAM selection, LUT format/mode, PWL start/end/offset values, and per-region LUT offsets/segment counts.

Persistence is hardware-defined. Configuration fields generally retain values until a modeset, writeback reconfiguration, power gate, firmware reset, suspend/resume, or ASIC reset changes them. Status, counter, interrupt, fault, ack, wake, and reset fields may be read-only, sticky, self-clearing, or write-one-to-clear; this generated header only provides bit layout, not access semantics.

## Dependencies And Integration Points

This chunk must match AMD's generated DCN 3.1.5 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- The DCN base segment constants defined in the consuming C files, such as `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5`.

Direct integration points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes this header and builds `dmub_srv_dcn315_regs`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.h`, whose `DMUB_DCN315_FIELDS()` macro consumes fields from this range such as `DMCUB_CNTL.DMCUB_ENABLE`, `DMCUB_CNTL2.DMCUB_SOFT_RESET`, `DMCUB_SEC_CNTL.*`, `DMCUB_REGION3_CW*_TOP_ADDRESS.*`, `CC_DC_PIPE_DIS.DC_DMCUB_ENABLE`, and DMCUB interrupt fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes this header for interrupt-source setup, acknowledgement, and DAL IRQ mapping for vblank, vline, page-flip, vupdate, DMCUB outbox, HPD, and HPD RX sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes this header while constructing DCN 3.1.5 hardware register tables for hubs, pipes, timing generators, stream encoders, DWB, MMHUBBUB, DMUB-backed features, and other display resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c`, which select the `DMUB_ASIC_DCN315` register set.

The DWB field families integrate with the DCN 3.0/3.1 DWB and MMHUBBUB code included by `dcn315_resource.c` (`dcn30_dwb.h`, `dcn30_mmhubbub.h`). The generated field names are also tied to enum definitions in AMD SOC enum headers for values such as DWB OGAM LUT mode, host RAM selection, read color selection, and OGAM enable/bypass modes.

## Risks And Edge Cases

- Field drift is the central risk. A wrong shift or mask can compile cleanly but update the wrong bits in a live display register.
- The chunk boundaries are artificial. It begins after some `DC_PERFMON2_PERFCOUNTER_CNTL2` masks and ends immediately after `DC_PERFMON3_PERFMON_CNTL2`, so adjacent chunks are required for complete `DC_PERFMON2` and `DC_PERFMON3` coverage.
- Interrupt-destination fields are sensitive because a one-bit mistake can route vblank, vline, page-flip, HPD, AUX, DSC, DMCUB, or block error interrupts to the wrong destination, leave them masked, or make acknowledgement ineffective.
- DMU and power-gating fields are sequencing-sensitive. Writes made while clocks are off, memory is gated, or the DMCUB is held in reset can be ignored or can leave firmware-visible state inconsistent.
- DMCUB ring and memory-window fields are high risk. Incorrect base/top/offset, high-address, code-window enable, inbox/outbox pointer, interrupt, or scratch fields can break DMUB firmware boot, command submission, outbox notifications, PSR/ABM/replay features, or debug collection.
- DWB writeback fields affect captured pixels rather than scanout. Bugs may only appear in screen recording, capture, virtual display, CRC validation, or pipe-specific writeback workloads.
- DWB color programming is format-sensitive. Bad OGAM/gamut/HDR fields can produce subtle color errors, incorrect LUT bank selection, broken host LUT access, or only fail for particular color depths and matrix/LUT modes.
- Many status and ack fields have side effects not visible in this file. Treating read-only, sticky, self-clearing, or write-one-to-clear bits as ordinary writable fields can cause lost interrupts, stale faults, or stuck status.

## Test Signals

Useful validation is a mix of generated-header consistency, build coverage, and hardware behavior:

- Build AMDGPU display support with DCN 3.1.5 enabled; missing or renamed macros should fail in DMUB, IRQ, resource, DWB, and register-table construction.
- Mechanically verify that every complete field in lines 2401-4862 has both a `__SHIFT` and `_MASK` definition, allowing for the known first and last partial register families.
- Diff this chunk against AMD's authoritative DCN 3.1.5 register database and against nearby generated DCN 3.1.x headers where field compatibility is expected.
- Boot a DCN 3.1.5 system and verify DMCUB firmware initialization, reset release, command submission, inbox/outbox pointer movement, GPINT handling, scratch/debug capture, and DMUB outbox interrupts.
- Exercise IRQ-heavy display paths: vblank, vline, page flips, vupdate no-lock, HPD plug/unplug, HPD RX, AUX/DDC activity, DSC-capable links, and suspend/resume.
- Exercise DWB paths if hardware and driver features expose them: capture enable/disable, window/source-size changes, output format/depth changes, CRC readback, overflow/backpressure counters, host read behavior, and DWB soft reset.
- Validate writeback color processing with known ramps and matrices: HDR multiplier, gamut remap coefficients, OGAM LUT host programming, RAM A/B bank selection, per-channel PWL start/end/offset fields, and region 0-33 descriptors.
- Watch kernel logs and display diagnostics for DMCUB boot failures, stuck interrupts, HPD storms, lost vblank/page-flip events, AUX timeouts, writeback overflows, CRC mismatches, color corruption, and resume failures.

## Cross-Chunk Notes

Adjacent chunks should be merged before making complete file-level claims about `DC_PERFMON2`, `DC_PERFMON3`, or any full DCN 3.1.5 perfmon namespace. This chunk owns the middle DMU/IHC/DMCUB/DWB field-layout coverage for `dcn_3_1_5_sh_mask.h`, while the final per-file document should reconcile it with earlier and later field families in the same generated header.
