# Research: subset-b-005551

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/cgbc_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/cgbc_bl.c

## Purpose
This is a platform backlight driver for Congatec Board Controller managed LCD backlights. It exposes the board controller PWM duty cycle as a Linux `backlight_device` with a linear 0-100 brightness range.

## Important APIs, Types, and Functions
`struct cgbc_bl_data` stores the child device, parent `struct cgbc_device_data`, and cached `current_brightness`. `cgbc_bl_read_brightness()` issues `cgbc_command()` command `0x75` and extracts the 7-bit PWM duty field with `FIELD_GET(BLT_PWM_DUTY_MASK, ...)`. `cgbc_bl_update_status()` reads the current controller settings, preserves polarity/frequency bytes, writes a new duty cycle, and verifies the reply. `cgbc_bl_get_brightness()` refreshes hardware state before returning it.

## Control Flow
Probe fetches parent driver data from `pdev->dev.parent`, reads initial brightness, fills `backlight_properties`, and registers `cgbc-backlight` using `devm_backlight_device_register()`. Runtime updates flow from the backlight core into `update_status`; the driver avoids a write if the requested brightness matches the cached value. When a write is needed, it performs a read-modify-write transaction through CGBC firmware and only updates the cache after the controller acknowledges the new duty.

## State and Persistence
The only persistent runtime state is the in-memory cached brightness. Hardware PWM polarity and frequency are not owned by the driver; they are preserved across brightness updates by reading and replaying the existing controller reply bytes. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on `linux/backlight.h`, bitfield helpers, the CGBC MFD API in `linux/mfd/cgbc.h`, and platform-device binding name `cgbc-backlight`. It uses `BL_CORE_SUSPENDRESUME`, so suspend/resume brightness behavior is delegated through normal backlight core calls.

## Risks
The command buffer layout is firmware-contract sensitive: only byte 1 is changed on writes while reply byte 0 is interpreted as the duty field. A controller reply that reports a rounded or constrained duty value is treated as verification failure. Because updates are read-modify-write, concurrent non-driver CGBC PWM changes could be overwritten between read and write.

## Test Signals
Useful tests are probe with valid and failing `cgbc_command()`, initial brightness read, setting 0, 50, and 100, preserving non-duty PWM bits, verification mismatch returning `-EIO`, and suspend/resume update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/cgbc_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/corgi_lcd.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/corgi_lcd.c

## Purpose
This SPI driver controls the LCD timing generator and backlight on Sharp Zaurus Corgi-family handhelds. It registers both an `lcd_device` for panel power and mode switching and a `backlight_device` for brightness.

## Important APIs, Types, and Functions
`struct corgi_lcd` holds the SPI device, LCD/backlight devices, current mode/power/intensity, optional `BL_ON` and `BL_CONT` GPIOs, and a platform battery callback. `corgi_ssp_lcdtg_send()` writes compact register/data values over SPI. `lcdtg_*` helpers bit-bang a write-only pseudo-I2C path through LCD timing generator registers to program common voltage. `corgi_lcd_power_on()` and `corgi_lcd_power_off()` implement the panel sequencing. `corgi_lcd_set_mode()` switches QVGA/VGA. `corgi_bl_update_status()` enforces suspend and low-battery limits before calling `corgi_bl_set_intensity()`. `corgi_lcd_limit_intensity()` is exported for battery policy code.

## Control Flow
Probe requires `struct corgi_lcd_platform_data`, allocates state, registers `corgi_lcd` and `corgi_bl`, obtains optional GPIOs, stores `kick_battery`, powers the LCD on, applies default brightness, then publishes the singleton `the_corgi_lcd`. LCD power transitions only execute when crossing the `POWER_IS_ON()` boundary. Mode changes update phase adjustment and resolution control. Suspend sets `CORGIBL_SUSPENDED`, forces intensity zero, and powers the panel off; resume reverses those steps.

## State and Persistence
State is volatile and partly global. `the_corgi_lcd` and `corgibl_flags` are file-scope globals, while per-device state records current intensity, mode, power, and limit mask. Hardware state is spread across the timing generator, GPIO lines, and the common-voltage DAC. There is no persistent storage.

## Dependencies and Integration Points
The driver depends on SPI, GPIO descriptors, the LCD/backlight core, Corgi platform data, and `sharpsl_param` for `comadj` and phase-adjust defaults. It integrates with external power management via `corgi_lcd_limit_intensity()` and optional `kick_battery()`.

## Risks
The singleton design assumes one device and makes `corgi_lcd_limit_intensity()` unsafe before successful probe. The pseudo-I2C path assumes writes are acknowledged because the bus is write-only. Register sequences are delay-sensitive and platform-data dependent. Brightness encoding mutates values above `0x10`, uses a GPIO for bit 5, and stores the translated intensity rather than the original user-visible value.

## Test Signals
Test probe without platform data, optional GPIO acquisition, QVGA/VGA mode changes, power on/off ordering, low-battery limiting, suspend/resume, exported intensity limiting after probe, and removal forcing brightness zero and panel power off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/corgi_lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/da903x_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/da903x_bl.c

## Purpose
This platform driver exposes DA9030 and DA9034 PMIC WLED outputs as raw Linux backlights. It handles the different brightness ranges and enable mechanisms of the two PMIC variants.

## Important APIs, Types, and Functions
`struct da903x_backlight_data` caches the parent PMIC device, platform ID, and current brightness. `da903x_backlight_set()` is the main hardware path: DA9034 updates `DA9034_WLED_CONTROL1` and toggles `DA9034_WLED_BOOST_EN`, while DA9030 writes trim bits plus charge-pump enable to `DA9030_WLED_CONTROL`. `da903x_backlight_update_status()` forwards `backlight_get_brightness()`, and `get_brightness()` returns the cache.

## Control Flow
Probe validates `pdev->id` against DA9030/DA9034 WLED IDs, selects max brightness, applies optional DA9034 output-current platform data, registers a raw backlight named from `pdev->name`, sets initial brightness to the maximum, and calls `backlight_update_status()`. Runtime updates write brightness first and then enable or disable the relevant boost/charge-pump path based on transitions to or from zero.

## State and Persistence
Only `current_brightness` is tracked in memory. Hardware register state persists in the PMIC until overwritten, but the driver does not reread it after probe except through its own update path.

## Dependencies and Integration Points
The driver depends on the DA903x MFD register helpers (`da903x_update`, `da903x_write`, `da903x_set_bits`, `da903x_clr_bits`) and platform-device IDs from `linux/mfd/da903x.h`. It integrates with legacy board platform data for output current.

## Risks
The DA9034 output-current write is attempted without checking the return value. `get_brightness()` can report stale cached state if firmware or another driver changes WLED registers. Unsupported IDs fail probe, but no default case in `da903x_backlight_set()` reports an error if corrupted state reaches runtime.

## Test Signals
Exercise both PMIC IDs, max brightness selection, DA9034 boost enable/disable transitions, DA9030 charge-pump enable behavior, optional output-current platform data, suspend/resume through `BL_CORE_SUSPENDRESUME`, and I2C/MFD write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/da903x_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/da9052_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/da9052_bl.c

## Purpose
This platform driver controls one of three DA9052 PMIC WLED banks through the backlight subsystem.

## Important APIs, Types, and Functions
`struct da9052_bl` stores the parent `struct da9052`, current brightness, on/off state, and selected LED-bank index. `wled_bank[]` maps `DA9052_TYPE_WLED1/2/3` to PMIC LED config registers. `da9052_adjust_wled_brightness()` writes boost enable, LED current sink enable, clears the selected WLED register, waits, and then writes the requested brightness. `da9052_backlight_update_status()` updates state and brightness before applying hardware changes.

## Control Flow
Probe allocates state, retrieves the parent MFD data, obtains the bank index from the platform ID table, registers a raw backlight, sets initial brightness to zero/off, and calls `da9052_adjust_wled_brightness()` to force hardware off. Remove sets brightness zero and state off, then reapplies the sequence. Runtime updates always set state to on and use brightness zero to clear the selected bank after enabling/disabling common boost/current registers.

## State and Persistence
The driver caches brightness and state in memory. Shared PMIC boost and current-sink registers affect all WLED banks, so hardware state is not isolated to one backlight instance.

## Dependencies and Integration Points
It depends on the DA9052 MFD core (`da9052_reg_write`) and register definitions under `linux/mfd/da9052`. Platform IDs `da9052-wled1`, `da9052-wled2`, and `da9052-wled3` select the output bank.

## Risks
The update path always marks the WLED state on, even for brightness zero, so zero brightness relies on register values rather than the state enum. Common boost/current writes can affect sibling WLED outputs if multiple platform devices exist. Brightness is not clamped inside update beyond the backlight core max.

## Test Signals
Test each platform ID, probe initial off state, brightness 0/nonzero transitions, remove cleanup, MFD register failures at each write, and behavior when multiple WLED banks are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/da9052_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ep93xx_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ep93xx_bl.c

## Purpose
This platform driver controls the EP93xx SoC LCD `BRIGHT` PWM register and exposes it as a raw 0-255 backlight.

## Important APIs, Types, and Functions
`struct ep93xxbl` stores the mapped MMIO base and cached brightness. `ep93xxbl_set()` writes `(brightness << 8) | EP93XX_MAX_COUNT` to the PWM register and updates the cache. `ep93xxbl_update_status()` and `ep93xxbl_get_brightness()` implement the backlight callbacks. PM callbacks set brightness to zero on suspend and restore by calling `backlight_update_status()` on resume.

## Control Flow
Probe allocates state, fetches the first memory resource, maps it with `devm_ioremap()`, registers a raw backlight, sets default brightness 128, and writes the register. It intentionally does not request the memory region because the framebuffer driver shares the same register block.

## State and Persistence
The cached brightness is volatile. Hardware PWM state persists in MMIO until changed; resume replays the backlight core brightness rather than the cached zero written during suspend.

## Dependencies and Integration Points
The file depends on platform resources, MMIO accessors, and the backlight core. It has an explicit integration constraint with `drivers/video/ep93xx-fb.c` because both share register space.

## Risks
Because the MMIO region is not reserved, accidental overlapping access by other drivers is possible. `devm_ioremap()` rather than `devm_ioremap_resource()` means resource conflicts and range metadata are not enforced. There is no blank-state handling beyond what `backlight_get_brightness()` provides.

## Test Signals
Check probe with missing resource, MMIO mapping failure, default register value, brightness extremes, suspend writing zero, resume restoring requested brightness, and coexistence with the EP93xx framebuffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ep93xx_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/gpio_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/gpio_backlight.c

## Purpose
This simple platform driver turns one GPIO into a binary backlight device.

## Important APIs, Types, and Functions
`struct gpio_backlight` stores an optional controlled display device and the GPIO descriptor. `gpio_backlight_update_status()` sets the GPIO to the effective backlight brightness. `gpio_backlight_controls_device()` filters global blank notifications to the matching display device when platform data supplies one.

## Control Flow
Probe reads optional legacy platform data, checks the `default-on` property, obtains the unnamed GPIO, registers a raw max-brightness-1 backlight, determines initial power from firmware phandle/current GPIO state or legacy default, sets brightness to one, and drives the GPIO direction/output to the effective brightness. The driver binds to `gpio-backlight`.

## State and Persistence
No mutable driver state exists beyond the GPIO descriptor and optional display-device pointer. Hardware state is just the output level; there is no cached brightness field.

## Dependencies and Integration Points
It depends on GPIO descriptors, device properties, optional `gpio_backlight_platform_data`, Open Firmware match data, and `BL_CORE_SUSPENDRESUME`. It integrates with display blanking through `controls_device`.

## Risks
This is a binary device: all nonzero brightness values collapse to on. Initial power semantics differ between DT phandle-linked devices and non-DT/legacy devices. An active-low GPIO is handled by gpiolib, so board descriptions must encode polarity correctly.

## Test Signals
Test DT and platform-data probe, missing GPIO, active-low GPIOs, default-on behavior, reading existing GPIO state for phandle-linked DT nodes, display-specific blank filtering, and suspend/resume blanking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/gpio_backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/hp680_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/hp680_bl.c

## Purpose
This legacy platform driver controls HP Jornada 680 LCD backlight brightness using SH DAC output and HD64461 GPIO bits.

## Important APIs, Types, and Functions
File-scope state includes `hp680bl_suspended`, `current_intensity`, and `bl_lock`. `hp680bl_send_intensity()` computes effective brightness, serializes hardware access with a spinlock, enables or disables the DAC, toggles the LCD-off bit, and outputs inverted intensity through `sh_dac_output()`. Backlight callbacks wrap this helper, and PM callbacks force zero on suspend and restore on resume.

## Control Flow
Module init manually registers both the platform driver and a simple platform device named `hp680-bl`. Probe registers a raw backlight with max 255 and default 10, stores the backlight device as driver data, and applies brightness. Remove sets brightness to zero and calls the hardware path. Exit unregisters device and driver.

## State and Persistence
State is global and assumes one HP680 backlight. `current_intensity` is volatile. The hardware DAC/GPIO state persists only until the platform reinitializes it.

## Dependencies and Integration Points
The driver depends on SuperH/Jornada platform headers, `sh_dac_*`, HD64461 port accessors, platform devices, and the backlight subsystem. It is tightly bound to the HP680 board and not firmware-described.

## Risks
The driver uses direct port I/O and global state, so it is not suitable for multiple devices. Brightness is inverted for DAC output (`255 - intensity`), so polarity mistakes produce reversed brightness. PM state and current intensity are not protected by a separate mutex, though hardware writes are spinlocked.

## Test Signals
Test module init/exit, default brightness programming, zero/nonzero transitions, DAC enable/disable, HD64461 LCDOFF bit changes, suspend/resume, and remove forcing the panel dark.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/hp680_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/hx8357.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/hx8357.c

## Purpose
This SPI LCD driver initializes and powers Himax HX8357 and HX8369 display controllers. It exposes LCD power control through `lcd_device`; framebuffer memory updates are expected to arrive over a separate RGB/display interface.

## Important APIs, Types, and Functions
`struct hx8357_data` stores optional IM mode GPIOs, reset GPIO, SPI device, and current LCD state. The many `hx8357_seq_*` and `hx8369_seq_*` arrays encode vendor command sequences. `hx8357_spi_write_then_read()` builds 9-bit SPI command/data transfers by tagging data bytes with bit 8. `hx8357_lcd_reset()`, `hx8357_lcd_init()`, and `hx8369_lcd_init()` implement reset and variant-specific initialization. `hx8357_enter_standby()` and `hx8357_exit_standby()` implement power transitions.

## Control Flow
Probe sets up SPI, chooses an init function from OF match data, requests reset and optional `im` GPIO arrays, registers an LCD device named `mxsfb`, resets the panel, and runs the selected init sequence. `set_power` only sends standby/exit-standby commands when crossing the on/off boundary and updates `lcd->state` only on success. HX8357 init sets IM pins to SPI mode, sends power/VCOM/gamma/address/pixel-format/RGB/display-mode sequences, exits sleep, turns display on, and starts memory write. HX8369 init unlocks extension commands and sends its own display, waveform, VCOM, GIP, power, gamma, CABC, and brightness sequences.

## State and Persistence
Current power state is kept in memory. Panel registers retain sequence values until reset or power loss. No brightness backlight device is registered; HX8369 CABC and display-brightness commands are fixed initialization values.

## Dependencies and Integration Points
The driver depends on SPI, GPIO descriptors, device properties, OF match data, and the LCD class. The LCD device name `mxsfb` suggests integration with a matching framebuffer/display pipeline.

## Risks
The 9-bit SPI packing is sensitive to controller and SPI master support. Init tables are fixed and hardware-specific; wrong compatible data can send an incompatible sequence. Optional IM pins require at least three descriptors. There is no remove/shutdown hook to enter standby on driver removal or reboot.

## Test Signals
Test both compatibles, reset GPIO polarity/timing, optional IM GPIO count validation, SPI setup failure, individual sequence write failures, LCD power off/on transitions with 120 ms sleep delays, and probe-time initialization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/hx8357.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ili922x.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ili922x.c

## Purpose
This SPI LCD driver initializes Ilitek ILI9221/ILI9222 display controllers. Register access uses SPI, while pixel memory is refreshed over an RGB interface.

## Important APIs, Types, and Functions
`struct ili922x` stores SPI, LCD device, and power state. Module parameters `ili922x_id` and `tx_invert` alter start-byte ID and byte polarity. `ili922x_read_status()`, `ili922x_read()`, and `ili922x_write()` implement the controller's start-byte/index/data protocol with register-access speed limiting. `ili922x_poweron()`, `ili922x_poweroff()`, and `ili922x_display_init()` program power, display, gamma, GRAM window, and RGB-interface registers. `ili922x_lcd_power()` backs the LCD `set_power` callback.

## Control Flow
Probe allocates state, reads `REG_DRIVER_CODE_READ`, verifies the masked device ID, reads status for debug, runs display initialization, registers `ili922xlcd`, and powers on. Runtime power transitions call the power-on/off register sequences only when crossing the `POWER_IS_ON()` boundary. Remove powers the panel off.

## State and Persistence
Power state is volatile in `ili->power`. The panel retains programmed register state until reset or power loss. There is no persistent software storage.

## Dependencies and Integration Points
The driver depends on SPI, OF headers, the LCD class, and module parameters for legacy board quirks. It caps register access speed to 4 MHz while allowing higher-speed GRAM access outside this driver.

## Risks
Several initialization writes ignore return values because `ili922x_display_init()` is `void`; failures can leave partially initialized hardware. Power-on/off accumulate return codes with addition rather than preserving the first negative error cleanly. `tx_invert` and `ili922x_id` are global module settings, not per-device properties.

## Test Signals
Test ID read success/failure, register speed capping, byte inversion mode, init sequence execution, power off/on via sysfs LCD power, remove cleanup, and SPI transfer failures during read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ili922x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ili9320.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ili9320.c

## Purpose
This is the reusable core for ILI9320 LCD controllers attached over SPI. Board-specific clients provide reset and initialization callbacks; this file supplies register write helpers, LCD class integration, and power/PM handling.

## Important APIs, Types, and Functions
`ili9320_write()` and `ili9320_write_regs()` are exported helpers used by client drivers. `ili9320_setup_spi()` prebuilds a two-transfer SPI message for index and data cycles. `ili9320_probe_spi()` validates platform data, allocates `struct ili9320`, registers an LCD device, and powers the panel on. `ili9320_suspend()`, `ili9320_resume()`, `ili9320_shutdown()`, and `ili9320_remove()` are exported lifecycle helpers.

## Control Flow
The SPI write path fills `buffer_addr` with ID/index/write bytes and `buffer_data` with ID/data/write bytes, then calls `spi_sync()` on the prebuilt message. Probe requires positive panel size and a reset callback, sets access ID `ILI9320_SPI_IDCODE | ILI9320_SPI_ID(1)`, registers `ili9320`, and calls `ili9320_power(..., LCD_POWER_ON)`. First power-on resets the panel and calls the client `init()` callback, then sets display enable bits in cached `display1`. Power-off clears those bits.

## State and Persistence
`struct ili9320` stores current power, initialization status, platform data, client callbacks, cached `display1`/`power1`, and SPI buffers. Deep suspend writes sleep/deep-standby bits, clears `initialised`, and causes resume to reinitialize.

## Dependencies and Integration Points
The file depends on `video/ili9320.h`, the private `ili9320.h`, SPI, LCD core, and platform data. It is not a standalone SPI driver; client drivers call `ili9320_probe_spi()` with a `struct ili9320_client`.

## Risks
Platform data is mandatory and reset/init callbacks are trusted. `ili9320_power_on()` ignores the return value of `ili9320_init_chip()` when `initialised` is false, so an init failure may be followed by display-enable writes. The cached register fields must be initialized correctly by clients.

## Test Signals
Test probe validation, SPI message contents, client init failure paths, power on/off, deep suspend/resume reinitialization, exported write helpers, and shutdown powering off the panel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ili9320.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ili9320.h -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ili9320.h

## Purpose
This private header defines the internal data structures and exported core-helper prototypes for the ILI9320 LCD controller driver.

## Important APIs, Types, and Functions
`struct ili9320_reg` is a register/value pair consumed by `ili9320_write_regs()`. `struct ili9320_client` names a board/client implementation and provides its `init()` callback. `struct ili9320_spi` holds the SPI device, prebuilt message, two transfers, ID byte, and address/data buffers. `struct ili9320` is the core runtime state shared by the implementation and clients. Prototypes expose write, probe, remove, shutdown, suspend, and resume helpers.

## Control Flow
The header has no executable control flow. It defines the contracts used by `ili9320.c`: clients fill `struct ili9320_client`, call `ili9320_probe_spi()`, and use exported write helpers during initialization.

## State and Persistence
The runtime state fields described here are all volatile kernel memory. The cached `display1` and `power1` values mirror controller registers and are used during power transitions.

## Dependencies and Integration Points
The declarations require `struct spi_device`, `struct lcd_device`, and `struct ili9320_platdata` from included kernel/video headers in C users. It is private to this driver family and pairs with the public `<video/ili9320.h>` register definitions.

## Risks
The structures expose low-level SPI buffers and cached registers directly to the core, so ABI-like coupling exists between client code and the core. The comment typo `attachged` is harmless, but any field reordering affects in-tree users compiled with this header.

## Test Signals
Validation is compile-time: ensure all client drivers build, exported prototypes match `ili9320.c`, and structure fields used by clients remain available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ili9320.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ipaq_micro_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ipaq_micro_bl.c

## Purpose
This platform child driver exposes an iPAQ microcontroller backlight command as a raw backlight device.

## Important APIs, Types, and Functions
`micro_bl_update_status()` builds `struct ipaq_micro_msg` with ID `MSG_BACKLIGHT`, instance byte 1, on/off byte, and 0-255 intensity, then sends it with `ipaq_micro_tx_msg_sync()`. `micro_bl_ops` uses `BL_CORE_SUSPENDRESUME`; `micro_bl_props` sets max brightness 255 and default 64.

## Control Flow
Probe fetches the parent `struct ipaq_micro`, registers `ipaq-micro-backlight`, stores the backlight as platform data, and immediately applies default brightness. There is no explicit remove path because devm manages registration.

## State and Persistence
No driver-private mutable state is kept. The microcontroller may retain its last brightness, while the Linux side relies on backlight core properties.

## Dependencies and Integration Points
The driver depends on the iPAQ micro MFD interface and platform child name `ipaq-micro-backlight`. It integrates with suspend/resume through the backlight core.

## Risks
The message protocol is fixed to instance `0x01`; platforms with multiple backlights would need changes. There is no `get_brightness()` to read controller state. All failures come from synchronous microcontroller messaging.

## Test Signals
Test probe with valid parent data, default update message contents, zero brightness on/off byte, nonzero brightness, transport failure propagation, and suspend/resume updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ipaq_micro_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/jornada720_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/jornada720_bl.c

## Purpose
This platform driver controls HP Jornada 710/720/728 backlight brightness through the Jornada SSP microcontroller protocol and a PPC GPIO enable bit.

## Important APIs, Types, and Functions
`jornada_bl_get_brightness()` checks the PPC backlight enable bit, sends `GETBRIGHTNESS`, validates `TXDUMMY`, reads the value, and returns an inverted brightness. `jornada_bl_update_status()` turns hardware off when blanked, enables the PPC bit otherwise, sends `SETBRIGHTNESS`, and writes the inverted 0-255 value. `jornada_bl_ops` exposes get/update callbacks with `BL_CORE_SUSPENDRESUME`.

## Control Flow
Probe registers a raw backlight named `S1D_DEVICENAME`, sets power on and default brightness 25, applies the setting, and logs the driver banner. Runtime updates serialize SSP transactions with `jornada_ssp_start()`/`jornada_ssp_end()` and use timeout errors when the microcontroller handshake is not `TXDUMMY`.

## State and Persistence
There is no private state. Brightness lives in the microcontroller and backlight core properties. The PPC GPIO bit records whether the backlight is physically enabled.

## Dependencies and Integration Points
The driver depends on Jornada platform headers, direct PPC port macros, `video/s1d13xxxfb.h` for the device name, and the backlight core. It is paired with `jornada720_lcd.c` for LCD power/contrast.

## Risks
The inverted brightness mapping is hardware-specific and easy to misinterpret. Backlight-off handshake failure still clears the PPC bit and reports timeout. Direct global register manipulation assumes no competing owner.

## Test Signals
Test SSP success and timeout cases, blanking to off, brightness inversion, get when PPC bit is off, default probe update, and suspend/resume core calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/jornada720_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/jornada720_lcd.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/jornada720_lcd.c

## Purpose
This platform driver controls LCD power and contrast for HP Jornada 700-series devices through PPC GPIO bits and the Jornada SSP microcontroller.

## Important APIs, Types, and Functions
`jornada_lcd_get_power()` reads PPC bit `PPC_LDD2`. `jornada_lcd_get_contrast()` and `jornada_lcd_set_contrast()` issue `GETCONTRAST`/`SETCONTRAST` SSP commands and validate `TXDUMMY`. `jornada_lcd_set_power()` toggles `PPC_LDD2`. The `lcd_ops` table supplies power and contrast callbacks.

## Control Flow
Probe registers an LCD device named `S1D_DEVICENAME`, stores it as platform data, sets default contrast `0x80`, powers the LCD on, and waits 100 ms. Sysfs operations through the LCD class call the contrast and power callbacks directly.

## State and Persistence
No private state is kept. Power state is the PPC output bit; contrast is held by the microcontroller. There is no software cache.

## Dependencies and Integration Points
The driver depends on Jornada platform register macros, SSP helpers, the LCD class, and the S1D framebuffer device name. It complements the separate Jornada backlight driver.

## Risks
SSP errors surface as `-ETIMEDOUT`, but direct power bit writes always return success. Contrast reads return zero when the LCD is off, which is a policy choice rather than a hardware contrast value. Direct PPC register access assumes board exclusivity.

## Test Signals
Test probe defaults, sysfs `lcd_power`, sysfs `contrast`, SSP timeout handling, power off returning contrast zero, and coexistence with the Jornada backlight driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/jornada720_lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/kb3886_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/kb3886_bl.c

## Purpose
This DMI-gated platform driver controls the KB3886 backlight controller on Tabletkiosk Sahara Touch-iT systems through legacy I/O ports.

## Important APIs, Types, and Functions
`kb3886_bl_set_intensity()` writes controller select, PWM write command, and intensity bytes to ports `0x64` and `0x60` under `bl_mutex`. `struct kb3886bl_machinfo` supplies max/default/limit values and the setter callback. `kb3886bl_send_intensity()` applies suspend forcing and stores `kb3886bl_intensity`. PM callbacks toggle `KB3886BL_SUSPENDED` and call `backlight_update_status()`.

## Control Flow
Module init checks DMI vendor/product, registers a static platform device with platform data, then registers the platform driver. Probe stores platform data globally, registers `kb3886-bl`, sets power on/default brightness `0xa0`, and applies it. Exit unregisters the driver.

## State and Persistence
The driver is single-instance and global. It stores current intensity, backlight device pointer, platform callback pointer, and suspend flags in file-scope variables. Hardware PWM state persists until overwritten.

## Dependencies and Integration Points
It depends on DMI matching, x86-style port I/O, platform devices, mutexes, delays, and the backlight core. The module alias targets the specific DMI system.

## Risks
The static platform device is not explicitly unregistered in exit after `platform_add_devices()`, so lifetime relies on module/device-core behavior. Direct I/O port writes are hardware-specific. `limit_mask` is initialized but not used in the runtime path.

## Test Signals
Test DMI match/no-match, port write order under mutex, default brightness, suspend/resume zeroing/restoration, platform-data validation, and module unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/kb3886_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ktd253-backlight.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ktd253-backlight.c

## Purpose
This GPIO pulse-count modulation driver controls Kinetic KTD253/KTD259 backlight chips. The chip powers up at maximum current and each pulse steps brightness down through 32 ratios.

## Important APIs, Types, and Functions
`struct ktd253_backlight` stores device, backlight, GPIO, and current ratio. `ktd253_backlight_set_max_ratio()` drives GPIO high to establish max brightness. `ktd253_backlight_stepdown()` sends a precise low/high pulse using non-sleeping GPIO APIs and returns `-EAGAIN` if the low interval exceeded the critical off threshold. `ktd253_backlight_update_status()` computes target ratio, powers off on zero, resets to max if needed, and steps down until the target is reached.

## Control Flow
Probe reads and clamps `max-brightness` and `default-brightness`, gets the `enable` GPIO, holds it low long enough to force off, registers a backlight, initializes core brightness/power fields, and applies status. Runtime updates either power the chip off or loop through timing-sensitive pulses. If a pulse was interrupted long enough to risk losing state, the driver powers off, re-enables max, and retries.

## State and Persistence
The software ratio cache is essential because the chip only supports relative step-down pulses. On power-off the cache becomes zero; on power-on the known state is max ratio. There is no nonvolatile storage.

## Dependencies and Integration Points
The driver depends on GPIO descriptors that can be used from non-sleeping context for pulse timing, device properties, delays, and the backlight core. It matches `kinetic,ktd253` and `kinetic,ktd259`.

## Risks
GPIO expanders or sleeping GPIO controllers are invalid despite descriptor APIs allowing them at probe. Interrupt latency can corrupt pulse timing; the driver detects only long low phases. The update loop may need many pulses when moving from low ratios to slightly higher ratios because the hardware wraps via max.

## Test Signals
Test property clamping, GPIO acquisition, initial off reset, zero brightness timing, stepping down from max to target, wrap from ratio 1 to 32, `-EAGAIN` recovery, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ktd253-backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ktd2801-backlight.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ktd2801-backlight.c

## Purpose
This platform driver controls a Kinetic KTD2801 backlight chip using the kernel ExpressWire LED protocol helper.

## Important APIs, Types, and Functions
`ktd2801_timing` defines the ExpressWire timings extracted from Samsung code. `struct ktd2801_backlight` embeds `expresswire_common_props`, stores the backlight device, and tracks whether the chip was on. `ktd2801_update_status()` powers off on blanking, enables ExpressWire when transitioning on, and writes an 8-bit brightness value.

## Control Flow
Probe allocates state, initializes timing, reads/clamps brightness properties, gets `ctrl` GPIO, registers a backlight, initializes brightness, and calls `backlight_update_status()`. Runtime updates are mostly delegated to `expresswire_power_off()`, `expresswire_enable()`, and `expresswire_write_u8()`.

## State and Persistence
`was_on` prevents redundant ExpressWire enable sequences. Brightness is kept by the chip/backlight core; no persistent storage exists.

## Dependencies and Integration Points
The driver depends on `linux/leds-expresswire.h`, GPIO descriptors, device properties, and the backlight subsystem. It imports the `EXPRESSWIRE` namespace and matches `kinetic,ktd2801`.

## Risks
Correctness depends on the ExpressWire timing constants and GPIO electrical behavior. `was_on` starts true, so the first update after probe writes brightness without an explicit enable sequence because the GPIO is requested high. Error returns from ExpressWire write helpers are not propagated because the helpers are void in this usage.

## Test Signals
Test max/default property clamping, GPIO failure, initial update behavior, blanking power-off, re-enable after blanking, brightness write values, and suspend/resume through blank state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ktd2801-backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ktz8866.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ktz8866.c

## Purpose
This I2C/regmap driver controls the Kinetic KTZ8866 backlight and optional LCD bias functions.

## Important APIs, Types, and Functions
`struct ktz8866` stores client, regmap, `led_on`, and optional enable GPIO. `ktz8866_backlight_update_status()` toggles the backlight enable bit on zero/nonzero transitions and writes 11-bit brightness split across `BL_BRT_LSB` and `BL_BRT_MSB`. `ktz8866_init()` applies optional DT properties for current sinks, ramp delays, and LCD bias enable.

## Control Flow
Probe initializes regmap, enables `vddpos` and `vddneg` regulators, gets optional `enable` GPIO high, registers a linear raw backlight with default 1500/max 2047, calls `ktz8866_init()`, stores the backlight as I2C client data, and applies brightness. Remove sets brightness zero and updates hardware.

## State and Persistence
The `led_on` boolean tracks whether the enable bit is believed active. Brightness registers hold hardware state until changed. Regulator enables are devm-managed.

## Dependencies and Integration Points
The driver depends on I2C, regmap, regulator bulk-by-name via `devm_regulator_get_enable()`, optional GPIO, OF properties, and the backlight core. It matches `kinetic,ktz8866`.

## Risks
Register writes in `update_status()` ignore return values, so I2C failures are not reported to the backlight core. Ramp delay uses `ilog2(val)` without explicit zero handling for `current-ramp-delay-ms`; zero would be invalid for `ilog2()`. `current-num-sinks` is used as `BIT(val)-1`, so out-of-range values can program unexpected bits.

## Test Signals
Test regulator failures, optional GPIO behavior, default and property-based initialization, brightness split encoding, zero/nonzero enable transitions, remove cleanup, invalid ramp/current-sink properties, and I2C write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ktz8866.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/l4f00242t03.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/l4f00242t03.c

## Purpose
This SPI LCD driver powers and initializes an Epson L4F00242T03 panel, including regulators and reset/enable GPIOs.

## Important APIs, Types, and Functions
`struct l4f00242t03_priv` stores SPI, LCD device, LCD state, IO/core regulators, reset GPIO, and enable GPIO. `l4f00242t03_lcd_init()` sets regulator voltages, enables regulators, resets the panel, asserts data enable, and sends initial 9-bit SPI commands. `l4f00242t03_lcd_power_set()` handles on, standby, resume, and full-off transitions. Remove and shutdown force LCD power off.

## Control Flow
Probe sets `spi->bits_per_word = 9`, requests reset/enable GPIOs and `vdd`/`vcore` regulators, registers an LCD device, initializes the panel from off into reduced state, then sets power on. `set_power` recursively initializes from full off before entering requested on or standby states. Full off sends display-off, waits, then disables GPIO/regulators.

## State and Persistence
`lcd_state` records the last requested LCD class power state. Regulator and panel register state are hardware-held and lost on powerdown. No persistent storage exists.

## Dependencies and Integration Points
The driver depends on SPI masters supporting 9-bit words, GPIO descriptors, regulator consumer APIs, and the LCD class.

## Risks
`l4f00242t03_lcd_init()` logs regulator/SPI failures but returns void, so probe and power transitions may continue after partial initialization. Recursive power handling must maintain `lcd_state` carefully. Regulator disable order in powerdown is IO before core, matching existing code but hardware-sensitive.

## Test Signals
Test SPI setup failure, missing GPIO/regulators, regulator voltage/enable failures, probe initialization, sysfs power transitions on/reduced/off, shutdown cleanup, and 9-bit command formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/l4f00242t03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lcd.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lcd.c

## Purpose
This file implements the Linux LCD class abstraction used by low-level LCD panel drivers. It creates `/sys/class/lcd/*` devices, exposes power/contrast attributes, supports managed registration, and provides broadcast blank/mode notifications.

## Important APIs, Types, and Functions
Global `lcd_dev_list` tracks registered LCD devices under `lcd_dev_list_mutex`. `lcd_notify_blank_all()` and `lcd_notify_mode_change_all()` walk the list and call per-device ops after `controls_device` filtering. Sysfs handlers implement `lcd_power`, `contrast`, and `max_contrast`. `lcd_device_register()` and `lcd_device_unregister()` allocate/register/free `struct lcd_device`. `devm_lcd_device_register()` and `devm_lcd_device_unregister()` wrap registration in devres.

## Control Flow
The class is registered at `postcore_initcall()` so built-in LCD users can register later. `lcd_device_register()` allocates the device, initializes locks, sets class/parent/release/name/driver-data, stores ops, registers the device, then adds it to the global list. Unregister removes it from the list, clears `ops` under `ops_lock`, and unregisters the device. Sysfs reads/writes hold `ops_lock` while calling optional driver callbacks.

## State and Persistence
The only class-level state is the in-memory global list. Each LCD device carries properties, locks, ops pointer, and driver data. No state persists across reboot.

## Dependencies and Integration Points
The file depends on the device core, sysfs attribute groups, notifier-like exported helpers, mutex guard helpers, and `linux/lcd.h`. It is the integration point for panel drivers in this work item.

## Risks
Sysfs store paths ignore callback return values from `set_power()` and `set_contrast()` and return `count` if an op exists. Broadcast notifications call callbacks while holding the global list lock and each device ops lock, so callback reentrancy into registration paths would be hazardous. The class init warning says "backlight class" although it registers the LCD class.

## Test Signals
Test class registration, device register/unregister, devm release, sysfs power/contrast read-write with and without ops, broadcast blank/mode filtering, unregister racing with sysfs, and driver callbacks returning errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/led_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/led_bl.c

## Purpose
This platform driver aggregates one or more LED class devices into a single raw backlight device.

## Important APIs, Types, and Functions
`struct led_bl_data` stores the backlight device, LED classdev pointers, optional brightness-level table, defaults, max brightness, and enabled flag. `led_bl_set_brightness()` maps a backlight level through the optional levels table and writes every LED. `led_bl_power_off()` sets all LEDs to `LED_OFF`. `led_bl_get_leds()` resolves LED phandles and validates equal ranges. `led_bl_parse_levels()` reads `brightness-levels` and `default-brightness-level`.

## Control Flow
Probe resolves LEDs from the `leds` property, optionally maps brightness levels, registers a backlight, creates device links to LED suppliers, disables each LED's own sysfs interface while under `led_access`, and applies initial status. Remove unregisters the backlight, powers LEDs off, and reenables LED sysfs access.

## State and Persistence
The driver owns volatile aggregation state and disables direct LED sysfs control during its lifetime. Brightness values persist only in the LED class devices/hardware.

## Dependencies and Integration Points
It depends on OF LED phandles, LED class APIs, device links, and the backlight subsystem. It binds to `led-backlight`.

## Risks
`props.power` is initialized opposite of the usual expectation: default brightness greater than zero sets `BACKLIGHT_POWER_OFF`, relying on `backlight_get_brightness()` semantics. All LEDs must have identical ranges; mixed hardware cannot be used without a table or redesign. Direct LED sysfs access is disabled, which can surprise users but avoids competing control.

## Test Signals
Test no LEDs, LED lookup deferral/failure, mismatched LED ranges, brightness-level mapping, default-brightness-level validation, device-link failure rollback, LED sysfs disable/enable, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/led_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lm3509_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lm3509_bl.c

## Purpose
This I2C/regmap driver exposes the TI LM3509 dual-sink backlight controller as one or two raw backlight devices.

## Important APIs, Types, and Functions
`struct lm3509_bl` stores regmap, main/sub backlight devices, and optional reset GPIO. `struct lm3509_bl_led_data` holds per-child label, sink mask, brightness, and max. `lm3509_update_status()` writes the bank brightness register and toggles enable bits in `REG_GP` depending on blanking. DT helpers parse child `reg`, `led-sources`, `label`, `max-brightness`, and `default-brightness`.

## Control Flow
Probe checks I2C functionality, initializes regmap, gets optional reset GPIO, pulses reset, parses child DT nodes, reads optional OLED and ramp-rate properties, writes `REG_GP`, registers main/sub backlights based on parsed sink masks, and immediately applies their brightness. Sink validation prevents duplicate use and restricts the secondary bank to valid hardware combinations.

## State and Persistence
The software state is the regmap and registered devices. Configuration is loaded from firmware at probe and written into device registers; there is no runtime persistence beyond hardware registers.

## Dependencies and Integration Points
The driver depends on I2C, regmap, GPIO, OF child-node parsing, and the backlight subsystem. It matches `ti,lm3509`.

## Risks
If no child nodes are present, parsing succeeds but no backlight may be registered. `seen_led_sources` is initialized but led data defaults are zero, so child definitions are required for active outputs. Invalid ramp rates only warn and fall back to default bits.

## Test Signals
Test main-only, sub-only, unified main+sub, duplicate sink rejection, invalid child `reg`, reset GPIO timing, ramp-rate property mapping, OLED mode bit, and regmap write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lm3509_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lm3533_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lm3533_bl.c

## Purpose
This platform child driver exposes one LM3533 high-voltage control bank as a raw backlight and provides sysfs controls for ALS, linear mapping, and PWM mode.

## Important APIs, Types, and Functions
`struct lm3533_bl` stores parent MFD pointer, `struct lm3533_ctrlbank`, backlight device, and bank ID. Backlight callbacks call `lm3533_ctrlbank_set_brightness()` and `lm3533_ctrlbank_get_brightness()`. Sysfs attributes include `id`, `als_channel`, `als_en`, `linear`, and `pwm`, with ALS attributes hidden when the parent lacks ALS support. `lm3533_bl_setup()` applies max current and PWM from platform data.

## Control Flow
Probe fetches parent MFD data and platform data, validates `pdev->id` against the two HV control banks, registers a named raw backlight, creates the attribute group, applies initial brightness, configures max current/PWM, and enables the control bank. Remove disables the bank and removes sysfs.

## State and Persistence
State lives in the parent LM3533 register map and the `lm3533_ctrlbank` helper. Sysfs writes mutate hardware configuration but are not persisted outside the chip.

## Dependencies and Integration Points
The driver depends on the LM3533 MFD API, platform data, sysfs, and the backlight core. It is instantiated by the parent MFD for each configured bank.

## Risks
Platform data is mandatory; there is no DT parser here. Sysfs writes expose low-level ALS/PWM/linear bits directly and rely on parent helper validation. Probe creates sysfs before setup/enabling, so setup failure must remove the group, which the error path handles.

## Test Signals
Test illegal bank IDs, missing platform data, sysfs visibility with/without ALS, brightness get/set, PWM and linear sysfs writes, setup failures, enable/disable, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lm3533_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lm3630a_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lm3630a_bl.c

## Purpose
This I2C/regmap driver controls TI LM3630A dual-bank backlight hardware, with optional PWM and interrupt handling.

## Important APIs, Types, and Functions
The driver uses `struct lm3630a_chip` for device, regmap, platform data, enable GPIO, PWM state, IRQ/workqueue state, and backlight devices. Register helpers wrap regmap access. Backlight update callbacks write bank brightness registers and, when configured, drive a PWM device instead. Firmware parsing validates child banks, `led-sources`, labels, defaults, max brightness, and linear mapping. Interrupt handling records fault bits from the chip.

## Control Flow
Probe checks I2C support, initializes regmap, creates or reads platform data, parses firmware if needed, gets optional enable GPIO high, initializes the chip registers, registers one or two backlight devices based on bank controls, optionally obtains a PWM named `lm3630a-pwm`, and configures IRQ handling if present. Remove writes zero to both brightness registers and tears down IRQ/workqueue resources.

## State and Persistence
Runtime state includes platform configuration, brightness/core properties, PWM state, and interrupt worker state. Hardware registers persist until reset or removal cleanup writes zero.

## Dependencies and Integration Points
The driver depends on I2C, regmap, GPIO, PWM, fwnode APIs, optional IRQ/workqueue infrastructure, and the backlight core. It matches `ti,lm3630a`.

## Risks
Firmware parsing is strict about valid bank/sink combinations; invalid board descriptions fail probe. PWM mode depends on a named PWM and must be coordinated with brightness-register behavior. IRQ cleanup is manual and must match successful interrupt setup. As with many LED drivers, incorrect max/default brightness values can overdrive user expectations even if clamped by code.

## Test Signals
Test DT child parsing for bank A/B, combined LEDB-on-A mode, linear mapping, default/max clamping, enable GPIO, PWM mode acquisition and duty updates, IRQ setup/fault handling, remove zeroing both banks, and regmap failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lm3630a_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lm3639_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lm3639_bl.c

## Purpose
This I2C/regmap driver controls a TI LM3639 combined backlight, flash LED, and torch LED device.

## Important APIs, Types, and Functions
`struct lm3639_chip_data` stores platform data, one backlight device, flash/torch LED class devices, regmap, mode/map fields, and last flag. `lm3639_chip_init()` programs pin routing, initial brightness, and output enables. `lm3639_bled_update_status()` handles PWM-platform callback mode or I2C brightness writes and enable bit changes. LED class brightness callbacks control torch and flash fields in `REG_FL_CONF_1` and `REG_ENABLE`. A write-only `bled_mode` sysfs attribute toggles brightness mapping.

## Control Flow
Probe requires platform data, initializes regmap, configures the chip, registers the backlight, creates `bled_mode`, registers flash LED, then torch LED. Error paths unwind LED/sysfs registrations. Remove disables all outputs, unregisters torch/flash LEDs, and removes the sysfs file.

## State and Persistence
Backlight, torch, and flash state live in hardware registers and LED/backlight core properties. There is no firmware parser; all configuration is platform data.

## Dependencies and Integration Points
The file depends on I2C, regmap, LED class, backlight core, interrupts headers, and `linux/platform_data/lm3639_bl.h`. It integrates with board PWM callbacks when `pin_pwm` is configured.

## Risks
Platform data is mandatory and trusted. In PWM mode, missing platform callbacks cause logged errors but update returns the current brightness rather than a hard failure. Fault flags are read and logged but not surfaced through a structured error interface. Backlight, torch, and flash share enable register bits, so coordination matters.

## Test Signals
Test missing platform data, chip init register writes, I2C and PWM brightness modes, `bled_mode` sysfs write, torch/flash brightness zero/nonzero, fault flag logging, error unwinding, and remove disabling all outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lm3639_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lms283gf05.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lms283gf05.c

## Purpose
This SPI LCD driver initializes and powers a Samsung LMS283GF05 panel using fixed vendor register sequences.

## Important APIs, Types, and Functions
`struct lms283gf05_state` stores SPI, LCD device, and optional reset GPIO. `struct lms283gf05_seq` describes register/value/delay entries. `lms283gf05_toggle()` writes each register index (`0x74`) and data (`0x76`) pair over SPI and delays as requested. `lms283gf05_power_set()` runs the init sequence when on and the powerdown sequence when off.

## Control Flow
Probe obtains optional reset GPIO, registers an LCD device, stores state, resets the panel if possible, and runs the init sequence. LCD power writes always replay the full on or off sequence depending on requested power threshold.

## State and Persistence
There is no software power cache and `get_power` is NULL. The panel register state exists only in hardware.

## Dependencies and Integration Points
The driver depends on SPI, optional GPIO, delays, and the LCD class. It registers an SPI driver named `lms283gf05`.

## Risks
SPI write return values are ignored in the sequence helper, so hardware communication failures are silent. Without a power cache, repeated `set_power` calls replay full sequences. Optional reset GPIO is requested with non-devm `gpiod_get_optional()` and is not explicitly put, which is a lifetime concern.

## Test Signals
Test probe with and without reset GPIO, init sequence writes/delays, powerdown sequence, repeated sysfs power writes, and SPI write failure instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lms283gf05.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lms501kf03.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lms501kf03.c

## Purpose
This SPI LCD panel driver initializes and powers the Samsung LMS501KF03 TFT panel through 9-bit SPI command/data transfers and platform power/reset callbacks.

## Important APIs, Types, and Functions
`struct lms501kf03` stores device, SPI, power state, LCD device, and platform data. Sequence arrays encode password, power, display, RGB interface, inversion, VCOM, gate, panel, color, gamma, sleep-out, and display-on/off commands. `lms501kf03_panel_send_sequence()` writes command byte first and subsequent bytes as data. `lms501kf03_power_on()` calls platform `power_on`, waits, calls reset, initializes LDI, and enables display. PM callbacks force off on suspend and on after resume.

## Control Flow
Probe sets SPI to 9-bit mode, requires platform data, registers an LCD device, and either powers on if the bootloader left the panel off or marks it already on. Runtime `set_power` accepts only on/off/reduced, then calls the internal power transition helper. Remove and shutdown power off.

## State and Persistence
`lcd->power` tracks current LCD state. Platform data controls external rails and reset timing. Panel registers persist while powered.

## Dependencies and Integration Points
The driver depends on SPI, LCD class, and legacy `struct lcd_platform_data` callbacks/delays. It has no DT parser.

## Risks
Platform `power_on` and `reset` callbacks are mandatory for normal operation; missing callbacks fail power-on. `seq_display_off` contains command `0x10` (sleep-in) despite its name, so sequencing expectations must come from the panel datasheet. Suspend discards prior reduced/on distinction and resume always powers on.

## Test Signals
Test SPI setup, missing platform data/callbacks, bootloader-on vs off paths, LDI init sequence error propagation, sysfs power validation, suspend/resume, remove/shutdown poweroff, and 9-bit SPI formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lms501kf03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/locomolcd.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/locomolcd.c

## Purpose
This legacy Locomo driver controls LCD power and frontlight brightness for Sharp Zaurus Collie/Poodle-era hardware.

## Important APIs, Types, and Functions
Global pointers track the Locomo device and backlight device. `locomolcd_on()` and `locomolcd_off()` sequence Locomo GPIOs, DAC/common voltage, and timing controller registers. `locomolcd_power()` is exported and wraps those sequences with local IRQ disable. `locomolcd_set_intensity()` maps brightness levels 0-4 to hard-coded `locomo_frontlight_set()` parameters and honors `LOCOMOLCD_SUSPENDED`.

## Control Flow
Module init registers a `locomo_driver` for `LOCOMO_DEVID_BACKLIGHT`. Probe stores the Locomo device, configures frontlight GPIO direction, registers `locomo-bl`, sets default brightness 2, and applies it. Suspend sets the suspended flag and reapplies intensity as zero; resume clears it and restores. Remove sets brightness zero, unregisters the backlight, and clears the global device pointer under IRQ disable.

## State and Persistence
This is single-instance global state. `current_intensity`, `locomolcd_flags`, and global device pointers are volatile. Hardware state is in Locomo GPIO/registers and DAC output.

## Dependencies and Integration Points
The driver depends on Locomo bus APIs, ARM machine detection, `sharpsl_param.comadj`, SA1100 generic headers, and the backlight core. `locomolcd_power()` is exported for other platform code.

## Risks
The file explicitly assumes old single-CPU hardware and uses local IRQ disabling rather than general locking. Long delays occur with interrupts disabled in `locomolcd_power()`. Global exported power control can race conceptually with driver remove if callers do not honor device lifetime.

## Test Signals
Test Locomo probe/remove, exported power on/off, comadj defaulting on Collie, all brightness levels including invalid values, suspend/resume, and frontlight GPIO/register sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/locomolcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lp855x_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lp855x_bl.c

## Purpose
This I2C driver supports the TI LP8550/1/2/3/5/6/7 backlight family in register-based or PWM-based brightness modes, with optional EEPROM/EPROM programming and regulator control.

## Important APIs, Types, and Functions
`struct lp855x` stores chip identity, mode, device config, I2C client, backlight, platform data, PWM, regulators, and PWM-init state. `lp855x_configure()` performs optional device-specific pre-init, writes initial brightness and device-control registers, programs valid ROM addresses, and runs optional post-init. `lp855x_pwm_ctrl()` computes PWM duty. `lp855x_bl_update_status()` chooses PWM or register brightness. DT/ACPI parsers populate platform data.

## Control Flow
Probe identifies the chip from I2C or ACPI ID, selects register layout, parses platform data/DT/ACPI, obtains optional `power` and `enable` regulators, detects optional PWM named after the chip, enables regulators with required delay, configures the chip, registers a backlight, creates `chip_id` and `bl_ctl_mode` sysfs attributes, and applies brightness. Remove sets brightness zero, disables regulators, and removes sysfs.

## State and Persistence
Configuration from firmware becomes platform data in memory. Optional ROM programming writes device nonvolatile or shadow configuration regions depending on chip behavior. PWM state persists in the PWM provider; regulator state is managed at probe/remove.

## Dependencies and Integration Points
The driver depends on I2C SMBus block functionality, PWM, regulators, OF/ACPI, platform data, sysfs, and the backlight core. LP8557/LP8555 use a different brightness/control register map and BL_ON pre/post sequence.

## Risks
Invalid ROM addresses are silently skipped, which avoids bad writes but can hide firmware mistakes. ACPI assumes firmware already initialized register mode and reads current registers. PWM duty calculation uses brightness times period and should be checked for range. Regulator-enable failure paths unwind manually.

## Test Signals
Test each chip ID, DT parsing including child ROM entries, ACPI readback path, register vs PWM mode, LP8557 pre/post BL_ON handling, regulator enable/unwind, sysfs attributes, suspend blanking, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lp855x_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lp8788_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lp8788_bl.c

## Purpose
This platform child driver exposes the TI LP8788 MFD backlight block as a raw backlight device.

## Important APIs, Types, and Functions
`struct lp8788_bl` stores parent `struct lp8788` and the backlight device. `lp8788_backlight_configure()` programs ramp time, full-scale current, exponential dimming, and enable bits. `lp8788_bl_update_status()` writes brightness and forces zero during core suspend. A read-only sysfs attribute reports "Register based" control mode.

## Control Flow
Probe fetches parent MFD data, allocates state, configures hardware, registers `lcd-backlight`, creates sysfs attributes, and applies brightness. Remove sets brightness zero, updates hardware, removes sysfs, and unregisters the backlight.

## State and Persistence
The driver holds only the parent pointer and backlight device. Hardware registers retain configuration until the parent or removal changes them.

## Dependencies and Integration Points
It depends on LP8788 MFD helper `lp8788_write_byte`, platform child name `LP8788_DEV_BACKLIGHT`, sysfs, and the backlight core.

## Risks
The driver uses hard-coded ramp, current, and dimming policy rather than firmware properties. `lp8788_bl_update_status()` ignores the return value of `lp8788_write_byte()`, so write failures are not reported. It uses non-devm `backlight_device_register()` and manually unregisters.

## Test Signals
Test hardware configuration writes, registration failure unwind, sysfs creation/removal, brightness update including suspend forcing zero, remove cleanup, and parent MFD write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lp8788_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ltv350qv.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ltv350qv.c

## Purpose
This SPI LCD driver controls power sequencing for the Samsung LTV350QV QVGA panel.

## Important APIs, Types, and Functions
`struct ltv350qv` stores SPI, an 8-byte transfer buffer, current power state, and LCD device. `ltv350qv_write_reg()` sends a two-transfer index/data SPI message using opcodes from `ltv350qv.h`. `ltv350qv_power_on()` programs power, interface, timing, porch, gamma, and display-on registers with recovery attempts on failure. `ltv350qv_power_off()` executes the display-off/powerdown sequence.

## Control Flow
Probe allocates state and buffer, registers an LCD device, powers the panel on, and stores driver data. Runtime `set_power` only runs sequences on on/off boundary transitions. Suspend powers off; resume powers on; remove and shutdown power off.

## State and Persistence
`lcd->power` records current LCD class state. Panel registers persist while powered. The SPI buffer is reused for each register write.

## Dependencies and Integration Points
The driver depends on SPI, LCD core, and private register definitions in `ltv350qv.h`. It binds to SPI alias/name `ltv350qv`.

## Risks
The power-on path has best-effort recovery but still may leave partial register state after SPI errors. No external regulator/GPIO control exists here, so board files must have rails already handled. Register values are fixed for one panel timing/polarity setup.

## Test Signals
Test SPI message formatting, probe power-on, power-off, suspend/resume, shutdown, write failure at each power-on stage, and repeated sysfs power requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ltv350qv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ltv350qv.h -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/ltv350qv.h

## Purpose
This private header defines register addresses, SPI opcodes, and bitfield helpers for the Samsung LTV350QV LCD panel driver.

## Important APIs, Types, and Functions
Constants `LTV_OPC_INDEX` and `LTV_OPC_DATA` define the index/data SPI cycles. Register constants cover interface, data, entry mode, gate control, porch/timing, power, and gamma registers. Bitfield macros encode interface mode, RGB order, sync polarity, gate timing, source output timing, VCOM, drive current, supply current, and VCOMH/VCOML voltages.

## Control Flow
The header has no executable flow. `ltv350qv.c` consumes these macros to compose power-on and power-off register values.

## State and Persistence
No software state is declared. The macros describe hardware register fields used to create persistent panel register state at runtime.

## Dependencies and Integration Points
The file is private to the LTV350QV driver and guarded by `__LTV350QV_H`. It must stay synchronized with the S6F2002/LTV350QV command definitions used by the panel.

## Risks
Most macros do not validate semantic ranges beyond bit masking, so callers can encode invalid combinations. Because values are panel-specific, reuse for a different panel revision may require careful datasheet comparison.

## Test Signals
Compile-time validation with `ltv350qv.c`, review generated register values against datasheet, and test panel display timing/polarity after power-on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/ltv350qv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lv5207lp.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/lv5207lp.c

## Purpose
This I2C driver controls a Sanyo LV5207LP LED/backlight controller with platform-data supplied brightness defaults and display association.

## Important APIs, Types, and Functions
`struct lv5207lp` stores the I2C client, backlight device, and platform data. `lv5207lp_backlight_update_status()` writes control registers to enable charge pump/current paths and brightness minus one, or clears both controls for zero. `lv5207lp_backlight_controls_device()` filters blank notifications using `pdata->dev`.

## Control Flow
Probe requires platform data and SMBus byte-data support, allocates state, initializes backlight properties with max clamped to 32 and default clamped to max, registers the backlight, applies initial brightness, and stores the backlight in client data. Remove sets brightness zero and updates hardware.

## State and Persistence
The driver has no brightness cache beyond backlight core properties. Hardware control registers persist until cleared or power loss.

## Dependencies and Integration Points
It depends on I2C SMBus byte data, `linux/platform_data/lv5207lp.h`, and the backlight core. It integrates with display blanking through `controls_device`.

## Risks
Register write return values are ignored in `update_status()`, so I2C failures are silent. Platform data is mandatory; there is no OF/ACPI parser. Brightness value zero disables the chip, while nonzero maps to register value `brightness - 1`.

## Test Signals
Test missing platform data, unsupported I2C adapter, max/default clamping, zero/nonzero register writes, display blank filtering, remove cleanup, and I2C write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/lv5207lp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/max8925_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/max8925_bl.c

## Purpose
This platform child driver controls Maxim MAX8925 PMIC WLED backlight registers.

## Important APIs, Types, and Functions
`struct max8925_backlight_data` stores parent chip pointer, current brightness, mode-control register, and brightness-control register. `max8925_backlight_set()` writes brightness, toggles WLED enable bit on zero/nonzero transitions, and caches brightness. `max8925_backlight_get_brightness()` reads the brightness register. `max8925_backlight_dt_init()` reads a parent `backlight` child node for `maxim,max8925-dual-string`.

## Control Flow
Probe retrieves two `IORESOURCE_REG` resources for mode/control registers, registers a raw backlight with default max brightness, optionally builds platform data from DT, programs mode bits for scaling/frequency/dual-string, and applies brightness. Runtime update writes brightness first, then enables/disables the output bit.

## State and Persistence
Brightness cache mirrors hardware after successful writes. Mode settings come from platform/DT at probe and persist in PMIC registers until changed.

## Dependencies and Integration Points
The driver depends on MAX8925 MFD helpers, platform register resources, optional OF parsing, and the backlight core. It is bound by platform name `max8925-backlight`.

## Risks
`of_get_child_by_name()` failure in DT init logs an error but silently leaves platform data unset. The DT helper allocates platform data and assigns it to `pdev->dev.platform_data`, which is an older pattern. `get_brightness()` maps any read error to `-EINVAL`, losing the original error.

## Test Signals
Test missing register resources, DT dual-string parsing, platform data mode bits, brightness clamp/enable transitions, hardware readback, MFD write failures, and probe cleanup on registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/max8925_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/mp3309c.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/mp3309c.c

## Purpose
This I2C/regmap driver controls MPS MP3309C WLED backlights in either PWM dimming mode or analog I2C dimming mode.

## Important APIs, Types, and Functions
`struct mp3309c_platform_data` stores max/default brightness, optional levels table, dimming mode, OVP, sync mode, and power status. `struct mp3309c_chip` stores device, platform data, backlight, enable GPIO, regmap, and PWM. `mp3309c_enable_device()` sets enable, sync, and OVP bits. `mp3309c_bl_update_status()` applies PWM duty based on the levels table or packs analog 5-bit brightness into `REG_I2C_0`. `mp3309c_parse_fwnode()` validates firmware properties and level tables.

## Control Flow
Probe initializes regmap, allocates/parses platform data from firmware, gets optional enable GPIO and optional PWM depending on mode, registers a backlight, and applies status. PWM mode applies duty first, then enables the chip after a stabilization delay when transitioning from off/first power-on. Analog mode enables the chip on first update before programming dimming bits.

## State and Persistence
`pdata->status` tracks first/off/on state and affects enable sequencing. Brightness levels and dimming mode are firmware-derived runtime configuration. Hardware registers retain OVP/sync/brightness until reset.

## Dependencies and Integration Points
The driver depends on I2C, regmap, fwnode properties, GPIO, PWM, and the backlight core. It supports firmware properties for dimming mode, levels, sync, and over-voltage protection.

## Risks
The analog bit-packing loop iterates through bit index 5 even though the analog range is 0-31; the extra bit is zero for valid values but would matter if validation changed. PWM mode relies on a nonempty monotonic levels table and a valid max-brightness index. Enable sequencing depends on the `status` state machine matching hardware auto-off behavior.

## Test Signals
Test analog and PWM modes, property validation, default level generation, zero/nonzero transitions, first-power-on behavior, PWM duty calculation, OVP/sync register writes, enable GPIO, and regmap/PWM failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/mp3309c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/mt6370-backlight.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/mt6370-backlight.c

## Purpose
This platform child driver controls the MediaTek/Richtek MT6370/MT6371/MT6372 backlight block through the parent regmap.

## Important APIs, Types, and Functions
`struct mt6370_priv` stores brightness bit masks/shifts, default max brightness, backlight, device, optional enable GPIO, and parent regmap. `mt6370_check_vendor_info()` reads hardware vendor bits and verifies they match the compatible string, then selects 11-bit common or 14-bit MT6372 brightness encoding. `mt6370_init_backlight_properties()` parses PWM hysteresis, OVP, OCP, max/default brightness, exponential mode, and channel-use properties. `mt6370_bl_update_status()` writes split brightness bytes, drives optional GPIO, and toggles enable bit.

## Control Flow
Probe gets the parent regmap, validates vendor info, obtains optional enable GPIO, initializes hardware properties and backlight props, registers the backlight, applies brightness, and stores driver data. Remove sets brightness zero and updates hardware.

## State and Persistence
Encoding parameters are derived once at probe from hardware and match data. Backlight properties and hardware configuration are volatile runtime state held in memory and registers.

## Dependencies and Integration Points
The driver depends on platform MFD instantiation, parent regmap, GPIO, device properties, bitfield helpers, and the backlight core. It matches `mediatek,mt6370-backlight` and `mediatek,mt6372-backlight`.

## Risks
A wrong compatible string intentionally fails probe after reading hardware vendor info. `mediatek,bled-channel-use` is mandatory and must be 1-15. Register update masks use `val` as both mask and value for some optional fields, so properties that are absent leave those bits untouched rather than cleared.

## Test Signals
Test common vs MT6372 vendor detection, wrong compatible rejection, mandatory channel property, max/default clamping, exponential scale, OVP/OCP/PWM property mapping, GPIO enable, brightness readback, and remove zeroing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/mt6370-backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/omap1_bl.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/omap1_bl.c

## Purpose
This platform driver controls OMAP1 LCD backlight intensity and enable state through board-specific LCD panel callbacks.

## Important APIs, Types, and Functions
`struct omap_backlight` stores the backlight device, saved power state, current enabled state, and `omap_backlight_config` from platform data. `omapbl_send_intensity()` and `omapbl_send_enable()` call panel callbacks. `omapbl_enable()` updates enable state and hardware. `omapbl_update_status()` computes blanking, sends intensity, and toggles enable. PM callbacks save power and force off during suspend, then restore.

## Control Flow
Probe requires platform data, allocates state, registers a raw max-255 backlight, initializes brightness to the configured default, powers on, stores driver data, and applies status. Runtime updates blank or enable the backlight based on backlight core state.

## State and Persistence
The driver caches `enabled` and saved `powermode`; hardware intensity/enable are external board callbacks. No persistent storage exists.

## Dependencies and Integration Points
It depends on `linux/platform_data/omap1_bl.h`-style platform data, platform devices, and the backlight core. It has no DT parser.

## Risks
All hardware work is delegated to platform callbacks, so missing or faulty callbacks break control. Suspend changes `props.power` directly and must restore it correctly. Enable and intensity are separate callbacks, so inconsistent callback behavior can leave LEDs on at stale intensity.

## Test Signals
Test missing platform data, default brightness, update blanking behavior, enable callback transitions, suspend/resume restoring power state, and callback error assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/omap1_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/otm3225a.c -->
# sources/distributed-fs/ceph-client/drivers/video/backlight/otm3225a.c

## Purpose
This SPI LCD driver initializes an ORISE OTM3225A TFT LCD controller and controls display on/off state. Pixel data is supplied through a separate 16-bit RGB interface.

## Important APIs, Types, and Functions
`struct otm3225a_data` stores SPI, LCD device, and power state. `struct otm3225a_spi_instruction` describes register/value/delay entries. Static arrays define display initialization, enabling RGB interface, display-off, and display-on sequences. `otm3225a_write()` sends each register through index opcode `0x70` and data opcode `0x72`. `otm3225a_set_power()` chooses display-on/off sequences based on the LCD power value.

## Control Flow
Probe allocates state, registers an LCD device named after the SPI device, stores driver data, logs initialization, sends the full init sequence, then switches to RGB interface. Power changes are no-ops when the requested state matches cached power; otherwise values greater than `LCD_POWER_ON` send display-off and values at/on send display-on.

## State and Persistence
`dd->power` is the only software state. Controller registers persist while powered. The driver does not implement remove, shutdown, or PM hooks.

## Dependencies and Integration Points
The driver depends on SPI and the LCD class. It is an SPI driver named `otm3225a` and expects an external RGB controller to provide frame data.

## Risks
`spi_write()` return values are ignored throughout initialization and power sequencing. Probe does not explicitly set `dd->power` after initialization, so the cached state starts at zero from allocation and may not reflect the initialized display state. Lack of shutdown/remove hooks can leave the panel on during detach or reboot.

## Test Signals
Test init sequence write ordering/delays, RGB-interface enable sequence, sysfs power off/on, cached power behavior after probe, SPI write failure instrumentation, and reboot/remove expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/backlight/otm3225a.c -->
