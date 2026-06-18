# sources/distributed-fs/ceph-client/drivers/media/i2c/rdacm21.c

## Purpose
`rdacm21.c` is a V4L2 sub-device driver for the IMI RDACM21 GMSL camera module, built around a MAX9271 serializer, an OV490 ISP, and an OV10640 sensor. It configures the serializer, maps the OV490 over remote I2C, powers and checks the OV10640 through OV490 SCCB proxy registers, applies OV490 firmware/workaround registers, reads the active ISP output size, and exposes a fixed YUYV8_1X16 source format.

## Important APIs, types, and functions
- `struct rdacm21_device` contains the parent device, MAX9271 serializer, dummy OV490 I2C client, V4L2 subdev, media pad, current frame format, pixel-rate control handler, address pair, and cached OV490 page.
- `ov490_regs_wizard` is the static OV490 configuration sequence for DVP, embedded lines, PCLK workaround, FSIN timing, OV10640 FSIN/HFLIP behavior, and host commands.
- `ov490_read()`, `ov490_write()`, `ov490_set_page()`, `ov490_read_reg()`, and `ov490_write_reg()` implement paged 32-bit OV490 register access through 16-bit page registers plus 16-bit offsets.
- `ov10640_power_up()` controls OV490 GPIO registers to power and reset the OV10640.
- `ov10640_check_id()` uses OV490 SCCB slave proxy registers and host command triggering to read the OV10640 ID.
- `ov490_initialize()` validates the OV490 ID, waits for firmware output enable, checks OV10640 ID, writes OV490 configuration, reads firmware-provided output dimensions, and sets DVP bus width/order.
- `rdacm21_initialize()` sequences MAX9271 setup, address translation, reset release, OV490 initialization, and reverse-channel threshold configuration.
- `rdacm21_s_stream()` enables/disables the MAX9271 serial link.

## Control flow
Probe reads the two-address `reg` property, creates a dummy OV490 I2C client at the default address, initializes the module, sets up the subdev and fixed pixel-rate control, initializes the source pad, and registers the async subdev.

Module initialization wakes MAX9271, disables the serial link, configures reverse-channel I2C, verifies serializer ID, holds OV490 in reset via serializer GPIO, configures GMSL, readdresses the serializer, installs I2C translation for the OV490, releases OV490 reset, and runs OV490 initialization. OV490 initialization powers the OV10640 via OV490 GPIOs, retries OV490 ID reads until firmware exits reset, waits up to 300 ms for frame output enable, checks OV10640 communication through SCCB proxy registers, writes the OV490 wizard table with inter-write delays, reads output width/height from ISP registers, and sets DVP control.

Streaming only gates the MAX9271 serial link after the ISP is expected to provide a valid pixel clock. Format get/set both return the current fixed format derived from the OV490 firmware.

## State and persistence behavior
`last_page` caches the selected OV490 high/low page to avoid redundant page writes. `fmt.width` and `fmt.height` persist the output size read from OV490 firmware during probe. There is no runtime PM or reinitialization state machine. Hardware setup is one-shot at probe, while stream state is held by the serializer helper.

## Dependencies and integration points
The driver depends on I2C, firmware properties, V4L2 async subdev/media/control APIs, and `max9271.h`. It binds to OF compatible `imi,rdacm21`, creates a dummy client for the remote OV490, and depends on MAX9271 address translation for access to the ISP. It exposes a camera-sensor media entity with a single source pad and a fixed 55 MHz pixel-rate control.

## Risks and edge cases
- `rdacm21_subdev_ops` initializes `.pad` twice; this is harmless duplicate assignment but should be cleaned if the file is touched.
- One-shot probe initialization cannot recover if the remote ISP/sensor or serializer resets later.
- OV490 SCCB proxy handling is explicitly undocumented in comments; register names are arbitrary and fragile.
- Firmware readiness and output dimensions are inferred from OV490 registers, so firmware changes can alter exposed format without driver table changes.
- Large opaque register sequences and fixed delays make failures timing-sensitive.
- Remove unregisters controls and dummy client but does not call `media_entity_cleanup()`, unlike most media entity users.

## Test signals
Useful validation includes MAX9271 verification, successful address translation to the OV490, OV490 ID `0x0490`, firmware output-enable within timeout, OV10640 high ID `0xa6`, completion of OV490 register writes, nonzero width/height read from ISP registers, fixed YUYV8_1X16 format reporting, 55 MHz pixel-rate control, and serial-link toggling on stream start/stop.
