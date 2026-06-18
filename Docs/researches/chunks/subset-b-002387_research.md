# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 2387-4746

## Scope

This chunk is a generated AMDGPU DPCS/DCIO register field mask header slice. It contains only C preprocessor constants: every visible API is a `#define` ending in `__SHIFT` or `_MASK`, with register-section comments and `addressBlock` comments used as structure. There are no functions, structs, enums, storage objects, or executable control flow in this range.

The chunk starts in the middle of `RDPCSTX3_RDPCSTX_CLOCK_CNTL` and continues through:

- The rest of the `RDPCSTX3` transmitter-3 field map.
- The complete `dpcssys_dpcs0_rdpcstx4_dispdec` `RDPCSTX4` transmitter-4 field map.
- Two small `RDPCSPIPE0`/`RDPCSPIPE1` DPALT pipe control maps.
- DCIO global, UNIPHY link/channel crossbar, reset, pinstrap, intercept, genlock/swaplock, GPIO, DDC, HPD, AUX/I2C pad, and power-good field maps.
- The beginning of `dpcssys_dcio_dcio_uniphy1_dispdec`, ending at the `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED8` register comment.

## Purpose

The purpose of these definitions is to give AMD display driver code stable symbolic names for bit positions and masks in DPCS 4.2.3 display PHY/DCIO registers. Driver code can combine these macros with register addresses from the matching `dpcs_4_2_3_offset.h` header and lower-level MMIO helpers to compose, read, modify, and decode 32-bit register values without hard-coding numeric bit positions at each call site.

The prefix naming convention encodes the hardware register and field:

- `RDPCSTX3_*` and `RDPCSTX4_*` target repeated RDPCS transmitter instances.
- `RDPCSPIPE0_*` and `RDPCSPIPE1_*` target pipe-level DP alternate-mode controls.
- `DC_*`, `DCIO_*`, `UNIPHY*`, and `DC_GPIO_*` target shared display I/O, pin, pad, and PHY routing registers.
- Each field has a `__SHIFT` constant for the starting bit and a `_MASK` constant for the field width and position.

## Important Definitions

The `RDPCSTX3` tail covers transmitter clocking, interrupts, PLL-update data/address/data control-register windows, SRAM power control, scratch/spare registers, CR conversion FIFO status, DMCU/DPALT access controls, debug selection, PHY reset/power/link controls, fuse-derived tuning fields, RX lock-detect values, byte-order changes, and PLL update override fields.

The `RDPCSTX4` block mirrors the transmitter-3 shape for another physical transmitter instance. Its key register groups are:

- `RDPCSTX4_RDPCSTX_CNTL`: soft resets, lane bit order/packing, interrupt mask, PLL update request/pending, FIFO lane enables, FIFO start/delay, CR/non-DPALT register block enables, DPALT block status, and TX soft reset.
- `RDPCSTX4_RDPCSTX_CLOCK_CNTL`: external reference clock, per-lane TX clocks, TX/SRAM/OCLA clock gates/enables/status bits, and PHY alternate reference clock enable.
- `RDPCSTX4_RDPCSTX_INTERRUPT_CONTROL`: FIFO overflow/error flags, DPALT disable/4-lane toggle flags, clear bits, and masks for those interrupt sources.
- `RDPCSTX4_RDPCS_TX_CR_ADDR` and `RDPCSTX4_RDPCS_TX_CR_DATA`: 16-bit CR address/data windows.
- `RDPCSTX4_RDPCSTX_PHY_CNTL0` through `PHY_CNTL17`: PHY reset, test/powerdown, HDMI mode, reference range/clock detect, power-gating state, lane loopback, per-lane reset/disable/ready/data/request/ack handshakes, termination/inversion/equalization controls, lane rate/width/detect-RX bits, lane power states, MPLL enable, DPALT state, fractional-N/SSC PLL parameters, reset selectors, link numbers, lane select, reserved/test fields, voltage regulator bypass, generic debug buses, and OCLA debug source selection.
- `RDPCSTX4_RDPCSTX_PHY_FUSE0` through `PHY_FUSE3`: fuse fields for per-lane EQ main/pre/post values and PLL/DCO/voltage tuning parameters.
- `RDPCSTX4_RDPCSTX_DMCU_DPALT_PHY_CNTL3` and `PHY_CNTL6`: DMCU-reserved mirrors of lane handshake and DPALT/power-state controls.
- `RDPCSTX4_RDPCSTX_DPALT_CONTROL_REG`: driver access allowance/block status and spare bits for DPALT coordination.
- `RDPCSTX4_RDPCS_CNTL3`: per-lane byte-order-change fields.
- `RDPCSTX4_RDPCS_TX_PLL_UPDATE_ADDR_OVRRD` and `DATA_OVRRD`: PLL update override address and data fields.

The pipe-level definitions are narrow:

- `RDPCSPIPE0_RDPCSPIPE_PHY_CNTL6` and `RDPCSPIPE1_RDPCSPIPE_PHY_CNTL6` expose only `RDPCS_PHY_DPALT_DP4`, `RDPCS_PHY_DPALT_DISABLE`, and `RDPCS_PHY_DPALT_DISABLE_ACK`.

The DCIO/global definitions include:

- `DC_GENERICA`/`DC_GENERICB`: generic output enable/source and UNIPHY PLL clock source selections.
- `DCIO_CLOCK_CNTL` and `DC_REF_CLK_CNTL`: test clock, DCIO clock gating, HSYNC, and genlock clock output selection.
- `UNIPHYA` through `UNIPHYE` link and channel crossbar controls: channel inversion and xbar source fields for four channels per UNIPHY.
- `DC_PINSTRAPS`, `INTERCEPT_STATE`, `DCIO_BL_PWM_FRAME_START_DISP_SEL`, `DCIO_GSL_GENLK_PAD_CNTL`, `DCIO_GSL_SWAPLOCK_PAD_CNTL`, and `DCIO_SOFT_RESET`: strap decode, intercept status, PWM frame-start routing, genlock/swaplock pad routing, and resets for UNIPHY/DSYNC/PWRSEQ blocks.

The DC GPIO chip definitions cover:

- Generic GPIO A-G mask, output, enable, and readback registers.
- DDC1-DDC5 and DDCVGA mask/output/enable/readback registers for SCL/SDA pads.
- GENLK, swaplock, HPD, and power-sequencer pad masks/enables/readbacks.
- Pad strength controls, AUX receive select, TX12 enable, GPIO RX enable, and pull-up enable.
- AUX control registers `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`, including slew/spike rejection, bias/resistor selection, comparator selection, HPD pad tuning, AUX termination/swap/hysteresis, per-AUX control nibbles, AUX VOD tuning, DDC I2C mode, 1.2V power enable, and DDC pad I2C control bits.
- `AUXI2C_PAD_ALL_PWR_OK`: one power-good bit per AUX/I2C PHY 1-6.

The final visible block begins `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED7` and the comment for `RESERVED8`. These expose full-width `UNIPHY_MACRO_CNTL_RESERVED` fields as `0xFFFFFFFFL` masks and are likely placeholders for reserved or macro-specific control storage.

## Control Flow

There is no runtime control flow in this chunk. The only ordering is declarative:

1. Register comments identify a register.
2. `__SHIFT` macros define each field's least-significant bit.
3. `_MASK` macros define each field's positioned bitmask.
4. Consumers use the two constants together to build field values, usually through helper macros or explicit `(value << SHIFT) & MASK` style operations.

The hardware sequencing implied by the names is handled elsewhere. For example, `*_REQ`/`*_ACK`, `*_CLR`, `*_PENDING`, `*_CLOCK_ON`, and `*_PWR_STABLE` fields suggest request/acknowledge and status polling protocols, but this header does not implement those protocols.

## State And Persistence

The macros are compile-time constants and do not persist state. The persistent state they describe lives in GPU/display hardware registers and is accessed through MMIO by the AMDGPU display stack. Some fields describe stateful hardware latches or status bits, including:

- FIFO error/overflow and DPALT toggle interrupt bits plus corresponding clear bits.
- PLL update request and pending bits.
- PHY clock-ready, request/acknowledge, power-stable, reference-clock-detect, RX detect, and lock-detect fields.
- Intercept-state bits for power sequencers and DPCS instances.
- GPIO readback (`*_Y`/`*_RECV`) and AUX/I2C power-good fields.

Reset, power, and pad-control fields can alter hardware state across display link bring-up, mode changes, suspend/resume, hotplug, and DP alternate-mode transitions until overwritten by driver code or reset by hardware.

## Dependencies

This chunk depends on the rest of the generated AMD register header family:

- The matching offset header, especially `dpcs_4_2_3_offset.h`, supplies register addresses such as `regRDPCSTX4_RDPCSTX_PHY_CNTL3`, `regDC_GPIO_AUX_CTRL_5`, and `regAUXI2C_PAD_ALL_PWR_OK`.
- Other ASIC generations' headers contain similar names and masks, which are useful for comparing generated layout drift but must not be mixed with this ASIC version.
- AMDGPU display code supplies register access helpers, include plumbing, ASIC revision selection, and higher-level sequencing. This header is not useful without those consumers.

The constants also rely on standard C preprocessor behavior and 32-bit register arithmetic. The `L` suffix makes these long integer constants; consumers should avoid signed-width surprises by using the established AMD register helper macros and unsigned register types.

## Integration Points

Expected integration points are AMD display link and DCIO code paths that program:

- DPCS transmitter lane resets, FIFOs, byte packing/order, PLL update paths, and CR address/data windows.
- PHY power, lane mode/rate/width, loopback, term/inversion/equalization, MPLL/SSC/fractional-N configuration, and debug bus routing.
- DP alternate-mode arbitration between driver and DMCU/firmware-controlled fields.
- UNIPHY channel routing/inversion and DCIO soft resets.
- GPIO, DDC, HPD, AUX, genlock, swaplock, and power-sequencer pads.

Because this is a `dpcs_4_2_3` ASIC header, integration must pair it with the same version's offsets and with code paths selected for that hardware generation. The `RDPCSTX3`/`RDPCSTX4` repetition also means generic transmitter code may select instance-specific macro families through preprocessor tables or generated register lists elsewhere.

## Risks

- A wrong mask or shift silently corrupts MMIO programming. This can manifest as failed display link training, broken hotplug, bad DDC/AUX communication, incorrect lane mapping, unstable PLLs, missed interrupts, or hardware blocks stuck in reset/powerdown.
- The chunk begins and ends mid-register context. Any merge-level research must join it with adjacent chunks to avoid losing the first `RDPCSTX3_RDPCSTX_CLOCK_CNTL` field and the continuation of `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED8`.
- Repeated transmitter blocks are highly similar. Copy/paste or generator drift between `RDPCSTX3` and `RDPCSTX4` is easy to miss; version-to-version comparisons should be deliberate.
- Fields named `RESERVED`, `SPARE`, `DMCU_DPALT_*_RESERVED`, and full-width `UNIPHY_MACRO_CNTL_RESERVED` are especially risky to program outside known sequences because they may be undocumented, firmware-owned, or silicon-revision-specific.
- Some field names imply handshakes (`REQ`/`ACK`, `PENDING`, `CLOCK_ON`, `PWR_STABLE`). Driver code must preserve required ordering and polling timeouts; these masks alone do not encode sequencing constraints.
- GPIO/AUX/DDC/HPD pad controls interact with physical connector behavior. Incorrect pull-up, I2C mode, termination, voltage, or swap settings can break monitor detection and sideband communication.

## Test Signals

Good validation signals for consumers of this chunk include:

- Compile coverage for the ASIC-generation include path that uses `dpcs_4_2_3_sh_mask.h` with `dpcs_4_2_3_offset.h`.
- Static checks that every referenced field macro exists and that field writes are masked and shifted through common register helpers.
- Display smoke tests on DPCS 4.2.3 hardware: boot display, hotplug, suspend/resume, mode set, multi-monitor, link retraining, DP/HDMI paths, and MST or DP alternate-mode scenarios where applicable.
- AUX/DDC/HPD tests: EDID reads, HPD interrupt detection, DDC retry behavior, AUX transaction reliability, and connector power-good checks.
- Link-training diagnostics around PLL update, lane request/acknowledge, clock-ready, power-stable, RX detect, and error interrupt fields.
- Register-dump comparison against known-good firmware/driver traces for `RDPCSTX3`, `RDPCSTX4`, DCIO soft reset, UNIPHY xbar, and GPIO/AUX control registers.

## Open Questions For Merge

- Which adjacent chunk contains the beginning of `RDPCSTX3_RDPCSTX_CLOCK_CNTL`, and does it describe the missing `RDPCS_EXT_REFCLK_EN` shift before line 2387?
- Which later chunk finishes the `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED8` and subsequent UNIPHY1 reserved register series?
- Which runtime AMD display modules include this generated header for DPCS 4.2.3, and do they use all of the exposed `RDPCSTX4`/DCIO GPIO/AUX fields or only a generated subset?
