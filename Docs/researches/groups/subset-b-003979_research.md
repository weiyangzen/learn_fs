# subset-b-003979 research

Grouped research for Linux touchscreen drivers under `sources/distributed-fs/ceph-client/drivers/input/touchscreen`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix.c

## Purpose
`goodix.c` is the main I2C input driver for older Goodix GT1x/GT9x touchscreen controllers. It powers the controller, handles GPIO/ACPI reset and interrupt-line sequencing, optionally loads configuration from firmware files, reports multitouch/key/active-pen events, and coordinates suspend/resume with the firmware upload helper in `goodix_fwupload.c`.

## Important APIs, types, and functions
- `struct goodix_chip_id` maps textual controller IDs to `struct goodix_chip_data`, which selects config register address, config length, and 8-bit or 16-bit config checksum routines.
- `goodix_i2c_read()`, `goodix_i2c_write()`, and `goodix_i2c_write_u8()` are exported helpers used by this file and the firmware upload file. They perform raw 16-bit-register Goodix I2C transfers.
- `goodix_ts_read_input_report()` polls `GOODIX_READ_COOR_ADDR` until the ready bit appears, reads the first contact/key footer, fetches extra contacts, and services firmware request IRQs when the status byte is zero on flashless devices.
- `goodix_process_events()` dispatches key events, 8-byte or 9-byte finger reports, and active pen reports. It uses `input_mt_sync_frame()` with `INPUT_MT_DROP_UNUSED` slots.
- `goodix_get_gpio_config()` discovers regulators plus IRQ/reset GPIOs and can synthesize ACPI GPIO mappings or ACPI INTI/INTO method access for x86 tablets with broken firmware descriptions.
- `goodix_read_config()`, `goodix_check_cfg_*()`, `goodix_calc_cfg_checksum_*()`, and `goodix_send_cfg()` read, validate, patch, and write controller configuration blocks.
- `goodix_configure_dev()` allocates and registers the main input device, applies touchscreen properties and DMI quirks, creates the delayed-registration pen input device, and requests IRQ or polling mode.
- `goodix_ts_probe()`, `goodix_ts_remove()`, `goodix_suspend()`, and `goodix_resume()` implement I2C driver lifetime and power management.

## Control flow
Probe checks raw I2C functionality, allocates `goodix_ts_data`, gets `AVDD28`/`VDDIO` regulators and GPIOs, enables power, optionally resets the controller, tests I2C, performs firmware upload if a `firmware-name` property exists, reads the controller ID/version, and selects chip data. If board policy says to load config from disk, it starts `request_firmware_nowait()` and finishes initialization in `goodix_config_cb()`. Otherwise it directly calls `goodix_configure_dev()`.

At runtime the threaded IRQ or polling callback calls `goodix_process_events()` and then clears the coordinate status register. The event path reads the controller packet, reports a special active-pen path when a single touch has the pen flag, releases stale pen or key state as needed, and reports each finger into its MT slot. Suspend waits for asynchronous config loading, frees the IRQ if it needs to drive the INT line, saves backup reference data for flashless firmware, drives INT low, sends `GOODIX_CMD_SCREEN_OFF`, and observes the required wake delay. Resume drives INT high, synchronizes the interrupt pin, verifies the config version, resets and resends config on mismatch, and re-requests the IRQ.

## State and persistence
Runtime state lives in `struct goodix_ts_data`: controller ID/version, config bytes, keymap, touchscreen properties, IRQ flags, GPIO access mode, pen registration state, backup reference buffer, and the firmware-loading completion. Persistent device state is in controller firmware/config registers; config writes and firmware request handling program hardware immediately but are not saved by the kernel. Asynchronous config loading requires `remove()` and suspend to wait on `firmware_loading_complete`.

## Dependencies and integration points
The driver integrates with the I2C core, input/MT, touchscreen property parsing, firmware loader, regulator framework, GPIO descriptors, ACPI GPIO mappings, x86 SOC/DMI quirks, OF/ACPI device matching, and the companion firmware upload helpers declared in `goodix.h`.

## Risks
- ACPI GPIO inference is intentionally heuristic and hardware-specific; wrong mapping can break reset, IRQ locking, or wake sequencing.
- `goodix_config_cb()` ignores the return from `goodix_configure_dev()` after config processing, so probe-time async failures are only visible through logs and missing input registration.
- Active pen input is registered lazily inside the event path; failures are cached and future pen events are dropped.
- IRQ-free suspend uses the same INT pin as output; error recovery must re-request IRQs on all failed sleep-command paths.
- Flashless firmware request handling can trigger firmware re-upload from an IRQ-driven read path, making I2C failures and timing regressions visible as lost events.
- DMI quirks change packet format and coordinate inversion; tests must cover both standard and quirked report layouts.

## Test signals
- Build with `CONFIG_TOUCHSCREEN_GOODIX`, ACPI, OF, DMI, and firmware upload support.
- Probe tests should cover regulator deferral, missing GPIOs, ACPI mapping variants, no-IRQ polling mode, reset retry after failed I2C test, async config loading, and default config fallback.
- Event tests should validate 8-byte and 9-byte packets, contact count bounds, key footer handling, pen down/up, status clearing, and firmware request status-zero handling.
- PM tests should cover screen-off suspend, resume config-version mismatch resend, IRQ-free vs no-pin suspend, and flashless backup-reference save/restore interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix.h -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix.h

## Purpose
`goodix.h` is the shared private interface for the legacy Goodix touchscreen driver and its firmware upload helper. It centralizes register addresses, request codes, controller limits, GPIO access modes, chip configuration callbacks, runtime driver state, and cross-file function prototypes.

## Important APIs, types, and functions
- Register definitions cover reset/upload control registers, firmware signature/main clock locations, request/status/command registers, config data addresses for GT1x and GT9x chips, ID and coordinate registers, and backup-reference storage.
- `enum goodix_irq_pin_access_method` describes how the driver may drive the interrupt pin during reset and PM: no access, normal GPIO, ACPI GPIO with raw semantics, or ACPI INTI/INTO methods.
- `struct goodix_chip_data` is the per-family configuration contract used by `goodix.c`: config base address, config length, config validator, and checksum updater.
- `struct goodix_ts_data` is the shared runtime object for the main driver and firmware upload code. It stores I2C/input devices, regulators, GPIOs, config state, IRQ flags, firmware/config names, controller ID/version, keymap, main clock bytes, and backup-reference memory.
- Exported helper prototypes expose I2C access, config sending, interrupt synchronization, reset-without-INT-sync, firmware checking, firmware request handling, and backup-reference saving.

## Control flow
The header does not execute code, but it defines the contracts that tie `goodix.c` and `goodix_fwupload.c` together. `goodix_ts_probe()` fills the shared structure, calls `goodix_firmware_check()`, and later configures input reporting. The firmware helper uses the same register constants and state object to upload code, answer controller requests, send main-clock data, and preserve backup-reference data.

## State and persistence
The structure layout makes configuration and firmware-upload state persistent for the lifetime of the I2C client. `config[]`, `main_clk[]`, `bak_ref`, `bak_ref_len`, and `firmware_name` are the key fields shared across normal event handling, PM, and flashless-firmware request handling. Hardware state persists only in the controller.

## Dependencies and integration points
The header depends on GPIO descriptor, I2C, input, MT, touchscreen-property, and regulator types. It is intentionally private to the touchscreen driver directory rather than a UAPI header.

## Risks
- Because `struct goodix_ts_data` is shared across two C files, changing field meaning or initialization order can break firmware upload or PM paths without compiler errors.
- Register constants are reused for different controller families; incorrect chip-data selection can send valid-looking writes to the wrong address.
- `GOODIX_CONFIG_MAX_LENGTH`, key counts, and ID length are embedded array bounds and must remain synchronized with parsing code.

## Test signals
- Build both `goodix.c` and `goodix_fwupload.c` after any header changes.
- Static checks should verify all shared fields are initialized before firmware helper use, especially `chip`, `config`, `gpiod_int`, `gpiod_rst`, and `irq_pin_access_method`.
- Firmware-upload and suspend/resume tests are the best behavioral coverage for this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin.h -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin.h

## Purpose
`goodix_berlin.h` is the private interface between the Goodix Berlin common core and its I2C/SPI transport drivers. It defines per-IC register metadata and exports the shared probe, PM operations, and sysfs attribute groups.

## Important APIs, types, and functions
- `GOODIX_BERLIN_FW_VERSION_INFO_ADDR_A/D` and `GOODIX_BERLIN_IC_INFO_ADDR_A/D` define revision-specific firmware-version and IC-info addresses.
- `struct goodix_berlin_ic_data` passes transport/chip metadata into the core: firmware version address, IC-info address, and SPI read dummy/prefix lengths.
- `goodix_berlin_probe()` is the core entry point called by both bus drivers with a `struct device`, IRQ, input ID, regmap, and IC data.
- `goodix_berlin_pm_ops` and `goodix_berlin_groups` are exported from the core for direct use in the I2C and SPI driver structs.

## Control flow
Bus-specific probe creates a regmap and selects a `goodix_berlin_ic_data` table from device match data, then hands control to `goodix_berlin_probe()`. PM and dev_groups in the transport drivers are shared through the declarations in this header.

## State and persistence
The header itself stores no state. Its IC data tables determine which on-chip addresses are read during core probe and how much prefix/dummy data the SPI regmap transport strips from reads.

## Dependencies and integration points
This file depends only on forward declarations plus `<linux/pm.h>`, keeping the bus drivers decoupled from core structure internals. It integrates the core module with `goodix_berlin_i2c.c` and `goodix_berlin_spi.c`.

## Risks
- I2C IC data leaves SPI prefix/dummy lengths zero by design; core code must not assume those fields are valid for all buses.
- Wrong firmware/IC-info addresses in a table make the core reject the device as checksum-invalid or dummy data.
- The exported attribute group includes raw register access; transport drivers inherit that surface automatically.

## Test signals
- Build all three Berlin modules together.
- Probe GT9916 over I2C and GT9897/GT9916 over SPI to validate IC-data table addresses and transport-specific prefix lengths.
- Check that module unload/order resolves exported `goodix_berlin_pm_ops`, `goodix_berlin_groups`, and `goodix_berlin_probe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_core.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_core.c

## Purpose
`goodix_berlin_core.c` is the shared implementation for newer Goodix Berlin touchscreen ICs. It performs regulator/reset power sequencing, device confirmation, firmware and IC-info discovery, multitouch event parsing, request handling, input device setup, PM, and an admin-only raw register sysfs interface.

## Important APIs, types, and functions
- Packed firmware/version, IC-info, header, touch, and event structures model the Berlin firmware protocol.
- `struct goodix_berlin_core` stores device, regmap, regulators, reset GPIO, touchscreen properties, firmware version, input device, IRQ, runtime `touch_data_addr`, selected IC data, and a reusable event buffer.
- `goodix_berlin_checksum_valid()` verifies u16 additive checksums over firmware, IC-info, headers, and touch data.
- `goodix_berlin_power_on()` enables `vddio`, then `avdd`, deasserts reset, confirms the device by writing/readback of `0xaa` at boot option address, and waits for firmware boot. `goodix_berlin_power_off()` reverses the state.
- `goodix_berlin_read_version()` and `goodix_berlin_get_ic_info()` read and validate firmware metadata, reject dummy all-zero/all-ones bus data, and parse the variable IC-info layout to find `touch_data_addr`.
- `goodix_berlin_irq()` reads the event header plus up to two contacts, validates header checksum, dispatches touch/request events, fetches remaining contacts when needed, and clears the status byte.
- `goodix_berlin_input_dev_config()` configures the MT input device with 10 direct slots and touchscreen properties.
- `registers_read()` and `registers_write()` implement an admin read/write binary sysfs file backed by raw regmap accesses.
- `goodix_berlin_probe()` is exported for bus drivers.

## Control flow
The transport driver initializes a regmap and calls `goodix_berlin_probe()`. Core probe requires a positive IRQ, allocates state, gets optional reset GPIO and required `avdd`/`vddio` regulators, powers the device on, registers a devm power-off action, reads version and IC-info, configures input, requests a threaded IRQ, and finally stores driver data.

The IRQ path performs a fixed first read sized for header plus two contacts and checksum. If the status byte is zero it exits. Otherwise it validates the header, handles touch events by completing the contact buffer and validating the touch checksum, handles reset request events by toggling reset when available, clears the status byte, and returns handled. Suspend disables IRQ and powers down; resume powers on and re-enables IRQ.

## State and persistence
Runtime state is devm-managed and persists for the device lifetime. The only parsed firmware state kept after probe is `touch_data_addr` and `fw_version`. The driver does not update firmware/config; it assumes firmware and config are already programmed. Sysfs register writes can mutate arbitrary device state while powered.

## Dependencies and integration points
The core integrates with regmap, input/MT, touchscreen properties, GPIO descriptors, regulators, device property parsing, sysfs binary attributes, PM helpers, and the I2C/SPI transport wrappers. It exports symbols for loadable transport modules.

## Risks
- IC-info parsing walks a variable-width buffer; offset errors can misinterpret `misc` or read beyond validated layout if structure formats change.
- Raw admin register access is powerful and can conflict with IRQ processing or device firmware state.
- The first IRQ read intentionally over-reads for one contact and under-reads for more than two until a second read; checksum placement is subtle and must match protocol.
- Stylus and gesture events are explicitly unsupported; stylus events are warned once and dropped.
- Suspend/resume fully powers the controller but does not reread IC-info, so firmware state must remain compatible after power cycling.

## Test signals
- Build with both Berlin transports and exercise probe on revision A and D devices.
- Validate bad checksum, dummy data, missing IRQ, missing regulators, invalid touch count, invalid slot ID, and unsupported request code paths.
- IRQ tests should cover 0, 1, 2, and more-than-2 contacts, status clearing, reset request handling, and checksum failures.
- PM tests should confirm regulator/reset ordering and event delivery after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_i2c.c

## Purpose
`goodix_berlin_i2c.c` is the I2C transport wrapper for the Goodix Berlin core. It provides a 32-bit-register/8-bit-value regmap over I2C, supplies a BUS_I2C input ID, selects GT9916 IC metadata, and delegates functional behavior to `goodix_berlin_probe()`.

## Important APIs, types, and functions
- `goodix_berlin_i2c_regmap_conf` sets `reg_bits = 32`, `val_bits = 8`, and caps raw read/write transfers at 256 bytes.
- `goodix_berlin_i2c_input_id` sets the input bus type to `BUS_I2C`; vendor/product are intentionally unset.
- `goodix_berlin_i2c_probe()` gets IC data from match data, creates the regmap with `devm_regmap_init_i2c()`, and calls the core probe.
- `gt9916_data` uses revision D firmware-version and IC-info addresses.
- I2C and OF match tables bind `"gt9916"` and `"goodix,gt9916"` to that data.

## Control flow
When an I2C client matches, probe initializes regmap and immediately transfers ownership of device setup to the common Berlin core. The driver struct shares the core PM ops and raw-register dev_groups, so suspend/resume and sysfs behavior are implemented by the core.

## State and persistence
The transport wrapper stores no private state beyond regmap devm resources. All runtime state belongs to `goodix_berlin_core`.

## Dependencies and integration points
This file integrates the I2C subsystem, regmap-I2C, OF/I2C ID matching, input bus IDs, and the exported Berlin core symbols. It depends on a valid IRQ in `client->irq`.

## Risks
- The fixed 256-byte raw transfer cap must be sufficient for core reads such as IC-info chunks and event buffers; future larger reads need transport review.
- Only GT9916 is matched here; other Berlin I2C parts require correct IC-data addresses before adding compatibles.
- Regmap setup assumes the controller accepts 32-bit register addresses over I2C as provided by regmap.

## Test signals
- Build with `CONFIG_TOUCHSCREEN_GOODIX_BERLIN_I2C`.
- Probe a DT node with `goodix,gt9916`, required regulators, reset GPIO, and IRQ.
- Verify core sysfs register reads work through the I2C regmap and that event delivery survives suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_spi.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_spi.c

## Purpose
`goodix_berlin_spi.c` is the SPI transport wrapper for the Goodix Berlin core. It implements custom regmap bus operations that prepend Goodix SPI read/write flags, big-endian 32-bit addresses, and revision-specific dummy bytes before delegating device behavior to the common core.

## Important APIs, types, and functions
- SPI framing constants define read/write flags (`0xf1`/`0xf0`), 4-byte register width, and revision A/D read dummy and prefix lengths.
- `goodix_berlin_spi_read()` allocates one TX/RX buffer, writes read flag plus big-endian address and dummy bytes, performs `spi_sync()`, and copies payload after the configured prefix.
- `goodix_berlin_spi_write()` builds write flag plus address plus payload and performs `spi_sync()`.
- `goodix_berlin_spi_regmap_conf` supplies custom `.read` and `.write` callbacks for a 32-bit-register/8-bit-value regmap.
- `goodix_berlin_spi_probe()` forces SPI mode 0 and 8 bits per word, sizes regmap raw read/write limits from `spi_max_transfer_size()`, initializes regmap, and calls `goodix_berlin_probe()`.
- `gt9897_data` uses revision A addresses and 4 dummy bytes; `gt9916_data` uses revision D addresses and 3 dummy bytes.

## Control flow
SPI device matching selects IC data, probe configures the SPI controller, creates a regmap with transfer-size limits that account for Goodix prefixes, and calls the core. Runtime event and PM paths are core-owned; every core regmap operation routes through the custom SPI framing callbacks.

## State and persistence
The wrapper keeps no persistent private state except the regmap and SPI device configuration. IC-data read prefix/dummy lengths are essential per-device constants used on every read.

## Dependencies and integration points
The file integrates the SPI core, custom regmap accessors, OF/SPI ID matching, the input subsystem through a BUS_SPI ID, and the exported Berlin core PM/groups/probe functions.

## Risks
- `goodix_berlin_spi_write()` computes `len = count - 4`; malformed regmap calls shorter than 4 bytes would underflow, though regmap should honor `reg_bits = 32`.
- `spi_max_transfer_size()` minus prefix length can underflow if a controller reports an unexpectedly tiny maximum.
- Endianness is protocol-specific: regmap stores native u32 at the front of buffers, but the wire address is big-endian.
- Wrong dummy length for a compatible shifts all read data and causes checksum or device-confirm failures.

## Test signals
- Build with `CONFIG_TOUCHSCREEN_GOODIX_BERLIN_SPI`.
- Probe GT9897 and GT9916 compatibles and verify both read-prefix variants.
- Exercise raw register sysfs reads/writes through SPI and touch events with large enough transfer sizes for first and remaining-contact reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_berlin_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_fwupload.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_fwupload.c

## Purpose
`goodix_fwupload.c` supports legacy Goodix controllers without flash by uploading firmware into SRAM, answering firmware runtime requests, sending main-clock/config data, and preserving backup-reference calibration values across suspend where possible.

## Important APIs, types, and functions
- `struct goodix_fw_header` describes the firmware blob header containing hardware info, PID, and VID.
- `goodix_firmware_verify()` checks the exact expected firmware size and verifies separate additive checksums for the main firmware and DSP firmware regions.
- `goodix_enter_upload_mode()` holds the controller cores in reset, powers DSP clocks, disables watchdog/cache, selects SRAM boot, reboots, disables scrambling, and enables code-memory access.
- `goodix_firmware_upload()` requests `goodix/<firmware-name>`, verifies it, resets without INT sync, enters upload mode, writes four main 8 KiB sections across SRAM banks 0/1, writes the 4 KiB DSP section to bank 2, starts firmware, and performs INT sync.
- `goodix_prepare_bak_ref()` sizes and initializes backup-reference data from the current config matrix dimensions.
- `goodix_send_main_clock()` derives a 6-byte checksum-protected clock payload from `goodix,main-clk` or default 54.
- `goodix_firmware_check()` detects the `firmware-name` property and triggers upload during probe.
- `goodix_handle_fw_request()` services controller requests for config, backup reference, reset/reupload, main clock, unknown, and idle states.
- `goodix_save_bak_ref()` reads backup-reference data on suspend when firmware reports valid status.

## Control flow
During probe, `goodix_firmware_check()` returns early for normal flash-backed controllers. If a firmware name is present, it requires an IRQ-pin access method, marks config loading from disk as necessary, and uploads firmware before the main driver reads version/config. After firmware boot, the event path in `goodix.c` may see a zero coordinate status and call `goodix_handle_fw_request()`. That helper reads `GOODIX_REG_REQUEST`, performs the requested side effect, and acknowledges with `GOODIX_RQST_RESPONDED`.

## State and persistence
Uploaded firmware resides in volatile controller SRAM. The driver keeps the selected firmware name, config bytes, main-clock bytes, and backup-reference buffer in `struct goodix_ts_data`. Backup-reference data is initialized to neutral values and refreshed on suspend if available; it is not persisted to the filesystem.

## Dependencies and integration points
The file depends on the firmware loader, I2C helpers and shared state from `goodix.h`, device properties, Goodix reset/INT-sync sequencing, and the main event/PM paths in `goodix.c`.

## Risks
- Firmware upload is timing- and register-sequence-sensitive; partial failures can leave the controller in upload/reset mode.
- Firmware blob verification only checks size and additive checksums, not semantic compatibility with the current panel.
- `goodix_handle_fw_request()` acknowledges even for unknown/idle cases and ignores ack write errors, so request state can diverge silently.
- `goodix_save_bak_ref()` assumes `bak_ref` is allocated before a valid firmware status is seen; request ordering must ensure `goodix_prepare_bak_ref()` ran before reads that need the buffer.
- Main-clock values are truncated into bytes in a loop; unusual `goodix,main-clk` values should be tested.

## Test signals
- Probe a flashless controller with valid, missing, bad-size, and bad-checksum firmware files.
- Exercise request handling for CONFIG, BAK_REF, RESET, MAIN_CLOCK, UNKNOWN, and IDLE.
- Suspend/resume tests should verify backup-reference preservation and firmware reupload after controller reset requests.
- Fault-injection tests should cover I2C failures during bank selection, section writes, firmware start, and request acknowledgement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/goodix_fwupload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/gunze.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/gunze.c

## Purpose
`gunze.c` is a serio driver for Gunze AHL-51S RS232 touchscreens. It receives ASCII packets from the serio line, parses X/Y/touch state, and exposes a simple absolute-position input device.

## Important APIs, types, and functions
- `struct gunze` stores the input device, serio port, packet index, 10-byte packet buffer, and physical path string.
- `gunze_interrupt()` collects bytes until carriage return, then processes the packet and resets the buffer index.
- `gunze_process_packet()` validates packet length, comma delimiter, and leading `T` or `R`, then reports `ABS_X`, inverted `ABS_Y`, and `BTN_TOUCH`.
- `gunze_connect()` allocates state/input, opens the serio port, and registers the input device.
- `gunze_disconnect()` unregisters input, closes serio, clears driver data, and frees state.

## Control flow
The serio core matches `SERIO_RS232` with protocol `SERIO_GUNZE`. On connect, the driver initializes an input device with fixed X/Y ranges 24..1000. Each incoming byte advances packet state; `\r` terminates a packet. Valid packets are converted with `simple_strtoul()` from fixed decimal fields.

## State and persistence
State is limited to the in-progress packet buffer and input device lifetime. There is no hardware configuration or persistent storage.

## Dependencies and integration points
The driver integrates with the serio subsystem and input core, typically through userspace `inputattach` selecting the Gunze protocol.

## Risks
- Packet parsing assumes a fixed 10-byte ASCII layout and uses weak validation; malformed numeric fields can be accepted as zero or partial values.
- Bad packets log with `printk()` and raw packet contents, which can be noisy on an unsynchronized serial line.
- The Y coordinate is hard-coded as `1024 - value`; panel variants with different scaling need userspace calibration.

## Test signals
- Use serio/inputattach with valid `Txxxxx,yyyy` and release packets.
- Fuzz packet lengths, delimiter placement, CR resynchronization, and nonnumeric fields.
- Confirm disconnect during active serial input does not use freed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/gunze.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hampshire.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hampshire.c

## Purpose
`hampshire.c` is a serio driver for Hampshire 4-byte serial touchscreens. It decodes a compact binary packet format into absolute X/Y and touch state input events.

## Important APIs, types, and functions
- Packet macros decode the touch bit and 12-bit X/Y coordinates from four bytes.
- `struct hampshire` stores input device, serio port, current index, 4-byte packet buffer, and physical path.
- `hampshire_interrupt()` accepts bytes only when the first byte has the begin bit and advances packet parsing.
- `hampshire_process_data()` emits `ABS_X`, `ABS_Y`, and `BTN_TOUCH` when a full packet is collected.
- `hampshire_connect()` and `hampshire_disconnect()` implement serio/input lifetime.

## Control flow
The driver binds to `SERIO_HAMPSHIRE`. Connect allocates and registers an RS232 input device with X/Y ranges 0..0x1000. The interrupt callback stores each byte at the current packet index. If byte 0 has `0x80`, packet assembly continues; otherwise the byte is logged as unsynchronized. At four bytes, coordinates and touch state are reported and the index is reset.

## State and persistence
Only packet assembly state persists between interrupts. The driver does not send commands to the device or persist calibration.

## Dependencies and integration points
Integration is through the serio core and input subsystem, with RS232 protocol selection usually provided by userspace attachment.

## Risks
- Resynchronization is minimal: non-begin bytes at index 0 are ignored, but unexpected bytes after a valid begin byte are trusted.
- Coordinate extraction is macro-heavy and sensitive to bit layout; endian-like mistakes would produce plausible but wrong positions.
- No checksum exists, so serial noise can become input events.

## Test signals
- Feed known 4-byte frames and verify exact coordinate/touch decoding.
- Test loss of sync, partial packets, and reconnect/disconnect behavior.
- Validate min/max ranges against real Hampshire hardware calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hampshire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hideep.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hideep.c

## Purpose
`hideep.c` is an I2C touchscreen driver for HiDeep controllers. It powers and resets the controller, reads DWZ product/firmware metadata, reports multitouch/key events, exposes version/product/update sysfs files, and implements in-driver NVM firmware flashing.

## Important APIs, types, and functions
- `struct hideep_ts` stores I2C/regmap/input state, regulators, reset GPIO, mutex, event/programming transfer buffer, keymap, DWZ metadata, firmware size, and NVM mask.
- Program-mode helpers `hideep_pgm_w_mem()`, `hideep_pgm_r_mem()`, `hideep_pgm_w_reg()`, `hideep_pgm_r_reg()`, `hideep_enter_pgm()`, and `hideep_pgm_set()` implement the raw 32-bit programming protocol over I2C.
- NVM helpers `hideep_nvm_unlock()`, `hideep_check_status()`, `hideep_program_page()`, `hideep_program_nvm()`, `hideep_verify_nvm()`, `hideep_flash_firmware()`, and `hideep_update_firmware()` erase, write, verify, and reset flash.
- `hideep_load_dwz()` enters program mode, reads DWZ metadata, sets `fw_size` and `nvm_mask` based on product code, and resets back out.
- `hideep_power_on()`/`hideep_power_off()` control `vdd`, `vid`, reset GPIO or reset command.
- `hideep_irq()` reads the event buffer and `hideep_parse_and_report()` reports up to 10 contacts and up to 3 key events.
- Sysfs callbacks expose `version`, `product_id`, and writable `update_fw`.
- `hideep_probe()` sets up regmap, power, metadata, native protocol mode, input, and IRQ.

## Control flow
Probe requires full I2C functionality and a valid IRQ, allocates state, initializes a 16-bit little-endian regmap, gets regulators/reset GPIO, powers on, registers a devm power-off action, reads DWZ data through program mode, optionally forces native protocol, initializes input axes/keycodes, and requests a threaded IRQ. IRQ reads the fixed 108-byte event block as 16-bit regmap words and parses touch and key counts from the first two bytes.

Firmware update is initiated by writing `update_fw`. The driver requests `hideep_ts_<product_id>.bin`, validates word alignment and maximum size, locks `dev_mutex`, disables IRQ, enters program mode, writes and verifies NVM with retries, resets, and reloads DWZ metadata.

## State and persistence
Hardware firmware in NVM is persistent and can be changed by sysfs. Driver state includes DWZ metadata, derived firmware size/mask, keymap, and runtime event buffer. `dev_mutex` serializes sysfs metadata/update access, and update disables IRQ to avoid event-path interference. Regulator state follows probe/PM.

## Dependencies and integration points
The driver uses I2C, regmap, firmware loader, sysfs attributes, input/MT, touchscreen properties, regulators, GPIO descriptors, ACPI/OF matching, mutex guards, and IRQ disable guards.

## Risks
- The sysfs firmware update path can permanently alter controller NVM; size, product-code, and verify handling are critical.
- `hideep_power_on()` may overwrite an earlier regulator enable error with a later one and can leave `vdd` enabled if enabling `vid` fails before devm cleanup.
- Event parsing indexes keycodes by device-supplied key index; malformed key data beyond configured keys can index uninitialized `key_codes`.
- Program-mode macros ignore some write return values, so failures can cascade before being detected.
- Native-protocol forcing is a kernel-internal property and explicitly not DT ABI.

## Test signals
- Probe tests should cover regulator errors, missing IRQ, reset-GPIO and reset-command paths, DWZ product-code variants, and native-protocol forcing.
- Input tests should cover finger, pen tool type, release flags, key counts, and malformed key indexes.
- Firmware tests should cover missing firmware, unaligned size, oversize image, program/verify mismatch, retry success, and post-update DWZ reload.
- PM tests should verify IRQ disable/power-off and native protocol restore after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hideep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/himax_hx83112b.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/himax_hx83112b.c

## Purpose
`himax_hx83112b.c` is an I2C/regmap driver for Himax HX83112B and HX83100A-family touchscreens. It resets the device, optionally verifies chip ID, reads event stacks, validates event checksums, and reports up to 10 multitouch contacts.

## Important APIs, types, and functions
- `struct himax_chip` provides per-chip product ID checking and event-read method.
- `struct himax_ts_data` stores chip data, reset GPIO, input device, I2C client, regmap, and touchscreen properties.
- `himax_bus_enable_burst()` and `himax_bus_read()` access 32-bit AHB-style addresses through 8-bit regmap command registers.
- `himax_reset()` toggles the reset GPIO with downstream-derived delays.
- `himax_read_product_id()`/`himax_check_product_id()` validate HX83112B IDs.
- `himax_input_register()` configures input slots and abs axes.
- `himax_verify_checksum()` requires the byte sum over the 56-byte event packet to have a zero low byte.
- `himax_handle_input()` reads an event via chip callback and reports it if checksum is valid.

## Control flow
Probe checks I2C functionality, allocates state, gets match data, initializes a little-endian 32-bit-value regmap, gets reset GPIO, resets the controller, checks product ID for chips that require it, registers input, and requests a threaded IRQ. IRQ reads one event packet, validates checksum, reports active points until the advertised count is exhausted, and syncs the MT frame.

## State and persistence
The driver has no firmware/config persistence. State is devm-managed per device. Suspend/resume only disables/enables IRQ; it does not power-cycle or reinitialize the controller.

## Dependencies and integration points
It integrates with I2C, regmap, GPIO descriptors, input/MT, touchscreen properties, OF/I2C matching, and PM helpers.

## Risks
- HX83100A skips product ID validation, so compatible correctness depends entirely on firmware description.
- The event parser treats point index as slot ID rather than a device-supplied ID; this matches the packet layout but should be kept in mind for protocol changes.
- Invalid checksum is logged but not fatal; repeated noise can produce log volume and dropped frames.
- PM does not reset or wake the controller, which may be insufficient on boards that power-gate externally.

## Test signals
- Probe HX83112B with matching and mismatching product IDs, and HX83100A with its alternate event stack address.
- IRQ tests should cover zero points (`0xff`), invalid coordinates, checksum failure, and maximum contacts.
- PM tests should confirm no IRQ delivery during suspend and successful event delivery after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/himax_hx83112b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/himax_hx852x.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/himax_hx852x.c

## Purpose
`himax_hx852x.c` supports Himax HX852x/HX852xES I2C touchscreens. It reads panel configuration from SRAM test mode, powers the controller only while the input device is open, reports multitouch and optional touch keys, and handles runtime PM-style suspend/resume around input open state.

## Important APIs, types, and functions
- `struct hx852x` stores client, input device, touchscreen properties, reset GPIO, two regulators, max finger count, and optional keycodes.
- `hx852x_i2c_read()` performs command-plus-read I2C transfers.
- `hx852x_power_on()`, `hx852x_start()`, `hx852x_stop()`, and `hx852x_power_off()` control regulators, reset, sleep, and sense commands.
- `hx852x_read_config()` powers the device, briefly starts/stops sensing, enters SRAM test mode, reads config, extracts resolution and max finger count, and powers down.
- `hx852x_handle_events()` reads a variable-size report based on `max_fingers`, decodes coordinate/width/touch-info sections, reports active slots, and reports optional key bits.
- `hx852x_input_open()` and `hx852x_input_close()` own power and IRQ enable/disable.
- `hx852x_parse_properties()` reads optional `linux,keycodes`.

## Control flow
Probe verifies required I2C/SMBus capabilities, allocates state and input, obtains `vcca`/`vccd` regulators and reset GPIO, requests the threaded IRQ with `IRQF_NO_AUTOEN`, reads configuration while temporarily powering the chip, configures input axes and keys, initializes MT slots for the reported finger count, and registers input. The device is powered and IRQ-enabled only when userspace opens the input device.

## State and persistence
Driver state is runtime-only. `max_fingers` and resolution are cached from controller SRAM config at probe. Power state follows input open/close and suspend/resume. No firmware or calibration is written.

## Dependencies and integration points
The driver integrates with I2C, SMBus byte/word writes, regulators, GPIO reset, input open/close callbacks, IRQ auto-disable behavior, touchscreen properties, OF matching, and input-device mutexes in PM.

## Risks
- `hx852x_read_config()` depends on entering/leaving test mode correctly; failure cleanup must always restore test mode and power down.
- A diagnostic message for too many keys prints `hx->keycount` before assignment, which can obscure the actual count.
- Event buffer layout depends on 32-bit alignment and `max_fingers`; corrupt config can affect report sizing.
- Suspend only sends stop commands if the input device is enabled and does not disable IRQ separately; correctness depends on open/close IRQ state.

## Test signals
- Probe tests should cover missing capabilities, regulator/GPIO errors, invalid max finger count, and optional keycode parsing.
- Event tests should cover no-touch all-bits-set cases, maximum fingers, key bits, and variable report sizes.
- Open/close and suspend/resume tests should verify regulator, reset, sleep/sense, and IRQ state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/himax_hx852x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hp680_ts_input.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hp680_ts_input.c

## Purpose
`hp680_ts_input.c` is a board-specific touchscreen driver for the HP Jornada 680. It uses SuperH board registers, ADC channels, and a delayed work item to sample a resistive touchscreen after the pen-down IRQ fires.

## Important APIs, types, and functions
- Global `hp680_ts_dev` holds the input device and `DECLARE_DELAYED_WORK(work, do_softint)` defers ADC sampling.
- `hp680_ts_interrupt()` disables the pen IRQ and schedules `do_softint()` after `HZ / 20`.
- `do_softint()` checks pen-down state, drives scan GPIO bits for Y then X measurement, reads `ADC_CHANNEL_TS_Y` and `ADC_CHANNEL_TS_X`, reports touch/coordinates, syncs input, and re-enables the IRQ.
- `hp680_ts_init()` allocates input, sets fixed ABS ranges, requests `HP680_TS_IRQ`, and registers the device.
- `hp680_ts_exit()` frees IRQ, cancels delayed work, and unregisters input.

## Control flow
Module init creates one global input device. The interrupt path does no sampling directly; it masks the IRQ and schedules delayed work. The work function performs the settle delays and ADC reads, then reports either a contact with X/Y or a release and reenables interrupts.

## State and persistence
State is global and module-lifetime only. Hardware state is manipulated through memory-mapped board registers during each sample. There is no persistence.

## Dependencies and integration points
The driver is tightly tied to SuperH HP6xx platform headers, raw I/O, the platform ADC API, the input subsystem, and a board-defined IRQ.

## Risks
- Global state and hard-coded physical addresses make this unsuitable outside the HP680 platform.
- Exit frees the IRQ before canceling delayed work; any already-running work must not race with device unregister.
- IRQ handler passes `NULL` dev_id while work uses global device state, limiting multi-instance support.
- Sampling constants and axis ranges are fixed and hardware-calibration-sensitive.

## Test signals
- Build on the target architecture with HP6xx headers.
- Hardware tests should validate pen-down IRQ, release reporting, ADC channel order, scan GPIO sequencing, and module unload under active touches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hp680_ts_input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/htcpen.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/htcpen.c

## Purpose
`htcpen.c` is an ISA I/O port touchscreen driver for the HTC Shift embedded controller. It is DMI-gated to HTC Shift systems, reads coordinates from fixed EC ports on IRQ 3, and reports a simple absolute touchscreen input device.

## Important APIs, types, and functions
- Module parameters `invert_x` and `invert_y` optionally flip axes.
- `htcpen_interrupt()` reads touch, X, Y, and low-bit registers through indexed I/O ports, reports `BTN_TOUCH`, `ABS_X`, and `ABS_Y`, and clears the IRQ.
- `htcpen_open()`/`htcpen_close()` send EC enable/disable commands and synchronize IRQ on close.
- `htcpen_isa_probe()` claims I/O port regions, allocates input, requests IRQ 3, clears pending IRQ state, registers input, and stores drvdata.
- `htcpen_isa_remove()` unregisters input, frees IRQ, and releases I/O regions.
- `htcpen_isa_init()` checks a DMI table before registering the ISA driver.

## Control flow
Module init refuses to load unless DMI matches the HTC Shift. ISA probe reserves ports `0x068`, `0x06c`, and `0x250-0x251`, creates an input device with 0..2040 axes, and requests the fixed IRQ. The input device open/close hooks enable or disable the EC. Each IRQ reads the current sample, ignores sentinel edge X values, reports contact/position or release, syncs, and clears the IRQ status port.

## State and persistence
Persistent driver state is limited to the input device pointer stored as ISA drvdata and module parameters. The EC enable state changes while the input device is open or during PM suspend/resume.

## Dependencies and integration points
This driver depends on x86-style port I/O, the ISA bus helper, DMI matching, fixed hardware resources, and the input subsystem.

## Risks
- Fixed ports and IRQ are safe only because of DMI gating; widening matching risks conflicts with unrelated hardware.
- I/O port access and coordinate bit assembly are hardware-specific and have no protocol validation.
- Resume unconditionally enables the device even if userspace had not opened it before suspend.
- Module parameters can invert axes but no dynamic calibration is provided.

## Test signals
- Confirm the DMI gate prevents loading on non-HTC Shift systems.
- On hardware, test port reservation conflicts, input open/close, IRQ clear behavior, axis inversion parameters, and suspend/resume enable state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/htcpen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hycon-hy46xx.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hycon-hy46xx.c

## Purpose
`hycon-hy46xx.c` is an I2C/regmap driver for HYCON HY46xx capacitive touch controllers. It reports up to 11 multitouch contacts and exposes controller tuning/status registers through per-attribute sysfs files.

## Important APIs, types, and functions
- `struct hycon_hy46xx_data` stores I2C/input/regmap state, regulator/reset GPIO, mutex, touchscreen properties, and cached tuning/status fields.
- `hycon_hy46xx_check_checksum()` verifies the report checksum using the packet-supplied length.
- `hycon_hy46xx_isr()` reads a 0x44-byte report, validates checksum, decodes 6-byte touch records, and reports active MT slots.
- `struct hycon_hy46xx_attribute` plus `HYCON_ATTR_U8`/`HYCON_ATTR_BOOL` generate sysfs attributes for threshold, glove, report speed, filters, gain, edge offset, versions, and chip IDs.
- `hycon_hy46xx_setting_show()` and `_store()` synchronize cache and hardware register values under a mutex.
- `hycon_hy46xx_get_defaults()` writes optional device-property defaults to hardware.
- `hycon_hy46xx_get_parameters()` reads current hardware settings into the cache.
- `hycon_hy46xx_probe()` powers, resets, initializes regmap/input/sysfs/IRQ, and registers input.

## Control flow
Probe enables the `vcc` regulator with devm cleanup, optionally pulses reset, allocates input, initializes regmap, applies default properties, caches parameters, configures touchscreen properties and 11 MT slots, stores client data, requests IRQ, and registers input. IRQ reads the whole report from register 0, validates checksum, skips reserved touches, uses the top bits as event type, extracts 12-bit X/Y and slot ID, reports non-UP contacts, and syncs.

## State and persistence
Controller tuning writes through sysfs and default properties persist in hardware until reset/power cycle. The driver mirrors each sysfs field in `hycon_hy46xx_data` and warns if hardware reads differ. No firmware state is managed.

## Dependencies and integration points
The driver uses I2C, regmap, regulators, GPIO descriptors, input/MT, touchscreen properties, sysfs device groups, IRQ threading, OF/I2C matching, and asynchronous probe preference.

## Risks
- Default property writes do not enforce the same range limits as sysfs stores.
- Checksum length comes from the packet; malformed lengths can affect validation semantics.
- Sysfs attributes expose mutable controller tuning that can degrade usability without a reset path.
- Input axes are initially configured with max `-1` and rely on touchscreen properties for useful bounds.

## Test signals
- Probe all listed compatibles with and without reset GPIO and default properties.
- IRQ tests should cover checksum failure, reserved/up/down/contact event types, maximum point count, and invalid slot IDs.
- Sysfs tests should cover range enforcement, bool handling, read/cache mismatch warnings, and read-only version/chip attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hycon-hy46xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hynitron-cst816x.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hynitron-cst816x.c

## Purpose
`hynitron-cst816x.c` is a compact I2C driver for Hynitron CST816x-series single-touch controllers with optional gesture key reporting.

## Important APIs, types, and functions
- `struct cst816x_touch` models the 7-byte touch report: gesture, active state, and big-endian packed X/Y.
- `struct cst816x_priv` stores client, optional reset GPIO, input device, gesture keycodes, and keycode count.
- `cst816x_parse_keycodes()` reads optional `linux,keycodes` into a five-entry array.
- `cst816x_i2c_read_register()` performs command-plus-read I2C transfer.
- `cst816x_gest_idx()` maps supported gesture IDs to keycode indexes.
- `cst816x_process_touch()` reads and decodes 12-bit X/Y.
- `cst816x_register_input()` configures ABS_X/ABS_Y, `BTN_TOUCH`, and optional gesture key capabilities.
- `cst816x_irq_cb()` reads one report and emits coordinates, gesture key state, touch state, and sync.

## Control flow
Probe allocates state, gets optional reset GPIO, performs reset if present, parses optional keycodes, registers the input device, and requests a threaded IRQ. Every IRQ reads from register `0x01`, reports raw coordinates on fixed 0..240 axes, optionally reports the mapped gesture key, reports `BTN_TOUCH`, and syncs.

## State and persistence
State is minimal and devm-managed. There is no power, firmware, or configuration persistence. Gesture key mappings persist only for the input device lifetime.

## Dependencies and integration points
The driver integrates with I2C, GPIO reset, input, optional device properties, OF/I2C matching, and threaded IRQs.

## Risks
- If no valid `linux,keycodes` are provided, `keycodemax` remains zero, but IRQ still indexes `priv->keycode[cst816x_gest_idx()]` for any nonzero gesture. A controller gesture without keycodes can therefore report KEY_RESERVED or uninitialized mappings.
- `cst816x_gest_idx()` maps unsupported gestures to the last index; this requires enough configured keycodes to be meaningful.
- Axis limits are hard-coded to 240 rather than parsed from touchscreen properties.
- Probe logs "no gestures found" for any keycode parse error but continues.

## Test signals
- Test with no keycodes, partial keycodes, all supported gestures, and unsupported gesture IDs.
- Validate reset timing, coordinate masking, active-state release reporting, and IRQ behavior on I2C read errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hynitron-cst816x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hynitron_cstxxx.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hynitron_cstxxx.c

## Purpose
`hynitron_cstxxx.c` is an I2C driver for Hynitron CST3xx touchscreens, currently represented by CST340-compatible chip data. It is derived from vendor code without datasheets, validates firmware presence/check code, enters bootloader mode during probe, and reports up to five multitouch contacts.

## Important APIs, types, and functions
- `struct hynitron_ts_chip_data` provides per-chip max touches, firmware check code, and function callbacks for firmware info, bootloader entry, input init, and touch reporting.
- `struct hynitron_ts_data` stores selected chip data, client, input, touchscreen properties, and reset GPIO.
- `hyn_reset_proc()` toggles reset with fixed delays.
- `cst3xx_i2c_write()` retries short raw writes; `cst3xx_i2c_read_register()` reads little-endian 16-bit register addresses.
- `cst3xx_firmware_info()` enters firmware-info mode, validates check code, rejects invalid firmware version, and exits info mode.
- `cst3xx_bootloader_enter()` retries reset plus bootloader command until the bootloader check register returns `0xac`, then resets again.
- `cst3xx_touch_report()` reads and validates the CST3xx touch buffer, sends a finish-read command, parses variable touch layouts, and reports contacts.
- `cst3xx_input_dev_int()` configures the input device, touchscreen properties, defaults, MT slots, and registration.

## Control flow
Probe allocates state, gets OF match data and required reset GPIO, resets, enters bootloader mode, initializes input, verifies firmware info, and requests the threaded IRQ. The IRQ calls the chip-specific report callback. Touch reporting reads the full 28-byte buffer, validates marker bytes, acknowledges completion before parsing, derives touch count, checks the trailing marker for multi-touch reports, parses each 5-byte contact, reports active contacts, and syncs.

## State and persistence
There is no managed firmware update despite bootloader access. Driver state is runtime-only. It verifies firmware presence and chip code during probe but does not store version beyond logs. Hardware reset/bootloader/info commands mutate controller mode transiently.

## Dependencies and integration points
The driver uses I2C raw transfers, GPIO reset, input/MT, touchscreen properties, OF match data, and asynchronous probe preference.

## Risks
- Probe enters bootloader before initializing input and then verifies firmware after input registration; failures can leave a registered input device if devm cleanup is not enough for the exact sequence.
- Protocol constants are inferred from vendor code and comments note missing datasheets, so changes are high-risk.
- Touch count is not clamped before buffer-derived `end_byte`; malformed counts can address beyond meaningful report contents.
- The finger ID sanity check uses `< finger_id`, so an ID equal to `max_touch_num` is not rejected even though slots are zero-based.
- Continuous IRQ behavior while touched can amplify log noise on read/marker failures.

## Test signals
- Probe CST340 hardware through reset, bootloader entry, firmware check-code validation, and invalid firmware version handling.
- Touch tests should cover one, multiple, zero, malformed marker bytes, high touch counts, and boundary finger IDs.
- Regression tests should verify default axis fallback and touchscreen property override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/hynitron_cstxxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ili210x.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ili210x.c

## Purpose
`ili210x.c` is an I2C touchscreen driver for Ilitek ILI210x/ILI2117/ILI2120/ILI251x controllers. It abstracts chip-specific report formats, supports IRQ or polling input, exposes calibration/version/mode sysfs attributes, and implements ILI251x firmware update from Intel HEX firmware.

## Important APIs, types, and functions
- `struct ili2xxx_chip` provides per-chip register read, touch-data read, touch parser, polling continuation policy, max touches, resolution, and feature flags.
- `struct ili210x` stores client/input/reset GPIO, touchscreen properties, chip data, cached firmware/kernel/protocol versions, IC mode, and a `stop` flag.
- Chip parsers handle ILI210x, ILI211x checksumed packets, ILI212x, and ILI251x split touch reports and optional pressure.
- `ili210x_process_events()` reads reports and loops at 15 ms while the chip-specific continuation callback says contact polling should continue.
- Firmware metadata helpers cache resolution, firmware version, kernel version, protocol version, and boot mode for ILI251x.
- `ili210x_calibrate()` writes `REG_CALIBRATE` for capable chips.
- Firmware update helpers parse IHEX to a 64 KiB buffer, switch application/bootloader modes, poll busy, write dataflash and application blocks, verify CRC readback, reset, and refresh cached state.
- `ili210x_i2c_probe()` selects chip data, resets hardware, configures input, sets up IRQ or polling, installs a stop action, and registers input.

## Control flow
Probe resolves chip data from OF or I2C ID, optionally asserts a reset GPIO with devm power-down action, allocates state/input, sets default MT axes, caches firmware metadata if supported, parses touchscreen properties, initializes slots, and chooses interrupt or polling mode. Runtime input processing reads one or more reports, reports each chip's active contacts into stable slots, and repeats if the protocol needs continued polling for contact release.

Firmware update is exposed through `firmware_update` only on ILI251x. The store path requests `ilitek/ili251x.bin` as IHEX, flattens it, disables IRQ if present, hardware resets, switches to bootloader, writes DF and AC areas in 32-byte chunks with busy polling and CRC checks, switches back to application mode, refreshes cached metadata, and resets again.

## State and persistence
Normal touch state is runtime-only. Calibration and firmware update commands mutate controller state; ILI251x firmware writes are persistent. Cached version/mode/resolution fields reflect the last successful metadata refresh. The `stop` flag is a devm cleanup signal for a potentially looping polling/event path.

## Dependencies and integration points
The driver uses I2C, input/MT, touchscreen properties, GPIO reset, firmware and IHEX loaders, CRC-CCITT, sysfs attribute visibility, IRQ or input polling, and OF/I2C matching.

## Risks
- ILI251x firmware update is complex and persistent; mode switching, address ranges, CRC lengths, and reset recovery all need hardware validation.
- `ili251x_read_reg_common()` returns `ret` rather than normalized `error` in one failure path, which can leak positive short-transfer counts.
- The IHEX flattening buffer is not explicitly initialized before sparse records are copied, so gaps depend on allocator contents unless firmware is dense.
- Event polling can loop while contacts remain active; cleanup relies on the `stop` flag.
- Firmware-update sysfs has no input value semantics; any write attempts an update.

## Test signals
- Probe all supported chip IDs with IRQ and no-IRQ polling.
- Report tests should cover each chip parser, ILI211x checksum failures, pressure reporting, release polling, and touchscreen property transforms.
- Sysfs tests should verify attribute visibility by feature flag, calibration input validation, and cached version/mode formatting.
- Firmware tests should cover malformed IHEX, oversize records, sparse records, bootloader switch retries, busy timeout, CRC mismatch, and recovery after failed update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ili210x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ilitek_ts_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ilitek_ts_i2c.c

## Purpose
`ilitek_ts_i2c.c` is an I2C driver for ILITEK 23xx, 25xx, and Lego-series touch ICs using protocol v6-style reports. It initializes protocol metadata, reports multitouch contacts, exposes firmware/product information, and supports basic sleep/wake PM commands.

## Important APIs, types, and functions
- `struct ilitek_ts_data` stores client, reset GPIO, input device, touchscreen properties, protocol callback table/version, product ID, MCU/firmware versions, IC mode, reset timing, screen bounds, and max touch count.
- `struct ilitek_protocol_map` maps logical command indexes to protocol command bytes and handler functions.
- `ilitek_i2c_write_and_read()` implements combined or delayed write/read I2C command transactions.
- `ilitek_process_and_report_v6()` reads 64-byte report packets, fetches additional packets as needed, validates report ID and max-point count, bounds-checks coordinates, and reports active contacts.
- Protocol handlers read protocol, MCU, firmware, screen resolution, touch resolution/max touch, IC mode, sleep, and wake commands.
- `ilitek_protocol_init()` rejects unsupported protocol v3 and older bootloader versions.
- `ilitek_read_tp_info()` populates metadata used by input setup and sysfs.
- `ilitek_input_dev_init()` configures the MT input device from screen bounds and touchscreen properties.
- `ilitek_suspend()`/`ilitek_resume()` disable IRQ and send sleep/wake/reset when the device is not configured as a wake source.

## Control flow
Probe checks I2C functionality, allocates state, gets optional reset GPIO, performs a reset, initializes protocol callbacks/version, reads panel and firmware metadata, registers input, and requests a threaded IRQ. IRQ reads and reports v6 touch data. Sysfs read-only attributes present cached firmware version and product/module strings.

## State and persistence
The driver caches controller metadata at probe. It does not update firmware or persistent configuration. Sleep/wake commands affect controller runtime mode across PM transitions, and reset timing is cached in `reset_time`.

## Dependencies and integration points
The driver integrates with I2C, GPIO reset, input/MT, touchscreen properties, ACPI/OF matching, sysfs groups, wakeup policy, and PM helpers.

## Risks
- `ilitek_i2c_write_and_read()` treats nonnegative short `i2c_transfer()` counts as success; short transfers can lead to stale or incomplete metadata/report data.
- Report buffering assumes a 512-byte stack buffer and 5-byte points; protocol changes or high point counts must remain within bounds.
- If suspend sends sleep and that command fails after IRQ disable, the function returns error without re-enabling IRQ.
- The driver relies on firmware-reported screen bounds and max touch; invalid metadata can prevent input registration or drop touches.

## Test signals
- Probe supported OF/ACPI compatibles and reject unsupported protocol/bootloader versions.
- IRQ tests should cover multi-packet reports, bad report IDs, too-large reported point counts, invalid coordinates, and release frames.
- PM tests should cover wakeup-enabled and wakeup-disabled paths, sleep/wake command failures, and reset after resume.
- Sysfs tests should verify firmware/product formatting from cached probe data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ilitek_ts_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/imagis.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/imagis.c

## Purpose
`imagis.c` is an I2C driver for Imagis IST30xx/IST3038-family capacitive touch controllers. It uses per-compatible register metadata to validate chip identity, report multitouch contacts and optional touch keys, and power the controller only while the input device is open.

## Important APIs, types, and functions
- `struct imagis_properties` describes interrupt-message register, coordinate register, chip-ID register/value, protocol variant, and touch-key support.
- `struct imagis_ts` stores client, properties, input device, touchscreen properties, two regulators, keycodes, and keycode count.
- `imagis_i2c_read_reg()` sends a big-endian 32-bit register address and reads a 32-bit value with up to three retries.
- `imagis_interrupt()` reads the interrupt message, validates finger count, reads per-finger or shared coordinate registers depending on protocol, reports slots, reports optional keys, and syncs.
- `imagis_power_on()`/`imagis_power_off()` bulk-enable/disable `vdd` and `vddio`.
- `imagis_input_open()`/`imagis_input_close()` start/stop power and IRQ.
- `imagis_init_input_dev()` configures input, keycodes, required touchscreen size properties, and MT slots.
- Per-compatible property tables support IST3032C, IST3038, IST3038B, IST3038C, and IST3038H.

## Control flow
Probe allocates state, gets match data, obtains regulators, powers on long enough to read chip ID, installs devm power-off cleanup, verifies identity, requests an IRQ with `IRQF_NO_AUTOEN`, and registers input. Input open powers the controller and enables IRQ; close disables IRQ and powers off. PM stops/starts only if the input device is enabled.

## State and persistence
The driver has no firmware/config persistence. Keycode mappings and compatible-specific register tables are runtime state. Regulator/IRQ state follows input open/close and PM.

## Dependencies and integration points
It uses I2C, OF match data, regulator bulk APIs, input open/close, input/MT, touchscreen properties, optional `linux,keycodes`, IRQ no-auto-enable, and PM with input-device mutex locking.

## Risks
- Probe powers the controller and installs a devm power-off action before input open; the controller may be powered off after probe while the input device exists, as intended, so IRQ auto-enable must remain disabled.
- For protocol variants without separate per-finger registers, repeated reads of the same coordinate register inside the finger loop rely on device-side sequencing.
- Touchscreen size properties are mandatory; missing DT properties fail probe.
- Touch-key default mappings are only applied for key-capable variants when no property is present.

## Test signals
- Probe each compatible with matching and mismatching chip IDs.
- Input tests should cover protocol A/B coordinate reads, maximum finger count rejection, optional/default keycodes, and required touchscreen-size properties.
- Power tests should verify regulator and IRQ state on input open/close and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/imagis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/imx6ul_tsc.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/imx6ul_tsc.c

## Purpose
`imx6ul_tsc.c` is a platform driver for the Freescale/NXP i.MX6UL resistive touchscreen controller and its coupled ADC. It configures ADC calibration/hardware trigger mode, TSC measurement timing, pen-detect GPIO checks, and reports single-touch ABS_X/ABS_Y events.

## Important APIs, types, and functions
- `struct imx6ul_tsc` stores device/input, TSC and ADC MMIO bases, TSC/ADC clocks, XNUR pen-detect GPIO, timing/filter properties, and an ADC calibration completion.
- `imx6ul_adc_init()` configures 12-bit ADC mode, clock source/divider, optional averaging, calibration interrupt, starts calibration, waits for completion, checks failure, and switches ADC to hardware trigger.
- `imx6ul_tsc_channel_config()` programs ADC channels around a documented TSC channel workaround.
- `imx6ul_tsc_set()` writes TSC measurement delay, deglitch, precharge, interrupt enables, and starts sense detection.
- `imx6ul_tsc_disable()` disables TSC and ADC conversion.
- `tsc_wait_detect_mode()` polls the TSC state machine before reading pen-detect GPIO.
- `tsc_irq_fn()` clears TSC status, restarts sense detection, extracts X/Y measurement, decides touch/release using detect mode and XNUR GPIO, and reports input.
- `adc_irq_fn()` completes ADC calibration when conversion complete is signaled.
- `imx6ul_tsc_probe()` maps resources, gets clocks/GPIO/IRQs, reads DT timing properties, configures input, and registers the platform device.

## Control flow
Probe allocates state/input, gets XNUR GPIO, maps TSC and ADC resources, gets clocks, requests TSC and ADC IRQs, reads `measure-delay-time`, `pre-charge-time`, `touchscreen-average-samples`, and `debounce-delay-us`, computes deglitch selection, registers input, and stores drvdata. Input open enables clocks and initializes ADC/TSC; close disables both. The TSC IRQ handles measurements and touch/release reporting. The ADC IRQ is only used to complete calibration during startup.

## State and persistence
State is runtime-only and mostly derived from DT. Hardware registers are reinitialized on input open and resume when the input device is enabled. No calibration persistence is stored by the driver beyond each ADC init cycle.

## Dependencies and integration points
The driver integrates with platform resources, MMIO, clocks, GPIO descriptors, OF properties, threaded TSC IRQ, hard ADC IRQ, completions, input open/close, and PM helpers.

## Risks
- ADC calibration depends on IRQ completion; IRQ ordering or missing ADC interrupt causes open to timeout.
- Debounce conversion depends on TSC clock rate and coarse threshold buckets; board DT values need validation.
- `tsc_wait_detect_mode()` may time out and then treats the contact as active, which can delay release reporting.
- Hardware workaround channel programming is SoC-specific and easy to break when refactoring.
- The driver supports only one host-style resistive touch, not multitouch or pressure reporting.

## Test signals
- Probe with valid and invalid `touchscreen-average-samples`, missing resources, missing clocks, and absent XNUR GPIO.
- Open/close tests should verify clock enable rollback, ADC calibration timeout/failure, and TSC/ADC disable.
- Hardware tests should validate X/Y extraction, release detection, debounce settings, precharge/measure timing, and suspend/resume while input is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/imx6ul_tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/inexio.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/inexio.c

## Purpose
`inexio.c` is a serio driver for iNexio RS232 touchscreens. It decodes 5-byte binary packets into absolute X/Y coordinates and `BTN_TOUCH` state for the Linux input subsystem.

## Important APIs, types, and functions
- Packet macros define begin bit, touch bit, 5-byte packet length, coordinate ranges, and coordinate extraction.
- `struct inexio` stores input device, serio port, packet index, 16-byte buffer, and physical path string.
- `inexio_interrupt()` stores incoming bytes, starts processing only when byte 0 has the response begin bit, and logs unsynchronized bytes.
- `inexio_process_data()` reports X/Y/touch when five bytes have been accumulated and resets the index.
- `inexio_connect()` and `inexio_disconnect()` manage serio and input lifetimes.

## Control flow
The serio core binds `SERIO_RS232` protocol `SERIO_INEXIO`. Connect allocates state/input, sets fixed 0..0x3fff axes, opens the serio port, and registers input. Each byte is appended to the packet buffer; after a valid begin byte and five total bytes, the driver reports the decoded coordinates and touch bit.

## State and persistence
State is limited to packet assembly and the input device. There is no hardware configuration, firmware, or persistent calibration.

## Dependencies and integration points
The driver integrates with serio and input, normally through userspace protocol attachment for serial touchscreens.

## Risks
- The interrupt path does not bound-check `idx` against `INEXIO_MAX_LENGTH` before storing; persistent unsynchronized data after a begin byte could overrun if packet completion logic is disrupted.
- There is no checksum; serial noise after a begin byte becomes input data.
- Coordinate ranges are fixed and may require userspace calibration for a given panel.
- Logging uses raw `printk()` style and can be noisy on bad serial data.

## Test signals
- Feed valid 5-byte frames, release frames, unsynchronized bytes, and partial frames through serio.
- Test repeated invalid streams for index bounds and resynchronization.
- Verify connect/disconnect while data is arriving.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/inexio.c -->
