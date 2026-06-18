# sources/distributed-fs/ceph-client/drivers/hid/hid-led.c

## Purpose

`hid-led.c` is a simple USB HID RGB LED driver for several notification-light devices. It registers red, green, and blue LED class devices for each supported RGB unit and translates LED brightness changes into each device's HID feature or output report protocol.

## Important APIs, Types, and Functions

- `struct hidled_config`: per-device protocol configuration: type, names, max brightness, RGB unit count, report size/type, optional init callback, and write callback.
- `struct hidled_device`, `struct hidled_rgb`, and `struct hidled_led`: runtime topology for HID device, RGB units, and individual LED class devices.
- `hidled_send(...)`: serialized report sender using either `hid_hw_raw_request(... SET_REPORT)` or `hid_hw_output_report`.
- `hidled_recv(...)`: RAW_REQUEST-only helper that sends a command and reads a feature report response.
- Device protocol callbacks: `riso_kagaku_write`, `dream_cheeky_init/write`, `thingm_init/write`, `delcom_init/write`, and `luxafor_write`.
- `hidled_init_led(...)` / `hidled_init_rgb(...)`: register LED class devices with stable names and `LED_HW_PLUGGABLE`.
- `hidled_probe(...)`: parses HID, selects config from `driver_data`, runs protocol init, starts HIDRAW, gets the hidraw minor for LED names, allocates RGB state, and registers LEDs.
- `hidled_table`: maps Riso Kagaku, Dream Cheeky, ThingM blink(1), Delcom Visual Indicator, and Luxafor USB IDs to config types.

## Control Flow

Probe allocates `hidled_device` and a DMA-safe-ish report buffer, parses the HID descriptor, chooses a protocol config, optionally performs an init/readback check, allocates one `hidled_rgb` per RGB unit, and starts HID with `HID_CONNECT_HIDRAW`. It then registers red/green/blue LED class devices for each unit. When userspace changes any color LED brightness, the device-specific write callback reads the sibling color brightnesses, builds the protocol packet, and calls `hidled_send` under a mutex.

## State and Persistence Behavior

Runtime state is devres-managed and lives for the HID device lifetime: selected config, HID pointer, shared buffer, mutex, RGB array, LED names, and LED class brightness values. Device firmware state changes persist in the USB device until overwritten or reset. `thingm_init` can swap the config to a v1 variant based on firmware version readback.

## Dependencies and Integration Points

The driver integrates HID core, HIDRAW, LED class, mutexes, and device IDs. It exposes standard LED class devices rather than input events. It uses a module parameter, `riso_kagaku_switch_green_blue`, to adapt devices with swapped green/blue wiring.

## Risks and Edge Cases

- Protocol packets are hand-coded and device-specific; report size mismatches return `-EMSGSIZE`.
- `hidled_send` uses caller stack buffers as sources but copies into `ldev->buf` before HID I/O because raw requests require a separate buffer.
- `hidled_recv` is only valid for RAW_REQUEST configs and performs a SET_REPORT before GET_REPORT.
- Delcom devices share VID/PID; the init readback rejects non-family-2 devices.
- LED names include hidraw minor, so names can change across replug.
- Brightness writes for one component send all three current component values; concurrent LED writes are serialized but userspace may observe intermediate colors.

## Test Signals

Hardware tests should verify LED class device creation, RGB writes for each supported protocol, ThingM v1 detection, Delcom family rejection, Luxafor multi-unit naming, and Riso green/blue module-parameter behavior. Fault tests should cover short HID writes, unsupported report types, unregister during brightness writes, and probe failure cleanup after partial LED registration.
