# subset-b-003965 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/pxa27x_keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/pxa27x_keypad.c

## Purpose

This platform driver supports the Marvell/PXA27x keypad controller, including matrix keys, direct GPIO-like keys, and up to two rotary encoders. It exposes all detected inputs through the Linux input subsystem and uses firmware properties to describe matrix dimensions, direct-key masks, rotary behavior, keymaps, and debounce timing.

## Important APIs, Types, and Functions

`struct pxa27x_keypad` owns the clock, MMIO base, IRQ, keycode table, current matrix/direct state, and rotary descriptors. Property parsing is split across `pxa27x_keypad_matrix_key_parse()`, `pxa27x_keypad_direct_key_parse()`, and `pxa27x_keypad_rotary_parse()`. Event paths are `pxa27x_keypad_scan_matrix()`, `pxa27x_keypad_scan_direct()`, `pxa27x_keypad_scan_rotary()`, and `pxa27x_keypad_irq_handler()`. `pxa27x_keypad_config()` programs `KPC`, `KPREC`, and debounce registers; input `open`/`close` gate the controller clock.

## Control Flow

Probe obtains IRQ, MMIO, clock, and an input device, builds keymaps from matrix-keypad bindings, requests the IRQ, registers input, and marks the device wake-capable. Opening the input device enables the clock and writes controller configuration. The IRQ handler reads `KPC`, dispatches direct/rotary and matrix scanners based on pending bits, and reports `MSC_SCAN` plus key or relative events. Matrix scanning decodes either the single-key `KPAS` fields or multi-key `KPASMKP*` registers and compares them with cached column state.

## State and Persistence Behavior

The driver persists only runtime input state: prior matrix columns, prior direct-key mask, rotary default counter value, and firmware-derived keycode arrays. Hardware configuration persists while the clock remains enabled. Suspend keeps the clock active only for wake-capable use; otherwise it disables and later reprograms the controller if the input device is still open.

## Dependencies and Integration Points

It depends on platform devices, MMIO registers, a clock, IRQ delivery, generic firmware properties, and `matrix_keypad_build_keymap()`. DT matching uses `marvell,pxa27x-keypad`; direct and rotary properties are Marvell-specific.

## Risks and Edge Cases

Direct-key default mask calculation uses `GENMASK(direct_key_num - 1, 0)`, so a malformed configuration with no direct/rotary keys must not reach that branch. Rotary reporting has both relative and synthetic press/release modes, and invalid property combinations can silently change event semantics. Matrix multi-key registers expose eight columns regardless of configured columns, so bounds and state comparison matter. The rotary scan loop always calls `report_rotary_event(keypad, 0, ...)`, which makes the second encoder path suspicious.

## Test Signals

Useful tests include DT/property validation for matrix-only, direct-only, and mixed layouts; keymap bounds failures; low-active direct keys; relative and keycode rotary modes; multi-key matrix changes; suspend/resume with and without wakeup; open/close clock balancing; and IRQ storms with no state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/pxa27x_keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/qt1050.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/qt1050.c

## Purpose

This I2C driver supports the Microchip AT42QT1050 five-channel capacitive touch key controller. It identifies the chip, configures enabled pads from child firmware nodes, applies per-key charge/sampling/threshold parameters, recalibrates and resets the chip, and reports configured keys through the input subsystem.

## Important APIs, Types, and Functions

`struct qt1050_priv` stores the I2C client, regmap, input device, configured key descriptors, registered-key mask, and last-key bitmap. The regmap configuration defines readable, writable, cached, and volatile registers. `qt1050_identify()` validates chip ID and firmware version. `qt1050_parse_fw()` reads child-node `reg`, `linux,code`, and Microchip tuning properties. `qt1050_apply_fw_data()` disables all channels, then enables and programs configured keys. `qt1050_irq_threaded()` clears detection status, reads key status, and reports deltas.

## Control Flow

Probe checks SMBus byte support and a required IRQ, initializes regmap/input state, identifies the chip, parses firmware key nodes, sets key capabilities, triggers calibration, waits for completion via `regmap_read_poll_timeout()`, performs a soft reset, writes configuration, requests a threaded IRQ, clears the change line, and registers input. On interrupt, it reads detection status to clear the line, maps sparse hardware key bits into a five-bit logical bitmap, masks to registered keys, reports changed key states, updates `last_keys`, and syncs.

## State and Persistence Behavior

Persistent runtime state is the cached `last_keys`, configured key table, and regmap cache for nonvolatile writable registers. Hardware retains channel thresholds and low-power mode until reset or suspend changes it. Suspend disables IRQ and writes `QT1050_LPMODE` to either a one-second measurement interval for wakeup or off; resume re-enables IRQ and restores a 16 ms interval.

## Dependencies and Integration Points

The driver integrates with I2C, regmap, firmware child nodes, IRQ threading, and input key events. It uses `REGCACHE_MAPLE` and relies on the chip's change line for event delivery.

## Risks and Edge Cases

The optional numeric properties silently fall back to defaults when not power-of-two or out of range, so board tuning mistakes may look like valid defaults. IRQ handling returns `IRQ_NONE` on I/O failure, which can interact poorly with level-triggered lines. Key status bits are sparse and remapped manually, making regressions easy if a future chip variant differs.

## Test Signals

Tests should cover valid/invalid child-node counts, missing `linux,code` or `reg`, reserved and out-of-range keycodes, tuning conversions, calibration timeout, reset failure, IRQ state changes, suspend low-power programming, wakeup mode, and regmap access-table enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/qt1050.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/qt1070.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/qt1070.c

## Purpose

This I2C input driver supports the Atmel AT42QT1070 seven-key QTouch sensor. It provides a fixed keymap from hardware channels 0-6 to `KEY_0` through `KEY_6`, handles the change IRQ, and reports key state changes.

## Important APIs, Types, and Functions

`struct qt1070_data` holds the client, input device, IRQ, editable keycode table, and last key bitmap. `qt1070_read()` and `qt1070_write()` wrap SMBus byte access with logging. `qt1070_identify()` validates chip ID and reads firmware version. `qt1070_interrupt()` clears detection status, reads key status, compares against `last_keys`, and reports changed bits. `qt1070_suspend()` and `qt1070_resume()` only toggle IRQ wake when the device may wake the system.

## Control Flow

Probe verifies SMBus byte support and the presence of an IRQ, identifies the chip, allocates state/input, initializes capabilities and keycodes, calibrates, resets, requests a threaded IRQ, registers input, stores client data, and clears the change line. Interrupt flow is simple: read detection status for acknowledge, read `KEY_STATUS`, walk the seven bits, report only changed keys, sync, and cache the new bitmap.

## State and Persistence Behavior

The driver has no dynamic configuration beyond the fixed keycode array and `last_keys`. Calibration and reset affect chip-local state during probe. Power management preserves operation and only configures IRQ wake, so any deeper chip power policy is left to the board or parent power domain.

## Dependencies and Integration Points

It depends on I2C SMBus byte transfers, a wired IRQ, input key events, and optional OF matching using compatible `qt1070`. The I2C device ID table exposes `qt1070` for non-DT systems.

## Risks and Edge Cases

There is no firmware keymap customization, so boards needing different keycodes must patch or remap in userspace. `qt1070_interrupt()` stores negative read results into `u8 new_keys` if the key-status read fails, which can produce bogus events after an I2C error. IRQ trigger flags are `IRQF_TRIGGER_NONE | IRQF_ONESHOT`, relying on firmware or board setup for electrical triggering.

## Test Signals

Test chip ID mismatch, missing IRQ, SMBus failure, probe calibration/reset ordering, press/release transitions for all seven bits, I2C read errors during IRQ, wakeup-enabled suspend/resume, and module autoload through I2C and OF tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/qt1070.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/qt2160.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/qt2160.c

## Purpose

This I2C driver supports the Atmel AT42QT2160 touch sense controller as a 16-key input device and, when LED class support is enabled, as an eight-LED controller backed by the chip's X-drive/PWM outputs.

## Important APIs, Types, and Functions

`struct qt2160_data` stores the client, input device, keycodes, last key matrix, and optional `qt2160_led` array. `qt2160_read_block()` reads consecutive chip registers using raw I2C when available or sequential SMBus byte reads otherwise. `qt2160_get_key_matrix()` reads general status through GPIO registers and reports key deltas. `qt2160_irq()` invokes that scanner for IRQ mode; `input_setup_polling()` is used when no IRQ exists. LED integration is in `qt2160_led_set()` and `qt2160_register_leds()`.

## Control Flow

Probe validates SMBus support, identifies the chip, allocates state/input, fills a fixed 16-key keymap, calibrates the device, chooses IRQ or polling event delivery, registers optional LEDs, and registers input. IRQ or poll callbacks read the status/key block, combine key bytes into a 16-bit matrix, compare it with the previous matrix, report changed keys, and sync. LED brightness changes read and update drive/PWM enable registers, then write a global PWM duty register when turning an LED on.

## State and Persistence Behavior

The cached `key_matrix` is the event delta base. LED state is cached per LED in software, but PWM duty is a chip-global value shared by all LEDs. Hardware calibration and LED drive registers persist until changed or reset. There is no explicit PM implementation in this file.

## Dependencies and Integration Points

It integrates with I2C/SMBus, optional raw I2C receive, input polling, threaded IRQs, and the LED class. The I2C ID table is `qt2160`; no OF match table is present here.

## Risks and Edge Cases

`qt2160_read_block()` treats a short `i2c_master_recv()` as an error but returns the byte count, which may be positive and ambiguous to callers. LED brightness is globally limited by hardware, so per-LED brightness expectations are misleading. Polling every two seconds is slow for keyboard-like use if no IRQ is wired. No PM hooks means suspend behavior depends on the I2C core and board power.

## Test Signals

Test ID/version reads, calibration write failure, IRQ and polling modes, all 16 key transitions, short/raw I2C read behavior, SMBus fallback, LED register programming with multiple LEDs, LED class cleanup, and module load on systems without `CONFIG_LEDS_CLASS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/qt2160.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/samsung-keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/samsung-keypad.c

## Purpose

This platform driver supports Samsung S3C/S5P matrix keypad controllers. It scans rows and columns through MMIO registers, reports Linux input key events, supports platform data and DT bindings, handles runtime/system PM, and configures wakeup for keypad interrupts.

## Important APIs, Types, and Functions

`struct samsung_keypad` contains chip metadata, input device, clock, MMIO base, wait queue, stopped/wake flags, dimensions, cached row state, and keycodes. `samsung_keypad_scan()` drives each column and reads rows. `samsung_keypad_report()` compares new state with cached state. `samsung_keypad_irq()` loops while keys remain pressed. `samsung_keypad_start()` and `samsung_keypad_stop()` manage clock and interrupts. PM paths include runtime suspend/resume and system suspend/resume with wake toggling.

## Control Flow

Probe parses platform data or DT child key nodes, validates dimensions, optionally configures GPIOs, maps MMIO, obtains a prepared clock, builds the keymap, requests a threaded IRQ, enables runtime PM, registers input, and frees temporary DT platform data. Opening the input device starts the controller. The IRQ thread clears pending bits, scans the matrix, reports changed keys, and if any key is down waits up to 50 ms before rescanning; this continues until release or stop.

## State and Persistence Behavior

`row_state[]` is the persistent software snapshot of pressed keys. `stopped` coordinates close/suspend with the IRQ polling loop. Wake enable state is tracked separately for runtime PM. Hardware interrupt, wake, and column registers persist only while the clock and controller are active.

## Dependencies and Integration Points

The driver depends on platform/OF data, `matrix_keypad_build_keymap()`, Samsung keypad register layout, clocks, runtime PM, and input `open`/`close` callbacks. Chip variants differ by column bit shift and are selected from OF data or platform IDs.

## Risks and Edge Cases

The IRQ thread actively polls while keys are held, so stuck keys can keep the device busy. DT parsing reads child properties without checking individual property read errors. Start/stop and runtime PM both manipulate clocks and wake bits, so clock balance and stopped-state transitions are important. S5PV210 row/interrupt masks are defined but the scan path only uses generic row masks through dimension limits.

## Test Signals

Tests should cover S3C and S5PV210 variants, DT and platform-data keymaps, held-key polling, close during IRQ wait, no-autorepeat, runtime suspend/resume while open and closed, wakeup suspend/resume, invalid dimensions, and clock/IRQ failure unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/samsung-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/sh_keysc.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/sh_keysc.c

## Purpose

This platform driver supports the SuperH KEYSC matrix keypad controller. It uses board-provided `struct sh_keysc_info` to select a hardware scan mode, scan timing, keycodes, and debounce delays, then reports matrix key events through the input subsystem.

## Important APIs, Types, and Functions

`struct sh_keysc_priv` stores the MMIO base, last-key bitmap, input device, and copied platform data. `sh_keysc_mode[]` maps controller modes to keyout/keyin counts and KYMD values. `sh_keysc_read()` and `sh_keysc_write()` access 16-bit registers. `sh_keysc_level_mode()` arms level IRQ mode. `sh_keysc_isr()` performs the full matrix scan, debouncing/intersection logic, and event reporting. Probe/remove manually allocate and tear down resources.

## Control Flow

Probe requires platform data, MMIO resource, and IRQ, maps registers, allocates input, requests a threaded IRQ, sets key capabilities, registers input, enables runtime PM, programs KYCR1, enters level mode, and enables wakeup. The ISR disables IRQ generation, drives each output line low, reads input lines, accumulates repeated scan results into `keys0` and `keys1`, restores level mode, and loops while the controller indicates pending activity. It then compares with `last_keys` and emits press/release events.

## State and Persistence Behavior

`last_keys` tracks currently reported keys. Platform data is copied into driver state so board data persists after probe. Runtime PM is held active after probe and released on remove or non-wakeup suspend. Suspend can set a wake bit in KYCR1 and enable IRQ wake.

## Dependencies and Integration Points

It depends on legacy platform data (`linux/input/sh_keysc.h`), platform IRQ/MMIO resources, runtime PM, and SuperH KEYSC register semantics. There is no DT parser in this file.

## Risks and Edge Cases

Manual allocation and cleanup increase unwind risk compared with devm-managed drivers. Invalid platform mode values could index outside `sh_keysc_mode[]` unless board data is trusted. The scan algorithm is timing-sensitive (`delay`, `kycr2_delay`) and may misreport on boards with slow lines. Wake/runtime PM behavior assumes the controller remains configured across low-power transitions.

## Test Signals

Test each KEYSC mode, invalid or missing platform data, IRQ scan with simultaneous keys, release detection, timing extremes, runtime PM suspend/resume with and without wakeup, remove cleanup after registered input, and keycode arrays containing zero/reserved entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/sh_keysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/snvs_pwrkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/snvs_pwrkey.c

## Purpose

This platform driver reports the i.MX SNVS ON/OFF key as an input power key. It configures SNVS low-power control bits through a syscon regmap, handles short/long press status, emulates press/release behavior for early silicon, and supports wakeup through the PM wake IRQ framework.

## Important APIs, Types, and Functions

`struct pwrkey_drv_data` stores the SNVS regmap, IRQ, selected keycode, current key state, wakeup flag, timer, input device, and minor revision. `imx_snvs_pwrkey_interrupt()` handles the SPO interrupt and clears `SNVS_LPSR_SPO`. `imx_imx_snvs_check_for_events()` polls `SNVS_HPSR_BTN` after debounce and during long presses. `imx_snvs_pwrkey_probe()` parses `regmap`, `linux,keycode`, `wakeup-source`, and `power-off-time-sec`, enables debounce/power-off configuration, and registers input/IRQ.

## Control Flow

Probe gets the parent SNVS regmap, optional clock, keycode, IRQ, and optional power-off timing, reads the silicon minor revision, enables debounce power-key detection, clears stale SPO status, initializes a timer, registers an input device, requests IRQ, enables device wakeup, and installs the IRQ as a wake IRQ. On interrupt it records a wakeup event, reads LP status, and either emits a synthetic press/release for minor revision 0 or schedules the debounce timer. The timer reads live button state and reports only changes, rescheduling while pressed.

## State and Persistence Behavior

The driver persists `keystate` and the timer while bound. SNVS LPCR bits for debounce and power-off timing persist in the shared SNVS block. Wakeup state is managed by device core and PM wake IRQ. A devm action deletes the timer during teardown.

## Dependencies and Integration Points

It depends on OF, `syscon_regmap_lookup_by_phandle()`, SNVS register layout, optional clock control, input key events, timers, and `dev_pm_set_wake_irq()`. Compatible string is `fsl,sec-v4.0-pwrkey`.

## Risks and Edge Cases

The timer callback ignores regmap read errors and treats unread state as whatever was left in `state`. Revision-specific behavior is critical: first-generation i.MX6 only interrupts on release. `power-off-time-sec` accepts only 0, 5, 10, or 15 seconds. Wake IRQ setup errors are logged but not fatal.

## Test Signals

Test revision 0 synthetic events, newer revision debounce and long-press polling, keycode override, invalid power-off timing, regmap failure, wake from suspend, timer cleanup on unbind, optional clock paths, and repeated press/release races around IRQ clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/snvs_pwrkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/spear-keyboard.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/spear-keyboard.c

## Purpose

This platform driver supports the ST SPEAr keyboard controller. It exposes a 16x16 matrix through a hardware FIFO-style data register, reports one active key at a time, manages scan start/stop through input open/close, and supports wake-aware suspend behavior.

## Important APIs, Types, and Functions

`struct spear_kbd` owns the input device, MMIO base, clock, IRQ, mode, suspended clock rate, saved control register, last pressed key, keycode matrix, and IRQ wake flag. `spear_kbd_interrupt()` reads status/data and reports release of the prior key plus press of the new key. `spear_kbd_open()` programs clock frequency, mode, scan rate, and starts scanning. `spear_kbd_close()` stops scanning and disables the clock. PM functions save/restore mode control and optionally reprogram suspend rate.

## Control Flow

Probe requires an IRQ and `st,mode`, optionally reads `suspended_rate`, maps MMIO, obtains a prepared clock, builds the fixed 16x16 keymap from firmware, requests IRQ, registers input, and marks the device wake-capable. Open enables the clock, computes the peripheral clock divider in MHz minus one, writes scan configuration, clears status, and sets start-scan. Interrupt flow validates data availability, releases `last_key` if set, reads row/column from `DATA_REG`, maps it to a keycode, emits scan/key press, caches the key, and clears status.

## State and Persistence Behavior

Only one active `last_key` is tracked, reflecting the hardware model. Saved `mode_ctl_reg` is used across suspend/resume. Wake mode may leave scanning active and changes frequency programming for low-power clock assumptions.

## Dependencies and Integration Points

It depends on platform resources, clock rate, matrix keymap bindings, input open/close callbacks, and OF compatible `st,spear300-kbd`.

## Risks and Edge Cases

The interrupt handler always releases the previous key before pressing a new one, so true multi-key rollover is unsupported. A `KEY_RESERVED` key can become `last_key` if the keymap leaves holes. The driver uses a nonstandard `suspended_rate` property name without vendor prefix. Clock enable/disable in suspend is explicit and can become unbalanced if input open state changes unexpectedly.

## Test Signals

Test mode parsing, keymap bounds, single-key press/release replacement, no data interrupt returning `IRQ_NONE`, clock divider calculations, autorepeat property, suspend with wake and custom suspended rate, and close/resume interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/spear-keyboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/st-keyscan.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/st-keyscan.c

## Purpose

This platform driver supports the STMicroelectronics STI keyscan controller. It programs matrix dimensions and debounce timing, reads a compact 16-bit matrix state on interrupts, and reports key transitions through a matrix keymap.

## Important APIs, Types, and Functions

`struct st_keyscan` stores MMIO base, IRQ, clock, input device, last 16-bit matrix state, row/column counts, and debounce time. `keyscan_isr()` reads `KEYSCAN_MATRIX_STATE_OFF`, computes changed bits, reports key transitions using the input keycode array, and syncs. `keyscan_start()` enables the clock and programs debounce, dimensions, and enable. `keyscan_stop()` disables scanning and the clock. Probe parses matrix properties and `st,debounce-us`.

## Control Flow

Probe requires DT, allocates input/state, parses rows/columns, builds a keymap, maps registers, gets a clock, briefly enables the clock to stop/reset the controller, requests IRQ, registers input, stores driver data, and marks wakeup capable. Input open starts hardware; close stops it. Interrupts are edge/simple state-change notifications, with all changed bits in the 16-bit matrix reported from the cached state comparison.

## State and Persistence Behavior

`last_state` is the only event-state cache. Hardware debounce and dimension registers persist while the controller is enabled. Suspend either enables IRQ wake or stops scanning if the input device is open; resume reverses that behavior.

## Dependencies and Integration Points

The driver depends on OF compatible `st,sti-keyscan`, the matrix-keypad binding, platform MMIO/IRQ, a clock, and input `open`/`close` callbacks.

## Risks and Edge Cases

The controller maximum is 16 keys, but matrix parsing does not explicitly reject row/column products greater than 16 before building a keymap. `for_each_set_bit(..., BITS_PER_LONG)` iterates beyond the 16 hardware bits if high bits somehow change. Probe enables the clock and calls `keyscan_stop()`, which disables it; failures after that must not assume the clock is still active. Wakeup capability is set, but policy depends on userspace enabling wake.

## Test Signals

Test valid and oversized matrices, debounce conversion from microseconds and clock rate, open/close clock balance, interrupt deltas, all release behavior after suspend, wake-enabled suspend/resume, missing DT, and keymap holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/st-keyscan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/stmpe-keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/stmpe-keypad.c

## Purpose

This platform child driver supports keypad blocks in STMPE multi-function expanders. It configures variant-specific keypad pins, row/column masks, debounce, scan count, and FIFO reads, then reports matrix key press/release events through input.

## Important APIs, Types, and Functions

`struct stmpe_keypad_variant` captures per-chip FIFO width, auto-increment behavior, pull-up requirements, max rows/cols, and GPIO masks. `struct stmpe_keypad` stores parent STMPE, input, variant, timing settings, row/column masks, and keymap. `stmpe_keypad_read_data()` reads FIFO bytes. `stmpe_keypad_irq()` decodes row/column/up records. `stmpe_keypad_altfunc_init()` assigns pins to keypad alternate function. `stmpe_keypad_chip_init()` enables the block and programs registers.

## Control Flow

Probe gets the parent `struct stmpe`, selects the variant by `partnum`, parses debounce/scan/autorepeat and matrix properties, builds a keymap, derives used row/column masks from non-reserved keymap entries, initializes chip hardware, requests a threaded IRQ, registers input, and stores driver data. IRQ flow reads the variant's data bytes, skips no-key markers, decodes row/column and release bit, emits `MSC_SCAN` and key state, and syncs for each FIFO entry.

## State and Persistence Behavior

The software row/column masks are derived once from the keymap and persist for the device lifetime. Hardware block enable, alternate-function pin selection, pull-ups, scan count, debounce, and row/column registers remain active until remove disables the keypad block.

## Dependencies and Integration Points

It depends on the STMPE MFD core (`stmpe_enable()`, `stmpe_block_read()`, `stmpe_set_altfunc()`), matrix-keypad bindings, platform IRQs, and I2C-backed input devices. Supported variants are STMPE1601, STMPE2401, and STMPE2403.

## Risks and Edge Cases

Variant pin masks are consumed with `__ffs()` while clearing bits; incorrect variant metadata can corrupt pin selection. Some variants require pull-ups and different FIFO read behavior. IRQ handling returns `IRQ_NONE` on read error, which may matter for shared/level IRQs. There is no explicit PM path, so parent MFD suspend must preserve or restore keypad block state.

## Test Signals

Test all variants, auto-increment and non-auto-increment reads, row counts above eight, pull-up programming, debounce/scan-count limit failures, keymap-derived pin masks, FIFO no-key markers, release events, remove disabling the block, and parent MFD suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/stmpe-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/stowaway.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/stowaway.c

## Purpose

This serio driver supports Stowaway RS232 keyboards. It maps one-byte Stowaway scancodes to Linux keycodes, reports press/release events, and registers as a serio protocol driver for `SERIO_STOWAWAY`.

## Important APIs, Types, and Functions

`skbd_keycode[128]` is the static scancode-to-keycode map. `struct skbd` stores an editable keycode table, input device, serio port, and physical path. `skbd_interrupt()` decodes the release bit and key mask. `skbd_connect()` allocates state/input, opens the serio port, initializes input capabilities, and registers the device. `skbd_disconnect()` closes and unregisters resources.

## Control Flow

When a matching serio port appears, connect allocates driver state and input, copies the default map, sets bus/vendor/product IDs, marks key and repeat capability, opens the serio device, and registers input. Each received byte is handled synchronously by the serio interrupt callback: the low seven bits select a keycode, bit 7 means release, and nonzero mapped keys are reported then synced.

## State and Persistence Behavior

There is no protocol state machine; only the keycode array and input registration persist. The driver does not track key-down state itself and trusts the keyboard's make/break stream.

## Dependencies and Integration Points

It depends on the serio core, RS232 transport, input key events, and `SERIO_STOWAWAY` protocol matching. Users can inspect or remap the exposed keycode table via normal input mechanisms.

## Risks and Edge Cases

Unknown or zero-mapped scancodes are silently ignored, so hardware variants may appear to drop keys. There is no resynchronization or error handling for corrupt serial bytes. Allocation uses manual cleanup paths, and connect failure must close the serio port only after it was opened.

## Test Signals

Test serio attach/detach, every mapped scancode press and release, zero-mapped scancode ignoring, input keycode remapping, repeat capability exposure, open failure unwind, and disconnect while events are in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/stowaway.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/sun4i-lradc-keys.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/sun4i-lradc-keys.c

## Purpose

This platform driver reports keys connected to Allwinner LRADC channel 0 through a resistor ladder. It converts ADC readings to voltages using the regulator voltage and SoC-specific divisor, selects the closest configured key voltage, and reports one active key at a time.

## Important APIs, Types, and Functions

`struct lradc_variant` describes voltage divisor and optional clock/reset requirements. `struct sun4i_lradc_data` stores device/input, MMIO, optional clock/reset, VREF regulator, keymap, active keycode, and computed VREF. `sun4i_lradc_load_dt_keymap()` parses child nodes with `channel`, `voltage`, and `linux,code`. `sun4i_lradc_open()` powers/configures LRADC. `sun4i_lradc_irq()` handles keyup/keydown interrupts and voltage matching.

## Control Flow

Probe loads the DT keymap, selects variant data, acquires optional clock/reset for newer variants, gets the `vref` regulator, allocates input, maps MMIO, requests IRQ, registers input, and optionally configures wake IRQ. Opening enables regulator, reset, clock, computes effective VREF, programs sample/debounce control, and enables keyup/keydown interrupts. On keydown with no cached key, the handler reads 6-bit ADC data, computes voltage, chooses the closest configured key, reports press, and caches the keycode. On keyup it releases the cached key.

## State and Persistence Behavior

The cached `chan0_keycode` is required because release interrupts do not identify which key was released. The computed VREF is refreshed on open, reflecting current regulator voltage. Hardware is fully disabled on close, including IRQ mask, clock, reset, and regulator.

## Dependencies and Integration Points

The driver depends on OF child keymap nodes, platform MMIO/IRQ, regulators, optional clocks/resets, `dev_pm_set_wake_irq()`, and Allwinner compatible variants for A10, A83T R-LRADC, and R329 LRADC.

## Risks and Edge Cases

Only channel 0 is supported; child nodes for other channels are rejected. Closest-voltage matching has no tolerance threshold, so noisy or misconfigured resistor ladders can report the wrong key. If `chan0_keycode` is zero and a keyup arrives, keycode zero is released. Optional clock/reset pointers are NULL for older variants and rely on helper APIs accepting NULL.

## Test Signals

Test DT keymap validation, voltage matching under varied VREFs, noisy ADC values, keydown while a key is cached, keyup release, regulator/clock/reset failure unwind, wake IRQ setup, all compatible variants, and open/close power sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/sun4i-lradc-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/sunkbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/sunkbd.c

## Purpose

This serio driver supports Sun Type 4/5 serial keyboards. It probes keyboard type and layout, translates Sun scancodes into Linux keycodes, handles LEDs and sound controls, and restores device state after keyboard resets.

## Important APIs, Types, and Functions

`sunkbd_keycode[128]` is the default scancode map. `struct sunkbd` stores keycodes, input/serio pointers, a reset work item, wait queue, name/phys strings, type, enabled flag, and reset/layout handshake state. `sunkbd_interrupt()` handles reset/layout replies, all-up markers, and key events. `sunkbd_event()` sends LED, click, and bell commands. `sunkbd_initialize()` resets/probes the keyboard. `sunkbd_reinit()` restores LEDs/beeps after reset.

## Control Flow

Connect allocates state/input, opens the serio port, sends reset, waits for the keyboard ID, optionally queries Type 4 layout to distinguish Type 5, initializes input capabilities, enables event processing under `serio_pause_rx`, and registers input. Runtime bytes either complete reset/layout waits, schedule reinitialization after reset notifications, or report key press/release events if enabled. Input LED/sound events send command bytes back over serio.

## State and Persistence Behavior

The driver persists keyboard type, keymap, enabled flag, reset/layout handshake values, and desired LED/sound state via input core. After keyboard reset, delayed work waits for the ID byte and re-sends LED/click/bell state if the device is still enabled. Disconnect disables processing, cancels work, unregisters input, and closes serio.

## Dependencies and Integration Points

It depends on serio RS232 transport, Sun keyboard protocol constants, input LED/SND event callbacks, wait queues, workqueues, and serio matching for both `SERIO_SUNKBD` and probe-capable `SERIO_UNKNOWN`.

## Risks and Edge Cases

The protocol uses volatile `s8` handshake fields and wait queues; reset bytes arriving during disconnect must be coordinated with `enabled`. Unknown scancodes log warnings. The driver probes unknown serio ports, so reset timeouts must avoid false positives. All-up is ignored rather than releasing tracked keys, because the driver does not track key-down state.

## Test Signals

Test Type 4 and Type 5 identification, layout timeout, key press/release streams, unknown scancodes, LED/click/bell writes, reset notification and reinit work, disconnect during reset wait, and matching on `SERIO_UNKNOWN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/sunkbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/tc3589x-keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/tc3589x-keypad.c

## Purpose

This platform child driver supports the TC35893/TC3589x MFD keypad controller. It configures keypad size, debounce, settle timing, GPIO pull-ups, block clocks/reset, interrupt masks, and FIFO event decoding for matrix key input.

## Important APIs, Types, and Functions

`struct tc3589x_keypad_platform_data` stores parsed keypad dimensions, timing, IRQ trigger, wake/autorepeat flags, and optional keymap data. `struct tc_keypad` stores parent MFD, input device, platform data, keymap pointer, and stopped flag. `tc3589x_keypad_init_key_hardware()` writes size/config/pull-up registers. `tc3589x_keypad_irq()` drains event FIFO and decodes row/column/up records. Enable/disable paths manipulate reset, MFS, clock, IRQ clear, and mask registers.

## Control Flow

Probe parses OF properties, gets IRQ, allocates state/input, builds a matrix keymap using the maximum hardware matrix, disables the keypad block, requests a threaded IRQ, registers input, and configures wake capability. Input open enables the block and initializes hardware. IRQ handling reads up to eight FIFO entries, skips empty/clear codes, reports each valid event, clears keyboard interrupts, and re-enables event/loss masks. Suspend disables non-wakeup devices or enables IRQ wake; resume reverses that state.

## State and Persistence Behavior

`keypad_stopped` tracks whether the block is disabled and drives PM behavior. The keymap pointer is the input core keycode array. Hardware state includes keypad size, pull-up configuration, debounce/settle registers, interrupt masks, and block clock/reset state.

## Dependencies and Integration Points

The driver depends on the TC3589x MFD API (`tc3589x_reg_write/read`, `tc3589x_set_bits`), matrix-keypad bindings, platform IRQ resources, and input device open/close. Wake policy is exposed through device wakeup flags.

## Risks and Edge Cases

The OF parser checks for `linux,keymap` but never fills `plat->keymap_data`; actual keymap loading relies on `matrix_keypad_build_keymap()` reading from input parent properties. Resume returns immediately when `keypad_stopped` is false, so a wakeup-enabled active keypad may skip disabling IRQ wake. FIFO overflow/loss is only masked/re-enabled, not surfaced as input loss. Pull-ups are programmed broadly for row/column groups.

## Test Signals

Test OF dimension parsing, missing keymap, open/close block enable, FIFO press/release decoding, overflow/loss interrupts, wake and non-wake suspend/resume, IRQ trigger behavior, MFD register errors, and keymap holes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/tc3589x-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/tca8418_keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/tca8418_keypad.c

## Purpose

This I2C driver supports the TI TCA8418 keyboard scanner. It configures selected rows/columns as keypad pins, enables key event interrupts, drains the hardware FIFO, and reports matrix key events.

## Important APIs, Types, and Functions

`struct tca8418_keypad` stores the I2C client, input device, and row shift. `tca8418_write_byte()` and `tca8418_read_byte()` wrap SMBus byte access. `tca8418_configure()` writes keypad GPIO masks, debounce registers, and interrupt configuration. `tca8418_read_keypad()` drains `REG_KEY_EVENT_A` until an empty code. `tca8418_irq_handler()` checks interrupt status, warns on overflow, reads key events, and clears all interrupt bits.

## Control Flow

Probe verifies SMBus support, parses matrix dimensions, validates against 8x10 hardware limits, allocates state, probes presence by reading `REG_KEY_LCK_EC`, allocates input, builds keymap, requests a shared threaded IRQ, configures the chip, and registers input. IRQ flow reads `REG_INT_STAT`, ignores empty interrupts, logs overflow, drains key events when key interrupt is set, and writes `0xff` to clear all pending sources.

## State and Persistence Behavior

The driver does not keep key state; it trusts FIFO make/break event values. The row shift is persisted for scan-code calculation. Hardware keypad/GPIO/debounce/interrupt configuration persists after probe; there are no open/close or PM hooks.

## Dependencies and Integration Points

It depends on I2C SMBus byte operations, matrix-keypad properties, optional `keypad,autorepeat`, client IRQ, and OF compatible `ti,tca8418`. It uses the input keycode array created by `matrix_keypad_build_keymap()`.

## Risks and Edge Cases

The row/column conversion adjusts the chip's one-based event code with a wraparound path when `col == 0`; malformed event code zero is already treated as empty, but unexpected codes can calculate invalid rows. The IRQ is requested before chip configuration, so a live interrupt line may run against partially configured hardware. Overflow is only logged, with no recovery beyond FIFO drain/clear. No PM means system sleep depends on external chip state.

## Test Signals

Test all row/column bounds, event-code conversion, FIFO empty and multi-entry cases, overflow interrupt, shared IRQ returning `IRQ_NONE`, missing IRQ behavior, SMBus read/write failures, autorepeat property, and module autoload via I2C/OF tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/tca8418_keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/tegra-kbc.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/tegra-kbc.c

## Purpose

This platform driver supports NVIDIA Tegra matrix keyboard controllers. It configures KBC row/column pin routing, debounce/repeat timing, FIFO interrupt processing, optional ghost filtering, and wakeup key handling for Tegra20/30/114 variants.

## Important APIs, Types, and Functions

`struct tegra_kbc` stores device state: timing counts, pin map, keymap, wake flags, MMIO, input, IRQ, spinlock, polling timer, clock/reset, current keys, and variant limits. `tegra_kbc_parse_dt()` reads debounce/repeat, ghost-filter, wake, keymap, and row/column pin arrays. `tegra_kbc_config_pins()` writes row/column pin config registers. `tegra_kbc_report_keys()` decodes FIFO entries, handles optional Fn mapping, filters ghost states, and reports deltas. `tegra_kbc_isr()` transitions from IRQ to timer polling until all keys release.

## Control Flow

Probe selects hardware limits, parses DT, validates pin config, gets IRQ/input/MMIO/clock/reset, computes repoll delay, builds the keymap, requests a disabled high-trigger IRQ, registers input, and marks wakeup. Opening resets/configures hardware, flushes FIFO, clears interrupts, and enables IRQ. FIFO threshold interrupt disables further FIFO interrupts and schedules the timer after the controller's continuous-poll delay. The timer repeatedly reports keys while FIFO count is nonzero, then releases all cached keys and re-enables FIFO interrupts.

## State and Persistence Behavior

`current_keys[]` and `num_pressed_keys` persist currently reported keys. Wake suspend stores continuous-poll timeout in `cp_to_wkup_dly`, switches to keypress wake mode, and records whether wake was caused by a keypress. Hardware configuration is reset and reprogrammed on every input open.

## Dependencies and Integration Points

The driver depends on OF pin arrays (`nvidia,kbc-row-pins`, `nvidia,kbc-col-pins`), matrix-keypad keymaps, platform MMIO/IRQ, reset control, clocks, timers, spinlocks, and input PM locking.

## Risks and Edge Cases

Fn-map fields exist, but this version does not visibly parse a property setting `use_fn_map`, so alternate keymap support may be dormant. Ghost filtering suppresses an entire scan iteration and can delay legitimate chords. Wake resume can synthesize `wakeup_key`, but this field is not populated in the visible code. IRQ disabling and timer deletion must stay ordered to avoid stale timer reads after close/suspend.

## Test Signals

Test Tegra20/30/114 limits, invalid pin arrays, ghost-filter chords, FIFO flush and multi-key events, held-key polling, close during timer activity, wake suspend/resume, reset/clock failures, keymap bounds, and dormant Fn/wakeup-key behavior if platform data expects it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/tegra-kbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/tm2-touchkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/tm2-touchkey.c

## Purpose

This I2C driver supports Samsung/Cypress/Coreriver touchkey devices used on TM2, Midas, Aries, and TC360 platforms. It reports capacitive touch keys and exposes a LED class device for touchkey backlight control, with variant-specific I2C command formats and regulator behavior.

## Important APIs, Types, and Functions

`struct touchkey_variant` describes keycode register, command register, LED commands, no-register protocol, and fixed-regulator behavior. `struct tm2_touchkey_data` stores client, input, LED device, regulators, variant, and keycodes. `tm2_touchkey_power_enable()` enables supplies and waits for initialization. `tm2_touchkey_irq_handler()` reads event data, decodes key index and press/release bit, and reports input events. `tm2_touchkey_led_brightness_set()` sends LED commands and optionally changes VDD voltage.

## Control Flow

Probe checks I2C capabilities, selects OF variant data, gets three regulators, reads optional `linux,keycodes` or uses defaults, powers the device, installs a devm power-off action, registers input keys, requests a threaded IRQ, registers the LED class device, and turns LEDs on for fixed-regulator variants. IRQ handling reads either a byte or byte-data register, validates the key index, reports `MSC_SCAN`, releases all keys on release events, or presses the indexed key, then syncs. Suspend disables IRQ and power; resume reenables IRQ and power.

## State and Persistence Behavior

Keycodes and variant selection persist for device lifetime. LED brightness is stored in the LED class device, while actual hardware state is controlled by I2C commands and possibly VDD voltage. Regulators are kept enabled while active and disabled on suspend/remove.

## Dependencies and Integration Points

The driver depends on OF match data, I2C SMBus byte/byte-data support, regulator bulk APIs, input key events, LED class, and threaded IRQs. Compatibles include `cypress,tm2-touchkey`, `cypress,midas-touchkey`, `cypress,aries-touchkey`, and `coreriver,tc360-touchkey`.

## Risks and Edge Cases

The handler references `data` in the fixed-regulator LED sync block even after a failed I2C read path, so error handling should be reviewed. Release events release all configured keys rather than the indexed key. Suspend enables IRQ before power in resume, allowing a narrow race if the line fires before the device is initialized. Regulator voltage changes are ignored for fixed-regulator variants.

## Test Signals

Test all variants, no-register and register protocols, custom/default keycodes, invalid key indexes, I2C read failures, LED on/off commands, regulator voltage behavior, suspend/resume race behavior, and fixed-regulator backlight synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/tm2-touchkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/twl4030_keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/twl4030_keypad.c

## Purpose

This platform child driver supports the keypad controller in TWL4030-family MFD chips. It programs the controller's 8x8 hardware decoder, reads full matrix state over the TWL I2C module, filters ghost states, and reports matrix key changes.

## Important APIs, Types, and Functions

`struct twl4030_keypad` stores the keymap, cached row state, dimensions, IRQ, debug device, and input. `twl4030_kpread()` and `twl4030_kpwrite_u8()` wrap TWL module I2C access. `twl4030_col_xlate()` maps all-ground rows to an extra column. `twl4030_read_kp_matrix_state()` reads row status bytes. `twl4030_is_in_ghost_state()` detects ambiguous multi-key states. `twl4030_kp_scan()` reports changed keys. `twl4030_kp_program()` configures debounce, timeout, edge detection, and clear-on-read behavior.

## Control Flow

Probe allocates state/input, parses matrix dimensions, validates limits, gets IRQ, builds a keymap large enough for an extra column, registers input, programs hardware, requests a threaded IRQ, and unmasks key/timeout interrupts. The IRQ handler reads and clears `KEYP_ISR1`; if a key interrupt is present it scans the current matrix, otherwise it releases all keys. Scanning compares each row with cached state, skips ghost states, reports `MSC_SCAN` and key events, updates row cache, and syncs.

## State and Persistence Behavior

`kp_state[]` persists currently reported row bits. Hardware keeps debounce/timeout/edge/SIH settings and keypad enable state after probe. There is no explicit suspend/resume hook in this file, relying on the TWL core and always-on keypad hardware semantics.

## Dependencies and Integration Points

It depends on TWL4030 MFD APIs, matrix-keypad properties, platform IRQ child devices, input events, and optional OF compatible `ti,twl4030-keypad`. The keypad is an I2C-backed MFD child, so all event reads happen in threaded context.

## Risks and Edge Cases

Input is registered before hardware programming and IRQ request; failures after registration leave devm-managed input but may expose a partially initialized device briefly. Ghost states are ignored without releasing prior keys, which can leave stale reports until a non-ghost scan. The extra ground-row column requires keymap size and userspace expectations to match. I2C read failure releases all keys only in IRQ path, not in direct scan read failure.

## Test Signals

Test row/column bounds, extra-column ground rows, ghost combinations, I2C read/write failures, timeout interrupt release-all behavior, keymap build size, unmasking interrupts, and MFD suspend/resume interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/twl4030_keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/xtkbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/xtkbd.c

## Purpose

This serio driver supports legacy XT keyboards. It translates XT set-like scancodes from a serio port into Linux key events and exposes an editable keycode table with repeat capability.

## Important APIs, Types, and Functions

`xtkbd_keycode[256]` is the default map. `struct xtkbd` stores the keycode table, input device, serio port, and physical path. `xtkbd_interrupt()` ignores `0xe0`/`0xe1` emulation prefixes, decodes release bit and low seven-bit key index, and reports mapped keys. `xtkbd_connect()` allocates state/input, opens serio, registers input, and installs driver data. `xtkbd_disconnect()` closes/unregisters/frees resources.

## Control Flow

The serio core calls connect for `SERIO_XT` ports. Connect initializes input identity as `BUS_XTKBD`, marks key/repeat events, copies the keymap, opens the serio device, and registers input. Each incoming byte is processed immediately; mapped scancodes emit press/release and sync, while unmapped scancodes log warnings.

## State and Persistence Behavior

The driver does not track modifier or prefix state, so `0xe0` and `0xe1` prefixes are discarded rather than extending the next code. Runtime state is limited to the keycode array and registration pointers.

## Dependencies and Integration Points

It depends on serio XT transport, input key event APIs, and manual allocation/free paths. The serio ID table matches any XT protocol ID/extra.

## Risks and Edge Cases

Ignoring emulation prefixes limits support for extended keys. `kmalloc_obj()` does not zero memory, but all fields used by the driver are initialized before use. The loop setting key bits uses `i < 255`, leaving index 255 out despite a 256-entry table. Unknown scancodes can spam kernel warnings.

## Test Signals

Test attach/detach, all mapped press/release scancodes, prefix byte handling, unmapped warning paths, keycode remapping, input repeat exposure, serio open failure cleanup, and disconnect during input activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/xtkbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/matrix-keymap.c -->
# sources/distributed-fs/ceph-client/drivers/input/matrix-keymap.c

## Purpose

This shared helper implements matrix-keypad binding support for input drivers. It parses row/column dimensions and encoded keymap entries, validates them, allocates or fills keycode arrays, and sets input key capabilities.

## Important APIs, Types, and Functions

`matrix_keypad_parse_properties()` reads `keypad,num-rows` and `keypad,num-columns`. `matrix_keypad_build_keymap()` is the exported conversion API used by many keypad drivers. `matrix_keypad_parse_keymap()` reads `linux,keymap` or a caller-specified property into temporary memory. `matrix_keypad_map_key()` decodes `KEY_ROW`, `KEY_COL`, and `KEY_VAL`, validates bounds, stores the keycode at `MATRIX_SCAN_CODE()`, and sets the key bit.

## Control Flow

Callers set `input_dev->dev.parent`, provide dimensions and optionally platform `matrix_keymap_data` and storage. The build function computes `row_shift` from columns, allocates managed storage if needed, assigns input keycode metadata, sets `EV_KEY`, then either maps platform entries or parses firmware property entries. After successful mapping it clears `KEY_RESERVED`.

## State and Persistence Behavior

The helper owns no global state. It mutates the caller's input device keycode pointer, keycode size/count, event bits, and key bitmask. When it allocates storage, memory is devm-managed by the input parent device.

## Dependencies and Integration Points

It depends on the generic device property API, input subsystem key bitmaps, matrix-keypad encoding macros, and devm allocation. It is exported for GPL and non-GPL symbol users as currently declared (`EXPORT_SYMBOL_GPL` for parse properties, `EXPORT_SYMBOL` for build keymap).

## Risks and Edge Cases

`size > max_keys` rejects keymaps with more entries than matrix cells, but sparse maps larger than cells are invalid even if duplicates exist. Duplicate scan codes overwrite prior keycodes while leaving the old key bit set. Keycode values are not checked against `KEY_MAX` here. Callers that pass wrong dimensions produce incorrect row shifts and scan-code indexing.

## Test Signals

Test missing/malformed properties, invalid rows/columns in entries, duplicate entries, automatic allocation, caller-supplied keymap storage, custom property names, sparse keymaps, oversized keymap arrays, and integration with drivers that use non-power-of-two column counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/matrix-keymap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/88pm80x_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/88pm80x_onkey.c

## Purpose

This platform child driver reports the ONKEY status of Marvell 88PM80x PMICs as `KEY_POWER`. It also enables long-onkey detection and sets the long-press interval through PMIC RTC miscellaneous registers.

## Important APIs, Types, and Functions

`struct pm80x_onkey_info` stores input device, parent PMIC chip, regmap, and IRQ. `pm80x_onkey_handler()` reads `PM800_STATUS_1`, masks `PM800_ONKEY_STS1`, and reports the power key state. `pm80x_onkey_probe()` obtains parent chip/regmap/IRQ, allocates input, requests the PMIC IRQ through `pm80x_request_irq()`, registers input, programs long-onkey bits, and enables wakeup. Remove frees the PMIC IRQ and input device.

## Control Flow

Probe is driven by an MFD platform child named `88pm80x-onkey`. After resource allocation and input setup, the parent PMIC IRQ helper installs a threaded/oneshot handler. Once input is registered, the driver updates `PM800_RTC_MISC4` to enable long-onkey detection and `PM800_RTC_MISC3` to configure an eight-second interval. IRQ handling is level/status based and directly reports current key state.

## State and Persistence Behavior

Software state is limited to resource pointers. Long-onkey enable and interval persist in PMIC registers after probe. Wake behavior is initialized on the platform child and parent PM ops are reused through `pm80x_dev_suspend/resume`.

## Dependencies and Integration Points

It depends on the 88PM80x MFD core, PMIC regmap definitions, PMIC IRQ allocation helpers, platform child devices, and the input subsystem.

## Risks and Edge Cases

The driver uses manual allocation and non-devm input allocation, so every failure path must remain correct. Register update return values for long-onkey configuration are ignored. IRQ status read failure returns `IRQ_NONE`, potentially problematic for PMIC IRQ dispatch. Wakeup depends on parent PM implementation rather than local IRQ wake calls.

## Test Signals

Test missing IRQ/regmap, PMIC IRQ request/free, status read failures, press/release status changes, long-onkey register programming, input registration failure unwind, remove cleanup, and suspend/resume wake behavior through the parent MFD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/88pm80x_onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/88pm860x_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/88pm860x_onkey.c

## Purpose

This platform child driver reports Marvell 88PM860x PMIC ONKEY status as a Linux power key. It reads PMIC status over I2C, re-enables long-onkey detection after interrupts, and participates in PMIC wakeup flag management.

## Important APIs, Types, and Functions

`struct pm860x_onkey_info` stores input, parent chip, selected I2C client, device, and IRQ. `pm860x_onkey_handler()` reads `PM8607_STATUS_2`, masks `ONKEY_STATUS`, reports `KEY_POWER`, syncs, and sets `LONG_ONKEY_EN` in `PM8607_WAKEUP`. Probe selects the correct PM8607 I2C client or companion, allocates input, registers it, requests a threaded IRQ, stores driver data, and enables wakeup. PM hooks manipulate `chip->wakeup_flag`.

## Control Flow

The MFD child probe gets its IRQ, chooses the PMIC I2C endpoint based on chip ID, exposes an input power key, registers input, then requests the IRQ. On every ONKEY interrupt, it samples current status and reports that state. Suspend/resume do not touch IRQs directly; they set or clear the parent chip wakeup flag bit for `PM8607_IRQ_ONKEY` when device wakeup is enabled.

## State and Persistence Behavior

Driver-local persistent state is resource pointers only. The parent chip's `wakeup_flag` is persistent cross-device PM state. Long-onkey detection is programmed after each interrupt rather than once at probe, implying PMIC hardware may clear or require refresh.

## Dependencies and Integration Points

It depends on the 88PM860x MFD core, PMIC I2C register helpers, platform IRQs, input power-key events, and parent PM wakeup flag handling.

## Risks and Edge Cases

`pm860x_reg_read()` return value is masked without checking for negative errors, so I2C failures can be reported as key states. Input is registered before IRQ request; if IRQ request fails, devm cleanup removes the input later but the device may briefly exist. Wakeup flag manipulation assumes no concurrent unsynchronized updates from sibling drivers.

## Test Signals

Test chip/client selection, status read failures, press/release reporting, long-onkey re-enable writes, IRQ request failure after input registration, wakeup flag set/clear, and module unload with active PMIC child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/88pm860x_onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/88pm886-onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/88pm886-onkey.c

## Purpose

This platform driver reports the ONKEY status of Marvell 88PM886 PMICs as a Linux `KEY_POWER` input event. It is a small MFD child driver using the parent chip regmap and IRQ resource.

## Important APIs, Types, and Functions

`struct pm886_onkey` stores the input device and parent chip pointer. `pm886_onkey_irq_handler()` reads `PM886_REG_STATUS1`, masks `PM886_ONKEY_STS1`, reports the power key state, and syncs. `pm886_onkey_probe()` allocates state/input, gets the platform IRQ, sets input identity/capability, requests a threaded IRQ with `IRQF_ONESHOT | IRQF_NO_SUSPEND`, registers input, and exposes platform ID matching.

## Control Flow

Probe is invoked for platform ID `88pm886-onkey`. It obtains the parent `pm886_chip`, configures an input device, attaches an IRQ handler, and registers input. Interrupt flow reads current PMIC status rather than relying on edge direction, so both press and release depend on the PMIC status bit at handler time.

## State and Persistence Behavior

No key state is cached in software; PMIC status is sampled on each IRQ. Resources are devm-managed. `IRQF_NO_SUSPEND` keeps IRQ delivery active during suspend, but there are no explicit local PM hooks.

## Dependencies and Integration Points

It depends on the 88PM886 MFD parent, regmap, platform IRQ resources, input power-key events, and platform device ID matching.

## Risks and Edge Cases

The driver does not call `device_init_wakeup()` or `enable_irq_wake()`, so suspend wake behavior must be provided by parent IRQ configuration despite `IRQF_NO_SUSPEND`. Status read errors return `IRQ_NONE`, which may affect shared interrupt accounting. Long-press or reset-related PMIC features are not configured here.

## Test Signals

Test platform ID autoload, IRQ retrieval failures, regmap read failures, press/release status sampling, suspend IRQ behavior, input registration failure, and parent MFD teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/88pm886-onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/misc/Kconfig

## Purpose

This Kconfig file declares the `INPUT_MISC` menu and build-time configuration symbols for miscellaneous Linux input drivers that do not fit keyboard, mouse, touchscreen, joystick, or tablet categories. It includes power keys, haptics, accelerometers, speakers, USB remotes, MFD child inputs, and virtual/input helper devices.

## Important APIs, Types, and Functions

The top-level `menuconfig INPUT_MISC` gates the menu. Symbols relevant to this work item include `INPUT_88PM860X_ONKEY`, `INPUT_88PM80X_ONKEY`, `INPUT_88PM886_ONKEY`, `INPUT_AB8500_PONKEY`, `INPUT_AD714X`, `INPUT_AD714X_I2C`, and `INPUT_AD714X_SPI`. Each option declares `tristate` visibility, dependency expressions such as `depends on MFD_88PM800`, and selected helper subsystems where needed, for example `INPUT_FF_MEMLESS` for haptics.

## Control Flow

There is no runtime control flow. Kconfig resolution determines whether each driver is built-in, modular, or omitted. Dependency expressions hide or constrain options based on enabled buses, MFD cores, architecture support, and helper frameworks. Resulting `CONFIG_*` values are consumed by the misc Makefile to include object files.

## State and Persistence Behavior

The file persists configuration state in the kernel `.config`. It does not create runtime state. Module names in help text communicate expected build artifacts and user-facing module names.

## Dependencies and Integration Points

It integrates input misc drivers with MFD, I2C, SPI, USB, ACPI, PWM, regulator, haptics, Xen, GPIO, and architecture-specific subsystems. The AD714x parent option intentionally requires users to select at least one bus connection suboption.

## Risks and Edge Cases

Dependency drift can make a driver visible without all symbols it needs or hide a driver during compile testing. Defaults of `y` for bus subdrivers under a parent option can surprise minimal builds. Help text module names can become stale after file renames. `INPUT_MISC` itself is bool and says it does not affect the kernel, but its `if INPUT_MISC` block gates all contained choices.

## Test Signals

Useful checks include allmodconfig/allnoconfig coverage, each relevant symbol as built-in and module, dependency-disabled visibility, module-name consistency with Makefile entries, compile-test matrix for MFD-backed onkey drivers, and AD714x parent with I2C-only, SPI-only, and both bus subdrivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/misc/Makefile

## Purpose

This Kbuild Makefile maps miscellaneous input `CONFIG_*` symbols to the object files compiled into the kernel or emitted as modules. It is the build integration point for all drivers configured by `drivers/input/misc/Kconfig`.

## Important APIs, Types, and Functions

Relevant entries include `obj-$(CONFIG_INPUT_88PM860X_ONKEY) += 88pm860x_onkey.o`, `obj-$(CONFIG_INPUT_88PM80X_ONKEY) += 88pm80x_onkey.o`, `obj-$(CONFIG_INPUT_88PM886_ONKEY) += 88pm886-onkey.o`, `obj-$(CONFIG_INPUT_AB8500_PONKEY) += ab8500-ponkey.o`, `obj-$(CONFIG_INPUT_AD714X) += ad714x.o`, `obj-$(CONFIG_INPUT_AD714X_I2C) += ad714x-i2c.o`, and `obj-$(CONFIG_INPUT_AD714X_SPI) += ad714x-spi.o`.

## Control Flow

There is no runtime flow. During Kbuild, each `obj-$(CONFIG_...)` expands to an object list when the symbol is `y` or `m`. Parent/common objects such as `ad714x.o` are built when the parent symbol is enabled, while bus glue modules are built by their bus-specific symbols.

## State and Persistence Behavior

The file affects generated build artifacts only. It determines which translation units are linked built-in or compiled as modules and therefore which module names exist.

## Dependencies and Integration Points

It consumes Kconfig symbols from the same directory and integrates source files with the broader input subsystem build. It also reflects module naming contracts documented in Kconfig help text.

## Risks and Edge Cases

Kconfig/Makefile mismatches can make an enabled driver fail to build or produce a module with an unexpected name. Parent/bus split drivers such as AD714x require the common object and at least one transport object to be selected coherently. Typographical whitespace inconsistency is mostly harmless but can obscure review. Adding a new misc input driver requires synchronized Kconfig and Makefile changes.

## Test Signals

Test `make M=drivers/input/misc` for relevant symbols as `m`, built-in link coverage for `y`, missing-object detection after file renames, AD714x parent plus I2C/SPI combinations, and module alias/autoload smoke tests for onkey and AD714x transport drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ab8500-ponkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/ab8500-ponkey.c

## Purpose

This platform child driver reports the ST-Ericsson AB8500 power-on key as `KEY_POWER`. It uses separate falling and rising transition IRQs from the AB8500 MFD parent to report press and release.

## Important APIs, Types, and Functions

`struct ab8500_ponkey` stores input, parent AB8500 pointer, falling IRQ, and rising IRQ. `ab8500_ponkey_handler()` compares the IRQ number with `irq_dbf` and `irq_dbr` to report true or false. `ab8500_ponkey_probe()` obtains named IRQs `ONKEY_DBF` and `ONKEY_DBR`, allocates input/state, requests both IRQs using `devm_request_any_context_irq()`, and registers input. OF matching uses `stericsson,ab8500-ponkey`.

## Control Flow

Probe is invoked for an AB8500 MFD child. It gets both transition IRQs by name, allocates an input device named `AB8500 POn(PowerOn) Key`, marks `KEY_POWER`, requests both IRQ lines, and registers input. Each IRQ directly maps to one key state and syncs input.

## State and Persistence Behavior

The driver does not cache key state; the active state is inferred from the IRQ source. Resources are devm-managed. There are no local PM hooks or wakeup calls in this file.

## Dependencies and Integration Points

It depends on the AB8500 MFD core for parent data and named IRQs, platform devices, input key events, and optional OF binding. It can run in hard or threaded context depending on `devm_request_any_context_irq()`.

## Risks and Edge Cases

If IRQ names are swapped or only one transition is present, key state becomes stuck or probe fails. The handler ignores unexpected IRQ numbers but still syncs. There is no explicit wakeup setup, so power-key wake behavior must be handled by AB8500 core/IRQ configuration. Parent pointer is used only for logging after allocation.

## Test Signals

Test both transition IRQs, missing named IRQs, press/release ordering, unexpected IRQ invocation, input registration failure, OF/platform matching, suspend wake behavior through the parent MFD, and repeated bounce events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ab8500-ponkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ad714x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/ad714x-i2c.c

## Purpose

This I2C transport driver connects Analog Devices AD714x capacitive touch controllers to the shared AD714x core. It supplies big-endian register read/write callbacks and registers chip instances for AD7142/AD7143/AD7147/AD7147A/AD7148 I2C IDs.

## Important APIs, Types, and Functions

`ad714x_i2c_write()` writes a 16-bit register address and 16-bit data word through `i2c_master_send()`. `ad714x_i2c_read()` writes the 16-bit register address, receives `len` 16-bit words, and converts from big-endian to CPU endian. `ad714x_i2c_probe()` calls the common `ad714x_probe()` with `BUS_I2C`, client IRQ, and transport callbacks, then stores chip data with `i2c_set_clientdata()`.

## Control Flow

When an I2C device ID matches, probe delegates most setup to the shared AD714x core. All later core register accesses call this file's transport callbacks. Reads first send the target register address and then perform a receive for the requested word count. Writes send address and data in one transfer.

## State and Persistence Behavior

The transport layer owns no independent state beyond the common chip pointer stored as I2C client data. It uses the shared chip transfer buffer for endian-converted command/data words.

## Dependencies and Integration Points

It depends on the I2C core, `ad714x.h` shared core, PM ops exported as `ad714x_pm`, and input bus identity `BUS_I2C`. The ID table controls module autoload for named I2C devices.

## Risks and Edge Cases

`i2c_master_send()` and `i2c_master_recv()` positive short transfers are treated as success; the code only checks `< 0`, so partial transfers can corrupt core register state. Shared `xfer_buf` length must be large enough for the maximum core read length. There is no OF/SPI-style device table here beyond I2C IDs.

## Test Signals

Test read/write endian correctness, partial transfer injection, negative I2C errors, all ID table names, IRQ propagation to core probe, PM suspend/resume through `ad714x_pm`, and concurrent core accesses if any locking is expected in the shared driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ad714x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ad714x-spi.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/ad714x-spi.c

## Purpose

This SPI transport driver connects Analog Devices AD714x capacitive touch controllers to the shared AD714x core. It formats AD714x SPI command words, performs big-endian register transfers, and delegates input/device setup to the common core.

## Important APIs, Types, and Functions

`AD714x_SPI_CMD_PREFIX` and `AD714x_SPI_READ` define the command word format. `ad714x_spi_read()` builds a two-transfer SPI message: command transmit followed by receive of `len` 16-bit words, then converts received data from big-endian. `ad714x_spi_write()` sends command and data words in one `spi_write()`. `ad714x_spi_probe()` sets `bits_per_word = 8`, calls `spi_setup()`, then calls `ad714x_probe()` with `BUS_SPI`, IRQ, and callbacks.

## Control Flow

SPI probe configures the bus word size, then delegates to the shared AD714x core. Core register reads invoke the command+receive message path; writes invoke the two-word write path. Driver registration uses `module_spi_driver()` with driver name `ad714x_captouch`.

## State and Persistence Behavior

The transport layer persists only the shared chip pointer in SPI driver data. Transfers use the common chip transfer buffer, with receive data starting at `xfer_buf[1]` because `xfer_buf[0]` holds the command.

## Dependencies and Integration Points

It depends on the SPI core, AD714x shared core, `ad714x_pm` sleep ops, input bus identity `BUS_SPI`, and the SPI device's IRQ. Unlike the I2C file, no explicit SPI ID or OF table is present here.

## Risks and Edge Cases

`spi_write()` and `spi_sync()` return errors, but the code does not validate actual transferred lengths. Buffer sizing must account for command plus maximum read length. Forcing `bits_per_word = 8` may override board-specified settings. Missing ID/OF tables can limit module autoload depending on how devices are instantiated.

## Test Signals

Test SPI setup failure, command word encoding for read/write, endian conversion, multiword reads, transfer error injection, buffer length limits, IRQ propagation to the shared core, PM suspend/resume, and device autoload paths for board-described SPI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ad714x-spi.c -->
