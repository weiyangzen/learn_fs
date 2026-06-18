# sources/distributed-fs/ceph-client/drivers/media/i2c/rdacm20.c

## Purpose
`rdacm20.c` is a V4L2 sub-device driver for the IMI RDACM20 GMSL camera module, which combines an OmniVision OV10635 sensor with a Maxim MAX9271 serializer. It initializes the serializer, resets and readdresses the remote sensor, writes a large OV10635 configuration table, exposes a fixed 1280x800 UYVY 16-bit parallel-style media bus format, and toggles the GMSL serial link for streaming.

## Important APIs, types, and functions
- `struct rdacm20_device` stores the parent device, embedded `struct max9271_device`, dummy I2C client for the remote OV10635, V4L2 subdev, media pad, pixel-rate control handler, and two firmware-provided addresses.
- `ov10635_regs_wizard` is the large static initialization sequence for sensor timing, ISP, FIFO, embedded MCU/configuration blocks, FSIN, and output behavior.
- `ov10635_read16()`, `__ov10635_write()`, `ov10635_write()`, and `ov10635_set_regs()` implement 16-bit sensor register access through the remote I2C path.
- `rdacm20_initialize()` is the core hardware bring-up sequence for MAX9271 and OV10635.
- `rdacm20_s_stream()` maps stream enable/disable directly to `max9271_set_serial_link()`.
- `rdacm20_get_fmt()` exposes fixed width, height, UYVY8_1X16 code, RAW colorspace, 601 encoding, full range, and no transfer function.
- `rdacm20_probe()`, `rdacm20_remove()`, and `rdacm20_shutdown()` manage dummy client lifetime, subdev registration, and shutdown stream-off.

## Control flow
Probe reads a two-entry `reg` firmware property for serializer and translated sensor addresses, creates a dummy OV10635 client at the default address, initializes hardware, creates the V4L2 subdev and fixed pixel-rate control, initializes the media source pad, and registers the async subdev.

Initialization wakes the serializer, disables the serial link while no valid pixel clock exists, configures MAX9271 reverse-channel I2C timing, asserts the remote sensor reset via serializer GPIO, configures the GMSL link, verifies serializer ID, changes serializer address, releases sensor reset, retries OV10635 ID reads, changes the sensor I2C address, writes the large sensor register table, logs identification, and raises the serializer reverse-channel threshold.

Streaming does not touch the sensor mode; it only enables or disables the MAX9271 serial link. Shutdown explicitly disables the serial link to avoid transmitting during reset/reboot.

## State and persistence behavior
The driver stores only fixed module state and rewritten I2C addresses. The OV10635 configuration is programmed once during probe; there is no runtime PM, mode switching, or cached format state. If the remote module loses power after probe, the driver has no automatic reinitialization path except reprobe. The serial link state is delegated to `max9271_set_serial_link()`.

## Dependencies and integration points
The driver depends on I2C, firmware properties, V4L2 async subdev/media/control APIs, and the local `max9271.h` serializer helper API. It binds to OF compatible `imi,rdacm20`. It creates an extra dummy I2C client for the remote OV10635 and depends on the serializer's I2C translation/reverse channel being configured before sensor access.

## Risks and edge cases
- The sensor register table is very large, opaque, and includes MCU/configuration writes; partial failure leaves hardware in unknown state.
- Probe-time-only initialization means power glitches or deserializer resets after probe are not recovered.
- The `reg` firmware property must contain exactly the expected two addresses; incorrect values break address reassignment or translation.
- `__ov10635_write()` contains duplicated debug logging, harmless but noisy at high debug levels.
- The fixed format uses `V4L2_COLORSPACE_RAW` with UYVY/YCBCR metadata, which may be surprising to consumers.
- TODO comments flag possible conflicts with embedded MCU startup and reverse-channel threshold assumptions.

## Test signals
Validation signals include successful MAX9271 ID verification, OV10635 ID `0xa635` after retries, successful sensor address change, completion of the full register table, fixed format enumeration, pixel-rate control at 44 MHz, stream enable/disable toggling the serial link, and shutdown forcing stream off.
