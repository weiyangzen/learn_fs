# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_hdmi.h

## Purpose
`sun4i_hdmi.h` is the shared register map and state/API contract for the original Allwinner HDMI controller driver. It defines video timing, pad, PLL, packet, DDC/I2C, CEC, and variant-specific register-field metadata used by HDMI encoder, I2C, DDC clock, and TMDS clock code.

## Important APIs, Types, and Functions
- Register macros for HDMI control, IRQ, HPD, video timing and polarity, AVI infoframes, pad/PLL control, packet control, DDC controller/FIFO/clock, and A31-specific DDC variants.
- `enum sun4i_hdmi_pkt_type`: packet selector values.
- `struct sun4i_hdmi_variant`: SoC-specific flags, initial pad/PLL values, DDC clock formula parameters, TMDS divider offset, regmap fields for I2C/DDC, FIFO behavior, and reset/parent-clock capabilities.
- `struct sun4i_hdmi`: persistent HDMI device state with DRM connector/encoder, MMIO/regmap, reset, clocks, I2C adapters, regmap fields, master driver pointer, CEC adapter, and variant pointer.
- Helper declarations: `sun4i_ddc_create`, `sun4i_tmds_create`, and `sun4i_hdmi_i2c_create`.

## Control Flow, State, and Persistence
The header has no executable flow but defines the persistent state shared across HDMI submodules. Variant data controls which register fields are allocated and how the DDC/TMDS helper clocks are created.

## Dependencies and Integration Points
It depends on DRM connector/encoder, Linux regmap, and CEC pin APIs. It integrates HDMI encoder, DDC clock, I2C transfer, TMDS clock, and master display-engine code.

## Risks and Test Signals
Risks include SoC variant field mismatch, DDC FIFO threshold semantics, clock formula differences between sun4i/sun6i, and broad mutable state shared by several compilation units. Tests should cover each supported HDMI variant, DDC read/write paths, HPD/IRQ behavior, CEC enablement, timing register programming, and TMDS/DDC clock creation.
