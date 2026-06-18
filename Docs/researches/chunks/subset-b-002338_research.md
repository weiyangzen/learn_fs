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
