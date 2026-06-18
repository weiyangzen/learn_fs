# sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5520-keys.c

Purpose: provides keypad support for Analog Devices ADP5520 PMIC MFD devices using platform data and the parent MFD notifier mechanism.

Important APIs/types/functions: `struct adp5520_keys` stores input device, notifier block, parent device, and keycode array. `adp5520_keys_report_event` reports press/release masks. `adp5520_keys_notifier` handles keypad press/release interrupts. `adp5520_keys_probe` configures hardware and input. `adp5520_keys_remove` unregisters the notifier.

Control flow: probe validates the platform ID and platform data, requires row/column masks, allocates input, copies the platform keymap, declares key capabilities and repeat, registers input, configures GPIO/keypad modes and pullups through ADP5520 MFD register helpers, then registers for key press and release interrupt notifications. The notifier reads low/high status registers twice to clear/collect latched bits, combines them into a keymask, and reports all affected keys as pressed or released.

State and persistence: keymap and parent pointer persist in driver memory. Hardware mode/pullup configuration is written at probe and notifier registration remains until remove.

Dependencies and integration: depends on `PMIC_ADP5520`, MFD register helpers (`adp5520_read`, `adp5520_set_bits`), platform data, Linux input, and platform driver registration.

Risks: platform data is mandatory; no firmware-node parsing exists. Register writes are OR-combined into `ret`, which reports generic `-EIO` after any failure. The notifier ignores read return values. Status read-twice clearing is hardware-specific and must not be simplified casually.

Test signals: board/platform-data tests for row/column masks and keymap size, simulated MFD notifier press/release masks, hardware register write failure injection, repeat capability checks, and notifier unregister on remove.
