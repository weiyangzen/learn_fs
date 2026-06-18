# sources/distributed-fs/ceph-client/drivers/platform/arm64/lenovo-thinkpad-t14s.c

Purpose: I2C EC driver for Qualcomm-based Lenovo ThinkPad T14s systems. It exposes EC-controlled LEDs, keyboard backlight, audio mute LEDs, and extra-key input events, and performs modern-standby register handshakes.

Important APIs, types, and functions: `struct t14s_ec` contains regmap, device pointer, several LED classdevs, keyboard backlight, audio LEDs, and input device. `t14s_ec_read()`/`t14s_ec_write()` implement custom regmap bus operations over I2C. `t14s_ec_read_evt()` reads EC event bytes. `t14s_led_*()` functions implement platform LED brightness/blink support. `t14s_kbd_bl_*()` handles keyboard backlight get/set and hardware-change notifications. `t14s_input_probe()` sets up `sparse_keymap`.

Control flow: probe initializes a custom 8-bit regmap backed by two-part I2C transfers, registers four platform LEDs, keyboard backlight, mic/speaker mute LEDs with audio triggers, extra-button input, then requests a threaded IRQ and disables wakeup by default. IRQ reads one event, updates keyboard-backlight state on Fn+Space, maps known Fn/touchpad events through sparse-keymap, and logs other AC/lid/thermal/performance events. Suspend writes the modern-standby entry bit three times and suspends the keyboard backlight LED classdev; resume writes the exit bit three times and resumes the LED.

State and persistence: LED state is stored in EC registers. `t14s_ec_led_classdev.cache` preserves blink/on choice for each platform LED. Regmap has no cache configuration, so reads and writes go to hardware. Keyboard backlight exposes hardware-changed notifications. Wakeup is explicitly disabled to avoid lid-close wake behavior until event masking exists.

Dependencies and integration points: uses I2C, regmap custom bus, LED class, audio LED triggers, input sparse-keymap, threaded IRQs, OF compatible `lenovo,thinkpad-t14s-ec`, and system sleep PM. Kconfig selects sparse-keymap and LED support.

Risks and edge cases: regmap read/write operations use fixed sleeps and raw I2C segment locking; timing assumptions are hardware-specific. Event reads process only one event per IRQ. Some known events only log and do not notify subsystems such as power_supply or thermal. Blink supports only the hardware 1 Hz rate. Wakeup disabled by default may surprise users expecting lid/power wake.

Test signals: verify each LED class device, blink rejection/acceptance, keyboard backlight brightness and hardware-change notification on Fn+Space, sparse-keymap event codes, suspend/resume register writes, and no wakeup from closed lid unless policy changes.
