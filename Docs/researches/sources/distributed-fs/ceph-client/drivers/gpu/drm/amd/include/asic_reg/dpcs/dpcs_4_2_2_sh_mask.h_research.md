# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002337`: lines 1-2378, `Docs/researches/chunks/subset-b-002337_research.md`
- `subset-b-002338`: lines 2379-4735, `Docs/researches/chunks/subset-b-002338_research.md`
- `subset-b-002339`: lines 4736-7219, `Docs/researches/chunks/subset-b-002339_research.md`
- `subset-b-002340`: lines 7220-9580, `Docs/researches/chunks/subset-b-002340_research.md`
- `subset-b-002341`: lines 9581-11939, `Docs/researches/chunks/subset-b-002341_research.md`
- `subset-b-002342`: lines 11940-14316, `Docs/researches/chunks/subset-b-002342_research.md`
- `subset-b-002343`: lines 14317-16696, `Docs/researches/chunks/subset-b-002343_research.md`
- `subset-b-002344`: lines 16697-19117, `Docs/researches/chunks/subset-b-002344_research.md`
- `subset-b-002345`: lines 19118-21534, `Docs/researches/chunks/subset-b-002345_research.md`
- `subset-b-002346`: lines 21535-23895, `Docs/researches/chunks/subset-b-002346_research.md`
- `subset-b-002347`: lines 23896-26285, `Docs/researches/chunks/subset-b-002347_research.md`
- `subset-b-002348`: lines 26286-28636, `Docs/researches/chunks/subset-b-002348_research.md`
- `subset-b-002349`: lines 28637-30999, `Docs/researches/chunks/subset-b-002349_research.md`
- `subset-b-002350`: lines 31000-33363, `Docs/researches/chunks/subset-b-002350_research.md`
- `subset-b-002351`: lines 33364-35750, `Docs/researches/chunks/subset-b-002351_research.md`
- `subset-b-002352`: lines 35751-38153, `Docs/researches/chunks/subset-b-002352_research.md`
- `subset-b-002353`: lines 38154-40593, `Docs/researches/chunks/subset-b-002353_research.md`
- `subset-b-002354`: lines 40594-42955, `Docs/researches/chunks/subset-b-002354_research.md`
- `subset-b-002355`: lines 42956-45339, `Docs/researches/chunks/subset-b-002355_research.md`
- `subset-b-002356`: lines 45340-47692, `Docs/researches/chunks/subset-b-002356_research.md`
- `subset-b-002357`: lines 47693-50047, `Docs/researches/chunks/subset-b-002357_research.md`
- `subset-b-002358`: lines 50048-52416, `Docs/researches/chunks/subset-b-002358_research.md`
- `subset-b-002359`: lines 52417-54805, `Docs/researches/chunks/subset-b-002359_research.md`
- `subset-b-002360`: lines 54806-57191, `Docs/researches/chunks/subset-b-002360_research.md`
- `subset-b-002361`: lines 57192-59638, `Docs/researches/chunks/subset-b-002361_research.md`
- `subset-b-002362`: lines 59639-62003, `Docs/researches/chunks/subset-b-002362_research.md`
- `subset-b-002363`: lines 62004-64388, `Docs/researches/chunks/subset-b-002363_research.md`
- `subset-b-002364`: lines 64389-66756, `Docs/researches/chunks/subset-b-002364_research.md`
- `subset-b-002365`: lines 66757-69113, `Docs/researches/chunks/subset-b-002365_research.md`
- `subset-b-002366`: lines 69114-71473, `Docs/researches/chunks/subset-b-002366_research.md`
- `subset-b-002367`: lines 71474-73853, `Docs/researches/chunks/subset-b-002367_research.md`
- `subset-b-002368`: lines 73854-76243, `Docs/researches/chunks/subset-b-002368_research.md`
- `subset-b-002369`: lines 76244-78674, `Docs/researches/chunks/subset-b-002369_research.md`
- `subset-b-002370`: lines 78675-81068, `Docs/researches/chunks/subset-b-002370_research.md`
- `subset-b-002371`: lines 81069-83440, `Docs/researches/chunks/subset-b-002371_research.md`
- `subset-b-002372`: lines 83441-85817, `Docs/researches/chunks/subset-b-002372_research.md`
- `subset-b-002373`: lines 85818-88178, `Docs/researches/chunks/subset-b-002373_research.md`
- `subset-b-002374`: lines 88179-90536, `Docs/researches/chunks/subset-b-002374_research.md`
- `subset-b-002375`: lines 90537-92913, `Docs/researches/chunks/subset-b-002375_research.md`
- `subset-b-002376`: lines 92914-95292, `Docs/researches/chunks/subset-b-002376_research.md`
- `subset-b-002377`: lines 95293-97714, `Docs/researches/chunks/subset-b-002377_research.md`
- `subset-b-002378`: lines 97715-100131, `Docs/researches/chunks/subset-b-002378_research.md`
- `subset-b-002379`: lines 100132-102491, `Docs/researches/chunks/subset-b-002379_research.md`
- `subset-b-002380`: lines 102492-103633, `Docs/researches/chunks/subset-b-002380_research.md`

## Chunk Research

### subset-b-002337: lines 1-2378

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 1-2378

## Purpose

This chunk is generated AMD DPCS 4.2.2 register-field metadata. It contains no executable C logic; it defines C preprocessor constants that map hardware register fields to bit positions and masks for the AMDGPU display DPCS/DPCSSYS block. Runtime display code combines these constants with the matching offset/header data to build MMIO register reads and writes for DisplayPort/HDMI PHY control, DPCS transmitter setup, panel power sequencing, backlight PWM, debug, interrupt, and DP Alt Mode access control.

The range begins at the file header, SPDX/license, and include guard, then covers 2,169 `#define` entries: 1,089 `__SHIFT` definitions and 1,079 `_MASK` definitions. The chunk has 168 register-comment groups across 11 address blocks. It covers CR address/data windows `CR0` through `CR4`, two panel power-sequencer/PWM instances `PWRSEQ0` and `PWRSEQ1`, complete generated field layouts for `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2`, and the start of `RDPCSTX3` through the first `RDPCSTX3_RDPCSTX_CLOCK_CNTL` mask. The final register is intentionally partial because line 2378 is a chunk boundary; the following chunk is required for the rest of `RDPCSTX3` and later DPCS instances.

Although this repository subtree is named `distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata, not Ceph or filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field in a 32-bit register value.

The main register families are:

- `DPCSSYS_CR0` through `DPCSSYS_CR4`: 16-bit CR address/data windows via `DPCSSYS_CR*_DPCSSYS_CR_ADDR` and `DPCSSYS_CR*_DPCSSYS_CR_DATA`.
- `PWRSEQ0` and `PWRSEQ1`: GPIO, panel power sequence, and backlight PWM fields. These include `DC_GPIO_VARY_BL`, `DC_GPIO_DIGON`, `DC_GPIO_BLON`, panel target state, sync/digon/blon override and polarity bits, power-up/down delays, reference dividers, PWM period/duty/fractional enablement, frame-start update controls, group lock/update-pending fields, and spare registers.
- `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2`: complete mirrored transmitter register field sets for DPCS transmitter instances 0-2.
- `RDPCSTX3`: partial field coverage for transmitter instance 3, ending inside `RDPCSTX3_RDPCSTX_CLOCK_CNTL`.

The complete `RDPCSTX0`-`RDPCSTX2` field sets include control, clocking, interrupt, CR access, SRAM power, scratch/spare, debug, PHY control, PHY fuse/readback, DP Alt Mode, generic PHY bus, byte-order, and PLL update override registers. Representative fields include DPCS CBUS/SRAM/TX soft reset bits, lane bit-order and byte-order controls, lane FIFO enables, FIFO start/read delay, interrupt status/clear/mask bits for register FIFO overflow, DPALT toggles, and per-lane FIFO errors, plus `RDPCS_TX_PLL_UPDATE_REQ/PENDING` and PLL update data/address overrides.

The PHY fields cover resets, TCA/APB reset, HDMI mode enable, reference range, reference clock detection, SRAM init/load/bypass status, power-gating mode, PCS/PMA/analog power enables and stable status, DP4 power-on-reset, lane loopback controls, per-lane TX reset/disable/clock-ready/data-enable/request/ack handshakes, termination/inversion/equalization-bypass/high-protection bits, low-power/rate/width/detect-RX controls, lane P-state and MPLL enablement, DP Alt Mode disable/ack, reference clock request/enable, MPLLB fractional denominator/quotient/remainder, SSC peak/step/up-spread, multiplier/divider/clock-enable/calibration controls, PHY fuse equalization and PLL tuning fields, RX load values, DPALT reserved copies for DMCU, and PHY generic input/output bus selectors.

## Control Flow

This header has no runtime control flow. Its effect is compile-time token expansion:

1. ASIC-specific AMDGPU display code includes the DPCS 4.2.2 offset and shift/mask headers for the selected GPU generation.
2. Register access tables and helper macros token-paste register and field names into shift/mask descriptors.
3. Runtime driver paths use those descriptors with MMIO helpers to update or poll hardware fields.
4. Hardware state machines perform the actual sequencing for panel power, PWM updates, DPCS transmitter reset/clock/FIFO operation, PHY power and PLL control, DP Alt Mode ownership, and interrupt/debug/status capture.

The mirrored `RDPCSTX0`-`RDPCSTX2` macro sets show that software can often reuse instance-generic programming flows while binding to per-instance register prefixes. `RDPCSTX3` is only partially represented in this chunk, so complete control-flow conclusions for instance 3 require the next chunk.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes encodings for hardware-visible state:

- CR windows persist the selected 16-bit CR address/data values according to hardware behavior.
- Power sequencer fields encode panel enable/target state, visible state bits, power-up/down timing, GPIO input/output state, and PWM duty/period/update state.
- Transmitter control fields encode DPCS soft reset state, lane/FIFO enablement, lane packing and byte ordering, register-block enablement, DP Alt Mode block status, and PLL update request/pending status.
- Clock fields encode external reference, TX lane clocks, global TX clock, SRAM clock, and OCLA/debug clock gate/enable/on status.
- Interrupt fields encode observed errors/toggles, clear bits, and interrupt masks.
- SRAM and PHY fields encode memory power forcing/state, PHY power mode/stability, lane handshake status, PLL and spread-spectrum settings, fuse/readback values, loopback/test controls, and debug-bus selections.
- Scratch, spare, and generic bus fields expose hardware-defined full-width or packed diagnostic state.

Persistence, volatility, access direction, reset values, and side effects are hardware-defined and are not represented in this generated mask header. Some fields are likely read-only status, write-one-to-clear, self-clearing request bits, sticky error status, or only valid while clocks/power domains are enabled. Driver code must rely on the hardware programming guide and higher-level register definitions for those semantics.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated register-header convention. This file is intended to be paired with the corresponding DPCS 4.2.2 offset/base-index header in the same `asic_reg/dpcs` area, because masks without register addresses are not sufficient for MMIO programming.

Important integration points include:

- AMDGPU display register access helpers and generated register tables that combine `*_offset.h` register addresses with these `*_sh_mask.h` field constants.
- Display Core link encoder and transmitter programming paths that configure DPCS TX clocks, lane enables, FIFO start, lane packing, byte order, reset sequencing, and PHY link parameters.
- Embedded DisplayPort and panel/backlight paths that program `PWRSEQ0`/`PWRSEQ1` panel sequencing delays, GPIO signals, PWM period/duty, frame-start PWM updates, and backlight reference dividers.
- DP Alt Mode and DMCU/firmware coordination paths that use allow-driver-access, driver-access-blocked, DMCU DPALT disable-block, force-TX-clock-disable, and reserved PHY-control mirror fields.
- Interrupt and diagnostic paths that read or clear DPCS register FIFO overflow, DPALT toggle, per-lane TX FIFO errors, debug counter, OCLA source selection, scratch/spare, and PHY generic bus fields.
- PHY/PLL programming code that needs the MPLLB fractional, multiplier, divider, SSC, calibration, power, lane P-state, and fuse/readback encodings.

Because these constants are a silicon ABI, manual edits must stay synchronized with AMD's authoritative generated register database and with the matching offset header. A wrong mask or shift can compile cleanly while causing writes to the wrong hardware bits.

## Risks And Edge Cases

- The macros are untyped preprocessor constants. A wrong field width, shift, or mask will not be caught by the C type system and can corrupt adjacent hardware fields.
- The chunk boundary is not semantically aligned. `RDPCSTX3_RDPCSTX_CLOCK_CNTL` is incomplete here, and the 1,089 shift versus 1,079 mask count reflects boundary and generated-field asymmetry. Whole-instance analysis for `RDPCSTX3` requires the following chunk.
- Instance symmetry matters. `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2` mirror many fields; a generated-name drift or copy/paste mistake can break only one physical transmitter and appear topology-dependent.
- Status, clear, and mask fields use similar names in interrupt registers. Confusing observed status bits, clear bits, and interrupt mask bits can leave faults latched, hide errors, or clear evidence before diagnostics read it.
- Power, reset, and clock fields are sequencing-sensitive. Programming PHY reset, SRAM bypass/load, PCS/PMA/analog power, TX clock gates, FIFO start, or PLL update request/pending bits out of order can cause blank displays, link-training failures, hangs waiting for stable bits, or intermittent resume failures.
- Panel power and PWM fields directly affect user-visible backlight and panel sequencing. Wrong delay/ref-divider/PWM masks can create flicker, no-backlight, panel power timing violations, or delayed updates tied to frame-start synchronization.
- DP Alt Mode ownership fields are coordination points between driver, DMCU/firmware, and hardware. Incorrect access-block handling can race firmware or program PHY registers while driver access is blocked.
- Full-width scratch/spare/debug fields such as `0xFFFFFFFFL` should not be treated as general policy storage unless the hardware guide explicitly permits it.
- The CR address/data windows are only 16 bits in this range; code must not assume the surrounding 32-bit register word is fully payload.

## Test Signals

Useful validation is a mix of generated-header consistency and hardware behavior:

- Build AMDGPU display code that includes the DPCS 4.2.2 offset and shift/mask headers. Missing or renamed macros should surface in register-table construction and display link/encoder code.
- Mechanically compare lines 1-2378 against AMD's authoritative DPCS 4.2.2 register source, treating the final `RDPCSTX3_RDPCSTX_CLOCK_CNTL` register as a partial-boundary case.
- Check that normal fields have matching `__SHIFT` and `_MASK` macros, then reconcile expected imbalances with neighboring chunks before drawing whole-file conclusions.
- Diff mirrored `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2` field layouts where the hardware database expects identical layouts.
- Exercise panel power and backlight flows: enable/disable panel, suspend/resume, brightness changes, PWM fractional mode, frame-start synchronized updates, and power-up/down delay handling.
- Exercise DisplayPort/HDMI link bring-up through transmitter instances 0-2, including lane-count changes, link retraining, hotplug, mode-set, clock gating, reset recovery, and DP Alt Mode ownership transitions.
- Validate interrupt/status handling by checking that FIFO errors, DPALT toggles, register FIFO overflow, clear bits, and mask bits behave as expected without stale or accidentally cleared status.
- Use debug/OCLA/generic bus and scratch/spare readback only under documented diagnostic flows, verifying that reads do not depend on disabled clocks or powered-down PHY domains.

## Cross-Chunk Notes

This is the first chunk for `dpcs_4_2_2_sh_mask.h`, so it includes the file guard and initial DPCSSYS/PWRSEQ/DPCS transmitter definitions. It fully covers `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2` register-field groups but stops after the first mask in `RDPCSTX3_RDPCSTX_CLOCK_CNTL`. The next chunk is required to complete `RDPCSTX3` and continue the generated DPCS 4.2.2 field map before any final per-file report can make complete claims about all transmitter instances.

### subset-b-002338: lines 2379-4735

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 2379-4735

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for DCN 3.1.5 display PHY and DCIO register fields. It contains no executable C logic. Its public surface is preprocessor metadata that names bit positions (`__SHIFT`) and bit masks (`_MASK`) used by AMDGPU display code when composing, updating, or decoding hardware registers.

The requested range contains 2,176 `#define` entries across 2,357 lines: 1,083 shift constants and 1,093 mask constants. It starts inside `RDPCSTX3_RDPCSTX_CLOCK_CNTL`: the earlier shift definitions for that register are immediately before line 2379, while this chunk begins with its later shift fields and all masks. It then covers the rest of the `RDPCSTX3` transmitter instance, a complete `RDPCSTX4` transmitter instance, DCIO link and GPIO/DDC/AUX pad control registers, and the beginning of the `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED*` reserved-register block. It ends at `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED24`, so later reserved UNIPHY1 entries are outside the chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The generated API contract is:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating or setting that field.

The main macro families in this chunk are:

- `RDPCSTX3_RDPCSTX_*`: the tail of transmitter instance 3. The chunk includes clock enables and clock-on status for external reference, per-lane TX clocks, aggregate TX clock, alternate PHY reference clock, SRAM clock, and OCLA clock; interrupt status/clear/mask fields for register FIFO overflow, DPALT toggles, and TX FIFO errors; PLL update data and CR address/data access; SRAM memory power controls; scratch/spare registers; FIFO status and PHY encoding selection; DMCU DPALT disable/force controls; debug mux/counter configuration; PHY reset, power-gating, loopback, per-lane request/ack/reset/disable/data-enable, termination, lane inversion, EQ-bypass, HP protection, link rate/width/LPD/detect-RX, voltage swing/pre-emphasis, PLL frequency, HDMI override, TX enable selection, TX/RX OCLA buses, fuse fields, RX load values, DPALT PHY controls, extended PHY control/debug buses, byte-order changes, and PLL-update override address/data fields.
- `RDPCSTX4_RDPCSTX_*`: a full repeated transmitter instance with the same structure as `RDPCSTX3`, starting at `RDPCSTX4_RDPCSTX_CNTL` and running through `RDPCSTX4_RDPCS_TX_PLL_UPDATE_DATA_OVRRD`. It covers lane selection/packing/FIFO/register-block control, clock control, interrupt control, PLL/CR/SRAM/scratch/spare/control/debug/PHY/fuse/DPALT/OCLA/byte-order/update-override fields for transmitter 4.
- `DC_GENERICA`, `DC_GENERICB`, `DC_REF_CLK_CNTL`, `UNIPHY[A-E]_LINK_CNTL`, and `UNIPHY[A-E]_CHANNEL_XBAR_CNTL`: DCIO display-decoder fields for generic output pins, reference-clock gating, UNIPHY link enables, HDMI mode, HBR2 selection, DP link rate, channel enablement, and channel crossbar mapping/inversion.
- `DC_PINSTRAPS`: strap-readout fields for audio disable, embedded-display disable, VGA disable, external-display disable, and display-generation strap status.
- `DC_GPIO_*`: chip-level GPIO/DDC/HPD/power-sequencing pad registers. The generated pattern repeats mask, input/readback `A`, output-enable `EN`, and output-value `Y` fields for generic GPIO, DDC1-5, DDCVGA, GENLK, and HPD pads, plus power-sequence enables, pad-strength controls, TX12 enable, RX enable, and pull-up enable fields.
- `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5` and `AUXI2C_PAD_ALL_PWR_OK`: AUX/DDC electrical and pad-mode fields for six AUX/DDC PHYs, including I2C-over-AUX modes, pad control, N/P enable controls, AUX output/input enables and values, receive enable, pull-up enable, termination disable, D+/D- swap, hysteresis tuning, AUX control nibbles, voltage-output-drive tuning, DDC I2C mode, 1.2 V rail enables, pad I2C controls, and all-power-good status bits.
- `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED24`: full-width reserved macro-control slots. Each entry exposes a `UNIPHY_MACRO_CNTL_RESERVED` field at shift 0 with mask `0xFFFFFFFFL`.

Most values are 32-bit masks with an `L` suffix. The RDPCS/RDPCSTX and DCIO names are generated to match the companion offset header rather than to provide type safety or access semantics.

## Control Flow

This header has no runtime control flow. It participates in compile-time register table construction:

1. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes `dpcs/dpcs_4_2_2_offset.h` and this `dpcs/dpcs_4_2_2_sh_mask.h`.
2. DCN 3.1.5 resource code uses generated register-list, shift-list, and mask-list macros such as `DPCS_DCN31_REG_LIST`, `LINK_ENCODER_MASK_SH_LIST_DCN31`, `DPCS_DCN31_MASK_SH_LIST`, and `DCN3_1_RDPCSTX_REG_LIST` to build typed runtime register tables.
3. Link encoder, HPO DP link encoder, AUX/I2C, GPIO, and display-resource paths use those tables through AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. Actual sequencing for PHY reset, link training, lane enablement, PLL/update access, DPALT behavior, interrupt handling, AUX/DDC transactions, HPD/pad control, and suspend/resume lives outside this generated header.

The macros only describe bit layout. They do not encode reset values, read-only/write-only status, write-one-to-clear behavior, self-clearing fields, power-domain validity, clock-domain ordering, or firmware ownership.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible control and status:

- RDPCSTX3/RDPCSTX4 transmitter state includes lane source selection, data packing, FIFO delay/enables/start, CR/register-block enables, DPALT block status, soft reset, clocks, interrupt latches/clears/masks, PLL update data and override paths, CR address/data access, SRAM power state, scratch/spare fields, debug muxes/counters, PHY reset/power/clock/ack handshakes, loopback, lane term/invert/EQ/protection, link rate/width/LPD, detect-RX request/ack, voltage swing/pre-emphasis/presets, HDMI and PLL-frequency selection, fuses, RX load values, DPALT controls, OCLA bus selection, and byte-order-change fields.
- DCIO display-decoder state includes generic output values, reference clock enable/gating/status, UNIPHY link enable/HDMI/HBR2/rate controls, channel crossbar mapping, channel disable controls, and display-related strap readouts.
- GPIO/DDC/HPD/power-sequence state includes pad masks, input readback, output enable, driven output values, pad drive strength, pull-ups, RX enables, TX12 enables, and power-sequencer output enables.
- AUX/I2C pad state includes AUX electrical drive/tuning, D+/D- swap, receive enable, pull-up/termination controls, DDC I2C mode, per-DDC 1.2 V enable, per-DDC pad I2C control, and per-AUX/I2C PHY all-power-good readback.
- Reserved UNIPHY1 macro-control entries are full-width named placeholders. Their semantics are not documented by this header and should be treated as hardware-database-reserved unless the programming guide or firmware contract says otherwise.

Persistence is hardware-defined. Configuration fields usually remain until display modeset, link-disable/link-enable, PHY or DCIO power gating, suspend/resume, GPU reset, ASIC reset, or firmware reinitialization changes them. Status, ACK, interrupt, clock-on, power-stable, all-power-good, strap, and FIFO fields may be read-only, latched, self-clearing, clear-on-write, or valid only when the relevant display, PHY, AUX/DDC, or GPIO power/clock domain is active.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching register offsets and base indices. Examples in this range include `regRDPCSTX3_RDPCSTX_CLOCK_CNTL` at `0x2bb9`, `regRDPCSTX4_RDPCSTX_CNTL` at `0x2c90`, `regDC_GPIO_AUX_CTRL_5` at `0x291d`, `regAUXI2C_PAD_ALL_PWR_OK` at `0x291e`, and `regDCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` at `0x2a00`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` is the direct DCN 3.1.5 include site for this header pair. It defines the DPCS base segments and combines DPCS 4.2.2 field metadata with DCN 3.1.5 resource creation.
- DCN 3.1/3.1.5 link encoder and HPO DP link encoder code consume these register tables for link PHY programming and high-performance DisplayPort link control. Many consumers use canonical field-list macros whose token-pasted names resolve through this header.
- AUX/I2C, GPIO, HPD, DDC, power-sequencing, reference-clock, and UNIPHY setup paths rely on the DCIO and pad-control fields represented here, even when their higher-level code is shared with neighboring DCN generations.
- Adjacent generated DPCS variants such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h`, and DCN/DCE shift-mask headers containing matching DCIO field names, are useful for generator drift checks but are not interchangeable with DPCS 4.2.2.

Behaviorally, this range sits below user-visible display policy. It supports display link bring-up, physical lane mapping, DP/HDMI mode setup, PHY power and clock control, low-level diagnostics, AUX/DDC pad behavior, hotplug detection, and board-specific pad/strap interpretation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding hardware status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, `dpcs_4_2_2_offset.h`, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. The range starts after the first `RDPCSTX3_RDPCSTX_CLOCK_CNTL` shift definitions and ends before the wider UNIPHY1 reserved block is complete.
- RDPCSTX3 and RDPCSTX4 are highly repetitive. A generator or merge error can affect only one transmitter instance, one lane group, one lane within a group, or one of the repeated DPALT/debug/fuse/OCLA fields while nearby names still look correct.
- Clock, reset, request/ack, data-enable, PLL, SRAM power, power-stable, and all-power-good fields are sequencing-sensitive. Bad masks can cause stuck polling, false readiness, link-training failure, blank displays, or failed suspend/resume restore.
- Interrupt status, clear, and mask fields use similar names. Confusing status bits with clear bits or event masks can drop register FIFO, DPALT-toggle, or TX FIFO error events, or leave interrupts repeatedly asserted.
- PHY electrical fields such as termination, inversion, voltage swing, pre-emphasis, PLL frequency, HP protection, HDMI enable, AUX VOD, AUX hysteresis, D+/D- swap, pull-up, and pad-strength controls can fail only on specific boards, connectors, cable quality, link rates, or voltage/temperature corners.
- GPIO/DDC/HPD fields are shared with board wiring and BIOS/firmware assumptions. Wrong masks can break hotplug detection, DDC/I2C reads, AUX transactions, panel power sequencing, or external sync behavior.
- Full-width scratch, spare, PLL override data, and reserved UNIPHY fields can be tempting to treat as generic storage. They are hardware registers and may have firmware, debug, or reserved side effects not captured by this header.

## Test Signals

Useful validation combines generated-header consistency checks with display hardware behavior:

- Build AMDGPU display support for DCN 3.1.5. Missing, renamed, or malformed macros should surface in `dcn315_resource.c`, link encoder mask/shift tables, HPO DP link encoder tables, AUX/I2C tables, or GPIO-related register lists.
- Mechanically verify that every complete field in this range has the expected `__SHIFT` and `_MASK` pair, allowing the known split at `RDPCSTX3_RDPCSTX_CLOCK_CNTL`.
- Cross-check all complete register names in this range against `dpcs_4_2_2_offset.h`, including the RDPCSTX3/RDPCSTX4 instance transition and the DCIO address-block transitions.
- Run repetition checks between `RDPCSTX3_*` and `RDPCSTX4_*` where the hardware database expects identical field layouts, while allowing instance-specific register names and offsets.
- Compare against AMD's source register database and nearby generated variants such as DPCS 4.2.0, DPCS 4.2.3, and DCN/DCE DCIO headers for expected naming, mask-width, and field-presence differences.
- Exercise DisplayPort and HDMI link bring-up across available links, lane counts, link rates, and connector types. Watch for PHY reset/request/ack timeouts, PLL update failures, clock-on failures, FIFO errors, DPALT toggle errors, and link-training instability.
- Test hotplug, DDC EDID reads, AUX transactions, panel power sequencing, blank/unblank, modeset, suspend/resume, and GPU reset paths. Expected signals are stable HPD behavior, successful EDID/AUX reads, correct pad power-good state, and restoration of RDPCSTX and DCIO controls.
- Use register dumps during display failures to confirm that transmitter clock, lane mapping, PHY control, interrupt, DPALT, AUX/DDC pad, HPD, pull-up, and power-good fields decode correctly with these masks.
- Exercise debug and diagnostic surfaces where available: scratch/spare readback, OCLA selections, generic in/out buses, fuse readback, PLL-update override registers, DPALT controls, and UNIPHY crossbar settings.

## Cross-Chunk Notes

The previous chunk owns the start of the `RDPCSTX3_RDPCSTX_CLOCK_CNTL` register group and earlier `RDPCSTX3_RDPCSTX_CNTL` definitions. This chunk begins mid-group, completes RDPCSTX3, covers the full RDPCSTX4 transmitter instance, crosses into DCIO display-decoder and chip-level GPIO/AUX/DDC register blocks, and starts the `dpcssys_dcio_dcio_uniphy1_dispdec` reserved macro-control block. The next chunk should continue `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED24` onward and reconcile the reserved UNIPHY boundary before making whole-block claims.

### subset-b-002339: lines 4736-7219

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 4736-7219

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment. It covers lines 4736-7219 and defines 2,076 preprocessor constants: 1,043 `__SHIFT` constants and 1,033 `_MASK` constants. The unequal count is expected for this slice because it starts in the middle of the `DCIO_UNIPHY1` reserved-register run and ends after only the shift macro for `DPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0__PTTRN_MSK_CR1A_4_0`.

The file is declarative only. It contains no C functions, structs, enums, global variables, branches, loops, allocation, locking, I/O calls, or persistence code. Its exported surface is a set of generated symbolic bitfield definitions for display PHY and UNIPHY registers.

## Purpose

`dpcs_4_2_2_sh_mask.h` gives AMDGPU display code symbolic field positions and masks for DPCS 4.2.2 hardware registers. Consumer code pairs these macros with register addresses from `dpcs_4_2_2_offset.h` and the display core register-helper macros to compose read-modify-write operations without embedding raw bit numbers in driver logic.

This chunk specifically covers:

- The tail of the `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED*` field map and complete reserved macro-control maps for `DCIO_UNIPHY2`, `DCIO_UNIPHY3`, and `DCIO_UNIPHY4`.
- The start and most of the `DPCSSYS_CR0` indirect register-field namespace under address block `dpcssys_cr0_rdpcstxcrind`.
- Common/supervisor digital and analog control surfaces for reference clock overrides, MPLLA/MPLLB override/input/status fields, spread-spectrum fields, bandgap/prescaler/RTUNE fields, and MPLL power-control fields.
- Lane 0 ASIC-facing override/input/output fields and the beginning of lane 0 TX power-control, DCC DAC, clock-align, LBERT, and RX statistic match definitions.

## Exported API Surface

There are no callable APIs or local types. The public interface is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field.
- `REGISTER__FIELD_MASK` gives the bit mask for the same field.

Important macro families in this range:

- `DCIO_UNIPHY{1,2,3,4}_UNIPHY_MACRO_CNTL_RESERVED*`: full-width `UNIPHY_MACRO_CNTL_RESERVED` masks and shifts for reserved UNIPHY macro-control slots. These are 32-bit masks (`0xFFFFFFFFL`) and should not be treated as driver-owned scratch fields.
- `DPCSSYS_CR0_SUP_DIG_IDCODE_*`: low/high identification data fields for the CR0 DPCS block.
- `DPCSSYS_CR0_SUP_DIG_REFCLK_OVRD_IN`, `MPLLA_*_OVRD_IN`, `MPLLB_*_OVRD_IN`, `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, and `LVL_OVRD_IN`: digital override fields for reference clocks, PLL controls, divider/HDMI clocks, charge pump settings, power-good/state signals, and lane-level support signals.
- `DPCSSYS_CR0_SUP_DIG_*_ASIC_IN`, `BANDGAP_ASIC_IN`, `MPLLA_CP_ASIC_IN`, and `MPLLB_CP_ASIC_IN`: ASIC-sourced values that feed the same common support and PLL control paths when hardware rather than software override owns the signal.
- `DPCSSYS_CR0_SUP_ANA_*`: analog supervisor controls for prescaler, RTUNE, bandgap, MPLLA/MPLLB miscellaneous controls, override enables, analog test-bus selections, PLL control registers, and reserved analog fields.
- `DPCSSYS_CR0_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR0_SUP_DIG_MPLLB_MPLL_PWR_CTL_*`: MPLL power-control override, status, timer, calibration, DAC, and spread-spectrum selection fields for both PLLs.
- `DPCSSYS_CR0_SUP_DIG_CLK_RST_*` and `RTUNE_*`: common clock/reset bring-up timing and resistor-tuning configuration/status/set-value fields.
- `DPCSSYS_CR0_SUP_DIG_ANA_*_OVRD_OUT`, `ANA_STAT`, `ANA_BG_OVRD_OUT`, and `*_PMIX_OVRD_OUT`: digital-to-analog override output and status fields for PLL, RTUNE, bandgap, and PMIX paths.
- `DPCSSYS_CR0_LANE0_DIG_ASIC_*`: lane 0 loopback, TX/RX request, pstate, rate, width, MPLL select, reset, data enable, electrical cursor, beacon, async-data, VREG bypass, ACK, adaptation, and cross-lane clock/shift override surfaces.
- `DPCSSYS_CR0_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX power-state programming for P0/P0S/P1/P2, power-up timing, DCC bank/DAC controls, clock alignment, and TX LBERT controls.
- `DPCSSYS_CR0_LANE0_DIG_RX_STAT_*`: start of lane 0 RX statistic load/data/match-mask definitions.

## Register Areas Covered

The UNIPHY portion is a reserved macro-control map. It exposes a long sequence of full-width reserved fields for UNIPHY instances 1 through 4. The chunk starts at `UNIPHY1` reserved index 14, then includes all 58 reserved entries for `UNIPHY2`, `UNIPHY3`, and `UNIPHY4`. Because these are named reserved fields, consumers should preserve their values unless an AMD hardware sequence explicitly documents otherwise.

The `DPCSSYS_CR0_SUP_DIG_*` section is the common digital supervisor surface for the first DPCS CR instance. It includes ID fields, reference clock source/range/bandgap controls, MPLLA/MPLLB divided-clock and HDMI-clock overrides, PLL override-input bundles, spread-spectrum peak/step-size registers, support/status override paths, prescaler settings, debug, ASIC input mirrors, and level/bandgap/charge-pump inputs.

The `DPCSSYS_CR0_SUP_ANA_*` section maps common analog controls. It includes prescaler control, RTUNE control, bandgap trim/status fields, switch power measurement, MPLLA/MPLLB misc and override fields, analog test bus selectors, PLL control registers, and reserved analog slots. These fields affect PHY analog behavior and are tightly coupled to board, process, and ASIC stepping assumptions.

The MPLL power-control subsection appears twice, once for MPLLA and once for MPLLB. Each side defines override selection, clock enables, fast power-up/lock options, DTB/divider control, FSM state, lane ownership/status bits, lock/calibration/reset/status bits, DAC maximum range, lock and pclk-stable timers, calibration controls, analog DAC output, and SSC spread-type fields.

The clock/reset and RTUNE subsection defines bandgap/reference power-up timers, VPH underdrive timing, RTUNE debug/config/status fields, RX/TXDN/TXUP set values and readbacks, counter configuration, and TX calibration code fields. These are hardware calibration and sequencing registers rather than software-maintained state.

The digital-to-analog override-output subsection defines how digital logic can override or observe analog MPLLA/MPLLB, RTUNE, bandgap, and PMIX signals. Many fields are paired value and override-enable bits, so the field map is a contract for controlled bring-up, validation, or diagnostic code that needs to force a signal away from normal hardware ownership.

The lane 0 ASIC subsection maps the first lane's digital interface to the ASIC-side lane/TX/RX controls and status. It covers serial/parallel loopback, lane enable, ACJTAG enable, TX request/pstate/rate/width/MPLLB select/reset/data-enable/electrical cursor override fields, TX async and VREG bypass controls, TX/RX acknowledgement and status outputs, normal ASIC input mirrors, and cross-lane/master-lane clock synchronization override fields.

The lane 0 TX power-control subsection defines TX power states P0, P0S, P1, and P2. Common fields enable analog refgen, VCM hold, analog clock, word clock, analog reset, serial enable, digital clock, data, RX detect, and DCC compensation calibration. P2 additionally exposes `TX_P2_ALLOW_VBOOST`. The timing registers configure refgen/clock/VCM/VBOOST/RX-detect/reset/serial-enable waits and skip/fast-path controls. DCC fields expose CR bank address/data and DAC control/range/selection/request/ack/address. The end of this slice starts RX statistic matching after TX clock alignment and LBERT control.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior is created by driver code that selects these masks and shifts when programming hardware registers, and by the DPCS/UNIPHY hardware state machines that interpret those register values.

The field names imply several hardware sequences:

- Reference and PLL bring-up: reference clock overrides, bandgap enable/status, MPLLA/MPLLB override inputs, PLL power timers, lock timers, pclk-stable timers, calibration controls, and SSC fields participate in link clock setup and power transitions.
- Common analog calibration: RTUNE, bandgap, charge pump, prescaler, PMIX, analog override, and analog status fields expose low-level calibration and analog-control state.
- Lane 0 link state: TX request, reset, pstate, rate, width, data-enable, MPLLB select, electrical cursor, beacon, async data, and ACK/status fields describe the PHY-side part of DisplayPort/HDMI lane activation.
- Lane 0 power-state transitions: P0/P0S/P1/P2 and timing fields encode the sequencing of refgen, clocks, reset, serial enable, VCM hold, VBOOST, RX detect, and DCC compensation calibration.
- Diagnostics and validation: ACJTAG, analog test-bus, DTB selection, LBERT, DCC DAC, debug, and override-output fields support manufacturing, board validation, or deep hardware debug paths.

No software state is persisted in this file. Hardware register contents persist only according to the ASIC reset and power-domain behavior. Reserved fields and value/override-enable pairs must be handled by consumers with read-modify-write discipline and hardware-spec access semantics.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is AMD's generated DPCS 4.2.2 register database and the companion address header `dpcs_4_2_2_offset.h`.

In this source tree, `dpcs_4_2_2_sh_mask.h` is included by `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` together with `dpcs_4_2_2_offset.h`. That resource file also defines the DPCS base segments used for DCN 3.1.5 display hardware. The offset header maps the direct DPCS CR address/data windows, RDPCSTX register ranges, and repeated instance bases; this shift/mask header supplies the bitfield layer for those addresses.

Likely higher-level integration points include DCN 3.1.5 resource construction, link encoder and PHY setup, DisplayPort/HDMI link training, hotplug and link-rate/lane-width changes, power management, suspend/resume, PHY calibration, manufacturing test, and debug code that reads or writes DPCS indirect registers through the CR address/data windows.

## Risks

- Generated-header drift is the primary risk. A wrong shift or mask can silently program the wrong PHY bit and cause display link failures that look like training, clocking, or board issues.
- The slice contains many value and override-enable bit pairs. Setting a value without the matching enable bit may do nothing; leaving an enable bit asserted can force hardware away from normal state-machine control.
- Reserved UNIPHY and analog fields are numerous and sometimes full-width. Treating them as software-owned fields can corrupt undocumented hardware state.
- MPLLA and MPLLB fields are structurally similar. Copy/generation mistakes between the A and B PLL families can create asymmetric behavior depending on clock source selection.
- Lane 0 TX power-state and timing fields directly affect analog sequencing. Incorrect timings or skip/fast bits can break RX detect, VBOOST behavior, DCC compensation, or PLL/clock stability.
- The chunk ends mid-register at `DPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0`; merge/reconciliation must not assume the RX statistic match group is complete here.
- Mask constants do not encode access type. Status, clear, latch, and write-one-to-clear semantics must come from the hardware spec or surrounding driver accessors.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Preprocess or build AMDGPU DCN 3.1.5 code that includes `dcn315_resource.c`, `dpcs_4_2_2_offset.h`, and `dpcs_4_2_2_sh_mask.h`.
- Static checks that complete register groups have paired `__SHIFT` and `_MASK` definitions; for this exact sliced range expect 1,043 shifts and 1,033 masks because of boundary cuts.
- Compare generated field names against `dpcs_4_2_2_offset.h` and adjacent ASIC revisions to detect missing or renamed CR0 supervisor, analog, MPLL, RTUNE, lane 0, and UNIPHY register groups.
- Runtime display validation on DPCS 4.2.2/DCN 3.1.5 hardware: DP and HDMI link training, link-rate and lane-count changes, hotplug, suspend/resume, low-power entry/exit, and recovery from display blanking.
- Hardware readback should show expected transitions for reference clock enable, bandgap/RTUNE status, MPLL lock/calibration/FSM state, pclk stable, TX request/ACK, RX/adapter status, TX pstate sequencing, DCC DAC ACK, and LBERT/statistic paths when exercised.
- Debug/manufacturing validation should explicitly clear any override-enable bits it sets for analog, PLL, RTUNE, PMIX, lane, TX, RX, DCC, ACJTAG, and cross-lane synchronization tests.

## Chunk Notes For Merge

This document intentionally covers only lines 4736-7219 of `dpcs_4_2_2_sh_mask.h`. Earlier chunks should cover the beginning of the file and the start of `DCIO_UNIPHY1`; later chunks should continue lane 0 RX statistic/match fields and the remaining DPCS lane/register blocks. The final merged per-file report should describe the whole file as a generated ASIC register bitfield map for DPCS 4.2.2 rather than handwritten driver logic, with `dcn315_resource.c` and `dpcs_4_2_2_offset.h` as the primary in-tree anchors.

### subset-b-002340: lines 7220-9580

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 7220-9580

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for CR0 lane register fields. It contains only C preprocessor constants: `__SHIFT` macros identify bit positions and `_MASK` macros identify the corresponding field masks. The range starts inside `DPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0`, covers the rest of CR0 lane 0 RX statistic and TX analog definitions, then covers a broad CR0 lane 1 region from ASIC-facing override/status fields through TX/RX power, calibration, adaptation, statistics, MPHY, digital analog overrides, and analog TX registers. It ends after the `__SHIFT` definitions for `DPCSSYS_CR0_LANE1_ANA_TX_DCC_DAC`.

## Purpose

The header provides register-field metadata used by AMDGPU display/PHY code when programming DPCS 4.2.2 hardware. Driver code can combine these masks and shifts with matching address macros from `dpcs_4_2_2_offset.h` to perform read-modify-write operations against indexed CR registers without embedding numeric bit layouts in the caller.

In this range, the fields describe:

- CR0 lane 0 RX statistic pattern matching, sample counters, statistic counters, statistic clocks, valid-loss control, and stop control.
- CR0 lane 0 TX digital-to-analog override outputs, termination-code override/clock controls, TX equalization taps, DCC DAC controls, fast-start/loopback controls, and raw analog TX measurement/power/ATB/termination/miscellaneous registers.
- CR0 lane 1 ASIC override and ASIC status interfaces for lane, TX, RX, RX equalization, RX CDR/VCO, cross-lane clock/shift handshakes, and OCLA clock/data enables.
- CR0 lane 1 TX power-state controls, power-up timing, DCC CR-bank/DAC access, TX clock alignment, and TX LBERT control.
- CR0 lane 1 RX power-state controls, RX power-up timing, VCO calibration controls/status, RX alignment/LBERT, CDR/DPLL controls, RX adaptation configuration/status, RX statistic counters, MPHY controls, RX/TX analog overrides, and analog TX registers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or callable APIs in this chunk. The public interface is the generated macro naming convention:

- `DPCSSYS_CR0_LANE*_...__FIELD__SHIFT`: bit offset for `FIELD`.
- `DPCSSYS_CR0_LANE*_...__FIELD_MASK`: mask for the same field after shifting.
- Register delimiter comments such as `//DPCSSYS_CR0_LANE1_DIG_RX_CDR_CDR_CTL_0` identify field groups that correspond to `ix...` address macros in the companion offset header.

Notable lane 0 groups include:

- `DIG_RX_STAT_*`: pattern CR1A/CR1B match fields, data masks, sample/count enable bits, clock/control selectors, done bits, calibration comparator clock controls, extended pattern-mask registers, and statistic stop.
- `DIG_ANA_TX_*`: digital override outputs for TX clocks, refgen, VCM hold, reset, serial/data enable, data rate, div4/RX detect, termination code, driver source, DCC calibration, fast start, loopback, AC JTAG, and TX equalization coefficients such as pre/post cursor and main cursor fields.
- `DIG_ANA_STATUS_0` and raw `ANA_TX_*`: status/measurement paths and analog TX controls for power override, alternate bus/ATB measurement selection, DCC DAC/control, termination code, override clocking, and miscellaneous/reserved analog registers.

Notable lane 1 groups include:

- `DIG_ASIC_*`: ASIC-facing lane/TX/RX override inputs, output status, TX/RX ASIC inputs, RX equalization inputs, RX CDR/VCO input fields, extra cross-lane override registers, and OCLA data/clock enables.
- `DIG_TX_PWRCTL_*`: per-power-state TX enables for refgen, VCM hold, analog/digital clocks, reset, serial, data, RX detect, VBOOST allowance, and DCC calibration, plus power-up timing and DCC DAC register access.
- `DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, and `DIG_RX_DPLL_*`: RX analog/clock/AFE/adaptation/CDR power controls, VCO calibration, CDR status/configuration, and DPLL frequency/bounds.
- `DIG_RX_ADPTCTL_*`: RX adaptation configuration, ATT/VGA/CTLE/DFE tap status, slicer/DAC offsets, adaptation reset, DAC control selection, and CR-bank access.
- `DIG_RX_STAT_*` and `DIG_MPHY_*`: statistic pattern/counter controls plus MPHY PWM/termination and clock-stability fields.
- `DIG_ANA_RX_*`, `DIG_ANA_TX_*`, and raw `ANA_TX_*`: digital analog override/status fields for RX/TX power, VCO, calibration, DAC selection, AFE, scope, slicer, phase/IQ controls, signal-change enables, squelch/signal detect, TX DCC/equalization, analog measurement, power override, ATB selection, and TX DCC DAC.

## Control Flow

This header contributes no runtime control flow. Runtime sequencing is implemented by AMD display/PHY code that uses these constants to assemble register values, typically by clearing bits with a `_MASK`, shifting a field value by the matching `__SHIFT`, and writing the result to the DPCS register address from the offset header.

The implied hardware control paths are display PHY bring-up and diagnostics: TX/RX power transitions, TX startup timing, RX VCO/CDR/DPLL setup, RX adaptation, lane alignment, LBERT testing, RX statistic sampling, MPHY low-speed behavior, and analog override programming.

## State And Persistence

The macros are stateless compile-time constants. The state they describe lives in DPCS hardware registers and is volatile hardware state, not persisted by this header. Values can be changed by display link training, PHY reinitialization, hotplug handling, suspend/resume, GPU/display reset, power gating, or diagnostic/debug code. Reserved masks are present so consumers can preserve or avoid undocumented bits during read-modify-write sequences.

## Dependencies

This chunk depends on the AMD ASIC register-generation pipeline staying synchronized with DPCS 4.2.2 hardware specifications. It is normally consumed with:

- `dpcs_4_2_2_offset.h`, including lane 0 addresses such as `ixDPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0` at `0x1082` and lane 1 addresses beginning at `ixDPCSSYS_CR0_LANE1_DIG_ASIC_LANE_OVRD_IN` around `0x1100`.
- AMDGPU display/DC register access helpers that combine address, mask, and shift constants for indexed DPCS CR MMIO access.
- Link-training, PHY power-management, receiver adaptation, and debug/validation code in the AMD GPU driver.

The file is part of an imported Linux GPU driver tree under this repository and has no dependency on Ceph filesystem logic.

## Integration Points

These definitions integrate with AMD display link bring-up, DisplayPort/HDMI PHY tuning, high-speed lane power sequencing, receiver calibration, and diagnostic paths. Lane 0 content in this slice is mostly RX statistic and TX analog-side control, while lane 1 content spans the whole lane control surface from ASIC handshakes to analog TX/RX programming. The companion offset header supplies the physical register addresses; the macros here supply the bit layout for those addresses.

The repetitive lane-specific naming is an important integration contract. A consumer must pair `DPCSSYS_CR0_LANE1_*` masks with the lane 1 `ixDPCSSYS_CR0_LANE1_*` register address, not with lane 0 or another CR instance. ASIC-version specificity also matters: these are `dpcs_4_2_2` layouts and should not be mixed casually with nearby `dpcs_4_2_0` or `dpcs_4_2_3` headers unless the caller explicitly gates by the matching ASIC register block.

## Risks

- The range starts in the middle of `DPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0`; the preceding chunk is needed for the full field list of that register.
- The range ends before the `_MASK` definitions for `DPCSSYS_CR0_LANE1_ANA_TX_DCC_DAC`; the following chunk is needed to complete that register summary.
- Generated mask/shift mistakes would compile cleanly but could silently program the wrong hardware bits.
- Writing reserved bits, failing to preserve reserved bits, or mixing lane/ASIC-version macros can destabilize the analog PHY or misprogram a different physical lane.
- TX/RX power-state, reset, DCC, VCO/CDR/DPLL, adaptation, and analog override fields are sequencing-sensitive. Incorrect use can cause link training failures, display blanking, intermittent high-rate instability, or misleading diagnostic counter results.
- Many fields have override-enable companions; setting an override value without the corresponding enable, or leaving an enable asserted after diagnostics, can make later normal link management behave unexpectedly.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`.
- Static checks that each field has matching `__SHIFT` and `_MASK` constants, that masks match their shifts and widths, and that DPCS CR masks fit the expected 16-bit register shape unless a register is known wider.
- Display bring-up on hardware using DPCS 4.2.2, including boot display, modesets, hotplug, suspend/resume, GPU reset recovery, and multi-monitor operation.
- Link-training stress across lane counts and rates, especially CR0 lane 0 statistic paths and CR0 lane 1 TX/RX power/adaptation paths.
- PHY diagnostics that exercise TX/RX LBERT, RX statistic counters, pattern-match controls, VCO/CDR/DPLL status, DCC DAC selection/acknowledgement, MPHY controls, and analog override/status readback.

### subset-b-002341: lines 9581-11939

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 9581-11939

## Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.2 shift/mask register header. It contains C preprocessor constants only; each useful symbol describes either a field bit offset (`...__SHIFT`) or a pre-shifted field mask (`..._MASK`) for DPCSSYS CR lane registers. Runtime display code pairs this file with `dpcs_4_2_2_offset.h` and AMD display register helpers so link/PHY code can compose indexed DPCS register reads and writes without embedding numeric bit positions.

The requested range is a line-bounded PHY slice. It starts in the tail of `DPCSSYS_CR0_LANE1_ANA_TX_DCC_DAC`, completes lane 1 analog TX/RX control and measurement fields, covers a large lane 2 digital and analog PHY block, and ends at the comment for `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2`. The `RX_PWR_CTRL2` fields themselves are outside this chunk. The range contains 2,140 `#define` lines across 219 register groups: 1,069 shift definitions and 1,071 mask definitions. The small imbalance is expected because the first visible register began in the previous chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, allocation paths, locks, callbacks, or executable APIs in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position, usually in a 16-bit-style DPCS CR register payload and emitted with an `L` suffix.

The important source-aligned register families are:

- `DPCSSYS_CR0_LANE1_ANA_TX_*`: tail of lane 1 analog transmitter fields for DCC DAC selection/control, termination code and update/reset controls, TX clock override, VREG/current behavior, slew/inversion/peaking options, ATB force bits, and reserved low-byte fields.
- `DPCSSYS_CR0_LANE1_ANA_RX_*`: lane 1 analog receiver fields for CDR/VCO startup and clock enable overrides, IQ phase adjustment, loopback clock, deserializer/word-clock controls, slicer controls, AFE/DFE/DESER/loopback power overrides, signal-detect threshold/response, calibration mux selections, ATB regulator/reference and measurement controls, VDAC ranges, CDR regulator behavior, and reserved fields.
- `DPCSSYS_CR0_LANE2_DIG_ASIC_*`: lane 2 digital ASIC override, ASIC input, and ASIC output fields for loopback, lane enable, RX AC JTAG, TX/RX request/p-state/rate/width, MPLLB selection, data enable, TX main/pre/post cursor values, HDMI mode, clock-ready, RX detect, polarity inversion, low-power detect, DC coupling, MPHY mode, reset, boost/equalization controls, VCO/DAC controls, signal detect, adaptation status, ACK/valid flags, OCLA, and repeat/master lane clock synchronization.
- `DPCSSYS_CR0_LANE2_DIG_TX_PWRCTL_*`: lane 2 TX p-state recipes for P0/P0S/P1/P2, TX power-up timing fields, DCC CR bank address/data, DCC DAC enable/range/selection/ack/address fields, clock alignment, and TX LBERT control.
- `DPCSSYS_CR0_LANE2_DIG_RX_PWRCTL_*`, `*_RX_VCOCAL_*`, `*_RX_CDR_*`, and `*_RX_DPLL_*`: lane 2 RX p-state and timing controls, RX VCO calibration controls/status/timers, XAUI comma mask, RX LBERT control/error count, CDR/SSC/PI controls, CDR lock/status, DPLL frequency, and DPLL frequency bounds.
- `DPCSSYS_CR0_LANE2_DIG_RX_ADPTCTL_*`: lane 2 receiver adaptation configuration and status fields for ATT, VGA, CTLE, DFE taps 1-5, even/odd data and error VDAC offsets, slicer controls, error slicer level, adaptation reset, DAC selector controls, and CR bank address/data access.
- `DPCSSYS_CR0_LANE2_DIG_RX_STAT_*`: data-mask, match-control, statistic-control, sample-count, statistic counter, calibration-comparator clock, additional match controls, statistic-control extension, and statistic-stop fields.
- `DPCSSYS_CR0_LANE2_DIG_MPHY_*`: MPHY low-speed PWM, termination, and analog PWM clock-stability fields.
- `DPCSSYS_CR0_LANE2_DIG_ANA_*`: digital-to-analog bridge fields for TX override outputs, TX termination-code outputs, TX equalization outputs, RX control/power/VCO override outputs, RX calibration/DAC/AFE/CTLE/scope/slicer/IQ controls, analog status readback, MPHY override outputs, signal-detect override outputs, and TX DCC DAC override outputs.
- `DPCSSYS_CR0_LANE2_ANA_TX_*`: direct lane 2 analog TX fields for override measurement, power override, alternate bus, ATB muxing/measurement, DCC DAC, termination code and update/reset controls, clock overrides, miscellaneous TX controls, and reserved fields.
- `DPCSSYS_CR0_LANE2_ANA_RX_CLK_1`, `CLK_2`, `CDR_DES`, `SLC_CTRL`, and `PWR_CTRL1`: beginning of direct lane 2 analog RX fields for CDR/VCO startup, RX clock enable override, IQ phase adjustment, loopback clock, word-clock/deserializer controls, slicer controls, AFE/ACJT power controls, common-mode selection, and attenuator pulldown.

Reserved, `NC*`, and `RSVD*` fields are still emitted as masks. They are part of the register layout contract even when ordinary driver code should preserve them rather than treat them as programmable features.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consumers:

1. DCN315 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Register-list macros such as `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(__SHIFT/_MASK)` token-paste DPCS register and field names into link-encoder register tables.
3. Link encoder, PHY, clock/power, training, and diagnostics code uses those tables through AMD register helpers to read, write, update, and poll DPCS fields.
4. Hardware and firmware sequencing decides when to apply p-state recipes, rate/width changes, resets, CDR/DPLL/VCO calibration, RX adaptation, TX DCC settings, LBERT/loopback modes, statistic sampling, or analog override paths.

The macros do not encode access semantics. They do not say whether a field is read-only, sticky, write-one-to-clear, self-clearing, reset-sensitive, or safe to modify while a link is active.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It describes hardware-backed lane state:

- Lane 1 analog TX/RX trim, clocking, DCC, termination, CDR/deserializer, slicer, signal-detect, ATB, and calibration selection state.
- Lane 2 digital override and normal ASIC interface state for lane requests, p-states, rate/width, data enable, cursor/equalization, reset, detect, polarity, loopback, low-power, MPHY, VCO/DAC, adaptation, and status handshakes.
- Lane 2 TX/RX p-state recipes and power-up wait counters used by hardware sequencing.
- Lane 2 RX clock recovery, VCO calibration, DPLL, CDR, SSC, adaptation, slicer, CTLE/VGA/DFE, statistic counter, and LBERT state.
- Lane 2 digital-to-analog bridge state and direct analog TX/RX override/measurement state.

Persistence is device-local and tied to hardware reset and power domains. Configuration fields can remain until a modeset, link retrain, lane reset, DPCS block reset, power-gate transition, suspend/resume restore, or ASIC reset. Status, ACK, calibration, counter, and measurement fields can change asynchronously while the PHY trains, calibrates, enters low power, receives symbols, or runs diagnostics.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which provides the matching indexed DPCS register addresses and base-index metadata. Shifts and masks are not meaningful without the correct offset header.

The direct include site found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes both the DPCS 4.2.2 offset and shift/mask headers and builds DCN315 link encoder register, shift, and mask tables. The shared macro definitions live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` through `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`.

Functionally, these fields integrate with AMD display link encoder and PHY paths: DisplayPort/HDMI lane bring-up, link training, lane-rate and lane-width programming, p-state transitions, suspend/resume restore, hotplug-triggered retraining, clock recovery, RX adaptation, analog trimming, signal-detect handling, loopback/BERT diagnostics, statistic counters, and manufacturing/debug access through ATB/OCLA-style paths.

The generated namespace is ASIC-version-specific. Nearby headers such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` have similar shapes, but consumers must bind the DPCS 4.2.2 mask file to the DPCS 4.2.2 offset file and the target DCN315 register tables unless the hardware database explicitly says a layout is shared.

## Risks And Edge Cases

- Shift/mask drift is high impact. These are untyped preprocessor constants, so a one-bit error can compile cleanly while writing a neighboring PHY field.
- Offset/header mismatch can apply a valid field mask to the wrong indexed DPCS register address.
- Override-enable fields are hazardous. `*_OVRD*`, p-state, reset, rate, width, cursor, termination, DCC, VCO, CDR, DPLL, MPHY, loopback, and analog mux fields can force hardware away from normal sequencing.
- Lane-instance mistakes may be connector-specific. A lane 1 or lane 2 table error may only reproduce on displays or link configurations that use that physical lane.
- Reserved and `NC` fields are exposed as masks. Driver read-modify-write paths should preserve them unless hardware documentation requires an explicit value.
- Timing and count fields are narrow. Callers must clamp or mask software values before shifting so high bits do not spill into adjacent fields.
- Status, ACK, counter, and calibration fields can be transient or side-effect-sensitive. Wrong masks can cause polling timeouts, false adaptation status, lost LBERT/statistic data, stuck calibration flows, or bad link-training decisions.
- The chunk boundaries are artificial. The first visible register is only the mask tail of `LANE1_ANA_TX_DCC_DAC`, and the final `LANE2_ANA_RX_PWR_CTRL2` comment has no fields in this range. Whole-register validation needs neighboring chunks.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU/DC with DCN315 support enabled so `dcn315_resource.c`, `dcn31_dio_link_encoder.h`, and DPCS register-table expansion catch missing, renamed, or malformed macros.
- Mechanically verify shift/mask pairing after merging adjacent chunks. For this exact range, 1,069 shifts and 1,071 masks are expected because the start boundary includes masks whose shifts are above line 9581.
- Cross-check `dpcs_4_2_2_sh_mask.h` against `dpcs_4_2_2_offset.h` so every covered register group has a matching indexed register address and base-index context.
- Compare repeated lane 1/lane 2 field layouts against adjacent lane blocks and nearby generated DPCS 4.2.x variants where the hardware register database expects matching geometry.
- Exercise display links using the affected lanes across link rates, lane counts, hotplug, retraining, suspend/resume, low-power entry/exit, and mode changes. Watch for lane-specific training failures, blank displays, repeated retraining, stuck reset/power status, or signal-detect errors.
- Run PHY diagnostics where available: LBERT/loopback, statistic counters, CDR/DPLL/VCO calibration polling, RX adaptation status, TX DCC DAC programming, OCLA/ATB measurement routing, and analog status readback.
- Inspect kernel logs and register dumps for wrong ACK/valid bits, unexpected p-state recipes, invalid cursor/equalization values, stuck calibration-done fields, counter overflow handling problems, or connector-specific instability after generated-register changes.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR0_LANE1_ANA_TX_DCC_DAC`. The next chunk owns all fields under `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2` and continues later lane 2 analog RX definitions. The final per-file research document should reconcile those boundaries before making whole-file claims about DPCS 4.2.2 lane coverage or shift/mask pairing.

### subset-b-002342: lines 11940-14316

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 11940-14316

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY registers. It contains no executable logic; it exports preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for indirect DPCS hardware registers.

The requested range spans 2,377 source lines, with 2,124 `#define` entries and 253 register-comment markers. It begins at the first field of `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2` but excludes that register's comment marker at line 11939. It then completes late lane-2 analog RX controls, covers a broad CR0 lane-3 digital/analog lane programming section, moves into CR0 raw common PLL/supervisor and RTUNE controls, and continues through CR0 raw lane0 PCS, PMA, FSM, IRQ, MPHY, and RX-adaptation transfer registers. The last line in this chunk is only the marker for `DPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL`; that register's field definitions start in the next chunk.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display hardware metadata. It is not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The public interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, compose, or update that field.

Major register families covered by this chunk include:

- Lane 2 analog RX tail registers: `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2`, `ANA_RX_SQ`, `ANA_RX_CAL1`, `ANA_RX_CAL2`, `ANA_RX_ATB_REGREF`, `ANA_RX_ATB_MEAS1` through `MEAS4`, `ANA_RX_ATB_FRC`, and `ANA_RX_RESERVED1`. These describe DFE/deserializer/loopback/fast-start enable overrides, squelch response/threshold, RX calibration muxes, regulator/test-bus references, ATB measurement selection, and reserved analog latches.
- Lane 3 ASIC-facing digital override and status registers: `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`, `DIG_ASIC_TX_OVRD_IN_0` through `_5`, `DIG_ASIC_TX_OVRD_OUT`, `DIG_ASIC_RX_OVRD_OUT_0`, `DIG_ASIC_LANE_ASIC_IN`, `DIG_ASIC_TX_ASIC_IN_*`, `DIG_ASIC_TX_ASIC_OUT`, and `DIG_ASIC_RX_ASIC_OUT_0`. These fields expose request, pstate, rate, width, MPLL select, data-enable, reset, beacon, async, cursor, EQ, deemphasis, termination, loopback, and acknowledge-style handshakes between ASIC control logic and the lane PHY.
- Lane 3 TX power/control and debug registers: `DPCSSYS_CR0_LANE3_DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, `P2`, `TX_PWRUP_TIME_*`, `DCC_CR_BANK_*`, `DCC_DAC_*`, `DIG_TX_CLK_ALIGN_TX_CTL_0`, and `DIG_TX_LBERT_CTL`. These encode pstate-specific TX settings, power-up timing, DCC bank access and DAC selection/acknowledgement, clock alignment, and link built-in error-test controls.
- Lane 3 RX statistics registers: `DPCSSYS_CR0_LANE3_DIG_RX_STAT_*` groups define sample-load values, data masks, match controls, statistic/correlation selectors, sample/stat counters, pause/clock controls, valid-loss handling, calibration comparison clock controls, extended match controls, statistic stop, and related status/control fields.
- Lane 3 digital-to-analog TX/RX surfaces: `DPCSSYS_CR0_LANE3_DIG_ANA_TX_OVRD_OUT`, TX term-code and EQ override groups, `DIG_ANA_STATUS_0`, TX DCC DAC override groups, and `DIG_ANA_TX_OVRD_OUT_2`. The companion analog TX groups `DPCSSYS_CR0_LANE3_ANA_TX_*` cover measurement overrides, power overrides, alternate bus selection, ATB control, DCC DAC/control, termination-code programming, override clocking, slew/vreg/misc controls, and reserved registers.
- CR0 raw common controls: `DPCSSYS_CR0_RAWCMN_DIG_CMN_CTL`, MPLLA/MPLLB override and SSC override groups, lane FSM extension, common control, MPLL state control, TX calibration code, SRAM init status, OCLA, supervisor analog overrides, PCS and firmware ID readbacks, AON RTUNE RX/TXDN/TXUP values for lanes 0-7, SRAM bitline config, AON power-gating overrides, supervisor overrides, VREF statistics, resistor/reference-range overrides, and miscellaneous common configuration.
- CR0 raw lane0 PCS transfer registers: `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_TX_*`, `RX_*`, `RX_ADAPT_*`, directed TX cursor feedback registers, lane number, ATE overrides, RX EQ delta/IQ controls, TX/RX termination controls, and PH2 calibration. These fields model the transfer interface between PCS control and lane PHY state for TX/RX rate, pstate, width, reset, request, data enable, loopback, beacon, adaptation, FOM, and termination behavior.
- CR0 raw lane0 FSM and fast-path controls: `DPCSSYS_CR0_RAWLANE0_DIG_FSM_*` groups define FSM overrides, memory/status monitors, fast RX startup/adapt/AFE/DFE/bypass/reference-level/IQ calibration controls, fast supervisor/TX common-mode/RX detect/RX power-up/VCO wait/VCO calibration controls, MPLL and RCAL calibration status, continuous calibration/adaptation flags, CR lock, TX DCC flags/status, TX EQ update flag, OCLA selection, and RX IQ phase offset.
- CR0 raw lane0 IRQ controls: `DPCSSYS_CR0_RAWLANE0_DIG_IRQ_CTL_*` defines reset-return request, RX reset/request/rate/pstate/adaptation IRQs, corresponding clear registers, IRQ mask and mask-2 fields, lane transceiver-mode IRQs, PH2 calibration request/disable IRQs, serial loopback IRQs, DCC on-demand status, TX reset/request IRQs, and TX clear registers.
- CR0 raw lane0 PMA transfer registers: `DPCSSYS_CR0_RAWLANE0_DIG_PMA_XF_*` groups expose PMA lane and supervisor override inputs/outputs, TX/RX request/reset/data-enable/loopback/beacon/async/DWORD-clock override outputs, TX/RX PMA acknowledgements, lane RTUNE request and acknowledgement, MPHY PWM/termination/asynchronous controls, and RX PMA IQ phase-adjust adaptation override output.

Most masks in this region use low 16-bit values with an `L` suffix, consistent with DPCS indirect register fields. Reserved and `NC` fields are also exported as masks; callers must still treat their semantics as hardware-defined.

## Control Flow

This header has no runtime control flow. It participates in compile-time register metadata setup:

1. AMD display code for the matching ASIC generation includes this DPCS 4.2.2 shift/mask header and the companion offset header.
2. Version-specific register, shift, and mask tables refer to these generated token names, often through register helper macros and token-pasted field names.
3. Runtime driver paths use those tables with helpers such as register read, write, get, set, and update operations.
4. Actual sequencing for lane power, link training, PLL setup, RX adaptation, RX statistic capture, PMA/PCS handshakes, DCC/RTUNE calibration, IRQ clear/mask behavior, and debug capture lives outside this generated header.

The macros describe bit layout only. They do not encode access type, reset value, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, timing requirements, clock-domain restrictions, or power-domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR0 DPCS lane and raw-lane registers:

- Lane 2 RX analog state includes DFE, deserializer, loopback, fast-start, squelch, calibration mux, ATB measurement/reference, regulator, and reserved analog fields.
- Lane 3 ASIC and lane PHY state includes TX/RX request, reset, pstate, rate, width, MPLL selection, data enable, beacon, async drive, loopback, cursor, pre/main/post EQ, deemphasis, termination, vboost, receive-detect, acknowledgements, and state-machine-facing status.
- Lane 3 TX power state includes pstate-specific TX control values, power-up timing, DCC DAC/bank state, clock alignment, and LBERT test settings.
- Lane 3 RX statistic state includes match masks, match patterns, statistic/correlation source selection, sample counters, statistic counters, done bits, clock/pause controls, valid-loss controls, and stop controls.
- Lane 3 analog TX state includes power overrides, measurement muxes, ATB routing, DCC DAC values, termination codes, override clocks, slew/vreg/peaking controls, and status readbacks.
- Raw common state includes MPLLA/MPLLB override and SSC fields, lane FSM operation extension, MPLL state controls, TX calibration code, SRAM init status, OCLA selection, firmware and PCS IDs, AON RTUNE values across lanes, common power-gating/supervisor/resistor/reference-range controls, and VREF statistics.
- Raw lane0 PCS/PMA/FSM state includes PCS transfer request/reset/data-enable/loopback/rate/pstate/width signals, RX adaptation ACK/FOM and directed TX coefficient feedback, termination controls, PH2 calibration, fast calibration/adaptation enables, continuous adaptation/calibration status, lane IRQ status/clear/mask bits, PMA handshakes, lane RTUNE, MPHY PWM/termination/asynchronous controls, and RX PMA IQ phase adjustment.

Persistence is determined by hardware. Configuration fields generally remain until modeset or link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, IRQ, statistic, calibration, and handshake fields may be latched, sampled, self-clearing, clear-on-write, or valid only while their lane/common clock and power domains are active. This header does not define those semantics.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DPCS 4.2.2 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`.

Observed companion offset anchors include:

- `ixDPCSSYS_CR0_LANE3_DIG_ASIC_TX_OVRD_IN_0` at `0x1301`, matching the lane-3 ASIC transfer area in this chunk.
- `ixDPCSSYS_CR0_RAWCMN_DIG_CMN_CTL` at `0x2000`, matching the raw common section.
- `ixDPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN` at `0x3000`, matching the raw lane0 PCS transfer section.
- `ixDPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL` at `0x3080`, matching the next register marker at the chunk end.

The macros integrate with AMDGPU display DCN/DPCS resource code through generated register/shift/mask tables rather than through direct local logic in this file. Consumers include low-level display PHY initialization, DisplayPort and HDMI link training, clock and PLL programming, lane power transitions, hotplug and modeset paths, diagnostics, debug register dumps, IRQ handling, suspend/resume restore, and manufacturing or ATE test paths.

Firmware or hardware state machines interact with many of the same fields, especially raw common MPLL/SSC controls, AON RTUNE values, lane FSM fast-path controls, DCC calibration, PMA/PCS request/acknowledge transfers, RX adaptation, PH2 calibration, and IRQ latches. Driver code must use the correct offset namespace and lane instance when pairing these field masks with register addresses.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- The source chunk boundary excludes the `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2` comment marker while including all of that register's field macros. The final line is only the `DPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL` comment marker; its actual masks and shifts are in the next chunk.
- Several register groups contain repeated pairs such as value plus override-enable, status plus clear, or input plus output. Mixing those masks can force hardware state unintentionally, miss an IRQ clear, or read an override shadow instead of live state.
- Analog RX/TX fields affect electrical behavior. Incorrect masks for DFE, deserializer, squelch, slicers, calibration muxes, ATB, termination, EQ, DCC DACs, vreg, slew, CDR, loopback, or fast-start controls can cause black screens, unstable links, compliance failures, or misleading debug traces.
- Raw common MPLLA/MPLLB and SSC override fields are clock-sensitive. Bad fields around PLL enable/divider, standby, SSC, calibration, or lane FSM extension can cause link lock failures, retraining loops, mode-specific instability, or suspend/resume regressions.
- AON RTUNE and power-gating fields are lane-wide/common resources. A field error can affect multiple lanes even when the broken macro name appears local to one generated block.
- Raw lane0 PCS/PMA override paths can bypass normal state-machine behavior. Misprogramming request/reset/data-enable/loopback/rate/pstate/width/RTUNE/MPHY/PH2 fields can leave a lane in a state that higher-level display code cannot infer correctly.
- IRQ status, clear, and mask groups repeat very similar names. Confusing status with clear or mask fields can drop events, leave stale interrupts latched, or create repeated interrupt storms.
- RX statistic and adaptation controls are easy to validate only under stressed links. Wrong masks may not be visible in basic modes but can break high-rate links, marginal cables, diagnostics, or factory test flows.

## Test Signals

Useful validation should combine generated-header checks with real display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in lines 11940-14316 has a matching `__SHIFT` and `_MASK` definition, allowing the known boundary cases for the missing `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2` comment and the marker-only `DPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL`.
- Cross-check all complete register groups against `dpcs_4_2_2_offset.h`, especially the transitions from lane2 analog RX to lane3 digital/analog, then to raw common, then to raw lane0 PCS/FSM/IRQ/PMA areas.
- Diff this generated region against AMD's source register database and nearby DPCS variants such as 4.2.0 and 4.2.3 where layouts are expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lanes, pstate transitions, hotplug, stream disable/enable, suspend/resume, and GPU reset. Expected signals are stable link training, correct MPLL selection, no stuck PMA/PCS ACK bits, clean IRQ clear/mask behavior, and no unexpected retraining loops.
- Validate high-bandwidth and clock-sensitive modes that stress MPLLA/MPLLB override, SSC, RTUNE, pstate, RX adaptation, TX EQ, DCC, and analog termination fields. Watch for blank displays, PHY lock failures, corruption, audio/video timing instability, rate-specific failures, or compliance regressions.
- Use register dumps or PHY debug traces during failures to confirm that DFE/deserializer/squelch/calibration, RX statistic counters, DCC DAC/status, RTUNE values, FSM status, IRQ status/clear/mask bits, PMA/PCS transfer state, MPHY controls, and RX adaptation FOM/ACK decode correctly.
- Exercise diagnostic paths where available: LBERT, OCLA, RX statistic match/count controls, analog test bus/readback fields, directed TX coefficient feedback, PH2 calibration, loopback controls, ATE overrides, and MPHY low-speed controls.

## Cross-Chunk Notes

The previous chunk ends immediately before this range with `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL1` and the comment marker for `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2`. This chunk owns all `PWR_CTRL2` field definitions and continues through lane2 RX analog tail, lane3 digital/analog controls, raw common controls, and raw lane0 PCS/FSM/IRQ/PMA transfer surfaces. The next chunk should start with the actual `DPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_TX_FSM_CTL` field definitions and continue raw lane0 TX/RX control coverage. The final per-file report should reconcile those artificial boundaries before making whole-file claims.

### subset-b-002343: lines 14317-16696

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 14317-16696

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask register-field slice. It contains no executable C logic; it publishes preprocessor constants that describe bit offsets and masks for DPCS CR0 raw-lane digital registers used by AMDGPU display link-encoder code. The companion `dpcs_4_2_2_offset.h` file supplies the matching MMIO/indexed-register addresses, while this header supplies the field geometry needed by register helpers and macro-generated shift/mask tables.

The requested range covers 2,111 `#define` entries: 1,058 `__SHIFT` macros and 1,053 `_MASK` macros. It starts in the tail of `RAWLANE0`, contains the full register-field map for `RAWLANE1`, and continues through most of the early `RAWLANE2` map. The chunk boundary is artificial: it stops after the first two masks for `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_TX_OVRD_IN_2`, with the remaining masks for that register immediately after line 16696.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or callable APIs in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset of a DPCS register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, or update that field.

The covered register groups are all under `DPCSSYS_CR0_RAWLANE<n>_DIG_*`:

- `RAWLANE0` tail: TX control, RX control, ATE RX/TX override inputs, master MPLL loop enables, VCO/reference load override fields, RX-valid override output, and late TX override input bits.
- `RAWLANE1` complete lane slice: PCS transmit and receive override/input/output registers; RX equalization, adaptation, figure-of-merit, lane number, TX pre/main/post cursor direction registers; FSM override/status/fast-step monitor registers; IRQ request/status/clear/mask registers; PMA override/input registers; TX/RX control registers; and ATE override registers.
- `RAWLANE2` early lane slice: the same PCS, FSM, IRQ, PMA, TX/RX control, and ATE register pattern through the first two masks of `PCS_XF_TX_OVRD_IN_2`.

Important field families in this chunk include:

- Link operating-state fields such as `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, and master MPLL state/override enables.
- TX/RX request, reset, data-enable, async-data, beacon, RX detect, RX valid, and serial/parallel loopback override value/enable pairs.
- RX adaptation and calibration controls/status: `ADAPT_REQ`, `ADAPT_ACK`, `ADAPT_DONE`, `ADAPT_FOM`, IQ/AFE/DFE/reflvl calibration fast-step bits, continuous calibration/adaptation fields, and PH2 calibration.
- Equalization and termination controls: TX pre/main/post direction fields, RX EQ delta/IQ override fields, TX/RX termination control override fields, and PMA lane/termination/tune controls.
- IRQ state and acknowledgement fields for RX/TX reset/request/rate/pstate/adapt transitions, lane transceiver mode, PH2 calibration, loopback changes, DCC on-demand, and mask registers.
- Observability/test hooks, including `OCLA`, `UPCS_OCLA`, `FSM_*_MON`, reserved monitor slots, ATE override registers, and PMA/MPHY override inputs/outputs.

Most fields are 16-bit register layouts represented with 32-bit-looking mask literals in this version (`0x0000....L`). Reserved fields are also emitted as macros, so consumers must avoid treating their presence as permission to write undocumented bits.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMD display code that includes generated offset and shift/mask headers, builds register tables, and uses those tables through register helper macros.

The typical path is:

1. ASIC-specific resource or link-encoder code includes the matching DPCS offset and shift/mask headers.
2. Register-list macros select concrete `ixDPCSSYS_CR0_RAWLANE...` offsets from `dpcs_4_2_2_offset.h`.
3. Field-list macros use token-pasting helpers such as `LE_SF(<reg>, <field>, __SHIFT)` and `LE_SF(<reg>, <field>, _MASK)` to initialize `struct dcn10_link_enc_shift` and `struct dcn10_link_enc_mask` instances.
4. Link encoder and PHY programming paths use `REG_GET`, `REG_SET`, `REG_UPDATE`, indexed register reads/writes, or equivalent helpers to update individual fields without hard-coding bit positions.

The chunk itself does not encode programming order. Sequencing for resets, PLL enablement, rate/width changes, lane power states, RX adaptation, IRQ acknowledgement, loopback/test overrides, and PMA controls is determined by the display link-encoder implementation and the hardware programming guide.

## State And Persistence Behavior

This file stores no software state and persists nothing on its own. It describes hardware state in the DPCS CR0 raw-lane register space:

- Lane configuration state for link rate, lane width, power state, low-power detect, MPLL selection/enables, and RX/TX data/clock enables.
- TX and RX finite-state-machine state, including fast calibration/adaptation step bits, status monitors, CR lock, DCC flags/status, and lane reset/request handshakes.
- Interrupt state and control bits for lane events, with separate status, clear, and mask registers.
- PHY-facing PMA and PCS state for lane overrides, PMA inputs/outputs, RX valid, RX adaptation, equalization, TX cursor direction, termination, VCO/reference load overrides, and loopback controls.
- Test/debug state for ATE overrides, OCLA/UPCS OCLA, MPHY overrides, and reserved monitor registers.

Persistence is hardware-defined. Configuration fields generally last until the driver reprograms the link, disables or power-gates the PHY, performs suspend/resume restore, resets the display engine, or resets the ASIC. Status, IRQ, acknowledgement, calibration, and monitor bits may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant clock and power domains are active. The generated macros do not identify access type or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DPCS 4.2.2 register database and especially with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which defines the matching `ixDPCSSYS_CR0_RAWLANE...` register addresses. For example, the offset file maps `RAWLANE0` TX/RX/ATE registers around `0x3080`-`0x30c8`, `RAWLANE1` around `0x3100`-`0x31c8`, and `RAWLANE2` around `0x3200` onward, matching the lane repetition visible in this shift/mask chunk.

Display integration is through AMDGPU display link-encoder register tables:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.h` defines `DPCS_DCN2_MASK_SH_LIST(mask_sh)`, which expands field constants into link-encoder shift/mask tables through `LE_SF(...)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c` initializes `le_shift` with `DPCS_DCN2_MASK_SH_LIST(__SHIFT)` and `le_mask` with `DPCS_DCN2_MASK_SH_LIST(_MASK)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.h` extends the DPCS field list with CR0 `RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_2` and `RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_3` VCO/reference load override fields, which are present in this chunk.
- Later DCN resource files use similar DPCS mask/shift table patterns, so generated-field correctness affects link bring-up, PHY control, debug override plumbing, and power-management behavior across ASIC variants that consume this register family.

The most direct behavioral integration from this chunk is display PHY and DisplayPort/HDMI link-lane control: link training, lane rate/width programming, MPLL gating, lane reset/request handshakes, RX adaptation/calibration, lane IRQ handling, and diagnostic/ATE paths.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bit, corrupting a neighboring field, missing a status bit, or clearing an interrupt incorrectly.
- The file is generated metadata. Manual edits risk divergence from the offset header, AMD's authoritative register database, firmware expectations, and silicon documentation.
- Lane definitions are repetitive but not risk-free. A generator or copy/paste error can affect only `RAWLANE1` or `RAWLANE2`, so one working lane does not prove the others are correct.
- The chunk boundary cuts through `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_TX_OVRD_IN_2`: shifts and two masks are inside this range, while the remaining masks are in the next chunk. Consumers and merged research must consider the full register definition across chunk boundaries.
- Reserved field masks are emitted. Code should preserve reserved bits unless the hardware specification explicitly says otherwise.
- Override registers often pair a value bit with an enable bit. Setting only the value or only the enable can leave hardware in normal mode, force stale values, or wedge debug/test paths.
- IRQ/status/clear registers are side-effect-sensitive. Confusing status fields with clear fields, or mask fields with enable fields, can cause missed HPD/link events, interrupt storms, or stuck lane state.
- PMA/PCS calibration and MPLL controls are timing-sensitive. Incorrect field geometry or sequencing can cause link-training failures, unstable high-rate links, silent black screens, or suspend/resume-only regressions.
- Some masks use the wider `0x0000....L` literal style compared with older DPCS headers that use shorter 16-bit masks. Mechanical comparisons across ASIC revisions should normalize values before flagging differences.

## Test Signals

Useful validation is mostly compile-time plus hardware/link behavior:

- Build AMDGPU display code for ASIC configurations that include DPCS 4.2.2 headers. Missing, renamed, or malformed macros should fail in link-encoder/resource table initializers that token-paste register and field names.
- Run a generated-header consistency check that verifies every `__SHIFT` has the expected `_MASK` within the full file, while allowing this chunk's artificial split for `RAWLANE2_DIG_PCS_XF_TX_OVRD_IN_2`.
- Compare `dpcs_4_2_2_sh_mask.h` against `dpcs_4_2_2_offset.h` and adjacent generated revisions (`dpcs_4_2_0`, `dpcs_4_2_3`) for lane-stride consistency and intended field-layout changes.
- Exercise display link bring-up at multiple DisplayPort rates and lane counts, including retraining, hotplug, suspend/resume, and modeset transitions.
- Validate lane-specific behavior on one-, two-, and four-lane configurations so `RAWLANE1` and `RAWLANE2` paths are actually programmed, not just `RAWLANE0`.
- Check diagnostics for IRQ clear/mask behavior, RX adaptation completion, link-training status, DCC status, and PMA/PCS debug outputs when hardware and debug tooling expose them.
- For changes to override/test fields, use targeted ATE or debug-mode tests; normal desktop display tests may never touch those bits.

### subset-b-002344: lines 16697-19117

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h - subset-b-002344

## Scope

This chunk covers lines 16697-19117 of the generated AMD DPCS 4.2.2 shift/mask header. It is a compile-time register-field map, not executable driver logic. The visible content begins in the tail of the `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_TX_OVRD_IN_2` mask block, then defines the full `DPCSSYS_CR0_RAWLANE3_*` digital lane 3 PCS/FSM/IRQ/PMA/TX/RX field masks, and ends after the `DPCSSYS_CR0_RAWAONLANE2_DIG_FAST_FLAGS_2` block with the next `RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS` register header starting at the boundary.

## Purpose

The header exposes symbolic `__SHIFT` and `_MASK` constants for DPCS CR0 lane registers. Consumers combine these constants with matching register offsets from the DPCS offset headers and AMD register access helpers to read, modify, or decode packed hardware registers without hard-coded bit numbers.

Within this chunk, the purpose is mainly lane bring-up, training, override, interrupt, and status support:

- `RAWLANE3_DIG_PCS_XF_*` describes PCS-facing TX/RX request, reset, power-state, link-rate, width, MPLL, loopback, adaptation, equalization, ATE, and RX validity controls for raw lane 3.
- `RAWLANE3_DIG_FSM_*` describes the lane finite-state-machine control, status, fast-calibration shortcut flags, command lock/status, OCLA/debug, TX DCC, common calibration, and RX IQ phase status fields.
- `RAWLANE3_DIG_IRQ_CTL_*` maps lane 3 interrupt status, clear, and mask bits for RX/TX reset/request, rate/pstate/adaptation transitions, lane transceiver mode, phase-2 calibration, loopback, and DCC on-demand events.
- `RAWLANE3_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` define the PMA interface, test/override outputs, lane/supervisor power and clocking signals, TX/RX control FSM knobs, data-enable/LOS timing, and OCLA visibility.
- `RAWAONLANE0/1/2_DIG_*` defines always-on lane analog/training status and calibration data: AFE/DFE offsets, adaptation result values, coarse MPLL tune, power-up done, fast flags, common-calibration status, disable bits, signal-detect data, DCC calibration data, firmware config bits, and lane transceiver mode.

## Important Constants And Register Families

The file has no C types, functions, structs, enums, or callable APIs in this range. Its public API is the generated macro namespace. Each register appears as a comment marker followed by one or more `REGISTER__FIELD__SHIFT` constants and matching `REGISTER__FIELD_MASK` constants. Most registers are 16-bit logical fields represented in 32-bit C constants with an `L` suffix.

Key lane 3 PCS register families:

- TX inputs and override inputs: `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN`, `_IN_1`, `_IN_2`, and `TX_PCS_IN` map reset/request, `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, master MPLL override states, TX async/data enables, TX beacon, detect-RX request, voltage/current boost, and TX-to-RX serial loopback fields.
- TX outputs: `TX_OVRD_OUT` and `TX_PCS_OUT` expose acknowledge, detect-RX result, enable control, and TX dword clock sync override/status bits.
- RX inputs and override inputs: `RX_OVRD_IN`, `_IN_1`, `_IN_2`, `_IN_3`, `RX_PCS_IN`, and `_IN_1` through `_IN_4` cover request, rate, width, power state, low-power disable, CDR/VCO/ref load values, AFE/DFE adaptation enables, LOS threshold, continuous adaptation/off-cancellation controls, RX data enable, RX clock enable, phase-2 calibration request, and RX-to-TX loopback fields.
- RX outputs and adaptation status: `RX_OVRD_OUT`, `RX_OVRD_OUT_1`, `RX_OVRD_OUT_2`, `RX_PCS_OUT`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, and `RX_TXPOST_DIR` expose ack/data-valid/adaptation result values and transmitter equalization direction hints derived from RX adaptation.
- Equalization/test controls: `RX_EQ_DELTA_IQ_OVRD_IN`, `RX_EQ_OVRD_IN_1`, `RX_EQ_OVRD_IN_2`, `TXRX_TERM_CTRL_OVRD_IN`, `TXRX_TERM_CTRL_IN`, `RX_PH2_CAL`, `ATE_OVRD_IN`, `ATE_RX_OVRD_IN*`, `ATE_TX_OVRD_IN*`, and `MASTER_MPLL_LOOP` map explicit override/test paths for ATE and diagnostics.

Key lane 3 control/status families:

- `DPCSSYS_CR0_RAWLANE3_DIG_FSM_FSM_OVRD_CTL` provides FSM jump address, jump enable, command start, override enable, and break bits. `FSM_MEM_ADDR_MON` and `FSM_STATUS_MON` expose FSM memory address and state/ALU/wait/mask status.
- Per-feature fast-path registers such as `FSM_FAST_RX_STARTUP_CAL`, `FSM_FAST_RX_ADAPT`, `FSM_FAST_RX_AFE_CAL`, `FSM_FAST_RX_DFE_CAL`, `FSM_FAST_SUP`, `FSM_FAST_TX_RXDET`, `FSM_FAST_RX_PWRUP`, and `FSM_FAST_RX_VCO_CAL` each carry a one-bit fast mode plus reserved bits. `FSM_FAST_FLAGS` packs the same family into a consolidated bitfield.
- `FSM_CMNCAL_MPLL_STATUS` and `FSM_CMNCAL_RCAL_STATUS` expose common-calibration init/done bits. `FSM_CR_LOCK`, `FSM_TX_DCC_FLAGS`, `FSM_TX_DCC_STATUS`, `FSM_TX_EQ_UPDATE_FLAG`, `FSM_RX_IQ_PHASE_OFFSET`, and `FSM_OCLA` cover command-register lock/debug, TX DCC calibration, TX equalization update, RX IQ phase, and observation/debug latching.
- `IRQ_CTL_*` registers are split into event status, event clear, and masks. `IRQ_MASK` packs RX reset/req/rate/pstate/adapt, return reset request, TX reset/req, lane mode, phase-2 calibration, loopback, and DCC events; `IRQ_MASK_2` covers additional TX reset/request mask bits.
- `PMA_XF_*` registers bridge PCS-side control to the PMA: lane/supervisor override inputs and outputs, TX/RX PMA inputs, MPHY override input/output, lane RTUNE, and RX adaptation override output.
- `TX_CTL_*` and `RX_CTL_*` define lane-local controller policy and debug fields such as TX/RX FSM enables, rate-change behavior, TX clock enable mode, TX DCC continuous status, LOS mask count, RX data enable override count, internal reference tracking count, off-cancellation/adaptation continuous status, and UPCS/OCLA data/clock enables.

Key always-on lane families:

- Lanes 0 and 1 are represented with complete repeated `DPCSSYS_CR0_RAWAONLANE{0,1}_DIG_*` blocks in this chunk. Lane 2 begins at `AFE_ATT_IDAC_OFST` and continues through `FAST_FLAGS_2`; the `LANE_CMNCAL_RCAL_STATUS` block begins but is completed by the next chunk.
- Analog/adaptation result registers include `AFE_ATT_IDAC_OFST`, `AFE_CTLE_IDAC_OFST`, `RX_ADPT_IQ`, `RX_ADAPT_FOM`, `DFE_*_VDAC_OFST`, `DFE_*_REF_LVL`, `RX_PHSADJ_LIN`, `RX_PHSADJ_MAP`, `RX_IQ_PHASE_ADJUST`, `RX_ADPT_ATT`, `RX_ADPT_VGA`, `RX_ADPT_CTLE`, `RX_ADPT_DFE_TAP1` through `TAP5`, and `RX_ADAPT_DONE`.
- Power and calibration status/control registers include `INIT_PWRUP_DONE`, `LANE_CMNCAL_MPLL_STATUS`, `LANE_CMNCAL_RCAL_STATUS` for lanes 0 and 1, `MPLLA_COARSE_TUNE`, `MPLLB_COARSE_TUNE`, `MPLL_DISABLE`, `MPLL_BG_CTL`, `RX_SIGDET_CAL`, DCC calibration code registers, `TX_DCC_BANK_ADDR`, `TX_DCC_BANK_DATA`, and `TX_DCC_CONT`.
- Packed fast-control registers `FAST_FLAGS` and `FAST_FLAGS_2` mirror lane FSM fast-path concepts: RX startup/adapt/AFE/DFE/bypass/ref-level/IQ/power/VCO calibration, supervisor and TX RX-detect shortcuts, continuous calibration/adaptation shortcuts, TX/RX DCC, VPHUD/VREF, TX RTUNE skip, and signal-detect calibration.
- Firmware and mode registers include `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, `FW_CALIB_CONFIG`, `LANE_XCVR_MODE_OVRD_IN`, `LANE_XCVR_MODE_IN`, `RX_SIGDET_CONFIG`, and `TX_DCC_CONFIG`.

## Control Flow

There is no software control flow in this chunk. Hardware-facing control flow is implied by the register groups:

1. Driver code selects the DPCS 4.2.2 register-offset/mask set for an ASIC.
2. Code reads or writes a 16-bit lane register through the AMD MMIO/register abstraction.
3. For writes, a value is shifted by the corresponding `__SHIFT` and constrained by the corresponding `_MASK`.
4. Override enable bits gate whether a forced value replaces the normal PCS/PMA/FSM signal.
5. Status and ack bits are read back to verify reset/request handshakes, adaptation completion, calibration completion, signal detect, RX validity, TX/RX DCC state, or IRQ events.

The chunk separates normal PCS/PMA inputs from override/test inputs. That split matters operationally: setting an `*_OVRD_VAL` field without the paired `*_OVRD_EN` bit generally should not affect hardware, while setting an enable bit with a stale value can force a lane into an unintended reset, power, loopback, or adaptation state.

## State And Persistence

These macros do not store software state and do not persist data themselves. They describe volatile hardware register fields whose state lives in the GPU DPCS block. Persistence and reset behavior are hardware-defined:

- `RAWLANE3` fields describe live lane state, handshakes, masks, clears, and override controls.
- `RAWAONLANE*` fields are in the always-on lane namespace and can remain observable across parts of lane power sequencing, but the header does not define exact retention semantics.
- `*_IRQ_CLR` fields imply write-to-clear style interrupt behavior in consuming code, while `*_IRQ_MASK` fields persist as register-programmed masks until changed or reset.
- Calibration/adaptation result fields expose current or last hardware calibration values; software should treat them as snapshots that can change after retraining, hotplug, link-rate changes, or power transitions.

## Dependencies And Integration Points

This header is generated hardware metadata. It is normally included alongside the matching DPCS 4.2.2 offset header and consumed by AMDGPU display/link code through register helper macros that know how to combine register addresses, masks, shifts, and instance/lane selection.

Important integration points:

- AMD display link bring-up and retraining code can use TX/RX `REQ`, `ACK`, `RATE`, `WIDTH`, `PSTATE`, `LPD`, `MPLL`, adaptation, and LOS fields to coordinate PHY lane state.
- Diagnostics, factory/ATE flows, and low-level debug tooling can use the ATE and override fields to force reset/request/data/clock/loopback/equalization behavior.
- Interrupt handling uses the `IRQ_CTL_*` status, clear, and mask definitions to detect lane changes and clear latched events.
- Calibration and telemetry paths use `RAWAONLANE*` result fields to inspect AFE/DFE/CTLE/VGA/DCC/signal-detect state and calibration outcomes.
- Cross-generation headers under the same `asic_reg/dpcs/` directory may contain similarly named macros for other DPCS revisions; consumers must pair this file with the DPCS 4.2.2 offset definitions for the target ASIC.

## Risks And Review Notes

- Generated macro drift is the primary risk. A wrong shift or mask silently programs the wrong hardware bit and may only appear as unstable link training, failed hotplug, broken low-power transitions, or hard-to-reproduce display failures.
- The namespace is repetitive across lanes and DPCS revisions. Accidentally mixing a DPCS 4.2.2 mask with another generation's offset or using a lane 3 mask for a differently laid-out register can compile cleanly but touch the wrong field.
- Several control fields are destructive or disruptive when written: reset overrides, request overrides, loopback enables, MPLL disable/select, TX/RX data enable overrides, DCC/calibration controls, IRQ clears, and FSM override/jump/break bits.
- Reserved masks are explicitly present. Write paths should preserve reserved bits with read-modify-write helpers unless hardware documentation says otherwise.
- The chunk boundary splits related content: it starts after the lane 2 TX override block has already begun, and it ends just before the lane 2 always-on `LANE_CMNCAL_RCAL_STATUS` fields. The merge lane should not infer that either neighboring register group is complete from this chunk alone.

## Test Signals

Useful validation for code that consumes this header:

- Build coverage for the ASICs that include `dpcs_4_2_2_sh_mask.h`; generated macro names should resolve without fallback to another DPCS generation.
- Register pack/unpack unit checks can assert representative fields: multi-bit fields such as `RATE`, `WIDTH`, `PSTATE`, `FSM_JMP_ADDR`, `RX_LOS_THRSHLD_OVRD_VAL`, `VCO_LD_VAL_OVRD`, `CTLE_BOOST_ADPT_VAL`, and DFE tap masks should round-trip through shift/mask helpers.
- Hardware or emulation smoke tests should exercise link bring-up, hotplug/retraining, low-power entry/exit, interrupt clear/mask paths, RX adaptation completion, signal detect, and DCC/calibration status reads.
- Debug/test flows that set overrides should verify paired value/enable behavior and then restore normal control, especially for reset, request, loopback, MPLL, TX/RX data enable, and ATE fields.
- Cross-header consistency checks should compare repeated `RAWAONLANE0`, `RAWAONLANE1`, and `RAWAONLANE2` field layouts where the same register family appears in this chunk, while respecting that lane 2 continues in the next chunk.

### subset-b-002345: lines 19118-21534

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 19118-21534

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It contains no executable C logic; it publishes preprocessor constants for bit positions (`__SHIFT`) and masks (`_MASK`) used to access fields in DPCS indirect hardware registers.

The requested range contains 2,101 `#define` entries across 316 register comment groups. It starts at `DPCSSYS_CR0_RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS`, continues through the tail of raw always-on lane 2 controls, complete raw always-on lane 3 controls, the raw always-on lane-X template controls, and a large CR0 supervisor (`SUPX`) digital/analog/MPLL section. It ends inside `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`: only the first mask for that register is in this chunk, with the remaining masks in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for the hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, compose, or update the field.

The main macro families in this chunk are:

- `DPCSSYS_CR0_RAWAONLANE2_DIG_*`: tail of raw always-on lane 2, covering common RCAL status, TX/RX disable overrides, RX loss-of-signal mask timing, RX signal-detect filtering, RX status, RX PMA/squelch/VREF/termination/signal-detect overrides, signal-detect calibration codes, VREF enable, current/VREF calibration codes, RX DCC calibration code banks, TX DCC bank address/data/continuous enable, MPLL bandgap control, signal-detect output override/input, firmware memory/adaptation/calibration configuration, lane transceiver-mode override/input, RX signal-detect configuration, and TX DCC configuration.
- `DPCSSYS_CR0_RAWAONLANE3_DIG_*`: complete repeated raw always-on lane 3 register map for RX adaptation offsets, DFE reference/data/error/bypass values, RX IQ and FOM readback, MPLLA/MPLLB coarse tune, power-up done state, adaptation status, fast calibration flags, DFE taps, slicer controls, common MPLL/RCAL status, adaptation control words, MPLL disable, TX/RX disable overrides, LOS/signal-detect controls, RX PMA override outputs, calibration code registers, DCC banks, firmware config, lane mode, signal-detect, and TX DCC config.
- `DPCSSYS_CR0_RAWAONLANEX_DIG_*`: lane-X template version of the same raw always-on lane controls. This is used as a generic lane pattern rather than a fixed physical lane number and mirrors the lane 3 fields for adaptation, DFE, calibration, overrides, signal-detect, firmware config, and DCC setup.
- `DPCSSYS_CR0_SUPX_DIG_*`: supervisor digital fields for ID code, reference-clock override, MPLLA/MPLLB divider and HDMI clock overrides, PLL override inputs, SSC peak/stepsize words, fractional PLL words, charge-pump overrides, supervisor/prescaler/level overrides, debug, ASIC-provided PLL and supervisor inputs, bandgap inputs, charge-pump ASIC inputs, MPLL power-control state, PLL timers, calibration override, analog DAC readback, SSC spread type, and the start of clock/reset power-up timing.
- `DPCSSYS_CR0_SUPX_ANA_*`: supervisor analog fields for prescaler control, RTUNE control, bandgap controls, switch power measurement, MPLLA/MPLLB analog miscellaneous controls, overrides, analog test bus selectors, PLL control words, and reserved analog words.

Most masks are 16-bit-style values with an `L` suffix, matching the DPCS indirect register-field convention. The companion offset header maps representative groups in this chunk to offsets such as `0x422e` for `RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS`, `0x4300` for lane 3 raw always-on fields, `0x7000` for the lane-X template, `0x8000` for supervisor ID code, and `0x807b` for `CLK_RST_REF_PWRUP_TIME_0`.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Generated register-list, shift-list, and mask-list initializers token-paste register and field names into AMD Display Core resource tables.
3. Runtime display code uses register helpers to read, write, get, set, or update individual fields through the matching offsets and these shift/mask constants.
4. Actual sequencing for lane power, RX adaptation, signal-detect calibration, DCC/RTUNE calibration, MPLL programming, reference-clock setup, PLL power control, bandgap bring-up, and supervisor analog controls lives in AMDGPU display code, firmware, and hardware state machines outside this header.

The macros only describe bit layout. They do not encode reset values, access width beyond the mask shape, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, polling order, clock-domain restrictions, or power-domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR0 raw always-on lane and supervisor DPCS registers:

- Lane 2 tail state includes common RCAL init/done status, TX/RX disable override state, RX LOS mask count, signal-detect filter settings, RX PMA status, PMA override values/enables, signal-detect calibration thresholds and codes, VREF/current calibration code latches, RX DCC calibration code banks, TX DCC bank address/data/continuous enable, MPLL bandgap control, firmware config bits, lane transceiver mode, and signal-detect/DCC configuration.
- Lane 3 and lane-X state includes RX adaptation values for ATT/VGA/CTLE/DFE, DFE even/odd reference and data/error/bypass offsets, slicer controls, adaptation done flags, fast calibration/adaptation flags, continuous calibration flags, common MPLL/RCAL status, coarse-tune values, RX IQ phase and FOM readback, PMA RX override outputs, signal-detect status/override, and DCC/calibration code registers.
- Supervisor digital state includes ID-code readback, reference-clock and divider/HDMI clock overrides, MPLLA/MPLLB enable/divider/VCO/fractional/SSC/standby/calibration/clock-sync controls, charge-pump and gain-scheduled charge-pump controls, supervisor override inputs/outputs, prescaler and level overrides, ASIC-driven PLL/supervisor inputs, bandgap inputs, MPLL power-control FSM status, PLL lock status, PCLK/output/feedback clock enables, timer values, calibration override, analog DAC output readback, SSC spread type, and clock/reset power-up timing.
- Supervisor analog state includes prescaler enable/divider/output controls, RTUNE comparator and manual tuning controls, bandgap calibration and power measurement controls, MPLLA/MPLLB analog overrides, ATB/test-bus selectors, loop-filter/capacitor/current/DAC/VCO-related PLL controls, and reserved analog latches.

Persistence is hardware-defined. Programmed control and override fields generally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, calibration, statistic, ACK, and lock fields may be latched, sampled, self-clearing, read-only, or only valid while the relevant lane/common clock and power domains are active. This generated header does not define those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion address map:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` offsets for the register groups whose fields are defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`, tying this generated contract to DCN 3.1.5 resource construction.
- The AMD Display Core register-helper layer consumes the generated offset, shift, and mask tables to access hardware without open-coding bit positions.
- Firmware and hardware state machines share these fields with the driver for RX adaptation, signal detection, DCC and RTUNE calibration, PLL power sequencing, reference-clock control, bandgap bring-up, and debug or manufacturing override paths.

Behaviorally, this range sits below the user-facing display stack. DisplayPort/HDMI link bring-up, PHY clock programming, lane calibration, hotplug/modeset, suspend/resume, diagnostics, and manufacturing/ATE flows can depend on these bitfield definitions being exactly correct.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong hardware bit, corrupting a reserved field, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The range is repetitive across lane 2, lane 3, and lane-X. A generator or merge error can affect only one lane/template while nearby fields look correct.
- Many registers pair override value bits with override enable bits. Leaving enable bits asserted after debug or validation use can bypass normal PHY, supervisor, or PLL state-machine control.
- PLL, SSC, fractional divider, charge-pump, bandgap, prescaler, and clock/reset timing fields are timing-sensitive and electrically significant. Bad masks can produce clock instability, lock failures, black screens, rate-specific retraining loops, or compliance regressions.
- RX adaptation, DFE, slicer, signal-detect, DCC, VREF, and RTUNE fields are calibration-sensitive. Incorrect bit definitions can cause subtle link-training failures, degraded margins, misleading debug readbacks, or stuck polling loops.
- Status and control fields with similar names repeat across override, ASIC input, supervisor output, and power-control blocks. Consumers must pair each mask with the correct offset block and access semantics.
- Chunk boundaries are artificial. This chunk starts cleanly at `RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS`, but it ends mid-register at `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`; the `FAST_REF_WAIT` and reserved masks are outside this slice.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for DCN 3.1.5. Missing, renamed, or malformed macros should fail where `dcn315_resource.c` and generated register tables consume DPCS 4.2.2 symbols.
- Mechanically verify that complete register groups in this range have matching `__SHIFT` and `_MASK` definitions, allowing the known end-boundary exception for `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`.
- Cross-check every complete register group in this chunk against `dpcs_4_2_2_offset.h`, especially the transitions from raw always-on lane 2 to lane 3, lane-X, and supervisor offsets.
- Diff against AMD's generated source register database and adjacent DPCS versions such as 4.2.0 or 4.2.3 where compatible hardware layout is expected.
- Exercise DP and HDMI link bring-up across lane counts, link rates, power states, and hotplug/modeset paths. Expected signals are stable link training, successful RX adaptation, correct signal-detect behavior, PLL lock, and no unexpected lane or supervisor timeout.
- Exercise suspend/resume, GPU reset, low-power entry/exit, and display disable/enable paths to catch stale override, bandgap, reference-clock, PLL, DCC, RTUNE, or calibration state.
- Use register dumps or PHY debug traces during failures to confirm DFE/adaptation values, RX IQ/FOM readbacks, RCAL status, DCC code banks, signal-detect output, MPLL power-control FSM status, PLL lock, SSC/fractional PLL values, charge-pump fields, bandgap controls, and clock/reset timing decode correctly.
- Where supported, run debug/manufacturing paths for ATB, analog test bus, signal-detect override, DCC bank access, manual RTUNE, prescaler override, and PLL override controls, then confirm normal link training resumes after overrides are released.

## Cross-Chunk Notes

The previous chunk covers earlier raw always-on lane 2 fields and ends immediately before the `RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS` group. This chunk completes the lane 2 tail, covers lane 3, lane-X, and a broad CR0 supervisor digital/analog/MPLL section. The next chunk should finish `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0` masks and continue supervisor clock/reset and RTUNE configuration fields. The final per-file report should reconcile these boundaries before making whole-file claims about all DPCS 4.2.2 register groups.

### subset-b-002346: lines 21535-23895

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 21535-23895

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for `DPCSSYS_CR0` supervisor and lane-X display PHY register fields. It contains no executable C logic; its exported surface is a set of preprocessor constants describing bit positions (`__SHIFT`) and bit masks (`_MASK`) for 16-bit DPCS indirect hardware registers.

The requested range contains 2,361 lines, 2,139 `#define` entries, 1,080 shift definitions, 1,070 mask definitions, and 222 register comment headings. The line range starts inside `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`, where only the final two masks are in this chunk, and ends inside `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1`, where only the `master_atb_en` shift appears before the next chunk.

Although this repository path is under a local `ceph-client` mirror, the file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The header lets AMD display driver code refer to DPCS 4.2.2 register fields symbolically instead of hard-coding bit positions. Consumer code pairs these macros with addresses from `dpcs_4_2_2_offset.h` and the AMD DC register helper layer to compose, isolate, or update hardware register fields during link bring-up, link training, PHY power management, debug, and diagnostics.

This chunk covers the end of CR0 supervisor reference-clock power timing, supervisor RTUNE and analog/MPLL override fields, lane-X ASIC override/input/output transfer fields, lane TX and RX power/control/calibration/statistic fields, digital-to-analog override outputs, and the beginning of raw analog TX/RX register fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The important interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used to isolate or update that field.

Major macro families in this chunk include:

- `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_*`: supervisor reference-clock and reference-regulator timing/control fields, including `FAST_REF_WAIT` and `SUP_ANA_VPHUD_*`.
- `DPCSSYS_CR0_SUPX_DIG_RTUNE_*`: common RTUNE debug, enable, status, RX/TXDN/TXUP set values and readbacks, timing counters, and TX calibration code fields.
- `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLA_*`, `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_*`, `DPCSSYS_CR0_SUPX_DIG_ANA_RTUNE_OVRD_OUT`, `DPCSSYS_CR0_SUPX_DIG_ANA_BG_OVRD_OUT`, and `DPCSSYS_CR0_SUPX_DIG_ANA_*PMIX_OVRD_OUT`: supervisor analog override/status fields for MPLLA/MPLLB clocks, outputs, charge-pump values, RTUNE, bandgap/reference regulation, async reset, and PMIX controls.
- `DPCSSYS_CR0_LANEX_DIG_ASIC_*`: lane-X ASIC-side override inputs/outputs and normal ASIC input/output mirrors for lane, TX, RX, RX EQ, and RX CDR/VCO signals. These fields describe request, pstate, rate, width, MPLL select, data enable, loopback, polarity, EQ coefficients, adaptation controls, signal-detect, calibration, and acknowledgement/status paths.
- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_*` and `DPCSSYS_CR0_LANEX_DIG_RX_PWRCTL_*`: lane TX/RX power-state encodings and power-up timing fields for P0, P0S, P1, P2, DCC, and RX power-up flows.
- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_DCC_*` and `DPCSSYS_CR0_LANEX_DIG_TX_CLK_ALIGN_*`: TX DCC CR-bank, DAC control/range/selection/ack/address, and TX clock alignment controls.
- `DPCSSYS_CR0_LANEX_DIG_TX_LBERT_*` and `DPCSSYS_CR0_LANEX_DIG_RX_LBERT_*`: TX/RX low-level BERT test controls and RX BERT error reporting.
- `DPCSSYS_CR0_LANEX_DIG_RX_VCOCAL_*`, `DPCSSYS_CR0_LANEX_DIG_RX_CDR_*`, and `DPCSSYS_CR0_LANEX_DIG_RX_DPLL_*`: RX VCO calibration controls/timers/status, CDR controls/status, DPLL frequency, and DPLL frequency bounds.
- `DPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset/status, DFE tap statuses, even/odd VDAC offsets, slicer controls, error levels, DAC control selection, and CR-bank address/data access.
- `DPCSSYS_CR0_LANEX_DIG_RX_STAT_*`: RX statistic loading, masks, match controls, statistic source controls, sample counts, statistic counters, calibration-comparison clock control, extended match controls, and statistic stop controls.
- `DPCSSYS_CR0_LANEX_DIG_MPHY_RX_*`: MPHY RX PWM, low-speed termination, and analog PWM clock-stable counter fields.
- `DPCSSYS_CR0_LANEX_DIG_ANA_*`: digital override outputs and status fields bridging lane digital control into analog TX/RX, including TX power/clock/reset/data, TX termination and EQ, RX control/power/VCO/calibration/DAC/slicer/scope, signal-detect, term-code clocks, MPHY, and DCC DAC override fields.
- `DPCSSYS_CR0_LANEX_ANA_TX_*` and `DPCSSYS_CR0_LANEX_ANA_RX_*`: raw analog TX/RX fields for measurement override, TX power, alternate/test bus, ATB controls, DCC DAC/control, termination, override clocks, TX miscellaneous controls, RX clocks, CDR/deserializer, slicer, RX power, squelch, calibration, and ATB/reference measurement controls.

## Control Flow

This header has no software control flow. It participates in compile-time construction of register/shift/mask tables:

1. AMD DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`.
2. Driver table macros token-paste register and field names from the offset and shift/mask headers into version-specific hardware access tables.
3. Runtime display code uses AMD DC register helpers to read, write, update, or decode the underlying DPCS registers.
4. Actual sequencing for RTUNE, MPLL overrides, TX/RX power transitions, DCC calibration, VCO/CDR setup, RX adaptation, RX statistics, LBERT, analog overrides, and test-bus control lives outside this generated header and inside the display driver, firmware, or hardware state machines.

The macros only encode bit layout. They do not encode access type, reset values, polling order, write-one-to-clear behavior, self-clearing behavior, clock-domain validity, power-domain constraints, or reserved-bit policy.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR0 DPCS supervisor and lane-X registers:

- Supervisor/common state includes RTUNE debug/manual values, RTUNE enable/status, RX/TX termination calibration set values and readbacks, RTUNE timing counters, TX calibration code, MPLLA/MPLLB output enable/reset/calibration/standby/clock-select override values, RTUNE analog override, bandgap/reference-regulator controls, analog status, async reset, and PMIX controls.
- Lane ASIC transfer state includes override values and enables for lane TX/RX requests, pstate, rate, width, MPLL selection, data enable, loopback, async drive, polarity, TX pre/main/post cursor values, RX adaptation requests, RX EQ controls, signal-detect thresholds, RX VCO/reference loads, phase calibration, termination, and lane outputs/acknowledgements.
- TX state includes lane P-state bitfields, TX power-up timings, DCC CR-bank address/data, DCC DAC programming, DAC ACK/address fields, TX clock alignment, and TX LBERT test controls.
- RX state includes RX P-state and power-up timing, VCO calibration control/timer/status, XAUI alignment mask, RX LBERT control/error status, CDR control/status, DPLL frequency/bounds, adaptation configuration/status, DFE tap readbacks, slicer and error offsets, adaptation reset, RX statistic capture controls and counters, and MPHY low-speed controls.
- Digital analog override state includes TX/RX analog enable, clock, reset, power, termination, EQ, VCO, DAC, calibration, slicer, signal-detect, MPHY, DCC, and status/readback fields.
- Raw analog state includes TX/RX power and clock override latches, measurement/test-bus selections, ATB selectors, DCC/termination controls, TX slew/peaking/vreg/inversion controls, RX CDR/deserializer/slicer/AFE/DFE/deserializer/loopback/fast-start/squelch/calibration/reference controls, and the first RX ATB measurement bit at the chunk boundary.

Persistence is hardware-defined. Configuration fields usually remain until link reprogramming, modeset, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, calibration, statistic, BERT, and handshake fields may be sampled, latched, self-clearing, clear-on-write, or valid only while relevant DPCS clocks and power domains are active. This generated header does not define those runtime semantics.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` offsets. Example anchors for this chunk include `ixDPCSSYS_CR0_SUPX_DIG_RTUNE_CONFIG` at `0x8081`, `ixDPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P0` at `0x9020`, `ixDPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0` at `0x9060`, and `ixDPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` at `0x90fa`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`, tying this register contract to DCN 3.1.5 display resource setup.
- Higher-level display integration points include link encoder and PHY programming, DisplayPort/HDMI link training, lane power-state transitions, PLL/MPLL control, RX adaptation and CDR/VCO calibration, DCC and RTUNE calibration, hotplug/modeset/suspend/resume flows, manufacturing ATE/LBERT paths, OCLA/statistic/debug readback, and low-level interrupt or status polling paths that decode these fields through generated tables.

## Risks And Edge Cases

- These are untyped preprocessor constants. An incorrect mask or shift can compile cleanly while updating the wrong hardware field, corrupting reserved bits, or decoding a status bit incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, firmware expectations, silicon documentation, and the companion offset header.
- The range starts and ends inside logical registers. `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0` has its heading, shifts, and first mask before this chunk; `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` continues in the next chunk. Merge/reconciliation must not treat either register as fully documented by this chunk alone.
- Many fields pair an override value with an override-enable bit. Writing the value without enabling it may do nothing; leaving an enable asserted after test/debug use can force hardware away from normal state-machine control.
- Supervisor RTUNE, MPLLA/MPLLB, bandgap/reference, and PMIX fields can affect clocks, termination, and analog supplies. Bad masks here can cause PLL instability, black screens, link training failures, or power-management regressions.
- TX/RX power, request, reset, pstate, rate, width, MPLL-select, data-enable, and ACK fields are sequencing-sensitive. Misprogramming them can leave a lane stuck in reset, powered down, unclocked, or out of sync with the display controller.
- RX adaptation, DFE, slicer, CDR, VCO, DPLL, statistic, and calibration fields are easy to misread because status, configuration, reset, and CR-bank access fields are densely packed and similarly named.
- DCC, termination-code, TX EQ, peaking, slew, vreg, and analog test-bus fields affect electrical behavior. Wrong values may produce mode-specific failures or compliance problems rather than immediate software faults.
- BERT, ATE, OCLA, ATB, and raw analog override fields are intended for validation/debug/manufacturing-style flows. Using them in normal paths can perturb link training and power management.
- Reserved and `NC` masks cover large bit ranges. Consumers should preserve these bits through read-modify-write operations unless the hardware specification says otherwise.

## Test Signals

Useful validation is mainly generated-header, build, and hardware-integration oriented:

- Build AMDGPU display support for DCN 3.1.5 so `dcn315_resource.c` preprocesses the DPCS 4.2.2 offset and mask headers. Missing or renamed macros should fail during table initialization.
- Mechanically verify each complete register group in this range has matching `__SHIFT` and `_MASK` pairs, allowing the known boundary exceptions at `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0` and `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1`.
- Cross-check register-family names in this chunk against `dpcs_4_2_2_offset.h` so every complete group has a matching `ixDPCSSYS_CR0_*` address.
- Diff against AMD's generated source data and nearby DPCS versions such as `dpcs_4_2_0_sh_mask.h` where compatible layouts are expected, watching for accidental field-width, shift, or mask drift.
- Runtime display tests on DPCS 4.2.2 hardware should cover DP/HDMI link bring-up, lane-count/rate changes, pstate transitions, hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset.
- Link-training and PHY debug traces should show expected transitions for RTUNE calibration, MPLLA/MPLLB enable/lock-related control, TX/RX request and ACK fields, DCC calibration, RX VCO/CDR/DPLL state, RX adaptation done/status fields, signal-detect, and statistic counters.
- Diagnostic validation should exercise LBERT, OCLA/statistic capture, ATB/test-bus selection, analog override readbacks, DCC DAC controls, termination-code controls, and RX/TX loopback or ATE paths where available.

## Chunk Notes For Merge

This document intentionally covers only lines 21535-23895 of `dpcs_4_2_2_sh_mask.h`. The previous chunk owns most of `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`; this chunk begins with its final two masks. The next chunk owns the rest of `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` and subsequent raw analog/raw lane register groups. The final per-file report should describe the whole file as generated ASIC bitfield metadata for DPCS 4.2.2, with `dcn315_resource.c` and `dpcs_4_2_2_offset.h` as primary in-tree integration anchors.

### subset-b-002347: lines 23896-26285

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 23896-26285

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It contains C preprocessor constants for DPCS register bitfields, not executable driver logic. The constants are consumed by AMDGPU display code so higher-level register helpers can set, clear, update, and decode fields without hard-coding bit positions.

The requested range contains 2,390 source lines with 1,065 `__SHIFT` macros, 1,077 `_MASK` macros, and 266 register/comment boundary lines. It starts inside `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1`, covers CR0 lane-X analog RX measurement and raw lane PCS/FSM/IRQ/PMA/TX/RX/ATE control fields, then crosses into the `dpcssys_cr1_rdpcstxcrind` address block for CR1 support digital/analog, MPLLA/MPLLB, clock/reset, spread-spectrum, and rtune fields. The last line is the comment for `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`; that register's field definitions continue in the next chunk.

Although the path is under a local `ceph-client` source mirror, this file belongs to AMDGPU display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, memory allocations, locks, or direct MMIO operations in this range. The public surface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index of a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask of that field within the register value.

The main macro families in this chunk are:

- `DPCSSYS_CR0_LANEX_ANA_RX_ATB_*` and nearby analog RX definitions: analog test bus and RX measurement selection fields such as ATB master enable, voltage/regulator measurement selects, CDR VCO measurement, calibration VREF, ATB force values, and reserved/NC fields.
- `DPCSSYS_CR0_RAWMEM_DIG_ROM/RAM_*`: raw memory data windows for common ROM/RAM fields, represented as 16-bit `DATA` masks.
- `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_*`: PCS transfer controls for TX and RX. These include TX/RX pstate, low-power detect, width, rate, MPLL selection/enables, master MPLL override, async enable/data overrides, reset/request/detect-RX handshakes, TX/RX data-enable overrides, loopback controls, RX equalization/CTLE/DFE-related overrides, PH2 calibration, lane number, and ATE/test override forms of many of the same controls.
- `DPCSSYS_CR0_RAWLANEX_DIG_FSM_*`: micro-FSM override, monitor, status, fast-path calibration/adaptation flags, common calibration status, DCC flags/status, OCLA enable, TX EQ update flags, register/memory lock bits, and RX IQ phase offset fields.
- `DPCSSYS_CR0_RAWLANEX_DIG_IRQ_CTL_*`: RX/TX reset/request/rate/pstate/adaptation/PH2/loopback/DCC interrupt status, clear, and mask fields.
- `DPCSSYS_CR0_RAWLANEX_DIG_PMA_XF_*`: PMA transfer override and readback fields for lane/supply/TX/RX, including TX/RX request/ack, reset/data enable, PMA ack, retune request/ack, async/PWM controls, RX termination, and MPHY override controls.
- `DPCSSYS_CR0_RAWLANEX_DIG_TX_CTL_*` and `DPCSSYS_CR0_RAWLANEX_DIG_RX_CTL_*`: TX/RX lane control fields for FSM behavior, TX clock selection and DCC status, RX LOS masking, data-enable override counters, continuous off-cancel/adaptation status, and UPCS/OCLA observation gates.
- `DPCSSYS_CR1_SUP_DIG_*`: support-digital CR1 controls for IDCODE low/high data, reference clock overrides, MPLLA/MPLLB divider and HDMI clock overrides, PLL override controls, SSC peak/stepsize/fract-N values, charge pump controls, supply/prescaler/lane-level overrides, ASIC input mirrors, and debug fields.
- `DPCSSYS_CR1_SUP_ANA_*`: support-analog CR1 fields for prescaler, rtune, bandgap, analog switch/power measurement, MPLLA/MPLLB miscellaneous controls, analog PLL override bits, ATB measurement, PLL control registers, reserved analog controls, and duplicated A/B PLL control banks.
- `DPCSSYS_CR1_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR1_SUP_DIG_MPLLB_MPLL_PWR_CTL_*`: MPLL power-control override/status/timing/calibration/DAC fields for both MPLL instances.
- `DPCSSYS_CR1_SUP_DIG_CLK_RST_*` and `DPCSSYS_CR1_SUP_DIG_RTUNE_*`: bandgap/reference clock startup timing, VPHUD reference enable/select, rtune manual/debug/config/status/set/stat fields, and rtune timing counters.
- `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_*`: readback/output fields for MPLLA word/HDMI/div/output clocks, analog enable/reset/calibration, gearshift, standby, and analog integer output. The range ends just as `OVRD_OUT_2` begins.

Several field names carry hardware sequencing semantics even though this header only records bit layout: `*_OVRD_EN`, `*_OVRD_VAL`, `*_REQ`, `*_ACK`, `*_DONE`, `*_IRQ`, `*_IRQ_CLR`, `*_MSK`, `*_FAST_*`, `*_CAL`, `*_STAT`, and `*_LOCK`.

## Control Flow

This header has no runtime control flow. It participates in AMDGPU display code through compile-time table construction:

1. The matching DPCS 4.2.2 offset header supplies register addresses or indirect register indexes.
2. This shift/mask header supplies field positions for those registers.
3. AMDGPU display resource, link-encoder, PHY, and register helper code combines offsets with shift/mask macros through generated field-list macros and token-pasting helpers.
4. Runtime helpers such as register read/modify/write paths use the resulting tables to program or inspect DPCS hardware.

Any real sequencing, such as asserting resets, waiting for request/ack transitions, masking or clearing interrupts, forcing ATE overrides, changing PLL/divider settings, triggering calibration, or polling rtune/MPLL status, lives in display driver code, firmware, and hardware state machines outside this generated header.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It identifies hardware-visible state and control fields:

- CR0 lane-X analog and raw lane state: RX ATB/measurement controls, TX/RX PCS override inputs and outputs, RX equalization and phase calibration values, PH2 calibration request/ack bits, FSM status/monitor/debug flags, interrupt state/clear/mask bits, PMA transfer handshakes, TX/RX lane controls, and ATE override fields.
- CR1 support-digital and support-analog state: reference clock and bandgap controls, MPLLA/MPLLB enable/divider/HDMI/SSC/fract-N/charge-pump controls, ASIC input mirrors, analog ATB and PLL control registers, MPLL power-control override/status/timers/calibration/DAC fields, clock/reset startup timers, and rtune controls/status.

Persistence is hardware-defined. Control fields may remain programmed until a modeset path, link reconfiguration, suspend/resume, GPU reset, ASIC reset, or power-gating transition rewrites them. Status, ack, calibration, IRQ, and readback fields may be read-only, latched, write-one-to-clear, self-clearing, or valid only while the relevant DPCS block is powered and clocked. This file does not encode access direction, reset values, volatility, or legal programming sequences.

## Dependencies And Integration Points

This generated header must stay synchronized with its ASIC register database and with the matching DPCS 4.2.2 offset definitions. Shift/mask consumers generally assume that every register field in the shift/mask header has a compatible register offset in the companion offset header and that field names match the token-pasted names used by AMD display register lists.

Integration points include:

- Companion AMD DPCS 4.2.2 generated headers under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`, especially the matching offset header and adjacent chunks of this `dpcs_4_2_2_sh_mask.h` file.
- AMDGPU Display Core resource and link-encoder code that builds register access tables from ASIC-specific offset and mask/shift headers.
- DPCS/RDPCS register access helpers that use these constants for PHY/link bring-up, DisplayPort/HDMI lane control, link training, clock/PLL programming, signal detect, calibration, interrupt handling, and debug/test override flows.
- Firmware or hardware microcontroller interfaces that rely on matching interpretations of MPLL, rtune, FSM, calibration, and ATE fields.

The chunk crosses from the CR0 raw lane-X block to the CR1 support block at line 25043. That boundary matters for the merge lane: CR0 lane-X fields describe one lane/control context, while CR1 support fields describe another DPCS instance/address block with its own reference clock, MPLL, analog, and rtune controls.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly and only fail as a hardware programming bug.
- The file is generated. Manual edits risk divergence from AMD's register source, companion offset headers, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first lines continue `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` from the previous chunk, and the final line only introduces `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`.
- Many fields are paired `*_OVRD_VAL` and `*_OVRD_EN` controls. Mixing the value and enable masks can force clocks, resets, data enables, PLL selection, loopback, RX termination, or analog controls away from hardware/firmware ownership.
- Request/ack, done, IRQ, clear, and status fields are sequencing-sensitive. Incorrect definitions can cause false readiness, missed interrupts, uncleared latched events, link training timeouts, or hangs in PHY bring-up/teardown.
- Analog and clocking fields such as MPLLA/MPLLB dividers, SSC peak/stepsize, fract-N quotient/remainder/denominator, charge pump values, bandgap startup timers, VPHUD, rtune, CTLE/DFE/VGA/ATT/phase, and DCC values may only fail at specific link rates, board designs, cable/sink combinations, or voltage/temperature corners.
- Reserved and `NC` masks appear throughout the chunk. Driver code should not repurpose them unless the authoritative programming guide explicitly says so.
- Similar MPLLA/MPLLB and CR0/CR1 field names are easy to confuse. Token-pasted users must include the ASIC-specific header and register-list variant that matches the hardware generation.
- Some field names use `DATA` while others use `data`, and generated spelling/case is part of the API. Renaming for style would break consumers.

## Test Signals

Useful validation should combine generated-header consistency checks with hardware-oriented display testing:

- Build AMDGPU display configurations that include DPCS 4.2.2 support. Missing, renamed, or misspelled macros should surface in resource/link-encoder register table compilation.
- Mechanically compare this range against the authoritative DPCS 4.2.2 register database and ensure each complete field has a consistent `__SHIFT`/`_MASK` pair; account for the split first and last registers.
- Cross-check every complete register group in this chunk against the matching DPCS 4.2.2 offset header so register names in shift/mask macros have corresponding offsets.
- Run structural diff checks across repeated MPLLA/MPLLB groups and repeated override/status families to catch accidental generator drift while allowing intentional A/B PLL differences.
- Exercise DisplayPort/HDMI link bring-up, link-rate changes, hotplug, modeset, blank/unblank, suspend/resume, and GPU reset on hardware using this DPCS generation.
- Watch runtime logs and register dumps for request/ack timeouts, stuck reset/data-enable overrides, IRQs that fail to clear, missed RX/TX request events, RX adaptation failures, signal-detect instability, rtune failures, and MPLL lock/power-control anomalies.
- Validate ATE/test/debug override paths only in controlled diagnostics, since forcing override bits can bypass normal PHY control.
- Compare dumps decoded with these masks against hardware documentation or known-good tools for PLL dividers, SSC/fract-N values, rtune status, bandgap/reference startup timing, TX/RX lane controls, PH2 calibration, DCC calibration, and analog ATB/measurement fields.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1`, including at least the register comment and first field(s) before line 23896. This chunk then covers CR0 lane-X analog/RX, raw memory, PCS transfer, FSM, IRQ, PMA, TX/RX control, and ATE definitions through `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN_2`, followed by the start of the CR1 support block. The next chunk should complete `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2` and continue the remaining CR1 support output/readback definitions. The final merged per-file report should reconcile these split register groups before making whole-file coverage claims.

### subset-b-002348: lines 26286-28636

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 26286-28636

## Scope

This chunk covers lines 26286-28636 of the generated AMD DPCS 4.2.2 shift/mask header. The range contains 2,142 preprocessor definitions: 1,076 `__SHIFT` definitions and 1,066 `_MASK` definitions when counted by suffix-style macro names. It spans 209 comment-delimited register block starts plus one carried-in block at the beginning, because line 26286 starts inside `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`. It also ends inside `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1`; the remaining shift definitions and all masks for that register continue after the requested range.

The content is declarative register metadata only. It defines bit positions and masks for DPCS CR1 supervisor analog controls, CR1 lane 0 TX/debug/statistics/analog TX controls, and the first half of CR1 lane 1 TX/RX controls. It contains no C functions, structs, enums, local storage, runtime branching, allocation, locking, or software-owned persistence.

## Purpose

This header fragment provides symbolic bitfield definitions for AMDGPU display code that programs and inspects the DPCS 4.2.2 display PHY. Consumer code pairs these field macros with companion register offsets from `dpcs_4_2_2_offset.h` and AMD display register helper macros to form read-modify-write values without embedding literal bit numbers.

The slice is centered on the CR1 DPCS PHY instance:

- Supervisor analog control and status for MPLLA/MPLLB, RTUNE, bandgap/reference regulator, and PMIX controls.
- Lane 0 ASIC-facing override and mirror registers, TX power-state programming, DCC controls, RX statistic counters, digital analog TX overrides, and direct analog TX controls.
- Lane 1 ASIC-facing override/mirror registers for both TX and RX, TX power controls, RX power/VCO/CDR/DPLL/adaptation controls, and the beginning of lane 1 RX statistic control.

## Exported API Surface

There are no callable APIs or user-defined types. The public interface is the macro namespace itself. Complete field groups generally provide:

- `REGISTER__FIELD__SHIFT`: the bit position used to place or extract the field value.
- `REGISTER__FIELD_MASK`: the bit mask for the same field in the corresponding DPCS register.

Important macro families in this chunk include:

- `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`, `DPCSSYS_CR1_SUP_DIG_ANA_MPLLB_OVRD_OUT_*`, `DPCSSYS_CR1_SUP_DIG_ANA_RTUNE_OVRD_OUT`, `DPCSSYS_CR1_SUP_DIG_ANA_STAT`, `DPCSSYS_CR1_SUP_DIG_ANA_BG_OVRD_OUT`, and `DPCSSYS_CR1_SUP_DIG_ANA_MPLL*_PMIX_OVRD_OUT`: CR1 supervisor analog PLL, RTUNE, bandgap, reference regulator, and PMIX override/status fields.
- `DPCSSYS_CR1_LANE0_DIG_ASIC_*`: lane 0 ASIC interface overrides and readbacks for lane loopback, TX request, P-state, rate, width, MPLLB select, data enable, main/pre/post cursor, HDMI mode, clock ready, invert, reset, detect-RX, async data, and low-power detect fields.
- `DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX P-state and power-up timing fields, DCC CR-bank address/data windows, DCC DAC control/range/selection/ack/address, TX clock alignment, and LBERT control.
- `DPCSSYS_CR1_LANE0_DIG_RX_STAT_*`: lane 0 RX statistic load value, data mask, pattern match controls, statistic control, counter enables, sample count, counters 0-6, calibration comparison clock control, extra match controls, statistic control extension, and statistic stop bits.
- `DPCSSYS_CR1_LANE0_DIG_ANA_*` and `DPCSSYS_CR1_LANE0_ANA_TX_*`: lane 0 digital-to-analog TX override fields, TX term-code and EQ override fields, analog status, TX DCC DAC override fields, and direct analog TX measurement/power/ATB/DCC/term/miscellaneous controls.
- `DPCSSYS_CR1_LANE1_DIG_ASIC_*`: lane 1 ASIC interface overrides and mirrors. Unlike the lane 0 portion in this chunk, lane 1 includes RX override and RX ASIC input groups for RX enable, termination enable, CDR freeze, adapt requests, rate, width, AFE/VGA/CTLE/DFE controls, calibration, CDR/VCO controls, inversion, squelch, and signal-detect selection.
- `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_*`: lane 1 TX P-state, power-up timing, DCC, clock alignment, and LBERT controls.
- `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_*`, `DPCSSYS_CR1_LANE1_DIG_RX_VCOCAL_*`, `DPCSSYS_CR1_LANE1_DIG_RX_CDR_*`, `DPCSSYS_CR1_LANE1_DIG_RX_DPLL_*`, and `DPCSSYS_CR1_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX power states, VCO calibration, receive alignment, LBERT, CDR/DPLL configuration and status, adaptation configuration/status, DFE offsets, slicer controls, adaptation reset, DAC control selection, and adaptation CR-bank address/data.
- `DPCSSYS_CR1_LANE1_DIG_RX_STAT_*`: the beginning of lane 1 RX statistic load/mask/match/control definitions, ending mid-register at `STAT_CLK_EN__SHIFT`.

## Register Areas Covered

The supervisor analog section defines CR1-wide mixed-signal controls. MPLLA and MPLLB override registers expose clock enables, output enables, analog enable, reset, calibration, divider clocks, feedback clock, gearshift, standby, integral/proportional charge-pump fields, and override selection. RTUNE and bandgap/reference regulator fields expose resistor tuning override, comparator reset, tuning mode/value, bandgap startup, async reset, reference regulator fast-start, and reference selection. These fields sit above individual lanes and can affect shared clocking or analog bias behavior.

The lane 0 ASIC interface groups describe the boundary between display/link logic and the lane 0 PHY. Override input fields can replace normal hardware signals for request, power state, link rate, width, MPLLB selection, data enable, main/pre/post cursor, HDMI mode, clock-ready, reset, invert, detect-RX, and async-data paths. Mirrored ASIC input/output groups expose the same style of signals without the override-enable bits, useful for observing the live hardware-facing state.

The lane 0 TX power-control and analog TX groups define the low-level transmitter behavior used during link bring-up, power transitions, and diagnostics. P-state registers cover analog reference generation, VCM hold, analog clocking, power-down, high-Z, termination enable, DCC enable, output enable, serializer enable, divider control, and low-power DCC values. DCC and DAC fields provide CR-bank address/data access, DAC range/selection/ack/address, and direct analog controls for TX measurement, power override, alternate bus, ATB routing, term code, override clocks, and miscellaneous TX settings.

The lane 0 and lane 1 RX statistic blocks expose programmable hardware measurement counters. They include data masks, pattern masks, pattern values, scope delay, statistic source selection, correlation/source shifts, RX clock selection, sample counter load/start, individual counter enables, pause/clock/data-delay controls, valid-loss clearing/control, counter readbacks, calibration comparison clock controls, additional pattern and saturation controls, and explicit statistic stop bits. These are bit contracts for diagnostics and calibration validation, not a software statistics implementation.

The lane 1 RX control section is broader than lane 0 in this chunk. It includes RX override fields for enable/termination/CDR/adaptation, AFE/VGA/CTLE/DFE programming, DFE data/error VDACs, slicers, CDR/VCO controls, calibration request and mode, inversion, common-mode mask, squelch, signal-detect select, and power sequencing. It also maps VCO calibration control/time/status, CDR control/status, DPLL frequency and bounds, adaptation state-machine configuration, adaptation resets, status readbacks for ATT/VGA/CTLE/DFE taps, and CR-bank address/data access.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior is created by driver code that includes these macros and writes or reads the mapped DPCS registers.

The field names imply several hardware state machines and handshakes:

- PLL and common analog control: MPLLA/MPLLB clock enable, output enable, reset, calibration, divider, standby, charge-pump, RTUNE, bandgap, and PMIX fields affect CR1 shared analog state. These controls can influence more than one lane when the lane consumes shared PLL or bias resources.
- Lane request and power sequencing: TX/RX `REQ`, `ACK`, `PSTATE`, power-up timing, reset, disable, high-Z, termination, serializer, output enable, CDR, and clock-ready fields model PHY bring-up, idle, rate changes, and power-down transitions.
- Override ownership: many fields pair a value bitfield with `*_OVRD_EN`, `*_OVRD_VAL`, or an `OVRD_SEL` field. Consumer code must explicitly decide when software takes control from normal ASIC or firmware-owned hardware paths and when it restores normal ownership.
- RX calibration and adaptation: VCO calibration request/mode/status, CDR controls, DPLL frequency bounds, adaptation `START_ASM1`, `ASM1_DONE`, ATT/VGA/CTLE/DFE status codes, VDAC offsets, slicer controls, and adaptation reset expose hardware calibration progress and results.
- Diagnostic measurement: LBERT, RX statistic matchers/counters, OCLA, ATB, DCC DAC, term-code, and analog status fields provide bring-up and validation hooks for link quality and analog behavior.

No software persistence is implemented in this header. Hardware register contents persist or reset according to ASIC power, reset, clock, and firmware ownership domains. Fields named `STATUS`, `STAT`, `ACK`, `DONE`, `RESULT`, `VALID`, `ERR`, `CNT`, and `CODE` are status or readback oriented by naming; fields named `OVRD`, `RESET`, `PSTATE`, `DAC`, `DCC`, `TERM`, `EN`, and `SEL` are control oriented. The macros do not enforce access direction or sequencing.

## Dependencies And Integration Points

The direct syntactic dependency is only the C preprocessor. The practical dependency is the matching DPCS 4.2.2 offset header, because these macros identify bitfields while `dpcs_4_2_2_offset.h` identifies register addresses such as CR1 supervisor analog registers at offsets `0x008c`-`0x0096`, lane 0 registers beginning at `0x1000`, and lane 1 registers beginning at `0x1100`.

AMDGPU DCN 3.1.5 display resource construction includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`. In `dcn315_resource.c`, DPCS base segments are defined, `DPCS_DCN31_REG_LIST(id)` contributes DPCS registers to link encoder register lists, and `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`/`DPCS_DCN31_MASK_SH_LIST(_MASK)` contribute these shift and mask values to the `dcn10_link_enc_shift` and `dcn10_link_enc_mask` tables. The macros in this chunk therefore integrate with the display link encoder, PHY programming, and link diagnostics paths for DCN 3.1.5-era hardware.

Other integration points visible from naming are DisplayPort/HDMI link training and mode set paths (`RATE`, `WIDTH`, `PSTATE`, `HDMIMODE`, cursor/pre/post EQ, data enable, DETRX, MPLL fields), suspend/resume and hotplug recovery paths (power states, reset, clock ready, signal detect), and hardware diagnostic paths (RX statistics, LBERT, CDR/DPLL/VCO/adaptation status, DCC/ATB/OCLA/RTUNE-style controls).

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently write or read an adjacent hardware bit during register helper operations, causing display link failures without compile-time errors.
- This chunk begins at line 26286 inside `DPCSSYS_CR1_SUP_DIG_ANA_MPLLA_OVRD_OUT_2`; the register comment is just before the chunk. It ends at line 28636 inside `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1`; later shifts and masks are outside this chunk. Per-chunk validators must account for these boundary effects.
- Field names can contain `MSK` or `MASK` as semantic field text, for example RX statistic data-mask fields. Counting masks by substring can overcount; generated-data checks should match the macro suffix pattern.
- Lane 0 and lane 1 blocks are structurally similar but not identical. Lane prefix, RX/TX direction, field width, or mask-copy mistakes can affect one lane while nearby lanes still work.
- Override-enable fields are adjacent to value fields. Accidentally enabling an override can seize normal hardware control; failing to enable one can make a programmed value ineffective.
- Supervisor analog and PLL fields can have shared-resource effects. MPLL, RTUNE, bandgap/reference regulator, PMIX, reset, and calibration writes can destabilize multiple lanes if ownership and sequencing are wrong.
- Reserved fields are explicitly mapped. Consumer code should preserve reserved bits during read-modify-write unless the hardware specification requires a defined write value.
- Status/readback and writable controls are intermixed in one generated namespace. Consumers cannot infer safe writeability from the existence of a mask macro alone.

## Test Signals

Useful validation is mostly build-time, generated-data, and hardware-integration oriented:

- Preprocess or compile AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`, especially the DCN 3.1.5 resource path that builds DPCS link encoder register, shift, and mask tables.
- Validate this chunk against the authoritative DPCS 4.2.2 register database and `dpcs_4_2_2_offset.h`, accounting for the partial first and last register groups.
- Check that complete register groups in the range have matching shift and mask definitions for each field, while `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1` is intentionally incomplete in this chunk.
- Compare repeated CR1 lane 0/lane 1 families and neighboring generated variants such as `dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_3_sh_mask.h`, and `dcn_4_1_0_sh_mask.h` where the hardware database expects stable layouts.
- Runtime display tests on DPCS 4.2.2/DCN 3.1.5 hardware: DisplayPort and HDMI link training, rate/width changes, hotplug, suspend/resume, lane power transitions, and multi-lane operation that exercises CR1 lane 0 and lane 1 separately.
- PHY diagnostic tests that read back TX ACK/clock-ready, RX adaptation done/status codes, VCO/CDR/DPLL status, DFE tap values, RX statistic counters, LBERT error paths, analog status, DCC DAC ack, and signal-detect/detect-RX results.
- Recovery tests around override fields: enable overrides only in controlled debug or bring-up paths, restore normal ASIC ownership, and confirm stale overrides do not survive link reconfiguration or power transitions.

## Chunk Notes For Merge

This document intentionally covers only lines 26286-28636 of `dpcs_4_2_2_sh_mask.h`. The later per-file merge should describe the full header as a generated DPCS 4.2.2 register bitfield map used by AMDGPU display code, not handwritten driver logic. Adjacent chunks are needed for the preceding MPLLA override fields and the remaining lane 1 RX statistic definitions after `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1__STAT_CLK_EN__SHIFT`.

### subset-b-002349: lines 28637-30999

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 28637-30999

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for CR1 lane register fields. It contains only preprocessor constants: `__SHIFT` macros define bit positions and `_MASK` macros define field masks for DPCS hardware registers. The range has 2,135 `#define` entries across 228 register-comment groups: 1,071 shift constants and 1,073 mask constants. It starts in the middle of `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1`, covers the remainder of CR1 lane 1 RX statistic and analog TX/RX-related fields, then covers a broad CR1 lane 2 region from ASIC-facing controls through TX/RX power, calibration, CDR/DPLL, adaptation, statistics, MPHY, and the beginning of TX analog equalization override fields. It ends inside `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3`.

Although this file is located under a `ceph-client` source mirror, this chunk is AMDGPU display PHY register metadata. It has no Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header slice is to give AMDGPU display code a generated bitfield contract for DPCS 4.2.2 CR1 lane registers. Callers combine these constants with addresses from the matching `dpcs_4_2_2_offset.h` header and the AMD display register helper macros to read, update, and write DPCS registers without hard-coding numeric bit positions in driver logic.

The covered fields describe:

- CR1 lane 1 RX statistic controls, sample counters, statistic counters, pattern/mask continuation fields, statistic-stop behavior, MPHY low-speed controls, RX termination timing, and PWM clock-stability control.
- CR1 lane 1 digital analog TX/RX override outputs for TX clocks, refgen, VCM hold, reset, serial/data enable, data rate, div4/RX detect, termination code, driver source, equalization taps, RX power, RX VCO/CDR controls, RX calibration, AFE/VGA/CTLE/scope/slicer/IQ controls, signal detect, DCC DAC, and analog TX measurement/power/miscellaneous registers.
- CR1 lane 2 ASIC-facing lane/TX/RX override inputs and outputs, including request/ack handshakes, pstate/rate/width, data enable, reset, loopback, CDR/adaptation controls, equalization inputs, RX CDR/VCO values, cross-lane clock/shift controls, and OCLA enables.
- CR1 lane 2 TX power-control state fields for P0, P0S, P1, and P2, TX power-up timing fields, DCC CR-bank/DAC access, TX clock alignment, and TX LBERT controls.
- CR1 lane 2 RX power-control state fields, RX power-up timing, RX VCO calibration controls/status, RX alignment and LBERT status, CDR/DPLL configuration/status, RX adaptation configuration/status, DAC/slicer offsets, RX statistic counters, MPHY controls, and the start of lane 2 TX analog override/equalization fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocations, or direct MMIO operations in this range. The exported interface is the generated macro namespace:

- `DPCSSYS_CR1_LANE*_...__FIELD__SHIFT`: least-significant bit index for `FIELD`.
- `DPCSSYS_CR1_LANE*_...__FIELD_MASK`: bit mask for the same field.
- Register delimiter comments such as `//DPCSSYS_CR1_LANE2_DIG_RX_CDR_CDR_CTL_0`: field-group markers corresponding to register address names in the companion offset header.

Notable lane 1 macro groups:

- `DPCSSYS_CR1_LANE1_DIG_RX_STAT_*`: statistic counter enables, sample-count done bits, statistic counter values, comparator clock control, CR1A/CR1B pattern and mask fields, delayed-data/scope/sample-count controls, and statistic stop.
- `DPCSSYS_CR1_LANE1_DIG_MPHY_*`: RX PWM polarity/data polarity, low-speed termination count, and analog PWM clock stable count.
- `DPCSSYS_CR1_LANE1_DIG_ANA_TX_*`: TX analog override control for clock/data/refgen/VCM/reset/serial/rate, termination-code and driver-source override, termination clocking, EQ override pull-enable/pull-direction/pre/post controls, DCC DAC override controls, fast-start/loopback fields, and TX override outputs.
- `DPCSSYS_CR1_LANE1_DIG_ANA_RX_*`: RX data-rate/word-clock/div4/DFE/adaptation overrides, RX power enables, RX CDR/VCO frequency tune controls, RX calibration DAC and AFE update clocks, AFE ATT/VGA/CTLE, scope/slicer/IQ controls, RX termination override, MPHY squelch/PWM controls, signal-detect overrides, and analog status readbacks.
- `DPCSSYS_CR1_LANE1_ANA_TX_*` and `DPCSSYS_CR1_LANE1_ANA_RX_*`: raw analog-side register layouts for TX measurement, power override, alternate bus/ATB selection, TX DCC/termination/misc fields, RX clock/CDR/slicer/power/squelch/calibration/ATB fields, and reserved analog register fields.

Notable lane 2 macro groups:

- `DPCSSYS_CR1_LANE2_DIG_ASIC_*`: lane loopback and AC JTAG controls; TX/RX override inputs for request, pstate, rate, width, data enable, reset, polarity, low-power detect, HDMI mode, clock readiness, DCC/termination/PWM controls; TX/RX ack/status outputs; RX EQ and CDR/VCO input fields; cross-lane repeater/clock/shift/master controls; and OCLA clock/data enables.
- `DPCSSYS_CR1_LANE2_DIG_TX_PWRCTL_*`: per-power-state TX enables for refgen, VCM hold, analog/digital clocks, reset, serial, data, RX-detect, VBOOST, and DCC compensation; TX startup timing fields; DCC bank address/data/control/range/selection/ack/address; TX clock alignment; and TX LBERT mode/error injection controls.
- `DPCSSYS_CR1_LANE2_DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, and `DIG_RX_DPLL_*`: RX AFE/clock/CDR/deserializer/adaptation power controls, RX P-state control, RX power-up timing, VCO calibration mode/timing/status, XAUI comma mask, RX LBERT error count, CDR tracking/SSC/PI/slicer controls, CDR status, and DPLL frequency bounds.
- `DPCSSYS_CR1_LANE2_DIG_RX_ADPTCTL_*`: adaptation configuration words, reset control, ATT/VGA/CTLE/DFE tap status, even/odd VDAC offsets, slicer levels, DAC-control selection, and adaptation CR-bank address/data fields.
- `DPCSSYS_CR1_LANE2_DIG_RX_STAT_*` and `DIG_MPHY_*`: load-value/data-mask/pattern-match registers, statistic counter control and stop, sample/count done fields, PWM polarity, termination low-speed count, and PWM clock stability.
- `DPCSSYS_CR1_LANE2_DIG_ANA_TX_*`: beginning of lane 2 TX analog override controls, including TX clock/data/refgen/VCM/reset/serial/rate, termination-code override, termination clock, and the first EQ override registers for leg pull enable, EQ mux selection, pre-cursor, and the first post-cursor field.

## Control Flow

This generated header has no runtime control flow. It only supplies compile-time constants. The runtime flow belongs to AMD display code that:

1. Includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`.
2. Builds register offset/shift/mask tables through macros such as `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`/`DPCS_DCN31_MASK_SH_LIST(_MASK)`.
3. Uses register helper operations to clear masked fields, shift new values into position, and read or update hardware registers.

The implied hardware sequencing includes display link bring-up, lane power transitions, TX/RX request-acknowledge handshakes, TX DCC programming, RX VCO/CDR/DPLL setup, RX adaptation, statistic sampling, MPHY low-speed behavior, analog override/debug programming, and LBERT/OCLA diagnostics. This header does not enforce ordering, polling, timeouts, or access direction.

## State And Persistence Behavior

The macros themselves are stateless and persistent only as compile-time constants. The state they describe lives in volatile DPCS hardware registers. Register values may be modified by normal link training, modesets, hotplug handling, runtime PHY retuning, diagnostic paths, suspend/resume, power gating, GPU reset, or firmware/hardware state machines.

Several field families describe stateful hardware behavior:

- Request/ack, valid, done, calibration, and error fields reflect transient hardware handshakes and status.
- P-state, reset, clock-enable, serial-enable, data-enable, adaptation-enable, and override-enable fields influence lane operation until rewritten or reset by hardware.
- DCC, VCO, CDR, DPLL, CTLE, VGA, ATT, DFE, slicer, IQ phase, signal-detect, and termination fields encode analog tuning state that may be sensitive to lane rate, board, cable, sink, voltage, and temperature.
- Reserved masks represent hardware-owned or undocumented bits that consumers should preserve or avoid unless the authoritative programming guide says otherwise.

## Dependencies

This chunk depends on the DPCS 4.2.2 register-generation source staying synchronized with the target ASIC. The most important paired file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which supplies the matching `ixDPCSSYS_CR1_LANE*...` register addresses. A mask/shift macro from this file is meaningful only when paired with the corresponding DPCS 4.2.2 offset macro.

The concrete in-tree consumer for this generated header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`. That resource file builds DCN 3.1.5 link encoder register tables with `DPCS_DCN31_REG_LIST(id)` and appends `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` to the link encoder shift/mask structures.

Related integration patterns live in AMD display DIO/HPO link encoder headers, especially the DCN31 DPCS register-list and mask-list macros. Nearby generated DPCS versions such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` are useful for generator drift checks, but they are not interchangeable with this ASIC-specific 4.2.2 file.

## Integration Points

This chunk participates in AMDGPU display PHY programming for DCN 3.1.5 hardware using DPCS 4.2.2. The lane 1 portion is concentrated on late RX statistics and analog TX/RX controls. The lane 2 portion spans the main control surface for an entire CR1 lane: ASIC interface, TX/RX power sequencing, calibration, CDR/DPLL, receiver adaptation, statistics, low-speed MPHY behavior, and analog TX overrides.

These definitions feed register access helpers indirectly through generated tables. Consumers must maintain three alignments:

- ASIC-version alignment: use DPCS 4.2.2 offsets with DPCS 4.2.2 masks/shifts.
- Instance alignment: use `CR1` masks with `CR1` register addresses.
- Lane alignment: use `LANE1` and `LANE2` macros only with their matching lane addresses and physical lane programming paths.

## Risks And Edge Cases

- Chunk boundaries are not semantic. The first line is a continuation of `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1`, and the final lines stop before `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3` is complete.
- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly and only appear as hardware misprogramming at runtime.
- Manual edits to generated headers can diverge from AMD's register database, the companion offset header, firmware assumptions, and silicon documentation.
- Lane repetition is copy-sensitive. `LANE1` and `LANE2` fields often look structurally similar, but a wrong lane prefix can program the wrong physical lane or produce misleading register dumps.
- Request/ack, valid, done, calibration, and adaptation status fields are sequencing-sensitive. Incorrect masks can produce false readiness, timeouts, stuck training, or failure recovery loops.
- Override-enable fields can bypass normal hardware or firmware control. Leaving override bits asserted after diagnostics can break later link training, power management, hotplug, or suspend/resume.
- Analog tuning fields for DCC, CDR, DPLL, CTLE, VGA, ATT, DFE, slicer, termination, phase, and signal detect can fail only under specific rates, lane counts, sinks, boards, cables, or environmental corners.
- Reserved fields are widely present. Driver code should avoid writing reserved bits unless the programming guide explicitly requires it and should preserve them during read-modify-write sequences.
- Many registers are 16-bit shaped in this slice, but callers should still respect the generated mask rather than assuming a fixed register width across all DPCS generations.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`, especially `dcn315_resource.c` and DCN31 link encoder table initialization.
- Static generation checks that each complete field has matching `__SHIFT` and `_MASK` constants, that masks align with the shift and intended field width, and that the first and last split registers are reconciled with adjacent chunks.
- Cross-checks against `dpcs_4_2_2_offset.h` to ensure every register group in this range has a matching CR1 lane address macro.
- Repetition checks between CR1 lane 1 and lane 2 where the hardware model expects identical field layouts, while allowing intentional lane/position differences and chunk-boundary splits.
- Display bring-up, hotplug, modeset, blank/unblank, suspend/resume, and GPU reset recovery on hardware using DCN 3.1.5 / DPCS 4.2.2.
- Link-training stress across lane counts, rates, and protocols that exercise lane 2 TX/RX request/ack, pstate/rate/width, power sequencing, CDR/DPLL, adaptation, and signal-detect paths.
- PHY diagnostic coverage for RX/TX LBERT, OCLA, RX statistic counters, pattern match controls, DCC DAC selection/ack, VCO calibration status, CDR status, adaptation status, and analog override readback.
- Register dumps from failed link training decoded with these masks to confirm TX power state, RX power/adaptation, CDR/DPLL, DFE/CTLE/VGA/ATT, MPHY, signal-detect, and TX EQ fields match expected programming.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1` and earlier CR1 lane 1 RX statistic fields. This chunk completes much of CR1 lane 1's statistic and analog control surface, then covers most of CR1 lane 2 through the start of TX analog EQ override output 3. The next chunk should complete `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3` and continue the remaining CR1 lane 2 analog TX/RX definitions. The final per-file research document should reconcile these boundary splits before making whole-register or whole-file claims.

### subset-b-002350: lines 31000-33363

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 31000-33363

## Scope

This chunk covers line 31000 through line 33363 of the generated AMD DPCS 4.2.2 shift/mask header. It is a hardware register-field description block, not executable C. The visible slice contains about 2,140 `#define` entries: paired `__SHIFT` and `_MASK` constants for 16-bit DPCS/PHY control registers. The chunk begins in the middle of `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3` mask definitions and ends in the middle of `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN`, so the adjacent chunks are needed for complete boundary-register coverage.

## Purpose

The purpose of this chunk is to expose bit positions and bit masks for display PHY control/status fields under `DPCSSYS_CR1`. Driver code can combine these field constants with register addresses from the sibling `dpcs_4_2_2_offset.h` header and with AMDGPU/DC register helper macros to read, write, or update specific hardware fields without hard-coding bit arithmetic.

The represented hardware areas are:

- Lane 2 digital-to-analog and analog TX/RX controls, including RX CDR/VCO, calibration, AFE, scope, slicer, signal-detect, DCC DAC, TX power, TX ATB, TX termination, and RX analog power/control fields.
- Lane 3 ASIC-facing lane/TX/RX overrides and status, including request/pstate/rate/width, data enable, loopback, reset, RX detect, MPLL selection, cursor/pre/post equalization, voltage boost, async driver, and handshake acknowledgement fields.
- Lane 3 TX power-control sequencing, including P0/P0S/P1/P2 state enable bits, power-up timing fields, DCC calibration bank/data/DAC controls, TX clock alignment, loopback BERT, and RX statistic/correlation counters.
- Lane 3 digital analog output and analog TX fields, largely mirroring lane 2 TX analog override/measurement/register controls.
- Raw common `CR1_RAWCMN` controls for PHY reset, MPLLA/MPLLB clock/SSC/bandwidth overrides, common MPLL state, SRAM/OCLA/support analog override, firmware/id-code reads, RTUNE values, SRAM built-in logic control, power-gate override/status, supply override, VREF stats, and resistance/reference range controls.
- Raw lane 0 PCS transfer (`CR1_RAWLANE0_DIG_PCS_XF`) TX/RX override, PCS input/output, adaptation, equalization feedback, lane number, reserved registers, and ATE override fields.

## Important Macros And Register Families

The public surface is preprocessor symbols named:

`<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`

Each register family is preceded by a `//<REGISTER>` comment. Within this chunk, 224 complete register-comment blocks are visible plus one boundary register carried from the previous chunk, for 225 unique register names.

Important visible families include:

- `DPCSSYS_CR1_LANE2_DIG_ANA_RX_*`: RX control, power, VCO, calibration, DAC, AFE, scope, slicer, IQ phase/sense, status, term code, MPHY, signal detect, and TX DCC DAC overrides.
- `DPCSSYS_CR1_LANE2_ANA_TX_*` and `DPCSSYS_CR1_LANE2_ANA_RX_*`: lower-level analog TX/RX register fields such as ATB measurement, DCC, term code, clocks, miscellaneous TX settings, RX CDR/deserializer, slicer, power, SQ, calibration, and ATB measurement.
- `DPCSSYS_CR1_LANE3_DIG_ASIC_*`: ASIC-facing lane/TX/RX override and status fields. These provide override-enable/value pairs for request, pstate, rate, width, MPLL select, data enable, reset, RX detect, cursor values, async driver, vboost, HDMI mode, RX/TX loopback, and acknowledgements.
- `DPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_*`: lane 3 TX state-machine fields for P-state output enables and timing. P0/P0S/P1/P2 fields expose analog refgen, VCM hold, clock, reset, serial, data, RX detect, vboost, and DCC compensation controls.
- `DPCSSYS_CR1_LANE3_DIG_RX_STAT_*`: RX statistic/correlation load values, masks, pattern-match controls, statistic counter enables, sample count and count outputs, calibration comparator clock controls, and stop controls.
- `DPCSSYS_CR1_RAWCMN_DIG_*`: raw common controls shared under CR1, including common PHY reset, PLL clock/SSC overrides for MPLLA/MPLLB, lane FSM extension, common control overrides, MPLL state, ID/status, RTUNE values for RX/TXDN/TXUP lanes 0-7, SRAM boot logic, power gate overrides, supply/resistance/reference overrides, and VREF stats.
- `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_*`: raw lane 0 PCS exchange fields for TX and RX override inputs, PCS inputs, override outputs, PCS outputs, RX adaptation ack/FOM, RX feedback to TX pre/main/post direction, lane number, reserved storage, and the beginning of ATE override input.

## Control Flow And Usage Model

There is no runtime control flow in this header. The effective flow is compile-time expansion into MMIO field operations elsewhere:

1. A caller chooses a register address macro, typically `ix<REGISTER>` from `dpcs_4_2_2_offset.h`.
2. The caller chooses the field's `__SHIFT` and `_MASK` constants from this header.
3. AMDGPU/DC helper macros shift a value into place, mask it, and perform a register read/modify/write or field read.
4. Hardware implements the actual state transition, acknowledgement, counter update, or self-clearing behavior.

Several field names encode hardware protocols even though no C logic appears here. Examples include `*_OVRD_EN` fields that gate corresponding override values, `*_ACK` status bits for override/PCS handshakes, `*_SELF_CLEAR_DISABLE` fields that alter hardware pulse behavior, `*_START`/`*_STOP` controls for statistic collection, and `*_DONE` bits for sample/counter completion. Driver code using these fields must respect those hardware semantics outside this header.

## State And Persistence Behavior

This file stores no software state. State resides in hardware registers addressed by DPCS MMIO or indirect register access paths. The constants define how software maps logical fields to persistent or transient hardware bits.

State categories visible in this chunk include:

- Power and reset state: PHY functional reset, TX/RX pstate controls, refgen/clock/serial/data enables, reset override bits, power-gate stable/request/acknowledge fields, and SRAM boot-logic start/bypass fields.
- Clock and PLL state: MPLLA/MPLLB word dividers, TX clock divider, div8/div10 enables, bandwidth override, SSC range/clock/enable/fractional controls, MPLL state override, bank select, and force/off timings.
- Analog calibration state: RTUNE readback values for RX/TX up/down, DCC DAC controls and acknowledgements, term-code overrides, VCO/ref load values, calibration mux selection, AFE attenuation/gain/CTLE, slicer controls, and VREF statistics.
- Diagnostic state: ATB measurement controls, OCLA probe selection, RX statistic sample/count registers, LBERT mode/error pattern controls, firmware/id-code read fields, and adaptation FOM/ack values.

Because many fields are override enables or direct analog controls, incorrect writes can persist until reset or until firmware/hardware state machines regain control.

## Dependencies And Integration Points

This generated header depends on normal C preprocessor inclusion and its include guard `_dpcs_4_2_2_SH_MASK_HEADER`. It has no includes of its own and defines no functions, structs, enums, or storage.

Primary integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which contains the matching `ix...` register offsets for these register names. For example, this chunk's lane 3 and raw common fields line up with offsets such as `ixDPCSSYS_CR1_LANE3_DIG_ASIC_TX_OVRD_IN_0`, `ixDPCSSYS_CR1_RAWCMN_DIG_CMN_CTL`, and `ixDPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`.
- AMD display/DC and AMDGPU register helper code that consumes `*_MASK` and `*__SHIFT` constants through generated register-field lists or direct macro use.
- Neighbor ASIC register versions such as `dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_3_sh_mask.h`, and DCN/DPCS generated headers. Similar macro names appear there, so version-specific include selection is important.
- Hardware/firmware tables that determine when override fields are safe to touch. The header only describes layout; it does not enforce sequencing, locking, or ownership between driver, firmware, and PHY state machines.

## Risks

- Header/version mismatch is the largest risk. Pairing this 4.2.2 shift/mask header with a different offset header or ASIC register block can write valid-looking bits to the wrong hardware fields.
- The chunk contains many reserved and `NC` fields. Driver code should preserve reserved bits during read/modify/write unless the hardware programming guide explicitly requires otherwise.
- Override fields can bypass normal PHY control. Setting `*_OVRD_EN`, PLL override, reset override, pstate override, DCC/term override, or power-gate override bits without corresponding value/timing discipline can break link training, display output, or power sequencing.
- Timing fields such as TX VCM hold, vboost disable, reset, serial enable, and RX detect timing are encoded as raw bitfields. Off-by-one shifts or masks would not be caught by C type checking.
- Several fields indicate hardware pulses or self-clearing behavior. Treating them as ordinary persistent bits can cause missed updates or repeated actions.
- This slice starts and ends mid-register. Any automated analysis or regeneration that operates only on this chunk must not conclude that `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3` or `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` are complete in this report.

## Test Signals

Useful validation signals for this chunk are mostly static or hardware-integration oriented:

- Compile coverage: configurations that include DPCS 4.2.2 headers should compile without undefined field or offset macros when lane 2, lane 3, raw common, and raw lane 0 PCS fields are referenced.
- Generated-header consistency: every complete register comment in this slice should have paired `__SHIFT` and `_MASK` macros for each field, and every register should have a matching `ix<REGISTER>` offset in `dpcs_4_2_2_offset.h` unless it is a documented alias or generated exception.
- Bitfield sanity: masks should match shifts and widths, remain within the expected 16-bit register payloads in this DPCS block, and avoid overlap within each register except for intentional aliases.
- Cross-version diffing: compare against adjacent versions (`dpcs_4_2_0`, `dpcs_4_2_3`, DCN generated headers) to identify intentional 4.2.2 differences versus generator drift.
- Runtime/hardware smoke tests: display link bring-up, link training, PHY power transitions, hotplug/RX detect, and mode changes exercise many pstate, PLL, DCC, calibration, and override fields indirectly.
- Diagnostic validation: debug paths that read RX stat counters, firmware/id codes, RTUNE values, adaptation FOM/ack, and ATB/OCLA controls can reveal field-address or mask mismatches without intentionally disturbing normal display operation.

### subset-b-002351: lines 33364-35750

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 33364-35750

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic. Its exported surface is a large set of preprocessor constants that encode bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,105 `#define` entries across 2,387 lines. It is entirely within the `dpcssys_cr1_rdpcstxcrind` address block and covers CR1 raw-lane register fields. The chunk starts in the mask half of `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN`, then continues through the rest of raw lane 0 PCS/FSM/IRQ/PMA/TX/RX/ATE control fields, all corresponding raw lane 1 fields, and the beginning of raw lane 2 fields through the first masks of `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS`. The companion offset header maps these raw lane windows around `0x3000` for lane 0, `0x3100` for lane 1, and `0x3200` for lane 2.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main register-field families are:

- Lane 0 PCS tail: `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` masks for ATE overrides of RX/TX reset, RX/TX request, RX AFE/DFE adaptation enable, and RX/TX data enable. The shifts for this register begin before the chunk boundary.
- Lane 0 PCS equalization and termination: `RX_EQ_DELTA_IQ_OVRD_IN`, `TXRX_TERM_CTRL_OVRD_IN`, `TXRX_TERM_CTRL_IN`, `RX_OVRD_OUT_1`, `RX_EQ_OVRD_IN_1`, `RX_EQ_OVRD_IN_2`, and `RX_PH2_CAL` describe RX equalization delta/IQ overrides, RX/TX termination control overrides, RX clock enable output, AFE gain, attenuation level, DFE tap1, CTLE boost, and phase-2 calibration request/acknowledge bits.
- Lane 0 FSM controls and monitors: `FSM_OVRD_CTL`, `MEM_ADDR_MON`, `STATUS_MON`, `FAST_RX_*`, `FAST_SUP`, `FAST_TX_*`, `CMNCAL_*_STATUS`, `FAST_RX_CONT_*`, `FAST_FLAGS`, `CR_LOCK`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `OCLA`, `TX_EQ_UPDATE_FLAG`, and `RX_IQ_PHASE_OFFSET` expose state-machine override, command readiness, memory address monitor, fast calibration/adaptation enables, common MPLL/RCAL status, continuous-calibration controls, DCC and EQ update flags, OCLA selection, and RX IQ phase offset.
- Lane 0 IRQ controls: `RESET_RTN_REQ`, individual RX IRQ status registers, matching RX IRQ clear registers, `IRQ_MASK`, `IRQ_MASK_2`, lane transceiver-mode IRQs, PH2 calibration IRQs, serial loopback IRQs, DCC on-demand IRQ, and TX reset/request IRQ status and clear fields. These names repeat across status, clear, and mask registers but have different hardware semantics.
- Lane 0 PMA transfer fields: `PMA_XF_LANE_OVRD_IN/OUT`, `SUP_OVRD_IN`, `SUP_PMA_IN`, `TX_OVRD_OUT`, `TX_PMA_IN`, `RX_OVRD_OUT`, `RX_PMA_IN`, `LANE_RTUNE_CTL`, `SUP_PMA_IN_1`, `MPHY_OVRD_IN/OUT`, and `RX_ADAPT_OVRD_OUT` define lane/supervisor/PMA handshakes, TX and RX override outputs, lane RTUNE control, MPHY PWM/termination override paths, and RX adaptation override outputs.
- Lane 0 TX/RX control and late ATE fields: `TX_CTL_*`, `RX_CTL_*`, `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN_1`, `PCS_XF_MASTER_MPLL_LOOP`, `PCS_XF_ATE_RX_OVRD_IN_1/2/3`, `PCS_XF_RX_OVRD_OUT_2`, and `PCS_XF_TX_OVRD_IN_2` describe TX FSM/clock controls, TX DCC continuous status, OCLA probes, RX FSM controls, LOS mask timing, RX data-enable override timing, off-cancel/adaptation continuous status, manufacturing/test overrides, master MPLL loop selection, and additional RX/TX override outputs.
- Lane 1 complete raw-lane window: the chunk repeats the same CR1 raw-lane schema for `DPCSSYS_CR1_RAWLANE1_*`, starting at `PCS_XF_TX_OVRD_IN` and continuing through PCS TX/RX overrides, PCS inputs/outputs, RX adaptation ACK/FOM and directed TX coefficient feedback, lane number and reserved words, ATE overrides, EQ/termination/PH2 fields, FSM, IRQ, PMA, TX_CTL, RX_CTL, and late ATE registers.
- Lane 2 partial raw-lane window: the chunk begins `DPCSSYS_CR1_RAWLANE2_*` at `PCS_XF_TX_OVRD_IN` and continues through PCS TX/RX, RX adaptation, ATE, EQ/termination/PH2, and early FSM controls. It ends inside `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS`; the remaining masks and the lane 2 IRQ/PMA/TX_CTL/RX_CTL/ATE tail are in the next chunk.

Most field masks are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these raw-lane blocks. Several fields occupy full 16-bit words, while many control/status fields are single-bit enables, status bits, clear bits, or override-value/override-enable pairs.

## Control Flow

This header has no runtime control flow. It participates in compile-time register access setup:

1. AMD display code for the matching DPCS/DCN generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables use generated names from this header and companion `ixDPCSSYS_*` offsets.
3. Runtime driver code uses register helpers and those tables to read, write, set, clear, or update hardware fields during PHY bring-up, link training, modeset, diagnostics, interrupt handling, suspend/resume, and reset recovery.
4. Hardware and firmware state machines perform the actual lane sequencing; this header only names bit positions and masks.

The macros do not encode access type, reset value, polling order, write-one-to-clear behavior, self-clearing behavior, clock-domain restrictions, power-domain validity, or whether a field is read-only, write-only, or reserved.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR1 raw-lane registers:

- PCS state includes TX/RX reset and request overrides, pstate/rate/width/MPLL select paths, beacon/loopback/data-enable style controls, PCS input/output mirrors, RX adaptation request/disable/ACK/FOM, directed TX pre/main/post cursor feedback, lane number, ATE override bits, RX equalization overrides, termination controls, RX clock output, and PH2 calibration handshakes.
- FSM state includes manual FSM override controls, jump address and command start bits, state/status monitor bits, fast calibration/adaptation selectors, common MPLL/RCAL completion status, continuous calibration/adaptation selectors, CR lock, TX DCC flags and status, TX EQ update flags, OCLA selection, and RX IQ phase offset.
- IRQ state includes latched RX/TX reset and request events, RX rate and pstate events, RX adaptation request/disable events, lane transceiver-mode events, PH2 calibration events, serial loopback events, DCC on-demand events, clear registers, reset-return request bits, and mask registers.
- PMA transfer state includes lane and supervisor override inputs/outputs, TX/RX PMA handshakes, RTUNE control, MPHY override in/out fields, and RX adaptation override output.
- TX/RX local control state includes TX FSM and clock controls, TX DCC continuous status, RX FSM control, RX LOS masking, RX data-enable override timing, off-cancel/adaptation continuous status, and OCLA/UPCS OCLA probes.
- ATE and debug state includes manufacturing/test override values and enables for RX/TX controls, RX calibration and equalization fields, TX data and data-valid controls, master MPLL loop controls, and additional RX/TX override outputs.

Persistence is hardware-defined. Configuration and override fields generally last until another modeset/link-training sequence, PHY power transition, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, ACK, IRQ, calibration, clear, and handshake fields may be latched, sampled, write-one-to-clear, self-clearing, or valid only when the corresponding lane power and clocks are active. This generated header does not specify those behaviors.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching CR1 raw-lane offsets. In that file, the relevant address block is `dpcssys_cr1_rdpcstxcrind`.
- Lane 0 registers covered here map from `ixDPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` at `0x3018` through PCS EQ/termination/PH2, FSM at `0x3020` through `0x303f`, IRQ at `0x3040` through `0x305b`, PMA at `0x3060` through `0x306c`, TX_CTL at `0x3080` through `0x3084`, RX_CTL at `0x30a0` through `0x30a5`, and late ATE/PCS fields at `0x30c0` through `0x30c8`.
- Lane 1 uses the same layout offset by `0x100`, with PCS starting at `0x3100`, FSM at `0x3120`, IRQ at `0x3140`, PMA at `0x3160`, TX_CTL at `0x3180`, RX_CTL at `0x31a0`, and late ATE/PCS fields at `0x31c0`.
- Lane 2 begins at `0x3200`; this chunk reaches `ixDPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` at `0x3238` but does not include the rest of lane 2's raw-lane window.
- AMD display link encoder, PHY sequencing, link-training, mode-setting, hotplug, low-power, debug, and interrupt paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware/hardware state machines share ownership of many of these fields, especially reset/request handshakes, RX adaptation, DCC and RTUNE calibration, PH2 calibration, PMA/PCS handshakes, lane IRQs, and test overrides.

Behaviorally, this chunk sits below user-facing display code. It describes the bit layout needed to configure and observe CR1 raw lanes during display PHY operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts mid-register. `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` shift definitions are in the previous chunk; only the later shifts and masks are visible here.
- The chunk ends mid-register. `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` masks continue after line 35750 in the next chunk.
- Repeated lane layouts are copy-sensitive. A generator issue can affect one lane while neighboring lanes appear correct; lane 0, lane 1, and lane 2 names must pair with their matching offsets and tables.
- Status, clear, and mask registers use similar field names. Mixing IRQ status masks with clear or interrupt-mask masks can drop events, leave stale events latched, or create repeated interrupts.
- PCS and PMA override fields can bypass normal hardware sequencing. Bad masks around reset, request, data-enable, loopback, MPLL selection, termination, RTUNE, RX adaptation, PH2 calibration, or ATE controls can leave a lane in a state that higher-level display code cannot reason about.
- FSM fast-flow and calibration bits are sequencing-sensitive. Incorrect masks for fast RX startup/adapt/AFE/DFE/bypass/reference/IQ/VCO/common calibration or continuous calibration flags can cause link training failure, poor equalization, unstable links, or stuck polling loops.
- TX/RX analog-adjacent control fields affect electrical behavior through PMA/PCS handshakes and calibration paths. Wrong DCC, termination, EQ, IQ phase, or adaptation fields may produce blank displays, rate-specific failures, compliance failures, or misleading debug traces.
- Reserved masks are still emitted. Consumers should not treat reserved fields as safe software-owned configuration fields unless hardware documentation explicitly says so.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that complete fields in this range have consistent `__SHIFT` and `_MASK` pairs, allowing the known boundary exceptions for `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` at the start and `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` at the end.
- Cross-check every complete register group against `dpcs_4_2_2_offset.h`, especially lane-local offset spacing: lane 0 around `0x3000`, lane 1 around `0x3100`, and lane 2 around `0x3200`.
- Diff against AMD's source register database and nearby DPCS generated variants where lane layouts are expected to match.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lanes, and power states. Expected signals are stable link training, completed RX adaptation, no stuck reset/request handshakes, and no unexpected lane IRQs.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in PCS, FSM, IRQ, PMA, TX_CTL, RX_CTL, and ATE fields.
- Use register dumps or PHY debug traces during failing links to confirm that RX adaptation ACK/FOM, directed TX coefficient feedback, DCC status, FSM state, CR lock, IRQ clear/mask bits, RTUNE handshakes, PH2 calibration, OCLA probes, and ATE overrides decode correctly.
- Exercise diagnostic paths where available: OCLA and UPCS OCLA, serial loopback, RX statistic/adaptation debug, PH2 calibration, DCC on-demand IRQs, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` and earlier lane 0 PCS fields such as lane number and reserved PCS words. This chunk continues lane 0, fully covers lane 1, and starts lane 2. The next chunk should finish `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` and continue lane 2's IRQ, PMA, TX_CTL, RX_CTL, and late ATE/PCS fields. The final per-file research document should reconcile these artificial boundaries before making whole-file claims about all DPCS 4.2.2 CR1 raw-lane registers.

### subset-b-002352: lines 35751-38153

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 35751-38153

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment. It contains register-field metadata for AMDGPU display PHY hardware, not executable driver logic. The public surface is a large set of C preprocessor constants that give each hardware register field a bit position (`__SHIFT`) and a bit mask (`_MASK`) for use by AMD display register helpers.

The requested range covers 2,403 lines with 2,094 `#define` entries: 1,046 shift macros, 1,084 mask macros, and 309 register-comment markers. It starts in the middle of `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS`: the initial `TX_FAST_DCC_CAL` and `RX_FAST_DCC_CAL` shift definitions are in the previous chunk, while this chunk begins with `RX_FAST_VPHUD_CAL`. It then covers the tail of CR1 raw lane 2 FSM, IRQ, PMA, TX/RX control, and ATE fields; a broad CR1 raw lane 3 PCS/FSM/IRQ/PMA/TX/RX/ATE block; a full CR1 raw always-on lane 0 block; and the beginning of CR1 raw always-on lane 1 through `RX_ADPT_DFE_TAP5`. The final line is only the comment for `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN`, so that register's field definitions belong to the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, runtime variables, includes, locks, allocations, or direct MMIO calls in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` defines the least-significant bit for a field in a DPCS indirect register.
- `<REGISTER>__<FIELD>_MASK` defines the field mask used when extracting, composing, or updating that field.

Important register families in this chunk are:

- CR1 raw lane 2 FSM tail: `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS`, `CR_LOCK`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `OCLA`, `TX_EQ_UPDATE_FLAG`, `CMNCAL_RCAL_STATUS`, and `RX_IQ_PHASE_OFFSET` expose fast calibration/adaptation flags, CR register/memory lock state, TX duty-cycle-correction flags and status, on-chip logic analyzer selection, TX equalization update state, common RCAL status, and RX IQ phase offset.
- CR1 raw lane 2 IRQ controls: `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_*` defines reset-return request, RX/TX reset and request IRQs, RX rate/pstate/adaptation IRQs, clear registers, IRQ masks, lane transceiver-mode IRQs, phase-2 calibration IRQs, serial loopback IRQs, and DCC on-demand IRQ state.
- CR1 raw lane 2 PMA/PCS and controller controls: `PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and late `PCS_XF_ATE_*` groups describe PMA lane/supervisor/TX/RX override and status paths, MPHY override paths, RTUNE control, RX adaptation override output, TX FSM and clock control, DCC continuous status, RX LOS and data-enable override timing, OFFCAN/adaptation continuous status, OCLA probes, ATE RX/TX override inputs, master MPLL loop, and secondary RX/TX override banks.
- CR1 raw lane 3 PCS crossbar: `DPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_*` covers TX and RX override inputs/outputs, PCS input/output status, rate/width/pstate/low-power detect fields, MPLL selection and enablement, data enable and async TX controls, loopback/beacon/DETRX controls, RX adaptation acknowledgement and figure-of-merit, directed TX pre/main/post cursor feedback, lane number, ATE overrides, RX EQ delta/IQ controls, TX/RX termination controls, RX EQ override controls, and phase-2 calibration request/acknowledge fields.
- CR1 raw lane 3 FSM and IRQ controls: `DPCSSYS_CR1_RAWLANE3_DIG_FSM_*` and `IRQ_CTL_*` repeat the raw-lane state-machine, calibration, OCLA, DCC, IQ phase, event, clear, and mask model for lane 3.
- CR1 raw lane 3 PMA and TX/RX controller controls: `PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` expose lane/supply/TX/RX/MPHY handshakes, RTUNE controls, RX adaptation override output, TX FSM/clock/DCC status, RX FSM/LOS/data-enable controls, continuous calibration/adaptation status, and UPCS/OCLA observability.
- CR1 raw lane 3 ATE and secondary override banks: `PCS_XF_ATE_RX_OVRD_IN`, `ATE_TX_OVRD_IN`, `ATE_TX_OVRD_IN_1`, `ATE_RX_OVRD_IN_1`, `ATE_RX_OVRD_IN_2`, `ATE_RX_OVRD_IN_3`, `RX_OVRD_OUT_2`, and `TX_OVRD_IN_2` define manufacturing or deep debug override surfaces for RX/TX lane state.
- CR1 raw always-on lane 0: `DPCSSYS_CR1_RAWAONLANE0_DIG_*` includes AFE IDAC offsets, RX adaptation IQ/FOM/ATT/VGA/CTLE/DFE tap values, DFE even/odd VDAC and reference-level offsets, RX phase adjust values, MPLLA/MPLLB coarse tuning, initial power-up done bits, fast flags, slicer controls, common MPLL/RCAL status, adaptation control words, MPLL disable, fast flags 2, TX/RX overrides, LOS mask and signal-detect filtering, statistics, RX override readbacks, signal-detect calibration and codes, VREF generator enable, calibration codes, RX DCC calibration I/Q code banks, TX DCC bank address/data/continuous control, MPLL bandgap control, signal-detect output override/input, firmware mode/adaptation/calibration config, lane transceiver-mode override/input, RX signal-detect config, and TX DCC config.
- CR1 raw always-on lane 1 start: `DPCSSYS_CR1_RAWAONLANE1_DIG_*` begins the same always-on lane pattern from AFE offsets through RX adaptation DFE taps 2-5, but the slicer-control fields and later lane 1 always-on registers continue in the next chunk.

Most masks are 16-bit-style constants with an `L` suffix, matching the DPCS indirect register width used by these PHY control and status blocks. Several multi-field masks cover reserved bit ranges; consumers must preserve these according to the register access semantics implemented outside this header.

## Control Flow

This header has no runtime control flow. It is compile-time data used by the display driver:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Version-specific register, shift, and mask tables are built with generated names and token-pasting helper macros.
3. Runtime display code uses register helpers such as read, write, get, set, and update operations with those tables.
4. Actual sequencing for lane bring-up, PLL and MPLL selection, link training, RX adaptation, DCC calibration, interrupt handling, ATE/debug override use, power management, and diagnostics lives in AMDGPU display code and hardware/firmware state machines.

The macros here only describe bit layout. They do not encode access type, reset value, read-only/write-only behavior, write-one-to-clear behavior, self-clearing bits, polling order, timeout requirements, or clock and power domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR1 DPCS registers:

- Raw lane 2 and lane 3 FSM state includes fast startup/adaptation/calibration flags, common MPLL/RCAL status, continuous calibration/adaptation state, CR lock state, TX DCC state, OCLA selection, TX EQ update state, and RX IQ phase offset.
- Raw lane 2 and lane 3 IRQ state includes RX and TX reset/request events, RX rate and pstate events, adaptation request/disable events, phase-2 calibration request/disable events, lane transceiver-mode changes, serial loopback enable events, DCC on-demand events, matching clear fields, and mask fields.
- Raw lane 2 and lane 3 PMA/PCS state includes TX/RX reset, request, pstate, rate, width, low-power detect, MPLL select and enable, master MPLL state, receive-detect controls, loopback and beacon controls, data-enable and async data paths, adaptation acknowledgements, FOM readback, directed TX coefficient feedback, termination controls, RTUNE control, MPHY control, supply power state, and PMA-facing ACK/data/valid/readback paths.
- Raw lane 2 and lane 3 TX/RX controller state includes TX FSM control, TX clock control, DCC continuous status, RX FSM control, LOS mask timing, RX data-enable override timing, OFFCAN continuous state, adaptation continuous state, and OCLA/UPCS debug observability.
- Raw always-on lane 0 and lane 1 state includes adaptation results and tuning values for AFE, CTLE, VGA, DFE taps, slicers, phase adjust, FOM, ATT, common calibration status, MPLL coarse tuning, initial power-up, signal-detect, VREF, DCC calibration code banks, TX DCC bank access, firmware configuration, and lane transceiver mode.

Persistence is determined by hardware. Configuration fields generally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver initialization rewrites them. Status, ACK, IRQ, statistic, calibration, and handshake fields may be sampled, latched, clear-on-write, self-clearing, or valid only while the relevant DPCS lane, always-on lane, common clock, and power domains are active. This generated header does not specify those semantics.

## Dependencies And Integration Points

The direct compile-time dependency is the C preprocessor. The semantic dependency is AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` addresses. For the CR1 instance covered here, this chunk aligns with offsets such as `0x3238` for `RAWLANE2_DIG_FSM_FAST_FLAGS`, `0x324d` and `0x324e` for raw lane 2 IRQ mask registers, `0x3300` and later for raw lane 3 PCS transfer registers, `0x4000` and later for raw always-on lane 0, and `0x4100` and later for raw always-on lane 1.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`, tying this generated register contract to DCN 3.1.5 resource initialization.
- AMD display link encoder, PHY, clock-source, link-training, power-management, interrupt, diagnostics, and manufacturing/test code consume the generated constants indirectly through register tables and helper macros rather than open-coded bit numbers.
- Firmware and hardware state machines interact with the same fields, especially for PMA/PCS handshakes, RX adaptation, signal detect, DCC calibration, RTUNE, MPLL status, fast calibration flows, and low-level lane IRQ latching.

Behaviorally, this range sits below user-facing display policy. It defines bit positions and masks needed when the driver or firmware configures CR1 raw lanes 2 and 3, observes low-level lane state, handles lane interrupts, and reads or overrides raw always-on lane calibration and adaptation state.

## Risks And Edge Cases

- These are untyped preprocessor constants. Incorrect shifts or masks can compile cleanly while writing adjacent fields, preserving the wrong reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register source, the companion offset header, firmware expectations, and silicon behavior.
- The chunk starts and ends inside logical groups. `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` is missing its first two shift definitions in this slice, and `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` is only a trailing comment with its field definitions in the next slice.
- The range mixes raw lane 2 tail definitions, full raw lane 3 definitions, raw always-on lane 0 definitions, and the start of raw always-on lane 1. Consumers must pair each macro with the correct CR1 offset and lane/register table.
- Lane 2 and lane 3 register names are highly repetitive. A generator, merge, or manual-copy error can affect only one lane while adjacent lane definitions appear valid, causing asymmetric link-training or lane-count failures.
- IRQ status, clear, and mask fields have similar names. Confusing status, clear, and mask registers can drop events, leave latched IRQ bits uncleared, or produce repeated low-level interrupts.
- Override registers often contain both override-enable bits and override-value bits. Setting values without enables, or leaving enables asserted after ATE/debug use, can force the PHY away from normal state-machine control.
- PMA/PCS, termination, RTUNE, MPHY, DCC, MPLL, signal-detect, VREF, slicer, and DFE fields affect electrical link behavior. Wrong masks can surface as blank displays, unstable links, compliance failures, retraining loops, or misleading hardware debug traces.
- Reserved masks are explicit but not safe scratch space. Register update code must use the correct helper semantics so reserved bits are not corrupted.

## Test Signals

Useful validation combines generated-header checks with hardware-oriented display testing:

- Build AMDGPU display support for DCN 3.1.5 code that includes `dpcs_4_2_2_sh_mask.h` through `dcn315_resource.c`. Missing, renamed, or malformed macros should fail in generated register/shift/mask table initialization.
- Statically verify that complete register groups in this chunk have matching `__SHIFT` and `_MASK` definitions, while allowing the known boundary exceptions for `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` at the start and `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` at the end.
- Cross-check every complete register group in the slice against `dpcs_4_2_2_offset.h`, especially the CR1 raw lane 2 tail, raw lane 3 repeated window, raw always-on lane 0 window, and raw always-on lane 1 start.
- Diff generated DPCS 4.2.2 fields against adjacent hardware versions or sibling lanes where layouts are expected to match. Repeated lane 2/lane 3 and always-on lane 0/lane 1 patterns are strong signals for generator drift.
- Exercise DisplayPort and HDMI link bring-up across lane counts, rates, power states, and hotplug sequences. Watch for stable link training, correct RX adaptation completion, correct PMA/PCS acknowledgements, no stuck DCC or calibration status, and no unexpected raw lane IRQs.
- Run modeset, stream disable/enable, suspend/resume, and GPU reset flows to catch persistence and reinitialization issues around FSM, IRQ, PMA/PCS, signal-detect, DCC, MPLL, and always-on lane calibration state.
- Use register dumps or PHY debug traces on failures to confirm that IRQ status/clear/mask bits, RX adaptation FOM/tap values, DFE offsets, slicer controls, signal-detect calibration, VREF generator state, DCC code banks, RTUNE fields, and MPLL status decode with the expected masks.
- Exercise diagnostic or manufacturing paths where available: OCLA, UPCS_OCLA, ATE RX/TX override banks, MPHY override paths, loopback, directed TX coefficient feedback, phase-2 calibration, signal-detect output override, firmware config registers, and TX DCC bank access.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` and earlier raw lane 2 PCS/FSM fields. This chunk finishes that raw lane 2 tail, covers raw lane 3 and raw always-on lane 0, and begins raw always-on lane 1. The next chunk should start with the field definitions for `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` and continue the rest of CR1 raw always-on lane 1. The later merge/reconciliation lane should combine these boundaries before making whole-file claims about the complete DPCS 4.2.2 register map.

### subset-b-002353: lines 38154-40593

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 38154-40593

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic; its exported interface is a large set of C preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,083 `#define` entries across 2,440 lines and 357 commented register-group markers. It starts at `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` and continues through the rest of CR1 always-on lane 1, then repeats the CR1 always-on lane programming surface for lane 2, lane 3, and the lane-X broadcast/template block. The latter part switches to CR1 supervisor (`SUPX`) digital and analog fields, including ID-code readback, reference-clock overrides, MPLLA/MPLLB override inputs, spread-spectrum and fractional PLL words, charge-pump overrides, ASIC input readback fields, common supervisor control, prescaler control, and bandgap enable. The range ends at the comment for `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL`; that register's field definitions are in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The public surface follows the generated AMD register-field convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main macro families in this chunk are:

- CR1 raw always-on lane 1 tail: `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` through `DPCSSYS_CR1_RAWAONLANE1_DIG_TX_DCC_CONFIG` define slicer controls, common MPLL/RCAL calibration status, adaptation control words, MPLL disable bits, fast calibration/adaptation flags, TX/RX disable overrides, LOS mask timing, signal-detect filtering, RX override outputs, signal-detect thresholds/codes, VREF/calibration codes, RX and TX DCC calibration/bank controls, MPLL bandgap control, signal-detect output override/readback, firmware mode/adaptation/calibration configuration, lane transceiver-mode override/readback, and RX signal-detect/TX DCC configuration.
- CR1 raw always-on lanes 2, 3, and X: `DPCSSYS_CR1_RAWAONLANE2_*`, `DPCSSYS_CR1_RAWAONLANE3_*`, and `DPCSSYS_CR1_RAWAONLANEX_*` repeat the full always-on lane pattern starting at AFE ATT/CTLE offset fields and covering RX adaptation IQ/FOM, DFE data/error/bypass/phase/ref-level offsets, RX phase adjust, MPLLA/MPLLB coarse tune, initial power-up done, ATT/VGA/CTLE/DFE tap adaptation values, adaptation-done bits, fast flags, slicer control, common calibration status, adaptation-control words, TX/RX overrides, LOS/signal-detect controls, calibration codes, DCC controls, firmware config, and transceiver-mode fields. The `LANEX` names usually serve register-table or broadcast/template paths rather than naming a single physical lane.
- CR1 supervisor digital identification and clock overrides: `DPCSSYS_CR1_SUPX_DIG_IDCODE_LO`, `IDCODE_HI`, `REFCLK_OVRD_IN`, `MPLLA_DIV_CLK_OVRD_IN`, `MPLLA_HDMI_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, and `MPLLB_HDMI_CLK_OVRD_IN` expose ID-code readback, reference-clock source/enable/test override fields, and divider/HDMI clock override controls for MPLLA and MPLLB.
- CR1 MPLLA/MPLLB override programming: `DPCSSYS_CR1_SUPX_DIG_MPLLA_OVRD_IN_*`, `MPLLB_OVRD_IN_*`, `MPLLA_SSC_*`, `MPLLB_SSC_*`, `MPLLA_CP_OVRD_IN`, `MPLLB_CP_OVRD_IN`, and the gain-scheduled CP override registers define PLL enable, dividers, VCO range, standby, calibration force, fractional-N enable/update, SSC enable/up-spread/PMIX/word-div2/clock-sync controls, SSC peak and step-size split words, fractional numerator/remainder/denominator split words, and charge-pump proportional/integral override values and enables.
- CR1 supervisor control and readback: `DPCSSYS_CR1_SUPX_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `DEBUG`, `*_ASIC_IN_*`, `*_DIV_CLK_ASIC_IN`, `*_HDMI_CLK_ASIC_IN`, `ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, `*_CP_ASIC_IN`, and `*_CP_GS_ASIC_IN` define supervisor reset/reference/RTUNE/test override fields, prescaler override fields, calibration and PLL lock readback, level/voltage controls, PLL ASIC input mirrors, divider/HDMI clock ASIC input mirrors, common PHY reset/reference/RTUNE state, VREF/vboost selections, bandgap enable, and charge-pump ASIC input mirrors.
- CR1 supervisor analog prescaler: `DPCSSYS_CR1_SUPX_ANA_PRESCALER_CTRL` defines analog prescaler ATB selection, VREG measurement, fast-start override, VREG boost, and hysteresis reference fields. The next marker, `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL`, is present only as a comment at line 40593 in this chunk.

Most fields use 16-bit masks with an `L` suffix, matching the narrow DPCS indirect register fields used by these raw lane, always-on lane, supervisor, MPLL, and analog control blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register metadata construction:

1. AMD display code for the matching DCN/DPCS generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables token-paste or name these constants for hardware helper code.
3. Runtime display code uses register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` with those tables to program or read DPCS PHY state.
4. Real sequencing for link bring-up, RX adaptation, signal detection, DCC calibration, MPLL programming, reference-clock selection, RTUNE, power state transitions, diagnostics, and suspend/resume lives outside this generated header.

The macros describe only bit layout. They do not encode reset values, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, clock-domain constraints, power-domain validity, programming order, or timeout requirements.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR1 always-on lane and CR1 supervisor DPCS registers:

- Lane RX adaptation state includes AFE ATT/CTLE offsets, IQ adaptation, FOM, DFE phase/data/error/bypass offsets, DFE tap values, ATT/VGA/CTLE adaptation results, even/odd slicer controls, phase-adjust values, adaptation-done bits, fast adaptation/calibration flags, and free-form adaptation-control words.
- Lane calibration and signal-detect state includes common MPLL/RCAL init/done bits, RX LOS mask count, signal-detect filter controls, squelch/stat outputs, RX signal-detect thresholds and codes, VREF generator enable, IOFF/ICONST/VREFGEN calibration codes, RX DCC I/Q calibration code words, TX DCC bank address/data/continuous control, and signal-detect output override/readback.
- Lane override state includes RX/TX disable override values/enables, RX PMA squelch/VREF/termination/signal-detect override outputs, MPLLA/MPLLB disable/coarse-tune controls, MPLL bandgap control, lane transceiver-mode override/readback, firmware mode/adaptation/calibration configuration, RX signal-detect configuration, and TX DCC configuration.
- Supervisor and PLL state includes ID-code readback, reference-clock override, MPLLA/MPLLB divider and HDMI clock overrides, PLL enable/standby/divider/VCO/calibration/fractional-N controls, SSC peak and step-size values, fractional numerator/remainder/denominator words, clock-sync controls, charge-pump proportional/integral overrides, gain-scheduled charge-pump overrides, PLL lock readback, calibration outputs, PHY reset/reference/RTUNE state, level controls, bandgap enable, and analog prescaler controls.

Persistence is hardware-defined. Configuration fields normally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, done, lock, calibration, and readback fields may be latched, sampled, self-clearing, or valid only while the corresponding lane, supervisor, reference-clock, and PLL power domains are active. This generated header does not define those semantics.

## Dependencies And Integration Points

This generated shift/mask file must stay synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` offsets. In that file, CR1 always-on lane 1 begins at offsets such as `0x4100` and this chunk starts at `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` at `0x4121`; lane 2 starts at `0x4200`, lane 3 at `0x4300`, and lane X at `0x7000`.
- The same offset header maps CR1 supervisor/SUPX registers from `DPCSSYS_CR1_SUPX_DIG_IDCODE_LO` at `0x8000` through the MPLLA/MPLLB override, ASIC input, common supervisor, and analog prescaler region. For example, `DPCSSYS_CR1_SUPX_DIG_MPLLA_OVRD_IN_0` is at `0x8007`, `DPCSSYS_CR1_SUPX_DIG_MPLLA_ASIC_IN_0` is at `0x8024`, and `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL` follows the chunk boundary at `0x8041`.
- AMD display DCN/DPCS resource code consumes these constants indirectly through generated register, shift, and mask tables rather than by open-coding bit values.
- Link encoder, PHY bring-up, DisplayPort/HDMI link training, clock programming, diagnostics, hotplug recovery, suspend/resume, and GPU reset code may interact with the hardware fields described here via the register helpers.
- Firmware and hardware state machines also share this register surface, especially for RX adaptation, signal detection, DCC calibration, MPLL calibration/lock, SSC/fractional PLL programming, RTUNE handshakes, power state entry/exit, and analog prescaler/bandgap controls.

Behaviorally, this range is below the user-facing display stack. It is the bit-layout contract used when the driver and firmware configure CR1 lanes and common supervisor/PLL resources for display PHY operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while causing the driver to update the wrong field, corrupt reserved bits, or decode hardware status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. The previous chunk contains earlier lane 1 adaptation and DFE tap groups; this chunk starts at the first field of `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN`. This chunk ends with only the `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL` marker; all RTUNE field definitions follow in the next chunk.
- The lane 2, lane 3, and lane-X blocks are highly repetitive. Generator or merge mistakes can affect only one lane, one broadcast/template name, or one duplicated A/B PLL side while nearby fields look correct by inspection.
- RX adaptation and signal-detect fields are sequencing-sensitive. Wrong masks around DFE taps, slicers, VDAC/IDAC offsets, adaptation-done bits, signal-detect thresholds, LOS masking, or RX DCC codes can lead to link-training failures, marginal equalization, false loss-of-signal, or misleading debug traces.
- Override registers bypass normal hardware state-machine choices. Misprogramming TX/RX disable, PMA squelch/termination/VREF/signal-detect, MPLL disable/coarse tune, firmware config, or transceiver-mode fields can leave a lane in a state that higher-level display code cannot easily diagnose.
- MPLLA/MPLLB and reference-clock fields affect shared clocking. Bad masks for PLL enable, dividers, HDMI dividers, VCO selection, fractional-N words, SSC controls, charge-pump overrides, clock-sync, standby, or calibration force can cause unstable clocks, black screens, retraining loops, audio/video timing problems, or mode-specific regressions.
- Status/readback and configuration fields are interleaved across similarly named `OVRD_IN`, `ASIC_IN`, and `OVRD_OUT` groups. Confusing these groups can make code write to readback-style fields or read stale override configuration instead of live hardware state.
- Reserved-bit masks are present throughout the generated header. Register update helpers must avoid relying on reserved fields as meaningful state, and hand-written values must preserve hardware-required reserved behavior.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this range has the expected `__SHIFT` and `_MASK` pair, while treating the final `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL` marker as a next-chunk boundary rather than a missing definition.
- Cross-check every complete register group in this chunk against `dpcs_4_2_2_offset.h`, especially the CR1 lane offsets (`0x4100`, `0x4200`, `0x4300`, `0x7000`) and CR1 supervisor offsets (`0x8000+`).
- Diff against AMD's source register database and nearby generated variants such as other DPCS 4.2.x shift/mask headers where hardware layout is expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across supported rates, lane counts, PHY lanes, and power states. Expected signals are stable link training, correct RX adaptation completion, valid signal-detect behavior, correct MPLL selection/lock, and no stuck calibration status.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in lane adaptation, signal-detect, DCC calibration, transceiver-mode, reference-clock, and MPLL fields.
- Validate clock-sensitive modes that stress MPLLA/MPLLB dividers, HDMI dividers, SSC, fractional PLL programming, charge pump settings, reference-clock source selection, and clock-sync controls. Watch for black screens, PHY lock failures, retraining loops, display corruption, or timing instability.
- Use register dumps or PHY debug traces during failing links to confirm DFE tap values, RX FOM/IQ, slicer settings, signal-detect thresholds/codes, DCC calibration words, transceiver-mode fields, PLL override inputs, ASIC input readbacks, lock status, and analog prescaler fields decode correctly.

## Cross-Chunk Notes

The previous chunk owns earlier CR1 raw always-on lane 1 adaptation fields through `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_ADPT_DFE_TAP5`. This chunk starts with `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN`, completes the rest of lane 1, covers complete lane 2, lane 3, lane-X, and most CR1 SUPX digital/supervisor/PLL readback groups, then stops at the `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL` comment. The next chunk should provide the RTUNE field definitions and continue the CR1 SUPX analog register sequence. The final per-file research document should reconcile these boundaries before making whole-file claims about all DPCS 4.2.2 register groups.

### subset-b-002354: lines 40594-42955

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 40594-42955

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic; the exported surface is preprocessor constants that encode DPCS register bit positions (`__SHIFT`) and bit masks (`_MASK`).

The requested range contains 2,136 `#define` entries across 226 register-comment groups. It starts at `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL`, covers CR1 supervisor analog bandgap/RTUNE/MPLL definitions, CR1 supervisor digital MPLLA/MPLLB power-control and analog override outputs, and most of the CR1 lane-X digital ASIC, TX/RX power, CDR, adaptation, statistics, MPHY, and digital-to-analog override field definitions. It ends inside `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2`, before that register's final two masks and before `DPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL` in the next chunk.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field inside the associated DPCS register.
- `<REGISTER>__<FIELD>_MASK`: bit mask used by AMD display register helpers to isolate, compose, or update that field.

Most fields in this slice describe 16-bit DPCS register payloads stored in 32-bit constants. The exact requested range has 1,072 shift macros and 1,064 mask macros. The imbalance is caused by generated data and the artificial chunk boundary: `DPCSSYS_CR1_SUPX_DIG_RTUNE_DEBUG` provides shifts without matching masks in this range, and `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2` has two masks after line 42955.

Main register families in this chunk:

- `DPCSSYS_CR1_SUPX_ANA_*`: supervisor analog RTUNE, bandgap/reference selection, switch/power measurement, MPLLA/MPLLB miscellaneous, override, analog-test-bus, charge pump, PLL control, and reserved analog control fields.
- `DPCSSYS_CR1_SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR1_SUPX_DIG_MPLLB_MPLL_PWR_CTL_*`: digital MPLL override, status, DAC range, lock and power timing, calibration, analog DAC readback, and spread-spectrum type fields for both PLLs.
- `DPCSSYS_CR1_SUPX_DIG_CLK_RST_*`, `RTUNE_*`, and `ANA_*_OVRD_OUT`: supervisor digital bandgap/reference power-up timing, RTUNE configuration/status/setpoint/readback, MPLLA/MPLLB analog override outputs, RTUNE override output, analog status, bandgap override, and PMIX override fields.
- `DPCSSYS_CR1_LANEX_DIG_ASIC_*`: lane-X ASIC-facing override and normal input/output mirrors for TX, RX, EQ, CDR/VCO, lane loopback, AC JTAG, OCLA, ACK/status, lane-master, and cross-lane clock/shift handshakes.
- `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_*`: TX P-state programming, TX power-up timing, DCC CR-bank windows, DCC DAC control/range/selection/ACK/address, TX clock alignment, and TX LBERT controls.
- `DPCSSYS_CR1_LANEX_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, `RX_ADPTCTL_*`, and `RX_STAT_*`: RX power-state control, VCO calibration, CDR, DPLL frequency/bounds, adaptation configuration/status/reset, CR-bank windows, programmable RX statistic masks/matchers/counters, sample counts, and stop controls.
- `DPCSSYS_CR1_LANEX_DIG_MPHY_*` and `DIG_ANA_*`: MPHY RX PWM/termination controls and digital-to-analog TX/RX override outputs for TX control, term code, TX EQ, RX control/power, and RX VCO tuning.

## Control Flow

This header has no runtime control flow. It participates in AMDGPU display setup as compile-time register metadata:

1. `dcn315_resource.c` includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`.
2. DCN resource macros such as `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` expand register offsets, shifts, and masks into display resource tables.
3. Runtime display code uses common helpers such as register read/update macros against those tables.
4. Actual sequencing for PLL power, RTUNE, lane power states, CDR/VCO calibration, DCC, RX adaptation, statistics, and analog diagnostics lives outside this generated header.

The constants here define where bits live. They do not encode access direction, self-clearing behavior, timeout policy, clock-domain constraints, or reset ordering.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible CR1 supervisor and lane-X state:

- Supervisor analog state: bandgap/reference selection, RTUNE controls, ATB measurement selection, MPLLA/MPLLB enable/reset/calibration override values, charge-pump and PLL tuning, clock divider and regulator bypass bits, and PMIX control.
- Supervisor digital state: MPLLA/MPLLB power-control finite-state status, lock status, PLL lane ownership bits, clock enables, calibration controls, timing values, DAC limits/readback, spread-spectrum type override, RTUNE setpoints/status, and analog override outputs.
- Lane ASIC interface state: TX/RX request, P-state, rate, width, data enable, reset, disable, inversion, low-power detect, clock-ready, detect-RX, MPLLB select, HDMI/MPHY modes, loopback, async TX data/drive, ACK, valid, adaptation status, EQ values, VCO/ref load values, and lane-master/other-lane synchronization.
- TX state: per-P-state analog refgen, VCM hold, clock, reset, serial/data, powerdown, high-Z, DCC, output, RX-detect, and Vboost bits; TX power-up timing; DCC bank/DAC programming; TX clock alignment; LBERT control.
- RX state: per-P-state AFE, clock, CDR, deserializer, squelch, scope, adaptation, slicer, DFE, and fast-start controls; VCO calibration control/timing/status; CDR bypass/tracking/rate controls; DPLL frequency and bounds; adaptation algorithm settings and status readbacks.
- Diagnostic state: RX statistic masks/patterns/counters, OCLA enable/data controls, MPHY PWM and low-speed termination controls, term-code/TX EQ/RX VCO override outputs, analog status, and readback fields.

Persistence is hardware-defined. Control fields generally retain values until driver reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/hardware ownership changes. ACK, valid, lock, statistic, calibration, and status fields may be sampled, latched, self-clearing, or only valid while the relevant CR1 power and clock domains are active. This generated header does not describe those side effects.

## Dependencies And Integration Points

The direct syntactic dependency is only the C preprocessor, but the values must stay synchronized with the DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `regDPCSSYS_*` and `ixDPCSSYS_*` register addresses, including examples in this slice such as `ixDPCSSYS_CR1_SUPX_DIG_MPLLA_MPLL_PWR_CTL_MPLL_OVRD`, `ixDPCSSYS_CR1_LANEX_DIG_RX_STAT_MATCH_CTL0`, and `ixDPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes this header and the matching offset header for DCN 3.1.5 resource initialization.
- AMD display register helper tables consume the shift/mask names through DPCS register-list and mask-list macros.
- Behavioral consumers are link encoder, PHY, AUX/DPCS access, HPO/DP, HDMI, link-training, modeset, power-management, and diagnostic paths that program or inspect DPCS CR1 lanes and supervisor PLL/RTUNE blocks.

The chunk is source-tree-aligned with generated AMDGPU ASIC register headers, not with filesystem logic.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong bit position or mask compiles cleanly but can write an adjacent hardware field, preserve the wrong reserved bits, or decode a status field incorrectly.
- Manual edits to generated metadata risk divergence from AMD's authoritative register source, the matching `dpcs_4_2_2_offset.h`, firmware assumptions, and nearby DPCS generations.
- The chunk ends mid-register at `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2`; whole-register validation must reconcile its remaining masks from the next chunk.
- `DPCSSYS_CR1_SUPX_DIG_RTUNE_DEBUG` has shift-only field definitions in this range. Validators should distinguish generated shift-only groups from missing accidental masks.
- MPLLA/MPLLB and supervisor RTUNE/bandgap fields are shared resources for the CR1 PHY. Incorrect masks can affect more than one lane or connector path.
- Override-enable fields sit near override values. Accidentally setting an enable can take ownership away from normal hardware or firmware control; forgetting it can make a debug value write appear ineffective.
- TX/RX power, CDR, VCO, DPLL, DCC, adaptation, and termination fields are sequencing-sensitive. A mask error may show up as intermittent link training failure, blank display, CDR unlock, high bit error rate, or resume-only failure.
- Status/readback fields are intermixed with writable controls. Consumers cannot infer access direction, clear behavior, or side effects from `_MASK` presence alone.
- Repeated MPLLA/MPLLB and TX/RX lane-X structures are copy-sensitive. A generator issue can affect only one PLL, P-state, statistic counter, DFE tap, or calibration field while surrounding groups remain correct.
- Reserved and `NC` fields have explicit masks throughout the range. Driver writes should preserve them unless the hardware specification explicitly requires a value.

## Test Signals

Useful validation is mostly generated-data, build, and hardware-integration oriented:

- Build AMDGPU display code that includes `dcn315_resource.c`; missing or renamed DPCS 4.2.2 macros should fail during resource-table initialization.
- Mechanically verify that complete register groups in lines 40594-42955 have matching `__SHIFT` and `_MASK` entries, allowing the known `RTUNE_DEBUG` shift-only group and the `ANA_RX_VCO_OVRD_OUT_2` boundary.
- Cross-check the register names in this chunk against `dpcs_4_2_2_offset.h` for corresponding `ixDPCSSYS_*` offsets.
- Diff compatible fields against AMD's generated source and nearby DPCS variants such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` where the hardware register database expects stable layouts.
- Exercise DCN 3.1.5 display paths that depend on DPCS 4.2.2: DisplayPort and HDMI link bring-up, rate/width changes, hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset.
- Check register dumps or PHY debug traces for MPLLA/MPLLB lock and power states, RTUNE status/setpoints, TX/RX P-state transitions, CDR/VCO calibration status, DPLL bounds, DCC ACK, RX adaptation status, RX statistic counters, DETRX/TX ACK, and analog override/readback fields.
- Run controlled diagnostic paths for LBERT, OCLA, RX statistic match/counter logic, MPHY PWM/termination, TX term/EQ override, RX VCO override, RTUNE, and DCC DAC controls when hardware access is available.

## Cross-Chunk Notes

The previous chunk ends with `DPCSSYS_CR1_SUPX_ANA_PRESCALER_CTRL`; this chunk begins the next complete register group, `DPCSSYS_CR1_SUPX_ANA_RTUNE_CTRL`. The next chunk should continue `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2` masks and then cover `DPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL` and later lane-X analog fields. The final per-file report should reconcile these artificial chunk boundaries before making whole-file claims about DPCS 4.2.2.

### subset-b-002355: lines 42956-45339

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 42956-45339

## Scope

This chunk covers lines 42956-45339 of the generated AMD DPCS 4.2.2 shift/mask header. It contains register bitfield definitions only: 1,065 `__SHIFT` macros and 1,083 `_MASK` macros across 254 register/comment groups in a 2,384-line slice. The shift/mask count is intentionally uneven at this boundary because the chunk starts in the middle of `DPCSSYS_CR1_LANEX_DIG_ANA_RX_VCO_OVRD_OUT_2` mask definitions and ends after the first `DPCSSYS_CR2_SUP_ANA_MPLLA_ATB1__meas_iv_wrap__SHIFT` line, before that register group's remaining shifts and masks.

The covered content spans the tail of the `DPCSSYS_CR1` generic lane (`LANEX`) analog and raw-lane control definitions, then begins the `addressBlock: dpcssys_cr2_rdpcstxcrind` section and defines the first part of the `DPCSSYS_CR2` supervisor digital/analog PLL support mask surface. It is declarative C preprocessor data; there are no functions, structs, enums, storage objects, branches, locks, or direct register accesses in this chunk.

## Purpose

`dpcs_4_2_2_sh_mask.h` gives AMDGPU display code symbolic bit positions and masks for indexed DPCS 4.2.2 registers. This chunk defines how callers compose or decode fields for:

- CR1 generic-lane receive analog controls, calibration controls, signal-detect controls, transmit analog controls, and analog measurement/test hooks.
- CR1 raw PCS/PMA/FSM/IRQ/TX/RX lane controls used around lane state machines, interrupt signaling, crossbar/PHY interfaces, ATE paths, and adaptation status.
- CR2 supervisor common digital controls for reference clocks, MPLLA/MPLLB overrides, spread-spectrum parameters, charge-pump values, power/reset state, level controls, and ASIC-facing values.
- CR2 supervisor analog controls for prescaler, RTUNE, bandgap/reference selection, power measurement switching, and initial MPLLA analog override/test fields.

The macros are intended to be used with the matching `dpcs_4_2_2_offset.h` register-offset macros. For example, this chunk's `DPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL__*` fields pair with `ixDPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL`, and `DPCSSYS_CR2_SUP_DIG_MPLLA_OVRD_IN_0__*` pairs with `ixDPCSSYS_CR2_SUP_DIG_MPLLA_OVRD_IN_0`.

## Exported API Surface

The only API exported by this chunk is preprocessor constants. Every complete register group has a family of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. There are no callable APIs.

Important CR1 LANEX analog groups include:

- RX calibration and DAC controls: `DPCSSYS_CR1_LANEX_DIG_ANA_RX_CAL`, `RX_DAC_CTRL`, `RX_DAC_CTRL_OVRD`, `RX_DAC_CTRL_SEL`, `RX_ANA_CAL_DAC_CTRL_EN`, and `RX_ANA_SIGNALS_CHANGES_ENABLE`.
- RX front-end and sampling controls: `RX_AFE_ATT_VGA`, `RX_AFE_CTLE`, `RX_SCOPE`, `RX_SLICER_CTRL`, `RX_ANA_IQ_PHASE_ADJUST`, `RX_ANA_IQ_SENSE_EN`, and `RX_ANA_PHASE_ADJUST_CLK`.
- RX status and termination controls: `DPCSSYS_CR1_LANEX_DIG_ANA_STATUS_0`, `STATUS_1`, `RX_TERM_CODE_OVRD_OUT`, and `RX_TERM_CODE_CLK_OVRD_OUT`.
- MPHY/signal-detect controls: `MPHY_OVRD_OUT`, `SIGDET_OVRD_OUT_1`, and `SIGDET_OVRD_OUT_2`.
- TX DCC/equalization/power/measurement controls: `TX_DCC_DAC_OVRD_OUT`, `TX_DCC_DAC_OVRD_OUT_2`, `TX_OVRD_OUT_2`, `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1`, `ANA_TX_ATB2`, `ANA_TX_DCC_DAC`, `ANA_TX_DCC_CTRL1`, `ANA_TX_TERM_CODE`, `ANA_TX_TERM_CODE_CTRL`, `ANA_TX_OVRD_CLK`, `ANA_TX_MISC1`, `MISC2`, `MISC3`, and reserved TX analog registers.
- RX analog raw controls: `ANA_RX_CLK_1`, `ANA_RX_CLK_2`, `ANA_RX_CDR_DES`, `ANA_RX_SLC_CTRL`, `ANA_RX_PWR_CTRL1`, `ANA_RX_PWR_CTRL2`, `ANA_RX_SQ`, `ANA_RX_CAL1`, `ANA_RX_CAL2`, `ANA_RX_ATB_REGREF`, `ANA_RX_ATB_MEAS1` through `MEAS4`, `ANA_RX_ATB_FRC`, and `ANA_RX_RESERVED1`.

Important CR1 raw-lane digital groups include:

- PCS crossbar interfaces: `RAWLANEX_DIG_PCS_XF_TX_OVRD_IN`, `TX_OVRD_IN_1`, `TX_PCS_IN`, `TX_OVRD_OUT`, `TX_PCS_OUT`, `RX_OVRD_IN`, `RX_OVRD_IN_1` through `RX_OVRD_IN_3`, `RX_PCS_IN` through `RX_PCS_IN_4`, `RX_OVRD_OUT`, and `RX_PCS_OUT`.
- Adaptation and directed-control status: `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, `RX_TXPOST_DIR`, `LANE_NUMBER`, `ATE_OVRD_IN`, `RX_EQ_DELTA_IQ_OVRD_IN`, `TXRX_TERM_CTRL_OVRD_IN`, `TXRX_TERM_CTRL_IN`, `RX_OVRD_OUT_1`, `RX_EQ_OVRD_IN_1`, `RX_EQ_OVRD_IN_2`, and `RX_PH2_CAL`.
- Lane FSM programming/status: `FSM_FSM_OVRD_CTL`, `FSM_MEM_ADDR_MON`, `FSM_STATUS_MON`, many `FSM_FAST_*` calibration/adaptation step registers, `FSM_CMNCAL_MPLL_STATUS`, `FSM_FAST_FLAGS`, `FSM_CR_LOCK`, `FSM_TX_DCC_FLAGS`, `FSM_TX_DCC_STATUS`, `FSM_OCLA`, `FSM_TX_EQ_UPDATE_FLAG`, `FSM_CMNCAL_RCAL_STATUS`, and `FSM_RX_IQ_PHASE_OFFSET`.
- IRQ status/clear/mask controls: reset, request, rate, p-state, adaptation request/disable, phase-2 calibration, loopback, DCC-on-demand, TX reset/request, corresponding clear registers, `IRQ_MASK`, and `IRQ_MASK_2`.
- PMA crossbar and TX/RX controller controls: `PMA_XF_LANE_OVRD_IN`, `PMA_XF_LANE_OVRD_OUT`, `PMA_XF_SUP_OVRD_IN`, `PMA_XF_SUP_PMA_IN`, `PMA_XF_TX_OVRD_OUT`, `PMA_XF_TX_PMA_IN`, `PMA_XF_RX_OVRD_OUT`, `PMA_XF_RX_PMA_IN`, `PMA_XF_LANE_RTUNE_CTL`, `PMA_XF_MPHY_OVRD_IN`, `PMA_XF_MPHY_OVRD_OUT`, `PMA_XF_RX_ADAPT_OVRD_OUT`, `TX_CTL_*`, and `RX_CTL_*`.
- ATE and secondary PCS views: `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN_1`, `PCS_XF_MASTER_MPLL_LOOP`, `PCS_XF_ATE_RX_OVRD_IN_1` through `IN_3`, `PCS_XF_RX_OVRD_OUT_2`, and `PCS_XF_TX_OVRD_IN_2`.

Important CR2 supervisor groups include:

- Identification and clocks: `SUP_DIG_IDCODE_LO`, `SUP_DIG_IDCODE_HI`, `SUP_DIG_REFCLK_OVRD_IN`, `MPLLA_DIV_CLK_OVRD_IN`, `MPLLA_HDMI_CLK_OVRD_IN`, `MPLLB_DIV_CLK_OVRD_IN`, and `MPLLB_HDMI_CLK_OVRD_IN`.
- MPLL override/programming: `MPLLA_OVRD_IN_0` through `MPLLA_OVRD_IN_5`, `MPLLA_SSC_PEAK_1`, `MPLLA_SSC_PEAK_2`, `MPLLA_SSC_STEPSIZE_1`, `MPLLA_SSC_STEPSIZE_2`, `MPLLA_CP_OVRD_IN`, `MPLLA_CP_GS_OVRD_IN`, and parallel `MPLLB_*` groups.
- Supervisor overrides and ASIC inputs: `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `DEBUG`, `MPLLA_ASIC_IN_0` through `MPLLA_ASIC_IN_6`, `MPLLB_ASIC_IN_0` through `MPLLB_ASIC_IN_6`, DIV/HDMI clock ASIC inputs, `ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, and MPLL charge-pump ASIC input groups.
- Supervisor analog controls: `SUP_ANA_PRESCALER_CTRL`, `SUP_ANA_RTUNE_CTRL`, `SUP_ANA_BG1`, `SUP_ANA_BG2`, `SUP_ANA_SWITCH_PWR_MEAS`, `SUP_ANA_BG3`, `SUP_ANA_MPLLA_MISC1`, `SUP_ANA_MPLLA_MISC2`, `SUP_ANA_MPLLA_OVRD`, and the first line of `SUP_ANA_MPLLA_ATB1`.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior is created by AMD display code that includes this header, uses the matching offset header to select a register, and then applies these masks and shifts through register read/modify/write helpers.

The names in this chunk imply several hardware state machines and sequencing requirements:

- RX analog bring-up and calibration: AFE attenuation/VGA, CTLE boost, slicer control, IQ phase adjust, calibration MUX/DAC, scope capture, signal-detect thresholds, and VCO counter/status fields are typically programmed and then observed during receiver enablement or diagnostics.
- TX analog/DCC sequencing: TX DCC DAC, term-code, power override, equalization/measurement, and clock override fields expose low-level transmitter tuning surfaces that must align with link-rate and lane-power transitions.
- PCS/PMA lane handshakes: raw PCS/PMA override/input/output fields represent the boundary between digital control logic and PHY analog state. Request/ack, p-state, rate, loopback, and lane mode fields should be treated as ordered hardware handshakes, not plain memory bits.
- FSM control and observation: `FSM_FAST_*`, `FSM_STATUS_MON`, common calibration status, lock bits, DCC flags/status, OCLA, and TX EQ update flags represent calibration/adaptation state-machine checkpoints.
- Interrupt management: IRQ status, clear, and mask fields expose lane reset/request/rate/p-state/adaptation/phase-calibration/TX events. Consumers must distinguish status bits from write-one-clear or mask bits.
- MPLLA/MPLLB programming: CR2 fields configure reference clocks, divider clocks, HDMI clocks, SSC peak/step size, fractional-N enable, charge pump settings, standby/reset/calibration controls, and ASIC input mirrors. These values influence link-clock generation and must be programmed in a hardware-defined order.
- Analog supervisor support: prescaler, RTUNE, bandgap/reference, power-measurement switch, and analog PLL override fields affect common PHY support circuits shared by lanes.

There is no software persistence in this file. The macros persist only as compiled constants. Hardware state persists according to DPCS power, reset, and clock domains, and higher-level driver code must restore or reprogram those registers across GPU reset, display suspend/resume, link retraining, and hotplug paths.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor and the include guard defined near the top of the file. This chunk is part of the generated DPCS 4.2.2 register-description pair:

- `dpcs_4_2_2_offset.h` supplies `ixDPCSSYS_*` register offsets.
- `dpcs_4_2_2_sh_mask.h` supplies the field shifts and masks documented here.

The visible source-tree integration point is `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes both DPCS 4.2.2 headers and defines the `DPCS_BASE__INST0_SEG*` base segments. That resource file also expands DPCS register and mask/shift list macros for the DCN 3.1.5 resource table layer, so these generated constants feed the AMD display register table infrastructure rather than standalone code in this header.

Functional integration areas include:

- AMDGPU DCN display resource initialization for ASICs using DPCS 4.2.2.
- DisplayPort/HDMI PHY link-clock and lane bring-up code using CR indexed register access.
- Link training, lane adaptation, signal-integrity tuning, receiver calibration, and TX DCC/equalization routines.
- IRQ handling or diagnostics that inspect and clear raw lane events.
- Firmware, ATE, OCLA, and analog-test paths using raw PCS/PMA/FSM/ATB register views.

## Risks And Edge Cases

- Generated-register drift is the dominant risk. Incorrect masks or shifts can corrupt adjacent analog/PLL fields and cause link training failures, unstable clocks, or PHY calibration timeouts.
- This chunk is cut at non-register boundaries. Automated per-chunk counts must account for incomplete `RX_VCO_OVRD_OUT_2` and `MPLLA_ATB1` field pairs; a simple one-to-one shift/mask check inside only this range will report a false mismatch.
- Many field names expose overrides, raw views, ATE controls, OCLA hooks, or reserved bits. Those fields are sensitive and may only be valid in firmware-defined sequences, lab diagnostics, or ASIC bring-up flows.
- Status, clear, mask, request, acknowledge, enable, and override bits are adjacent in several families. Treating every macro as a plain writable configuration bit can accidentally clear events, mask interrupts, or fight hardware state machines.
- CR1 `LANEX` and `RAWLANEX` names are generic lane aliases. Callers must select the correct indexed lane/register aperture and cannot infer a fixed physical lane solely from the macro name.
- CR2 supervisor fields affect common PLL/support circuitry, including both MPLLA and MPLLB. Wrong programming can break multiple lanes or display links, not just one lane.
- Some comparable fields in nearby DPCS revisions use different literal formatting or naming case. Consumers should include the exact IP-version header chosen by the resource code instead of mixing definitions from `dpcs_4_2_0`, `dpcs_4_2_3`, or DCN umbrella headers.

## Test Signals

Useful validation signals are mostly build-time, generated-header, and hardware-integration oriented:

- Compile AMDGPU display code that includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`, especially `dcn315_resource.c`.
- Regenerate DPCS 4.2.2 headers from the source register database and diff this chunk for changed field names, shifts, and masks.
- Cross-check complete register groups outside the chunk boundary to ensure every field has the expected paired shift and mask; for this exact slice, expect 1,065 shifts and 1,083 masks because of boundary cuts.
- Run display bring-up, hotplug, suspend/resume, and GPU reset recovery tests on hardware using DCN 3.1.5/DPCS 4.2.2.
- Exercise DisplayPort and HDMI link-rate changes, link training, lane disable/enable, loopback, and PHY calibration paths; failures can indicate bad PLL, AFE/CTLE, DCC, p-state, or handshake masks.
- Check IRQ paths by provoking lane reset/request/rate/p-state/adaptation events and confirming status, clear, and mask bits behave as expected.
- Use hardware register readback or debug traces during PHY bring-up to confirm VCO, MPLL, RTUNE, bandgap, FSM lock/status, DCC status, and adaptation fields transition through expected values.

## Chunk Notes For Merge

The final per-file report should treat this source as a generated ASIC bitfield map, not handwritten driver logic. This chunk is centered on CR1 generic-lane low-level PHY controls and the start of CR2 supervisor PLL/common controls. Earlier and later chunks are needed to describe the full DPCS 4.2.2 register surface, especially the complete CR1 context before `RX_VCO_OVRD_OUT_2` and the continuation of CR2 after `SUP_ANA_MPLLA_ATB1`.

### subset-b-002356: lines 45340-47692

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 45340-47692

## Scope

This chunk is a generated AMD DPCS 4.2.2 register shift/mask header slice for `DPCSSYS_CR2`. It contains 2,145 `#define` constants covering 209 register-field groups from the tail of supervisor MPLLA analog definitions through supervisor MPLLB, common supervisor digital controls, lane 0 PHY/TX/RX debug and power controls, and the beginning of lane 1 PHY/TX/RX controls. The source file is guarded by `_dpcs_4_2_2_SH_MASK_HEADER` and is included by the DCN 3.1.5 resource code together with `dpcs_4_2_2_offset.h`.

The chunk starts mid-register at `DPCSSYS_CR2_SUP_ANA_MPLLA_ATB1` masks and ends mid-register after the first fields of `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`; neighboring chunks must provide the missing opening and closing fields when the full-file report is reconciled.

## Purpose

The header gives symbolic bit positions and bit masks for 16-bit DPCS PHY control/status registers. Driver code can combine the matching offset macro from `dpcs_4_2_2_offset.h` with a `*_SHIFT`/`*_MASK` pair from this file to build read-modify-write values without hard-coded bit literals. The represented hardware area is display PHY link support for CR2: PLL A/B setup, spread-spectrum and reset tuning, analog override outputs, lane-level ASIC override inputs/outputs, TX power-state programming, TX DCC DAC programming, RX status counters, and lane analog TX controls.

The macros are declarative. They do not allocate storage, execute code, or validate values. Correctness depends on consumers applying values within the mask width and writing only the hardware-defined bits.

## Important Definitions

The dominant pattern is:

- `REGISTER__FIELD__SHIFT`: low bit index for `FIELD`.
- `REGISTER__FIELD_MASK`: bit mask for `FIELD`, usually 16-bit wide and suffixed with `L`.
- `RESERVED_*` fields: hardware-reserved regions included so generated register layouts cover the full register width.

Major register families in this chunk:

- Supervisor analog MPLLA/MPLLB fields: `DPCSSYS_CR2_SUP_ANA_MPLLA_*` and `DPCSSYS_CR2_SUP_ANA_MPLLB_*` expose PLL analog test bus, charge pump, VREF, standby, lock calibration, bypass, divider, gearshift, and reserved control bits.
- Supervisor digital MPLL power control: `DPCSSYS_CR2_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR2_SUP_DIG_MPLLB_MPLL_PWR_CTL_*` cover override enables, FSM/status bits, DAC range, lock/stable timers, PCLK stable timers, calibration, analog DAC output, and SSC spread type.
- Supervisor clock/reset and termination tuning: `DPCSSYS_CR2_SUP_DIG_CLK_RST_*`, `DPCSSYS_CR2_SUP_DIG_RTUNE_*`, and `DPCSSYS_CR2_SUP_DIG_ANA_*` cover bandgap and reference power-up timing, VPHUD control, RTUNE configuration/status/set values, analog override outputs for MPLLA/MPLLB/RTUNE/bandgap/PMIX, and analog status bits.
- Lane 0 ASIC digital controls: `DPCSSYS_CR2_LANE0_DIG_ASIC_*` defines lane loopback, TX override input/output, RX override/status output, and raw ASIC input/output observations.
- Lane 0 TX power and diagnostics: `DPCSSYS_CR2_LANE0_DIG_TX_PWRCTL_*`, `DPCSSYS_CR2_LANE0_DIG_TX_CLK_ALIGN_*`, `DPCSSYS_CR2_LANE0_DIG_TX_LBERT_*`, and `DPCSSYS_CR2_LANE0_DIG_RX_STAT_*` define TX P-state bit recipes, power-up timing, DCC DAC bank/DAC handshakes, clock alignment, transmit LBERT, and RX statistic match/counter controls.
- Lane 0 analog TX fields: `DPCSSYS_CR2_LANE0_DIG_ANA_TX_*` and `DPCSSYS_CR2_LANE0_ANA_TX_*` expose digital-to-analog override outputs for TX enable/reset/rate, term code, equalization, DCC DAC, and raw analog override/test-bus fields.
- Lane 1 counterpart fields: `DPCSSYS_CR2_LANE1_DIG_ASIC_*`, `DPCSSYS_CR2_LANE1_DIG_TX_PWRCTL_*`, `DPCSSYS_CR2_LANE1_DIG_TX_CLK_ALIGN_*`, `DPCSSYS_CR2_LANE1_DIG_TX_LBERT_*`, and the beginning of `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_*` mirror lane 0 TX/ASIC controls while also including RX override input/equalization/CDR/VCO controls that were not present in this lane 0 slice.

## Control Flow

There is no runtime control flow in this header. Its effective flow is compile-time substitution:

1. DCN 3.1.5 resource code includes `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`.
2. Register helper code selects an `ix...` offset such as `ixDPCSSYS_CR2_LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0`.
3. The corresponding field macros are used to shift and mask a value, commonly through AMD display register helper macros.
4. Hardware observes the resulting MMIO/register transaction and updates PHY state or returns status.

Because this file is generated constants only, the logical state transitions live in hardware and in the calling driver code, not here. Still, the field names reveal state machines and handshakes: MPLL `FSM_STATE`/`MPLL_LOCK`, TX `REQ`/`TX_ACK`, RX `REQ`/`ACK`/`VALID`, DCC DAC `REQ`/`ACK`, status-counter `START`/`STOP`/`DONE`, and calibration result bits.

## State And Persistence

No software state is persisted by this chunk. Persistence is hardware register state:

- MPLLA/MPLLB power, reset, calibration, lock, standby, clock-enable, feedback-clock, divider, and gearshift fields persist until hardware reset or later register writes.
- TX P-state registers encode desired PHY behavior for P0, P0S, P1, and P2, including analog reference generation, VCM hold, clock enable, word clock enable, reset, serial enable, data enable, RX-detect allowance, VBOOST allowance, and DCC comparator calibration.
- Override registers can force hardware signals away from normal controller-generated values. These are particularly stateful because one bit commonly supplies a value and a paired `*_OVRD_EN` bit selects whether that value is active.
- Status and counter registers expose transient hardware observations such as lock, calibration, RX detection, sample counter completion, and statistic counters.

The mask constants are 32-bit C integer constants even though most represented registers are 16-bit. Reserved masks should be treated as do-not-write areas unless the consuming code is explicitly preserving readback values.

## Dependencies And Integration Points

This header depends on matching address/offset definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`. For this chunk, relevant offset ranges include supervisor registers around `0x0064` through `0x0096`, lane 0 registers around `0x1000` through `0x10ef`, and lane 1 registers beginning around `0x1100`.

`sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes this header for the DCN 3.1.5 resource implementation. The macros therefore integrate with the AMD display core register abstractions and DPCS base segment definitions used to access the PHY.

This file also has version siblings such as `dpcs_3_1_4_sh_mask.h`, `dpcs_4_2_0_sh_mask.h`, and `dpcs_4_2_3_sh_mask.h`. The field shapes are similar across versions, but masks can differ in formatting or reserved coverage. Consumers must use the DPCS version matching the ASIC resource table.

## Risks

- Header/offset skew: a field macro from `dpcs_4_2_2_sh_mask.h` must be paired with the corresponding `ix...` offset from `dpcs_4_2_2_offset.h`; mixing versions can write correct-looking bits to the wrong register.
- Reserved-bit writes: the generated `RESERVED_*_MASK` definitions make reserved regions visible. Code that writes whole-register literals instead of masked read-modify-write can toggle reserved hardware behavior.
- Override enable hazards: many lane and PLL fields use value plus override-enable pairs. Setting only the value bit has no effect; setting only override enable can force an unintended default value.
- Lane symmetry assumptions: lane 0 and lane 1 share many TX definitions, but this chunk shows lane 1 RX override/equalization/CDR fields and OCLA fields in the same range. Generic lane code must account for actual per-lane register availability and offsets.
- Chunk boundary risk: `DPCSSYS_CR2_SUP_ANA_MPLLA_ATB1` and `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S` are incomplete in this slice; any generated per-file summary must merge adjacent chunks before claiming complete field coverage.
- Value-width risk: callers must clamp values to `FIELD_MASK >> FIELD_SHIFT`; this header only defines the mask and cannot prevent overflow before shifting.

## Test Signals

Useful validation signals for changes involving this header:

- Compile coverage for AMDGPU DCN 3.1.5 paths, proving `dcn315_resource.c` and related register macros still include cleanly.
- Static comparison of every `DPCSSYS_CR2_*` register in this chunk against `dpcs_4_2_2_offset.h` to ensure each field group has a matching `ix...` offset where expected.
- Generator/regression diffs against upstream AMD register headers or internal XML output, with special attention to reserved masks and fields whose masks cross byte boundaries.
- Runtime display bring-up on DCN315 hardware: link training, DisplayPort/HDMI output enable, hotplug/RX detect, low-power P-state transitions, spread-spectrum clocking, and suspend/resume can expose bad PLL, TX P-state, or reset timing fields.
- Debugfs/MMIO register readback checks for DCC DAC handshakes, MPLL lock status, TX/RX acknowledge fields, and RX statistic counter completion after driver-triggered operations.

## Cross-Chunk Notes

The full-file reconciliation lane should combine this report with adjacent chunk reports before producing the per-file document. In particular, it should recover the missing start of `DPCSSYS_CR2_SUP_ANA_MPLLA_ATB1` before line 45340 and the remaining `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S` fields after line 47692, then continue through later lane 1 RX power, VCO calibration, RX CDR, raw lane, and CR3/CR4 register blocks.

### subset-b-002357: lines 47693-50047

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 47693-50047

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for the CR2 register instance. It contains only C preprocessor constants: `__SHIFT` macros define field bit positions and `_MASK` macros define the corresponding field masks. The range starts in the middle of `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`, covers the remainder of CR2 lane 1 RX power, VCO calibration, CDR/DPLL, RX adaptation, RX statistics, MPHY, digital analog override/status, and raw analog TX/RX controls, then enters CR2 lane 2 and covers its ASIC override/status interface, TX power control, TX clock/LBERT fields, RX power control, and the first RX VCO calibration/status registers. It ends in the middle of `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_RX_VCO_STAT_1`.

## Purpose

The header provides compile-time bitfield metadata used by AMDGPU display/PHY code when programming DPCS 4.2.2 hardware. Consumers pair these masks and shifts with matching address macros from the companion DPCS offset header and with AMD display register-access helpers to assemble read-modify-write values without open-coding numeric bit positions.

In this range, the fields describe:

- CR2 lane 1 RX power-state programming for P0S, P1, and P2, including analog AFE/clock/deserializer/CDR enables, VCO reset/calibration/continuous-calibration controls, digital clock enables, and RX power-up timing.
- CR2 lane 1 RX VCO calibration controls, calibration timing, and status, including frequency-tune start values, calibration step controls, skip bits, startup/update/counter timing, VCO FSM state, calibration-done status, and DPLL reset status.
- CR2 lane 1 RX alignment, LBERT, CDR, DPLL, adaptation, statistics, MPHY, digital analog override, and raw analog TX/RX bit layouts.
- CR2 lane 2 ASIC-facing override and status registers for lane, TX, RX, RX equalization, RX CDR/VCO, cross-lane clock/shift handshake, and OCLA debug enablement.
- CR2 lane 2 TX power-state and power-up timing fields, DCC CR-bank/DAC controls, TX clock alignment, TX LBERT, RX power-state controls, RX power-up timing, and the start of RX VCO calibration status.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or callable APIs in this chunk. The public interface is the generated macro naming contract:

- `DPCSSYS_CR2_LANE*_...__FIELD__SHIFT`: bit offset for `FIELD`.
- `DPCSSYS_CR2_LANE*_...__FIELD_MASK`: bit mask for the same field.
- Register delimiter comments such as `//DPCSSYS_CR2_LANE1_DIG_RX_ADPTCTL_ADPT_CFG_0` mark groups that correspond to address macros in `dpcs_4_2_2_offset.h`.

Notable CR2 lane 1 groups include:

- `DIG_RX_PWRCTL_*`: RX P-state enable fields and timing controls for AFE, clock regulator, analog clock, deserializer, CDR, VCO reset/calibration, continuous calibration, fast-start timing, rate timing, CDR-enable timing, deserializer enable/disable timing, and reserved-bit preservation.
- `DIG_RX_VCOCAL_*`: VCO calibration control, timing, and status registers, including `INT_GAIN_CAL_*`, `RX_VCO_OVRD_SEL`, `RX_VCO_FREQ_RST`, `RX_VCO_CAL_RST`, `RX_VCO_CONTCAL_EN`, `DPLL_CAL_UG`, `DTB_SEL`, frequency tune values, calibration skip bits, startup/update/counter timing, VCO FSM state, calibration done, and DPLL frequency reset status.
- `DIG_RX_CDR_*` and `DIG_RX_DPLL_*`: CDR enable/status, bias, phase, calibration, and DPLL frequency/bound fields that support receiver clock recovery.
- `DIG_RX_ADPTCTL_*`: adaptation configuration, training-pattern generator fields, enable masks for CTLE/VGA/ATT/DFE/eye/TGG logic, threshold and adaptation step controls, reset controls, ATT/VGA/CTLE/DFE status codes, slicer/DAC offsets, error slicer levels, DAC control selections, and adaptation CR-bank address/data fields.
- `DIG_RX_STAT_*`: statistic load values, data masks, CR1A/CR1B pattern/mask controls, statistic/correlation source selectors, sample/count enable bits, seven statistic counters, comparator clock controls, extended pattern controls, valid-loss clearing, stop control, and sample-done bits.
- `DIG_MPHY_*`: low-speed MPHY RX PWM, termination, and analog PWM clock stability fields.
- `DIG_ANA_*` and raw `ANA_*`: digital outputs toward analog TX/RX blocks, analog status readback, RX termination/signal-detect/DAC/slicer/IQ/phase controls, TX DCC DAC/equalization/fast-start/loopback controls, analog TX power/ATB/termination/misc fields, and analog RX clock/CDR/slicer/power/squelch/calibration/ATB/reserved registers.

Notable CR2 lane 2 groups include:

- `DIG_ASIC_*_OVRD_IN`, `DIG_ASIC_*_OVRD_OUT`, and `DIG_ASIC_*_ASIC_IN/OUT`: ASIC-side override enables and values for TX/RX requests, resets, data enables, P-state/rate/width, lane inversion/disable, RX CDR tracking and SSC, RX alignment, low-power detect, term controls, EQ fields, CDR/VCO load values, TX cursors, TX/RX acknowledgements, adaptation status, valid/data readback, cross-lane repeater/digital-clock/shift handshakes, and OCLA clock/data enablement.
- `DIG_TX_PWRCTL_*`: TX P0/P0S/P1/P2 enables for refgen, VCM hold, analog/digital clocks, reset, serial/data, RX-detect, VBOOST allowance, and DCC calibration; power-up timing; DCC CR-bank address/data; DCC DAC control/range/selection/ack/address; TX clock alignment; and TX LBERT control.
- `DIG_RX_PWRCTL_*` and `DIG_RX_VCOCAL_*`: lane 2 mirrors of the RX power-state, power-up timing, VCO calibration control/time/status fields seen for lane 1 earlier in this chunk.

## Control Flow

This header contributes no runtime control flow. Runtime sequencing lives in AMDGPU display and PHY code that uses these constants to read, mask, shift, and write indexed DPCS CR registers.

The implied hardware sequences in this chunk are sensitive PHY bring-up and diagnostic paths: RX P-state changes, CDR/VCO/DPLL setup, RX adaptation, statistic sampling, MPHY low-speed handling, analog override programming, lane 2 ASIC handshakes, TX power-state entry/exit, TX DCC programming, TX clock alignment, LBERT test enablement, and RX VCO calibration/status polling.

## State And Persistence

The macros are stateless compile-time constants. The mutable state they describe lives in volatile DPCS hardware registers. That state can be changed by display link training, modesets, hotplug handling, PHY reinitialization, suspend/resume, GPU reset recovery, power gating, and debug or validation tools. The many reserved masks are part of the hardware contract: callers should preserve reserved bits during read-modify-write operations unless a hardware sequence explicitly documents otherwise.

Some fields represent latched or sampled hardware status, such as TX/RX acknowledge bits, detect-RX results, valid bits, adaptation status, statistic/sample done bits, calibration done, VCO FSM state, analog status, and DCC acknowledgements. Other fields are override values or override enables; leaving override enables asserted after diagnostics can persistently redirect normal PHY control until the register is restored or reset.

## Dependencies

This chunk depends on the AMD ASIC register-generation pipeline remaining synchronized with the DPCS 4.2.2 hardware specification. It is normally consumed together with:

- `dpcs_4_2_2_offset.h`, which supplies the `ixDPCSSYS_CR2_LANE1_*` and `ixDPCSSYS_CR2_LANE2_*` register addresses for the field groups described here.
- AMDGPU display/DC register access helpers that combine address, mask, and shift constants for indexed DPCS CR MMIO operations.
- Display link training, PHY power management, receiver adaptation, CDR/VCO/DPLL calibration, diagnostic, and hardware bring-up code in the AMD GPU driver.

The file is part of an imported Linux GPU driver tree under this repository and has no direct dependency on Ceph filesystem logic.

## Integration Points

The definitions integrate with AMD display PHY initialization and runtime link management for the CR2 instance. Lane 1 content in this slice is mostly receiver-side control and analog PHY detail, including power sequencing, calibration, adaptation, statistics, MPHY, and raw analog control. Lane 2 content begins with the ASIC-facing digital interface and then covers TX/RX power and early RX VCO calibration.

Correct integration requires pairing lane-specific masks with the matching lane-specific register addresses. A `DPCSSYS_CR2_LANE2_*` field must not be applied to a lane 1 or different CR instance address, even when field names and masks look identical. ASIC-version specificity also matters: these layouts are for `dpcs_4_2_2` and should not be mixed with neighboring DPCS versions without explicit hardware gating.

## Risks

- The range starts in the middle of `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`; the preceding chunk is required for that register's full field list.
- The range ends in the middle of `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_RX_VCO_STAT_1`; the following chunk is required for the rest of that status register.
- Generated mask/shift mistakes would compile cleanly but can silently program the wrong PHY bit.
- Many fields are sequencing-sensitive. Incorrect RX P-state, VCO/CDR/DPLL, adaptation, TX power, DCC, clock-alignment, or analog override writes can cause link-training failures, display blanking, intermittent high-rate instability, or misleading diagnostic readings.
- Reserved fields must be preserved. Accidentally writing reserved bits in 16-bit DPCS CR registers can change undocumented hardware behavior.
- Override fields usually have separate value and enable bits. Setting values without enables may do nothing; leaving enables asserted after a debug path can block normal ASIC control.
- Repetitive lane 1/lane 2 naming makes copy-paste errors likely in consumers, especially where lane 2 mirrors lane 1 field layouts but uses different address groups.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`.
- Static checks that each field has a matching `__SHIFT` and `_MASK`, masks match their shifts and widths, and DPCS CR fields stay within the expected 16-bit register shape unless hardware documentation says otherwise.
- Display bring-up on hardware using DPCS 4.2.2, including boot display, hotplug, modesets, suspend/resume, GPU reset recovery, and multi-monitor operation.
- Link-training stress across lane counts and link rates, with attention to CR2 lane 1 RX adaptation/statistic paths and CR2 lane 2 TX/RX power and calibration paths.
- PHY diagnostics that exercise TX/RX LBERT, DCC DAC programming and acknowledgement, RX VCO/CDR/DPLL status polling, adaptation status readback, statistic counters, MPHY low-speed controls, analog override/status readback, and cross-lane clock/shift handshakes.

### subset-b-002358: lines 50048-52416

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 50048-52416

## Purpose

This chunk is part of AMDGPU Display Core's generated DPCS 4.2.2 shift/mask header. It defines C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCSSYS CR2 PHY registers. The register addresses live in the companion `dpcs_4_2_2_offset.h`; this file supplies the field layout needed by register helper macros to extract or update individual hardware fields.

The line range starts in the middle of `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_RX_VCO_STAT_1` and ends after only the first field of `DPCSSYS_CR2_RAWCMN_DIG_CMN_CTL_1`, so the chunk is a partial slice of a larger generated header. Within the slice, the dominant coverage is CR2 lane 2 RX/analog controls, CR2 lane 3 digital/analog TX controls, and CR2 raw-common MPLL controls.

## Register Groups Covered

- Lane 2 RX calibration and clock recovery: VCO status, XAUI comma mask, LBERT control/error counters, CDR controls and status, DPLL frequency and frequency bounds.
- Lane 2 adaptive receiver tuning: `ADPTCTL_ADPT_CFG_0` through `_9`, reset configuration, ATT/VGA/CTLE/DFE tap status, slicer levels, DAC selector registers, CR bank address/data, and RX statistic/match/counter registers.
- Lane 2 MPHY and analog bridge controls: MPHY RX PWM/termination, digital-to-analog TX/RX override outputs, RX VCO override outputs, RX AFE/CTLE/scope/slicer controls, analog status, signal-detect overrides, TX DCC DAC overrides, and direct lane 2 analog TX/RX registers.
- Lane 3 ASIC lane and TX controls: lane override input, ASIC TX override inputs/outputs, ASIC TX/RX status outputs, TX power states `P0`, `P0S`, `P1`, `P2`, power-up timing, DCC DAC control, TX clock alignment, and TX LBERT.
- Lane 3 RX statistic monitor and analog TX controls: RX match/statistic counters plus digital analog TX override/status registers and direct lane 3 analog TX registers.
- CR2 raw common controls: `PHY_FUNC_RST`, MPLLA/MPLLB clock divider and bandwidth override inputs, MPLLA/MPLLB SSC override controls, lane FSM extension bit, MPLLA/MPLLB fractional-N SSC controls, and the first `MPLLA_INIT_CAL_DISABLE_OVRD_VAL` field of `RAWCMN_DIG_CMN_CTL_1`.

## Important APIs, Types, and Macros

There are no functions, structs, or runtime data structures in this chunk. Its API surface is the generated macro namespace:

- `DPCSSYS_CR2_<register>__<field>__SHIFT` gives the low bit index of a hardware field.
- `DPCSSYS_CR2_<register>__<field>_MASK` gives the already-shifted mask for that field.
- Fields are generally 16-bit CR register layouts, with many masks expressed as `0x0000....L`. Some adjacent ASIC register headers use shorter 16-bit spellings for equivalent masks; this 4.2.2 header consistently emits widened 32-bit constants for this area.
- Companion address macros such as `ixDPCSSYS_CR2_LANE2_DIG_RX_CDR_CDR_CTL_0` and `ixDPCSSYS_CR2_RAWCMN_DIG_MPLLA_OVRD_IN` are in `dpcs_4_2_2_offset.h`. The shift/mask macros are meaningful only when paired with the corresponding offset macro.

Notable fields include receiver adaptation enables (`CTLE_EN`, `VGA_EN`, `ATT_EN`, `DFE_EN`, `TGG_EN`), calibration completion/status (`RX_VCO_CAL_DONE`, `VCOCLK_TOO_FAST`, `RX_VCO_CORRECT`, `RX_VCO_UP`), TX power-state enables/resets/data enables, analog override enable/value pairs, MPLL divider/SSC/frac-N override enable/value pairs, and RX statistics comparator configuration (`PTTRN_*`, `DATA_MSK_*`, `STAT_CNT_*`).

## Control Flow

The header has no executable control flow. Control flow is indirect:

1. DCN resource code includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h` for DCN 3.1.5 resource construction.
2. Display Core register tables and helper macros bind register offsets, shifts, and masks into encoder/resource structures.
3. Runtime link encoder and PHY code writes or reads hardware registers through those tables; the macros from this file determine which bits are touched.

The direct include point found for this ASIC revision is `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes both DPCS 4.2.2 offset and shift/mask headers. More generic DPCS field lists are declared in `dcn20_link_encoder.h` and `dcn201_link_encoder.h`, but this chunk mostly covers lower-level PHY CR fields that are not referenced by their full generated names in ordinary C code.

## State and Persistence

The macros themselves are compile-time constants and do not persist state. The state they describe lives in GPU display PHY hardware registers:

- Status fields expose current hardware state, such as VCO calibration results, CDR gain values, RX adaptation tap values, analog status bits, TX calibration status, and RX statistic counters.
- Control and override fields can persist in hardware until reset, power-gate transitions, driver reprogramming, or firmware/BIOS ownership changes.
- Many fields are paired as override value plus override enable. Programming the value without the enable bit, or leaving an enable bit asserted after a diagnostic operation, can leave hardware in a forced state instead of autonomous PHY control.
- The CR2 raw-common MPLL fields affect shared PLL behavior for the CR2 DPCS instance, so their state can influence multiple lanes rather than a single lane-local datapath.

## Dependencies and Integration Points

- Depends on the generated DPCS register offset header for the matching ASIC revision: `dpcs_4_2_2_offset.h`.
- Integrated into AMDGPU Display Core through DCN 3.1.5 resource setup, where DPCS base addresses and DPCS shift/mask definitions are selected for the ASIC.
- Consumed by AMD display register helper macros that combine offset, mask, and shift definitions. A field rename or mask change can break build-time macro expansion even if no direct textual reference to a full generated macro name exists.
- Mirrors similar DPCS headers for nearby revisions (`dpcs_4_2_0`, `dpcs_4_2_3`, `dpcs_3_1_4`) and DCN aggregate headers. These are useful comparison points when validating generated register database changes, but revision-specific differences must not be manually normalized without hardware confirmation.

## Risks

- Bitfield drift is high impact: an incorrect shift or mask can silently write the wrong hardware bit, affecting link training, PLL setup, RX adaptation, signal detect, or lane power sequencing.
- Partial-register writes must preserve reserved bits. This chunk contains many `RESERVED_*` masks, which signal fields that should generally be left untouched by driver code.
- Lane and instance naming is easy to confuse. This slice mixes CR2 lane 2, CR2 lane 3, and CR2 raw-common registers; copying a field between lanes or CR instances can target the wrong PHY path.
- Override enable/value pairs are risky during diagnostics and bring-up. Incorrectly asserting override enables for MPLL, TX, RX, DCC, VCO, or signal-detect controls can mask firmware defaults or hardware state machines.
- The chunk boundary is incomplete. Research or regeneration work using only this slice must not conclude that `RAWCMN_DIG_CMN_CTL_1` has only one field; its remaining fields appear after the requested end line.

## Test Signals

- Build coverage: compile AMDGPU Display Core for the DCN 3.1.5 configuration that includes `dpcs_4_2_2_sh_mask.h`; macro spelling and field-list mismatches should surface as compiler errors.
- Register database validation: compare this header against its matching offset header and generated source database to ensure every field belongs to the intended register and every mask matches the declared shift/width.
- Link training and display smoke tests: DisplayPort/HDMI bring-up across all CR2 lanes, including lane 2 and lane 3, is the main behavioral signal for bad TX power, PLL, RX, or analog field definitions.
- Hardware diagnostics: readback of VCO calibration status, CDR status, RX adaptation status, RX statistic counters, MPLL override/status, and SRAM/init/common reset fields can indicate whether the masks decode expected values.
- Regression comparison: when updating generated headers, diff against neighboring ASIC revisions only as a sanity check; identical names with changed mask spellings may be expected, while changed bit positions require hardware-register-source confirmation.

### subset-b-002359: lines 52417-54805

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 52417-54805

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for the `DPCSSYS_CR2` register block. It covers 2,389 source lines and defines 2,105 preprocessor constants: 1,053 `__SHIFT` macros and 1,052 `_MASK` macros. The count mismatch is from the chunk boundaries: it starts after the first field of `DPCSSYS_CR2_RAWCMN_DIG_CMN_CTL_1` and ends before the final two masks of `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN`.

The content is declarative only. It contains no functions, structs, enums, branches, loops, runtime variables, allocation, locking, or file-backed persistence code. Its public surface is a large set of C preprocessor constants that describe bit positions and bit masks, mostly for 16-bit internal DPCS registers.

## Purpose

The header gives AMDGPU display code symbolic names for DPCS 4.2.2 hardware register fields. Driver code can combine these `*_SHIFT` and `*_MASK` constants with companion address macros from `dpcs_4_2_2_offset.h` and AMD register access helpers to perform read-modify-write operations without hard-coding bit locations.

This slice covers the CR2 raw common area, all CR2 raw lane 0 groups, and the beginning of CR2 raw lane 1. The common area describes MPLL state, TX calibration, SRAM initialization, OCLA/debug, supervisor analog overrides, PCS/FW IDs, always-on RTUNE values, SRAM bitline configuration, power-gating and supervisor overrides, VREF/resistor status, and reference-range/misc configuration. The lane area describes PCS/PMA crossbar overrides, finite-state-machine monitors and fast-sequence controls, IRQ status/clear/mask fields, TX/RX control fields, ATE override windows, and the start of the same PCS crossbar namespace for lane 1.

## Exported API Surface

There are no callable APIs or local types. The exported interface is the generated macro namespace. Most complete fields appear as a pair:

- `DPCSSYS_CR2_*__FIELD__SHIFT` gives the bit offset.
- `DPCSSYS_CR2_*__FIELD_MASK` gives the field mask.

Important macro families in this range:

- `DPCSSYS_CR2_RAWCMN_DIG_*`: CR2 common digital controls for MPLL state and bank selection, TX calibration code, SRAM initialization status, OCLA probe/clock controls, supervisor analog overrides, raw PCS and firmware identification, AON RTUNE RX/TX up/down values for indices 0 through 7, SRAM bitline read/write selection, AON power-gating and supervisor override inputs/outputs, VREF statistics, resistor override/readback fields, reference range override, and miscellaneous common configuration.
- `DPCSSYS_CR2_RAWLANE0_DIG_PCS_XF_*`: lane 0 PCS crossbar TX/RX override and status fields. These include TX/RX pstate, LPD, width, rate, MPLL selection and enable, master MPLL state override, reset/request override, DETRX, VBOOST/IBOOST, beacon, TX/RX acknowledge, RX adaptation request/disable/ack/FOM, RX data enable, loopback, LOS/LFPS, VCO/ref load, RX EQ and IQ delta overrides, TX/RX termination controls, lane number, reserved slots, ATE controls, TX pre/main/post direction hints, phase-2 calibration, and extended TX/RX valid/data override fields.
- `DPCSSYS_CR2_RAWLANE0_DIG_FSM_*`: lane 0 FSM override, memory-address/status monitors, fast RX startup/adaptation/AFE/DFE/bypass/reference-level/IQ calibration controls, fast supervisor and TX common-mode/RX detect controls, RX power-up/VCO wait/VCO calibration sequencing, common calibration status, continuous calibration/adaptation/data/phase/AFE controls, flags, CR lock, TX DCC flags/status, OCLA, TX EQ update flag, RCAL status, and RX IQ phase offset readback.
- `DPCSSYS_CR2_RAWLANE0_DIG_IRQ_CTL_*`: lane 0 interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation request/adaptation disable, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX serial loopback enable, DCC on-demand, TX reset, and TX request.
- `DPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_*`: lane 0 PMA crossbar fields for lane override in/out, supervisor override and PMA input, TX/RX PMA override outputs and inputs, lane RTUNE request/acknowledge, MPHY PWM/termination override inputs, MPHY output controls, and RX adaptation override output.
- `DPCSSYS_CR2_RAWLANE0_DIG_TX_CTL_*` and `DPCSSYS_CR2_RAWLANE0_DIG_RX_CTL_*`: lane 0 TX/RX controller controls for FSM timing, TX clock selection and enable, TX DCC continuous status, OCLA/UPCS debug enables, RX FSM enable and rate-change-in-P1 behavior, RX LOS masking, RX data-enable override counters, off-cancel/adaptation continuous status, and RX UPCS OCLA data/clock enables.
- `DPCSSYS_CR2_RAWLANE0_DIG_PCS_XF_ATE_*`: lane 0 ATE RX/TX override controls for rate, width, pstate, low-power detect, parallel/serial loopback, DETRX, VBOOST, IBOOST, TX beacon, TX async data, master MPLL loop, RX LOS/LFPS/adaptation continuous controls, VCO/ref load overrides, RX valid override, and extra TX data/async overrides.
- `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_*`, `FSM_*`, `IRQ_CTL_*`, `PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and `PCS_XF_ATE_*`: the start of the same lane register pattern for lane 1. This chunk covers lane 1 from PCS crossbar TX/RX override/status through FSM, IRQ, PMA, TX/RX control, ATE RX override, and most of ATE TX override.

## Register Areas Covered

The raw common group maps CR2-wide PHY controls and observability. The MPLL state register exposes off/force-on timing, A/B state selection, state override output enable, and bank selection. Common override registers expose calibration-disable, RTUNE request, HDMI mode, TX PWM clock selection/enable, supervisor analog override, power-gating, VREF/resistance, and reference-range control. The repeated AON RTUNE registers provide per-index RX, TX down, and TX up tuning values used by always-on common calibration logic.

The raw lane PCS crossbar groups map low-level signals between PCS-side lane logic and the surrounding PHY. TX fields cover pstate, low-power detect, width, rate, MPLL selection/enable, resets, requests, DETRX, VBOOST/IBOOST, beacon, async enable/data, TX acknowledgements, serial loopback, TX data enable, and master MPLL loop state. RX fields cover rate/width/pstate/LPD, adaptation request/disable/ack/FOM, RX data enable, loopback, LOS/LFPS thresholding, VCO/ref load, RX valid, RX EQ/IQ/phase calibration, and TX EQ direction feedback.

The raw lane FSM group describes internal sequencing and debug state. It exposes override control, micro-sequencer memory/status monitors, fast-path controls for RX startup and multiple calibration/adaptation phases, common calibration status for MPLL/RCAL, continuous RX calibration/adaptation stages, CR lock, TX DCC flags/status, OCLA debug selection, TX EQ update, and RX IQ phase offset.

The raw lane IRQ group provides per-event status, clear, and mask fields. It covers RX reset/request/rate/pstate/adaptation events, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX serial loopback, DCC on-demand, TX reset, and TX request. The presence of separate `*_IRQ`, `*_IRQ_CLR`, and `IRQ_MASK` groups means consumers must use the hardware-defined status/clear/mask semantics rather than treating these as ordinary persistent configuration bits.

The PMA, TX_CTL, RX_CTL, and ATE groups expose lower-level bring-up, debug, and manufacturing controls. PMA crossbar fields map supervisor, TX, RX, RTUNE, and MPHY signals. TX/RX controller fields tune FSM timing, clocking, continuous DCC/adaptation/off-cancel status, LOS/data-enable counters, and OCLA capture. ATE fields provide forced values and override enables for link mode, loopback, RX detect, TX boost, beacon, async data, LOS/LFPS, adaptation continuation, VCO/ref load, and RX valid behavior.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior comes from AMDGPU display code that selects these masks and from the DPCS hardware state machines that consume or expose the underlying register bits.

The field names imply several hardware state patterns:

- Request/acknowledge handshakes: `REQ`, `RESET`, `ACK`, `TX_ACK`, `RX_ACK`, `RTUNE_REQ`, `RTUNE_ACK`, `ADAPT_REQ`, and `ADAPT_ACK` fields represent hardware state-machine transitions and their observed completion signals.
- Override gating: many fields appear as adjacent value and enable pairs such as `*_OVRD_VAL` with `*_OVRD_EN`. The value field is meaningful only when the matching override enable is asserted.
- Link mode and power transitions: `PSTATE`, `RATE`, `WIDTH`, `LPD`, `DATA_EN`, `MPLLB_SEL`, `MPLL_EN`, reset/return requests, clock selection, LOS masks, and power-gating fields encode lane bring-up, low-power entry/exit, and rate/lane-width changes.
- Calibration and adaptation: RTUNE values, VREF/resistor controls, VCO/ref load overrides, RX AFE/DFE/IQ/reference-level/phase calibration controls, CR lock, TX DCC status, TX EQ update, RX adaptation status/FOM, and RX EQ delta fields expose calibration commands and readbacks.
- Debug, validation, and manufacturing paths: OCLA, ATE, FSM memory/status monitors, IRQ masks/clears, loopback, MPHY PWM/termination, raw ID/FW ID, reserved slots, and raw PCS/PMA crossbar registers provide observability or forced settings that can bypass normal hardware sequencing.

No software state is persisted here. Hardware register contents persist only according to ASIC reset, power-domain, firmware, and display-engine sequencing. Reserved masks are explicitly present and should be preserved by read-modify-write users.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is the DPCS 4.2.2 register database that generated this file and the companion `dpcs_4_2_2_offset.h` address map.

Within this source tree, `dpcs_4_2_2_sh_mask.h` is included by `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` together with `dpcs_4_2_2_offset.h`. The offset header maps the common CR2 raw registers around internal addresses `0x200b` onward in this slice, raw lane 0 PCS/FSM/IRQ/PMA/TX/RX/ATE groups from `0x3000` through the `0x30c*` extended fields, and lane 1 groups beginning at `0x3100`.

Integration points visible from the names include AMD DCN 3.15 display resource initialization, low-level DisplayPort/HDMI PHY programming, link training and rate/lane-width changes, TX/RX request-ack sequencing, power management and suspend/resume restore paths, RTUNE/VREF/resistor calibration, RX adaptation/equalization, TX DCC and TX EQ handling, hotplug/link recovery diagnostics, interrupt masking and clearing, OCLA debug capture, ATE/manufacturing override flows, and low-level PCS/PMA/MPHY diagnostics.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently target an adjacent hardware field during a register update.
- The slice starts and ends inside logical register groups. Merge/reconciliation should not treat `DPCSSYS_CR2_RAWCMN_DIG_CMN_CTL_1` or `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN` as fully described by this chunk alone.
- Many override value bits sit next to override-enable bits. Setting the value without the enable has no intended effect; leaving an enable asserted after debug, ATE, or recovery use can force hardware away from normal state-machine control.
- Calibration-sensitive fields such as RTUNE, VREF, resistor override, VCO/ref load, RX adaptation, RX IQ/phase calibration, TX DCC, TX EQ, and MPLL state/bank selection can destabilize link training or signal integrity if stale or misprogrammed.
- IRQ clear and mask fields are represented only as bit positions and masks; the header does not encode access semantics such as write-one-to-clear or read side effects.
- Reserved fields cover large bit ranges. Drivers should preserve reserved bits and avoid treating them as writable scratch space.
- Lane 0 and lane 1 groups are near-identical but have distinct address ranges. Copying a lane 0 register address or macro into a lane 1 path, or vice versa, can affect the wrong physical lane.
- Diagnostic, ATE, loopback, MPHY, and raw crossbar controls can interfere with normal display operation, hotplug handling, and power sequencing if used outside controlled bring-up or validation paths.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile/preprocess AMDGPU DCN 3.15 code that includes `dpcs_4_2_2_sh_mask.h` through `dcn315_resource.c`.
- Static checks that every complete register group has matching `__SHIFT` and `_MASK` definitions; for this sliced chunk, expect 1,053 shifts and 1,052 masks because the selected lines cross group boundaries.
- Consistency checks against `dpcs_4_2_2_offset.h` so every complete register-family prefix in this chunk has a corresponding `ixDPCSSYS_CR2_*` address define.
- Generated-register comparison against adjacent DPCS versions such as 4.2.0 and 4.2.3 to catch accidental field-width, reserved-bit, suffix, or mask-format changes.
- Runtime display tests on hardware using DPCS 4.2.2: DisplayPort and HDMI link training, lane-count/rate changes, hotplug, suspend/resume, low-power entry/exit, TX/RX request-ack transitions, RTUNE/VREF/resistor calibration, RX adaptation/equalization, TX DCC, TX EQ, VCO/ref load behavior, interrupt status/clear/mask behavior, and link recovery.
- Debug/validation readbacks should show plausible transitions for common MPLL state, SRAM init, RTUNE values, power-gating overrides, PCS TX/RX acknowledgements, FSM status monitors, calibration flags, CR lock, TX DCC status, IRQ masks/clears, PMA RTUNE acknowledge, MPHY override outputs, TX/RX controller status, ATE override readback, and lane 0 versus lane 1 addressing.

## Chunk Notes For Merge

This document intentionally covers only lines 52417-54805 of `dpcs_4_2_2_sh_mask.h`. Earlier chunks should complete the beginning of `DPCSSYS_CR2_RAWCMN_DIG_CMN_CTL_1` and preceding MPLL/SSC common registers. Later chunks should complete the remaining masks for `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN` and continue lane 1 register families. The final merged per-file report should describe the whole file as a generated ASIC bitfield map for DPCS 4.2.2 rather than handwritten driver logic, with `dcn315_resource.c` and `dpcs_4_2_2_offset.h` as primary in-tree integration anchors.

### subset-b-002360: lines 54806-57191

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 54806-57191

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It contains preprocessor constants only: `__SHIFT` and `_MASK` definitions for 16-bit DPCS control-register fields under the `DPCSSYS_CR2` indirect register namespace. There are no C functions, structs, enums, branches, allocations, locks, or software persistence paths in this range.

The slice starts at the final two mask definitions for `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN`, covers the remaining RAWLANE1 PCS ATE/override masks, then contains full repeated RAWLANE2 and RAWLANE3 digital PCS, FSM, IRQ, PMA, TX-control, and RX-control field layouts. It ends at the first shift definition for `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_ADPT_ATT`, after starting the RAWAONLANE0 always-on analog calibration/readback field group.

I counted 2,105 macro definitions in the assigned range: 1,052 shift macros and 1,053 mask macros. The one-extra mask count comes from the slice starting after the matching shifts for `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN`.

## Purpose

The header gives AMD display driver code symbolic bit positions and masks for DPCS 4.2.2 CR2 raw-lane registers. Companion offset headers identify the indirect CR register addresses, while this shift/mask header defines how callers extract or update individual fields after selecting a register through the DPCS CR address/data access path.

The hardware domains represented here are low-level display PHY and lane-control surfaces:

- PCS crossbar and override fields for TX/RX reset, request, power state, lane power-down, width, rate, MPLL selection, MPLL state, data-enable, async, beacon, loopback, detect-RX, voltage/current boost, RX loss-of-signal threshold, adaptation requests, and calibration continuations.
- Lane FSM monitor and fast-calibration controls/status bits for RX startup, AFE/DFE/bypass/reference-level/IQ/VCO calibration, continuous adaptation, common MPLL/RCAL status, CR register/memory locks, OCLA debug capture, TX DCC status, and TX EQ update flags.
- Per-lane IRQ status, clear, and mask fields for RX/TX reset and request events, RX rate and power-state changes, RX adaptation request/disable, RX phase-2 calibration request/disable, lane transceiver mode, serial loopback, and DCC on-demand events.
- PMA interface override/input/output fields for lane/supervisor MPLL state, TX/RX request/reset/data enables, async/beacon controls, PMA PWM and termination control, RX IQ phase-adjust map override, RTUNE request/ack, and PCS/PMA acknowledgement handshakes.
- TX and RX controller fields for FSM enable, wait timing, clock select/enable, async beacon wait, DCC continuous status, LOS mask, RX data-enable override, off-canonical/continuous adaptation status, and UPCS/OCLA debug enables.
- Always-on lane 0 analog calibration/readback masks for AFE/CTLE/DFE IDAC/VDAC offsets, RX adaptation figure-of-merit and IQ/phase values, MPLLA/MPLLB coarse tune, and initialization power-up done flags.

## Important API Surface

The exported API is the macro namespace. The macros are intended to be paired with register offsets such as `ixDPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_TX_OVRD_IN` from the matching DPCS offset header and with AMD register helper patterns that use `REG_GET`, `REG_SET`, `REG_UPDATE`, or table-generated equivalents.

Important field families in this chunk include:

- `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_*` tail coverage: ATE TX override masks for async enable, TX override input 1 fields for `DETRX_REQ`, `VBOOST_EN`, `IBOOST_LVL`, `TX_BEACON_EN`, serial loopback, and async data; master MPLL loop bits; ATE RX override fields for LOS LFPS/threshold, adaptation request, continuous adaptation, off-canonical continuation, VCO/reference load overrides, RX valid override, and TX async/data override input 2.
- `DPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_*`: complete lane 2 PCS TX/RX override and observed PCS input/output fields. Representative fields include `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, `OVRD_EN`, `MSTR_MPLLA_STATE`, `MSTR_MPLLB_STATE`, reset/request overrides, `ACK`, `DETRX_RESULT`, RX adaptation controls, RX VCO/reference load overrides, TX pre/main/post cursor direction registers, lane number, ATE overrides, RX EQ delta/IQ and PH2 calibration, and TX/RX termination control.
- `DPCSSYS_CR2_RAWLANE2_DIG_FSM_*`: lane 2 FSM override, memory/status monitor, fast calibration indicators, continuous calibration/adaptation indicators, `FAST_FLAGS`, CR lock bits, TX DCC flags/status, OCLA capture enables, TX EQ update flag, common MPLL/RCAL init/done flags, and RX IQ phase offset.
- `DPCSSYS_CR2_RAWLANE2_DIG_IRQ_CTL_*`: lane 2 IRQ status registers, corresponding clear registers, `IRQ_MASK` and `IRQ_MASK_2`, and event-specific fields for RX reset/request/rate/pstate/adaptation/PH2 calibration, lane transceiver mode, RX-to-TX serial loopback, DCC on-demand, TX reset, and TX request.
- `DPCSSYS_CR2_RAWLANE2_DIG_PMA_XF_*`: lane 2 PMA lane/supervisor/TX/RX override outputs and PMA inputs, RTUNE control, MPHY PWM/termination override in/out, and RX adaptation override output.
- `DPCSSYS_CR2_RAWLANE2_DIG_TX_CTL_*` and `DPCSSYS_CR2_RAWLANE2_DIG_RX_CTL_*`: lane-local TX/RX controller masks for FSM control, clock control, DCC continuous status, OCLA/UPCS OCLA, LOS masking, RX data-enable override, and adaptation/off-canonical continuous status.
- `DPCSSYS_CR2_RAWLANE3_DIG_*`: the same PCS/FSM/IRQ/PMA/TX/RX control surface repeated for raw lane 3. The lane 3 field names mirror lane 2, which makes generated-name parity a key correctness property.
- `DPCSSYS_CR2_RAWAONLANE0_DIG_*`: always-on lane 0 calibration and status masks for AFE/CTLE IDAC offset, RX adaptation IQ and FOM, DFE summer/phase/data/bypass/error VDAC offsets, even/odd reference levels, phase-adjust linear/map values, MPLLA/MPLLB coarse tune, and `INIT_PWRUP_DONE`/`PH2_PWRUP_DONE`.

Most field layouts are 16-bit wide. Many registers follow a simple paired pattern of value bit plus override-enable bit, while multi-bit fields use contiguous masks such as `PSTATE_MASK 0x00000003L`, `RATE_MASK 0x000000E0L`, `IBOOST_LVL_OVRD_VAL_MASK 0x00000F00L`, `VCO_LD_VAL_OVRD_MASK 0x00001FFFL`, `RX_PMA_TERM_CTL_R_MASK 0x000000C0L`, or 8-bit calibration `data_MASK 0x000000FFL`.

## Control Flow

This header has no executable control flow. The implied control flow exists in driver register access code:

1. Driver code selects an indirect CR2 register offset from the companion DPCS offset header.
2. It reads or writes that register through the DPCS CR address/data access window for the relevant instance.
3. It uses this header's `__SHIFT` and `_MASK` macros to pack field values into the register word or extract status fields from it.
4. Hardware lane state machines, PCS/PMA bridges, IRQ latches, PLL supervisors, adaptation engines, and analog calibration circuits perform the real state transitions.

The repeated RAWLANE2/RAWLANE3 layout means higher-level code can use per-lane tables or generated macros with consistent field semantics across lanes. The slice also shows boundary continuity: lane 1 tail fields precede lane 2, lane 3 repeats lane 2, and RAWAONLANE0 begins immediately after lane 3 ATE tail registers.

## State And Persistence

The file stores no runtime state. Its constants describe hardware-backed state and control bits:

- Override registers can force or bypass normal lane state machine behavior for reset, request, power state, MPLL selection/state, data-enable, async data, beacon, loopback, RX LOS, VCO/reference load, TX/RX termination, PMA PWM, and RX IQ phase mapping.
- Status and monitor fields expose transient hardware state such as ACK, RX valid, RX adaptation FOM, calibration flags, MPLL/RCAL init/done, TX DCC status, TX EQ update, CR lock state, RTUNE ack, and power-up done.
- IRQ status/clear/mask registers can persist event latches or mask decisions in hardware until explicitly cleared, overwritten, or reset by display power-management flows.
- Always-on lane calibration readbacks represent physical calibration values that may survive lane-level power changes but are still hardware-local, not file-backed software state.

Incorrect writes using these masks can leave a lane forced into reset, request, test/ATE, loopback, disabled data, altered calibration, masked IRQ, or wrong MPLL/termination state until the display driver reinitializes the block or the ASIC resets.

## Dependencies And Integration Points

This generated header depends only on the C preprocessor, but it must stay synchronized with several generated and handwritten layers:

- The matching `dpcs_4_2_2_offset.h` register-address macros for `ixDPCSSYS_CR2_RAWLANE{1,2,3}_...` and `ixDPCSSYS_CR2_RAWAONLANE0_...`.
- AMD display register helper macros and generated register-table code that combine offsets, shifts, and masks.
- DPCS/RDPCS/HPO DisplayPort link encoder paths that program lane reset/request/rate/width/power-state, MPLL selection, TX/RX enables, equalization, link training, and PHY diagnostic state.
- PHY initialization and power-management logic that uses FSM, PMA, TX_CTL, RX_CTL, IRQ_CTL, and ATE/test fields when bringing links up, retraining, entering low-power states, or collecting debug status.
- ASIC-generation comparison headers such as DPCS 4.2.0, 4.2.3, 3.1.4, and DCN 4.1.0 shift/mask headers. Similar names appear across generations, but mask formatting and exact field widths can differ, so consumers must include the correct ASIC header.

## Risks

- Generated mask/shift drift is the main risk. A single incorrect bit position in reset, request, PLL, data-enable, IRQ clear, or calibration fields can break link bring-up in a lane-specific way.
- RAWLANE2 and RAWLANE3 are large repeated blocks. Copy-generation errors are easy to miss because neighboring lanes may still work.
- This chunk starts and ends mid-register group. File-level reconciliation must preserve context from adjacent chunks before deciding whether a register family is complete.
- Override-enable fields are hazardous because setting an override value without the intended enable bit, or leaving an enable bit set after test/debug use, can make hardware ignore normal PCS/PMA/FSM control.
- IRQ status/clear/mask families use very similar names. Mixing status, clear, and mask macros can silently lose interrupts, create interrupt storms, or hide adaptation/reset events.
- Reserved masks occupy many upper bits. Code should preserve reserved bits unless hardware documentation explicitly permits writes.
- Always-on calibration fields often use generic `data` names. Misinterpreting signedness, lane ownership, or calibration units can cause bad diagnostics or incorrect tuning decisions.
- Several fields are test/ATE or OCLA oriented. Exposing them through normal runtime paths without strict gating can force loopback, async data, beacon, PMA PWM, or debug capture behavior during active links.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware/display behavior:

- Build all AMD display configurations that include DPCS 4.2.2 register headers; missing or renamed macros should fail at compile time.
- Generated-header checks should confirm every `*_MASK` is consistent with its matching `__SHIFT` and field width, especially 16-bit reserved masks and multi-bit fields like `RATE`, `WIDTH`, `PSTATE`, `VCO_LD_VAL_OVRD`, `IBOOST_LVL_OVRD_VAL`, `RX_PMA_TERM_CTL_R`, and calibration `data`.
- Compare RAWLANE2 and RAWLANE3 macro families for expected parity, excluding only lane-number prefixes and any documented lane-specific exceptions.
- Cross-check this shift/mask slice with the matching offset header so every register block named here has the expected `ixDPCSSYS_CR2_*` address and no stale field family exists without an address.
- Hardware smoke tests should exercise DisplayPort link bring-up, lane rate/width changes, retraining, low-power transitions, RX adaptation, EQ update, TX/RX reset/request handshakes, MPLL switching, and IRQ mask/clear handling.
- Debug tests can read FSM/IRQ/PMA/TX_CTL/RX_CTL status after link training and verify expected `ACK`, calibration done, power-up done, RX valid, DCC, RTUNE, and adaptation status transitions.
- Failure signatures include lane 2 or lane 3 only link failures, stuck reset/request/ACK bits, masked or uncleared PHY IRQs, continuous adaptation not starting or not stopping, wrong TX/RX data-enable state, broken loopback/test-mode cleanup, invalid calibration readbacks, or regressions limited to DPCS 4.2.2 while neighboring DPCS generations still pass.

### subset-b-002361: lines 57192-59638

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 57192-59638

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY raw always-on lane registers under the CR2 indirect register space. It contains no executable driver logic; its public surface is preprocessor metadata that maps hardware register fields to bit positions (`__SHIFT`) and masks (`_MASK`).

The requested range contains 2,447 source lines, 2,071 `#define` entries, and 376 register-comment markers. It starts inside `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_ADPT_ATT`: the register comment and `ATT_ADPT_VAL__SHIFT` are just before this chunk, while this range begins at `RESERVED_15_8__SHIFT` and the masks. It then covers the remainder of lane 0's raw always-on RX adaptation, calibration, signal-detect, DCC, firmware, and lane-mode fields; full corresponding blocks for `RAWAONLANE1`, `RAWAONLANE2`, and `RAWAONLANE3`; and most of the generic `RAWAONLANEX` template block. The range ends at the bare comment for `DPCSSYS_CR2_RAWAONLANEX_DIG_TX_DCC_CONT`; that register's shift and mask defines follow in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO accesses in this range. The only exported interface is generated macro names following the DPCS convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: mask used to read, compose, or update that field.

The main register families in this chunk are:

- RX adaptation readback and control: `DIG_RX_ADPT_ATT`, `DIG_RX_ADPT_VGA`, `DIG_RX_ADPT_CTLE`, `DIG_RX_ADPT_DFE_TAP1` through `TAP5`, `DIG_RX_ADPT_IQ`, `DIG_RX_ADAPT_FOM`, `DIG_RX_ADAPT_DONE`, and `DIG_ADPT_CTL_0` through `DIG_ADPT_CTL_7` expose attenuation, VGA, CTLE, DFE tap, IQ, figure-of-merit, done, and opaque adaptation-control fields.
- DFE, slicer, and phase state: `DIG_DFE_*_VDAC_OFST`, `DIG_DFE_*_REF_LVL`, `DIG_DFE_SUMMER_ODD_IDAC_OFST`, `DIG_RX_SLICER_CTRL_EVEN`, `DIG_RX_SLICER_CTRL_ODD`, `DIG_RX_PHSADJ_LIN`, `DIG_RX_PHSADJ_MAP`, and `DIG_RX_IQ_PHASE_ADJUST` describe even/odd data, error, bypass, phase, reference, and slicer adjustment values.
- Lane power, MPLL, and calibration status: `DIG_INIT_PWRUP_DONE`, `DIG_MPLLA_COARSE_TUNE`, `DIG_MPLLB_COARSE_TUNE`, `DIG_LANE_CMNCAL_MPLL_STATUS`, `DIG_LANE_CMNCAL_RCAL_STATUS`, `DIG_MPLL_DISABLE`, and `DIG_MPLL_BG_CTL` describe initial power-up, PH2 power-up, common calibration init/done, MPLL disable, coarse tune, and MPLL background wait/delay controls.
- Fast calibration/adaptation flags: `DIG_FAST_FLAGS` and `DIG_FAST_FLAGS_2` provide bitfields for accelerated RX startup/adaptation, AFE/DFE/bypass/reference/IQ calibration, supervisor and TX/RX-detect flows, RX power/VCO waits, continuous calibration/adaptation, TX/RX DCC calibration, VPHUD/VREF calibration, RTUNE skipping, and signal-detect calibration.
- TX/RX disable, lane mode, and firmware controls: `DIG_TXRX_OVRD_IN`, `DIG_LANE_XCVR_MODE_OVRD_IN`, `DIG_LANE_XCVR_MODE_IN`, `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, and `DIG_FW_CALIB_CONFIG` define override enables/values, lane transceiver mode fields, and firmware configuration words.
- RX loss-of-signal, squelch, and signal-detect controls: `DIG_RX_LOS_MASK_CTL`, `DIG_RX_SIGDET_FILT_CTRL`, `DIG_STATS`, `DIG_RX_OVRD_OUT_1` through `DIG_RX_OVRD_OUT_3`, `DIG_RX_SIGDET_CAL`, `DIG_RX_SIGDET_HF_CODE`, `DIG_RX_SIGDET_LF_CODE`, `DIG_RX_VREFGEN_EN`, `DIG_SIGDET_OUT_OVRD`, `DIG_SIGDET_OUT_IN`, and `DIG_RX_SIGDET_CONFIG` describe LOS mask timing, signal-detect filters, squelch/VREF status, PMA squelch and termination overrides, signal-detect calibration thresholds/tunes, VREF generator enable, and filtered signal-detect outputs.
- RX and TX DCC/calibration code storage: `DIG_CAL_IOFF_CODE`, `DIG_CAL_ICONST_CODE`, `DIG_CAL_VREFGEN_CODE`, `DIG_RX_DCC_CAL_ICM_CODE_*`, `DIG_RX_DCC_CAL_IDF_CODE_*`, `DIG_RX_DCC_CAL_QCM_CODE_*`, `DIG_RX_DCC_CAL_QDF_CODE_*`, `DIG_TX_DCC_BANK_ADDR`, `DIG_TX_DCC_BANK_DATA`, `DIG_TX_DCC_CONT`, and `DIG_TX_DCC_CONFIG` expose DCC calibration code words, banked TX DCC access, DCC continuous mode, and configuration fields.

Most masks in this region are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these raw always-on lane blocks. The `RAWAONLANE0` through `RAWAONLANE3` blocks map to concrete lanes; `RAWAONLANEX` is the lane-X/template form with the same field layout and separate offsets.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of AMD display register tables:

1. Driver code for the matching ASIC generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables token-paste these generated names into structures used by AMDGPU Display Core hardware helpers.
3. Runtime paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` against those tables.
4. Actual sequencing for link bring-up, RX equalization, DFE/CTLE/VGA adaptation, signal detection, DCC calibration, MPLL/power management, lane-mode changes, and firmware-assisted PHY flows lives outside this generated header.

The macros only encode bit layout. They do not encode access type, reset value, ordering requirements, clock-domain requirements, polling timeout, write-one-to-clear behavior, self-clearing semantics, or read-only/write-only status.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible state in the CR2 raw always-on lane register windows:

- Per-lane adaptation state includes attenuation, VGA, CTLE, DFE tap values, IQ values, FOM readback, adaptation done, DFE VDAC/IDAC offsets, even/odd reference levels, slicer controls, phase adjustment maps, and opaque adaptation control words.
- Per-lane power and PLL state includes initial and PH2 power-up done bits, MPLLA/MPLLB coarse-tune values, common MPLL/RCAL calibration init/done status, MPLL disable bits, and MPLL background wait/delay controls.
- Per-lane fast-flow state includes fast RX startup, adaptation, AFE/DFE, bypass, reference-level, IQ, supervisor, TX common-mode, RX-detect, RX power-up, VCO wait/VCO calibration, continuous calibration/adaptation, DCC, VPHUD/VREF, RTUNE skip, and signal-detect calibration flags.
- Signal-detect and RX front-end state includes LOS mask count, high/low-frequency signal-detect filter controls, PMA squelch status, VREF generator status/enable, PMA squelch/termination/signal-detect override values and enables, signal-detect calibration thresholds and tune codes, and filtered output override/readback fields.
- Calibration and DCC state includes IOFF, ICONST, VREFGEN, RX DCC ICM/IDF/QCM/QDF code words for banks 0 and 1, TX DCC bank address/data, TX DCC continuous enable, and TX DCC configuration.
- Firmware and mode state includes firmware microcode/configuration fields, firmware adaptation and calibration control bits, lane transceiver mode override and readback fields, and TX/RX disable overrides.

Persistence is hardware-defined. Configuration fields typically remain until a modeset/link reprogram, PHY power-gating event, suspend/resume, GPU reset, ASIC reset, firmware sequence, or driver initialization rewrites them. Status, done, calibration, and readback fields may be sampled, latched, self-clearing, or valid only while the relevant lane, MPLL, firmware, or always-on power domain is active. This header does not define those semantics.

## Dependencies And Integration Points

This file must stay synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching `ixDPCSSYS_*` offsets. The concrete lane windows use regular offset blocks, for example lane 0 `0x4000` through `0x4051`, lane 1 `0x4100` through `0x4151`, lane 2 `0x4200` through `0x4251`, lane 3 `0x4300` through `0x4351`, and lane-X/template offsets `0x7000` through `0x7051`.
- The immediate range begins at lane 0 offset `0x4017` (`RX_ADPT_ATT`) and proceeds through lane 0 offset `0x4051`; it then covers the complete lane 1, lane 2, and lane 3 raw always-on offset groups and the lane-X group through the `TX_DCC_CONT` boundary at `0x7047`.
- AMDGPU Display Core resource, link encoder, PHY, and diagnostics code consumes these generated masks through versioned register tables instead of hard-coding the bit values.
- Link training, hotplug/modeset, power management, firmware-controlled PHY calibration, DisplayPort/HDMI PHY bring-up, signal-detect handling, and debug register dumps are the most likely consumers of the state described here.
- Firmware and hardware state machines may also read or update the same registers, especially for fast adaptation/calibration, DCC tuning, signal-detect filtering, common calibration, and power-up completion.

Behaviorally, this chunk is below the user-facing display stack. It defines the raw bit layout needed when higher layers configure or diagnose per-lane PHY adaptation and calibration on DPCS 4.2.2 hardware.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting reserved bits, writing the wrong lane field, or decoding hardware status incorrectly.
- The header is generated metadata. Manual edits risk divergence from AMD's authoritative register database, firmware expectations, silicon documentation, and `dpcs_4_2_2_offset.h`.
- Chunk boundaries are artificial. The first register, `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_ADPT_ATT`, is split: its comment and `ATT_ADPT_VAL__SHIFT` are in the previous chunk. The last register, `DPCSSYS_CR2_RAWAONLANEX_DIG_TX_DCC_CONT`, is also split: only the comment is inside this range, while its actual defines follow in the next chunk.
- Lane repetition is copy-sensitive. Lanes 1, 2, and 3 should remain layout-compatible with lane 0, and the `RAWAONLANEX` template should remain compatible with the concrete lane forms where intended. A generator error could affect one lane while neighboring lanes look correct.
- RX adaptation fields are link-training-sensitive. Incorrect masks around CTLE, VGA, attenuation, DFE taps, IQ, FOM, slicer, phase adjustment, or done bits can lead to unstable equalization, retraining loops, or misleading diagnostics.
- DCC and calibration fields affect electrical timing. Bad masks for RX DCC code words, TX DCC banked access, TX DCC continuous mode, VREF generator, IOFF/ICONST, or signal-detect calibration can cause black screens, marginal links, or rate-specific failures.
- Override fields can bypass normal state-machine behavior. Incorrect TX/RX disable, lane mode, PMA squelch, PMA termination, VREF, or signal-detect override masks may leave a lane in a state that higher-level display code cannot infer from normal status alone.
- Fast-flow flags combine many calibration/adaptation shortcuts in dense bitfields. Confusing `FAST_FLAGS` with `FAST_FLAGS_2`, or continuous-calibration bits with one-shot bits, can create timing bugs that only appear on specific links or after power transitions.
- Many registers include broad `RESERVED_*` masks. Any helper that updates a field by composing raw values must preserve reserved bits according to hardware rules; the generated mask names alone do not enforce safe read-modify-write behavior.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU display support for the ASIC generation that includes DPCS 4.2.2. Missing or renamed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this range has a matching `__SHIFT` and `_MASK`, allowing the known boundary exceptions for the split `RAWAONLANE0_DIG_RX_ADPT_ATT` at the start and the bare `RAWAONLANEX_DIG_TX_DCC_CONT` comment at the end.
- Cross-check the field groups against `dpcs_4_2_2_offset.h`, especially lane 0 offsets `0x4017` through `0x4051`, lanes 1-3 offsets `0x4100` through `0x4351`, and lane-X offsets `0x7000` through `0x7047`.
- Diff this DPCS 4.2.2 generated output against AMD's source register database and nearby generated variants where lane layouts are expected to match.
- Exercise DisplayPort and HDMI link bring-up across available link rates, lane counts, power states, and PHY lanes. Expected signals are stable link training, adaptation completion, sane DFE/CTLE/VGA readback, no unexpected signal-detect loss, and no stuck calibration state.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in adaptation, DCC, signal-detect, MPLL, firmware, and lane-mode fields.
- Use register dumps or PHY debug traces during failing links to confirm the masks decode attenuation, VGA, CTLE, DFE taps, slicer settings, phase adjust, FOM, fast flags, signal-detect status, DCC code words, VREF/calibration codes, and lane-mode fields correctly.
- Validate diagnostic and firmware-assisted paths that touch `FW_*`, `SIGDET_*`, `RX_OVRD_OUT_*`, `TXRX_OVRD_IN`, `LANE_XCVR_MODE_*`, and DCC bank registers, because those are likely to expose mask/shift mistakes without changing higher-level display API behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR2_RAWAONLANE0_DIG_RX_ADPT_ATT` and the earlier lane 0 raw always-on registers, including the AFE, DFE, phase-adjust, MPLL coarse-tune, and power-up fields before line 57192. This chunk covers the rest of lane 0, all of lanes 1-3, and most of the `RAWAONLANEX` template. The next chunk should finish `DPCSSYS_CR2_RAWAONLANEX_DIG_TX_DCC_CONT` and continue with the remaining lane-X raw always-on registers before the later CR2 supervisor/template sections.

### subset-b-002362: lines 59639-62003

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 59639-62003

## Scope And Purpose

This chunk is generated AMD DPCS 4.2.2 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used to pack, update, and read fields in the DPCS `CR2` PHY/control-register space. Runtime code combines these field macros with the matching register-offset macros from `dpcs_4_2_2_offset.h` and DC register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `FD`, `SR`, and `SRI`.

The requested range is a mid-file slice of `dpcs_4_2_2_sh_mask.h` under the AMDGPU display driver source mirror. It starts inside the `DPCSSYS_CR2_RAWAONLANEX_DIG_TX_DCC_CONT` field definitions, then covers RAWAON lane signal-detect and firmware/calibration controls, a large `SUPX` shared-PHY block for reference clocks, MPLL A/B programming, analog bandgap/RTUNE/PLL controls, and the beginning-to-middle of per-lane `LANEX` TX/RX override, power-state, calibration, CDR, and LBERT controls. Although this repository path is under `ceph-client`, this file is GPU display hardware metadata, not distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocation paths, or persistence APIs in this range. The public interface is the generated macro namespace:

- `DPCSSYS_CR2_<register>__<field>__SHIFT`: the low bit position for a field.
- `DPCSSYS_CR2_<register>__<field>_MASK`: the raw bitmask for the same field.
- `RESERVED_*` field macros: generated masks for reserved bit ranges that consumers should generally preserve unless the hardware programming guide says otherwise.

Major register families covered by this chunk:

- `RAWAONLANEX_DIG_*`: always-on lane controls for MPLL bandgap state delay, HF/LF signal-detect override and readback, firmware micro/manual/adaptation/calibration configuration, lane transceiver mode override/readback, RX signal-detect filter counters, and TX duty-cycle-correction configuration.
- `SUPX_DIG_REFCLK_OVRD_IN`: shared reference-clock override fields for clock enable, pad selection, clock range, bandgap enable, HDMI mode, and pre-high-power override.
- `SUPX_DIG_MPLLA_*` and `SUPX_DIG_MPLLB_*`: symmetric MPLL A/B fields for divider clocks, HDMI divider clocks, enable/standby/frequency/VCO/calibration control, multipliers, fractional-N and spread-spectrum controls, SSC peak/stepsize words, charge-pump and gain controls, ASIC input mirrors, power-control status/timers/calibration, DAC output, and SSC spread type.
- `SUPX_DIG_SUP_*`, `PRESCALER_*`, `LVL_*`, `BANDGAP_*`, and `ASIC_IN`: shared supervisor, prescaler, level, bandgap, and ASIC input/override fields that bridge firmware/driver-visible digital control to analog PHY state.
- `SUPX_ANA_*`: analog-facing field maps for prescaler, RTUNE, bandgap, MPLL A/B miscellaneous, override, ATB, control, and reserved registers. These expose low-level PLL/bias/test controls and analog state mirrors.
- `SUPX_DIG_RTUNE_*` and `SUPX_DIG_ANA_*_OVRD_OUT`: RTUNE debug/config/status/set/stat/code fields plus digital-to-analog override outputs for MPLL, RTUNE, bandgap, and PMIX paths.
- `LANEX_DIG_ASIC_*`: per-lane TX/RX ASIC override input and output fields for lane mode, TX serializer/data/clock/swing/de-emphasis style controls, RX AFE/CDR/equalization controls, and status mirrors.
- `LANEX_DIG_TX_PWRCTL_*`: TX power-state bitfields for P0, P0S, P1, and P2 plus TX power-up timers, DCC bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT control.
- `LANEX_DIG_RX_PWRCTL_*`: RX power-state bitfields for P0, P0S, P1, and P2 plus RX AFE/VREG/clock/fast-start/rate/CDR/deserializer power-up timing.
- `LANEX_DIG_RX_VCOCAL_*`: RX VCO calibration controls, timing, and status fields for startup/update/counter timing, override selection, reset, continuous calibration, DPLL update gain, tune start/steps, skip bits, FSM state, calibration done, counter values, and VCO correctness/up indicators.
- `LANEX_DIG_RX_CDR_*`, `RX_LBERT_*`, and `RX_RX_ALIGN_XAUI_COMM_MASK`: RX CDR phase/frequency detector/gain/SSC fields, CDR/DPLL status and bounds, loopback/error-rate-test controls and counters, and XAUI comma alignment mask.

Most masks in this chunk are 16-bit register-field masks represented as `0x....L`, with some generated as 32-bit-form constants whose active bits remain in the low 16 bits. That width matters because DPCS CR access is often addressed through 16-bit PHY register windows even when C code stores values in `uint32_t`.

## Control Flow

This header has no runtime control flow. The runtime sequence is supplied by display-driver code:

1. DCN 3.1.5 resource code includes `dpcs/dpcs_4_2_2_offset.h` and this matching `dpcs/dpcs_4_2_2_sh_mask.h`.
2. Register tables and helper macros token-paste register and field names into offset, shift, and mask constants.
3. Link encoder, PHY, clock, power, and diagnostic paths use register helpers to write field values, preserve unrelated bits, and poll status fields.
4. Hardware then performs the actual state transitions: reference-clock and bandgap bring-up, MPLL programming/calibration, TX/RX lane power-state entry and exit, signal detection, CDR/VCO calibration, DCC adjustment, RTUNE calibration, and LBERT/debug capture.

The chunk does not encode sequencing rules. Consumers must still order operations correctly: enable reference and bandgap resources before PLL use, program PLL dividers before dependent lane clocks, observe MPLL/RX VCO lock and calibration status before enabling high-speed data, and avoid overriding analog/ASIC fields while firmware or hardware finite-state machines own them.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO or indirect CR-backed hardware state.

State represented by these fields includes:

- Shared PHY clocking state: reference-clock source/range/enables, HDMI mode, prescaler, bandgap, MPLL A/B enable/standby/divider/multiplier/fractional-N/SSC/charge-pump settings, lock and calibration timing, and PLL status.
- Per-lane TX state: power-state contents for P0/P0S/P1/P2, analog reference/clock/serializer/data enables, DCC compensation and DAC settings, power-up timing, TX clock alignment, and LBERT mode.
- Per-lane RX state: power-state contents, AFE/VREG/clock/CDR/deserializer timing, signal detection, equalizer-related ASIC overrides, RX VCO calibration configuration/status, CDR gain/SSC/phase detector settings, DPLL frequency and frequency bounds, XAUI comma masking, and LBERT error counters.
- Calibration and diagnostics: RTUNE set/stat/code values, firmware calibration/adaptation words, analog test-bus controls, OCLA selection, debug mux fields, FSM state readbacks, sticky status indicators, and error counters.

Persistence is hardware-defined. Configuration registers typically retain values until the link is reprogrammed, the PHY lane is power-gated, suspend/resume or display core reset runs, firmware reinitializes PHY state, or the ASIC resets. Status, calibration-done, counter, debug, and acknowledgment fields may be read-only, self-clearing, sticky, or write-sensitive depending on the underlying register. The mask header does not distinguish those access semantics, so driver code must rely on the hardware specification and existing register-access conventions.

## Dependencies And Integration Points

This chunk depends on the generated DPCS register database staying internally consistent:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the `ixDPCSSYS_CR2_*` register addresses that pair with these masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both the DPCS 4.2.2 offset and shift/mask headers and defines the DPCS base segments used by the display resource stack.
- AMD display register helpers consume the `__SHIFT` and `_MASK` macros through token-pasting field descriptors such as `FD(reg__field)` and through `REG_SET`/`REG_UPDATE`/`REG_GET` style helpers.

Functional integration points include DC link encoder and PHY programming, DisplayPort and HDMI link bring-up, link training, clock-source and PLL selection, PHY firmware handoff, lane power management, suspend/resume restore, hotplug and signal-detect handling, manufacturing or debug calibration flows, and diagnostic paths that read CDR/VCO/LBERT/OCLA/RTUNE status.

The chunk is also tightly coupled to adjacent generated slices. Its first lines are the tail of `TX_DCC_CONT` and its final line stops inside `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4`; neighboring chunks are needed for complete register-family coverage and for any file-level conclusions.

## Risks And Edge Cases

- Mask or shift drift is the main risk. These are untyped preprocessor constants, so a wrong bit position or mask can compile cleanly while silently programming the wrong PHY field.
- DPCS CR2 field names are highly repetitive across `MPLLA`/`MPLLB`, TX/RX, and P0/P0S/P1/P2. Copy-generation mistakes can affect only one PLL, lane direction, or power state, making failures connector-specific or link-rate-specific.
- Reserved fields are exposed as macros but are not permission to write reserved bits. Read-modify-write helpers must preserve unrelated bits, especially in analog and PLL control registers.
- Override fields can fight autonomous hardware or firmware control. Incorrect use of `*_OVRD_EN`, `*_OVRD_VAL`, `ASIC_*_OVRD_*`, or analog override outputs can leave clocks, bandgap, PLLs, CDR, or lane power in a forced state after modeset, suspend/resume, or error recovery.
- PLL and clock fields are sequencing-sensitive. Bad `REFCLK`, `MPLL*`, SSC, charge-pump, timer, or lock/calibration masks can produce blank displays, unstable high link rates, HDMI clocking issues, spread-spectrum failures, or long waits on lock polling.
- TX/RX power-state and timer fields directly affect lane bring-up and power saving. Incorrect bitfields can cause excessive power, failure to exit low power, missed RX detection, broken deserializer/CDR startup, or intermittent link training failures.
- Calibration/status fields are often side-effect-sensitive. Misreading VCO/RTUNE/LBERT/DCC status or writing to ack/control fields with the wrong mask can hide real hardware faults or corrupt diagnostic data.

## Test Signals

Useful validation signals are mostly integration and hardware-facing rather than unit-testable:

- Build coverage for `dcn315_resource.c` and any resource/link encoder code that includes `dpcs_4_2_2_sh_mask.h`, catching missing or renamed generated macros.
- Static consistency checks that each field has both a `__SHIFT` and `_MASK`, that active masks remain within the expected 16-bit CR field width, and that paired A/B or P-state families remain structurally symmetric where the hardware expects symmetry.
- Display smoke tests on DCN 3.1.5-era hardware across HDMI and DisplayPort, including hotplug, EDID/DPCD reads, link training at multiple rates/lane counts, suspend/resume, and multi-monitor modesets.
- PHY-specific debug evidence: successful MPLL lock/calibration polling, RX VCO calibration done/correct/up status, stable signal-detect state, expected RTUNE status/code values, no LBERT error counter growth under test modes, and no unexpected CDR/DPLL frequency-bound violations.
- Regression signals include blank or flickering displays, HDMI audio/video clock issues, DP training failures, wake/resume failures, elevated power from stuck PHY states, unexpected timeouts in register polling, and failures limited to one connector or one link rate.

### subset-b-002363: lines 62004-64388

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 62004-64388

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It contains no executable C logic; it publishes preprocessor constants for bit positions (`__SHIFT`) and masks (`_MASK`) used by AMDGPU Display Core code when composing or decoding DPCS indirect hardware register fields.

The requested range contains 2,119 `#define` entries and 263 register comment groups. It starts at the tail of `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4`, with only the final masks for that register in this chunk, then covers CR2 lane-X RX clock/data-recovery status, DPLL bounds, RX adaptation control/status, RX statistics, digital/analog lane controls, raw lane-X PCS/FSM/IRQ/PMA/TX/RX control fields, and early CR3 supervisor fields. It ends on the comment for `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN`; that register's shift/mask definitions are outside this slice.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for the hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, compose, or update the field.

The main macro families in this chunk are:

- `DPCSSYS_CR2_LANEX_DIG_RX_CDR_*` and `DPCSSYS_CR2_LANEX_DIG_RX_DPLL_*`: CDR status and DPLL frequency/bound fields, including `PHUG_VALUE`, `FRUG_VALUE`, current DPLL frequency, and upper/lower frequency-bound controls.
- `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation setup, reset, status, slicer, DFE, DAC-selection, and CR bank access fields. The groups cover adaptation timers and start bits, CTLE/VGA/attenuator/DFE enable and thresholds, adaptation step sizes, initial error values, reset bits for individual adaptation loops, done/status readbacks for ATT/VGA/CTLE/DFE taps, even/odd data/error VDAC offsets, slicer controls, and indexed CR bank address/data fields.
- `DPCSSYS_CR2_LANEX_DIG_RX_STAT_*`: RX statistic and pattern-match collection fields, including load values, data masks, match controls, statistic controls, sample-count and statistic-count words, calibration-comparison clock control, and statistic stop control.
- `DPCSSYS_CR2_LANEX_DIG_ANA_*` and `DPCSSYS_CR2_LANEX_ANA_*`: digital-facing analog override/readback and analog lane fields for TX override outputs, termination codes, EQ override words, RX control/power/VCO overrides, RX calibration, DAC controls, AFE ATT/VGA/CTLE, scope/slicer controls, IQ phase/sense/calibration enable, signal-change gating, analog status, signal-detect overrides, TX DCC DAC overrides, TX power/measurement/ATB/DCC/termination/misc controls, RX clock/CDR/slicer/power/squelch/calibration/ATB controls, and reserved analog latches.
- `DPCSSYS_CR2_RAWMEM_DIG_*`: raw common ROM/RAM single-data fields for CR2 common memory windows.
- `DPCSSYS_CR2_RAWLANEX_DIG_PCS_XF_*`: raw lane-X PCS transfer, override, ATE, and direction fields for TX/RX pstate, width, rate, MPLL selection, beacon, data-valid, adaptation request/ack/FOM, TX pre/main/post directions, lane number, reserved words, termination controls, RX EQ delta/IQ controls, PH2 calibration, loopback, and ATE override paths.
- `DPCSSYS_CR2_RAWLANEX_DIG_FSM_*`: raw lane-X finite-state-machine override, monitor, fast-sequence, calibration/adaptation, common calibration, flag, lock, DCC status, OCLA, TX EQ update, RCAL status, and RX IQ phase-offset fields.
- `DPCSSYS_CR2_RAWLANEX_DIG_IRQ_CTL_*`: raw lane-X IRQ request, status, clear, and mask fields for RX reset/request/rate/pstate/adaptation/PH2 calibration, lane transceiver mode, lane serial loopback, DCC on-demand, and TX reset/request events.
- `DPCSSYS_CR2_RAWLANEX_DIG_PMA_XF_*`: raw PMA transfer/override fields for lane, supervisor, TX, RX, RTUNE, MPHY, and RX adaptation override interfaces.
- `DPCSSYS_CR2_RAWLANEX_DIG_TX_CTL_*` and `DPCSSYS_CR2_RAWLANEX_DIG_RX_CTL_*`: TX/RX lane control, DCC/off-cancel/adaptation continuous-status, clock/data-enable/LOS-mask controls, and OCLA fields.
- `DPCSSYS_CR3_SUP_DIG_*`: the start of the CR3 supervisor block, covering ID-code low/high readback, reference-clock overrides, MPLLA divider and HDMI clock overrides, and MPLLB divider override definitions. The next CR3 HDMI-clock register is only introduced by comment at this chunk boundary.

Most masks are 16-bit-style values with an `L` suffix, matching the DPCS indirect register-field convention. The companion offset header maps representative groups in this range to offsets such as `0x9058` for `DPCSSYS_CR2_LANEX_DIG_RX_CDR_STAT`, `0xe0c8` for `DPCSSYS_CR2_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN_2`, and `0x0006` for the CR3 `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` register introduced at the end.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Generated register-list, shift-list, and mask-list initializers token-paste register and field names into AMD Display Core resource tables.
3. Runtime display code uses register helpers to read, write, get, set, or update individual fields through matching offsets and these shift/mask constants.
4. Actual sequencing for DPLL/CDR programming, RX adaptation, statistic collection, analog override programming, PCS/PMA transfer control, FSM sequencing, IRQ handling, lane calibration, and CR3 supervisor reference-clock/MPLL setup lives in AMDGPU display code, firmware, and hardware state machines outside this header.

The macros only describe bit layout. They do not encode reset values, access width beyond the mask shape, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, polling order, clock-domain restrictions, or power-domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR2 lane-X and CR3 supervisor DPCS registers:

- CDR/DPLL fields expose live or programmed receive-clock recovery gains and frequency bounds.
- RX adaptation fields hold configuration and readback state for ATT, VGA, CTLE, DFE taps, slicers, DAC selections, indexed CR bank access, adaptation reset, and adaptation-done conditions.
- RX statistic fields hold match/mask/sample/count configuration and statistic counters used for PHY or receiver diagnostics.
- Digital/analog lane fields hold TX/RX override values and enables, term-code and EQ controls, VCO/calibration/DAC/slicer/scope controls, analog status, signal-detect overrides, TX DCC controls, RX power/CDR/squelch/calibration/ATB state, and reserved analog latches.
- Raw lane-X PCS/PMA/FSM/IRQ/TX/RX fields expose cross-interface control and state for link rate, pstate, width, MPLL selection, TX/RX data/valid paths, adaptation request/ack/FOM, direction updates, ATE overrides, PMA handoff, fast calibration/adaptation sequencing, common calibration status, IRQ latches/clears/masks, OCLA debug, DCC status, and loopback or termination override paths.
- CR3 supervisor fields expose ID-code readback and early reference-clock/MPLLA/MPLLB divider and HDMI-clock override controls.

Persistence is hardware-defined. Programmed control and override fields generally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, statistic, IRQ, ACK, lock, done, calibration, and diagnostic readback fields may be latched, sampled, self-clearing, read-only, or only valid while the relevant lane/common clock and power domains are active. This generated header does not define those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion address map:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` offsets for the register groups whose fields are defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`, tying this generated contract to DCN 3.1.5 resource construction.
- The AMD Display Core register-helper layer consumes generated offset, shift, and mask tables to access hardware without open-coding bit positions.
- Firmware and hardware state machines share these fields with the driver for RX adaptation, signal detection, DCC and analog calibration, CDR/DPLL tuning, PCS/PMA handoff, IRQ signaling, test/ATE override routes, OCLA/debug capture, and supervisor reference-clock/MPLL setup.

Behaviorally, this range sits below the user-facing display stack. DisplayPort/HDMI link bring-up, PHY clock programming, lane calibration, hotplug/modeset, suspend/resume, diagnostics, and manufacturing/ATE flows can depend on these bitfield definitions being exactly correct.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong hardware bit, corrupting a reserved field, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The `LANEX` and `RAWLANEX` naming represents a repeated lane-template space rather than one ordinary C abstraction. A consumer that pairs these masks with the wrong lane or raw/normal offset block can manipulate the wrong hardware path.
- Many registers pair override value bits with override enable bits. Leaving enable bits asserted after debug, ATE, or validation use can bypass normal PHY, PCS, PMA, analog, CDR, DPLL, or supervisor state-machine control.
- RX adaptation, DFE tap, slicer, statistic, signal-detect, DCC, DAC, VCO, termination, and analog status fields are calibration-sensitive. Incorrect bit definitions can cause subtle link-training failures, degraded margins, misleading debug readbacks, or stuck polling loops.
- IRQ status/clear/mask groups repeat names across RX reset/request/rate/pstate/adaptation/PH2 and TX reset/request events. Misusing a clear or mask bit can hide real link events or produce repeated interrupt handling.
- PCS/PMA/FSM transfer fields have similar names across override input, hardware input, override output, and output/status groups. Consumers must pair each mask with the correct register offset and access direction.
- Supervisor reference-clock and MPLL divider/HDMI-clock override fields affect shared clocking. Bad masks can produce clock instability, lock failures, black screens, rate-specific retraining loops, or compliance regressions.
- Chunk boundaries are artificial. This chunk starts mid-register with only `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4` masks and ends at the comment for `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` before that register's definitions.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for DCN 3.1.5. Missing, renamed, or malformed macros should fail where `dcn315_resource.c` and generated register tables consume DPCS 4.2.2 symbols.
- Mechanically verify that complete register groups in this range have matching `__SHIFT` and `_MASK` definitions, allowing the known start-boundary exception for `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4` and the end-boundary comment-only exception for `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN`.
- Cross-check every complete register group in this chunk against `dpcs_4_2_2_offset.h`, especially the CR2 `LANEX` to `RAWLANEX` transition and the CR3 `dpcssys_cr3_rdpcstxcrind` address-block transition.
- Diff against AMD's generated source register database and adjacent DPCS versions where compatible hardware layout is expected.
- Exercise DP and HDMI link bring-up across lane counts, link rates, power states, and hotplug/modeset paths. Expected signals are stable link training, successful RX adaptation, valid CDR/DPLL status, correct signal-detect behavior, clean IRQ handling, and no unexpected lane or supervisor timeout.
- Exercise suspend/resume, GPU reset, low-power entry/exit, and display disable/enable paths to catch stale override, reference-clock, MPLL, PCS/PMA, DCC, analog calibration, or adaptation state.
- Use register dumps or PHY debug traces during failures to confirm adaptation values, DFE tap readbacks, slicer/DAC values, statistic counters, analog status, PCS/PMA transfer signals, FSM fast flags, IRQ status/clear behavior, DCC status, OCLA capture fields, CDR/DPLL values, and CR3 supervisor reference-clock/MPLL divider decodes correctly.
- Where supported, run debug/manufacturing paths for ATE overrides, loopback, ATB, analog test bus, OCLA, PMA override, PCS override, DCC bank access, signal-detect override, and supervisor clock overrides, then confirm normal link training resumes after overrides are released.

## Cross-Chunk Notes

The previous chunk should contain the beginning of `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4` and earlier CR2 CDR control fields. This chunk continues from that partial register, covers the bulk of CR2 lane-X RX adaptation/statistics/analog/raw PCS-FSM-IRQ-PMA control definitions, and enters the CR3 supervisor address block at line 64329. The next chunk should provide the definitions for `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` and continue the CR3 supervisor clock/MPLL register map. The final per-file report should reconcile these artificial boundaries before making whole-file claims about all DPCS 4.2.2 register groups.

### subset-b-002364: lines 64389-66756

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 64389-66756

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask register-field slice. It contains no executable C logic; it publishes preprocessor constants that describe bit offsets and bit masks for fields in the `DPCSSYS_CR3` display PHY/control-register space. Driver code combines these constants with the matching `dpcs_4_2_2_offset.h` offsets so AMDGPU display register helpers can pack, extract, and update individual MMIO or indexed DPCS fields.

The range covers 2,368 lines with 2,143 `#define` entries: 1,076 `__SHIFT` macros, 1,067 `_MASK` macros, and 225 register comment markers. It begins at the mask half of `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN`, so the matching shifts for that register are just before this chunk. It ends cleanly after `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_OVRD_IN_4`, while the rest of lane 1 continues in following chunks. Although the repository path is under a `ceph-client` mirror, this file is AMDGPU display hardware metadata and does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation APIs in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset of a DPCS register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate or preserve the field during read-modify-write operations.

The main register families in this range are:

- `DPCSSYS_CR3_SUP_DIG_MPLLA_*` and `DPCSSYS_CR3_SUP_DIG_MPLLB_*`: digital supervisor MPLL A/B override, status, ASIC input, spread-spectrum, fractional-N, charge-pump, clock-divider, HDMI clock, calibration, power-control timer, DAC range, lock, and PMIX fields. The A/B families are mostly mirrored and describe two PHY PLL paths.
- `DPCSSYS_CR3_SUP_DIG_SUP_*`, `PRESCALER_*`, `LVL_*`, `BANDGAP_*`, and `RTUNE_*`: supervisor control/status fields for prescaler override, RTUNE request/override/configuration/status, TX calibration codes, level controls, bandgap state, and analog override outputs.
- `DPCSSYS_CR3_SUP_ANA_*`: analog supervisor fields for prescaler, RTUNE, bandgap, MPLL miscellaneous controls, analog test bus controls, MPLL control registers, reserved analog fields, and power measurement.
- `DPCSSYS_CR3_LANE0_DIG_*`: lane 0 digital ASIC override/input/output fields for lane loopback, TX request and power-state controls, TX rate/width/data enable, PLL selection, cursor coefficients, HDMI mode, reset, RX status capture, DCC DAC control, TX clock alignment, LBERT, and status-match/count registers.
- `DPCSSYS_CR3_LANE0_ANA_*`: lane 0 analog TX override/status fields for power override, alternate bus, analog test bus, DCC DAC/control, termination code, EQ controls, clock override, vref, slew/peaking, regulator bypass, and reserved analog fields.
- `DPCSSYS_CR3_LANE1_DIG_ASIC_*`: the beginning of lane 1, covering lane-level loopback and TX overrides through reset. This mirrors the lane 0 digital ASIC TX override shape but is incomplete at the artificial chunk boundary.

Most field values are 16-bit-style masks such as `0x0000FFFFL`, though some counter, data, and status fields use 32-bit masks in other parts of the header. Many field names include explicit override-enable bits (`*_OVRD_EN`, `*_OVR_EN`) paired with the value they force, which is important for distinguishing normal hardware-driven state from software-forced PHY state.

## Control Flow

This header has no runtime control flow. The runtime path is supplied by AMDGPU display code:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Register-list macros such as `DPCS_DCN31_REG_LIST`, `DPCS_DCN31_MASK_SH_LIST`, and `DCN3_1_RDPCSTX_REG_LIST` token-paste register and field names into per-block register, shift, and mask tables.
3. Link encoder, DPCS/RDPCS TX, UNIPHY, and broader DC resource initialization stores those numeric constants in hardware object tables.
4. Runtime display paths call register helpers to program PHY PLLs, lane power states, link rates, training/equalization controls, HDMI/DP mode bits, status counters, and analog overrides.

The macros do not encode sequencing. Consumers must still order PLL enable/calibration, power-up timers, lane resets, rate/width transitions, EQ/cursor changes, HDMI mode changes, link training, and power-gating transitions according to the hardware specification.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware state in the CR3 DPCS register block:

- MPLL A/B configuration and observed state, including enable, divider, fractional-N quotient/remainder/denominator, SSC peak/step size, charge pump, VCO/frequency selection, calibration, clock synchronization, lock timers, and analog DAC outputs.
- Supervisor and analog support state for prescaler, RTUNE, bandgap, level controls, calibration codes, power measurement, and analog override/status outputs.
- Lane 0 TX state for request, power state, rate, width, PLL selection, data enable, main/pre/post cursor coefficients, async driver enable, HDMI mode, clock ready, receiver detect, invert, low-power detect, DC coupling, FIFO extension, MPHY mode, and reset.
- Lane 0 and lane 1 loopback/test state, including TX-to-RX serial loopback, RX-to-TX parallel loopback, AC JTAG enable, LBERT controls, RX status matching/counting, and analog test bus controls.
- Lane 0 analog TX state for power, DCC DAC, termination, equalization, regulator/vref/slew/peaking controls, and status readback.

Persistence is hardware-defined. Programmed fields generally last until link reconfiguration, PHY reset, power gating, suspend/resume restore, driver reset, or ASIC reset. Status, calibration, timer, counter, and ack fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the related PHY clocks and power islands are active. This generated header does not express those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` provides the matching `reg*`, `ix*`, and base-index address constants for these field macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both DPCS 4.2.2 generated headers and defines `DPCS_BASE__INST0_SEG*` for this ASIC generation.
- The same resource file uses `DPCS_DCN31_REG_LIST(id)`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, `DPCS_DCN31_MASK_SH_LIST(_MASK)`, and `DCN3_1_RDPCSTX_REG_LIST(0..4)` to build DPCS and RDPCS TX register tables.
- Higher-level display components consume those tables through DCN 3.1 link encoder, UNIPHY/DIO, link training, clock source, hardware sequencing, and resource-pool paths.

Behaviorally, this slice integrates with DisplayPort/HDMI PHY bring-up: PLL programming, spread-spectrum setup, link clock generation, lane power-state transitions, lane width/rate selection, transmitter cursor/equalization programming, link-test diagnostics, and analog calibration/status collection.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while touching the wrong MMIO bits, corrupting adjacent fields, failing PLL lock, breaking link training, or producing marginal signal integrity.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the offset header, firmware assumptions, and silicon documentation.
- The A/B MPLL families and lane 0/lane 1 families are highly repetitive. Instance-specific generator or copy errors can leave one PLL or lane broken while a neighboring instance works.
- The chunk starts after the `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` shift definitions, so local shift/mask pair checks must account for that artificial boundary. The lane 1 register family also continues after this chunk.
- Override fields are hazardous because they can bypass normal hardware control. Setting an override-enable bit without the intended value, or failing to clear it, can force stale PLL, clock, power, lane, or analog state across modesets and suspend/resume.
- PLL and SSC fields are timing-sensitive. Bad fractional-N, spread-spectrum, charge-pump, lock-timer, or divider masks can cause unstable clocks, link-training failures, display blanking, or receiver-specific HDMI/DP issues.
- Analog and DCC/EQ controls affect electrical behavior. Incorrect termination, vref, peaking, cursor, slew, regulator, or DCC DAC programming may pass simple bring-up but fail compliance, high-bit-rate modes, long cables, or hotplug/retrain cycles.
- Status, ack, timer, and counter fields may have side effects or validity windows not visible in this header. Consumers must not infer read/write semantics from `_MASK` names alone.

## Test Signals

Useful validation should combine generated-header checks with hardware behavior:

- Build AMDGPU display support with DCN 3.1.5 enabled. Missing or renamed macros should fail where `dcn315_resource.c` expands DPCS and RDPCS register, shift, and mask tables.
- Mechanically diff this range against AMD's authoritative DPCS 4.2.2 register database and compatible nearby DPCS generated headers where the CR3 supervisor/lane layouts are expected to match.
- Check shift/mask pairing for fields wholly inside lines 64389-66756, allowing the known leading partial register where only masks are present in this chunk.
- Exercise DP and HDMI links on DCN 3.1.5 hardware across hotplug, modeset, suspend/resume, link-rate changes, lane-count changes, MST or multi-display configurations, and retraining after link errors.
- Validate PLL behavior with logs or hardware traces for MPLL lock, spread-spectrum enablement, fractional-N programming, calibration completion, and clock-stable timing.
- Run link-training and signal-quality tests that stress cursor/pre/post settings, EQ overrides, DCC/termination controls, long cables, high refresh rates, and high bit-depth modes.
- Monitor kernel logs and display diagnostics for failed link training, PHY reset loops, PLL timeout messages, HPD-only failures, resume-only blank displays, intermittent bit errors, compliance-test failures, or status counters that stop updating.

## Cross-Chunk Notes

This is a middle chunk of `dpcs_4_2_2_sh_mask.h` within the `DPCSSYS_CR3` block. Earlier chunks contain the CR3 indexed address/data accessors and the start of the supervisor register set, including the shift definitions for the leading `DPCSSYS_CR3_SUP_DIG_MPLLB_HDMI_CLK_OVRD_IN` masks. Later chunks continue lane 1 and subsequent DPCS register families. The final per-file research document should merge adjacent chunks before making whole-file claims about all DPCS instances, all lanes, or complete PLL/lane coverage.

### subset-b-002365: lines 66757-69113

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 66757-69113

## Chunk Scope

This chunk covers 2,357 lines of generated AMD DPCS 4.2.2 register bitfield metadata from `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_OVRD_OUT` through the beginning of `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1`. It contains 216 register comment blocks and 2,141 `#define` entries, almost entirely paired `__SHIFT` and `_MASK` constants. The chunk is part of the `dpcssys_dpcssys_cr3_dispdec` register address block and describes DisplayPort/PHY control and status fields for CR3 lane 1 plus the opening lane 2 digital ASIC fields.

## Purpose

The header provides compile-time field layout constants for AMD display code that needs to read, write, or compose DPCS register values. The companion `dpcs_4_2_2_offset.h` file supplies `ix...` register addresses, while this file supplies the field shift and mask constants for those registers. In this range, the constants model:

- Lane 1 digital ASIC override inputs and outputs for TX/RX request, data enable, rate, width, reset, low-power detect, inversion, equalization, CDR, alignment, loopback, async data, and clock-shift handshakes.
- Lane 1 TX and RX power-control states, power-up timings, DCC calibration bank/DAC controls, clock alignment, and LBERT test controls.
- Lane 1 RX VCO calibration, CDR, DPLL bounds, adaptation-control configuration/status, DFE tap status, slicer/VDAC offsets, statistic/match counters, MPHY low-speed controls, and analog override/status surfaces.
- Lane 1 analog TX/RX direct control registers for measurement buses, DCC, termination, clocks, miscellaneous TX/RX tuning, signal detect, scope, ATB measurement, and reserved analog fields.
- The start of lane 2 digital ASIC override and live input/output fields, mirroring the lane 1 digital ASIC pattern for a second physical lane.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The public interface is the macro namespace itself:

- `DPCSSYS_CR3_LANE1_*__<FIELD>__SHIFT` defines the bit position for a field in a 16-bit DPCS register payload.
- `DPCSSYS_CR3_LANE1_*__<FIELD>_MASK` defines the field mask already shifted into register position.
- `DPCSSYS_CR3_LANE2_*__<FIELD>__SHIFT` and `_MASK` start the same scheme for CR3 lane 2.
- Register comments such as `//DPCSSYS_CR3_LANE1_DIG_RX_ADPTCTL_ADPT_CFG_0` delimit a set of field macros belonging to a single hardware register.

The dominant field families are:

- Override enable pairs, for example `REQ` with `REQ_OVRD_EN`, `PSTATE` with `PSTATE_OVRD_EN`, and many analog `*_OVRD_EN` fields. These indicate that writing code must usually set both a desired value field and its override-enable bit to force hardware behavior.
- Power-state fields under `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2` and `DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1/P2`, which define per-state analog/digital enable, reset, calibration, and data-enable bits.
- Timing fields under `TX_PWRUP_TIME_*` and `RX_PWRUP_TIME_*`, where masks span small counters plus fast/skip control bits.
- Calibration/status fields such as `RX_VCOCAL_RX_VCO_STAT_*`, `RX_ADPTCTL_*_STATUS`, `RX_STAT_STAT_CNT_*`, and `ANA_STATUS_*`, which are likely read paths rather than write-only configuration.

## Control Flow

This chunk has no executable control flow. Its practical control flow is preprocessor substitution into AMD display register helper macros. The include site for this exact header is `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`. Downstream display code typically combines an `ix...` register offset with `FD(register__field)`-style descriptors and `REG_SET`, `REG_UPDATE`, or related helpers; those helpers rely on the generated `__SHIFT` and `_MASK` tokens to isolate and place bitfield values.

Because the header is data-only, sequencing is enforced by the callers and hardware programming model rather than by this file. For example, a TX override sequence may need to write request, rate, width, data-enable, and override-enable fields in a hardware-defined order; this chunk only supplies the numeric bit locations needed by that sequence.

## State and Persistence Behavior

The macros are immutable compile-time constants and do not allocate memory or persist state. The state they describe exists in memory-mapped DPCS hardware registers. Important state categories visible in this range include:

- Control state: TX/RX request, reset, data enable, power state, rate, width, MPLL selection, low-power, inversion, CDR/SSC/alignment, termination, adaptation, and analog enable bits.
- Calibration state: TX DCC DAC selection/ack/address/data, RX VCO calibration controls and stats, RX adaptation controls, DFE tap status, CTLE/VGA/ATT status, and signal-detect calibration fields.
- Diagnostic state: LBERT control/error, RX statistic sample and counter registers, match-pattern controls, OCLA enables, scope data, analog status, ATB measurement routing, and reserved/NC fields.

Persistence across boot, suspend, reset, and link training depends on hardware register retention and the AMD display driver code that programs these registers. This header does not define reset values, polling loops, or save/restore policy.

## Dependencies and Integration Points

- Include guard `_dpcs_4_2_2_SH_MASK_HEADER` makes the header safe for repeated inclusion.
- The header is licensed MIT and marked AMD-generated/owned in the file prologue.
- `dpcs_4_2_2_offset.h` is the required companion for address constants; this chunk's lane 1 offsets around `0x1120` to `0x11ff` and lane 2 offsets beginning at `0x1200` match the register names in this chunk.
- `dcn315_resource.c` includes this exact DPCS 4.2.2 offset/mask pair, establishing the ASIC integration target.
- Nearby generated headers for other DPCS/DCN versions contain the same or similar register names with version-specific masks and literal formatting, so code must include the correct ASIC version header rather than mixing variants.

## Risks and Edge Cases

- Bit layout correctness is hardware-critical. A wrong mask or shift can silently program the wrong PHY bit, potentially breaking link training, power sequencing, calibration, or display bring-up.
- Many fields are only 16-bit wide within `0x0000FFFFL` masks even though they are represented as C long literals. Callers must not assume a 32-bit register field unless the companion register definition says so.
- Override fields are easy to misuse: setting a value field without its corresponding override-enable bit may have no effect, while leaving an override enabled can force stale PHY behavior.
- Reserved and `NC` masks are exposed like normal fields. Driver writes should preserve reserved bits unless hardware documentation explicitly requires a value.
- Lane names are embedded in macro names. Accidentally using lane 1 fields with lane 2 offsets, or vice versa, can compile if helper macros are manually assembled but would encode the wrong field layout if lanes ever diverge.
- This chunk starts in the middle of the broader file and ends during lane 2 register definitions. Whole-file research must reconcile adjacent chunks to avoid treating lane 2 coverage as complete here.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-regression oriented:

- Compile `dcn315_resource.c` and any DC register helper users with this header included; missing or renamed macros should fail at compile time.
- Compare every register block in this chunk against the matching `ixDPCSSYS_CR3_*` names in `dpcs_4_2_2_offset.h`; the offset names should exist for each register comment block.
- Run static checks for duplicate field names within a register, masks that do not match their declared shift/width, masks outside 16 bits, and overlapping non-reserved fields.
- Exercise AMD display link training, hotplug, suspend/resume, and multi-lane DisplayPort paths on DCN 3.1.5-class hardware that uses `dpcs_4_2_2`.
- Hardware tests around TX/RX power-state transitions, RX adaptation, CDR/VCO calibration, LBERT, and lane 2 bring-up are especially relevant because those are the main control surfaces described in this chunk.

## Cross-Chunk Notes

This chunk is a continuation of the larger generated DPCS mask header. It likely follows earlier CR3 lane 0 and lane 1 definitions and is followed by the remainder of lane 2 and later lanes/blocks. The merge lane should combine this report with adjacent chunks to produce a single source-tree-aligned research document for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h`.

### subset-b-002366: lines 69114-71473

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 69114-71473

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic. Its exported surface is a large set of preprocessor constants that encode bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,137 `#define` entries across 2,360 lines and 223 register comment markers. It is entirely inside the `dpcssys_cr3_rdpcstxcrind` register window and covers CR3 lane-local PHY control/status fields. The chunk starts in the mask half of `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1`, continues through the rest of lane 2 digital ASIC, TX power, RX power, VCO calibration, CDR/DPLL, RX adaptation, RX statistic, MPHY, digital-to-analog override, and analog TX/RX fields, then starts lane 3 and reaches the first masks of `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, decode, or update that field.

The main register-field families are:

- Lane 2 digital ASIC tail and PHY handshakes: the range begins with the final masks for `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1`, including TX async enable/data/driver enable and VREG driver bypass fields whose shift definitions are in the previous chunk. It then covers `TX_ASIC_IN_2`, `TX_ASIC_OUT`, RX ASIC input/output words, RX equalization ASIC inputs, RX CDR/VCO ASIC inputs, RX override input 6, TX override input/output words, and OCLA enable fields. These macros describe reset/request/data enable, low-power detect, pstate/rate/width, main/pre/post cursor values, RX adaptation enables, RX termination, TX/RX acknowledgements, and lane override handshakes.
- Lane 2 TX power and timing: `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_*` defines TX power-state templates for P0, P0s, P1, and P2 plus power-up timing registers. The fields control analog reference generation, VCM hold, analog and word clocks, reset, serial enable, digital clock enable, data enable, RX detect allowance, VBOOST allowance, DCC compensation calibration, reference-clock enable timing, VCM/VBOOST timing, RX detect timing, and serial-enable timing.
- Lane 2 TX DCC and TX diagnostic controls: `DCC_CR_BANK_ADDR`, `DCC_CR_BANK_DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, and `DCC_DAC_ADDR` define the indirect DCC bank/DAC interface. `TX_CLK_ALIGN_TX_CTL_0` defines 16b/20b shift-count and FIFO-bypass controls, while `TX_LBERT_CTL` defines LBERT mode, error trigger, and pattern fields.
- Lane 2 RX power, VCO calibration, CDR, and DPLL fields: `DIG_RX_PWRCTL_RX_PSTATE_*` and `RX_PWRUP_TIME_*` define RX power-state templates and timing. `RX_VCOCAL_*` controls VCO calibration request, bypass, force, reference-load and VCO-load values, timing, result/status, and binary-window fields. `RX_CDR_*`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_*` expose clock/data recovery, SSC/bypass/update behavior, gain/frequency controls, status, and DPLL frequency boundaries.
- Lane 2 RX adaptation and equalization state: `DIG_RX_ADPTCTL_ADPT_CFG_0` through `ADPT_CFG_9`, reset configuration, ATT/VGA/CTLE/DFE tap status, DFE data/error VDAC offsets, slicer controls, error slicer level, adaptation reset, DAC control selectors, and adaptation CR bank address/data fields describe RX equalization policy and observed adaptation values.
- Lane 2 RX statistic engine: `DIG_RX_STAT_*` registers define sample/load values, data masks, pattern match controls, statistic/correlation source selection, sample counters, statistic counters 0 through 6, calibration-comparison clock control, additional match controls, statistic control 2, and stop control. These are used for PHY debug, pattern matching, and adaptation/statistic sampling rather than normal filesystem-style state.
- Lane 2 MPHY and digital analog override outputs: `DIG_MPHY_RX_PWM_CTL`, `DIG_MPHY_RX_TERM_LS_CTL`, and `DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT` describe MPHY PWM and low-speed termination controls. `DIG_ANA_*` fields expose digital override outputs into analog TX/RX logic: TX override values and enables, TX termination-code overrides, TX EQ overrides, RX control and power overrides, RX VCO overrides, RX calibration/DAC/slicer/AFE/CTLE/scope/IQ controls, analog-change enables, analog status words, RX termination-code overrides, MPHY overrides, signal-detect overrides, TX DCC DAC overrides, and a second TX override word.
- Lane 2 analog TX/RX registers: `DPCSSYS_CR3_LANE2_ANA_TX_*` and `DPCSSYS_CR3_LANE2_ANA_RX_*` describe analog-side measurement overrides, power overrides, alternate/ATB buses, TX DCC DAC and DCC control, TX termination code and control, TX override clocks, TX miscellaneous/reserved words, RX clock controls, CDR deserializer controls, slicer controls, RX power controls, squelch, RX calibration, ATB register/reference/measurement controls, ATB force, and RX reserved state.
- Lane 3 partial digital ASIC and TX power window: the chunk starts lane 3 at `DPCSSYS_CR3_LANE3_DIG_ASIC_LANE_OVRD_IN` and covers lane override, TX override inputs 0 through 5, TX override outputs, RX override output 0, lane ASIC input, TX ASIC inputs/outputs, RX ASIC output 0, TX power-state templates, TX power-up timing, TX DCC bank/DAC interface, TX clock alignment, and TX LBERT.
- Lane 3 partial RX statistic window: the range ends inside `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1`. It fully covers `RX_STAT_LD_VAL_1`, `RX_STAT_DATA_MSK`, and `RX_STAT_MATCH_CTL0`; for `MATCH_CTL1`, the chunk includes the shift fields and the first three masks, while the remaining masks and later lane 3 RX statistic controls are in the next chunk.

Most masks in this range are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these lane-local CR3 blocks. Several registers are full 16-bit data/address words, while many fields are single-bit enables, override-enable bits, clear/start/update bits, acknowledge bits, or compact multi-bit analog calibration values.

## Control Flow

This header has no runtime control flow. It participates in compile-time register access setup:

1. AMD display code for the matching DPCS/DCN generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables use generated names from this header and companion `ixDPCSSYS_*` offsets.
3. Runtime driver code uses register helpers and those tables to read, write, set, clear, poll, or decode hardware fields during PHY bring-up, link training, modeset, diagnostics, interrupt/debug handling, low-power transitions, suspend/resume, and reset recovery.
4. Hardware and firmware state machines perform the actual lane sequencing; this header only names bit positions and masks.

The macros do not encode access type, reset value, polling order, write-one-to-clear behavior, self-clearing behavior, clock-domain restrictions, power-domain validity, or whether a field is read-only, write-only, or reserved.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 lane 2 and lane 3 registers:

- Lane control state includes TX/RX reset, request, data-enable, disable, low-power-detect, pstate, rate, width, MPLL/clock selection, TX cursor coefficients, TX/RX acknowledgement, detect-RX result, loopback/test pattern, OCLA, and lane-master/shift synchronization fields.
- Power sequencing state includes TX/RX power-state templates, reference generator and clock enables, analog reset/serial/data enables, VCM hold, VBOOST, RX detect allowance, DCC compensation calibration, and the timing counters used to sequence those transitions.
- Calibration state includes TX DCC bank/DAC request and acknowledgement, RX VCO calibration request/force/bypass/load/status values, RX CDR/DPLL control/status, RX adaptation policy and status, DFE tap status, slicer and VDAC offsets, RX analog calibration controls, and ATB measurement/force state.
- Statistic/debug state includes RX statistic pattern masks, match controls, source selectors, sample counters, statistic counters, calibration-comparison clock control, stop/start controls, LBERT mode/pattern/error trigger, OCLA enables, analog status words, signal detect overrides, and MPHY PWM/termination debug controls.
- Analog state includes digital override outputs into analog TX/RX blocks, TX/RX termination codes, TX EQ and DCC DAC controls, RX AFE/CTLE/slicer/IQ/phase controls, squelch, RX clocks, RX power controls, and analog test bus selection.

Persistence is hardware-defined. Configuration and override fields generally last until another modeset/link-training sequence, PHY power transition, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, ACK, statistic, calibration, start/update, clear, and handshake fields may be latched, sampled, write-one-to-clear, self-clearing, or valid only when the corresponding lane power and clocks are active. This generated header does not specify those behaviors.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching CR3 register offsets. In that file, the relevant address block is the CR3 DPCS TX/RX indirect register window.
- Lane 2 registers covered here map from the tail of `ixDPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1` at `0x1212` through `ixDPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_2` at `0x1213`, TX power control at `0x1220` through `0x1232`, RX power/VCO/CDR/DPLL/adaptation/statistics at `0x1240` through `0x1297`, digital analog override outputs at `0x12a0` through `0x12c4`, and analog TX/RX registers at `0x12e0` through `0x12ff`.
- Lane 3 starts at `ixDPCSSYS_CR3_LANE3_DIG_ASIC_LANE_OVRD_IN` at `0x1300`, covers the partial digital ASIC region through `0x131e`, TX power control through `ixDPCSSYS_CR3_LANE3_DIG_TX_LBERT_CTL` at `0x1332`, and reaches RX statistic registers from `0x1380` through `ixDPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1` at `0x1383`.
- AMD display link encoder, PHY sequencing, link-training, mode-setting, hotplug, low-power, debug, and reset-recovery paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware/hardware state machines share ownership of many of these fields, especially reset/request handshakes, TX/RX power-state sequencing, RX adaptation, DCC and VCO calibration, CDR/DPLL lock behavior, MPHY PWM/termination paths, analog override paths, and RX statistic/debug sampling.

Behaviorally, this chunk sits below user-facing display code. It describes the bit layout needed to configure, override, and observe CR3 lane 2 and early lane 3 PHY operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts mid-register. `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1` shift definitions and early masks are in the previous chunk; this range only contains the later masks for TX async/VREG/reserved fields.
- The chunk ends mid-register. `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1` still has `PTTRN_CR1A_ADPT_EN_MASK` and `RESERVED_15_12_MASK` immediately after the requested range, and the rest of lane 3 RX statistic controls continue in the next chunk.
- Repeated lane layouts are copy-sensitive. Lane 2 and lane 3 names must pair with their matching `0x12xx` and `0x13xx` offsets; a generator issue can affect one lane while neighboring lanes appear correct.
- Status, request, acknowledge, update, start, clear, and mask-style fields have similar names but different hardware semantics. Using a status mask as a writable control mask, or assuming a request bit is persistent configuration, can create stuck handshakes or misleading debug reads.
- Power-state and timing fields are sequencing-sensitive. Incorrect masks around TX/RX P0/P0s/P1/P2 templates, VCM/VBOOST timing, RX detect allowance, analog reset, data enable, or serial enable can cause link bring-up failures or unstable low-power transitions.
- Calibration and adaptation fields are analog-sensitive. Bad masks for DCC DAC selection, RX VCO load/status, CDR/DPLL controls, AFE/VGA/CTLE/DFE tap status, slicer levels, IQ/phase adjustment, squelch, or termination codes can produce rate-specific display failures, poor eye margins, or incorrect compliance behavior.
- OCLA, LBERT, statistic, ATB, MPHY, and manufacturing-style override fields are intended for debug/test/diagnostic flows. Accidentally enabling them during normal operation can change lane behavior without obvious high-level driver state.
- Reserved masks are emitted. Consumers should not treat reserved fields as safe software-owned configuration fields unless hardware documentation explicitly says so.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that complete fields in this range have consistent `__SHIFT` and `_MASK` pairs, allowing the known boundary exceptions for `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1` at the start and `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1` at the end.
- Cross-check every complete register group against `dpcs_4_2_2_offset.h`, especially lane-local offset spacing: lane 2 around `0x1200` and lane 3 around `0x1300`.
- Diff against AMD's source register database and nearby DPCS generated variants where lane layouts are expected to match.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lane counts, and power states. Expected signals are stable link training, completed RX adaptation/calibration, no stuck reset/request handshakes, and no unexpected lane debug/statistic anomalies.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in TX/RX power control, VCO calibration, CDR/DPLL, RX adaptation, statistic/debug, MPHY, and analog override fields.
- Use register dumps or PHY debug traces during failing links to confirm that TX/RX ACKs, DCC DAC ACK, RX VCO status, CDR status, DPLL frequency bounds, adaptation status, DFE tap values, slicer offsets, statistic counters, analog status words, and ATB/MPHY/OCLA/LBERT controls decode correctly.
- Exercise diagnostic paths where available: OCLA, LBERT, RX statistic matching, DCC bank/DAC access, VCO calibration debug, CDR/DPLL debug, MPHY PWM/termination overrides, analog test bus measurements, signal-detect overrides, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1` and earlier lane 2 digital ASIC override/input fields. This chunk finishes the lane 2 register window through `DPCSSYS_CR3_LANE2_ANA_RX_RESERVED1`, then starts lane 3 and covers its early digital ASIC, TX power/DCC/LBERT, and initial RX statistic registers. The next chunk should finish `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1` and continue the rest of lane 3 RX statistic/debug and later lane 3 PHY fields. The final per-file research document should reconcile these artificial boundaries before making whole-file claims about all DPCS 4.2.2 CR3 lane registers.

### subset-b-002367: lines 71474-73853

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 71474-73853

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic. Its exported surface is a set of preprocessor constants that encode field bit positions (`__SHIFT`) and field masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,119 `#define` entries across 2,380 lines. It is entirely in the CR3 DPCS namespace and spans several adjacent hardware register regions: the lane 3 RX statistic and TX analog tail, the CR3 raw-common digital block, the complete CR3 raw lane 0 register window, and the beginning of CR3 raw lane 1 through `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_DFE_CAL`. The companion offset header maps these groups around lane 3 offsets `0x1384` through `0x13ef`, raw-common offsets `0x2000` through `0x2040`, raw lane 0 offsets `0x3000` through `0x30c8`, and raw lane 1 offsets starting at `0x3100`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main register-field families are:

- Lane 3 RX statistic controls: `DPCSSYS_CR3_LANE3_DIG_RX_STAT_STAT_CTL0/1/2`, `SMPL_CNT1`, `STAT_CNT_0` through `STAT_CNT_6`, `CAL_COMP_CLK_CTL`, `MATCH_CTL2` through `MATCH_CTL5`, and `STAT_STOP`. These fields configure correlation/statistic source selection, statistic counter enables, sample/count completion bits, data delay/scope delay controls, calibration comparator clock counters, pattern/mask words, and the statistic counter stop bit.
- Lane 3 digital TX analog override outputs: `DPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT`, `TX_TERM_CODE_OVRD_OUT`, `TX_TERM_CODE_CLK_OVRD_OUT`, `TX_EQ_OVRD_OUT_0` through `_5`, `ANA_STATUS_0`, `TX_DCC_DAC_OVRD_OUT`, `TX_DCC_DAC_OVRD_OUT_2`, and `TX_OVRD_OUT_2`. These macros name software-visible override, status, equalization, termination, DCC DAC, data-rate, clock, reset, serial-enable, RX-detect, and transmit-coefficient fields.
- Lane 3 analog TX registers: `DPCSSYS_CR3_LANE3_ANA_TX_OVRD_MEAS`, `TX_PWR_OVRD`, `TX_ALT_BUS`, `TX_ATB1/2`, `TX_DCC_DAC`, `TX_DCC_CTRL1`, `TX_TERM_CODE`, `TX_TERM_CODE_CTRL`, `TX_OVRD_CLK`, `TX_MISC1/2/3`, and reserved words. These are analog-adjacent fields for measurement override, power override, alternate test buses, DCC, termination, clock override, and miscellaneous analog TX controls.
- CR3 raw-common digital controls: `DPCSSYS_CR3_RAWCMN_DIG_CMN_CTL`, MPLLA/MPLLB override and bandwidth/SSC registers, lane FSM extension, `CMN_CTL_1`, `MPLL_STATE_CTL`, `TX_CAL_CODE`, `SRAM_INIT_DONE`, `OCLA`, `SUP_ANA_OVRD`, PCS/FW ID codes, and the always-on common RTUNE, SRAM, power-gating, supervisor, VREF, resistor, reference-range, and miscellaneous controls. These fields describe common PLL, supervisor, calibration, debug, firmware identity, and always-on common resources shared by lanes.
- Raw lane 0 PCS transfer and adaptation fields: `DPCSSYS_CR3_RAWLANE0_DIG_PCS_XF_*` covers TX and RX override inputs/outputs, PCS input/output mirrors, RX adaptation ACK/FOM, directed TX pre/main/post cursor feedback, lane number and reserved words, ATE overrides, RX equalization delta/IQ, termination override and input mirrors, RX clock output, RX EQ overrides, and PH2 calibration request/acknowledge fields.
- Raw lane 0 FSM controls: `DPCSSYS_CR3_RAWLANE0_DIG_FSM_*` covers manual FSM override/jump/command control, memory address and status monitors, fast RX startup/adapt/AFE/DFE/bypass/reference/IQ/VCO flows, common MPLL/RCAL status, continuous calibration/adaptation controls, fast flags, CR lock, TX DCC flags/status, OCLA selection, TX EQ update flag, and RX IQ phase offset.
- Raw lane 0 IRQ controls: `DPCSSYS_CR3_RAWLANE0_DIG_IRQ_CTL_*` includes reset-return request, RX reset/request/rate/pstate/adaptation IRQ status, matching clear registers, IRQ masks, lane transceiver-mode IRQs, PH2 calibration IRQs, serial loopback IRQs, DCC on-demand IRQ, and TX reset/request IRQ status and clear fields.
- Raw lane 0 PMA, TX_CTL, RX_CTL, and ATE/debug fields: `PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and late `PCS_XF_*` registers describe PMA/PCS handshakes, lane and supervisor override paths, TX/RX PMA input/output mirrors, RTUNE and MPHY controls, TX FSM/clock/DCC status, RX FSM/LOS/data-enable/off-cancel/adaptation status, OCLA probes, manufacturing/test overrides, master MPLL loop controls, and additional RX/TX override outputs.
- Raw lane 1 beginning: the chunk repeats the CR3 raw-lane schema for `DPCSSYS_CR3_RAWLANE1_*` from PCS TX/RX transfer registers through early FSM fast RX calibration selectors. It ends after `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_DFE_CAL`; the later raw lane 1 FSM, IRQ, PMA, TX_CTL, RX_CTL, and ATE/debug fields continue in the next chunk.

Most masks in this slice are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these blocks. Several fields occupy full 16-bit words, while many hardware-control fields are single-bit enables, status bits, clear bits, or override-value/override-enable pairs.

## Control Flow

This header has no runtime control flow. It participates in compile-time register access setup:

1. AMD display code for the matching DPCS/DCN generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables use generated names from this header and companion `ixDPCSSYS_*` offsets.
3. Runtime driver code uses register helpers and those tables to read, write, set, clear, or update hardware fields during PHY bring-up, link training, modeset, diagnostics, interrupt handling, suspend/resume, and reset recovery.
4. Hardware and firmware state machines perform the actual lane/common sequencing; this header only names bit positions and masks.

The macros do not encode access type, reset value, polling order, write-one-to-clear behavior, self-clearing behavior, clock-domain restrictions, power-domain validity, or whether a field is read-only, write-only, or reserved.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 lane, common, and raw-lane registers:

- Lane 3 RX statistic state includes statistic/correlation selector configuration, counter enables, sample/count completion indicators, pattern matching words, data masks, calibration comparator timing, validity-loss clear/control, and statistic stop state.
- Lane 3 analog TX state includes override values and enables for TX clocks, data enable, reference generation, VCM hold, MPLL clocks, reset, serial enable, data rate, divide-by-4, RX detect, termination codes, driver source, equalization taps, DCC DAC controls, power override, test buses, and miscellaneous analog controls.
- Raw-common state includes common control bits, MPLLA/MPLLB override and SSC configuration, lane FSM extension controls, MPLL state control, TX calibration code, SRAM initialization status, OCLA selection, supervisor analog override state, PCS/firmware ID code words, always-on common RTUNE values for RX/TX down/up paths, SRAM block configuration, power-gating overrides, VREF stats, resistor overrides, reference range, and miscellaneous configuration.
- Raw lane 0 state includes PCS TX/RX reset/request/width/rate/pstate/MPLL/loopback/data-enable handshakes, RX adaptation ACK/FOM and directed TX coefficient feedback, ATE override paths, equalization and termination controls, PH2 calibration, FSM status and fast-flow selectors, lane IRQ latches/masks/clears, PMA handshakes, TX/RX local controls, and late ATE/debug output controls.
- Raw lane 1 state in this chunk is partial: PCS TX/RX transfer, RX adaptation, equalization/termination/PH2, ATE overrides, and early FSM fast RX calibration/adaptation fields are covered, but the rest of lane 1's FSM and downstream blocks are outside the requested line range.

Persistence is hardware-defined. Configuration and override fields generally last until another modeset/link-training sequence, PHY power transition, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, ACK, IRQ, calibration, clear, and handshake fields may be latched, sampled, write-one-to-clear, self-clearing, or valid only when the corresponding common/lane power and clocks are active. This generated header does not specify those behaviors.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching CR3 offsets.
- Lane 3 RX statistic registers in this chunk map from `ixDPCSSYS_CR3_LANE3_DIG_RX_STAT_STAT_CTL0` at `0x1384` through `ixDPCSSYS_CR3_LANE3_DIG_RX_STAT_STAT_STOP` at `0x1394`; their earlier load/data/match setup registers are just before this chunk.
- Lane 3 digital and analog TX registers covered here map through `ixDPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT` at `0x13a0`, digital analog TX fields through `0x13c4`, and analog TX controls from `0x13e0` through `0x13ef`.
- CR3 raw-common fields map from `ixDPCSSYS_CR3_RAWCMN_DIG_CMN_CTL` at `0x2000` through `ixDPCSSYS_CR3_RAWCMN_DIG_AON_CMN_MISC_CONF_IN_1` at `0x2040`.
- CR3 raw lane 0 uses the full lane window: PCS at `0x3000` through `0x301f`, FSM at `0x3020` through `0x303f`, IRQ at `0x3040` through `0x305b`, PMA at `0x3060` through `0x306c`, TX_CTL at `0x3080` through `0x3084`, RX_CTL at `0x30a0` through `0x30a5`, and late ATE/PCS fields at `0x30c0` through `0x30c8`.
- CR3 raw lane 1 begins at `0x3100`; this chunk reaches `ixDPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_DFE_CAL` at `0x3126`.
- AMD display link encoder, PHY sequencing, link-training, mode-setting, hotplug, low-power, debug, and interrupt paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware and hardware state machines share ownership of many fields, especially PLL/SSC controls, reset/request handshakes, RX adaptation, DCC and RTUNE calibration, PH2 calibration, PMA/PCS handshakes, lane IRQs, and ATE/test overrides.

Behaviorally, this chunk sits below user-facing display code. It describes the bit layout needed to configure and observe CR3 lane 3, CR3 common resources, and CR3 raw lanes during display PHY operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts immediately after `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1`; the preceding RX statistic load, data mask, and first pattern-match controls are in the previous chunk.
- The chunk ends immediately before `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_BYPASS_CAL`; raw lane 1's remaining FSM, IRQ, PMA, TX_CTL, RX_CTL, and late ATE/PCS registers are in the next chunk.
- Repeated lane layouts are copy-sensitive. A generator issue can affect one lane while neighboring lanes appear correct; CR3 lane 3, raw lane 0, and raw lane 1 names must pair with their matching offsets and tables.
- Status, clear, and mask registers use similar field names. Mixing IRQ status masks with clear or interrupt-mask masks can drop events, leave stale events latched, or create repeated interrupts.
- PCS, PMA, and analog override fields can bypass normal hardware sequencing. Bad masks around reset, request, data-enable, loopback, MPLL selection, termination, RTUNE, RX adaptation, PH2 calibration, ATE, TX DCC, or TX equalization controls can leave a lane in a state higher-level display code cannot reason about.
- Common PLL, SSC, SRAM, power-gating, VREF, resistor, and RTUNE fields are shared resources. Wrong masks here can affect multiple lanes rather than only the local lane being debugged.
- FSM fast-flow and calibration bits are sequencing-sensitive. Incorrect masks for fast RX startup/adapt/AFE/DFE/bypass/reference/IQ/VCO/common calibration or continuous calibration flags can cause link training failure, poor equalization, unstable links, or stuck polling loops.
- Reserved masks are still emitted. Consumers should not treat reserved fields as safe software-owned configuration fields unless hardware documentation explicitly says so.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that complete registers in this range have consistent `__SHIFT` and `_MASK` pairs, allowing the known cross-chunk boundaries before `DPCSSYS_CR3_LANE3_DIG_RX_STAT_STAT_CTL0` and after `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_DFE_CAL`.
- Cross-check every complete register group against `dpcs_4_2_2_offset.h`, especially lane/common address windows: lane 3 around `0x1384` to `0x13ef`, raw common around `0x2000`, raw lane 0 around `0x3000`, and raw lane 1 around `0x3100`.
- Diff against AMD's source register database and nearby DPCS generated variants where lane layouts are expected to match.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lanes, and power states. Expected signals are stable link training, completed RX adaptation, no stuck reset/request handshakes, no unexpected lane IRQs, and valid common PLL/RTUNE/SRAM status.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in RX statistic, analog TX, raw-common, PCS, FSM, IRQ, PMA, TX_CTL, RX_CTL, and ATE fields.
- Use register dumps or PHY debug traces during failing links to confirm that RX statistic counters, lane 3 TX analog overrides, MPLL/SSC state, RTUNE values, RX adaptation ACK/FOM, directed TX coefficient feedback, DCC status, FSM state, CR lock, IRQ clear/mask bits, PH2 calibration, OCLA probes, and ATE overrides decode correctly.
- Exercise diagnostic paths where available: RX statistic sampling, OCLA and UPCS OCLA, serial loopback, RX adaptation debug, PH2 calibration, DCC on-demand IRQs, common calibration, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the beginning of the CR3 lane 3 RX statistic sequence, including load value, data mask, and `MATCH_CTL0/1`. This chunk starts at `STAT_CTL0`, finishes lane 3 RX statistic and TX analog fields, covers the CR3 raw-common block and all CR3 raw lane 0, then starts raw lane 1 through early FSM fast RX calibration selectors. The next chunk should continue raw lane 1 at `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_BYPASS_CAL` and reconcile the rest of lane 1's raw-lane window. The final per-file research document should merge these artificial boundaries before making whole-file claims about all DPCS 4.2.2 CR3 registers.

### subset-b-002368: lines 73854-76243

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 73854-76243

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY control/status registers. It contains no executable logic; its exported interface is a set of preprocessor constants that describe bit positions and masks for indirect DPCS hardware registers.

The requested range contains 2,103 `#define` entries across 2,390 lines. It is within the CR3 raw-lane register space and spans the tail of raw lane 1, all raw lane 2, and the early/middle portion of raw lane 3. The range starts inside `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL`, continues through raw lane 1 FSM/IRQ/PMA/TX/RX/ATE fields, covers the complete raw lane 2 PCS/FSM/IRQ/PMA/TX/RX/ATE layout, then covers raw lane 3 PCS and FSM fields plus IRQ status/clear fields through the shift definitions for `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR`.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, direct MMIO accesses, or callbacks in this range. The API surface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position in a DPCS indirect register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main register-field families are:

- Raw lane 1 FSM tail: `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL` starts just before the chunk and is completed here, followed by fast RX DFE/bypass/reference-level/IQ calibration, AFE/DFE adaptation, fast supervisor/TX common-mode/TX RX-detect/RX power-up/RX VCO wait/RX VCO calibration controls, common MPLL and RCAL status, continuous RX calibration/adaptation/data/phase/AFE controls, `FAST_FLAGS`, CR register/memory lock bits, TX DCC flags/status, OCLA selection, TX EQ update flag, and RX IQ phase offset.
- Raw lane 1 IRQ controls: `RESET_RTN_REQ`, RX reset/request/rate/pstate/adaptation request/adaptation disable IRQ status bits, matching clear registers, `IRQ_MASK`, `IRQ_MASK_2`, lane transceiver-mode IRQs, PH2 calibration request/disable IRQs, serial loopback IRQs, DCC on-demand IRQ, and TX reset/request IRQ status and clear bits.
- Raw lane 1 PMA/TX/RX/ATE tail: PMA transfer fields for lane/supervisor/TX/RX override paths, RTUNE, MPHY override in/out, RX adaptation override out, TX FSM/clock/DCC/OCLA controls, RX FSM/LOS/data-enable/off-cancel/adaptation/UPCS OCLA controls, and late PCS ATE override registers for RX/TX manufacturing/test paths and master MPLL loop controls.
- Complete raw lane 2 PCS window: `DPCSSYS_CR3_RAWLANE2_DIG_PCS_XF_*` covers TX override inputs, TX PCS input/output mirrors, RX override inputs, RX PCS inputs/outputs, RX adaptation ACK/FOM, directed TX pre/main/post coefficient feedback, lane number and reserved words, ATE overrides, RX EQ delta/IQ override, TX/RX termination controls, RX clock output, RX EQ override controls, and PH2 calibration request/acknowledge.
- Complete raw lane 2 FSM/IRQ/PMA/TX/RX/ATE window: lane 2 repeats the same FSM, IRQ, PMA transfer, TX control, RX control, and late ATE/PCS register schema described for lane 1, with `RAWLANE2` names and offsets in the `0x3200` lane window.
- Raw lane 3 partial window: lane 3 starts at `PCS_XF_TX_OVRD_IN` and continues through PCS TX/RX override/input/output, RX adaptation, lane number, ATE/EQ/termination/PH2, FSM controls/status/calibration flags, CR lock, DCC/OCLA/EQ-update/RCAL/IQ fields, and IRQ status/clear registers through `RX_PSTATE_IRQ_CLR` shift definitions. The masks for that final register and the rest of lane 3 IRQ/PMA/TX/RX/ATE tail are outside this chunk.

Most fields are 16-bit DPCS register fields and use hexadecimal masks with an `L` suffix. Many control, status, clear, and mask registers are single-bit fields with a `RESERVED_15_1` mask; wider fields include full 16-bit words, packed override-value/override-enable pairs, state monitor bits, multi-bit IRQ mask words, and packed calibration/debug flags.

## Control Flow

This header has no runtime control flow. It participates in compile-time hardware-register description:

1. AMD display code for the DPCS/DCN generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Generated register tables or register-helper macros pair `ixDPCSSYS_*` offsets with the `__SHIFT` and `_MASK` constants from this file.
3. Runtime driver paths use those constants when reading, writing, updating, masking, clearing, or decoding raw-lane PHY registers during link bring-up, training, modeset, reset recovery, diagnostics, and interrupt handling.
4. The actual sequencing is performed by driver code, firmware, and hardware state machines; this chunk only names bit layouts.

The macros do not encode access permissions, reset values, polling order, self-clearing behavior, write-one-to-clear behavior, clock-domain restrictions, power-domain validity, or reserved-bit ownership.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 raw-lane registers:

- PCS state: TX/RX reset and request override paths, pstate/rate/width/MPLL selection fields, beacon/loopback/data-enable controls, PCS input/output mirrors, RX adaptation request/disable/ACK/FOM, directed TX coefficient feedback, lane-number fields, ATE overrides, RX equalization overrides, termination controls, RX clock output, and PH2 calibration handshakes.
- FSM state: manual FSM override controls, state and command readiness monitors, memory address monitor, fast startup/adaptation/calibration selectors, common MPLL and RCAL completion status, continuous calibration/adaptation selectors, CR locks, TX DCC flags/status, TX EQ update flag, OCLA probe selection, and RX IQ phase offset.
- IRQ state: latched RX/TX reset/request events, RX rate and pstate events, RX adaptation request/disable events, lane transceiver-mode events, PH2 calibration events, serial loopback events, DCC on-demand events, reset-return request bits, clear registers, and mask registers.
- PMA transfer state: lane and supervisor override inputs/outputs, TX/RX PMA handshake fields, RTUNE control, MPHY PWM/termination override in/out paths, and RX adaptation override outputs.
- TX/RX local control state: TX FSM and clock controls, TX DCC continuous status, OCLA/UPCS OCLA probe selection, RX FSM control, LOS masking, RX data-enable override timing, off-cancel continuous status, and adaptation continuous status.
- ATE/debug state: manufacturing/test override enables and values for RX/TX control paths, RX calibration/equalization fields, TX data/data-valid paths, master MPLL loop controls, and extra RX/TX override outputs.

Persistence is hardware-defined. Configuration and override fields generally remain until driver/firmware reprogramming, modeset/link-training changes, PHY power transitions, suspend/resume, GPU reset, ASIC reset, or display-engine reinitialization. Status, ACK, IRQ, calibration, handshake, and clear fields may be latched, sampled, self-clearing, write-one-to-clear, or valid only while the relevant lane power and clocks are active. This generated header does not specify those semantics.

## Dependencies And Integration Points

This generated file must remain synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_CR3_RAWLANE*` offsets for the registers described here.
- Raw lane 1 coverage starts mid-FSM at offsets around `0x3125`, continues through IRQ registers at `0x3140`-`0x315b`, PMA transfer at `0x3160`-`0x316c`, TX control at `0x3180`-`0x3184`, RX control at `0x31a0`-`0x31a5`, and late PCS/ATE fields at `0x31c0`-`0x31c8`.
- Raw lane 2 is the complete lane-local layout: PCS at `0x3200`-`0x321f`, FSM at `0x3220`-`0x323f`, IRQ at `0x3240`-`0x325b`, PMA at `0x3260`-`0x326c`, TX control at `0x3280`-`0x3284`, RX control at `0x32a0`-`0x32a5`, and late PCS/ATE at `0x32c0`-`0x32c8`.
- Raw lane 3 coverage starts with PCS at `0x3300`, covers FSM through `0x333f`, and reaches IRQ clear state around `0x334a`; later lane 3 IRQ masks, PMA, TX control, RX control, and late PCS/ATE fields continue after this range.
- AMD display link encoder, PHY, link-training, hotplug, modeset, low-power, debug, and interrupt paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware and hardware state machines share ownership of many fields, especially reset/request handshakes, RX adaptation, DCC and RTUNE calibration, PH2 calibration, PMA/PCS handshakes, lane IRQs, and ATE/test overrides.

Behaviorally, this chunk sits below user-facing display code. It defines the bit layout needed to configure, observe, and debug CR3 raw lanes during display PHY operation.

## Risks And Edge Cases

- The constants are untyped preprocessor macros. A wrong shift or mask can compile cleanly while updating the wrong bit, corrupting reserved bits, or decoding status incorrectly.
- This is generated hardware metadata. Manual edits risk divergence from AMD's source register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts mid-register. `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL__FAST_RX_AFE_CAL__SHIFT` is in the previous chunk, while this chunk contains the reserved shift and masks.
- The chunk ends mid-register. `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` masks continue after line 76243.
- Repeated lane layouts are copy-sensitive. Lane 1, lane 2, and lane 3 names must stay paired with their matching offset windows; an off-by-one lane or `CR` instance mismatch can target a different physical lane.
- Status, clear, and interrupt-mask registers have similar names. Mixing status masks with clear or mask-register fields can lose events, leave stale events latched, or create repeated interrupts.
- PCS and PMA override fields can bypass normal hardware sequencing. Bad masks around reset, request, data-enable, loopback, MPLL selection, termination, RTUNE, RX adaptation, PH2 calibration, or ATE controls can leave a lane in an unexpected electrical or protocol state.
- FSM fast-flow and calibration bits are sequencing-sensitive. Incorrect masks for fast RX startup/adapt/AFE/DFE/bypass/reference/IQ/VCO/common calibration or continuous calibration flags can cause link training failure, unstable links, stuck polling loops, or misleading debug dumps.
- Reserved masks are emitted alongside real fields. Consumers should not treat reserved bits as software-owned unless the hardware database or documentation explicitly allows it.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated tables are initialized.
- Mechanically verify that every complete register group in this range has matching `__SHIFT` and `_MASK` entries, allowing the known start boundary in `RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL` and the end boundary in `RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR`.
- Cross-check all complete register names against `dpcs_4_2_2_offset.h`, especially lane-local spacing around `0x3100`, `0x3200`, and `0x3300`.
- Diff this generated slice against AMD's authoritative register database and nearby DPCS variants where the raw-lane schema is expected to match.
- Exercise DisplayPort and HDMI link bring-up across supported rates, widths, lane counts, and power states. Expected signals include stable link training, completed RX adaptation, no stuck reset/request handshakes, and no unexpected lane IRQs.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in PCS, FSM, IRQ, PMA, TX control, RX control, and ATE fields.
- Use register dumps or PHY debug traces during failures to confirm that RX adaptation ACK/FOM, directed TX coefficient feedback, DCC status, FSM state, CR lock, IRQ clear/mask bits, RTUNE handshakes, PH2 calibration, OCLA probes, and ATE overrides decode correctly.
- Exercise diagnostic paths where available: OCLA and UPCS OCLA, serial loopback, RX adaptation debug, PH2 calibration, DCC on-demand IRQs, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL` and the earlier raw lane 1 PCS/FSM fields. This chunk completes the lane 1 tail, fully covers raw lane 2, and starts raw lane 3 through the early IRQ clear registers. The next chunk should complete `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` and continue through the remaining lane 3 IRQ masks, PMA transfer, TX control, RX control, and late PCS/ATE fields. The final per-file research document should reconcile these artificial boundaries before making whole-file claims about all DPCS 4.2.2 CR3 raw-lane registers.

### subset-b-002369: lines 76244-78674

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 76244-78674

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY registers. It contains no executable C logic; its exported surface is preprocessor metadata that names bit positions and masks for DPCS indirect hardware fields.

The requested range contains 2,080 `#define` entries across 2,431 lines and 351 register-comment groups. It is in the CR3 DPCS register namespace. The first part finishes the CR3 raw lane 3 digital IRQ/PMA/TX/RX/ATE control window. The larger second part starts the CR3 raw always-on lane window and covers raw AON lanes 0, 1, 2, and the beginning of lane 3. The chunk starts mid-register in `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR`, where only masks are present in this range, and it ends mid-register in `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL`, where only shifts are present in this range.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a field inside its hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main register-field families are:

- CR3 raw lane 3 IRQ control: `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_*` provides clear, status, and mask fields for RX pstate/rate/adaptation events, RX reset/request, lane transceiver-mode changes, PH2 calibration request/disable events, RX-to-TX serial loopback, DCC on-demand events, and TX reset/request events. The aggregate mask registers split RX/lane events in `IRQ_MASK` and TX events in `IRQ_MASK_2`.
- CR3 raw lane 3 PMA transfer and override fields: `PMA_XF_LANE_OVRD_IN/OUT`, `SUP_OVRD_IN`, `SUP_PMA_IN`, `TX_OVRD_OUT`, `TX_PMA_IN`, `RX_OVRD_OUT`, `RX_PMA_IN`, `LANE_RTUNE_CTL`, `SUP_PMA_IN_1`, `MPHY_OVRD_IN/OUT`, and `RX_ADAPT_OVRD_OUT` describe lane MPLL enables, supervisor MPLL state, TX request/reset/beacon/async/data-enable overrides, RX request/reset/AFE/DFE/data/path overrides, RTUNE handshakes, MPHY PWM/termination override paths, and RX adaptation acknowledge or command overrides.
- CR3 raw lane 3 local TX/RX controls: `TX_CTL_*` and `RX_CTL_*` cover TX FSM and clock controls, TX DCC continuous status, OCLA/UPCS OCLA probe enables, RX FSM enable/rate-change behavior, RX loss-of-signal mask timing, RX data-enable override timing, and off-cancel/adaptation continuous status.
- CR3 raw lane 3 late PCS/ATE controls: `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN_1`, `PCS_XF_MASTER_MPLL_LOOP`, `PCS_XF_ATE_RX_OVRD_IN_1/2/3`, `PCS_XF_RX_OVRD_OUT_2`, and `PCS_XF_TX_OVRD_IN_2` expose manufacturing/test override values and enables for RX rate/width/pstate/LPD/loopback, TX pstate/rate/width/MPLL selection, boost/beacon/async/serial-loopback/data controls, master MPLL loop enables, RX LOS/adaptation/continuous controls, VCO/reference load overrides, RX valid override, and additional TX data/async data overrides.
- CR3 raw AON lane 0 through lane 2 complete windows: each `DPCSSYS_CR3_RAWAONLANE{0,1,2}_DIG_*` group repeats the same always-on lane schema. It includes AFE/CTLE IDAC offsets, RX IQ/adaptation figure-of-merit, DFE summer/phase/data/bypass/error offsets, even/odd reference levels, RX phase-adjust linear/map values, MPLLA/MPLLB coarse tune, power-up done bits, RX adaptation values for ATT/VGA/CTLE/DFE taps 1-5, adaptation done status, fast calibration flags, slicer controls, common calibration MPLL/RCAL status, eight generic adaptation control words, MPLL disable bits, continuous fast flags, TX/RX disable overrides, RX LOS mask control, signal-detect filter control, RX PMA stats, RX PMA squelch/termination/sigdet overrides, RX sigdet calibration and code fields, VREF generator enable, calibration code registers, RX DCC calibration code words, TX DCC bank address/data/control, MPLL background control, sigdet output override/input mirrors, firmware MM/adaptation/calibration config words, lane transceiver-mode override/input mirrors, RX sigdet config, and TX DCC config.
- CR3 raw AON lane 3 partial window: the range begins the lane 3 AON schema at `AFE_ATT_IDAC_OFST` and continues through adaptation, DFE, fast flags, common calibration, TX/RX disable, LOS/sigdet/stat fields, and RX PMA override groups. It stops after the shift half of `RX_SIGDET_CAL`; the masks and later lane 3 AON groups are outside this chunk.

Most fields are 16-bit DPCS register fields with an `L`-suffixed mask. Many status/control fields are single-bit, while calibration and adaptation values often occupy 5, 6, 7, 8, 10, 12, 13, or full 16-bit field widths. A repeated pattern in override registers is `<signal>_OVRD_VAL` paired with `<signal>_OVRD_EN`, where the enable bit decides whether the override value bypasses normal hardware or firmware sequencing.

## Control Flow

This header has no runtime control flow. It participates in compile-time register access setup:

1. AMD display code for the matching DPCS/DCN generation includes this shift/mask header with the companion DPCS 4.2.2 offset header.
2. Generated register tables, macros, and helper code pair these `__SHIFT` and `_MASK` values with `ixDPCSSYS_*` register offsets.
3. Runtime driver paths use those tables through register helpers to read, compose, update, poll, clear, or mask hardware fields during PHY bring-up, link training, modeset, hotplug handling, diagnostics, low-power transitions, suspend/resume, and reset recovery.
4. Hardware and firmware state machines perform the actual PHY sequencing; this chunk only names the bit layout consumed by those paths.

The macros do not encode access type, reset value, write-one-to-clear behavior, self-clearing behavior, polling order, clock-domain restrictions, power-domain validity, or whether a field is read-only, write-only, or reserved.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 raw lane and raw always-on lane registers:

- IRQ state includes latched lane events, clear bits, and interrupt mask bits for RX request/reset/rate/pstate/adaptation events, PH2 calibration events, loopback events, lane transceiver-mode changes, DCC on-demand signals, and TX reset/request signals.
- Raw lane PMA/PCS state includes reset/request handshakes, rate/width/pstate/LPD controls, data-enable and async paths, serial and parallel loopback controls, MPLL selection and loop controls, RTUNE controls, MPHY override paths, TX/RX PMA handshakes, RX LOS/adaptation controls, and ATE overrides.
- TX/RX control state includes local FSM enables, TX clock controls, DCC continuous status, OCLA probe selection, RX LOS masking, RX data-enable override timing, and continuous off-cancel/adaptation status.
- Raw AON lane state includes analog-adjacent tuning and telemetry for AFE/CTLE/DFE/IQ/phase adjustment, adaptation values and completion, common calibration completion, fast and continuous calibration selectors, DCC calibration code storage, signal-detect filtering and calibration, VREF/squelch/termination controls, firmware configuration words, and lane transceiver-mode overrides.

Persistence is hardware-defined. Override and configuration fields generally remain until another link-training or modeset sequence, PHY power transition, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, ACK, IRQ, calibration, clear, and handshake fields may be latched, sampled, write-one-to-clear, self-clearing, or valid only while the corresponding lane, always-on domain, and clocks are active. This generated header does not specify those behaviors.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching `ixDPCSSYS_*` offsets for CR3 raw lane and raw AON lane registers.
- AMD display link encoder, PHY sequencing, link-training, mode-setting, hotplug, low-power, debug, and interrupt paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware and hardware state machines share ownership of many fields in this chunk, especially IRQ clear/mask fields, reset/request handshakes, RX adaptation, DCC and RTUNE calibration, PH2 calibration, PMA/PCS handshakes, lane transceiver-mode controls, signal-detect calibration, and ATE/debug overrides.
- The raw AON lane groups are repeated for lanes 0, 1, 2, and 3. Correct integration depends on each lane's mask names pairing with the same lane's offsets and not with neighboring raw lane or AON lane windows.
- The chunk is source-tree-aligned with the generated AMD header, not with any Ceph subsystem. Consumers should treat it as GPU display register metadata even though it lives inside the mirrored source tree under `sources/distributed-fs/ceph-client`.

Behaviorally, this chunk sits below user-facing display code. It describes the bit layout needed to configure, observe, and debug CR3 PHY lane behavior during display link operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong hardware field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts mid-register. `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` shift definitions are immediately before the requested range; this range only contains its two masks.
- The chunk ends mid-register. `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL` masks are immediately after the requested range; this range only contains its shift definitions.
- Status, clear, and mask registers use similar field names. Mixing IRQ status masks with clear or interrupt-mask masks can leave stale events latched, drop events, or create repeated interrupts.
- Override registers can bypass normal hardware sequencing. Bad masks around TX/RX reset, request, data enable, async, loopback, MPLL selection, termination, RTUNE, RX adaptation, PH2 calibration, signal detect, or ATE controls can leave a display PHY lane in a state that higher-level code cannot reason about.
- The raw AON groups are copy-sensitive. A generator issue in one lane can be hard to notice because adjacent lanes have nearly identical names and masks.
- Calibration fields are sequencing-sensitive. Incorrect masks for fast calibration flags, DCC codes, VREF/sigdet calibration, DFE/CTLE/IQ adaptation, common MPLL/RCAL status, or TX DCC bank controls can cause link training failure, unstable links, blank displays, rate-specific failures, compliance failures, or misleading debug traces.
- Reserved masks are emitted alongside real fields. Consumers should not treat reserved fields as software-owned configuration unless hardware documentation explicitly allows it.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify complete register groups in this range have matching `__SHIFT` and `_MASK` pairs, allowing the known boundary exceptions for `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` at the start and `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL` at the end.
- Cross-check the complete CR3 raw lane 3 and raw AON lane 0-2 groups against `dpcs_4_2_2_offset.h` and against nearby generated DPCS variants where repeated lane layouts should match.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lanes, and power states. Expected signals are stable link training, completed RX adaptation, no stuck reset/request handshakes, no unexpected lane IRQs, and plausible AON lane calibration/status readings.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in IRQ, PMA, TX_CTL, RX_CTL, ATE, and AON calibration fields.
- Use register dumps or PHY debug traces during failing links to confirm that IRQ clear/mask bits, RX adaptation ACK/FOM, DCC status and codes, common calibration done bits, RTUNE handshakes, PH2 calibration, signal-detect calibration, OCLA probes, lane transceiver-mode mirrors, and ATE overrides decode correctly.
- Exercise diagnostic paths where available: OCLA and UPCS OCLA, serial or parallel loopback, RX statistic/adaptation debug, PH2 calibration, DCC on-demand IRQs, signal-detect/VREF calibration, TX DCC bank access, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the `__SHIFT` half of `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` and earlier CR3 raw lane 3 IRQ state. This chunk continues CR3 raw lane 3 through its IRQ/PMA/TX/RX/ATE tail, fully covers raw AON lanes 0 through 2, and starts raw AON lane 3. The next chunk should finish `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL` masks and continue the remaining raw AON lane 3 signal-detect, VREF, calibration-code, DCC, firmware-config, and lane-mode fields. The final per-file research document should reconcile these artificial line boundaries before making whole-file claims about all DPCS 4.2.2 CR3 lane registers.

### subset-b-002370: lines 78675-81068

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 78675-81068

## Purpose

This chunk is part of the generated AMD DPCS 4.2.2 register bitfield header. It defines `*_SHIFT` and `*_MASK` constants for DPCSSYS CR3 registers, with no executable code, structs, or functions. The constants describe how callers pack and extract fields from 16-bit DPCS PHY/control registers when using the matching register-offset header.

The range starts in the tail of `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL`, then covers the remaining CR3 raw always-on lane 3 fields, the lane-X raw always-on fields, shared/supervisor `SUPX` PLL and analog control fields, and the beginning of lane-X ASIC-facing TX/RX interface fields.

## Important APIs, Types, And Macros

The API surface is macro-only:

- `DPCSSYS_CR3_*__FIELD__SHIFT` gives the least significant bit position for a hardware register field.
- `DPCSSYS_CR3_*__FIELD_MASK` gives the bit mask for that field.
- Reserved fields are explicitly represented as `RESERVED...` masks/shifts, which helps generated register tables preserve full register layout even when driver code should not write those bits.

Main register groups covered:

- `DPCSSYS_CR3_RAWAONLANE3_DIG_*`: lane 3 RX signal-detect calibration, VREF generator enable, calibration code latches, RX/TX DCC calibration/bank controls, MPLL bandgap timing, signal-detect overrides, firmware configuration fields, lane transceiver mode, and RX signal-detect filter configuration.
- `DPCSSYS_CR3_RAWAONLANEX_DIG_*`: lane-indexed common form of adaptation and calibration state, including AFE/CTLE offsets, RX IQ/FOM/adaptation values, DFE tap and slicer controls, MPLL/RCAL status, `ADPT_CTL_0..7`, fast flags, LOS/signal-detect filtering, statistics, RX override outputs, DCC controls, firmware configuration, and lane mode fields.
- `DPCSSYS_CR3_SUPX_DIG_*`: shared/supervisor digital controls for ID code, reference clock overrides, MPLLA/MPLLB override inputs, SSC peak and step-size fields, charge-pump controls, supervisor/prescaler/lane-level controls, ASIC input mirrors, MPLL power-control status/timers/calibration, RTUNE configuration/status/set values, and digital-to-analog override outputs.
- `DPCSSYS_CR3_SUPX_ANA_*`: shared analog controls for prescaler, RTUNE, bandgap, MPLLA/MPLLB misc/override/ATB/control/reserved registers, and switch power measurement.
- `DPCSSYS_CR3_LANEX_DIG_ASIC_*`: lane-X ASIC bridge fields for lane loopback, TX override input/output, RX override input/output, TX ASIC input/output, RX ASIC input, and RX equalization ASIC input fields.

There are no local C types. Consumers normally combine these field constants with offset macros from `dpcs_4_2_2_offset.h`, such as `ixDPCSSYS_CR3_RAWAONLANEX_DIG_ADPT_CTL_0`, `ixDPCSSYS_CR3_SUPX_DIG_MPLLA_OVRD_IN_0`, and `ixDPCSSYS_CR3_LANEX_DIG_ASIC_TX_ASIC_IN_0`.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time token substitution:

1. A display or DMUB register helper names a register and field.
2. Helper macros such as `FD_SHIFT(reg, field)` and `FD_MASK(reg, field)` concatenate tokens into `reg__field__SHIFT` and `reg__field_MASK`.
3. The constants in this header provide the numeric shift/mask pair used to build or decode MMIO register values.
4. The matching offset macro supplies the register address, while the DC resource layer supplies the DPCS base segment for the ASIC instance.

This makes spelling and bit-position stability part of the ABI between generated ASIC headers and hand-written display code.

## State And Persistence Behavior

The file itself has no persistent state. It documents hardware state that persists in DPCS registers until hardware reset, power-gating, firmware action, or later MMIO writes change it. The fields in this chunk cover several state classes:

- Calibration and adaptation latches: RX signal-detect thresholds/codes, DCC calibration codes, IOFF/ICONST/VREFGEN codes, RX adaptation values, DFE tap values, slicer controls, FOM/statistics, and common calibration status.
- Override state: lane/TX/RX override enable/value pairs, MPLLA/MPLLB override inputs, reference clock/divider/HDMI clock overrides, analog override outputs, and ASIC bridge override controls.
- Power/clock/PLL state: MPLLA/MPLLB enable, dividers, standby, VCO/fractional-N/SSC fields, power-control status/timers, bandgap and RTUNE controls.
- Link lane operational state: TX/RX reset, invert, data enable, request/ack, low-power disable, pstate, rate, width, termination, CDR tracking/SSC, alignment, equalization, and detect-RX result fields.

Because many registers include both value and `*_OVRD_EN` bits, stale override enables can force PHY behavior after the intended programming sequence has ended. Callers need to explicitly clear override enables when handing control back to normal hardware or firmware sequencing.

## Dependencies

Direct dependencies are generated-header conventions rather than C includes:

- `dpcs_4_2_2_offset.h` supplies the matching `ix...` register addresses. In the companion offset file, this chunk's RAWAONLANEX registers occupy the `0x701c..0x7051` range, SUPX registers occupy the `0x8000..0x8096` range, and LANEX ASIC bridge registers begin at `0x9000`.
- AMD display register helper macros consume these names through token concatenation, including patterns like `FD_SHIFT(reg_name, field)`, `FD_MASK(reg_name, field)`, `FN(reg_name, field)`, and register update/read helpers.
- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and this shift/mask header for DCN 3.1.5 resource setup, alongside DPCS base segment definitions.
- Neighbor generated headers for DPCS 4.2.0, DPCS 4.2.3, and DCN 4.1.0 contain the same logical register families with formatting and mask-width differences, so cross-version copy or regeneration must preserve the target ASIC's exact constants.

## Integration Points

The chunk integrates into the AMDGPU display stack as a register-definition source for Display Core and DMUB code. It is not called directly; instead, it enables generic register access code to remain readable by spelling fields symbolically. For example, a caller can name a DPCS register field such as `DPCSSYS_CR3_SUPX_DIG_MPLLA_OVRD_IN_0__MPLLA_EN` indirectly through helper macros and get the correct DPCS 4.2.2 mask and shift at compile time.

Hardware integration points represented by the fields include:

- Display PHY lane signal detection and loss-of-signal filtering.
- RX adaptation/DFE/equalization telemetry and controls.
- MPLLA/MPLLB clock generation, spread-spectrum clocking, PLL power sequencing, and status reporting.
- Analog PHY blocks such as bandgap, RTUNE, prescaler, charge pump, and MPLL analog controls.
- ASIC-to-lane handshake signals for TX/RX request, acknowledgement, reset, data enable, low-power state, pstate/rate/width, termination, CDR, alignment, loopback, and equalization.

## Risks And Edge Cases

- Incorrect shift or mask values can silently program the wrong PHY bits, causing link training failures, display hotplug instability, bad PLL programming, or broken low-power transitions.
- Several fields are tightly coupled value/enable override pairs. Setting a value without its enable bit has no effect; leaving the enable bit set can keep hardware forced into a diagnostic or firmware-bypass state.
- Reserved masks are present but should not be treated as writable feature bits. Read-modify-write helpers must preserve reserved bits unless hardware documentation says otherwise.
- The range begins and ends mid-register: line 78675 starts with masks for `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL`, whose shift definitions are just before the chunk, and line 81068 ends after the first two shifts for `DPCSSYS_CR3_LANEX_DIG_ASIC_RX_EQ_ASIC_IN_1`, whose remaining fields continue later. Merge/reconciliation must keep neighboring chunks together for full per-register analysis.
- Cross-ASIC headers are similar but not identical. DPCS 4.2.3 uses shorter-looking 16-bit mask literals in many equivalent places, while this DPCS 4.2.2 range mostly uses zero-extended `0x0000....L` masks. Mechanical substitution across versions is risky.
- The macros are consumed through token concatenation, so renaming or typo fixes that look cosmetic can break compilation in distant register-table code.

## Test Signals

Useful validation signals are mostly build-time and hardware/regression oriented:

- Compile AMDGPU display code that includes `dcn315_resource.c`; undefined `FD_SHIFT`/`FD_MASK` expansions catch missing or misspelled macros.
- Compare this header against the matching ASIC register database or regenerated `dpcs_4_2_2_*` files to confirm bit positions and masks for CR3 RAWAONLANEX, SUPX, and LANEX blocks.
- Run display bring-up/link-training tests that exercise DisplayPort/HDMI modes using DCN 3.1.5 resources, watching for HPD, link training, PLL lock, clock switching, and low-power state regressions.
- On hardware, inspect MMIO readback around offsets `0x7024`, `0x8007`, and `0x9011` to verify field packing through the helper macros matches expected register values.
- KUnit-style or compile-only tests can validate macro arithmetic for representative fields, for example `PSTATE`, `RATE`, `WIDTH`, MPLL enable/divider fields, and RX equalization masks.

### subset-b-002371: lines 81069-83440

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 81069-83440

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY/control registers. It contains no executable C code; it publishes preprocessor constants that describe bit positions and bit masks for hardware register fields. Driver code pairs these constants with the companion `dpcs_4_2_2_offset.h` offsets and uses AMD display register helpers to build per-block shift/mask tables.

The requested range is a mid-file slice of a 103,633-line generated header. It contains 2,128 `#define` lines: 1,063 `__SHIFT` definitions and 1,065 `_MASK` definitions. The imbalance is caused by artificial chunk boundaries. The range starts inside `DPCSSYS_CR3_LANEX_DIG_ASIC_RX_EQ_ASIC_IN_1`, after the `EQ_DFE_TAP2` and `EQ_DFE_TAP1` shift lines but before their masks, and ends on the comment for `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`, whose field definitions are in the next chunk.

Although the source path sits under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, preserve, or update that field.

The main register-field families in this range are:

- `DPCSSYS_CR3_LANEX_DIG_ASIC_*`: lane ASIC-facing RX/TX fields for RX equalization, RX CDR/VCO load values, RX ASIC output status, RX/TX override controls, TX override output controls, and OCLA clock/data observation enables.
- `DPCSSYS_CR3_LANEX_DIG_TX_PWRCTL_*`: TX power-state templates for `P0`, `P0S`, `P1`, and `P2`; TX power-up timing stages; and TX DCC CR-bank/DAC control, range, select, acknowledge, and address fields.
- `DPCSSYS_CR3_LANEX_DIG_RX_PWRCTL_*` and `DPCSSYS_CR3_LANEX_DIG_RX_VCOCAL_*`: RX power-state templates, RX power-up timing stages, RX VCO calibration control/time fields, and VCO calibration status.
- `DPCSSYS_CR3_LANEX_DIG_RX_*`: RX XAUI alignment mask, LBERT controls/error counters, CDR controls/status, DPLL frequency/bounds, adaptation configuration, adaptation reset, tap/status readbacks, DAC control selection, CR-bank access, statistical match/count controls, and statistic stop fields.
- `DPCSSYS_CR3_LANEX_DIG_MPHY_*`: MPHY RX PWM, low-speed termination, and analog PWM clock-stability counter fields.
- `DPCSSYS_CR3_LANEX_DIG_ANA_*` and `DPCSSYS_CR3_LANEX_ANA_*`: digital-to-analog override outputs and raw analog TX/RX controls for TX term code, TX equalization, RX power/VCO/calibration, DAC control, AFE ATT/VGA/CTLE, RX scope/slicer/IQ phase, signal-detect override, TX DCC DAC override, analog test-bus/measurement fields, analog power/clock/misc fields, RX CDR/slicer/squelch/calibration, and RX ATB measurement/force fields.
- `DPCSSYS_CR3_RAWMEM_DIG_*`: raw common ROM/RAM field masks for CR3 raw memory windows.
- `DPCSSYS_CR3_RAWLANEX_DIG_PCS_XF_*`: raw lane PCS transfer-interface fields for TX/RX override inputs/outputs, PCS input/output status, RX adaptation acknowledgement and figure-of-merit, directed TX pre/main/post cursor controls, lane number, ATE override, RX EQ delta-IQ override, TX/RX termination override/input, and phase-2 RX calibration.
- `DPCSSYS_CR3_RAWLANEX_DIG_FSM_*`: FSM override, memory-address monitor, FSM status monitor, fast RX/TX calibration/adaptation flags, common calibration status for MPLL and RCAL, CR register/memory lock bits, TX DCC flags/status, OCLA controls, and TX EQ update flag.

The power-state templates have repeated bit layouts. TX `P0/P0S/P1/P2` fields cover analog reference generation, VCM hold, analog clocks, word clock, reset, serial enable, digital clock enable, data enable, RX detect allowance, and DCC compensation calibration enable. RX `P0/P0S/P1/P2` fields similarly cover analog/digital clocks, resets, data, CDR tracking, termination, and related enable state. Those repeated layouts are intended for table-driven power sequencing by code outside this header.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.5 resource code includes `dpcs/dpcs_4_2_2_offset.h` and this matching `dpcs/dpcs_4_2_2_sh_mask.h`.
2. Register-list macros in display resource and link-encoder headers token-paste generated register and field names into offset, shift, and mask initializers.
3. AMD display objects store those constants in register, shift, and mask tables.
4. Runtime code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and poll/wait helpers to access MMIO or indexed DPCS CR registers through the generated constants.

The macros do not encode programming order. Consumers must still sequence PHY power state changes, TX/RX clock enables, CDR/VCO programming, DCC and RX calibration, PCS transfer handshakes, adaptation, interrupt/status handling, and suspend/resume restoration according to hardware rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware-backed state for CR3 lane and raw-lane DPCS blocks:

- RX equalization and adaptation state, including ATT/VGA/CTLE controls, DFE tap status, DAC selection, slicer offsets, adaptation reset, and RX adaptation acknowledgement/FOM values.
- RX CDR, DPLL, and VCO state, including load values, frequency bounds, calibration enables, calibration timers, and calibration status.
- TX state, including power templates, power-up timing, term-code override, equalization override, DCC DAC programming, TX DCC status, and TX EQ update flags.
- Lane digital override state, including RX/TX override enable bits, clock/data enable overrides, lane-master/shift acknowledgement controls, termination controls, and MPHY low-speed/PWM controls.
- Analog observation and override state for TX/RX analog controls, ATB measurement paths, OCLA controls, and raw analog status.
- PCS transfer-interface state for TX/RX PCS inputs/outputs, loopback/test/ATE controls, lane numbering, RX phase-2 calibration, and TX/RX termination controls.
- FSM state and diagnostics, including override control, memory-address monitor, state/readiness/overflow/zero flags, fast calibration/adaptation selectors, common MPLL/RCAL init/done bits, CR lock bits, and OCLA bank enables.

Persistence is hardware-defined. Configuration fields generally remain until link reprogramming, PHY reset, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, acknowledge, done, lock, monitor, and calibration flags may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the relevant DPCS power and clock domains are active. This generated header does not identify those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DPCS 4.2.2 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the corresponding `ix...` offsets. The registers in this chunk map to the CR3 `LANEX` address range around `0x9018-0x90ff`, raw memory windows at `0xa000` and `0xc000`, and raw lane PCS/FSM ranges around `0xe000-0xe03f`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both DPCS 4.2.2 generated headers and builds DCN 3.1.5 link-encoder register/shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the DPCS register and field-list macros used by DCN 3.1-family link encoders.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` uses DPCS/RDPCS generated metadata for HPO DP link-encoder PHY control registration.
- Shared AMD display register helper infrastructure consumes the generated values indirectly through table entries built by `SRI`, `SRII`, `LE_SF`, and related token-pasting macros.

Behaviorally, this range sits below the higher-level display link encoder. It describes the per-lane PHY, RX/TX adaptation, calibration, and diagnostic fields that link-training, PHY bring-up, power management, and hardware debug paths rely on, even when most field names are not referenced directly by hand-written C code.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while writing the wrong DPCS CR bit, corrupting adjacent PHY state, or reading a misleading status field.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk boundaries are not semantic. The first register group starts in the previous chunk, and the final `RX_IQ_PHASE_OFFSET` group starts only as a comment here and is defined in the next chunk.
- CR3 lane fields are one repeated slice of a broader DPCS namespace. A generator error limited to CR3 may only appear on a specific lane, connector, or link-encoder routing.
- PHY power, CDR/VCO, DPLL, DCC, and RX adaptation fields are sequencing-sensitive. Incorrect masks can cause link-training failures, unstable high-rate links, calibration timeouts, bad RX equalization, or failures that only appear after low-power transitions.
- Override and lock bits can bypass normal hardware sequencing. Writing the wrong override-enable or lock field may leave a lane stuck in test/debug mode, prevent firmware/hardware FSM updates, or interfere with normal link bring-up.
- Status and acknowledge fields are side-effect-sensitive. Misclassifying status, done, ack, lock, or clear semantics can produce busy waits that never finish, missed calibration completion, stale diagnostics, or interrupt/status storms in adjacent IRQ-control ranges.
- Analog and test-bus fields are hardware-revision-sensitive. Incorrect masks in ATB, OCLA, ATE, raw memory, or analog override areas can produce hard-to-reproduce board-specific failures or misleading lab diagnostics.

## Test Signals

Useful validation combines generated-header consistency checks with link/PHY behavior:

- Build AMDGPU display support with DCN 3.1.5 enabled. Missing or renamed macros should surface where `dcn315_resource.c` includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h` and initializes link-encoder DPCS tables.
- Mechanically verify that every field in lines 81069-83440 has the expected shift/mask pairing, while allowing the known artificial-boundary exceptions at `DPCSSYS_CR3_LANEX_DIG_ASIC_RX_EQ_ASIC_IN_1` and `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`.
- Cross-check each register group in this slice against `dpcs_4_2_2_offset.h` so every shift/mask group has a corresponding `ixDPCSSYS_CR3_*` offset.
- Diff this range against AMD's authoritative DPCS 4.2.2 register-field database and neighboring generated variants such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` where CR3 lane layouts are expected to be compatible.
- Exercise display link bring-up on hardware using this DPCS revision across all available connectors and lanes: hotplug, link training, link-rate/lane-count changes, DisplayPort alt-mode paths, suspend/resume, GPU reset, and repeated modesets.
- Validate high-rate and marginal-link cases that stress CDR/VCO/DPLL, equalization, DCC, RX adaptation, and termination programming. Expected signals are stable training, no stuck calibration done/ack polling, no unexpected link retrains, and clean PHY status readbacks.
- Use register dumps or debugfs-style diagnostics to confirm that TX/RX power templates, timing fields, calibration status, FSM state, and PCS transfer-interface fields match expected programming before and after power transitions.
- Watch kernel logs and display diagnostics for link-training failures, AUX/link instability caused by PHY misconfiguration, blank displays after resume, calibration timeouts, stuck FSM readiness, bad lane mapping, or failures isolated to one CR3-backed lane/encoder.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR3_LANEX_DIG_ASIC_RX_EQ_ASIC_IN_1`, including the `EQ_DFE_TAP2` and `EQ_DFE_TAP1` shift definitions. This chunk begins with the reserved shift and all masks for that register, then covers the rest of the CR3 lane ASIC, power, calibration, analog, raw PCS, and FSM groups through `DPCSSYS_CR3_RAWLANEX_DIG_FSM_CMNCAL_RCAL_STATUS`. The next chunk owns the `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET` definitions and continues into CR3 raw-lane IRQ-control fields. The final per-file research document should merge adjacent chunks before making whole-file claims about all DPCS 4.2.2 fields or all CR3 lane behavior.

### subset-b-002372: lines 83441-85817

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 83441-85817

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic. Its exported surface is preprocessor metadata that maps hardware register fields to bit positions (`__SHIFT`) and bit masks (`_MASK`) for AMDGPU display register helpers.

The requested range contains 2,132 `#define` entries across 2,377 source lines, plus 243 register/address-block comment markers. It starts at the field definitions for `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`, then covers the rest of the visible CR3 raw-lane IRQ, PMA, TX/RX control, and PCS/ATE override groups. It then enters `addressBlock: dpcssys_cr4_rdpcstxcrind`, covering CR4 supervisor digital and analog controls, MPLLA/MPLLB clocking and RTUNE metadata, CR4 lane0 ASIC and TX power/DCC controls, TX clock alignment/LBERT fields, and the beginning of lane0 RX statistic controls through the early shift definitions of `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0`.

Although the source path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The only interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for extracting, composing, or updating that field.

The main register-field families in this chunk are:

- CR3 raw-lane FSM tail: `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET` exposes the RX IQ phase offset field. The register marker is just before the requested line range, so this chunk starts inside that register group but includes its shift and mask definitions.
- CR3 raw-lane IRQ controls: `DPCSSYS_CR3_RAWLANEX_DIG_IRQ_CTL_*` defines reset-return request, RX reset/request/rate/pstate/adaptation IRQ status bits, matching clear bits, aggregate IRQ masks, TX reset/request IRQ status and clear bits, lane transceiver-mode IRQs, RX phase-2 calibration IRQs, serial loopback IRQs, and DCC on-demand IRQ state.
- CR3 raw-lane PMA cross-interface fields: `PMA_XF_LANE_OVRD_IN/OUT`, `SUP_OVRD_IN`, `SUP_PMA_IN`, `TX_OVRD_OUT`, `TX_PMA_IN`, `RX_OVRD_OUT`, `RX_PMA_IN`, `LANE_RTUNE_CTL`, `SUP_PMA_IN_1`, `MPHY_OVRD_IN/OUT`, and `RX_ADAPT_OVRD_OUT` describe lane and supervisor PMA override values/enables, TX/RX request/reset/data-enable handshakes, PMA ACK inputs, RTUNE controls, MPHY PWM/termination override paths, and RX adaptation override outputs.
- CR3 raw-lane TX/RX local control: `TX_CTL_TX_FSM_CTL`, `TX_CLK_CTL`, `TX_DCC_CONT_STATUS`, `TX_CTL_OCLA`, `TX_CTL_UPCS_OCLA`, `RX_CTL_RX_FSM_CTL`, `RX_LOS_MASK_CTL`, `RX_DATA_EN_OVRD_CTL`, `OFFCAN_CONT_STATUS`, `ADAPT_CONT_STATUS`, and `RX_CTL_UPCS_OCLA` define TX FSM and clock controls, DCC/off-cancel/adaptation continuous-status enables, RX LOS and data-enable override timing, and observation controls.
- CR3 PCS/ATE override controls: `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN_1`, `PCS_XF_MASTER_MPLL_LOOP`, `PCS_XF_ATE_RX_OVRD_IN_1/2/3`, `PCS_XF_RX_OVRD_OUT_2`, and `PCS_XF_TX_OVRD_IN_2` cover automated-test and forced-lane paths for RX/TX rate, width, pstate, resets, adaptation controls, DETRX/VBOOST/IBOOST, loopback, LOS/LFPS thresholds, VCO/ref load overrides, RX-valid forcing, master MPLL loop selection, and additional TX/RX override outputs.
- CR4 supervisor digital controls: ID-code words, reference-clock overrides, MPLLA/MPLLB divided and HDMI clock overrides, MPLLA/MPLLB fractional-N, SSC, divider, multiplier, enable/reset/power-state, charge-pump, gain-switch, level, ASIC-input, bandgap, prescaler, and supervisor override/output fields.
- CR4 supervisor analog and calibration controls: prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB miscellaneous/override/ATB/control/reserved fields, MPLL power-control status, timers, calibration, DAC range/output, SSC spread type, clock/reset power-up timers, RTUNE configuration/status/set/stat/code fields, and analog override/status outputs.
- CR4 lane0 ASIC and TX power controls: lane/TX/RX ASIC override inputs/outputs, lane ASIC status, TX pstate definitions for P0/P0s/P1/P2, TX power-up timers, DCC CR-bank address/data, DCC DAC control/range/select/ACK/address, TX clock-alignment controls, and LBERT pattern/error injection control.
- CR4 lane0 RX statistic controls: `RX_STAT_LD_VAL_1`, `RX_STAT_DATA_MSK`, `RX_STAT_MATCH_CTL0`, `RX_STAT_MATCH_CTL1`, and the start of `RX_STAT_STAT_CTL0` define statistic load/start, data mask, pattern matching, correction/statistic source selection, statistic shift selection, RX clock selection, sample-counter mode, and skip-enable fields. The requested range ends before the remaining `STAT_CTL0` shifts and masks.

Most fields are 16-bit register slices with an `L`-suffixed mask value. Some logical values are split across multiple registers, such as MPLL fractional/SSC high and low words, multiword TX power-up timing, and repeated MPLLA/MPLLB analog override/status banks.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to the AMDGPU display stack:

1. DPCS 4.2.2 register address metadata comes from the companion `dpcs_4_2_2_offset.h` file.
2. This file supplies matching field shifts and masks for those indexed registers.
3. DCN resource and link-encoder code token-pastes register, shift, and mask names into register tables.
4. Runtime display code uses those tables through AMD register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
5. Hardware and firmware sequencing for PHY reset, clock selection, PLL programming, pstate changes, lane power, AUX/ATE forcing, RX adaptation, RX statistics, and analog calibration lives outside this generated header.

The macro names describe field location only. They do not encode access type, reset value, polling order, write-one-to-clear behavior, self-clearing behavior, sticky status behavior, clock-domain restrictions, power-domain validity, or reserved-bit policy.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 and CR4 DPCS/PHY registers:

- CR3 IRQ state includes latched RX/TX reset and request events, RX rate and pstate events, RX adaptation request/disable events, lane transceiver-mode events, phase-2 calibration events, serial loopback events, DCC on-demand events, clear registers, reset-return request bits, and interrupt-mask registers.
- CR3 PMA/PCS override state includes forced request/reset/data-enable values, override-enable bits, TX/RX loopback state, PMA/RTUNE ACK state, MPHY PWM and termination controls, RX phase-map adaptation override, ATE rate/width/pstate forcing, DETRX/VBOOST/IBOOST forcing, LOS/LFPS and adaptation controls, VCO/ref-load overrides, master MPLL loop enables, and RX-valid forcing.
- CR3 TX/RX control state includes TX FSM enable/timing, TX clock enable/source selection, RXDET permission by pstate, DCC/off-cancel/adaptation continuous-status enables, RX LOS masking, RX data-enable override timing, and OCLA/UPCS observation gates.
- CR4 supervisor state includes MPLLA/MPLLB reference/divided/HDMI clock paths, fractional-N and SSC parameters, dividers, multipliers, enable/reset/power state, charge-pump and gain-switch tuning, bandgap and prescaler controls, RTUNE set/stat/calibration state, and clock/reset power-up timing.
- CR4 analog state includes MPLLA/MPLLB analog override, ATB, control, reserved, power-control, timer, calibration, DAC, and status readback fields.
- CR4 lane0 state includes ASIC override/in/out buses, TX pstate and power-up timing, DCC CR-bank and DAC access, TX clock alignment, LBERT control, and RX statistic matching/source-selection state.

Persistence is hardware-defined. Configuration fields generally remain until link reprogramming, modeset, suspend/resume, power-gating, GPU reset, ASIC reset, firmware ownership changes, or explicit driver reinitialization changes them. Status, ACK, IRQ, calibration, statistic-done, and handshake fields may be transient, latched, write-one-to-clear, self-clearing, sampled only under an active clock domain, or invalid while PHY power is gated. This generated header does not distinguish those cases.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ix...` offsets. In that file, `ixDPCSSYS_CR3_RAWLANEX_DIG_IRQ_CTL_RESET_RTN_REQ` is mapped at `0xe040`, the CR4 block starts with `ixDPCSSYS_CR4_SUP_DIG_IDCODE_LO` at `0x0000`, and the end-boundary register `ixDPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0` is mapped at `0x1084`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes the DPCS 4.2.2 offset and shift/mask headers when constructing DCN 3.1.5 display resources.
- DIO/HPO link encoder and display core register-list code consume these macros indirectly through generated register, shift, and mask tables.
- Low-level display link, PHY, PLL, lane-training, hotplug/AUX/DDC, diagnostics, hardware sequencing, and reset/power-management paths rely on these field locations when programming or decoding DPCS registers.

Behaviorally, this chunk sits below user-facing display code. It provides the bitfield layer for operations such as masking and clearing lane IRQs, forcing or observing PMA/PCS handshakes, programming MPLL and SSC parameters, controlling PHY power and clocking, running RTUNE and DCC calibration, configuring TX pstate timing, collecting RX statistics, and driving test/diagnostic override paths.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting adjacent reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts inside `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`; the register comment is immediately before the requested range. Whole-register analysis should reconcile the preceding chunk for the marker and local context.
- The chunk ends inside `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0`; later shifts and all masks for that register continue after line 85817. Consumers of this research must not treat this chunk as owning the whole RX statistic control register.
- CR3 and CR4 layouts are repetitive across lanes, PLLs, and analog banks. A generator or copy error can affect only one lane, MPLL, or transmitter path while neighboring definitions look correct.
- IRQ status, clear, and mask fields use similar names but have different hardware semantics. Mixing them can drop events, leave stale events latched, or cause repeated interrupts.
- Override-enable and override-value pairs must be handled carefully. Enabling an override with a stale value, or setting a value bit without the corresponding enable bit, can force unexpected PHY state.
- PLL, SSC, divider, multiplier, charge-pump, gain-switch, bandgap, power-up timer, RTUNE, DCC, and TX pstate fields are timing- and silicon-sensitive. Incorrect field definitions can cause link-training failures, unstable clocks, blank displays, excessive bit errors, calibration timeouts, or bad resume behavior.
- Status, ACK, statistic-done, calibration-result, and IRQ fields may be read-only, latched, or dependent on active power and clock domains. Treating them like ordinary writable configuration fields can hide real hardware state or clear diagnostics.
- RX statistic and LBERT fields are diagnostic/test-oriented. Incorrect masks can make validation tools report misleading pass/fail results even when normal link operation appears unchanged.
- Reserved masks are emitted throughout the chunk. Generic register writes must preserve reserved bits unless the hardware programming guide explicitly requires a value.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build or preprocess AMDGPU display support for DCN 3.1.5 with `dcn315_resource.c`, `dpcs_4_2_2_offset.h`, and `dpcs_4_2_2_sh_mask.h`. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that complete fields in this range have paired `__SHIFT` and `_MASK` definitions, allowing the known boundary exceptions for `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET` at the start and `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0` at the end.
- Cross-check every complete register group against `dpcs_4_2_2_offset.h` and AMD's source register database.
- Diff CR3/CR4 replicated lane, MPLLA/MPLLB, and analog-bank field layouts against neighboring generated DPCS versions where the hardware specification expects matching fields.
- Exercise DisplayPort and HDMI link bring-up on ports mapped to the affected DPCS/UNIPHY instances. Expected signals are stable link training, correct PLL lock behavior, completed RX adaptation, expected lane request/ACK transitions, and no recurring RX/TX calibration or IRQ failures.
- Run modeset, stream disable/enable, hotplug, suspend/resume, GPU reset, and power-gating tests to catch stale pstate, clock, reset, MPLL, analog override, RTUNE, and DCC state.
- Use register dumps or PHY debug traces during failures to confirm that IRQ clear/mask bits, PMA/PCS overrides, MPLLA/MPLLB settings, RTUNE/DCC status, TX pstate timers, RX statistic match controls, and analog override/status fields decode as expected.
- On validation hardware, run available OCLA/UPCS OCLA, LBERT, RX statistic, ATE, DCC on-demand, RTUNE, and phase-2 calibration paths to verify diagnostic counters, sample-done bits, ACK/status fields, and forced override paths use the intended field positions.

## Cross-Chunk Notes

The previous chunk owns the marker and surrounding context for `DPCSSYS_CR3_RAWLANEX_DIG_FSM_RX_IQ_PHASE_OFFSET`. This chunk owns that register's visible field definitions, the CR3 raw-lane IRQ/PMA/TX/RX/ATE tail, the CR4 supervisor and analog/control sections, and the CR4 lane0 TX power/statistic lead-in through early `RX_STAT_STAT_CTL0` shifts. The next chunk should finish `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0` and continue the remaining CR4 lane0 RX statistic, analog TX/RX, and later lane blocks. The final per-file report should reconcile these artificial chunk boundaries before making whole-file claims about DPCS 4.2.2 CR3/CR4 coverage.

### subset-b-002373: lines 85818-88178

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 85818-88178

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for low-level display PHY/DPCS register fields. It contains no executable C code; its public surface is preprocessor constants that identify bit positions and bit masks for fields in DPCSSYS CR4 lane registers.

The requested range contains 2,136 `#define` lines and 225 register-comment markers. It starts inside `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0`, covers the remainder of CR4 lane0 RX statistics and lane0 TX analog-control metadata, then covers a large CR4 lane1 span from ASIC override/status fields through TX/RX power, calibration, adaptation, statistics, MPHY, analog RX/TX override, signal-detect, DCC DAC, ATB, and TX term-code fields. The final line stops inside `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL`, so both the first and last register groups are artificial chunk boundaries.

Although this file lives under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or direct MMIO operations in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for the same field.

The main register-field families in this chunk are:

- CR4 lane0 RX statistics tail: statistic counter enables, sample count, statistic counters 0 through 6, comparator clock controls, pattern-match controls, statistic stop, valid-loss clear/control, and sample-count disabling.
- CR4 lane0 digital/analog TX controls: TX analog override outputs, TX termination-code overrides, term-code load clock control, equalization override outputs 0 through 5, analog status, TX DCC DAC overrides, fast-start/loopback/AC-JTAG controls, ATB measurement selectors, power override, alternate bus, DCC DAC, term-code, override clock, misc, and reserved TX fields.
- CR4 lane1 ASIC-facing override/input/output fields: lane loopback and AC-JTAG controls; TX request, P-state, rate, width, MPLL selection, data enable, main/pre/post cursor, HDMI mode, detect-RX request, invert, low-power-detect, DC coupling, MPHY mode, FIFO, raw ASIC inputs, and OCLA fields; RX status/override paths for CDR, DPLL, equalization, adaptation, DAC control, and VCO.
- CR4 lane1 TX power/control fields: TX P-state values for P0/P0S/P1/P2, power-up timing registers, DCC CR bank address/data, DCC DAC control/range/selection/ack/address, TX clock alignment, and TX LBERT pattern/error injection control.
- CR4 lane1 RX power/calibration/adaptation fields: RX P-state and power-up timing, RX VCO calibration controls/timers/status, XAUI alignment mask, RX LBERT control/error, CDR control/status, DPLL frequency/bounds, adaptation configuration and reset, ATT/VGA/CTLE/DFE status, DFE offset readbacks, slicer controls, error-slicer level, DAC control selects, and adaptation CR bank access.
- CR4 lane1 RX statistics and MPHY fields: statistic load value, data mask, match controls, statistic control/count/stop, calibration-comparator clock control, MPHY PWM control, low-speed termination, and PWM-clock stable-count fields.
- CR4 lane1 analog RX/TX controls: TX analog override and equalization outputs, RX analog control/power/VCO overrides, RX calibration and DAC controls, AFE ATT/VGA/CTLE, scope/slicer/IQ controls, analog signal-change enable, status readbacks, RX term-code override/clock controls, MPHY override, signal-detect thresholds/calibration controls, TX DCC DAC overrides, TX fast-start/clock-loopback/AC-JTAG, ATB measurement selectors, TX power and alternate-bus overrides, DCC DAC, and TX term-code low bits.

Many fields follow an `*_OVRD_EN` or `ovrd_*` pattern. Those macros describe manual override enable bits paired with override values or hardware-state readbacks, which makes this range especially sensitive to debug, bring-up, PHY tuning, and link-training flows.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this matching `dpcs_4_2_2_sh_mask.h`.
2. Register-list and mask/shift-list macros in `dcn315_resource.c` bind generated offsets, shifts, and masks into link-encoder and DPCS register tables.
3. Display link encoder code uses those tables through shared AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. Runtime control flow for link enable, lane power sequencing, DP/HDMI PHY setup, training, test patterns, clock recovery, equalization, diagnostics, suspend/resume, and reset lives outside this generated header.

The macros in this chunk do not define programming order, timing, reset requirements, or read/write side effects. They only provide the bitfield positions used by code that performs those operations.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields for two CR4 lanes:

- Lane power, P-state, rate, width, PLL selection, data enable, clock readiness, reset, serial enable, loopback, MPHY, and AC-JTAG controls.
- TX electrical tuning state, including main/pre/post cursor values, equalization leg pull/push controls, termination-code override and update/reset controls, DCC DAC controls, VREG/VCM/refgen/clock/data/serial enables, and fast-start settings.
- RX clock/data recovery and adaptation state, including CDR controls, DPLL frequency bounds, VCO calibration results, ATT/VGA/CTLE/DFE status, DAC control selectors, slicer thresholds, scope controls, and RX term-code/signaldetect controls.
- Diagnostic and production-test state, including LBERT controls/errors, OCLA selectors, alternate-bus and ATB measurement selectors, CR bank address/data windows, statistic counters, pattern matchers, sample counters, valid-loss clear/control, and analog status readbacks.

Persistence and side effects are hardware-defined. Configuration fields generally remain until rewritten by modeset, link training, PHY reconfiguration, suspend/resume, power gating, GPU reset, or ASIC reset. Status, counter, acknowledge, self-clear, and calibration fields may be latched, sticky, clear-on-write, self-clearing, or valid only while the relevant DPCS lane is powered and clocked. This generated file does not encode those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_CR4_*` register offsets, including the lane0 range around `0x1085-0x10ef` and the lane1 range around `0x1100-0x11e8` covered here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both DPCS 4.2.2 generated headers, defines `DPCS_BASE__INST0_SEG*`, and expands DPCS register and mask/shift lists for DCN 3.1.5 resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` also constructs HPO DP and DIO link encoder resources that depend on the generated register metadata for DPCS-backed link paths.
- Link management code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/` exercises the resulting encoder operations for DP link enable/disable, DP PHY setup, link training, power management, and HPD/link-state transitions.
- Neighboring generated DPCS versions (`dpcs_4_2_0_*` and `dpcs_4_2_3_*`) provide useful generated-header comparison points. The 4.2.3 shift/mask header keeps many equivalent fields but uses shorter 16-bit-looking mask literals and some upper-case field spellings, so consumers must include the ASIC-specific header rather than mix versions.

Behaviorally, this range is part of the display link PHY layer. A bad field macro here can surface as connector bring-up failure, unstable DP training, broken HDMI electrical programming, incorrect lane power sequencing, unreliable calibration, misleading diagnostics, or failures limited to CR4 lane0/lane1 depending on routing.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift compiles cleanly and may corrupt only one hardware field at runtime.
- The file is generated. Manual edits risk divergence from AMD's authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are only the tail of `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0`, and the final lines stop after only three shift definitions in `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL`; adjacent chunks are required for complete register descriptions at both ends.
- Lane instance repetition is copy-sensitive. Lane1 largely mirrors lane0 families with address and prefix changes, but this chunk includes only the tail of lane0 and a broad lane1 span, so whole-lane equivalence claims need reconciliation with neighboring chunks.
- Override enable bits are hazardous. Misprogramming `*_OVRD_EN`, `ovrd_*`, and corresponding value fields can force PHY states that hardware training or power sequencing expects to control automatically.
- TX cursor, equalization, termination, DCC, VREG, and VCM masks are electrically sensitive. Incorrect field definitions can cause link-training failures, eye-margin degradation, intermittent high-rate errors, or visible display corruption.
- RX CDR, DPLL, VCO calibration, adaptation, DFE, CTLE, VGA, and slicer fields influence clock recovery and equalization. Wrong masks may look like sink/cable instability while the real issue is local PHY programming.
- Statistic, LBERT, OCLA, ATB, and CR-bank fields are diagnostic surfaces. Bad definitions may not affect normal display output but can hide training defects, produce misleading debug data, or break manufacturing/bring-up tests.
- Power and P-state fields require sequencing outside this header. Incorrect use of these masks can interact badly with suspend/resume, fast link retraining, power gating, and lane disable/enable transitions.
- CR4 lane-specific errors may be topology-dependent. Bugs can appear only on connectors or modes routed through the affected DPCS lane, especially when alternate routing or HPO DP paths are in use.

## Test Signals

Useful validation combines generated-header consistency checks with real display-link behavior:

- Build DCN 3.1.5 AMDGPU display support. Missing or renamed macros should surface in `dcn315_resource.c` and downstream link encoder register-table construction.
- Mechanically compare every field in this range against the authoritative DPCS 4.2.2 register-field database, ensuring each `_MASK` has the intended paired `__SHIFT` definition.
- Cross-check this shift/mask range against `dpcs_4_2_2_offset.h`, confirming every register comment in the chunk has a corresponding `ixDPCSSYS_CR4_*` offset.
- Run generated-header diff checks against `dpcs_4_2_0_*` and `dpcs_4_2_3_*` to catch accidental version mixing while allowing intentional spelling and literal-format differences.
- Exercise DP and HDMI link bring-up on connectors routed through CR4 lane0 and CR4 lane1. Expected signals are successful modesets, stable hotplug/link state, and no unexpected training fallback at normal link rates.
- Exercise DP link training across multiple rates and lane counts, including retraining after unplug/replug and suspend/resume. Watch for CDR/DPLL/VCO/adaptation failures, repeated equalization retries, or lane-specific instability.
- Validate TX electrical programming using high-bandwidth modes and, where available, register dumps or lab margining for main/pre/post cursor, EQ override, termination, DCC DAC, and fast-start fields.
- Exercise diagnostic paths that rely on this metadata: LBERT pattern/error control, statistic counters, pattern-match controls, OCLA, ATB measurement selection, CR bank address/data access, and analog status readbacks.
- Test power-management transitions with active and inactive links, including link disable/enable, display blank/unblank, runtime power gating, and system suspend/resume. Expected signals are no stuck P-state/power-up/calibration bits and no lane that requires a full GPU reset to recover.

## Cross-Chunk Notes

The previous chunk owns earlier CR4 lane0 ASIC, TX power, TX clock-align/LBERT, RX statistic load/match/control0, and likely other lane0 register groups. This chunk begins after `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0__STAT_RXCLK_SEL__SHIFT` and finishes the rest of that register's masks before moving forward.

The next chunk continues `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL` with the remaining shift and mask definitions, then should cover later CR4 lane1 analog RX fields and subsequent DPCS register groups. The final per-file research document should reconcile these partial boundaries before making complete statements about `dpcs_4_2_2_sh_mask.h` or all DPCS 4.2.2 lane metadata.

### subset-b-002374: lines 88179-90536

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 88179-90536

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It provides C preprocessor constants that describe bit positions and masks for DPCS CR4 lane registers; it does not contain executable driver logic. AMDGPU display code uses these constants with companion register-offset headers and register-access helpers to program or decode PHY, lane, PLL, power, calibration, adaptation, interrupt, and debug/test fields without hard-coding bit arithmetic.

The requested range contains 2,358 lines, 2,141 `#define` statements, 1,072 `__SHIFT` macros, 1,069 `_MASK` macros, and 217 register comment boundaries. It starts in the middle of `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL`, completes the tail of CR4 lane 1 analog TX/RX field definitions, then covers a large CR4 lane 2 block: digital ASIC override/input/output mirrors, TX/RX power-control and calibration fields, CDR/DPLL/adaptation/statistics fields, MPHY controls, digital-to-analog override outputs, and the beginning of lane 2 analog TX/RX fields. The final lines start `DPCSSYS_CR4_LANE2_ANA_RX_SQ`; that register's remaining mask definitions continue in the next chunk.

Although the path is inside a local `ceph-client` source mirror, this file belongs to AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, memory allocations, locks, direct MMIO accesses, or exported symbols in this range. The public interface is the generated macro pair pattern:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit index for a register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field in a register value.

The main macro groups in this chunk are:

- `DPCSSYS_CR4_LANE1_ANA_TX_*` and `DPCSSYS_CR4_LANE1_ANA_RX_*`: tail definitions for lane 1 analog TX termination, clock override, TX miscellaneous, TX reserved, RX CDR/deserializer, slicer, power, squelch, calibration, analog test bus measurement, forced ATB value, and reserved fields.
- `DPCSSYS_CR4_LANE2_DIG_ASIC_*_OVRD_IN_*`: digital ASIC override input fields for lane, TX, RX, RX EQ, and additional TX/RX override banks. These include request, pstate, rate, width, MPLLA/MPLLB selection/enables, data enable, detect-RX, reset, loopback, async enable, RX adaptation, RX termination, SQ threshold/response, CDR/VCO/DFE/CTLE/VGA/ATT, PH2 calibration, ATE, and override-enable fields.
- `DPCSSYS_CR4_LANE2_DIG_ASIC_*_ASIC_IN_*` and `*_ASIC_OUT*`: non-override ASIC input/output mirror fields for lane, TX, RX, RX EQ, CDR VCO, request/ack, data enable, detect-RX, pstate/rate/width, equalization, adaptation, and status observation.
- `DPCSSYS_CR4_LANE2_DIG_TX_PWRCTL_*`: TX pstate configuration, data-enable and request/reset behavior, RX-detect bypass and termination settings, power-up timing windows, DCC DAC bank/address/data/select/range/control, DAC acknowledgment, and TX clock-align/LBERT control fields.
- `DPCSSYS_CR4_LANE2_DIG_RX_PWRCTL_*`: RX pstate configuration and RX power-up timing fields, including request, data-enable, reset, DFE, deserializer, loopback, fast-start, clock-enable, and analog-front-end enable controls.
- `DPCSSYS_CR4_LANE2_DIG_RX_VCOCAL_*`, `DPCSSYS_CR4_LANE2_DIG_RX_CDR_*`, and `DPCSSYS_CR4_LANE2_DIG_RX_DPLL_*`: VCO calibration control/status/timing, CDR control/status, and digital PLL frequency and frequency-bound fields.
- `DPCSSYS_CR4_LANE2_DIG_RX_ADPTCTL_*`: RX adaptation configuration/status fields for ATT, VGA, CTLE, DFE taps, slicer offsets, DAC-control muxes, adaptation reset, and CR-bank access.
- `DPCSSYS_CR4_LANE2_DIG_RX_STAT_*`: status match/mask/control/counter fields, sample counters, stop controls, and calibration-comparator clock controls used to observe or qualify RX state.
- `DPCSSYS_CR4_LANE2_DIG_MPHY_*`: MPHY RX PWM control, low-speed termination control, and analog PWM clock-stability count fields.
- `DPCSSYS_CR4_LANE2_DIG_ANA_*_OVRD_OUT*` and `DPCSSYS_CR4_LANE2_DIG_ANA_STATUS_*`: digital-to-analog output/readback masks for TX clock/data/reset/serial/rate, TX termination and EQ, RX control/power/VCO/calibration/DAC/scope/slicer/IQ/signal-change paths, MPHY, signal detect, DCC DAC, and analog status fields.
- `DPCSSYS_CR4_LANE2_ANA_TX_*` and `DPCSSYS_CR4_LANE2_ANA_RX_*`: lane 2 analog TX override/measurement, power override, alt bus, ATB, DCC DAC/control, termination code, clock, miscellaneous, reserved, RX clock, CDR/deserializer, slicer, power, and the beginning of squelch control definitions.

Several field-name patterns encode hardware semantics even though this header only describes layout: `*_OVRD_EN`, `ovrd_*`, `*_reg`, `*_REQ`, `*_ACK`, `*_DONE`, `*_STATUS`, `*_STAT`, `*_PSTATE_*`, `*_PWRUP_TIME_*`, `*_CAL*`, `*_DFE*`, `*_CTLE*`, `*_VGA*`, `*_ATT*`, `*_SLICER*`, `*_TERM*`, `*_LBERT*`, and `*_ATB*`.

## Control Flow

This header has no runtime control flow. It contributes to display-driver behavior through compile-time register descriptions:

1. The matching DPCS 4.2.2 offset header identifies the CR4 lane register addresses or indirect indexes.
2. This shift/mask header supplies field positions and masks for those register names.
3. AMD display code combines offsets, shifts, and masks through generated register tables or token-pasting helpers.
4. Runtime MMIO or indirect-register helpers perform read/modify/write, polling, or decode operations against DPCS hardware.

Actual sequencing lives outside this file. Examples include entering TX/RX pstate changes, asserting resets, enabling clocks/data, programming MPLL lane selection, forcing or releasing overrides, starting VCO/adaptation/calibration, waiting for request/ack or done bits, clearing/masking interrupt/status conditions, and collecting RX statistics.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible control and status fields that may be transient, latched, read-only, write-one-to-clear, self-clearing, or retained depending on the DPCS block, power state, and access path.

The named hardware state includes:

- Lane 1 analog tail state for TX termination, TX clocking, TX miscellaneous controls, RX CDR/deserializer, RX power, squelch, calibration, ATB measurement, and reserved/NC fields.
- Lane 2 digital ASIC override and mirror state for TX/RX request, pstate, rate, width, reset, data-enable, detect-RX, loopback, MPLL selection, RX equalization/adaptation, PH2 calibration, CDR/VCO, ATE, and analog-front-end controls.
- Lane 2 TX/RX power-control state, including pstate programming, power-up delays, DCC DAC state, DCC bank access, clock alignment, LBERT controls, RX VCO calibration, CDR/DPLL frequency, and RX adaptation controls.
- Lane 2 RX statistics and debug state, including match controls, masks, counters, stop controls, sample counts, and calibration-comparator clock controls.
- Lane 2 digital-to-analog output/readback state for TX analog controls, RX analog controls, termination, EQ, VCO, calibration, DAC selection, scope/slicer/IQ paths, MPHY, signal-detect, DCC DAC, and analog status.
- Lane 2 analog TX/RX control state for TX measurement/power/ATB/DCC/termination/clock/miscellaneous controls and RX clock/CDR/slicer/power/squelch fields.

Persistence is hardware-defined. Values may survive until the next modeset, link reconfiguration, suspend/resume, GPU reset, ASIC reset, power-gating transition, or firmware/hardware state-machine rewrite. The header does not describe reset values, legal write values, access width, ownership, volatility, or the ordering constraints needed to program these fields safely.

## Dependencies And Integration Points

This generated header must stay synchronized with its ASIC register database and with the matching DPCS 4.2.2 register-offset header. Consumers generally assume that register names in this file correspond to offset macros in the companion generated header and that field names match the token-pasted register-list definitions used by AMDGPU Display Core.

Integration points include:

- Companion AMD generated headers under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`, especially the DPCS 4.2.2 offset definitions and adjacent chunks of this same shift/mask file.
- AMDGPU Display Core resource, link, PHY, and encoder code that builds ASIC-specific register tables from offset and shift/mask headers.
- Register helper paths that program DisplayPort/HDMI lane bring-up, link training, pstate changes, RX adaptation, TX equalization, termination, signal detect, CDR/DPLL/VCO calibration, DCC calibration, and debug/test flows.
- Hardware/firmware state machines that interpret the same request/ack, override, calibration, status, and power-control fields.

The range crosses semantic regions. Lines 88179-88464 finish CR4 lane 1 analog fields, line 88465 begins CR4 lane 2 digital ASIC override/mirror fields, line 88937 begins lane 2 TX/RX power/calibration/clocking and RX adaptation/statistics fields, line 89855 begins lane 2 digital-to-analog override/status readback fields, and line 90236 moves into lane 2 analog TX/RX fields. Those boundaries should be preserved by the merge lane when building the final per-file report.

## Risks And Edge Cases

- These are untyped preprocessor constants. Incorrect masks or shifts can compile cleanly and produce subtle PHY or display-link failures at runtime.
- The file is generated. Manual edits can diverge from AMD's register source, companion offset headers, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first line continues `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL` from the previous chunk, and the final register `DPCSSYS_CR4_LANE2_ANA_RX_SQ` continues into the next chunk.
- Override/value and override-enable fields are easy to confuse. Misprogramming them can force resets, clocks, pstate/rate/width, data-enable, loopback, MPLL selection, termination, CDR/VCO behavior, RX adaptation, or analog controls away from hardware/firmware ownership.
- Request/ack, done, status, IRQ-like, and counter fields are sequencing-sensitive. A wrong field definition can cause false readiness, missed status, uncleared events, link-training timeouts, or hangs during lane bring-up/teardown.
- Analog and PHY tuning fields such as TX termination, TX EQ leg/pre/post controls, DCC DAC, RX ATT/VGA/CTLE/DFE/slicer offsets, CDR/DPLL/VCO controls, signal-detect thresholds, squelch response/threshold, and MPHY PWM/termination can fail only on specific link rates, boards, cable/sink combinations, or voltage/temperature corners.
- Reserved and `NC` masks appear throughout the range. Driver code should not repurpose them unless an authoritative programming guide explicitly defines them for the target ASIC stepping.
- Generated case and spelling are part of the API. Examples such as `sq_ctrl_tresh_reg`, mixed uppercase ASIC field names, and numbered split fields must remain exactly as generated for token-pasted users.
- Similar CR4 lane 1 and lane 2 macro names are structurally repeated. Using a lane 1 mask with a lane 2 offset, or mixing DPCS 4.2.2 with a neighboring DPCS-generation header, may compile if names overlap but program the wrong silicon layout.

## Test Signals

Useful validation should combine generated-header consistency checks with display hardware testing:

- Build AMDGPU display configurations that include DPCS 4.2.2 support. Missing, renamed, or malformed macros should surface in register table compilation.
- Mechanically compare this range against the authoritative DPCS 4.2.2 register database and verify that complete fields have matching `__SHIFT`/`_MASK` pairs; account for the split first and last registers.
- Cross-check complete register groups in this chunk against the matching DPCS 4.2.2 offset header so each shift/mask register has a corresponding offset definition.
- Run structural diffs across repeated lane 1/lane 2 and TX/RX override/status families to catch generator drift while allowing intentional lane- or block-specific differences.
- Exercise DisplayPort/HDMI link bring-up, link-rate changes, hotplug, modeset, blank/unblank, suspend/resume, and GPU reset on hardware using this DPCS generation.
- Watch runtime logs and register dumps for request/ack timeouts, stuck reset/data-enable/clock overrides, RX adaptation failures, CDR/DPLL/VCO calibration failures, unstable signal detect, DCC calibration issues, LBERT errors, and RX statistics counters that do not behave as expected.
- Decode known-good register dumps with these masks and compare against hardware documentation or reference tools for pstate, power-up timing, TX termination/EQ, RX ATT/VGA/CTLE/DFE/slicer, CDR/DPLL/VCO, DCC DAC, signal-detect, MPHY, and analog ATB/measurement fields.
- Treat ATE, OCLA/LBERT, and forced analog/debug override paths as controlled diagnostics only; forcing these bits can bypass normal PHY control.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL`, including the register comment and the first field definitions before `ovrd_reset_term`. This chunk completes that register and continues through lane 1 analog RX reserved fields before entering the lane 2 digital block.

The next chunk should complete `DPCSSYS_CR4_LANE2_ANA_RX_SQ` by adding the remaining masks after `afe_loopback_sel`, then continue lane 2 analog RX calibration and later CR4 lane definitions. The final merged per-file report should reconcile these split register groups before making whole-file coverage claims.

### subset-b-002375: lines 90537-92913

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 90537-92913

## Scope And Purpose

This chunk is generated AMD DPCS 4.2.2 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used to encode, update, and decode fields in the DPCS `CR4` PHY/control-register space. Runtime display-driver code pairs these `*_SHIFT` and `*_MASK` constants with the matching register offsets from `dpcs_4_2_2_offset.h` and AMD display register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `FD`, `SR`, and `SRI`.

The requested range starts inside the `DPCSSYS_CR4_LANE2_ANA_RX_SQ` field definitions and then covers the tail of lane 2 analog RX controls, a large lane 3 digital/analog TX/RX control section, raw common control and always-on common calibration fields, raw lane 0 PCS/PMA cross-interface fields, raw lane 0 FSM/status/IRQ fields, and the beginning of raw lane 0 TX control. Although this repository path is under `ceph-client`, the file is GPU display hardware register metadata, not distributed filesystem logic.

This slice contains 2,123 `#define` entries and 254 register comment markers. It is a chunk of a much larger generated header, so it intentionally documents only the visible `CR4` subset. Neighboring chunks are needed to complete the source-file-level report.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocation paths, or persistence APIs in this range. The public interface is the generated macro namespace:

- `DPCSSYS_CR4_<register>__<field>__SHIFT`: the low bit position for a field.
- `DPCSSYS_CR4_<register>__<field>_MASK`: the raw bitmask for the same field.
- `RESERVED_*`, `NC*`, and `RESERVED_REG_*` macros: generated reserved or not-connected bit ranges that should generally be preserved unless the ASIC programming guide explicitly defines a safe write value.

Major register families covered by this chunk:

- `DPCSSYS_CR4_LANE2_ANA_RX_*`: lane 2 analog RX squelch, DFE tap enable, calibration mux selection, ATB register reference and measurement controls, forced ATB calibration reference, and reserved analog RX fields.
- `DPCSSYS_CR4_LANE3_DIG_ASIC_*`: lane 3 ASIC-facing override inputs and status mirrors for lane loopback, TX request/pstate/rate/width/MPLL/data enable, TX cursor and pre/post-emphasis fields, HDMI mode, TX clock/reset/detect signals, RX AFE/CDR/equalization fields, and ASIC input/output mirrors.
- `DPCSSYS_CR4_LANE3_DIG_TX_PWRCTL_*`: lane 3 TX power-state register fields for P0/P0S/P1/P2, TX power-up timing registers, DCC bank address/data and DAC controls, TX clock alignment, and TX LBERT control.
- `DPCSSYS_CR4_LANE3_DIG_RX_STAT_*`: lane 3 RX pattern/statistic support, including load values, data masks, match-control words, sample-count controls, statistic counters 0-6, stop control, and calibration comparator clock control.
- `DPCSSYS_CR4_LANE3_DIG_ANA_*` and `DPCSSYS_CR4_LANE3_ANA_TX_*`: digital-to-analog TX override outputs, TX termination code controls, TX equalization override words, analog status readback, DCC DAC override controls, analog TX power/loopback/clock/alternate-bus/ATB/DCC/termination/miscellaneous fields, and reserved analog TX registers.
- `DPCSSYS_CR4_RAWCMN_DIG_*`: raw common control for MPLL A/B override, bandwidth override, spread-spectrum controls, common lane FSM extension, common control/status, MPLL state control, TX calibration code, SRAM init done, OCLA debug, supervisor analog override, PCS and firmware ID codes, and always-on common RTUNE/power-gating/resource/vref/reference-range/miscellaneous controls.
- `DPCSSYS_CR4_RAWLANE0_DIG_PCS_XF_*`: raw lane 0 PCS cross-interface TX/RX override, PCS input/output mirror, adaptation acknowledge/FOM, TX pre/main/post direction readbacks, lane number, ATE override, RX equalization override, TX/RX termination control, phase-2 calibration request/acknowledge, and reserved PCS fields.
- `DPCSSYS_CR4_RAWLANE0_DIG_FSM_*`: raw lane 0 firmware/FSM override, monitor, fast-start/calibration/adaptation flags, common calibration status, continuous calibration/adaptation status, CR lock, TX DCC status, OCLA debug, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANE0_DIG_IRQ_CTL_*`: raw lane 0 interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation events, lane transceiver mode, phase-2 calibration, RX-to-TX loopback, DCC on-demand, TX reset/request, and related clear bits.
- `DPCSSYS_CR4_RAWLANE0_DIG_PMA_XF_*`: raw lane 0 PMA cross-interface lane/MPLL/supervisor/TX/RX override and mirror fields, RTUNE request/acknowledge, MPHY PWM/async override fields, and RX adaptation phase-adjust map.
- `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_*`: beginning of raw lane 0 TX control fields for MPLL-off wait timing, RX-detect allowance by power state, TX clock selection, async beacon wait timing, and TX DCC continuous status.

Most field masks describe low 16-bit CR-register fields but are emitted with `0x0000....L` 32-bit-looking constants in this 4.2.2 header. Adjacent `dpcs_4_2_3_sh_mask.h` uses shorter `0x....L` spellings for many corresponding masks, so consumers should treat the numeric value, not textual width, as the contract.

## Control Flow

This header has no runtime control flow. It participates in hardware programming through compile-time token-pasted register access:

1. DCN resource or link code includes the DPCS 4.2.2 offset header and this shift/mask header for a supported ASIC generation.
2. Register helper macros combine a register token with a field token, expanding to the offset, mask, and shift constants.
3. Display link encoder, PHY, clock, power-management, calibration, debug, and interrupt paths read-modify-write hardware registers or poll status fields using those constants.
4. The DPCS hardware, PHY firmware, or autonomous finite-state machines perform the actual sequencing: PLL enable/disable, power-state transitions, clock selection, TX/RX request/ack handshakes, RX adaptation, calibration, interrupt latching, and status generation.

The chunk does not encode sequencing rules. Software must still order operations correctly around reference clocks, MPLL state, lane power, TX/RX reset and request handshakes, RX adaptation/calibration, DCC adjustment, RTUNE, power gating, and IRQ clear/mask behavior.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO or indirect CR-backed hardware state.

State represented by these fields includes:

- Analog RX/TX state: lane 2 RX squelch/calibration/ATB settings and lane 3 TX analog power, clock, loopback, DCC, termination, EQ, ATB, alternate-bus, and status fields.
- Digital lane state: lane 3 ASIC-facing TX/RX overrides and mirrors for rates, widths, p-states, MPLL selection, data enable, reset, request/acknowledge, loopback, RX adaptation, CDR/VCO load values, AFE/DFE/EQ settings, and TX de-emphasis/cursor values.
- Common PHY state: raw common MPLL A/B configuration and SSC fields, common control/status bits, firmware ID fields, OCLA debug selection, SRAM initialization, always-on RTUNE values for lanes 0-7, power-gating overrides, supervisor overrides, resource handshakes, VREF calibration status, reference range override, and MPLL powerdown time.
- Raw lane 0 PCS/PMA state: PCS and PMA TX/RX cross-interface controls, reset/request/data-enable overrides, RX detect/adaptation controls, TX/RX term controls, MPHY PWM/async controls, supervisor and lane MPLL enable mirrors, RTUNE request/acknowledge, and RX adaptation phase-adjust maps.
- Firmware/FSM and interrupt state: FSM override/jump/control fields, monitor/status flags, fast calibration/adaptation status bits, CR lock, DCC status, OCLA capture controls, TX EQ update flags, RX IQ phase offsets, IRQ status bits, IRQ clear bits, and IRQ masks.
- TX control state: raw lane 0 TX wait timers, per-pstate RX detect allowance, TX clock enable/selection, async beacon wait time, and DCC continuous enable status.

Persistence is hardware-defined. Configuration fields typically retain values until driver reprogramming, PHY or display-core reset, power gating, suspend/resume restore, firmware reinitialization, or ASIC reset. Status, interrupt, calibration, ack, monitor, and counter-like fields may be read-only, sticky, write-one-to-clear, self-clearing, or side-effect-sensitive. This mask header does not encode access policy, so runtime code must rely on the register specification and existing AMD display access conventions.

## Dependencies And Integration Points

This chunk depends on generated DPCS register metadata staying internally consistent:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the `ixDPCSSYS_CR4_*` register offsets that pair with these field masks.
- Adjacent DPCS headers such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` expose near-identical register families for related hardware revisions, making cross-version diffs a practical consistency signal.
- AMD display register-helper code consumes these macros through token-pasted field descriptors, so macro spelling and field names are part of the compile-time ABI for the driver source.

Functional integration points include DC link encoder and PHY programming, DisplayPort and HDMI link bring-up, high-speed lane power management, TX/RX equalization and adaptation, RX detect and hotplug-adjacent PHY behavior, spread-spectrum and MPLL clocking setup, firmware or microcode handoff, RTUNE and VREF calibration, power-gating entry/exit, suspend/resume restore, debug capture through OCLA/ATB/LBERT-style paths, and interrupt clear/mask handling for lane reset/request/rate/pstate/adaptation events.

The range is tightly coupled to neighboring chunks. It starts after the `DPCSSYS_CR4_LANE2_ANA_RX_SQ` shifts were already introduced and ends after only the first field of `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_TX_DCC_CONT_STATUS`, so complete register-family conclusions require the previous and next chunk reports.

## Risks And Edge Cases

- Mask or shift drift is the primary risk. These are untyped preprocessor constants, so incorrect generated values can compile cleanly while corrupting a different hardware field.
- The lane and raw-lane namespaces are repetitive. A generation, lane index, power state, TX/RX direction, or MPLLA/MPLLB copy error may affect only one connector, lane, link rate, or power transition.
- Override enables are hazardous when firmware or hardware FSMs own the same signal. Incorrect use of `*_OVRD_EN`, `*_OVRD_VAL`, `ASIC_*_OVRD_*`, `PMA_XF_*_OVRD_*`, or `PCS_XF_*_OVRD_*` fields can force resets, requests, clocks, data enables, power, loopback, adaptation, or calibration into a stale state.
- Interrupt clear and mask fields are side-effect-sensitive. Using the wrong clear mask can drop or preserve stale IRQ status, causing missed adaptation/reset/request events or repeated interrupt handling.
- Reserved and not-connected fields are named but should not be treated as writable feature fields. Read-modify-write helpers must preserve unrelated bits, especially in analog, common, and power-gating registers.
- Analog calibration, RTUNE, VREF, DCC, and equalization fields can produce failures that are intermittent or hardware-revision-specific. Bad masks may appear only at high link rates, after resume, under hotplug churn, or during factory/debug modes.
- TX/RX PCS/PMA handshake fields are sequencing-sensitive. Wrong request, acknowledge, reset, data-enable, power-state, or MPLL-state fields can cause link training timeouts, stuck low-power states, failed RX detect, or blank/flickering displays.
- Header width conventions differ across generated revisions. Local code should not assume that a `0x0000....L` spelling implies a 32-bit hardware register when the active field is a 16-bit DPCS CR field.

## Test Signals

Useful validation signals are mostly compile-time, static, and hardware-integration oriented:

- Build coverage for the AMD display resource/link code that includes `dpcs_4_2_2_sh_mask.h`, catching missing, renamed, or malformed macros.
- Static consistency checks that every visible field has a matching `__SHIFT` and `_MASK`, active masks stay within the expected low 16-bit DPCS CR width, and shift/mask pairs agree on field width and position.
- Cross-version generated-header diffs against `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` to find unexpected changes in corresponding `CR4` lane/common/raw-lane fields.
- Display smoke tests on the ASIC generation that uses DPCS 4.2.2: HDMI and DisplayPort modesets, hotplug, EDID/DPCD access, link training across rates and lane counts, multi-monitor operation, suspend/resume, and power-state cycling.
- PHY debug evidence: successful MPLL state transitions, stable TX/RX request and acknowledge handshakes, expected RTUNE and VREF calibration status, correct RX adaptation/FOM behavior, sane DCC and EQ status, no unexpected FSM error/status bits, and no repeated or missing lane IRQ events.
- Regression signals include blank or flickering displays, DP training failures, HDMI clocking issues, wake/resume failures, stuck PHY power states, RX detect failures, unexpected IRQ storms, timeout logs around register polling, and failures isolated to lane 3 or raw lane 0 paths covered by this chunk.

### subset-b-002376: lines 92914-95292

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 92914-95292

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for the CR4 raw-lane digital register space. It contains only preprocessor constants: `__SHIFT` macros define field bit positions and `_MASK` macros define field masks for 16-bit-shaped DPCS control/status registers. In this line range there are 2,111 `#define` entries across 268 register-comment groups, with 1,058 shift constants and 1,053 mask constants.

The chunk starts in the middle of `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_TX_DCC_CONT_STATUS`, covers the tail of raw lane 0 TX/RX control and ATE PCS override fields, then covers a large raw lane 1 and raw lane 2 digital control surface. It ends inside `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN`. Although the path is under a `ceph-client` source mirror, this header is AMDGPU display PHY register metadata and has no Ceph filesystem behavior.

## Purpose

The purpose of this header slice is to provide AMDGPU display code with generated bitfield metadata for programming DPCS 4.2.2 CR4 raw-lane PCS, FSM, IRQ, PMA, TX-control, and RX-control registers. Consumers pair these macros with the matching `ixDPCSSYS_CR4_RAWLANE*...` address definitions from `dpcs_4_2_2_offset.h` and AMD display register helpers, allowing driver code to assemble read-modify-write values without open-coding bit numbers.

The covered fields describe:

- Raw lane 0 late TX/RX control and ATE-facing PCS override fields, including OCLA/debug enables, RX FSM and loss-of-signal masking, RX data-enable override timing, adaptation/off-channel continuous status, rate/width/P-state/low-power detect overrides, loopback bits, master MPLL loop controls, VCO/ref load overrides, RX valid override, and TX data/async override bits.
- Raw lane 1 PCS transmit and receive handshakes, override inputs/outputs, PCS inputs/outputs, RX adaptation status/FOM, directed TX pre/main/post controls, lane-number readback, ATE override controls, EQ/termination/phase calibration registers, FSM control/status/fast-calibration flags, IRQ status/clear/mask fields, PMA interface overrides, TX/RX control registers, and lane 1 ATE PCS overrides.
- Raw lane 2 mirrors of the lane 1 PCS/FSM/IRQ/PMA/TX/RX control surface, including the same request/ack, reset, P-state/rate/width, RX adaptation, EQ, termination, phase calibration, fast-calibration, IRQ, PMA handshake, MPHY, TX/RX control, and ATE override families.
- The beginning of raw lane 3 PCS TX override input fields for P-state, low-power detect, width, rate, MPLL selection/enables, master MPLL state overrides, and TX async enable overrides.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocations, or direct MMIO operations in this chunk. The exported interface is the generated macro namespace:

- `DPCSSYS_CR4_RAWLANE*_*__FIELD__SHIFT`: least-significant bit index for `FIELD`.
- `DPCSSYS_CR4_RAWLANE*_*__FIELD_MASK`: bit mask for the same field.
- Register delimiter comments such as `//DPCSSYS_CR4_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK`: field-group markers that correspond to address macros in the companion offset header.

Notable PCS transfer/interface groups include:

- `DIG_PCS_XF_TX_OVRD_IN`, `DIG_PCS_XF_TX_OVRD_IN_1`, and `DIG_PCS_XF_TX_OVRD_IN_2`: TX-side override values/enables for reset, request, P-state, low-power detect, width, rate, MPLL selection/enables, master MPLL state, detect-RX request, VBOOST, IBOOST level, beacon, loopback, TX data enable, async data, and async enable.
- `DIG_PCS_XF_TX_PCS_IN`, `DIG_PCS_XF_TX_OVRD_OUT`, and `DIG_PCS_XF_TX_PCS_OUT`: PCS TX request/reset inputs and acknowledgement/detect-result/status outputs.
- `DIG_PCS_XF_RX_OVRD_IN`, `DIG_PCS_XF_RX_OVRD_IN_1` through `_3`, and ATE variants: RX-side override fields for rate, width, P-state, low-power detect, adaptation enable/request/continuous modes, reset/request, RX loss-of-signal thresholds, VCO/ref load values, CDR VCO low-frequency indication, RX data enable, and loopback.
- `DIG_PCS_XF_RX_PCS_IN` through `_4`: PCS RX inputs for request, rate, width, P-state, low-power detect, CDR VCO low-frequency, adaptation AFE/DFE, adaptation/off-channel continuous modes, reset, ref/VCO load values, EQ attenuation/VGA/CTLE/DFE fields.
- `DIG_PCS_XF_RX_OVRD_OUT`, `DIG_PCS_XF_RX_PCS_OUT`, `DIG_PCS_XF_RX_OVRD_OUT_1`, and `DIG_PCS_XF_RX_OVRD_OUT_2`: RX acknowledgements, control-enable status, RX clock enable, and RX valid override/readback fields.
- `DIG_PCS_XF_RX_ADAPT_ACK`, `DIG_PCS_XF_RX_ADAPT_FOM`, `DIG_PCS_XF_RX_TXPRE_DIR`, `DIG_PCS_XF_RX_TXMAIN_DIR`, and `DIG_PCS_XF_RX_TXPOST_DIR`: adaptation completion/quality and directed transmit-cursor feedback.
- `DIG_PCS_XF_ATE_OVRD_IN`, `DIG_PCS_XF_RX_EQ_DELTA_IQ_OVRD_IN`, `DIG_PCS_XF_TXRX_TERM_CTRL_OVRD_IN`, `DIG_PCS_XF_TXRX_TERM_CTRL_IN`, `DIG_PCS_XF_RX_EQ_OVRD_IN_1`, `DIG_PCS_XF_RX_EQ_OVRD_IN_2`, and `DIG_PCS_XF_RX_PH2_CAL`: ATE/debug hooks for reset/request/data-enable overrides, RX EQ, termination, delta-IQ, and phase-2 calibration handshake.

Notable FSM groups include:

- `DIG_FSM_FSM_OVRD_CTL`, `DIG_FSM_MEM_ADDR_MON`, and `DIG_FSM_STATUS_MON`: FSM jump/command/break override control and status/readiness monitoring.
- `DIG_FSM_FAST_RX_*`, `DIG_FSM_FAST_TX_*`, and `DIG_FSM_FAST_SUP`: fast-path calibration/adaptation flags for RX startup, AFE/DFE, bypass, reference level, IQ, continuous calibration/adaptation/data/phase/AFE operations, TX common-mode, TX RX-detect, and supervisor behavior.
- `DIG_FSM_CMNCAL_MPLL_STATUS`, `DIG_FSM_CMNCAL_RCAL_STATUS`, `DIG_FSM_TX_DCC_FLAGS`, `DIG_FSM_TX_DCC_STATUS`, `DIG_FSM_TX_EQ_UPDATE_FLAG`, and `DIG_FSM_RX_IQ_PHASE_OFFSET`: calibration status and tuning observability fields.
- `DIG_FSM_FAST_FLAGS` and `DIG_FSM_CR_LOCK`: consolidated fast-calibration flags and CR register/memory lock bits.

Notable IRQ groups include:

- Status bits for RX reset, RX request, RX rate, RX P-state, RX adaptation request/disable, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX loopback enable, DCC on-demand, TX reset, and TX request.
- Matching `_CLR` groups for write-to-clear style acknowledgement of those events.
- `DIG_IRQ_CTL_IRQ_MASK` and `DIG_IRQ_CTL_IRQ_MASK_2` fields that mask RX-side, lane-mode, phase-calibration, loopback, DCC, TX reset, and TX request interrupts.

Notable PMA/TX/RX control groups include:

- `DIG_PMA_XF_LANE_OVRD_IN/OUT`, `DIG_PMA_XF_SUP_OVRD_IN`, and `DIG_PMA_XF_SUP_PMA_IN`: lane MPLL and supervisor state override/readback.
- `DIG_PMA_XF_TX_OVRD_OUT`, `DIG_PMA_XF_TX_PMA_IN`, `DIG_PMA_XF_RX_OVRD_OUT`, and `DIG_PMA_XF_RX_PMA_IN`: PMA-facing TX/RX request, reset, beacon, async, loopback, data-enable, and acknowledgement fields.
- `DIG_PMA_XF_LANE_RTUNE_CTL`, `DIG_PMA_XF_SUP_PMA_IN_1`, `DIG_PMA_XF_MPHY_OVRD_IN`, `DIG_PMA_XF_MPHY_OVRD_OUT`, and `DIG_PMA_XF_RX_ADAPT_OVRD_OUT`: lane retune, low-speed MPHY PWM/termination/async, and RX adaptation phase-adjust map fields.
- `DIG_TX_CTL_TX_FSM_CTL`, `DIG_TX_CTL_TX_CLK_CTL`, `DIG_TX_CTL_TX_DCC_CONT_STATUS`, `DIG_TX_CTL_OCLA`, and `DIG_TX_CTL_UPCS_OCLA`: TX FSM timing, RX-detect allowance per power state, TX clock selection/enables, async beacon timing, DCC continuous status, and OCLA capture controls.
- `DIG_RX_CTL_RX_FSM_CTL`, `DIG_RX_CTL_RX_LOS_MASK_CTL`, `DIG_RX_CTL_RX_DATA_EN_OVRD_CTL`, `DIG_RX_CTL_OFFCAN_CONT_STATUS`, `DIG_RX_CTL_ADAPT_CONT_STATUS`, and `DIG_RX_CTL_UPCS_OCLA`: RX FSM enable/rate-change behavior, loss-of-signal masking, RX data-enable timing, off-channel/adaptation continuous status, and OCLA capture controls.

## Control Flow

This header has no runtime control flow. It supplies compile-time constants only. Runtime sequencing lives in AMD display/DC code that includes this header, selects the appropriate DPCS register address, reads the current register value, preserves unrelated and reserved bits, applies masks/shifts, and writes the updated value back to indexed DPCS hardware.

The implied hardware control flows are sensitive PHY paths: PCS request/ack transitions, TX/RX reset sequencing, P-state/rate/width changes, MPLL selection and master-state overrides, RX adaptation, RX EQ and termination overrides, phase calibration, DCC and VCO/ref load handling, PMA request/ack handshakes, interrupt/status polling and clearing, OCLA debug capture, low-speed MPHY behavior, and TX/RX continuous calibration status handling. This chunk describes the bit layout for those flows but does not enforce ordering, timeouts, polling loops, access direction, or reset cleanup.

## State And Persistence Behavior

The macros are stateless compile-time constants. The mutable state they describe lives in volatile DPCS CR4 raw-lane hardware registers. Those registers may be changed by link training, modesets, hotplug handling, PHY retuning, suspend/resume, GPU reset recovery, power gating, firmware or hardware state machines, and diagnostic tooling.

Several field families are stateful in hardware:

- Request, acknowledge, reset, ready, valid, calibration-done, and interrupt bits represent transient handshakes or latched status.
- P-state, rate, width, MPLL, clock-enable, data-enable, loopback, low-power detect, termination, RX EQ, adaptation, and PMA override fields influence active PHY behavior until rewritten or reset.
- Value/enable override pairs are common. Setting an override value without its enable bit may have no effect; leaving an enable bit asserted can keep normal PCS/PMA/FSM control bypassed after a debug or ATE path finishes.
- Reserved masks are widespread and should be preserved during read-modify-write operations unless authoritative hardware documentation requires a defined write.

## Dependencies

This chunk depends on the AMD ASIC register-generation source remaining synchronized with DPCS 4.2.2 silicon documentation. The key paired file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which defines matching register addresses such as `ixDPCSSYS_CR4_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`, `ixDPCSSYS_CR4_RAWLANE1_DIG_FSM_STATUS_MON`, and `ixDPCSSYS_CR4_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK`.

The in-tree AMD display resource consumers include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which include `dpcs_4_2_2_sh_mask.h` and build DPCS register shift/mask tables through `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`. Related register-list definitions live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`.

## Integration Points

This chunk integrates with AMDGPU display PHY programming for DPCS 4.2.2 hardware, particularly DCN 3.1.x-style link encoder/resource setup. The macros are not useful alone; they must be paired with the corresponding CR4 raw-lane address macros and the display register helper layer that performs indexed register access.

Correct integration requires three alignments:

- ASIC-version alignment: use DPCS 4.2.2 offsets with DPCS 4.2.2 masks/shifts, not neighboring generated DPCS versions.
- Instance alignment: use `CR4` raw-lane masks only with `CR4` raw-lane register addresses.
- Lane alignment: use `RAWLANE0`, `RAWLANE1`, `RAWLANE2`, and `RAWLANE3` masks only with their matching lane addresses and physical-lane programming path.

This range is especially relevant to low-level PHY diagnostics and bring-up because it exposes ATE override, OCLA capture, fast-calibration, PMA handshake, IRQ mask/clear, and continuous calibration/adaptation control fields that sit below the higher-level display link policy code.

## Risks And Edge Cases

- Chunk boundaries are not semantic. The first line is the final mask for `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_TX_DCC_CONT_STATUS`, and the final lines stop before `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` is complete.
- These are untyped preprocessor constants. A wrong shift, mask, or lane prefix can compile successfully and only surface as hardware misprogramming.
- Generated header edits can diverge from AMD's register database, the companion offset header, firmware assumptions, and silicon documentation.
- Lane repetition is copy-sensitive. Raw lane 1 and raw lane 2 are largely mirrored, but using a lane 1 field with a lane 2 address, or applying a raw-lane mask to a non-raw-lane address, can program the wrong hardware.
- Override value/enable pairs are easy to misuse. Leaving override enables asserted after ATE/debug use can break later link training, power management, hotplug handling, or suspend/resume.
- PCS/PMA request-ack and IRQ clear/mask fields are sequencing-sensitive. Incorrect masks can cause false readiness, missed interrupts, uncleared latched status, stuck state-machine waits, or failure recovery loops.
- Analog-adjacent fields such as RX EQ, termination, VCO/ref load, MPLL state, DCC, and IQ phase can fail only under specific link rates, lane counts, cables, boards, sinks, temperature, or voltage corners.
- Reserved bits are common. Consumers should preserve reserved fields during read-modify-write operations and should not assume the whole 16-bit register may be freely rewritten.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`, especially DCN315/DCN316 resource table initialization and DCN31 link encoder register tables.
- Static generation checks that complete fields have matching `__SHIFT` and `_MASK` constants, masks align with their shifts and intended widths, and all masks remain within the expected DPCS CR register shape.
- Cross-checks against `dpcs_4_2_2_offset.h` to ensure each CR4 raw-lane register-comment group in this range has a corresponding `ixDPCSSYS_CR4_RAWLANE*...` address macro.
- Repetition checks between raw lane 1 and raw lane 2 where the hardware model expects identical layouts, while allowing chunk-boundary splits and intentional lane-specific differences.
- Display bring-up, hotplug, modeset, blank/unblank, suspend/resume, and GPU reset recovery on hardware using DPCS 4.2.2.
- Link-training stress across lane counts and link rates that exercises PCS/PMA request-ack flows, P-state/rate/width changes, RX adaptation, TX/RX data-enable overrides, MPLL selection, and low-power transitions.
- PHY diagnostic coverage for OCLA, ATE override paths, RX EQ and termination overrides, phase-2 calibration, fast-calibration flags, DCC on-demand IRQs, RX/TX reset/request IRQs, PMA retune, MPHY PWM/termination, and RX adaptation FOM/ack readback.
- Register dumps from failed link training decoded with these masks to confirm request/ack state, interrupt masks/clears, TX/RX control bits, PMA override state, calibration flags, and reserved-bit preservation.

## Cross-Chunk Notes

The previous chunk is required to reconstruct the complete `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_TX_DCC_CONT_STATUS` group and earlier raw lane 0 definitions. This chunk then completes late raw lane 0 control/ATE fields and covers most of raw lanes 1 and 2. The following chunk is required for the remainder of raw lane 3 and for any whole-register claims about `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN`.

### subset-b-002377: lines 95293-97714

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 95293-97714

## Scope

This chunk covers lines 95293-97714 of the generated AMD DPCS 4.2.2 shift/mask header. It is a partial view of one oversized source file; the final source-file research document should be produced later by the chunk merge lane.

The chunk contains 2,084 `#define` constants grouped under 338 register-comment blocks. All definitions are preprocessor constants, not executable logic. Each hardware field normally appears as a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

These constants describe bit positions and bit masks for DPCS CR4 raw-lane, PCS/PMA, interrupt, FSM, ATE, and always-on-lane registers used by AMD display code.

## Purpose

The header provides compile-time metadata for programming DisplayPort/DPCS PHY registers on DCN 3.1.5-era AMD display hardware. This chunk is centered on `DPCSSYS_CR4`, especially:

- tail definitions for `RAWLANE3` PCS transmit/receive control, PMA bridge, finite-state-machine, interrupt, test, and calibration registers;
- repeated `RAWAONLANE0`, `RAWAONLANE1`, and the beginning of `RAWAONLANE2` always-on lane status/control fields for RX adaptation, DFE, signal detect, MPLL, calibration, DCC, and firmware configuration.

The companion offset header (`dpcs_4_2_2_offset.h`) supplies register addresses such as `ixDPCSSYS_CR4_RAWAONLANE1_DIG_RX_SIGDET_CONFIG` and `ixDPCSSYS_CR4_RAWAONLANE2_DIG_RX_LOS_MASK_CTL`; this header supplies the field layout needed to read, mask, shift, and update those registers correctly.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The important exported surface is the macro namespace consumed by AMD display register helpers.

Key macro families in the chunk include:

- `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_*`: PCS cross-interface fields for TX/RX resets, requests, rates, widths, power states, MPLL state, VCO/ref load values, RX adaptation, RX/TX pre/main/post direction, lane number, ATE overrides, equalization, termination, and phase-2 calibration.
- `DPCSSYS_CR4_RAWLANE3_DIG_FSM_*`: FSM override/status fields, fast calibration/adaptation selectors, common-calibration status, register/memory lock bits, TX DCC flags/status, OCLA enable bits, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANE3_DIG_IRQ_CTL_*`: interrupt request, clear, and mask bits for RX reset/request/rate/pstate/adaptation events, lane transceiver-mode changes, RX phase-2 calibration events, loopback events, on-demand DCC events, and TX reset/request events.
- `DPCSSYS_CR4_RAWLANE3_DIG_PMA_XF_*`: PMA bridge fields for lane/MPLL enables, supervisor state, TX/RX override outputs, RTUNE control, MPHY override, RX adaptation override output, and PMA-side signal state.
- `DPCSSYS_CR4_RAWLANE3_DIG_TX_CTL_*` and `DPCSSYS_CR4_RAWLANE3_DIG_RX_CTL_*`: TX/RX FSM, clock, DCC, OCLA, LOS mask, data-enable override, off-channel continuous status, and adaptation continuous status fields.
- `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_ATE_*`: automated-test-equipment override definitions for RX/TX PCS inputs, data enables, loopback, beacon, async data, LOS LFPS, LOS threshold, adaptation, VCO, and ref-load overrides.
- `DPCSSYS_CR4_RAWAONLANE[0-2]_DIG_*`: repeated per-lane always-on definitions for adaptation readback, DFE offsets, RX phase/slicer controls, MPLL/RCAL status, adaptation control words, RX/TX disable overrides, LOS/signal-detect controls, analog stats, PMA signal overrides, signal-detect calibration, DCC calibration codes, TX DCC bank access, MPLL bandgap controls, firmware config, lane transceiver mode, and DCC/sigdet config.

The densest multi-field registers in this chunk are `FAST_FLAGS`, `FAST_FLAGS_2`, `PCS_XF_ATE_OVRD_IN`, `PMA_XF_TX_OVRD_OUT`, `PCS_XF_TX_OVRD_IN_1`, `PCS_XF_RX_PCS_IN`, and `IRQ_CTL_IRQ_MASK`.

## Control Flow

The chunk has no local control flow. Its values participate in control flow indirectly when AMD display code uses register-helper macros such as `REG_GET`, `REG_UPDATE`, `LE_SF`, `SRI`, and related DC resource-table initializers.

Observed integration in the surrounding tree:

- `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and this `dpcs/dpcs_4_2_2_sh_mask.h`.
- The same resource file builds DPCS register, shift, and mask tables with `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(__SHIFT/_MASK)`.
- Runtime code later uses those tables through AMD display register access helpers, so these macros become the bitfield contract for register reads/writes rather than direct function calls.

Because this is generated register metadata, any meaningful runtime sequence is owned by the display link encoder, HPO encoder, resource, hardware sequencer, or PHY programming code that consumes these constants.

## State and Persistence Behavior

This chunk does not allocate memory or persist software state. Its constants describe persistent hardware register state in DPCS PHY blocks:

- request/ack/reset bits represent hardware handshakes for PCS/PMA TX and RX paths;
- power, width, rate, MPLL, VCO, ref-load, and pstate fields represent lane configuration state;
- adaptation, DFE, CTLE, VGA, slicer, signal-detect, and phase-adjust fields expose analog calibration state;
- interrupt mask/clear/status fields represent sticky or event-driven hardware state;
- `*_OVRD_*` fields can force hardware behavior away from normal FSM-driven values;
- `FAST_FLAGS` and calibration-status fields capture fast-path calibration enablement and completion state.

The values are persistent only as compiled constants in the driver binary; the actual state lives in MMIO/indirect DPCS registers on the GPU.

## Dependencies

Direct dependencies are preprocessor-level only:

- the header guard `_dpcs_4_2_2_SH_MASK_HEADER`;
- matching register-address definitions in `dpcs_4_2_2_offset.h`;
- AMD display register-access macros that expect `__SHIFT` and `_MASK` naming conventions.

The chunk is tightly coupled to the DPCS 4.2.2 hardware register specification. Neighbor headers (`dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_3_sh_mask.h`) contain similar definitions but with version-specific line placement and sometimes literal formatting, so cross-version substitution should be treated as hardware-sensitive.

## Integration Points

The primary integration point is AMDGPU display core for DCN 3.1.5 resources. The dcn315 resource code includes this header and the companion offset header, defines DPCS base segments, and populates link encoder mask/shift structures.

The definitions are also part of a generated ASIC register include tree under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`. Code that builds per-link encoder resources, DisplayPort PHY controls, or DPCS/RDPCS register tables depends on the names and masks matching both the offset header and the actual silicon register layout.

Within this chunk, integration boundaries include:

- PCS-side link training and lane control via TX/RX request, reset, rate, width, pstate, MPLL, and adaptation fields;
- PMA-side analog control via MPLL enables, RTUNE, MPHY, RX/TX PMA override, signal detect, and calibration fields;
- interrupt plumbing via `DIG_IRQ_CTL_*` request, clear, and mask definitions;
- debug/test flows via ATE override registers and OCLA fields;
- firmware or microcontroller policy hooks via `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG` always-on-lane registers.

## Risks and Edge Cases

- Bitfield drift is the primary risk. A wrong shift or mask can silently program the wrong hardware bit, causing link-training failure, display blanking, unstable signal detect, broken calibration, or bad interrupt behavior.
- Override fields are high risk because many pairs include both value and enable bits. Setting an override value without the corresponding enable bit, or leaving an enable bit asserted after debug/test use, can force the PHY into an unexpected state.
- Repeated lane blocks are easy to copy incorrectly. `RAWAONLANE0`, `RAWAONLANE1`, and `RAWAONLANE2` share many field layouts, but callers must still use the matching register address for the intended lane.
- Reserved masks are present throughout. Runtime code should avoid writing reserved bits except through documented reset values or read-modify-write helpers that preserve them.
- Interrupt clear and mask registers have similar names but different semantics. Mixing `*_IRQ`, `*_IRQ_CLR`, and `*_IRQ_MSK` fields can lose events or leave interrupts permanently masked.
- This chunk starts after the beginning of `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` and ends inside `DPCSSYS_CR4_RAWAONLANE2_DIG_RX_SIGDET_FILT_CTRL`; final whole-file research must merge with adjacent chunks to capture complete register families.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration oriented:

- successful AMDGPU/DC display compilation with `dcn315_resource.c` including `dpcs_4_2_2_sh_mask.h`;
- no duplicate or missing macro errors when generating `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`;
- static comparison against the vendor register database or neighboring generated headers for expected DPCS 4.2.2 field positions;
- display link-training and hotplug tests on DCN 3.1.5 hardware using multiple lanes/rates, watching for RX/TX request/ack, pstate/rate, MPLL, signal-detect, and adaptation regressions;
- interrupt behavior tests that exercise RX request/rate/pstate/adaptation, lane mode, phase-2 calibration, DCC, and TX request/reset events;
- PHY calibration diagnostics that confirm `FAST_FLAGS`, DCC/RCAL/MPLL status, RX adaptation done, and signal-detect calibration fields report sane values.

## Chunk Notes for Merge Lane

This chunk should be merged with adjacent chunks of the same header to build a source-file-level report. Adjacent context is needed for the complete `DPCSSYS_CR4_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` block before line 95293 and the rest of `DPCSSYS_CR4_RAWAONLANE2` after line 97714.

### subset-b-002378: lines 97715-100131

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 97715-100131

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for the CR4 register instance. It contains only C preprocessor constants: `__SHIFT` macros define field bit positions and `_MASK` macros define corresponding field masks for 16-bit DPCS CR registers. The range starts in the middle of `DPCSSYS_CR4_RAWAONLANE2_DIG_RX_SIGDET_FILT_CTRL`, finishes the remaining raw always-on lane 2 fields, covers the full raw always-on lane 3 and raw always-on lane X template blocks, then moves into shared `SUPX` digital and analog control for ID code, reference clocks, MPLLA/MPLLB overrides, ASIC input mirrors, prescaler, RTUNE, bandgap, shared analog levels, PLL analog controls, MPLL power-control/status, SSC spread type, and shared clock/reset timing. It ends in the middle of `DPCSSYS_CR4_SUPX_DIG_RTUNE_CONFIG`.

The chunk includes about 2,101 macro definitions across 317 register groups. The major groups are raw always-on lane 2 tail content, raw lane 3, raw lane X, `SUPX_DIG`, and `SUPX_ANA`.

## Purpose

The header provides compile-time bitfield metadata used by AMDGPU display/PHY code when programming DPCS 4.2.2 hardware. Consumers pair these masks and shifts with matching address macros from the companion DPCS offset header and with AMD display register-access helpers to assemble read-modify-write values without open-coding numeric bit positions.

In this range, the fields describe:

- Tail-end CR4 raw always-on lane 2 receiver signal-detect, squelch, VREF, calibration code, DCC code, TX DCC bank, MPLL background control, firmware configuration, transceiver-mode, and signal-detect configuration registers.
- Complete CR4 raw always-on lane 3 and raw lane X layouts for RX adaptation, DFE/slicer/phase offsets, MPLL coarse tuning, initialization and fast-calibration flags, common calibration status, TX/RX override inputs, signal-detect control, VREF/calibration/DCC code readback, TX DCC bank access, firmware configuration, and lane transceiver-mode programming.
- Shared CR4 `SUPX_DIG` control for ID code readback, reference-clock override, MPLLA/MPLLB divider and HDMI-clock override, PLL multiplier/SSC/fractional-N/charge-pump parameters, ASIC-provided PLL/reference control mirrors, global PHY reset/reference/RTUNE handshake, prescaler, level override, and debug fields.
- Shared CR4 `SUPX_ANA` control for prescaler analog settings, RTUNE analog settings, bandgap/reference-voltage selection, power measurement switching, MPLLA/MPLLB analog override, ATB measurement, loop-filter/charge-pump/VREG/DLL controls, and reserved analog tuning fields.
- MPLLA/MPLLB power-control status and timing registers, including override selection, fast power-up/lock bits, DTB selection, clock enable state, calibration/reset/lock status, DAC range/output, lock/stable timers, PCLK power timing, MPLL calibration override, and SSC spread type.
- Shared clock/reset timing for bandgap and reference power-up plus the beginning of RTUNE debug/configuration fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or callable APIs in this chunk. The public interface is the generated macro naming contract:

- `DPCSSYS_CR4_RAWAONLANE*_...__FIELD__SHIFT`: bit offset for `FIELD` in a raw always-on lane register.
- `DPCSSYS_CR4_RAWAONLANE*_...__FIELD_MASK`: mask for the same raw lane field.
- `DPCSSYS_CR4_SUPX_DIG_...__FIELD__SHIFT` and `_MASK`: shared digital/register-interface bit metadata.
- `DPCSSYS_CR4_SUPX_ANA_...__FIELD__SHIFT` and `_MASK`: shared analog-control bit metadata.
- Register delimiter comments such as `//DPCSSYS_CR4_SUPX_DIG_MPLLA_OVRD_IN_0` mark groups that correspond to address macros in `dpcs_4_2_2_offset.h`.

Notable raw always-on lane groups include:

- `DIG_AFE_*`, `DIG_DFE_*`, `DIG_RX_ADPT_*`, `DIG_RX_ADAPT_*`, `DIG_RX_SLICER_*`, `DIG_RX_PHSADJ_*`, and `DIG_RX_IQ_PHASE_ADJUST`: RX adaptation, CTLE/VGA/ATT, DFE tap/ref-level offsets, slicer DAC offsets, phase adjustment, figure-of-merit, and adaptation-done readback fields.
- `DIG_FAST_FLAGS` and `DIG_FAST_FLAGS_2`: fast or skip controls for PLL, TX/RX DCC, RX continuous calibration, TX RTUNE, RX VPHUD/VREF, RX signal detect, adaptation, and related calibration paths.
- `DIG_INIT_PWRUP_DONE`, `DIG_LANE_CMNCAL_MPLL_STATUS`, and `DIG_LANE_CMNCAL_RCAL_STATUS`: initialization, MPLL common calibration, and RCAL status bits.
- `DIG_MPLL_DISABLE`, `DIG_MPLLA_COARSE_TUNE`, `DIG_MPLLB_COARSE_TUNE`, and `DIG_MPLL_BG_CTL`: lane-local MPLL disable/coarse-tune/background-state wait controls.
- `DIG_TXRX_OVRD_IN`, `DIG_LANE_XCVR_MODE_OVRD_IN`, and `DIG_LANE_XCVR_MODE_IN`: override and readback fields for RX/TX disable and lane transceiver mode.
- `DIG_RX_SIGDET_*`, `DIG_SIGDET_OUT_*`, `DIG_RX_LOS_MASK_CTL`, `DIG_STATS`, and `DIG_RX_OVRD_OUT_*`: signal-detect filtering/calibration/output override, loss-of-signal mask count, RX PMA squelch/VREF/termination/sigdet override, and RX status fields.
- `DIG_CAL_*`, `DIG_RX_DCC_CAL_*`, `DIG_TX_DCC_*`, and `DIG_TX_DCC_CONFIG`: calibration code readbacks and TX/RX duty-cycle-correction bank/configuration fields.
- `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, and `DIG_FW_CALIB_CONFIG`: firmware-facing configuration fields for memory-management, adaptation, and calibration behavior.

Notable `SUPX_DIG` groups include:

- `IDCODE_LO` and `IDCODE_HI`: 16-bit ID-code halves.
- `REFCLK_OVRD_IN`, `ASIC_IN`, `BANDGAP_ASIC_IN`, `LVL_OVRD_IN`, and `LVL_ASIC_IN`: reference-clock, PHY reset, bandgap, RTUNE handshake, voltage/reference level, and ASIC mirror fields.
- `MPLLA_*` and `MPLLB_*` override/input groups: enable, dividers, HDMI pixel clock, multiplier, VCO frequency, standby, calibration force, SSC enable/up-spread, PMIX, word-divide, fractional-N quotient/remainder/denominator, SSC peak/step-size, clock-sync, and charge-pump proportional/integral gain controls.
- `SUP_OVRD_IN`, `SUP_OVRD_OUT`, and `PRESCALER_OVRD_IN`: prescaler override, RTUNE request/ack, TX calibration code override, alternate low-power reference-clock selection, MPLLA/MPLLB and bandgap state override/readback, DCO range/fine-tune, reference dividers, and clock-detect controls.
- `MPLLA_MPLL_PWR_CTL_*` and `MPLLB_MPLL_PWR_CTL_*`: shared MPLL power FSM override/status, timers, DAC, calibration, and analog DAC readout fields.
- `CLK_RST_*`, `RTUNE_DEBUG`, and `RTUNE_CONFIG`: shared bandgap/reference power-up timing, VPHUD reference control, manual RTUNE debug, and RTUNE enable/configuration fields.

Notable `SUPX_ANA` groups include:

- `PRESCALER_CTRL` and `RTUNE_CTRL`: analog prescaler ATB/measurement/fast-start/VREG settings and RTUNE ATB, DAC mode/chop, force-continuous, and feedback-divider control.
- `BG1`, `BG2`, `BG3`, and `SWITCH_PWR_MEAS`: shared bandgap/reference-voltage selectors, temperature/power measurement, ATB switch, VPHUD/reference selection, and TX swing/RX calibration reference fields.
- `MPLLA_*` and `MPLLB_*` analog groups: matching analog controls for override enable/calibration/reset/feedback clock, ATB measurement, loop filter, charge pump, SPO calibration, VREG bypass/gain, DLL/divider reserved controls, and analog tuning.

## Control Flow

This header contributes no runtime control flow. Runtime sequencing lives in AMDGPU display and PHY code that uses these constants to read, mask, shift, and write indexed DPCS CR registers.

The implied hardware sequences in this chunk are sensitive PHY bring-up and diagnostic paths: lane RX adaptation and calibration, signal-detect calibration/filtering, TX/RX disable override, DCC bank programming, transceiver-mode selection, shared reference-clock selection, bandgap startup, MPLLA/MPLLB divider/SSC/fractional-N programming, charge-pump and analog tuning, RTUNE handshakes, MPLL power FSM transitions, and shared clock/reset timing.

## State And Persistence

The macros are stateless compile-time constants. The mutable state they describe lives in volatile DPCS hardware registers. That state can be changed by display link training, modesets, hotplug handling, PHY reinitialization, suspend/resume, GPU reset recovery, power gating, and debug or validation tools.

Some fields represent latched or sampled hardware status, such as adaptation done, initialization done, RCAL and MPLL common-calibration status, RX PMA squelch/status, signal-detect readback, RTUNE acknowledgement, reference-clock acknowledgement, MPLLA/MPLLB state, MPLL FSM state, clock-enable state, calibration/reset state, lock status, and analog DAC output. Other fields are override values or override enables; leaving override enables asserted after diagnostics can persistently redirect normal PHY control until the register is restored or reset.

The many reserved masks are part of the hardware contract. Consumers should preserve reserved bits during read-modify-write operations unless a hardware sequence explicitly documents otherwise. This is especially important here because most groups are 16-bit CR registers and many analog/shared-control fields affect the complete CR4 PHY instance rather than a single lane.

## Dependencies

This chunk depends on the AMD ASIC register-generation pipeline remaining synchronized with the DPCS 4.2.2 hardware specification. It is normally consumed together with:

- `dpcs_4_2_2_offset.h`, which supplies the `ixDPCSSYS_CR4_RAWAONLANE*_*` and `ixDPCSSYS_CR4_SUPX_*` register addresses for the field groups described here.
- AMDGPU display/DC register access helpers that combine address, mask, and shift constants for indexed DPCS CR MMIO operations.
- Display link training, PHY power management, receiver adaptation, DCC calibration, signal-detect, shared PLL/refclk setup, RTUNE, and low-level hardware bring-up code in the AMD GPU driver.

The file is part of an imported Linux GPU driver tree under this repository and has no direct dependency on Ceph filesystem logic.

## Integration Points

The definitions integrate with AMD display PHY initialization and runtime link management for the CR4 instance. Raw lane 3 and raw lane X content is lane-oriented, while `SUPX_DIG` and `SUPX_ANA` content is shared across the CR4 PHY. Correct integration requires pairing each mask with the matching lane or shared register address. A raw lane 3 field must not be applied to raw lane X or lane 2 addresses unless the caller is intentionally using the generic lane-X template with the matching address mapping. Similarly, `SUPX` fields should be treated as shared controls and not as per-lane-only state.

ASIC-version specificity matters: these layouts are for `dpcs_4_2_2` and should not be mixed with neighboring DPCS versions without explicit hardware gating. The MPLLA/MPLLB mirrored groups are structurally similar, but they control separate PLL instances; copy-paste use must keep the A/B prefix aligned with the corresponding address and link clock source.

## Risks

- The range starts in the middle of `DPCSSYS_CR4_RAWAONLANE2_DIG_RX_SIGDET_FILT_CTRL`; the preceding chunk is required for that register's first shift definitions.
- The range ends in the middle of `DPCSSYS_CR4_SUPX_DIG_RTUNE_CONFIG`; the following chunk is required for that register's remaining masks and subsequent RTUNE fields.
- Generated mask/shift mistakes would compile cleanly but can silently program the wrong PHY bit.
- Shared `SUPX` fields can affect reference clocks, bandgap, PLLs, RTUNE, and PHY reset behavior across more than one lane. Incorrect writes can produce broad link-training failures, blank display, unstable HDMI/DP clocking, or failed recovery after suspend/resume.
- Override fields usually have separate value and enable bits. Setting values without enables may do nothing; leaving enables asserted after debug or validation can block normal ASIC control.
- MPLLA/MPLLB and raw lane 3/lane X groups are repetitive. Applying an A-side mask to a B-side address, or a lane-template mask to the wrong lane address, is an easy integration error.
- Reserved fields must be preserved. Accidentally writing reserved bits in these 16-bit DPCS CR registers can change undocumented analog or clock behavior.
- RTUNE, charge-pump, SSC, fractional-N, bandgap, and MPLL timer fields are timing and analog quality sensitive; incorrect values may only fail at high link rates, with specific monitors, or after thermal/voltage changes.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`.
- Static checks that each field has a matching `__SHIFT` and `_MASK`, masks match their shifts and widths, and DPCS CR fields stay within the expected 16-bit register shape unless hardware documentation says otherwise.
- Display bring-up on hardware using DPCS 4.2.2, including boot display, hotplug, modesets, suspend/resume, GPU reset recovery, and multi-monitor operation.
- Link-training stress across lane counts and link rates, with attention to CR4 lane 3/lane-X RX adaptation, DFE/slicer/phase, signal-detect, TX/RX override, DCC calibration, and firmware-configuration paths.
- Clocking validation for both MPLLA and MPLLB, including divider and HDMI-clock paths, SSC, fractional-N settings, charge-pump settings, MPLL power FSM transitions, lock status polling, and PCLK power timing.
- PHY diagnostics that exercise RTUNE request/ack, prescaler clock detect, bandgap and reference power-up timing, analog ATB/power-measurement selections, signal-detect output override/readback, calibration-code readback, and reserved-bit-preserving read-modify-write behavior.

### subset-b-002379: lines 100132-102491

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 100132-102491

## Work Item

- Chunk id: `subset-b-002379`
- Source path: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h`
- Line range: 100132-102491
- Scope note: this is a chunk of a very large generated AMD DPCS ASIC register mask header. The chunk begins in the tail of `DPCSSYS_CR4_SUPX_DIG_RTUNE_CONFIG` mask definitions, starts its first complete register block at `DPCSSYS_CR4_SUPX_DIG_RTUNE_STAT`, and ends at the first `__SHIFT` field for `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3`.

## Purpose

This chunk defines C preprocessor constants for DPCS 4.2.2 CR4 supervisor and per-lane register bitfields. The constants provide the bit shift and mask values used by AMDGPU display/link code to read, write, compose, and decode packed hardware register fields without embedding literal bit positions throughout driver code.

The visible register families cover:

- Supervisor digital RTUNE controls and status, including RX/TX termination calibration status and set values.
- Supervisor digital-to-analog overrides for MPLLA/MPLLB, analog RTUNE, bandgap/reference controls, and PMIX controls.
- Lane digital ASIC override and ASIC input/output observation blocks for TX, RX, EQ, CDR/VCO, lane state, and OCLA.
- Lane TX power control, DCC DAC programming, clock alignment, and LBERT controls.
- Lane RX power control, VCO calibration, CDR/DPLL controls, adaptation control/status, match/stat counters, and LBERT controls.
- Lane digital analog-bridge override/status blocks that drive TX/RX analog controls from the digital register interface.
- Lane analog TX and RX control blocks for measurement, ATB routing, DCC, termination, clocks, CDR/deserializer, slicer, power, squelch, calibration, and register-reference controls.

## Important APIs, Types, and Functions

There are no functions, structs, enums, or runtime APIs in this range. The exported surface is a set of `#define` macros whose names follow the generated AMD register field convention:

- `DPCSSYS_CR4_<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit index.
- `DPCSSYS_CR4_<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register position.
- Register block comments of the form `//DPCSSYS_CR4_<REGISTER>` group the related field macros.

The chunk contains 2,139 `#define` lines, split almost exactly into 1,069 `__SHIFT` definitions and 1,070 `_MASK` definitions. The one-count imbalance is caused by the line-range boundary ending after `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3__meas_atb_cdr_vco_gd__SHIFT` before the corresponding mask definitions in the following chunk.

Key complete or nearly complete groups in this range include:

- `DPCSSYS_CR4_SUPX_DIG_RTUNE_*`: termination tuning status and RX/TX set/stat values, timing counters, and TX calibration code.
- `DPCSSYS_CR4_SUPX_DIG_ANA_MPLLA_*` and `DPCSSYS_CR4_SUPX_DIG_ANA_MPLLB_*`: override outputs for MPLL clock enables, output enables, analog enable, reset, calibration, dividers, feedback clock, gearshift, standby, integer and charge-pump fields.
- `DPCSSYS_CR4_LANEX_DIG_ASIC_*`: digital override input registers and ASIC-observed input/output registers for lane, TX, RX, RX EQ, and RX CDR/VCO paths.
- `DPCSSYS_CR4_LANEX_DIG_TX_PWRCTL_*`: TX P-state fields, reset/enable delay counters, DCC DAC bank address/data/control/range/select/ack/address fields.
- `DPCSSYS_CR4_LANEX_DIG_RX_PWRCTL_*`: RX P-state fields and RX power-up timing.
- `DPCSSYS_CR4_LANEX_DIG_RX_VCOCAL_*`: VCO calibration mode, configuration, timing, and status fields.
- `DPCSSYS_CR4_LANEX_DIG_RX_CDR_*` and `DPCSSYS_CR4_LANEX_DIG_RX_DPLL_*`: CDR control/status and DPLL frequency/bounds fields.
- `DPCSSYS_CR4_LANEX_DIG_RX_ADPTCTL_*`: adaptation configuration fields, reset fields, and status readback for ATT, VGA, CTLE, DFE taps, slicer offsets, DAC control selection, and CR bank addressing.
- `DPCSSYS_CR4_LANEX_DIG_RX_STAT_*`: programmable match/stat collection fields, counters, sample count, stop, and calibration compare clock control.
- `DPCSSYS_CR4_LANEX_DIG_ANA_*`: digital-side override outputs toward analog TX/RX/MPHY/sigdet/DCC/term-code controls plus analog status readback.
- `DPCSSYS_CR4_LANEX_ANA_TX_*`: analog-side TX measurement, power override, alternate bus, ATB routing, DCC DAC/control, termination code/control, clock override, and miscellaneous/reserved fields.
- `DPCSSYS_CR4_LANEX_ANA_RX_*`: analog-side RX clock, CDR/deserializer, slicer, power, squelch, calibration, ATB/register-reference, and measurement fields.

## Control Flow

This header has no executable control flow. Runtime control flow appears in consumers that include this header and combine masks/shifts with register access helpers. A typical consumer pattern is:

1. Read a hardware register through the AMDGPU display register access layer.
2. Extract a field with `value & FIELD_MASK`, then shift by `FIELD__SHIFT`.
3. Compose an updated field by shifting a value by `FIELD__SHIFT`, masking it with `FIELD_MASK`, and OR-ing it into a register update.
4. Write the updated register back through the MMIO/register abstraction.

The control semantics represented by the field names are hardware state-machine controls rather than C branches. Examples include P-state selection, RX/TX power-up timers, VCO calibration start/done/status fields, adaptation enables and windows, override-enable bits, reset bits, and LBERT enable/error fields.

## State and Persistence Behavior

The macros are compile-time constants and do not store software state. They map to persistent hardware register state in the DPCS block while the GPU/display hardware is powered. The most important state categories visible in this chunk are:

- Calibration and tuning state: RTUNE set/stat values, TX calibration code, RX VCO calibration controls/status, and DCC DAC controls.
- Power/link state: TX/RX P-state fields, lane power-up timing fields, MPHY RX controls, and analog enable/override fields.
- Clocking and CDR state: MPLLA/MPLLB enables, RX CDR controls, DPLL frequency/bounds, VCO override fields, and IQ phase adjustment fields.
- Adaptation state: ATT/VGA/CTLE/DFE adaptation configuration and status fields, slicer offsets, and error slicer level.
- Diagnostic and measurement state: LBERT controls/errors, OCLA fields, stat match/counter registers, ATB measurement selection, and analog status readbacks.

Because this is hardware state, persistence depends on GPU reset, display engine reset, power-gating, link training, and firmware or driver reprogramming sequences. The header itself does not document reset values or access permissions, so consumers must rely on register offset headers, hardware programming guides, and driver sequencing.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor and the broader generated AMD ASIC register-header ecosystem. It is expected to be included alongside companion DPCS headers that define register offsets, base indices, and possibly default values.

Integration points include:

- AMDGPU display core and DCN link training code that configures DisplayPort/PHY/DPCS lanes.
- Register accessor macros/helpers that use `_MASK` and `__SHIFT` names to set or read fields.
- Diagnostic paths that expose or inspect LBERT, OCLA, stat counters, CDR/VCO status, adaptation status, or ATB measurement selection.
- Generated ASIC-specific include selection for DPCS 4.2.2, where matching the correct generation-specific mask header to the correct register-offset header is required.

The field naming suggests integration with serializer/deserializer, PLL, CDR, DFE/adaptation, MPHY, and analog measurement logic in the display PHY. No Linux kernel APIs are directly invoked in this chunk.

## Risks and Edge Cases

- Boundary risk: this chunk is partial at both ends. The preceding chunk owns the earlier `DPCSSYS_CR4_SUPX_DIG_RTUNE_CONFIG` shift lines, while the following chunk owns most of `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3`. Merge logic must not treat this chunk alone as a complete register map.
- Generated-header drift: a wrong mask or shift silently corrupts hardware programming. Errors can cause failed link training, unstable displays, bad calibration, or hangs in low-level display initialization.
- Reserved and `NC` fields are numerous. Consumers should preserve reserved bits on read-modify-write unless hardware documentation explicitly permits writing them.
- Override fields are high risk because they bypass automatic hardware/firmware control. Incorrect `*_OVRD_EN`, reset, clock enable, or power bits can leave the lane analog path disabled, stuck in reset, or driven with invalid calibration values.
- Many fields are narrow packed values, often 1 to 10 bits inside 16-bit masks. Consumer code must validate value widths before shifting to avoid truncation or reserved-bit writes.
- Read-only status fields and writeable control fields are mixed in the same header naming style. The masks do not encode access direction, volatility, reset value, or side effects.
- Field spelling reflects generated hardware names, including lower-case field fragments and names such as `tresh`. Renaming for style would break consumers and generated consistency.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- The kernel tree should compile with this header included by AMDGPU display code; duplicate or malformed macro names would normally surface as preprocessor/build failures.
- Static checks can verify each complete register block has paired `__SHIFT` and `_MASK` macros for each field. The expected exception in this chunk is the partial `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3` block at the end.
- Mask/shift consistency can be checked mechanically by confirming each mask's least-significant set bit matches its corresponding shift and that masks do not overlap unexpectedly within a register unless the hardware definition intentionally aliases fields.
- Runtime display validation should cover DP/USB-C link bring-up, link training across rates/lanes, hotplug, suspend/resume, GPU reset, and displays requiring RX/TX calibration or CDR adaptation paths.
- Diagnostic validation should include LBERT/OCLA/stat-counter paths and analog measurement/ATB paths if the platform exposes them.

## Open Questions for Later Merge

- The complete per-file report should correlate these masks with the companion address header for DPCS 4.2.2 to identify the actual register offsets for each block.
- Access semantics, reset values, and sequencing constraints are not visible in this mask header and must be inferred from consumers or hardware documentation.
- The next chunk is needed to complete `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3` and continue into raw memory/raw lane definitions that begin immediately after this range.

### subset-b-002380: lines 102492-103633

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 102492-103633

## Scope And Purpose

This chunk covers the tail of AMDGPU's generated DPCS 4.2.2 shift/mask header. It is hardware register metadata, not executable logic: every `*_SHIFT` macro names a bit position and every `*_MASK` macro names the corresponding bit mask for fields in DPCS, raw lane, FSM, IRQ, PMA, TX/RX control, ATE, and RDPCSPIPE registers.

The covered range begins in the lane analog RX ATB measurement definitions, then moves through raw common memory data registers and a dense block of `DPCSSYS_CR4_RAWLANEX_DIG_*` register fields. The largest portion describes raw lane PCS/PMA TX and RX override inputs, PCS-visible inputs/outputs, adaptation controls, equalizer and termination controls, finite-state-machine status and fast-calibration flags, IRQ status/clear/mask fields, and TX/RX control helper registers. The chunk ends with a hand-annotated RDPCSPIPE PHY control exception for two RDPCSPIPE instances and the file's closing `#endif`.

This header is paired with `dpcs_4_2_2_offset.h`, which gives the register addresses such as `ixDPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN` at `0xe000`, `ixDPCSSYS_CR4_RAWLANEX_DIG_FSM_FAST_FLAGS` at `0xe038`, `ixDPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN_2` at `0xe0c8`, and `regRDPCSPIPE0_RDPCSPIPE_PHY_CNTL6` / `regRDPCSPIPE1_RDPCSPIPE_PHY_CNTL6`. The macros in this chunk let display and PHY code compose field writes and decode field reads without hard-coding bit arithmetic at each call site.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime APIs in this slice. The effective API is the generated macro namespace consumed by AMD display register helpers such as `REG_GET`, `REG_UPDATE`, `FN`, `SF`, and `LE_SF`-style register-field tables.

The macro naming convention is consistent:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit.
- `REGISTER__FIELD_MASK` gives the unshifted field mask in the register word.
- `RESERVED_*`, `NC*`, and `RESERVED_REG_*` macros document reserved or unused regions that callers should preserve unless a hardware sequence explicitly says otherwise.

Key register families in this chunk include:

- Analog/test fields: `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3`, `MEAS4`, `ATB_FRC`, and `RX_RESERVED1` cover ATB measurement selection, calibration reference forcing, and reserved lane analog bits.
- Raw memory windows: `DPCSSYS_CR4_RAWMEM_DIG_ROM_CMN0_B0_R0` and `DPCSSYS_CR4_RAWMEM_DIG_RAM_CMN0_B0_R0` expose 16-bit `DATA` fields for common ROM/RAM access.
- Raw PCS TX controls: `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN`, `_IN_1`, `_IN_2`, `TX_PCS_IN`, `TX_OVRD_OUT`, and `TX_PCS_OUT` describe TX reset/request, power state, low-power disable, width, rate, MPLL selection/enables, master MPLL override, async data/enables, detect-RX request, vboost, iboost, beacon, loopback, data enable, ACK, and detection-result fields.
- Raw PCS RX controls: `RX_OVRD_IN`, `_IN_1` through `_IN_3`, `RX_PCS_IN` through `_IN_4`, `RX_OVRD_OUT`, `RX_PCS_OUT`, `RX_OVRD_OUT_1`, and `RX_OVRD_OUT_2` describe rate/width/pstate/lpd overrides, adaptation AFE/DFE controls, loopback, RX data enable, LOS threshold and LFPS overrides, VCO/ref load overrides, equalizer values, reset/request/ACK, clock enable, and RX-valid override.
- Adaptation and equalization status: `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, `RX_TXPOST_DIR`, `RX_EQ_DELTA_IQ_OVRD_IN`, `RX_EQ_OVRD_IN_1`, `RX_EQ_OVRD_IN_2`, and `RX_PH2_CAL` expose adaptation handshakes, figure of merit, direction hints, EQ/CTLE/DFE override values, and phase-2 calibration request/ack bits.
- ATE and loop controls: `PCS_XF_ATE_OVRD_IN`, `PCS_XF_ATE_RX_OVRD_IN*`, `PCS_XF_ATE_TX_OVRD_IN*`, and `PCS_XF_MASTER_MPLL_LOOP` provide manufacturing/test override equivalents for normal RX/TX paths plus MPLLA/MPLLB loop enables.
- Raw FSM controls/status: `FSM_FSM_OVRD_CTL`, `FSM_MEM_ADDR_MON`, `FSM_STATUS_MON`, many `FSM_FAST_*` bits, `FSM_FAST_FLAGS`, `FSM_CR_LOCK`, `FSM_TX_DCC_FLAGS`, `FSM_TX_DCC_STATUS`, `FSM_OCLA`, `FSM_TX_EQ_UPDATE_FLAG`, `FSM_CMNCAL_*_STATUS`, and `FSM_RX_IQ_PHASE_OFFSET` expose state-machine jump/command/debug controls, fast calibration/adaptation bypasses, common calibration state, lock controls, and observability controls.
- IRQ controls: `IRQ_CTL_*` registers define RX/TX reset/request/rate/pstate/adaptation/phase-calibration/loopback/DCC interrupt status, clear, and mask fields. Most individual status and clear registers are one-bit flags with upper bits reserved; `IRQ_MASK` and `IRQ_MASK_2` aggregate mask bits.
- Raw PMA controls: `PMA_XF_LANE_*`, `SUP_*`, `TX_*`, `RX_*`, `MPHY_*`, `RX_ADAPT_OVRD_OUT`, and `LANE_RTUNE_CTL` fields cover MPLL lane enables, override enables, PMA-visible TX/RX reset/request/data/clock controls, superblock controls, RTUNE, and MPHY override handoff.
- TX/RX control helper registers: `TX_CTL_TX_FSM_CTL`, `TX_CTL_TX_CLK_CTL`, `TX_CTL_TX_DCC_CONT_STATUS`, `TX_CTL_OCLA`, `TX_CTL_UPCS_OCLA`, `RX_CTL_RX_FSM_CTL`, `RX_CTL_RX_LOS_MASK_CTL`, `RX_CTL_RX_DATA_EN_OVRD_CTL`, `RX_CTL_OFFCAN_CONT_STATUS`, `RX_CTL_ADAPT_CONT_STATUS`, and `RX_CTL_UPCS_OCLA` expose coarse FSM, clock, data-enable, LOS, continuous calibration/adaptation, and OCLA debug controls.
- RDPCSPIPE tail: `RDPCSPIPE0_RDPCSPIPE_PHY_CNTL6` and `RDPCSPIPE1_RDPCSPIPE_PHY_CNTL6` define `RDPCS_PHY_DPALT_DP4`, `RDPCS_PHY_DPALT_DISABLE`, and `RDPCS_PHY_DPALT_DISABLE_ACK` fields at bits 16-18.

The RDPCSPIPE fields are visibly integrated by `drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`, where `DPCS_DCN31_MASK_SH_LIST(mask_sh)` includes `LE_SF(RDPCSPIPE0_RDPCSPIPE_PHY_CNTL6, RDPCS_PHY_DPALT_DP4, mask_sh)`, `RDPCS_PHY_DPALT_DISABLE`, and `RDPCS_PHY_DPALT_DISABLE_ACK`.

## Control Flow And Runtime Use

This file has no runtime control flow. Its only control behavior is preprocessor expansion during compilation.

Typical use is indirect:

1. A DCN/DPCS implementation includes the relevant offset and shift/mask headers for the ASIC generation.
2. Register-list macros bind register addresses from `dpcs_4_2_2_offset.h` with field masks and shifts from this header.
3. Register helper macros turn a symbolic field access into masked read/modify/write operations, using the `*_MASK` and `*_SHIFT` constants to place or extract values.
4. The hardware register write or read is performed through AMD display's register access layer.

For the raw `DPCSSYS_CR4_RAWLANEX_DIG_*` register families, the likely runtime sequences are low-level PHY bring-up, link training, manufacturing test, diagnostics, and recovery flows that force or observe TX/RX requests, power state, width/rate, MPLL state, PMA/PCS handshakes, adaptation, calibration, interrupts, and loopback. The chunk itself does not enforce the ordering of those sequences; it only exposes the bit layout used by the implementation code and firmware-facing paths.

The RDPCSPIPE tail is more directly connected to DisplayPort alternate-mode handling. The DCN31 link encoder field list includes these mask/shift definitions so code can set `RDPCS_PHY_DPALT_DISABLE`, detect `RDPCS_PHY_DPALT_DISABLE_ACK`, and mark `RDPCS_PHY_DPALT_DP4` when controlling DP alternate-mode PHY behavior.

## State And Persistence Behavior

The macros do not allocate memory, store state, perform I/O, or persist anything by themselves. Their state impact occurs only when consumers use them to access memory-mapped hardware registers.

Hardware state affected through these fields is persistent at the register level until overwritten, reset, power-gated, or changed by the PHY microcontroller/state machines. In particular, override-enable fields can force TX/RX reset, request, data-enable, loopback, MPLL, termination, equalizer, adaptation, and PMA handoff values away from autonomous hardware control. IRQ clear fields are write-sensitive hardware controls: writing the wrong bit can acknowledge an interrupt event rather than merely update software bookkeeping.

Most masks in this slice are 16-bit hardware-field masks expressed as 32-bit-looking constants with an `L` suffix, often `0x0000....L`. Consumers should still treat them as register-field masks rather than generic 32-bit software flags. Reserved masks define bits that should generally be preserved across read/modify/write cycles.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header convention. Address macros come from `dpcs_4_2_2_offset.h`, while this file supplies field placement. The display code's register helper layer supplies the functions and macros that actually combine addresses, masks, shifts, and values.

Important integration points include:

- AMD Display Core register helper infrastructure under `drivers/gpu/drm/amd/display/dc/inc/reg_helper.h`, which defines the common `REG_GET*` and `REG_UPDATE*` style operations used throughout DC.
- ASIC-specific register lists and field lists in display modules, especially DCN/DPCS link encoder code. The observed DCN31 link encoder uses the RDPCSPIPE fields from this chunk through `DPCS_DCN31_MASK_SH_LIST`.
- Matching DPCS generations, such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h`, which carry similar field definitions. Differences in literal formatting and availability between generations are compatibility signals, not cleanup opportunities.
- Hardware/firmware link-training, PHY, ATE, and diagnostics paths that need raw lane PCS/PMA control or observation.

The final per-file report should reconcile this tail with earlier chunks of the same header because some register families begin before line 102492 and this slice starts mid-register at `DPCSSYS_CR4_LANEX_ANA_RX_ATB_MEAS3`.

## Risks And Edge Cases

Generated shift/mask headers are hardware ABI. A one-bit error in a mask or shift can redirect a write to another hardware field, leaving display link training, PHY power sequencing, calibration, interrupts, or DP alternate-mode handling broken in ways that may be ASIC-, board-, or monitor-specific.

Reserved fields are a particular risk. Many registers include high-bit reserved masks such as `RESERVED_15_1`, `RESERVED_15_2`, `RESERVED_15_6`, or `RESERVED_15_8`. Register writes should use helpers that preserve unrelated fields unless the hardware programming guide explicitly requires a full-register write.

Override-enable fields are operationally dangerous if left asserted. The chunk exposes many `*_OVRD_EN`, `*_OVRD_VAL`, ATE override, and PMA/PCS override controls. A debug or recovery path that enables one of these bits and fails to restore autonomous control can pin reset/request/data-enable, force an unsupported rate/width/pstate, disrupt calibration, or hide a real PHY handshake failure.

Interrupt clear registers are easy to misuse because they are represented as ordinary field masks. `IRQ_CTL_*_CLR` writes should be audited for write-one-to-clear semantics and for avoiding accidental clears of concurrent hardware events.

The RDPCSPIPE block contains an explicit source comment: `TODO: verify this still applies to DCN315` and `Hack. RDPCSPIPE only has 2 instances.` The adjacent offset header also aliases `regRDPCSPIPE2_RDPCSPIPE_PHY_CNTL6` to the same address as instance 0. Any future ASIC or DCN315-related work should verify instance count, address aliasing, and field validity before copying these definitions into new generation headers.

This chunk also differs from nearby generation headers in literal formatting. For example, DPCS 4.2.3 contains equivalent-looking field masks with shorter 16-bit-style literals such as `0x0003L`, while this 4.2.2 header often uses `0x00000003L`. That difference should not be normalized manually unless the generator or style contract is intentionally changed.

Because the raw-lane register space spans many subsystems, normal display hotplug testing may not exercise ATE, OCLA, IRQ clear, FSM override, PMA handoff, and fast-calibration fields. Regressions can survive compile and basic boot tests unless validation includes targeted PHY/debug flows.

## Test Signals

Build validation should compile every DCN/DPCS configuration that includes `dpcs_4_2_2_sh_mask.h` and related offset headers. A broken macro name, missing field, or duplicate conflicting definition should surface as compile failures in register-list users.

Static consistency checks should compare every field's mask against its shift and expected width. For one-bit fields, `MASK == 1 << SHIFT`; for multi-bit fields, the contiguous mask width should match the field's documented range. These checks are especially valuable for dense registers such as `PCS_XF_TX_OVRD_IN`, `PCS_XF_RX_PCS_IN`, `FSM_STATUS_MON`, `FSM_FAST_FLAGS`, `IRQ_CTL_IRQ_MASK`, and ATE override registers.

Header-pair validation should verify that every register in this chunk has a matching address macro in `dpcs_4_2_2_offset.h` when it is an indexed `DPCSSYS_CR4_*` register, and that RDPCSPIPE fields match the available `regRDPCSPIPE*_RDPCSPIPE_PHY_CNTL6` address macros.

Hardware or simulator tests should exercise link bring-up, DP alternate-mode disable/ack handling, lane rate/width/pstate changes, reset/request handshakes, MPLL selection, RX adaptation, LOS threshold behavior, TX/RX data enable, loopback controls, and IRQ mask/status/clear flows on the relevant ASIC generation.

Debug and manufacturing test coverage should include ATE override paths, OCLA enable fields, FSM override/status observation, PMA override handoff, and continuous adaptation/calibration status. These fields are less likely to be covered by normal display modeset tests but are prominent in this chunk.

Regression tests should include read/modify/write preservation of reserved bits and paired enable/value behavior for override controls. For DPALT-specific behavior, tests should confirm that setting `RDPCS_PHY_DPALT_DISABLE` produces the expected `RDPCS_PHY_DPALT_DISABLE_ACK` transition on the intended RDPCSPIPE instance and does not accidentally target an aliased or nonexistent pipe.
