<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ad714x.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/ad714x.c

Purpose: bus-neutral core for Analog Devices AD7142/AD7143/AD7147/AD7148 capacitive touch controllers. It turns platform-described button, slider, wheel, and touchpad stages into Linux input devices and exports `ad714x_probe()` for I2C/SPI wrappers.

Important APIs/types/functions: `ad714x_probe()` allocates the shared `struct ad714x_chip`, detects the part ID, writes stage/system configuration, registers input devices, and requests a threaded IRQ. `ad714x_interrupt_thread()` reads low/high/conversion interrupt status and runs button/slider/wheel/touchpad state machines. Helpers calculate peak stage, absolute position, IIR-filtered position, and threshold-vs-conversion interrupt mode.

Control flow and state: probe requires an IRQ and `struct ad714x_platform_data`, then lays out software state arrays after the chip object. Runtime state is kept in `l_state`, `h_state`, `c_state`, per-stage ADC/ambient/sensor arrays, per-widget `IDLE/JITTER/ACTIVE/SPACE` state, and filtered positions. IRQ handling is serialized by `ad714x->mutex`.

State and persistence behavior: persistent hardware state is the controller register map programmed from platform data. Driver state is in memory only. Suspend writes shutdown bits into `AD714X_PWR_CTRL`; resume restores the configured power-control value and drains interrupt status so edge-triggered IRQs can fire again.

Dependencies and integration points: depends on `linux/input/ad714x.h` platform descriptors, the local `ad714x.h` bus callback ABI, Linux input, threaded IRQs, device-managed allocation, and PM ops exported as `ad714x_pm`. Bus wrappers supply endian-safe `read` and `write` callbacks.

Risks: platform stage ranges are trusted; bad ranges can create invalid bit masks, divide by zero in position/endpoint calculations, or read/write wrong stages. Touchpad endpoint calculations divide by adjacent sensor values. Input registration loops use the first platform descriptor pointer in each class, so multi-widget coordinate variation needs review. Register I/O return values are mostly ignored.

Test signals: verify part-ID detection failures, stage register programming, IRQ status decoding, button press/release, slider/wheel/touchpad touch-release transitions, suspend/resume wake behavior, and boundary platform data for stage ranges and max coordinates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ad714x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ad714x.h -->
## sources/distributed-fs/ceph-client/drivers/input/misc/ad714x.h

Purpose: private bus-interface header for the AD714x core. It defines the shared chip object and the callback contract used by bus-specific drivers.

Important APIs/types/functions: `STAGE_NUM` fixes the controller model at 12 CDC stages. `ad714x_read_t` and `ad714x_write_t` abstract register access. `struct ad714x_chip` stores interrupt status, ADC/ambient/sensor arrays, platform and software state pointers, bus callbacks, IRQ, device, mutex, product/version, and a cacheline-aligned transfer buffer. It declares `ad714x_probe()` and `ad714x_pm`.

Control flow and state: the header contains no executable flow, but it is the ABI between bus wrappers and `ad714x.c`. The core owns all state after `ad714x_probe()` returns.

State and persistence behavior: all fields are volatile driver/runtime state except platform configuration referenced through `hw`. Hardware persistence is controlled by the implementation file.

Dependencies and integration points: includes `linux/pm.h` and `linux/types.h`, forward-declares platform/core structures, and is included by AD714x bus glue and the core.

Risks: callback implementers must honor register width, array length, and sleepability expected by the core. `xfer_buf[16]` is a convenience buffer but the core can request up to stage-sized reads, so wrappers must avoid overflow if using it.

Test signals: compile both bus and core users together, exercise read/write callback error paths, and confirm PM ops link for bus drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ad714x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-i2c.c

Purpose: I2C/SMBus transport wrapper for the ADXL345/ADXL346 accelerometer core.

Important APIs/types/functions: `adxl34x_smbus_read()`, `adxl34x_smbus_write()`, `adxl34x_smbus_read_block()`, and `adxl34x_i2c_read_block()` implement `struct adxl34x_bus_ops`. `adxl34x_i2c_probe()` checks byte-data support, chooses SMBus block read when available or raw I2C block read otherwise, then calls `adxl34x_probe()`.

Control flow and state: probe performs adapter capability validation, delegates all device initialization to the core, and stores the returned core pointer with `i2c_set_clientdata()`. The module registers an `i2c_driver` with I2C IDs and OF compatibles.

State and persistence behavior: this file owns no sensor state beyond client driver data. Register state, sysfs attributes, input events, and PM behavior are handled in `adxl34x.c`.

Dependencies and integration points: depends on I2C/SMBus APIs, OF matching for `adi,adxl345` and deprecated `adi,adxl34x`, the local `adxl34x.h` ABI, and core `adxl34x_groups`/`adxl34x_pm`.

Risks: the raw I2C block fallback only checks receive length, while the preceding address send may return a short positive count that is not rejected. Device tree lists only ADXL345 because ADXL346 is runtime-detected.

Test signals: test adapters with and without SMBus block support, missing IRQ, device-ID mismatch propagated from the core, OF autoloading, and sysfs group/PM attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-spi.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-spi.c

Purpose: SPI transport wrapper for the ADXL345/ADXL346 accelerometer core.

Important APIs/types/functions: SPI command macros encode read/write and multi-byte accesses. `adxl34x_spi_read()`, `adxl34x_spi_write()`, and `adxl34x_spi_read_block()` implement `adxl34x_bus_ops`. `adxl34x_spi_probe()` enforces a 5 MHz maximum, sets the FIFO delay flag for SPI clocks above 1.5 MHz, and calls `adxl34x_probe()`.

Control flow and state: probe validates bus speed, delegates initialization to the common core, and stores the returned pointer with `spi_set_drvdata()`. The registered `spi_driver` attaches common sysfs groups and sleep PM ops.

State and persistence behavior: no independent persistence. The SPI speed-derived `fifo_delay_default` influences core FIFO-drain timing for multi-sample reads.

Dependencies and integration points: depends on Linux SPI helpers, the local `adxl34x.h` transport ABI, and the core's input/sysfs/PM exports.

Risks: invalid board SPI mode or IRQ wiring is only caught indirectly. High-speed FIFO correctness depends on the 3 us delay in the core plus controller chip-select behavior.

Test signals: probe at valid and excessive SPI clock rates, multi-byte axis reads, FIFO watermark operation above and below 1.5 MHz, suspend/resume, and module binding by SPI device name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.c

Purpose: bus-neutral ADXL345/ADXL346 three-axis accelerometer input driver. It configures sensor thresholds, FIFO/data-ready interrupts, tap/free-fall/activity/orientation events, calibration sysfs, and power transitions.

Important APIs/types/functions: `struct adxl34x` stores device, input, platform data, calibration, saved axes, disabled/opened/suspended flags, IRQ, model, interrupt mask, and bus ops. `adxl34x_probe()` performs detection, input setup, register programming, IRQ request, and exports sysfs groups. `adxl34x_irq()` handles tap, double tap, free fall, activity/inactivity, orientation, FIFO/data samples, and overrun. Sysfs attributes are `disable`, `calibrate`, `rate`, `autosleep`, and `position`.

Control flow and state: probe copies platform data or defaults, verifies `DEVID`, configures input capabilities based on EV_ABS/EV_REL and optional events, writes all threshold/rate/format/FIFO registers, and enables selected interrupts. Input open/close toggles measurement mode unless disabled or suspended. IRQ reads status, reports event keys, drains one or more axis samples, updates `saved`, applies software calibration, and syncs input.

State and persistence behavior: runtime state includes calibration (`hwcal`, `swcal`), latest raw axes, orientation debounce values, and power flags. Hardware offset registers persist until reset; sysfs writes update registers immediately but are not stored across module/device removal.

Dependencies and integration points: uses Linux input, IRQ, sysfs attribute groups, device PM, platform data from `linux/input/adxl34x.h`, and bus operations from `adxl34x.h`. I2C and SPI wrappers call the exported `adxl34x_probe()`.

Risks: many register writes ignore return values through `AC_WRITE`. Platform data values are trusted for event codes, thresholds, data format, FIFO mode, and orientation arrays. Calibration depends on previously saved data, so writing `calibrate` before a sample can produce misleading offsets. FIFO sample count adds one to `FIFO_STATUS` entries, which should be validated against hardware behavior.

Test signals: verify default and custom platform data, device ID rejection, ABS and REL reporting, calibration sysfs math, disable/autosleep/rate sysfs behavior, tap/double-tap/free-fall/activity/orientation events, FIFO drain timing, and open/close/suspend/resume transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.h -->
## sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.h

Purpose: private transport ABI for the ADXL34x core and bus wrappers.

Important APIs/types/functions: `struct adxl34x_bus_ops` provides bus type, single-register read/write, and block-read callbacks. The header declares exported `adxl34x_probe()`, `adxl34x_pm`, and `adxl34x_groups`.

Control flow and state: no executable code; bus drivers provide callbacks and receive an opaque `struct adxl34x *` from the core.

State and persistence behavior: this file stores no state. Persistence is in sensor registers and core runtime structures.

Dependencies and integration points: used by `adxl34x.c`, `adxl34x-i2c.c`, and `adxl34x-spi.c`; depends on `struct device` and input/PM declarations from included kernel headers in users.

Risks: bus callbacks must match the core's signed/unsigned return expectations and must fill little-endian axis buffers for block reads.

Test signals: build all transports, check symbol exports under module builds, and inject read/write callback failures in probe and IRQ paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/apanel.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/apanel.c

Purpose: Fujitsu LifeBook application-panel driver for SMBus-accessible application/CD buttons and optional mail LED discovered from a BIOS signature.

Important APIs/types/functions: `apanel_init()` maps the 0xF0000 BIOS area, scans for `FJKEYINF`, records device-chip capabilities, and registers the I2C driver. `apanel_probe()` creates a polled input device, keymap, and optional LED class device. `apanel_poll()` reads a word from SMBus, clears the latch by writing zero, and emits press-release key events. `mail_led_set()` writes the LED bit.

Control flow and state: module init discovers one SMBus slave and feature set, then I2C probe clears the command register and registers input polling at 1000 ms. Polling decodes bit positions into `KEY_MAIL`, browser/program keys, and CD controls.

State and persistence behavior: static `device_chip[]` persists BIOS-discovered feature support for module lifetime. Input keymap is per-device. Mail LED state is hardware-backed and forced off during shutdown.

Dependencies and integration points: uses low BIOS memory mapping, I2C SMBus word accesses, input polling, LED class, and DMI aliases for Fujitsu LifeBook systems.

Risks: BIOS parsing trusts legacy table layout and supports only one SMBus slave. SMBus read errors are silently ignored in polling. The driver uses legacy platform discovery rather than firmware nodes.

Test signals: test BIOS signature absent/present, duplicate/unknown table entries, app-only and app+CD key maps, LED registration and shutdown-off behavior, and polling under SMBus errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/apanel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ariel-pwrbutton.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/ariel-pwrbutton.c

Purpose: Dell Wyse 3020 "Ariel" EC input driver that reports the EC power button over SPI.

Important APIs/types/functions: `struct ec_input_response` models the five-byte EC response. `ec_input_read()` sends the fixed SPI request. `ec_input_interrupt()` filters duplicate counters, accepts keyboard data message types, translates scan codes `0x74` and `0xf4` to KEY_POWER press/release, and logs unknown codes. `ariel_pwrbutton_probe()` registers input and IRQ.

Control flow and state: probe requires an IRQ, registers a `Power Button` input device, reads the initial message counter, and installs a threaded IRQ. Each IRQ performs one SPI transfer and reports all response bytes up to the encoded size.

State and persistence behavior: only `msg_counter` persists in memory to suppress stale messages. The hardware EC owns scan state.

Dependencies and integration points: depends on SPI, OF compatible `dell,wyse-ariel-ec-input`, SPI device ID `wyse-ariel-ec-input`, threaded IRQs, and Linux input.

Risks: response size/type/counter are trusted after bit extraction. Unknown EC protocol changes are only logged. No explicit locking protects `msg_counter`, relying on threaded IRQ serialization.

Test signals: verify missing IRQ failure, initial counter read, duplicate message suppression, press/release scan codes, unknown message filtering, and SPI transfer errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ariel-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/arizona-haptics.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/arizona-haptics.c

Purpose: memless force-feedback haptics driver for Wolfson/Cirrus Arizona MFD devices, controlling haptic intensity through regmap and ASoC DAPM.

Important APIs/types/functions: `struct arizona_haptics` holds the MFD pointer, input device, work item, mutex, and intensity. `arizona_haptics_play()` maps FF_RUMBLE magnitude/direction to device intensity and schedules work. `arizona_haptics_work()` writes intensity, enables/disables haptic control, and syncs the `HAPTICS` DAPM pin. `arizona_haptics_close()` cancels work and disables the pin.

Control flow and state: platform probe obtains parent `struct arizona`, configures actuator polarity/type, creates a memless FF input device, and registers it. Playback callbacks avoid direct register and DAPM work in input context by using a workqueue item.

State and persistence behavior: `intensity` is the only runtime playback state. Hardware haptic control and DAPM pin state persist until changed, with close forcing off.

Dependencies and integration points: depends on Arizona MFD core/pdata/registers, regmap, ASoC DAPM, Linux input FF, and platform device registration under `arizona-haptics`.

Risks: playback fails if `arizona->dapm` is unavailable. Workqueue operations are not explicitly locked around `intensity`, so rapid updates rely on simple byte stores and ordered work execution. Error paths can leave partially enabled hardware if later DAPM sync fails.

Test signals: test FF_RUMBLE strong magnitude scaling for both actuator modes, zero magnitude stop, missing DAPM context, close-time cancellation, and register update failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/arizona-haptics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atc260x-onkey.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/atc260x-onkey.c

Purpose: power-button input driver for Actions Semi ATC2603C and ATC2609A PMICs.

Important APIs/types/functions: per-chip `struct atc260x_onkey_params` maps register bits. `atc2603x_onkey_hw_init()` configures pending bits, interrupt enables, press time, and long-press reset behavior. `atc260x_onkey_irq()` reports KEY_POWER down, disables PMIC key interrupts, and starts release polling. `atc260x_onkey_query()` polls the key-down bit and reports release when cleared.

Control flow and state: probe reads parent `reset-time-sec`, selects chip parameters, creates input with open/close callbacks, requests a threaded IRQ, keeps it disabled until input open, initializes hardware, and enables wakeup. IRQ down events are hardware-driven; release is simulated by delayed work every 200 ms because the PMIC interrupts only on assertion.

State and persistence behavior: runtime state includes delayed work, IRQ number, parent PMIC pointer, and selected params. Hardware reset/press timing persists in PMIC registers after initialization.

Dependencies and integration points: depends on ATC260x MFD core, regmap, device properties, platform IRQs, Linux input, delayed work, and wakeup integration.

Risks: register update failures during release cleanup are not propagated. Long-press reset configuration accepts only 0 or 6-12 seconds from firmware; wrong firmware properties can disable reset unexpectedly. Open/close controls IRQ delivery, so userspace not opening the input device suppresses events.

Test signals: test ATC2603C and ATC2609A bitfield programming, reset-time property validation, IRQ down report, delayed release polling, open/close IRQ enablement, and wake-from-suspend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atc260x-onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ati_remote2.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/ati_remote2.c

Purpose: USB input driver for the ATI/Philips Remote Wonder II RF remote, including mouse pad motion, per-mode key maps, channel/mode filtering, autosuspend, reset, and sysfs configuration.

Important APIs/types/functions: `struct ati_remote2` owns two USB interfaces/endpoints/URBs, coherent buffers, input device, per-mode keycode table, channel/mode masks, current mode, and flags. `ati_remote2_probe()` claims both interfaces, initializes URBs, configures receiver channel, and registers input. `ati_remote2_complete_mouse()` and `ati_remote2_complete_key()` resubmit interrupt URBs after decoding. `getkeycode`/`setkeycode` expose per-mode remapping.

Control flow and state: probe handles only interface 0, claims interface 1, validates endpoints, and creates separate interrupt URBs for mouse and key reports. Input open resumes USB and submits URBs unless suspended; close kills them. Completion handlers parse channel/mode, filter masks, report REL_X/Y or key press/release/repeat, and resubmit. Suspend/reset paths kill and restart URBs under a global mutex.

State and persistence behavior: module parameters seed `channel_mask` and `mode_mask`; sysfs can update runtime masks, with channel changes also sent by vendor control request. Keymaps live in memory and can be changed via input keymap APIs. USB receiver channel setting must be restored after reset resume.

Dependencies and integration points: depends on USB input, coherent DMA URBs, USB autosuspend, vendor control messages, input keymap APIs, module parameters, and device attribute groups.

Risks: uses a global mutex across all devices. Some error paths log and continue resubmitting URBs. Mode-key filtering has device-specific quirks. `setkeycode` can set invalid keycodes if input core does not prevalidate. Two-interface ownership makes disconnect/reset ordering important.

Test signals: verify two-interface probing, endpoint validation, open/close URB lifecycle, channel/mode module and sysfs masks, vendor channel setup, mouse reports, key press/release/repeat timing, key remapping, suspend/resume, reset_resume, and disconnect while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ati_remote2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atlas_btns.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/atlas_btns.c

Purpose: ACPI address-space based button driver for Atlas wallmount touchscreen systems.

Important APIs/types/functions: `atlas_acpi_button_probe()` allocates a global input device, builds an F1-F9 keymap, registers it, and installs ACPI address-space handler `0x81`. `acpi_atlas_button_handler()` treats ACPI writes as scan events and reports press/release based on address bits. Remove unregisters the handler and input device.

Control flow and state: ACPI firmware writes to the custom region; the handler extracts low-nibble scan code and bit 4 key state, reports `MSC_SCAN`, key state, and sync. Probe/remove are platform-driver callbacks matched by ACPI ID `ASIM0000`.

State and persistence behavior: global `atlas_keymap` and `input_dev` persist for the device lifetime. Firmware owns button state; the driver reports events immediately without debouncing.

Dependencies and integration points: depends on ACPI companion device, ACPI address-space handler APIs, Linux input, and platform driver binding.

Risks: global input pointer assumes one device. Handler ignores reads and returns `AE_BAD_PARAMETER`. ACPI callbacks can race with remove if firmware still accesses the region after handler removal errors.

Test signals: test ACPI ID binding, address-space install/remove, all F1-F9 scan codes, key up/down address bit behavior, unexpected ACPI read handling, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atlas_btns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atmel_captouch.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/atmel_captouch.c

Purpose: I2C input driver for an ATmega-based capacitive touch-button controller using a custom register protocol.

Important APIs/types/functions: `struct atmel_captouch_device` stores client, input, button count, keycodes, previous button state, and transfer buffer. `atmel_read()` sends register/length and validates the echoed register in the response. `atmel_captouch_isr()` reads `REG_KEY_STATE`, diffs it against `prev_btn`, and reports changed keys. Probe reads firmware keycodes and requests IRQ.

Control flow and state: probe verifies I2C functionality, reads the initial key state, allocates input, reads `autorepeat` and keycode array from device tree, registers input, and installs a threaded IRQ. IRQ reports only changed bits and then syncs.

State and persistence behavior: `prev_btn` persists in memory to detect edges. Key mapping is read from firmware and exposed through input keycode metadata. Hardware thresholds/reference/delta registers are defined but not configured by this driver.

Dependencies and integration points: depends on I2C transfer APIs, OF properties, Linux input, and threaded IRQs. Compatible is `atmel,captouch`.

Risks: `of_property_count_u32_elems(node, "linux,keymap")` is used while the array read uses `linux,keycodes`, which may be a property-name mismatch. Negative element counts are not checked before array read. No explicit `client->irq` validation before requesting IRQ.

Test signals: test valid/invalid DT key arrays, initial state read failure, echoed-register mismatch, changed-button reporting for multiple simultaneous keys, autorepeat flag, missing IRQ, and I2C short transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atmel_captouch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/aw86927.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/aw86927.c

Purpose: I2C memless haptics driver for AWINIC AW86927/AW86938 LRA devices. It initializes analog/boost/brake/PWM settings, uploads a built-in sine waveform to SRAM, and exposes FF_RUMBLE playback.

Important APIs/types/functions: `struct aw86927_data` stores model, work item, device, input, client, regmap, reset GPIO, and current level. `aw86927_detect()` reads big-endian chip ID. `aw86927_haptic_init()` programs device tuning. `aw86927_ram_init()` uploads waveform header/data. `aw86927_haptics_play()` updates level and schedules `aw86927_haptics_play_work()`. `aw86927_irq()` reports protection and playback interrupts.

Control flow and state: probe creates regmap/input/reset GPIO, performs hardware and software reset, detects model, configures IRQ mode/masks, requests threaded IRQ, creates memless FF, enters standby, initializes haptic registers, uploads SRAM waveform, and registers input. Playback changes schedule work; nonzero level stops current playback, selects RAM mode, sets wave sequence/loop/gain, and starts GO; zero stops and waits for standby.

State and persistence behavior: `level` persists across callbacks to avoid restarts at the same magnitude. SRAM waveform and analog/boost configuration persist until reset. Close cancels work and stops playback.

Dependencies and integration points: depends on I2C, regmap, reset GPIO, Linux input FF, threaded IRQs, and OF compatible `awinic,aw86927`.

Risks: probe requests IRQ unconditionally using `client->irq`, so missing IRQ may fail late. Playback work has no explicit mutex around `level` and hardware sequencing. SRAM and tuning constants are fixed; board-specific actuator differences are not modeled. Some model-specific masks share AW86927 register names for AW86938.

Test signals: verify reset timing, chip-ID detection for both IDs, SRAM upload contents, FF_RUMBLE start/stop/close, protection IRQ logs, missing reset GPIO/IRQ handling, and regmap error propagation through probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/aw86927.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/axp20x-pek.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/axp20x-pek.c

Purpose: power enable key input and timing sysfs driver for X-Powers AXP20x/AXP221-family PMICs.

Important APIs/types/functions: `struct axp20x_pek` stores parent MFD, input, timing info, and rising/falling IRQs. `axp20x_pek_irq()` maps `PEK_DBF` to KEY_POWER down and `PEK_DBR` to release. Sysfs `startup` and `shutdown` show/store nearest supported timing values through `AXP20X_PEK_KEY`. PM ops manage IRQ wake and AXP288 resume-noirq interrupt clearing.

Control flow and state: probe allocates state, optionally registers input depending on AXP288/Cherry Trail duplicate-button detection, selects timing table from platform ID, and exposes attributes. Input setup converts regmap IRQ IDs to virtual IRQs and requests both edges.

State and persistence behavior: hardware PEK timing values persist in PMIC registers. Runtime state tracks IRQ numbers and selected timing table. Wakeup capability is enabled for the platform device.

Dependencies and integration points: depends on AXP20x MFD/regmap IRQ controller, ACPI duplicate-button detection helpers, Linux input, sysfs attribute groups, and PM wake APIs.

Risks: if input registration is skipped, suspend/resume still assumes IRQ fields are valid, which depends on platform path expectations. Store rounds requested times to nearest supported value, which may surprise users. Regmap update errors are returned as `-EINVAL`, losing detail.

Test signals: test AXP20x and AXP221 timing maps, sysfs round-trip values, press/release IRQs, AXP288 duplicate suppression, suspend wake/non-wake IRQ handling, and AXP288 resume-noirq interrupt clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/axp20x-pek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/bma150.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/bma150.c

Purpose: I2C input driver for Bosch BMA150/SMB380/BMA023 accelerometers, supporting interrupt-driven or polled ABS_X/Y/Z reporting.

Important APIs/types/functions: `struct bma150_data` stores client, input, and current mode. Register helpers update bitfields and write bytes while temporarily disabling IRQ around writes. `bma150_initialize()` resets the chip, configures bandwidth/range and optional motion/high-g/low-g interrupts, then sleeps the device. `bma150_report_xyz()` reads six data bytes and sign-extends 10-bit axes.

Control flow and state: probe checks I2C support and chip ID, applies platform or default config, initializes hardware, creates input with open/close PM hooks, sets ABS axes, chooses polling if no IRQ, registers input, optionally requests threaded IRQ, stores clientdata, and enables runtime PM. Open wakes normal mode; close runtime-suspends and sleeps.

State and persistence behavior: configured range, bandwidth, thresholds, and interrupt settings persist in sensor registers until reset. Runtime `mode` mirrors normal/sleep state. No calibration state is stored.

Dependencies and integration points: depends on I2C SMBus/block APIs, `linux/bma150.h` platform data, input polling, threaded IRQs, runtime/system PM, and I2C class HWMON matching.

Risks: `bma150_write_byte()` disables IRQ around writes but not around read-modify-read races from other contexts. Open error after `pm_runtime_get_sync()` can leak runtime PM usage. Probe registers input before requesting IRQ, leaving a small initialized-but-no-IRQ failure window handled by devm cleanup.

Test signals: test chip-ID rejection, platform GPIO config callback, default config, IRQ and polling modes, axis decoding/sign extension, open/close runtime PM, system suspend/resume, and threshold/range programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/bma150.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cm109.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cm109.c

Purpose: USB input and buzzer driver for CM109-based VoIP handsets, with selectable phone keymaps and matrix scanning over HID-like control/interrupt packets.

Important APIs/types/functions: `struct cm109_dev` owns USB device/interface, interrupt/control URBs and coherent packets, request object, submission flags, buzzer state, PM/reset flags, keymap, scan state, and cached GPI. Keymap functions support `kip1000`, `gtalk`, `usbph01`, and `atcom`. `cm109_urb_irq_callback()` decodes special keys and matrix columns. `cm109_urb_ctl_callback()` chains control and interrupt URBs. Input `event` handles `SND_TONE`/`SND_BELL`.

Control flow and state: module init selects the keymap from the `phone` parameter before registering USB. Probe validates an interrupt-in endpoint, allocates input/URBs/coherent buffers/control request, initializes key bits and sound bits, and registers input. Open submits an initial control packet that starts the IRQ/control scan loop; close stops traffic and turns buzzer off. PM/reset paths stop and restore traffic under `pm_mutex`.

State and persistence behavior: runtime scan state includes current key, keybit column mask, cached GPI, buzzer state, and pending URB flags protected by spinlock or mutex. No hardware state is persisted except current output packet values while open.

Dependencies and integration points: depends on USB HID-class interface matching for C-Media VID/PID, input key/sound events, coherent DMA URBs, USB autosuspend, module parameters, spinlocks, and PM callbacks.

Risks: control URB uses `USB_REQ_SET_CONFIGURATION` for class output, which is device-specific and fragile. Matrix scanning depends on strict URB chaining and pending flags. Unsupported `phone` parameter prevents module load. Error handling in callbacks logs but continues.

Test signals: test all keymap selections and unsupported parameter, probe endpoint validation, open/close scan loop, special mute/volume keys, matrix key press/release, buzzer EV_SND handling, suspend/resume, pre/post reset, and disconnect while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cm109.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x.c

Purpose: bus-neutral VTI CMA3000-D0x accelerometer core that reports ABS_X/Y/Z acceleration and ABS_MISC free-fall events.

Important APIs/types/functions: `struct cma3000_accl_data` stores bus ops, platform data, device, input, conversion scale, IRQ, range, mode, mutex, opened, and suspended. `cma3000_init()` validates platform data/IRQ, resets hardware, reads revision, requests threaded IRQ, and registers input. `cma3000_thread_irq()` reads interrupt status and axes, updates scale from CTRL mode/range, decodes signed mg values, and reports input. `cma3000_suspend()/resume()` and `cma3000_exit()` are exported.

Control flow and state: bus wrapper calls `cma3000_init()` with callbacks. Input open powers on unless suspended; close powers off. IRQ does all sampling and event reporting. Power-on writes motion/free-fall thresholds and mode/range with bus modifier.

State and persistence behavior: hardware mode, range, motion threshold/timer, and free-fall threshold persist while powered. Runtime state tracks open/suspended flags and selected platform range/mode.

Dependencies and integration points: depends on `linux/input/cma3000.h` platform data, local bus ops, input, IRQ, and exported symbols for bus modules.

Risks: platform data and mode/range are required; no firmware fallback exists. Register write helper errors during reset/power configuration are partly ignored through macros. Scale table returns zero for invalid modes and causes IRQ_NONE, so bad mode can suppress events.

Test signals: test missing platform data/IRQ, reset parity error, revision read, mode/range validation, free-fall reporting, axis mg conversion in 2G and 8G modes, open/close power control, and suspend/resume while open and closed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x.h -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x.h

Purpose: private bus ABI for the CMA3000-D0x accelerometer core.

Important APIs/types/functions: `struct cma3000_bus_ops` carries bus type, control-mode bits, and read/write callbacks with diagnostic message strings. The header declares exported `cma3000_init()`, `cma3000_exit()`, `cma3000_suspend()`, and `cma3000_resume()`.

Control flow and state: no executable flow. Bus wrappers call init/exit/PM helpers and pass the opaque `struct cma3000_accl_data *`.

State and persistence behavior: no state in the header; callback implementations and core manage hardware/runtime state.

Dependencies and integration points: includes Linux input/types and is shared by `cma3000_d0x.c` and bus files such as the I2C wrapper.

Risks: bus callbacks must return negative errors and raw register values exactly as the core expects. `ctrl_mod` must match the physical bus mode bits programmed into the CTRL register.

Test signals: compile with each transport, verify PM symbol use, and inject callback failures during reset, power-on, and IRQ sampling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x_i2c.c

Purpose: I2C transport wrapper for the CMA3000-D0x accelerometer core.

Important APIs/types/functions: `cma3000_i2c_set()` and `cma3000_i2c_read()` wrap SMBus byte writes/reads and log message-specific errors. `cma3000_i2c_bops` sets `BUS_I2C` and I2C control mode. Probe delegates to `cma3000_init()`, remove calls `cma3000_exit()`, and PM calls core suspend/resume.

Control flow and state: probe creates core state and stores it in clientdata. Remove and PM retrieve that pointer and delegate. The module registers an I2C driver for `cma3000_d01`.

State and persistence behavior: this file owns no independent state beyond clientdata. Core controls hardware mode and input state.

Dependencies and integration points: depends on I2C SMBus byte APIs, local `cma3000_d0x.h`, `linux/input/cma3000.h`, and module I2C registration.

Risks: no explicit I2C functionality check is performed before SMBus operations. PM assumes clientdata exists and core init completed.

Test signals: test read/write error logging, probe failure propagation, remove cleanup, suspend/resume delegation, and binding by I2C ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cma3000_d0x_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cobalt_btns.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cobalt_btns.c

Purpose: polled memory-mapped button driver for Cobalt systems.

Important APIs/types/functions: `struct buttons_dev` stores keymap, debounce counters, and mapped register. `handle_buttons()` reads the status register, inverts/shifts it, debounces each bit using a count threshold, and reports `MSC_SCAN` plus key state. Probe maps the memory resource and registers a polled input device.

Control flow and state: platform probe maps IORESOURCE_MEM, copies the static keymap, sets input capabilities, installs polling at 30 ms, and registers input. Polling reports press after three consecutive active reads and release after an inactive read following an accepted press.

State and persistence behavior: debounce counters persist in memory. Hardware button state is read-only from the mapped register.

Dependencies and integration points: depends on platform resources, MMIO `readl`, input polling, and platform alias `Cobalt buttons`.

Risks: uses `devm_ioremap()` rather than resource-managed exclusive mapping. Status mask constant is defined but not used. Polling assumes active-low bits in the top byte and fixed key count.

Test signals: test resource absence, register mapping failure, debounce press/release timing, all key bits, MSC_SCAN values, and polling interval behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cobalt_btns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cpcap-pwrbutton.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cpcap-pwrbutton.c

Purpose: Motorola CPCAP PMIC power-button input driver.

Important APIs/types/functions: `struct cpcap_power_button` stores parent regmap, input device, and device pointer. `powerbutton_irq()` calls `cpcap_sense_virq()` to read current button sense, emits KEY_POWER, syncs input, and marks a wakeup event. Probe gets platform IRQ, parent regmap, input device, threaded IRQ, and enables wakeup.

Control flow and state: platform probe wires a single IRQ to a threaded handler. IRQ reads the live PMIC sense value rather than relying on edge polarity and reports it directly.

State and persistence behavior: no driver-side button state is retained. Wakeup capability persists for device lifetime.

Dependencies and integration points: depends on Motorola CPCAP MFD helpers, regmap, OF compatible `motorola,cpcap-pwrbutton`, platform IRQs, Linux input, and PM wakeup.

Risks: `devm_kmalloc()` leaves structure fields uninitialized until assigned, but all fields are set before use. Sense-read failures are logged but still return IRQ_HANDLED. No debounce is performed in this layer.

Test signals: test missing IRQ/regmap, press and release sense values, wakeup event generation, threaded IRQ request failure, and OF matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cpcap-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cs40l50-vibra.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/cs40l50-vibra.c

Purpose: advanced force-feedback haptic input driver for Cirrus CS40L50 MFD devices, supporting ROM/RAM/open-wavetable effects, GPIO trigger mapping, and ordered playback commands to the DSP.

Important APIs/types/functions: `struct cs40l50_vibra` stores device, regmap, input, ordered workqueue, uploaded effect list, and DSP register/command description. `cs40l50_add()` uploads or updates FF_CUSTOM periodic effects through `cs40l50_add_worker()`. `cs40l50_playback()` queues start/stop workers. `cs40l50_erase()` removes mappings/effects and deletes OWT entries. Helpers select bank/index, configure GPIO triggers, and upload OWT headers/data.

Control flow and state: probe gets parent MFD data, creates an input FF device with one effect slot, installs upload/playback/erase callbacks, initializes the effect list, allocates an ordered high-priority workqueue, and registers input. Upload and erase use stack work plus flush to provide synchronous input-core semantics while serializing with playback. Playback allocates async work and writes DSP commands for the requested count or stop command.

State and persistence behavior: uploaded effects are tracked in `effect_head`; OWT uploads and GPIO mappings persist in DSP/register state until erased or reset. Runtime PM is acquired around DSP operations and released with autosuspend.

Dependencies and integration points: depends on CS40L50 MFD definitions and `cs40l50_dsp_write`, regmap, Linux input FF periodic/custom APIs, ordered workqueues, runtime PM, and platform device ID `cs40l50-vibra`.

Risks: only one effect slot is supported. `cs40l50_stop_worker()` leaks `work_data` if runtime resume fails. OWT indexing is compacted by decrementing later tracked indexes and assumes DSP delete has the same compaction behavior. Playback repeat uses `replay.length` as a microsecond sleep interval, so unit assumptions should be validated. GPIO register calculation trusts encoded trigger button bits.

Test signals: test ROM/RAM/OWT upload validation, OWT no-space handling, GPIO mapping and disable on erase, playback count and stop, runtime PM failure paths, ordered serialization between upload/play/erase, and effect-list compaction after OWT deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/cs40l50-vibra.c -->
