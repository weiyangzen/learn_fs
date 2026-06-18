# sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_mode.c

## Purpose
`et8ek8_mode.c` is a static mode-table companion for the Toshiba/Nokia ET8EK8 sensor driver. It does not implement I2C, V4L2, or PM logic directly; instead it exports `meta_reglist`, a versioned list of `struct et8ek8_reglist` objects consumed by the main ET8EK8 driver to program power-on and streaming modes.

## Important APIs, Types, and Data
- Includes only `et8ek8_reg.h`; all public contracts come from that header.
- Defines nine `static struct et8ek8_reglist` mode objects, one of which has type `ET8EK8_REGLIST_POWERON` and the rest `ET8EK8_REGLIST_MODE`.
- Each reglist embeds `struct et8ek8_mode` metadata: physical sensor dimensions, crop/window dimensions, output frame geometry, pixel clock, frame interval, maximum exposure, media-bus format, and 16.16 sensitivity.
- Register sequences are `struct et8ek8_reg` flexible arrays terminated by `{ ET8EK8_REG_TERM, 0, 0 }`.
- The exported `struct et8ek8_meta_reglist meta_reglist` has version `"V14 03-June-2008"` and a NULL-terminated pointer table in mode order.

## Control Flow
There is no executable control flow in this file beyond static initialization. Runtime flow is data-driven: the ET8EK8 driver selects a `meta_reglist.reglist[i].ptr`, inspects its `type` and `mode`, then iterates `regs` until `ET8EK8_REG_TERM`. The first list is a power-on/full-resolution setup with additional analog/CCP2/ISP initialization, while subsequent lists adjust timing, scaling/binning, bus format, and frame rate.

## State and Persistence
All state is immutable kernel data after module load. Persistence is limited to the compiled-in mode table. The table stores sensor timing assumptions such as SPCK/CCP2/VCO, HCOUNT/VCOUNT, divisors, maximum exposure, and output bus format. There is no dynamic allocation, locking, or per-device state here.

## Dependencies and Integration Points
- Depends on Linux media bus format constants via the header include path.
- Consumed by the ET8EK8 sensor driver through the external `meta_reglist` symbol.
- Register type constants (`ET8EK8_REG_8BIT`, `ET8EK8_REG_TERM`) and list type constants come from `et8ek8_reg.h`.
- Integration risk is mainly ABI-like: the order and metadata in `meta_reglist` must match the driver's selection and enumeration expectations.

## Risks
- Register values are opaque vendor tuning values; accidental edits can break PLL, CCP2/LVDS output, frame timing, exposure limits, or image quality.
- Some comments and values disagree slightly, for example denominator naming around 13.12 fps, so reviewers should validate effective timing rather than trusting comments alone.
- The flexible-array mode objects are static and non-const, which permits accidental writes by driver code even though the intended data is read-only.
- Any missing `ET8EK8_REG_TERM` would make the consumer walk past the register array.
- Mode metadata must stay consistent with register programming; mismatched width, height, pixel clock, or bus format can cause bad V4L2 negotiation.

## Test Signals
- Build/link should confirm `meta_reglist` resolves and `et8ek8_reg.h` contracts match the main driver.
- Runtime probe/stream tests should exercise each advertised mode, verify frame size and bus code negotiation, and check no register-list walk errors.
- Sensor capture should confirm frame interval, exposure limits, and compressed vs uncompressed bus formats for DPCM modes.
- Regression checks should compare the version and pointer ordering when changing tables.
