# Research: subset-b-003964

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/hilkbd.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/hilkbd.c

Purpose: basic HP Human Interface Loop keyboard driver for HP300 and selected PA-RISC HP700 systems. It exposes a single `input_dev` named `HIL keyboard` on `BUS_HIL` and translates HIL set-1 scancodes through `hphilkeyb_keycode`.

Important APIs/types/functions: the central state is the file-static `hil_dev` with input device, current HIL device id, 16-byte packet buffer, spinlock, and native bus `dev_id`. `hil_interrupt()` decodes status/data/command response nibbles, `handle_status()` and `handle_data()` assemble poll blocks, `poll_finished()` reports key state, and `hil_do()` serializes HIL command writes. Platform integration is split between a PA-RISC `parisc_driver` and HP300 direct I/O region setup.

Control flow: init claims the IRQ, enables HIL interrupts, sends `HIL_READKBDSADR`, attempts to discover the keyboard, switches keyboard addressing to raw mode, registers input capabilities, then registers the input device. Runtime is interrupt driven: status bytes mark block start/end, data bytes fill the circular packet buffer, and block completion reports a key press/release from packet type `0x40`.

State/dependencies/integration: persistent state is only in RAM plus HIL hardware interrupt/config state. It depends on architecture-specific HIL MMIO accessors, `linux/hil.h` keycode tables, the input core, and PA-RISC/HP300 bus discovery.

Risks and test signals: `hil_keyb_init()` waits on a local wait queue that the IRQ path never wakes, so discovery can always wait for the timeout even if `hil_dev.valid` changes. `poll_finished()` calls `input_report_key()` without a local `input_sync()`, so event delivery depends on later synchronization. Tests should cover IRQ block framing, raw-mode command ordering, module unload interrupt disable/free, and architecture-specific init paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/hilkbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/hpps2atkbd.h -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/hpps2atkbd.h

Purpose: HP PA-RISC PS/2 AT keyboard raw set-2 scancode table consumed by the AT keyboard path. It maps normal and escaped PS/2 scancodes to Linux `KEY_*` codes for HP workstation and laptop layouts.

Important APIs/types/functions: this header does not define functions or storage wrappers; it is an initializer fragment. `CONFLICT()` and the temporary `C_*` macros choose between HP and RDI PrecisionBook mappings depending on `CONFIG_KEYBOARD_ATKBD_RDI_KEYCODES`.

Control flow: inclusion context supplies the target array declaration. The header expands into two contiguous 256-entry-style tables: base set-2 scancodes followed by escaped-key offsets. Conditional conflict macros adjust keys such as F12/F1, left alt/control, caps/control, and 102nd/left.

State/dependencies/integration: no runtime state exists. It depends on the input keycode namespace and the including keyboard driver using the table shape correctly. Integration is compile-time only, with `#undef` cleanup for the temporary macros.

Risks and test signals: because it is an initializer fragment, table length/order is the contract. Off-by-one edits, missing escaped entries, or changing `CONFIG_KEYBOARD_ATKBD_RDI_KEYCODES` behavior can silently remap many physical keys. Test by booting both HP and RDI layout configurations, checking representative conflict keys and escaped cursor/navigation keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/hpps2atkbd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/imx-sm-bbm-key.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/imx-sm-bbm-key.c

Purpose: NXP i.MX System Manager SCMI BBM power-button input driver. It converts SCMI IMX BBM button notifications into a wake-capable Linux key, defaulting to `KEY_POWER`.

Important APIs/types/functions: `struct scmi_imx_bbm` stores the SCMI protocol handle, BBM ops, notifier block, keycode, cached `keystate`, suspend flag, delayed work, and input device. `scmi_imx_bbm_key_probe()` acquires `SCMI_PROTOCOL_IMX_BBM`; `scmi_imx_bbm_pwrkey_init()` allocates/registers input and notifier; `scmi_imx_bbm_key_notifier()` schedules polling; `scmi_imx_bbm_pwrkey_check_for_events()` calls `button_get()` and reports state changes.

Control flow: probe enables wakeup and registers the notifier. A BBM button event calls `pm_wakeup_event()`, optionally synthesizes a press after resume, and schedules debounce work. The delayed worker reads firmware state, reports changed press/release events, relaxes the wakeup source after transition handling, and keeps polling every 60 ms while pressed.

State/dependencies/integration: all state is volatile driver data. It integrates with the SCMI bus (`module_scmi_driver`), NXP BBM SCMI protocol ops, input core, delayed work, and system suspend wakeup accounting. Removal uses a devm action to cancel delayed work.

Risks and test signals: the notifier assumes non-button BBM events are unexpected and only logs them. Resume behavior forces a press if suspended, so tests should validate no duplicate press when firmware already reports pressed. Exercise debounce, long press polling, release wake-relax, notifier unregister, and wake from suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/imx-sm-bbm-key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/imx_keypad.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/imx_keypad.c

Purpose: i.MX keypad-port matrix driver for `fsl,imx21-kpp`. It scans up to an 8x8 hardware matrix and reports key transitions through the input matrix-keypad API.

Important APIs/types/functions: `struct imx_keypad` holds clock, input device, MMIO base, IRQ, debounce timer, enabled flag, row/column masks, keycodes, and stable/unstable column states. Core functions are `imx_keypad_scan_matrix()`, `imx_keypad_check_for_events()`, `imx_keypad_fire_events()`, `imx_keypad_irq_handler()`, `imx_keypad_open()`, and `imx_keypad_close()`.

Control flow: probe builds a matrix keymap, derives enabled row/column masks from non-reserved keys, inhibits hardware until opened, requests IRQ, and enables wakeup. Open enables the clock, configures rows/columns, clears status bits, and enables key-depress interrupts. IRQ disables KDI/KRI and starts a near-term timer. The timer repeatedly scans until three stable readings, reports changed keys with `MSC_SCAN`, then either re-enables key-depress IRQ when all keys are released or polls/re-enables release IRQ while keys remain down.

State/dependencies/integration: runtime state lives in the debounce timer and matrix arrays; hardware state is in KPCR/KPSR/KDDR/KPDR. Dependencies include platform resources, `clk`, MMIO, timers, `matrix_keypad_build_keymap()`, and noirq PM wake handling.

Risks and test signals: scan timing is sensitive to capacitance discharge delays and open-drain sequencing. The open sanity check treats all enabled row lines low as hardware misconfiguration. Test multi-key press/release, debounce stability, clock enable/disable balance, noirq suspend with wake enabled, and matrix masks generated from sparse keymaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/imx_keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/imx_sc_key.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/imx_sc_key.c

Purpose: i.MX System Controller single-key driver. It maps an SCU wake/button interrupt to a firmware-polled Linux key configured by `linux,keycodes`.

Important APIs/types/functions: `struct imx_key_drv_data` stores keycode, cached state, delayed work, input device, SCU IPC handle, and notifier. `imx_sc_key_probe()` gets the SCU handle, reads firmware properties, registers input, enables the SC wake IRQ group, and registers a notifier. `imx_sc_key_notify()` schedules debounce work; `imx_sc_check_for_events()` sends `IMX_SC_MISC_FUNC_GET_BUTTON_STATUS`.

Control flow: notifier fires only for `SC_IRQ_BUTTON` in `SC_IRQ_GROUP_WAKE`; it wakes the parent and schedules work after 30 ms. The worker performs an SCU RPC, masks the first response byte as button state, reports a transition, relaxes wakeup on release, and reschedules every 60 ms while pressed.

State/dependencies/integration: no persistent storage is used. Dependencies are the NXP SCU firmware IPC API, `imx_scu_irq_*` notifier group, delayed work, input core, and firmware property parsing. Cleanup is a devm action that disables the SCU IRQ group, unregisters the notifier, and cancels work.

Risks and test signals: the RPC response contains dirty upper bytes, so only the low byte is valid. Missing `linux,keycodes` is fatal. Test notification filtering, press/release polling, wakeup reference release, cleanup order, and firmware errors from `imx_scu_call_rpc()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/imx_sc_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/ipaq-micro-keys.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/ipaq-micro-keys.c

Purpose: iPAQ h3600 Atmel micro companion key subdevice. It exposes nine fixed PDA button/navigation keycodes from messages delivered by the parent `ipaq_micro` MFD.

Important APIs/types/functions: `struct ipaq_micro_keys` contains the parent micro device, input device, and mutable keycode copy. `micro_key_receive()` decodes a one-byte message with bit 7 as down state and low 7 bits as key index. `micro_key_start()` and `micro_key_stop()` install/remove the parent callback under `micro->lock`.

Control flow: probe allocates input, copies the fixed `micro_keycodes`, sets `EV_KEY` capabilities, and registers open/close callbacks. Opening the input device hooks the parent callback; closing unhooks it. Suspend unconditionally stops receiving, and resume reattaches only if the input device is enabled.

State/dependencies/integration: state is the parent callback pointer and keycode array. It depends on `linux/mfd/ipaq-micro.h`, parent driver locking, platform-device binding, input core, and PM callbacks.

Risks and test signals: message length is not validated before reading `msg[0]`, so parent callback contract must guarantee at least one byte. Index 0 is accepted but the table comment starts at 1; tests should confirm parent numbering. Validate open/close races, suspend/resume while open, and unknown key index suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/ipaq-micro-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/iqs62x-keys.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/iqs62x-keys.c

Purpose: Azoteq IQS620A/621/622/624/625 key and switch child driver. It maps parent MFD event flags to input keys and hall switches.

Important APIs/types/functions: `struct iqs62x_keys_private` stores the parent core, input device, notifier, switch descriptors, keycode array, max count, and wheel interval cache. `iqs62x_keys_parse_prop()` reads `linux,keycodes` and optional `hall-switch-north/south` child nodes. `iqs62x_keys_init()` unmasks relevant parent event bits and seeds switch state. `iqs62x_keys_notifier()` reports keys/switches and handles reset reinitialization.

Control flow: probe parses firmware data, sets input capabilities, initializes hardware event masks per product family, registers input, then registers with the parent blocking notifier. On parent reset events it re-runs initialization. On normal events it reports all configured key flags and hall switch flags, then emulates wheel key release when interval changes indicate a wheel event.

State/dependencies/integration: state is volatile and tied to the parent `iqs62x_core`, regmap, `iqs62x_events[]`, and blocking notifier chain. Product-specific behavior changes event registers and masks.

Risks and test signals: keycode indices assume alignment with `iqs62x_events`. Wheel events require interval tracking and synthetic release, which is easy to regress. Test each supported product number, hall prox/touch child properties, reset notification, `KEY_RESERVED` masking, notifier unregister, and wheel up/down release generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/iqs62x-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/jornada680_kbd.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/jornada680_kbd.c

Purpose: HP Jornada 620/660/680/690 platform keyboard driver. It polls SuperH GPIO/control registers to scan an 18-byte keyboard matrix and reports a fixed Jornada keymap.

Important APIs/types/functions: `struct jornadakbd` stores input, keymap, and old/new scan buffers. `jornada_scan_keyb()` drives PD/PE scan lines through raw hardware addresses and reads row bytes from PC/PF plus extra PG/PH bytes. `jornada_parse_kbd()` diffs old/new buffers and emits `MSC_SCAN` plus key events. `jornadakbd680_poll()` is the input polling callback.

Control flow: probe creates input, copies `jornada_scancodes`, sets polling with a 50 ms interval, registers key and MSC capabilities, and registers input. Runtime is entirely poll driven: each poll scans all matrix lines, compares with prior state, reports changed bits as active-low key states, syncs if needed, then saves the new scan.

State/dependencies/integration: state persists only in scan buffers and keymap. Dependencies are platform-device binding, input polling, architecture raw I/O helpers, and hard-coded SH register addresses.

Risks and test signals: hard-coded register addresses and timing make this driver platform-specific and fragile. The parser can report keycode 0 entries if unused positions change. Test boot on supported Jornada variants, active-low release handling, polling interval behavior, and no event spam when matrix is stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/jornada680_kbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/jornada720_kbd.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/jornada720_kbd.c

Purpose: HP Jornada 710/720/728 keyboard driver. It drains keyboard scancodes from the Jornada SSP interface on a falling-edge platform IRQ.

Important APIs/types/functions: `struct jornadakbd` holds the keymap and input device. `jornada720_kbd_interrupt()` wraps the SSP transaction with `jornada_ssp_start()`/`jornada_ssp_end()`, sends `GETSCANKEYCODE`, reads a pending count, and reports each queued byte.

Control flow: probe gets IRQ, allocates driver/input state, copies `jornada_std_keymap`, sets input bits, requests a falling-edge IRQ, and registers input. On interrupt, the handler reads the number of waiting keycodes and then consumes each byte; low 7 bits are scancode and bit 7 is release, so `!(kbd_data & 0x80)` is reported as pressed.

State/dependencies/integration: state is only the keymap and input pointer. It depends on machine-specific `mach/jornada720.h` SSP helpers, platform IRQ resources, and input core.

Risks and test signals: SSP timeout handling logs but does not otherwise recover beyond bus flushing by the helper path. Keymap index trust requires the firmware/scanner to emit values below 128. Test queued multi-key packets, release-bit polarity, falling IRQ configuration, SSP failure path, and input registration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/jornada720_kbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/lkkbd.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/lkkbd.c

Purpose: DEC LK201/LK401 serial keyboard driver for serio RS232 adapters. It supports key events, LED updates, bell, keyclick, Ctrl-click, reset/ID handling, and LK401 extended mode.

Important APIs/types/functions: `struct lkkbd` stores keycode table, ignored ID bytes, input device, serio port, reinit work, names, type, and volume settings. `lkkbd_interrupt()` handles incoming bytes; `lkkbd_reinit()` sends reset/default/mode/audio/LED commands; `lkkbd_event()` handles `EV_LED` and `EV_SND`; `lkkbd_connect()`/`lkkbd_disconnect()` bind the serio device.

Control flow: connect allocates state, copies the keymap, opens serio, registers input, and sends a power-cycle reset. Initial response bytes are collected into `id`; after six bytes `lkkbd_detection_done()` names the keyboard and reports self-test/stuck-key results. Runtime key bytes toggle their current state because LK up/down mode sends one byte per transition. `LK_ALL_KEYS_UP` releases all mapped keys. A `0x01` reset response starts another ID collection and schedules reinitialization work.

State/dependencies/integration: runtime state lives in `ignore_bytes`, ID bytes, input LED/sound bits, and hardware mode programmed over serio. Integration is via `module_serio_driver`, input event callbacks, workqueue, and module parameters for volumes/layout behavior.

Risks and test signals: key state toggling depends on correct keyboard mode; missed bytes can invert state until `LK_ALL_KEYS_UP`. Work and interrupt paths share serio writes without deep protocol locking. Test reset/ID sequences, LK201 compose-as-alt parameter, LED/sound event writes, all-keys-up recovery, disconnect while work is pending, and unknown scancode logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/lkkbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/lm8323.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/lm8323.c

Purpose: National/TI LM8323 I2C keypad and PWM LED driver. It reports keypad FIFO events and exposes up to three PWM LED engines with fade-time attributes.

Important APIs/types/functions: `struct lm8323_chip` stores I2C client, input, keypad enable/suspend flags, key count, keymap, matrix size, debounce/active timing, and PWM objects. `lm8323_write()`/`lm8323_read()` implement command I2C transactions with one retry. `process_keys()` drains FIFO events, `lm8323_irq()` handles interrupt status, and PWM functions build scripts for the hardware engine.

Control flow: probe validates platform data, resets/configures the chip, reads ID, registers optional PWM LEDs, registers input, requests a threaded low IRQ, and enables IRQ wake. IRQ handling loops while interrupt status is nonzero, processing keypad events, errors, lost configuration, rotator notifications, and PWM completion. Key events are AT-style: low 7 bits are key index and bit 7 is press.

State/dependencies/integration: state includes key-down count used for the active-time erratum, `kp_enabled` sysfs state, PWM running/desired brightness, and suspend flag. Dependencies are I2C, platform data, input, LED class, sysfs attribute groups, IRQ wake, mutexes, and workqueues.

Risks and test signals: I2C helpers return short positive counts instead of normalized errors in some paths, so callers must handle non-length returns. FIFO overflow and lost config are hardware risk points. Test IRQ loops, key-down active-time transitions, `disable_kp`, PWM fade completion, suspend/resume with LED brightness changes, and missing/invalid platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/lm8323.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/lm8333.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/lm8333.c

Purpose: LM8333 I2C matrix keyboard controller driver. It configures debounce/active timing and reports FIFO key events to the input subsystem.

Important APIs/types/functions: `struct lm8333` stores client, input, and 8x16 keycodes. `lm8333_read8()`, `lm8333_write8()`, and `lm8333_read_block()` retry SMBus accesses because the first access can wake the chip. `lm8333_key_handler()` drains the 16-byte FIFO, and `lm8333_irq_thread()` handles status/error interrupts.

Control flow: probe requires platform data, validates active time greater than debounce time, builds matrix keymap, writes optional timing registers, requests a falling threaded IRQ, registers input, and stores client data. IRQ reads status, logs/clears error FIFO on overrun, then drains keypad FIFO and reports each nonzero event with `MSC_SCAN`.

State/dependencies/integration: all driver state is volatile. It depends on I2C SMBus, legacy `lm8333_platform_data`, input matrix keymap helpers, and threaded IRQs.

Risks and test signals: if FIFO read length is short, no events are reported. Error handling drains the FIFO but cannot reconstruct lost events. Test wake-retry behavior, active/debounce validation, FIFO terminator handling, overflow/key-overrun errors, and keymap bounds for 8 rows by 16 columns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/lm8333.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/locomokbd.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/locomokbd.c

Purpose: LoCoMo keyboard driver for Sharp Zaurus Collie/Poodle PDAs. It scans a 16x8 keyboard matrix behind the LoCoMo companion chip.

Important APIs/types/functions: `struct locomokbd` stores keycodes, input, physical name, LoCoMo base, spinlock, release-detection timer, and cancel-key suspend counters. `locomokbd_scankeyboard()` drives each column and reports all row states. `locomokbd_interrupt()` acknowledges press interrupts and starts scanning. `locomokbd_timer_callback()` continues scanning until no keys remain.

Control flow: probe claims memory, initializes timer/lock/keymap, requests IRQ, and registers input. Open enables keyboard interrupt generation; close disables it. A hardware interrupt only indicates key press, so the driver scans immediately and schedules periodic scans while any key is held to detect release. Long pressing the cancel/ESC key emits `EV_PWR KEY_SUSPEND`.

State/dependencies/integration: state is the timer, suspend-jiffies/count, and LoCoMo register state. It depends on the LoCoMo bus driver, raw register helpers, input core, spinlocks, timers, and manually managed allocation/IRQ/mem-region cleanup.

Risks and test signals: `input_report_key()` is called for every matrix position, including keycode 0 entries, though key bit 0 is cleared. Long-press suspend timing depends on `SCAN_INTERVAL`. Test press-only IRQ release polling, open/close interrupt gating, memory-region conflicts, timer shutdown on remove, and cancel long press behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/locomokbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/lpc32xx-keys.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/lpc32xx-keys.c

Purpose: NXP LPC32xx key scan interface driver for square matrices from 1x1 to 8x8. It uses the SoC scanner hardware and reports changed matrix bits.

Important APIs/types/functions: `struct lpc32xx_kscan_drv` stores input, clock, MMIO base, matrix size, debounce/scan delays, row shift, keymap, and last column states. `lpc32xx_parse_dt()` reads matrix properties and NXP timing properties. `lpc32xx_mod_states()` converts a changed hardware column byte into input events. `lpc32xx_kscan_irq()` scans all columns and clears IRQ.

Control flow: probe parses DT, allocates a keymap, configures input, maps resources, obtains clock, writes scanner debounce/scan/clock/matrix registers with the clock temporarily enabled, requests IRQ, and registers input. Open enables the clock and clears IRQ; close clears IRQ and disables the clock. Suspend/resume mirror clock handling when input is enabled.

State/dependencies/integration: state is lastkeystates and clock state. Dependencies include platform resources, DT `matrix-keypad` properties, `nxp,debounce-delay-ms`, `nxp,scan-delay-ms`, MMIO, clk, PM, and input matrix helpers.

Risks and test signals: only square matrices are accepted. The IRQ handler reads `matrix_sz` columns regardless of sparse keymap content. Test DT validation, key state diffing, clock balance across open/close/suspend/resume, IRQ clear behavior, and 1x1/8x8 limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/lpc32xx-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/maple_keyb.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/maple_keyb.c

Purpose: Sega Dreamcast Maple bus keyboard driver. It polls keyboard condition packets and maps USB-HID-like scancodes to Linux input events.

Important APIs/types/functions: `struct dc_kbd` stores input, a 256-entry keycode table, and old/new 8-byte report buffers. `dc_scan_kbd()` reports modifier bits and key-array changes. `dc_kbd_callback()` receives Maple queue completions. `probe_maple_kbd()` registers input and installs `maple_getcond_callback()`.

Control flow: probe allocates state, copies keymap, registers input, requests Maple condition polling at approximately VBLANK cadence, and stores driver data. Callback validates the function word, copies the report, and scans changes under a cleanup mutex. Removal locks the mutex, unregisters input, frees state, and clears driver data.

State/dependencies/integration: state is the two keyboard report buffers. It depends on Maple bus condition polling, input core, a global cleanup mutex, and manually allocated devices.

Risks and test signals: modifier keys are reported every scan, which is acceptable but noisy. In the non-modifier press path, the code reports a press only when the new code is found in the old report; this looks inverted for new key detection and should be regression-tested carefully. Test single key press/release, six-key rollover changes, callback during removal, unknown scancodes, and Maple function mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/maple_keyb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/matrix_keypad.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/matrix_keypad.c

Purpose: generic GPIO-driven matrix keypad platform driver. It scans row/column GPIO matrices with debounce and optional wakeup support.

Important APIs/types/functions: `struct matrix_keypad` stores input, row shift, timing properties, row/column GPIO descriptors, row IRQs, wake IRQ bitmap, last column state, delayed work, spinlock, and stopped/scan flags. `matrix_keypad_scan()` performs the column scan and reports diffs. `matrix_keypad_interrupt()` gates row IRQs and schedules debounce work. `matrix_keypad_start()`/`stop()` manage scan lifecycle.

Control flow: probe reads timing and drive-mode properties, gets GPIOs, normalizes active-low settings, requests row IRQs initially disabled, builds keymap, registers input, and initializes wakeup. Opening schedules an immediate scan that activates columns and enables row IRQs. Row IRQs disable all row IRQs and schedule delayed work. The worker reads initial rows, scans each column, reports changed key states with `MSC_SCAN`, reactivates all columns, re-enables IRQs, and reschedules if rows changed during scanning.

State/dependencies/integration: state is delayed work, GPIO directions/values, row IRQ enabled state, last key matrix, and wake IRQ bitmap. Dependencies are gpiod, IRQ core, input matrix helpers, firmware properties, and PM wake hooks.

Risks and test signals: active-low normalization and `drive-inactive-cols` determine electrical behavior; wrong firmware polarity can invert all keys. The worker enables IRQs before checking post-scan row changes, so tests should cover rapid transitions. Validate suspend wake IRQs, debounce timing, sparse keymaps, GPIO acquisition failures, and row/column count limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/matrix_keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/max7359_keypad.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/max7359_keypad.c

Purpose: Maxim MAX7359 I2C key-switch controller driver for an 8x8 matrix. It reports FIFO events and manages controller autosleep.

Important APIs/types/functions: `struct max7359_keypad` stores keycodes, input, and client. `max7359_read_reg()`/`write_reg()` wrap SMBus accesses. `max7359_interrupt()` reads one FIFO byte and reports row/column press or release. `max7359_open()` and `max7359_close()` switch between short and long autosleep.

Control flow: probe requires a nonzero IRQ, reads the initial FIFO for device presence, allocates input, builds the keymap from platform data, requests a low threaded IRQ, registers input, initializes config/debounce/interrupt/autosleep registers, and enables device wakeup. IRQ decodes row bits, column bits, and release bit, emits `MSC_SCAN`, reports the mapped key, and syncs.

State/dependencies/integration: state is minimal and volatile; controller power state persists in hardware autosleep registers. Dependencies are I2C SMBus, matrix keymap platform data, threaded IRQ, input core, and PM wake.

Risks and test signals: the IRQ handler reads only one FIFO event per interrupt, so burst behavior depends on the chip retriggering. It does not check negative FIFO read before decoding. Test FIFO empty/error handling, press/release polarity, autosleep on open/close/suspend/resume, wake IRQ enable, and keymap bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/max7359_keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/max7360-keypad.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/max7360-keypad.c

Purpose: MAX7360 MFD keypad child driver. It uses the parent regmap and `intk` IRQ to report matrix FIFO events with firmware-described keymap and dimensions.

Important APIs/types/functions: `struct max7360_keypad` holds input, row/col count, debounce, IRQ, regmap, and keycodes. `max7360_keypad_irq()` drains/handles a FIFO event. `max7360_keypad_parse_fw()` reads matrix dimensions, autorepeat, and debounce. `max7360_keypad_build_keymap()` reads the parent `linux,keymap`. Open/close manipulate `MAX7360_CFG_SLEEP`.

Control flow: probe gets parent regmap and named IRQ, parses parent firmware properties, allocates input, builds keymap, requests a threaded IRQ, registers input, initializes debounce and interrupt timing, then enables wakeup via `dev_pm_set_wake_irq()`. IRQ reads `MAX7360_REG_KEYFIFO`, skips overflow by polling for a non-overflow value, ignores empty FIFO, decodes row/col/release fields, and reports the mapped key.

State/dependencies/integration: state lives in regmap-backed hardware and input keycodes. It depends on MAX7360 MFD definitions, regmap, firmware properties on the parent node, input matrix helpers, threaded IRQ, and PM wake IRQ helpers.

Risks and test signals: keymap parsing deliberately reads from `dev->parent`, so child/parent firmware layout must match. Overflow recovery drops unknown events. Test parent property lookup, debounce bounds, sleep bit polarity, overflow and empty FIFO behavior, wake IRQ setup/clear, and unsupported dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/max7360-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/mpr121_touchkey.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/mpr121_touchkey.c

Purpose: Freescale/NXP MPR121 capacitive touch-key driver. It configures up to 12 electrodes and reports touch/release bits as Linux keys, via IRQ or input polling.

Important APIs/types/functions: `struct mpr121_touchkey` stores client, input, cached status bits, keycount, and keycodes. `mpr121_phys_init()` writes thresholds, filter/AFE/autoconfig registers, and electrode enable. `mpr_touchkey_report()` reads status bytes, diffs against cached bits, and reports changed keys. `mpr_touchkey_probe()` handles regulator voltage, keycode properties, IRQ/poll setup, and input registration.

Control flow: probe enables `vdd` and reads voltage for autoconfig thresholds, reads `linux,keycodes`, configures input, initializes hardware, chooses IRQ or polling, and registers input. Runtime reads two status bytes, masks 12 touch bits, reports changes with `MSC_SCAN`, and updates cache. Suspend disables electrodes; resume re-enables `keycount` electrodes.

State/dependencies/integration: state is cached status bits and hardware electrode configuration. Dependencies are I2C SMBus, regulator voltage, firmware properties, optional IRQ, input polling, and PM.

Risks and test signals: the threshold initialization loop uses `i <= MPR121_MAX_KEY_COUNT`, which appears to program one more electrode threshold pair than the 12-key limit. Resume writes `keycount` without the quick-charge bit used at init. Test IRQ and polling modes, keycount zero/too large, voltage-derived autoconfig values, suspend/resume touch recovery, and I2C read/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/mpr121_touchkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/mt6779-keypad.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/mt6779-keypad.c

Purpose: MediaTek MT6779/MT6873 keypad driver. It reads hardware memory registers representing key states and maps them to matrix key events.

Important APIs/types/functions: `struct mt6779_keypad` stores regmap, input, clock, matrix dimensions, row/column calculation function, and previous bitmap state. `mt6779_keypad_irq_handler()` bulk reads state registers and reports changed bits. `mt6779_keypad_calc_row_col_single()` and `_double()` decode key numbers for one or two keys per group.

Control flow: probe maps MMIO through regmap, initializes previous state to all released, parses matrix dimensions, debounce, and `mediatek,keys-per-group`, builds keymap, writes debounce and row/column selection registers, enables the `kpd` clock, requests a threaded IRQ, registers input, and initializes wakeup. IRQ reads five memory registers, compares with prior bitmap, skips unused upper halfwords, converts each changed bit to row/column/scancode, reports active-low press state, syncs, and saves the new bitmap.

State/dependencies/integration: state is bitmap keymap_state and hardware configuration registers. Dependencies are platform MMIO, regmap, clock, matrix keypad properties, input core, and optional wakeup-source.

Risks and test signals: row/column decode is SoC-layout-specific; invalid `keys-per-group` is fatal. `regmap_bulk_read()` return value is not checked in the IRQ path. Test single/double group mappings, debounce max, active-low bit interpretation, sparse keymap, clock availability, and bulk-read error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/mt6779-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/mtk-pmic-keys.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/mtk-pmic-keys.c

Purpose: MediaTek PMIC power/home key driver for MT6397, MT6323, MT6331, MT6357, MT6358, and MT6359 families. It reports PMIC debounced key state and configures optional long-press reset behavior.

Important APIs/types/functions: `struct mtk_pmic_regs` provides per-chip register layouts; `struct mtk_pmic_keys_info` stores per-key registers, keycode, IRQs, and wake flag; `struct mtk_pmic_keys` stores input, device, regmap, and two key slots. `mtk_pmic_key_setup()` configures interrupt selection and IRQs. `mtk_pmic_keys_irq_handler_thread()` reads the debounce register and reports key state. `mtk_pmic_keys_lp_reset_setup()` programs long-press reset mode.

Control flow: probe gets the parent `mt6397_chip` regmap, matches chip data, allocates input, iterates child key nodes in fixed power/home order, gets named IRQs and optional release IRQs, reads `linux,keycodes`, sets wake flags, requests IRQs, registers input, then programs long-press reset. Suspend/resume enable or disable IRQ wake for per-key wake sources.

State/dependencies/integration: state is per-key metadata and PMIC registers. Dependencies are MFD register headers, parent regmap, OF child nodes, platform named IRQs, input core, and PM.

Risks and test signals: child iteration order must match fixed `powerkey`/`homekey` arrays. Some chip data differs in release IRQ support. The MT6357 home reset mask entry uses `MTK_PMIC_HOMEKEY_INDEX`, which deserves validation against hardware definitions. Test all compatible tables, one-key/two-key reset modes, press and release IRQ variants, wakeup-source handling, and missing child properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/mtk-pmic-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/newtonkbd.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/newtonkbd.c

Purpose: Apple Newton serial keyboard driver. It maps 7-bit Newton scancodes with a press bit into Linux key events through serio.

Important APIs/types/functions: `struct nkbd` stores the 128-byte keycode map, input device, serio port, and physical path. `nkbd_interrupt()` decodes incoming bytes using `NKBD_KEY` and `NKBD_PRESS`. `nkbd_connect()` allocates/registers input and opens serio; `nkbd_disconnect()` closes/unregisters/frees.

Control flow: connect copies the static keymap, sets `BUS_RS232` ids, marks all mapped keys and autorepeat, opens serio, and registers input. Runtime ignores unmapped scancodes except for `0xe7`, which logs end of initialization; mapped scancodes report `data & NKBD_PRESS` as key state and sync immediately.

State/dependencies/integration: no persistent state beyond the keymap and input/serio associations. Integration is via `module_serio_driver` with `SERIO_NEWTON`.

Risks and test signals: the keycode map uses byte-sized storage, but Linux keycodes here fit the selected values. Invalid initialization bytes are intentionally ignored. Test connect failure unwinding, press/release polarity, init-sequence logging, unknown scancodes, autorepeat bit, and disconnect ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/newtonkbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/nspire-keypad.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/nspire-keypad.c

Purpose: TI-Nspire keypad MMIO driver. It configures continuous hardware scanning over an 8x11 matrix and reports changed bits.

Important APIs/types/functions: `struct nspire_keypad` stores register base, interrupt mask, input, clock, row shift, scan/row delays, cached row state, and active-low flag. `nspire_keypad_open()` programs scan timing and enables interrupts. `nspire_keypad_irq()` reads data rows, applies polarity, diffs state, and reports transitions.

Control flow: probe reads required `scan-interval` and `row-delay` DT properties, gets clock and MMIO, disables/acks keypad and unknown GPIO interrupts with the clock temporarily enabled, builds keymap, requests IRQ, and registers input. Open enables clock and continuous scanning; close masks/acks interrupts and disables clock. IRQ validates status, copies 8 row words from data registers, reports changed row/column bits, syncs, and acknowledges interrupt bits.

State/dependencies/integration: state is cached row bitmasks and hardware scan registers. Dependencies include OF properties, MMIO, clock, input matrix helpers, IRQ, and platform resources.

Risks and test signals: delay-cycle calculations warn but mask overflow, so invalid timing can silently truncate. The debug print swaps row_delay and scan_interval arguments. Test active-low polarity, timing property bounds, open/close clock balance, unknown interrupt disable, row/column map coverage, and spurious IRQ returning `IRQ_NONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/nspire-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/omap-keypad.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/omap-keypad.c

Purpose: legacy OMAP1 MPUIO keypad driver. It scans a platform-data-described matrix using OMAP1 I/O registers, tasklet processing, and a timer while keys remain down.

Important APIs/types/functions: file-static `keypad_state`, `kp_enable`, and `kp_cur_group` hold global scanner state. `struct omap_kp` stores input, timer, IRQ, dimensions, delay/debounce, and flexible keymap. `omap_kp_interrupt()` masks IRQ and schedules `kp_tasklet`; `omap_kp_tasklet()` scans, reports diffs, and manages polling; sysfs `enable` toggles IRQ.

Control flow: probe validates platform data, disables MPUIO keyboard interrupt, builds keymap, registers input, enables optional debouncing, scans initial state, requests IRQ, and unmasks keyboard interrupt. IRQs are masked immediately; the tasklet scans each column and reports changed keys. If any key remains down, a timer reschedules scans at 20 Hz; otherwise IRQs are unmasked and group filtering resets.

State/dependencies/integration: state is global, so the driver effectively assumes one keypad. Dependencies are OMAP1 MPUIO register access, platform data, tasklets, timer, input matrix helpers, and sysfs attribute groups.

Risks and test signals: global state and tasklet object are not per-device. Group filtering masks keys by `GROUP_MASK` and can suppress events outside the active group. Test enable sysfs races, timer release detection, platform-data validation, grouped keymaps, debounce register behavior, and remove path tasklet/timer shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/omap-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/omap4-keypad.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/omap4-keypad.c

Purpose: OMAP4/OMAP5 keypad controller driver. It reads hardware full-code registers, reports matrix transitions, and uses runtime PM to handle auto-idle and wake.

Important APIs/types/functions: `struct omap4_keypad` stores input, base, IRQ, scan mutex, dimensions, revision offsets, row shift, no-autorepeat flag, cached key bitmap, keymap, and function clock. `omap4_keypad_scan_keys()` diffs bitmaps and reports releases before presses. `omap4_keypad_irq_thread_fn()` reads full-code registers. `omap4_keypad_runtime_suspend()` works around erratum i689 by clearing stuck releases after idle.

Control flow: probe enables runtime PM, reads revision to choose register offsets, stops hardware interrupts, allocates input/keymap, requests threaded IRQ, registers input, and sets wake IRQ. Open resumes runtime PM, enables clock, programs control/debounce/IRQ/wakeup registers, and enables IRQ. IRQ top half wakes the thread only if IRQSTATUS is nonzero; thread resumes device, reads low/high key bitmaps, scans changes, clears pending IRQs, and autosuspends. Close disables IRQs and clock.

State/dependencies/integration: state is cached 64-bit key bitmap, runtime PM state, hardware registers, and wake IRQ registration. Dependencies include OF matrix properties, clock, MMIO, input core, threaded IRQ, runtime PM, and PM wakeirq.

Risks and test signals: erratum handling relies on runtime suspend seeing an idle state machine before forcing all keys up. Revision offset handling must be correct for OMAP4 vs OMAP5. Test missed key-up recovery, runtime PM autosuspend, open/close clock balance, wake IRQ setup, no-autorepeat property, and unsupported revision rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/omap4-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/opencores-kbd.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/opencores-kbd.c

Purpose: simple platform driver for the OpenCores keyboard controller. It reads one byte per interrupt and reports key state directly.

Important APIs/types/functions: `struct opencores_kbd` stores input, mapped register address, IRQ, and 128 identity keycodes. `opencores_kbd_isr()` reads the data byte and reports low 7 bits as keycode, with bit 7 meaning release. `opencores_kbd_probe()` maps MMIO, initializes identity keymap, requests IRQ, and registers input.

Control flow: probe gets IRQ/MMIO, sets `BUS_HOST` IDs, fills keycodes 0..127, marks key bits, requests rising-edge IRQ, and registers input. Runtime IRQ reads the controller byte, reports press when bit 7 is clear and release when set, then syncs.

State/dependencies/integration: no mutable runtime state beyond input and MMIO mapping. Dependencies are platform resources, MMIO, interrupt core, and input.

Risks and test signals: the controller scancode is assumed to equal Linux `KEY_*` value, which limits layout flexibility. No `MSC_SCAN` is emitted. Test identity mapping expectations, release-bit polarity, rising-edge IRQ behavior, MMIO read side effects, and probe errors for missing IRQ/resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/opencores-kbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/pinephone-keyboard.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/pinephone-keyboard.c

Purpose: Pine64 PinePhone keyboard I2C driver. It reports a 6x12 matrix plus FN layer, validates scan CRCs, controls keyboard scanning for power, and optionally exposes the keyboard accessory's tunneled SMBus adapter.

Important APIs/types/functions: `struct pinephone_keyboard` stores optional `i2c_adapter`, input, double scan buffers, CRC table, FN state per column, buffer selector, and current FN press state. `ppkb_update()` reads scan data and reports diffs. `ppkb_adap_smbus_xfer()` proxies SMBus byte-data operations through keyboard firmware registers. `ppkb_open()`/`close()` enable or disable scanning.

Control flow: probe enables `vbat`, reads and validates device ID/firmware/matrix size, disables scanning by default, optionally registers a child I2C adapter from an `i2c` child node, builds the CRC table, allocates input, builds static normal/FN keymap, registers input, and requests a threaded IRQ. IRQ calls `ppkb_update()`, which reads CRC+columns, verifies CRC8, swaps buffers, reports changed normal or FN-layer scancodes, tracks FN key state, and syncs.

State/dependencies/integration: state includes scan buffers, FN state used to report releases against the layer active at press time, firmware scan-enable bit, regulator state, child I2C adapter, and input keymap. Dependencies are I2C SMBus block reads/writes, regulator, OF, CRC8, input matrix helpers, and threaded IRQ.

Risks and test signals: FN state tracking is subtle; release scancode must match the layer selected when pressed, not current FN state. CRC failures intentionally drop whole scans. Test bad CRC, scan enable/disable on open/close, FN press/hold/release combinations, child SMBus read/write proxy status handling, unexpected firmware matrix size, and IRQ before input open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/pinephone-keyboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/pmic8xxx-keypad.c -->
## sources/distributed-fs/ceph-client/drivers/input/keyboard/pmic8xxx-keypad.c

Purpose: Qualcomm PM8058/PM8921 PMIC keypad matrix driver. It programs PMIC keypad timing, reads recent/old scan arrays, handles stuck-key interrupts, filters ghost keys, and reports matrix events.

Important APIs/types/functions: `struct pmic8xxx_kp` stores dimensions, input, regmap, sense/stuck IRQs, keycodes, device, current and stuck states, and cached control register. `pmic8xxx_kpd_init()` validates/programs rows, columns, scan delay, row hold, and debounce. `pmic8xxx_kp_read_matrix()` implements the synchronous read protocol. `pmic8xxx_kp_scan_matrix()` interprets event counters and reports transitions; `pmic8xxx_detect_ghost_keys()` filters ambiguous multi-key states.

Control flow: probe parses matrix properties and timing/wakeup flags, gets parent regmap and two IRQs, builds keymap, initializes state arrays to released, programs hardware, requests sense and stuck IRQs, reads the control register, registers input, and sets wakeup. Open sets `KEYP_CTRL_KEYP_EN`; close clears it. Sense IRQ reads event count from `KEYP_CTRL`, reads recent/old matrices as needed, reports releases/presses, and updates cached state. Stuck IRQ reads matrices and compares against `stuckstate`.

State/dependencies/integration: state is cached key matrices, control register, PMIC hardware registers, and wake configuration. Dependencies include parent regmap, OF matrix properties, input matrix helpers, IRQs, delays tied to 32 kHz clock, and PM callbacks.

Risks and test signals: synchronous read timing and event counter cases are hardware-sensitive. Ghost-key detection drops the scan without error. Suspend disables the keypad unless wakeup is enabled. Test one/two/lost event paths, stuck IRQ behavior, ghost detection, timing property validation, wake/non-wake suspend paths, and open/close enable bit preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/pmic8xxx-keypad.c -->
