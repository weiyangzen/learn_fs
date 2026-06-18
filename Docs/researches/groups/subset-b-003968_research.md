# subset-b-003968 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/iqs626a.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/iqs626a.c

Purpose: `iqs626a.c` is an I2C input driver for the Azoteq IQS626A capacitive/inductive/Hall touch controller. It can expose two Linux input devices: a keypad-like device for proximity/touch/deep/Hall events and a trackpad device that either reports coordinates or gesture keycodes.

Important APIs, types, and functions: the driver uses `regmap` with 8-bit register addresses and 16-bit values, `devm_request_threaded_irq`, `fwnode`/device-property parsing, `touchscreen_parse_properties`, and normal input APIs. The main state is `struct iqs626_private`, which owns the I2C client, regmap, cached `struct iqs626_sys_reg`, ATI completion, keypad/trackpad input devices, touchscreen properties, configured key types/codes, gesture codes, and suspend mode. Register layouts are represented by packed structs such as `iqs626_flags`, `iqs626_sys_reg`, channel register structs, and descriptor tables `iqs626_events[]` and `iqs626_channels[]`. The main functions are `iqs626_parse_prop`, `iqs626_parse_channel`, `iqs626_parse_events`, `iqs626_parse_trackpad`, `iqs626_input_init`, `iqs626_report`, `iqs626_irq`, `iqs626_probe`, `iqs626_suspend`, and `iqs626_resume`.

Control flow: probe allocates state, creates a regmap, validates product number `0x51`, reads the current system register block, folds firmware-node properties into the cached register image, writes the full block back, creates input devices, requests the threaded IRQ, waits up to two seconds for ATI completion, and only then registers the keypad so initial switch state is known. Child nodes named `ulp-0`, `trackpad-3x2`, `trackpad-3x3`, `generic-*`, and `hall` selectively activate channels and configure thresholds, hysteresis, ATI targets, CRX/TX pins, sensing modes, association weights, gesture behavior, and event masks. IRQ handling reads the status/flags block, restores the cached system block after unexpected SHOW_RESET, ignores active ATI, derives Hall direction from differential output, reports configured keypad events, completes ATI, and reports trackpad coordinates or momentary gesture key events.

State and persistence: no persistent storage is used, but the cached `sys_reg` is authoritative runtime configuration and is replayed after device self-reset. `ati_done` gates keypad registration. `kp_type`, `kp_code`, and `tp_code` are populated from firmware and become input keymaps. Suspend/resume manually forces power modes when `azoteq,suspend-mode` is configured, disabling IRQs during register transitions and polling power-mode bits for completion.

Dependencies and integration points: integration is through I2C, regmap, OF compatible `azoteq,iqs626a`, firmware-node child properties, touchscreen properties, and the input subsystem. Hardware correctness depends on RDY interrupt timing; the driver inserts `iqs626_irq_wait()` after writes and IRQ handling.

Risks: most risk is property validation and register packing: incorrect child-node names, out-of-range values, or mismatched active trackpad variants can silently leave features disabled or fail probe. Reset recovery only succeeds if the cached register image remains valid. IRQ returns `IRQ_NONE` on reporting errors, so transient I2C failures may look like interrupt problems. Trackpad mode depends on gesture event mask semantics, which makes raw-coordinate versus gesture behavior easy to regress.

Test signals: useful signals are probe success, product-number rejection, firmware property validation failures, ATI timeout, input device registration, `Unexpected device reset` recovery, keypad/Hall press/release events, trackpad ABS events or gesture key press/release pairs, and suspend/resume power-mode polling. Device-tree tests should cover all channel classes, Hall direction, gesture and coordinate trackpad modes, invalid property bounds, and wake/suspend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/iqs626a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/iqs7222.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/iqs7222.c

Purpose: `iqs7222.c` is an I2C input driver for Azoteq IQS7222A/B/C/D capacitive controllers. It presents one input device that can include button/proximity keys, sliders or wheels, and trackpad coordinates/gestures depending on firmware-node configuration and supported product revision.

Important APIs, types, and functions: the driver uses raw I2C transfers, GPIO descriptors for RDY and optional reset, input/touchscreen APIs, and firmware-node parsing. `struct iqs7222_dev_desc` describes product number, minimum firmware, register group geometry, communication/control offsets, event offsets, slider resolution, links, GPIO quirks, and legacy gesture behavior. `struct iqs7222_private` caches all register groups in fixed arrays and stores keypad, slider, and trackpad key/axis mappings. Key functions are `iqs7222_force_comms`, `iqs7222_read_burst`, `iqs7222_write_burst`, `iqs7222_ati_trigger`, `iqs7222_dev_init`, `iqs7222_dev_info`, `iqs7222_parse_props`, `iqs7222_parse_chan`, `iqs7222_parse_sldr`, `iqs7222_parse_tpad`, `iqs7222_parse_all`, `iqs7222_report`, and `iqs7222_probe`.

Control flow: probe allocates state and one input device, requests the RDY GPIO and optional reset GPIO, hard-resets the device if possible, reads product/firmware ID, selects a descriptor, bulk-reads all supported register groups into cache, parses firmware properties into the cache, bulk-writes the modified groups, triggers ATI, reads and reports initial status, registers the input device, maps RDY GPIO to IRQ, and requests the threaded IRQ. The communication path is special: unsolicited access uses a one-byte force-communication command, polls RDY, retries transient RDY races, treats `0xEEEE` reads as invalid data, and optionally uses a stop-bit hold register while bulk reading/writing setup groups.

State and persistence: there is no durable storage. Runtime state is the cached register group arrays, selected `dev_desc`, event mappings, touchscreen properties, and GPIO descriptors. `iqs7222_dev_init(READ)` captures reset defaults; `parse_all` mutates the cached copy; `dev_init(WRITE)` writes it back and starts ATI. Reset or ATI errors in `iqs7222_report` cause configuration replay or ATI retry.

Dependencies and integration points: compatibles cover `azoteq,iqs7222a` through `azoteq,iqs7222d`. The driver integrates with firmware child nodes named by register group (`cycle-%d`, `channel-%d`, `slider-%d`, `trackpad`, `gpio-%d`) and a large property descriptor table mapping `azoteq,*` properties to register fields. Input integration supports EV_KEY/EV_SW button events, EV_ABS slider/trackpad axes, gesture keycodes, and touchscreen axis transformation.

Risks: product support is tightly coupled to firmware revision and register geometry; adding a revision with changed offsets can corrupt setup writes. The RDY/force-comms protocol has several timing races, so retry behavior and stop-bit hold handling are fragile. Slider/trackpad parsing depends on register offsets that differ across device families. Event masks, GPIO links, and channel selections can conflict; validation catches many but not all logical board mistakes. IRQ returns `IRQ_NONE` on read/report failure.

Test signals: test with all supported product descriptor families, reset GPIO present/absent, RDY active polarity, communication retries, ATI timeout/error recovery, channel prox/touch events, slider absolute axes and gesture momentary releases, trackpad ABS reporting, GPIO event-link conflicts, legacy gesture timing properties, invalid channel/CRX/CTX selections, and unexpected reset replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/iqs7222.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/keyspan_remote.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/keyspan_remote.c

Purpose: `keyspan_remote.c` is a USB input driver for the Keyspan UIA-11/DMR remote. It converts interrupt-in byte streams containing pulse-coded remote messages into Linux key events.

Important APIs, types, and functions: the driver uses `usb_driver`, interrupt URBs, coherent USB DMA buffers, `usb_control_msg` setup commands, and input keymap APIs. `struct usb_keyspan` holds USB/input objects, endpoint, URB, coherent input buffer, parser stage, toggle state, and a `struct bit_tester`. `struct keyspan_message` stores decoded system/button/toggle fields. `keyspan_load_tester`, `keyspan_check_data`, `keyspan_report_button`, `keyspan_irq_recv`, `keyspan_open`, `keyspan_close`, `keyspan_probe`, and `keyspan_disconnect` make up the main flow.

Control flow: probe finds an interrupt-in endpoint, allocates driver/input objects and an 8-byte coherent receive buffer, sends three vendor control messages to set bit rate, resume sensitivity, and receiver enable, builds a name/phys path, installs the keymap, initializes the interrupt URB, registers the input device, and stores interface data. The URB is submitted only when the input device is opened; close kills the URB. The completion callback optionally dumps bytes, feeds the parser, and resubmits unless the device was disconnected or the URB was canceled.

State and persistence: parser state spans multiple 8-byte URB packets. Stage 0 finds non-`0xff` data, stage 1 searches for the 14-bit sync sequence, and stage 2 decodes 9 system bits, 5 button bits, one toggle bit, and stop bits using 5-bit zero and 6-bit one encodings. `toggle` suppresses repeated reports for held buttons; a changed toggle causes a press and immediate release.

Dependencies and integration points: hardware matching is by USB VID/PID `06cd:0202`. Input integration includes EV_KEY keys from `keyspan_key_table` and EV_MSC/MSC_SCAN scan reports. The driver depends on the remote repeating messages after decode loss.

Risks: `message.button` is 5 bits and indexes the keymap directly; the table size matches 32 entries, so parser correctness is critical. Parser resynchronization can drop a message after malformed data. The code uses manual allocation rather than devm, so error labels and disconnect ordering matter. Repeated `usb_submit_urb` failures can log errors. Control-message magic values are undocumented in the driver.

Test signals: test probe on matching USB ID, open/close URB submission, disconnect during active URB, malformed bit streams, sync loss/recovery, toggle suppression, MSC_SCAN values, every non-reserved keymap entry, and debug byte dumping through the `debug` module parameter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/keyspan_remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/kxtj9.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/kxtj9.c

Purpose: `kxtj9.c` is an I2C input driver for Kionix KXTJ9 accelerometers. It reports three-axis acceleration via ABS_X/Y/Z using either polling or data-ready interrupts.

Important APIs, types, and functions: it depends on legacy `struct kxtj9_platform_data` for axis mapping, negation, g-range, poll intervals, and board power hooks. It uses I2C/SMBus transfers, input polling, threaded IRQs, sysfs attributes, and simple PM ops. The main state is `struct kxtj9_data`, holding the client, copied platform data, input device, last poll interval, data shift, and cached control register values. Core functions include `kxtj9_i2c_read`, `kxtj9_report_acceleration_data`, `kxtj9_update_g_range`, `kxtj9_update_odr`, `kxtj9_enable`, `kxtj9_disable`, `kxtj9_poll`, `kxtj9_isr`, `kxtj9_verify`, `kxtj9_probe`, suspend, and resume.

Control flow: probe requires I2C and SMBus byte-data support and non-null platform data. Optional platform `init` is registered for cleanup through `devm_add_action_or_reset`. The driver powers the device, reads WHO_AM_I, accepts IDs `0x07` or `0x08`, powers it off, allocates the input device, sets ABS ranges, configures polling when no IRQ is present, registers the input device, and then requests a threaded IRQ if provided. Opening the input device powers on the hardware, writes control registers with PC1 off, enables IRQ configuration if needed, applies g-range and ODR, sets PC1 on, and clears the initial interrupt. Closing powers it off.

State and persistence: no persistent storage exists. Runtime state is cached register values and `last_poll_interval`; sysfs `poll` is visible only in IRQ mode and updates ODR under the input mutex with IRQ disabled. In polling mode, changing the input polling interval updates hardware ODR during the next poll. Suspend disables the chip only if the input device is enabled; resume reenables it.

Dependencies and integration points: the driver is I2C ID based (`kxtj9`) and needs board-specific platform data, so it is not DT-property driven. Input integration is ABS-only with fuzz/flat values and optional poll controls.

Risks: lack of platform data makes probe fail. `kxtj9_i2c_read` returns the `i2c_transfer` message count on success, and report only treats negative values as failure. `kxtj9_set_poll` ignores an `update_odr` error but still returns `count`. Axis mapping and negation are trusted from platform data. Power hook failures can leave partially configured state.

Test signals: test both polling and IRQ modes, WHO_AM_I rejection, board power hooks, sysfs `poll` bounds through `min_interval`, ODR selection table behavior, g-range shifts, axis mapping/negation, interrupt clear via `INT_REL`, open/close sequencing, and suspend/resume with enabled and disabled input users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/kxtj9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/m68kspkr.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/m68kspkr.c

Purpose: `m68kspkr.c` exposes the m68k low-level machine beep function as a Linux input sound device supporting bell and tone events.

Important APIs, types, and functions: it uses platform driver/device registration, the input subsystem, and architecture hooks from `asm/machdep.h`. `m68kspkr_event` is the key callback; `m68kspkr_probe`, `m68kspkr_remove`, `m68kspkr_shutdown`, `m68kspkr_init`, and `m68kspkr_exit` provide lifecycle handling. A global `m68kspkr_platform_device` is allocated by module init.

Control flow: module init first checks the architecture-provided `mach_beep` pointer; without it the driver returns `-ENODEV`. It registers a platform driver, allocates a synthetic `m68kspkr` platform device, and adds it. Probe allocates an input device, sets BUS_HOST identity, advertises EV_SND with SND_BELL and SND_TONE, installs `m68kspkr_event`, registers input, and stores it as platform data. Remove and shutdown both force the speaker off by calling the event callback with zero value.

State and persistence: no persistent state exists beyond the registered platform device and input device. The event callback converts SND_BELL to a 1000 Hz tone when nonzero and SND_TONE to a PIT-style divisor count when `20 < value < 32767`; otherwise it passes zero to stop sound.

Dependencies and integration points: this file is m68k-specific and depends entirely on `mach_beep(count, -1)` for actual hardware access. Input clients use normal EV_SND events.

Risks: `m68kspkr_event` returns `-1` instead of `-EINVAL`, unlike most input callbacks. It assumes `mach_beep` remains valid after init. There is no locking inside the event path; hardware serialization is delegated to the low-level implementation. The fallthrough from SND_BELL into SND_TONE is intentional but not annotated.

Test signals: test module load on machines with and without `mach_beep`, input event acceptance for SND_BELL/SND_TONE, invalid type/code rejection, zero-value shutdown on remove and system shutdown, and audible frequency/count behavior on actual m68k hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/m68kspkr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max7360-rotary.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/max7360-rotary.c

Purpose: `max7360-rotary.c` is a platform child driver for the MAX7360 MFD that reports rotary encoder movement through the Linux input subsystem.

Important APIs, types, and functions: it uses a parent regmap, `fwnode_irq_get_byname`, input ABS/REL reporting, threaded IRQs, wake IRQ helpers, and MAX7360 register definitions. `struct max7360_rotary` stores the input device, regmap, debounce, current absolute position, steps, axis, relative/absolute mode, and rollover behavior. Main functions are `max7360_rotary_report_event`, `max7360_rotary_irq`, `max7360_rotary_hw_init`, probe, and remove.

Control flow: probe obtains the parent regmap and named parent IRQ `inti`, allocates state, reads parent properties (`linux,axis`, `rotary-encoder,rollover`, `rotary-encoder,relative-axis`, `rotary-encoder,steps`, `rotary-debounce-delay-ms`), validates debounce against `MAX7360_ROT_DEBOUNCE_MAX`, allocates and configures the input device, requests a shared threaded IRQ, registers input, writes rotary configuration, enables device wakeup, and assigns the wake IRQ. The IRQ handler reads `MAX7360_REG_RTR_CNT`, ignores zero, sign-extends the 8-bit counter, reports relative steps or updates an absolute position with clamp/rollover, then syncs input.

State and persistence: absolute mode persists only `pos` in RAM. Hardware debounce and interrupt-count configuration are written at probe and not otherwise refreshed. Remove clears wake IRQ and wakeup state.

Dependencies and integration points: this driver is tightly coupled to the MAX7360 parent MFD regmap and parent firmware node properties rather than child-only properties. It integrates with generic rotary-encoder bindings and Linux input ABS/REL axes.

Risks: absolute `input_set_abs_params` uses max `steps`, while reported positions range `0..steps-1`; consumers usually tolerate this but tests should note it. Probe registers the input device before hardware init, so a very early interrupt could run before configuration. Shared IRQ handling returns `IRQ_NONE` on zero counter or read error, which is appropriate but can obscure noisy hardware. Parent property lookup means board descriptions must place properties where this driver expects them.

Test signals: verify relative and absolute modes, rollover versus clamp, negative sign extension, debounce bounds, wake IRQ setup/cleanup, missing parent regmap or IRQ failures, zero counter handling, and axis/steps defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max7360-rotary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max77650-onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/max77650-onkey.c

Purpose: `max77650-onkey.c` exposes the MAX77650/MAX77651 ONKEY as an input event source. It supports push-button mode as EV_KEY and slide-switch mode as EV_SW.

Important APIs, types, and functions: it uses the parent MFD regmap, platform IRQs named `nEN_F` and `nEN_R`, and devm input/IRQ helpers. `struct max77650_onkey` stores the input device and configured code. Main functions are `max77650_onkey_falling`, `max77650_onkey_rising`, and `max77650_onkey_probe`.

Control flow: probe obtains the parent regmap, allocates state, reads optional `linux,code` defaulting to `KEY_POWER`, chooses slide or push mode from `maxim,onkey-slide`, updates `MAX77650_REG_CNFG_GLBL` bit 3 to select mode, fetches falling and rising IRQs, allocates an input device with I2C bus type and matching EV_KEY/EV_SW capability, requests both IRQs, and registers input. The falling handler reports value `0`; the rising handler reports value `1`.

State and persistence: the only runtime state is the input/code pair. The selected hardware mode persists in the PMIC register until changed by another actor or reset. There is no explicit PM handling or wakeup setup here.

Dependencies and integration points: platform binding uses compatible `maxim,max77650-onkey` and platform alias `max77650-onkey`. IRQ names must be supplied by the parent MFD. Input clients see either a key or switch event under the configured code.

Risks: the semantic mapping of falling to release and rising to press depends on PMIC IRQ naming/polarity; if parent IRQ descriptions invert names, events invert. There is no initial state report, so switch-mode users may not know current state until an edge arrives. The driver does not configure wakeup.

Test signals: test both push and slide modes, custom `linux,code`, regmap mode-bit updates, missing IRQ names, press/release edge ordering, and input capability type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max77650-onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max77693-haptic.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/max77693-haptic.c

Purpose: `max77693-haptic.c` is an ff-memless haptic driver for MAX77693, MAX77705, and MAX77843 PMIC/MFD variants. It converts rumble magnitudes to PWM duty cycle and PMIC haptic enable/configuration writes.

Important APIs, types, and functions: it uses MFD-provided regmaps, PWM, regulator, workqueue, and input force-feedback APIs. `struct max77693_haptic` stores variant type, PMIC and haptic regmaps, input device, PWM, motor regulator, enable/suspend flags, magnitude, PWM duty, motor type, pulse mode, and work item. Key functions include `max77693_haptic_set_duty_cycle`, `max77843_haptic_bias`, `max77693_haptic_configure`, `max77693_haptic_lowsys`, `max77693_haptic_enable`, `max77693_haptic_disable`, `max77693_haptic_play_work`, `max77693_haptic_play_effect`, open/close, probe, suspend, and resume.

Control flow: probe gets the parent `max77693_dev`, chooses variant-specific haptic regmap, initializes work, obtains an unnamed PWM and `haptic` regulator, allocates input, advertises EV_FF/FF_RUMBLE, creates a memless FF device, registers input, and stores driver data. Input open enables MAX77843 bias when needed and enables the motor regulator. FF playback stores strong magnitude or weak fallback, converts `0..0xffff` magnitude to PWM duty based on PWM period, and schedules work. Work disables haptics for zero magnitude, updates duty when already enabled, or enables PWM, low-system bit, and haptic config when starting. Close cancels work, disables haptics, disables regulator, and clears bias. Suspend disables currently active haptic output and remembers state; resume re-enables if it had been active.

State and persistence: runtime state is in `enabled`, `suspend_state`, `magnitude`, and `pwm_duty`. Hardware config is not persistent across reset and is written on each enable. The driver defaults to LRA motor and external PWM mode.

Dependencies and integration points: compatible strings and platform IDs cover all three variants. MAX77693 has a separate haptic regmap and low-system PMIC bit; MAX77705/MAX77843 use parent regmap variants, with MAX77843 needing an additional bias bit.

Risks: there is no explicit mutex around `enabled`/`magnitude`, relying on input serialization and workqueue ordering. If `max77693_haptic_disable` cannot clear config or low-system state, it may leave hardware enabled. PWM duty is computed as `(period + pwm_duty) / 2`, so the effective waveform is centered around half period rather than direct duty, and should be tested against hardware expectations.

Test signals: validate PWM/regulator acquisition, each variant register path, open/close resource sequencing, strong and weak rumble magnitudes, zero-magnitude stop, repeated duty updates while enabled, suspend/resume restoration, regulator/bias failure paths, and FF device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max77693-haptic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max8925_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/max8925_onkey.c

Purpose: `max8925_onkey.c` reports MAX8925 PMIC ONKEY press/release state as KEY_POWER input events.

Important APIs, types, and functions: it uses the MAX8925 MFD API, platform IRQs, devm input allocation, threaded IRQs, and PM wake flag integration through the parent `max8925_chip`. `struct max8925_onkey_info` stores the input device, I2C client, device pointer, and two IRQ numbers. Main functions are `max8925_onkey_handler`, probe, suspend, and resume.

Control flow: probe gets two IRQs from platform resources, allocates state and input, stores the parent PMIC I2C client, configures the input device for EV_KEY/KEY_POWER, requests threaded IRQs named `onkey-down` and `onkey-up`, registers input, stores driver data, and enables device wakeup. Both IRQs use the same handler: read `MAX8925_ON_OFF_STATUS`, report KEY_POWER based on `SW_INPUT`, sync, and set `HARDRESET_EN` in `MAX8925_SYSENSEL` so the PMIC can hard reset if software fails to shut down.

State and persistence: runtime state is minimal. The parent `chip->wakeup_flag` bitmask is modified during suspend/resume for both IRQs when wakeup is enabled. The hard-reset enable bit is reasserted on each key interrupt.

Dependencies and integration points: this is a platform child of the MAX8925 MFD and relies on `max8925_reg_read` and `max8925_set_bits`. Input integration is a single KEY_POWER.

Risks: no initial state is reported at probe. Handler does not check negative return from `max8925_reg_read` before using `state`. Wake flag bit shifting by IRQ number assumes the parent’s flag representation matches Linux IRQ numbers. The same handler for press and release depends on status register correctness.

Test signals: test both IRQ resources, state register press/release transitions, hard-reset enable write, input registration, suspend/resume wake flag changes, and failure behavior for PMIC register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max8925_onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max8997_haptic.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/max8997_haptic.c

Purpose: `max8997_haptic.c` is an ff-memless haptic driver for MAX8997. It supports internal-pattern mode and external PWM mode, converting rumble requests to PMIC haptic register writes and optional PWM output.

Important APIs, types, and functions: it uses MAX8997 MFD register helpers, platform data, regulator and PWM APIs, workqueues, mutexes, and input FF. `struct max8997_haptic` stores device/client/input/regulator/PWM, work, mutex, enabled flag, level, PWM period/divisor, motor type, mode, and internal pattern parameters. Main functions are `max8997_haptic_set_internal_duty_cycle`, `max8997_haptic_configure`, enable/disable, work handler, FF callback, close, probe, remove, and suspend.

Control flow: probe retrieves parent platform data and `haptic_pdata`, allocates state and input manually, initializes work and mutex, copies mode-specific parameters, obtains PWM for external mode or pattern data for internal mode, obtains `inmotor` regulator, configures input as EV_FF/FF_RUMBLE, creates the memless FF device, registers input, and stores platform data. FF playback stores strong magnitude or weak fallback as `level` and schedules work. Work enables if nonzero or disables if zero. Enable locks, sets internal duty when applicable, enables regulator and PMIC config if not already enabled, and applies PWM in external mode. Disable locks, clears enable config, disables PWM if external, and disables regulator. Close cancels work and disables; suspend disables.

State and persistence: `enabled` and `level` are runtime state guarded by `mutex` in enable/disable but written by FF callback before scheduling. Hardware state is reprogrammed on each enable. Manual resource cleanup is done in remove.

Dependencies and integration points: this driver depends on legacy MAX8997 platform data rather than firmware properties. External mode needs a PWM; both modes need the regulator and MFD haptic I2C client. Input clients see a standard memless rumble device.

Risks: FF magnitude is not scaled from `0..0xffff` to percent before external PWM duty; `level` may exceed 100, making `period * level / 100` potentially beyond period unless platform/input paths constrain it. Internal duty calculation also uses `level * 64 / 100`. Register writes ignore many return values in config helpers. Manual allocation creates more cleanup paths.

Test signals: test absence of platform data, internal and external modes, invalid mode, PWM/regulator failure paths, strong/weak/zero rumble, close and suspend stop behavior, remove cleanup, and actual PWM duty bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/max8997_haptic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/mc13783-pwrbutton.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/mc13783-pwrbutton.c

Purpose: `mc13783-pwrbutton.c` reports up to three MC13783 PMIC ON/OFF buttons as Linux key events with platform-configurable keycodes, debounce, polarity inversion, and hard-reset enable.

Important APIs, types, and functions: it uses MC13xxx MFD APIs for register access, locking, and IRQ management, plus input/platform APIs. `struct mc13783_pwrb` stores the input device, PMIC handle, polarity flags, and a three-entry keymap. Main functions are `button_irq`, `mc13783_pwrbutton_probe`, and remove.

Control flow: probe requires `mc13xxx_buttons_platform_data`. It allocates input and private state, computes `MC13783_REG_POWER_CONTROL_2` debounce and reset-enable bits from the three button flag fields, locks the PMIC, requests enabled button IRQs, records keycodes and polarity flags, writes the power-control bits, unlocks, configures input keymap/capabilities, registers input, and stores driver data. IRQ handling reads `MC13783_REG_INTERRUPT_SENSE_1`, selects the relevant sense bit based on IRQ number, applies polarity inversion, reports the corresponding key, and syncs.

State and persistence: keymap and polarity flags live in RAM. Debounce/reset configuration is written to the PMIC and persists until PMIC reset or another driver changes it. Remove frees enabled IRQs under the PMIC lock, unregisters input, and frees memory.

Dependencies and integration points: this is a platform child named `mc13783-pwrbutton`, dependent on legacy platform data and MC13xxx IRQ IDs `MC13783_IRQ_ONOFD1..3`. Input events are EV_KEY with board-provided keycodes.

Risks: missing platform data prevents probe. Error paths must free only IRQs that were successfully requested; the labels follow enabled button order but are sensitive to future edits. `mc13xxx_reg_read` return is ignored in IRQ handler. There is no PM wake handling in this driver. Keycodes may be `KEY_RESERVED`, resulting in enabled IRQs that report reserved/no useful input.

Test signals: test all combinations of enabled buttons, polarity inversion, debounce flag packing, reset-enable bits, KEY_RESERVED handling, register read failures, IRQ free paths after partial probe failure, and input reports for each ONOFD IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/mc13783-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/mma8450.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/mma8450.c

Purpose: `mma8450.c` is a polling I2C input driver for Freescale MMA8450 three-axis accelerometers. It reports 12-bit signed acceleration samples as ABS_X/Y/Z.

Important APIs, types, and functions: it uses SMBus byte and block reads/writes, input polling helpers, and I2C/OF match tables. The main functions are `mma8450_read`, `mma8450_write`, `mma8450_read_block`, `mma8450_poll`, `mma8450_open`, `mma8450_close`, and `mma8450_probe`.

Control flow: probe verifies SMBus byte support, reads `MMA8450_WHO_AM_I`, expects chip ID `0xc6`, allocates an input device, installs open/close callbacks, configures ABS ranges `-2048..2047`, sets up polling, sets default and max poll intervals, and registers input. Opening writes `XYZ_DATA_CFG` to enable all axes/no FIFO, writes `CTRL_REG1` for active +/-2G with configured data rates, then waits 100 ms for mode change. Polling reads `STATUS`, exits if no XYZ data-ready bit is set, reads six data bytes from `OUT_X_LSB`, reconstructs signed 12-bit X/Y/Z values, reports ABS axes, and syncs. Closing writes standby and reset/sleep control values.

State and persistence: the driver stores no private structure beyond the I2C client pointer in input drvdata. Hardware state is active only while the input device is open; close powers/stops it. No suspend/resume hooks are present, so input core open/close and system I2C behavior are the main gates.

Dependencies and integration points: compatible is `fsl,mma8450`; I2C ID is `mma8450`. It integrates only through input polling and ABS axes.

Risks: `mma8450_read_block` treats any nonnegative SMBus return as success and does not verify that all requested bytes were read. Probe does not check negative chip-ID read separately from mismatch in the message. There is no IRQ mode. The open configuration is fixed and not firmware-configurable. Close writes two registers but ignores failures.

Test signals: test chip-ID detection, polling setup, no-data-ready skips, signed 12-bit conversion, input open/close register writes, max/default poll intervals, SMBus block short-read behavior, and OF/I2C matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/mma8450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/nxp-bbnsm-pwrkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/nxp-bbnsm-pwrkey.c

Purpose: `nxp-bbnsm-pwrkey.c` reports the i.MX93 BBNSM power key as a Linux key event, including wakeup support and a timer-based release/debounce poll.

Important APIs, types, and functions: it uses a parent syscon regmap, platform IRQ, timers, PM wakeup helpers, wake IRQ helpers, and input APIs. `struct bbnsm_pwrkey` stores regmap, IRQ, keycode, current key state, suspend flag, timer, and input device. Main functions are `bbnsm_pwrkey_check_for_events`, `bbnsm_pwrkey_interrupt`, probe, remove, suspend, and resume.

Control flow: probe allocates state, gets the parent syscon regmap, reads optional `linux,code` defaulting to `KEY_POWER`, gets IRQ 0, enables the BBNSM debounce/power control bit `BBNSM_DP_EN`, clears pending power-key events, initializes the timer, allocates input, registers a cleanup action to shut down the timer, requests a shared IRQ, registers input, enables device wakeup, and sets the wake IRQ. The IRQ reads `BBNSM_EVENTS`, ignores interrupts without `BBNSM_BTN_OFF`, emits a wakeup event, optionally synthesizes a press immediately after resume, starts the debounce timer, clears the button-off event, and returns handled. The timer reads `BBNSM_EVENTS`, compares `BBNSM_BTN_PRESSED` with cached state, reports changes, relaxes the wakeup source, and reschedules while pressed.

State and persistence: `keystate` prevents duplicate reports; `suspended` allows one synthetic post-resume press. The timer is shut down through devm action. Hardware event bits are cleared in probe and IRQ.

Dependencies and integration points: compatible is `nxp,imx93-bbnsm-pwrkey`; the node’s parent must provide a syscon regmap. Input is BUS_HOST with a configurable keycode.

Risks: regmap read/write return values are mostly ignored in IRQ/timer paths. Shared IRQ handling depends on `BBNSM_BTN_OFF` filtering. `pm_relax` is called only on state change in timer, so unexpected no-change paths may keep wake accounting longer. Suspend and resume simply toggle a flag; wake IRQ handles the hardware wake side.

Test signals: test default/custom keycode, pending event clearing, IRQ filtering, press and release timer reports, long-press repeat polling, suspend/resume synthetic press, wake IRQ setup/cleanup, and regmap access failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/nxp-bbnsm-pwrkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/palmas-pwrbutton.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/palmas-pwrbutton.c

Purpose: `palmas-pwrbutton.c` reports the TI Palmas PMIC power button as KEY_POWER, configures hardware long-press shutdown/debounce, and polls for release after press interrupts.

Important APIs, types, and functions: it uses Palmas MFD register helpers, delayed work, threaded IRQ, input APIs, OF parsing, and IRQ wake. `struct palmas_pwron` stores the parent PMIC, input device, delayed work, and IRQ. `struct palmas_pwron_config` stores encoded long-press and debounce values. Main functions are `palmas_power_button_work`, `pwron_irq`, `palmas_pwron_params_ofinit`, probe, remove, suspend, and resume.

Control flow: probe parses optional DT properties `ti,palmas-long-press-seconds` and `ti,palmas-pwron-debounce-milli-seconds`, allocates state and input, configures KEY_POWER, writes `PALMAS_LONG_PRESS_KEY` fields for long press and debounce, initializes delayed work, gets IRQ 0, requests a high/low triggered threaded IRQ, registers input, stores state, and enables wakeup. The IRQ reports press, emits `pm_wakeup_event`, syncs input, and schedules delayed work after 20 ms. Work reads `PALMAS_INT1_LINE_STATE`; if bit 1 indicates release it reports KEY_POWER release, otherwise it reschedules itself.

State and persistence: delayed work is the only runtime state beyond pointers. Hardware long-press/debounce settings persist in PMIC registers until reset or reconfiguration. Suspend cancels pending release polling and enables IRQ wake if allowed; resume disables IRQ wake.

Dependencies and integration points: compatible is `ti,palmas-pwrbutton`; platform alias is `palmas-pwrbutton`. The driver depends on the Palmas parent MFD and PMU/interrupt register maps.

Risks: release detection is polling based and can miss/log read failures, rescheduling only when the register read succeeds and indicates still pressed. Manual allocation/request paths require careful cleanup. Wakeup is initialized but `device_may_wakeup` controls IRQ wake only during suspend. The work interprets bit 1 as release; board/PMIC polarity mistakes invert behavior.

Test signals: test DT property rounding to supported tables, long-press/debounce register write, press IRQ reporting, delayed release detection and rescheduling, read-error handling, suspend cancellation, IRQ wake enable/disable, remove cleanup, and repeated press while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/palmas-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pcap_keys.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/pcap_keys.c

Purpose: `pcap_keys.c` reports Motorola PCAP2 PMIC power and headset/microphone button events through the input subsystem.

Important APIs, types, and functions: it uses the EZX PCAP MFD API, platform IRQ mapping helpers, and input APIs. `struct pcap_keys` stores the parent PCAP chip and input device. Main functions are `pcap_keys_handler`, probe, and remove.

Control flow: probe allocates private state and input, gets the parent PCAP pointer, configures an EV_KEY input device with KEY_POWER and KEY_HP, registers input, requests PCAP ONOFF and MIC IRQs, and returns. The IRQ handler converts Linux IRQ to PCAP IRQ number, reads `PCAP_REG_PSTAT`, masks the bit for that source, reports KEY_POWER or KEY_HP as `!pstat`, and syncs. Remove frees both IRQs, unregisters input, and frees state.

State and persistence: the driver has no persistent state and does not cache button state. It reads status on each interrupt. Input device registration and IRQ ownership are the only lifecycle state.

Dependencies and integration points: it is a platform child named `pcap-keys`/alias `pcap_keys` and requires the parent `pcap_chip`. Input clients get two key codes on BUS_HOST.

Risks: `ezx_pcap_read` return is ignored; stale/uninitialized `pstat` would be harmful if read fails. The inverted `!pstat` logic depends on PCAP status polarity. Probe registers input before requesting IRQs; if second IRQ request fails, input is unregistered and memory freed. No PM or wakeup handling is implemented here.

Test signals: test both IRQ sources, status polarity, parent IRQ mapping, read failure behavior, failure of second IRQ request, input registration cleanup, and key events for power and headset button.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pcap_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pcf8574_keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/pcf8574_keypad.c

Purpose: `pcf8574_keypad.c` is an I2C input driver for a 4x4 keypad connected through a PCF8574 I/O expander.

Important APIs, types, and functions: it uses SMBus byte writes/reads, threaded IRQs, input keymap APIs, and simple PM ops. `struct kp_data` stores the keymap, input device, I2C client, names, and last state. `read_state`, `pcf8574_kp_irq_handler`, probe, remove, suspend, and resume define the behavior.

Control flow: probe first writes `240` to the expander as a sanity check, allocates state and input, copies the static 17-entry keymap into the instance keymap, sets EV_KEY bits, initializes name/phys and bus identity, reads initial state, requests a low-triggered threaded IRQ, registers input, and stores client data. `read_state` drives upper and lower nibbles in two passes, reads back active-low row/column state, calculates a button index, and returns it. IRQ handling reads the next state, compares it to `laststate`, reports a key press if next state is in range or a release of the previous key otherwise, syncs, and updates `laststate`. Suspend disables the IRQ; resume enables it.

State and persistence: `laststate` is the only runtime state and assumes at most one key is active. No durable state exists. The expander line directions/output values are re-driven on each scan.

Dependencies and integration points: I2C ID is `pcf8574_keypad`; no OF table is defined in this file. Input keymap includes KEY_1..KEY_0, A/B/C, ENTER, BACKSLASH, RIGHTBRACE, and reserved entry.

Risks: the `for` loops in `read_state` calculate only the highest set bit plus one and do not handle multiple simultaneous keys. SMBus read/write errors are not checked in `read_state`, so failures can turn into bogus key indexes. In probe, the condition `if (lp->btncode[i] <= KEY_MAX)` checks uninitialized destination before assignment, though zero-initialized memory makes it true. IRQ is disabled on suspend without checking wake needs.

Test signals: test one-key press/release for all 16 positions, no-key state, multiple-key ambiguity, SMBus failures, low-triggered IRQ behavior, suspend/resume IRQ gating, keymap exposure, and probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pcf8574_keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pcspkr.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/pcspkr.c

Purpose: `pcspkr.c` exposes the legacy PC speaker as an EV_SND input device for bell and tone playback.

Important APIs, types, and functions: it uses platform driver APIs, input sound events, raw I/O port access, PIT definitions, and `i8253_lock`. The key functions are `pcspkr_event`, `pcspkr_probe`, `pcspkr_remove`, `pcspkr_suspend`, and `pcspkr_shutdown`.

Control flow: probe allocates an input device, assigns ISA identity, advertises EV_SND with SND_BELL and SND_TONE, installs `pcspkr_event`, registers input, and stores it in platform data. The event callback rejects non-EV_SND and unknown sound codes, maps nonzero SND_BELL to 1000 Hz, computes PIT counter value for tones between 20 and 32767 Hz, locks `i8253_lock`, programs PIT counter 2 and port `0x61` to enable sound, or clears port bits to disable sound, then unlocks. Remove, suspend, and shutdown all stop the speaker.

State and persistence: no persistent driver state exists other than the input device. Hardware state is the PIT channel and speaker gate bits, reset to off on remove/suspend/shutdown or zero-value events.

Dependencies and integration points: the driver binds as platform `pcspkr` and has module alias `platform:pcspkr`. It depends on x86/ISA-style PIT and speaker I/O ports and serializes with the global i8253 lock.

Risks: direct I/O port programming is platform-sensitive. Tone values outside the accepted range silently stop output. The driver does not track whether another component has programmed PIT channel 2. Suspend only turns the speaker off and does not restore a previous tone on resume.

Test signals: test SND_BELL, SND_TONE, zero stop, invalid event rejection, concurrent timer users through lock behavior, suspend/remove/shutdown stop paths, and platform creation/binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pcspkr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pf1550-onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/pf1550-onkey.c

Purpose: `pf1550-onkey.c` reports PF1550 PMIC ONKEY interrupt events as KEY_POWER and optionally disables the PMIC key-power reset behavior.

Important APIs, types, and functions: it uses the PF1550 MFD data/regmap, platform IRQs, input APIs, and PM wake controls. `struct onkey_drv_data` stores device, parent data, wakeup flag, and input device. Main functions are `pf1550_onkey_irq_handler`, probe, suspend, and resume.

Control flow: probe allocates state, obtains parent PF1550 data and regmap, reads parent `wakeup-source`, optionally clears `PF1550_ONKEY_RST_EN` when `nxp,disable-key-power` is present, allocates input, advertises KEY_POWER unless key-power is disabled, requests six threaded IRQs with `IRQF_NO_SUSPEND`, registers input, and initializes wakeup. The IRQ handler identifies which platform IRQ fired by comparing against all six IRQ resources. `PUSHI` reports release (`0`), while 1s/2s/3s/4s/8s long-press interrupts report press (`1`), then syncs.

State and persistence: runtime state is minimal. Suspend masks all ONKEY interrupts in the PMIC when not a wakeup source, or enables IRQ wake for each IRQ when wakeup is allowed. Resume reverses this by unmasking or disabling IRQ wake.

Dependencies and integration points: platform ID is `pf1550-onkey`. The parent must expose PF1550 IRQ resources and regmap. Input is BUS_HOST.

Risks: if `nxp,disable-key-power` is set, the input device may register with no KEY_POWER capability while IRQs still report KEY_POWER, which should be validated against intended semantics. The handler calls `platform_get_irq` for every interrupt, adding overhead and possible error values in IRQ context. `IRQF_NO_SUSPEND` plus manual wake/mask handling needs careful system suspend testing.

Test signals: test all six IRQs, disabled key-power mode, wakeup-source true/false suspend paths, PMIC mask register writes, IRQ wake enable/disable, regmap absence, missing IRQ resources, and input capability exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pf1550-onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pm8941-pwrkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/pm8941-pwrkey.c

Purpose: `pm8941-pwrkey.c` handles Qualcomm PMIC PON power-key and resin/reset inputs across PM8941-style and newer PMK8350/GEN3 variants. It reports configured key events, programs debounce/pull-up where supported, and optionally configures PS_HOLD reset behavior on reboot/poweroff.

Important APIs, types, and functions: it uses regmap, OF address parsing, input, threaded IRQs, IRQ wake, reboot notifiers, ktime debounce, and variant match data. `struct pm8941_data` captures per-compatible status bit, pull-up bit, feature support, default wake behavior, name, and phys path. `struct pm8941_pwrkey` stores regmap/base addresses, revision/subtype, IRQ, input, keycode, software debounce timing, last status, reboot notifier, and variant data. Main functions are `pm8941_reboot_notify`, `pm8941_pwrkey_irq`, `pm8941_pwrkey_sw_debounce_init`, probe, remove, suspend, and resume.

Control flow: probe reads requested debounce from DT defaulting to 15625 us, validates it, reads pull-up option, gets variant data, locates a regmap on parent or grandparent, reads base `reg` address and optional PON_PBS address, obtains IRQ, reads revision/subtype, reads optional `linux,code`, allocates input, programs hardware debounce for supported variants, derives software debounce from hardware/PBS debounce register, configures pull-up if applicable, requests threaded IRQ, registers input, registers reboot notifier when PS_HOLD config is supported, stores driver data, and initializes wakeup. IRQ handling applies software debounce after releases, reads `PON_RT_STS`, masks variant status bit, synthesizes a press if a release arrives without a prior press, updates `last_status`, reports the key, and syncs. Reboot notifier disables PS_HOLD, waits, writes warm/hard/shutdown reset type, and re-enables PS_HOLD.

State and persistence: `last_status` and `sw_debounce_end_time` shape event reporting. Hardware debounce, pull-up, and PS_HOLD reset configuration persist in PMIC registers. Wakeup state is device-managed.

Dependencies and integration points: compatibles include `qcom,pm8941-pwrkey`, `qcom,pm8941-resin`, `qcom,pmk8350-pwrkey`, and `qcom,pmk8350-resin`. Some GEN3 variants need a second PON_PBS address to read debounce timing.

Risks: debounce programming uses logarithmic math and hardware masks; invalid rounding can misprogram delays if assumptions change. Status bits are named active-low in hardware but reported directly after masking, so variant data must be correct. Reboot notifier writes critical reset behavior and must not race with shutdown paths. If PON_PBS address is missing for variants that require it, software debounce is skipped after an error log.

Test signals: test all compatible variants, parent and grandparent regmap layouts, base and optional PBS addresses, debounce validation/programming, pull-up configuration, press/release including synthetic press on release-only event, software debounce suppression, wake IRQ suspend/resume, reboot notifier for halt/poweroff/warm/hard restart, and notifier unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pm8941-pwrkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pm8xxx-vibrator.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/pm8xxx-vibrator.c

Purpose: `pm8xxx-vibrator.c` exposes Qualcomm PMIC vibrator hardware as an ff-memless rumble input device for PM8058/PM8921, PM8916, and PMI632-style register layouts.

Important APIs, types, and functions: it uses parent regmap, OF match data, input FF, and workqueues. `struct pm8xxx_regs` describes variant register offsets, masks, shifts, manual enable mask, and whether drive level is expressed in voltage steps. `struct pm8xxx_vib` stores input, work, regmap, register addresses, speed/level, active flag, and cached drive register value. Main functions are `pm8xxx_vib_set`, `pm8xxx_work_handler`, `pm8xxx_vib_close`, `pm8xxx_vib_play_effect`, probe, and suspend.

Control flow: probe allocates state and input, obtains the parent regmap, initializes work, reads the base `reg` property, gets variant register data from OF match, computes enable/drive addresses, reads the drive register, clears bits to force manual mode, caches the register value, configures input as EV_FF/FF_RUMBLE with memless callback, registers input, and stores driver data. FF playback converts strong magnitude to an 8-bit `speed` via `>> 8`, falling back to weak magnitude via `>> 9`, then schedules work. Work reads the current drive register, scales nonzero speed into the PMIC’s voltage range, sets `active`, and calls `pm8xxx_vib_set`. That function writes low and optional high drive-strength bits and toggles an enable bit if the variant has one. Close cancels work and turns off active vibration. Suspend unconditionally turns off the vibrator.

State and persistence: `speed`, `level`, `active`, and cached `reg_vib_drv` are runtime state. Hardware manual-mode and drive settings persist until changed or reset. No resume restoration is attempted.

Dependencies and integration points: compatibles map to `pm8058_regs`, `pm8916_regs`, or `pmi632_regs`. The driver requires a parent regmap and a `reg` base address. Input clients use standard rumble FF.

Risks: `pm8xxx_vib_set` divides `vib->level` by step size in place for step-based variants, so callers must ensure `level` has just been recomputed before each call; close/suspend with old state can reuse a modified level. Work reads the drive register but uses cached `reg_vib_drv` for writes after initial cache. Some regmap write errors simply stop the worker without input feedback. There is no locking around FF callback, work, close, and suspend beyond work cancellation in close.

Test signals: test each compatible register layout, base address parsing, manual-mode write, strong/weak/zero rumble scaling, two-register PMI632 drive writes, enable-bit variants, close and suspend stop paths, repeated effects, and regmap failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pm8xxx-vibrator.c -->
