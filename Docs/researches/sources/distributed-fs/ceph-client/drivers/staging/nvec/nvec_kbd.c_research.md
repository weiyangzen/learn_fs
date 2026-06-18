# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_kbd.c

## Purpose
Input keyboard driver for keys reported by the NVEC embedded controller.

## Important APIs, Types, And Functions
`struct nvec_keys` stores the input device, notifier, NVEC pointer, and Caps Lock LED state. Key functions are `nvec_kbd_probe()`, `nvec_kbd_remove()`, `nvec_keys_notifier()`, `nvec_kbd_event()`, and `nvec_kbd_toggle_led()`. It uses tables from `nvec-keytable.h`.

## Control Flow
Probe builds the keycode table, allocates/registers an `input_dev`, marks key/repeat/LED capabilities, registers an NVEC notifier, synchronously enables the keyboard, configures wake and wake-key reporting, and clears LEDs. The notifier handles `NVEC_KB_EVT`, ignores variable-size power events, adjusts for 3-byte extended events, translates scancode/state to input key events, toggles Caps Lock LED on press, and stops notifier propagation. LED events from input core send `SET_LEDS` commands to the EC. Remove disables wake reporting and keyboard and unregisters the notifier.

## State And Persistence
Uses one static global `keys_dev`, so only one keyboard instance is supported. Caps Lock state is cached in memory. The input keycode array is static mutable initialization data. No durable storage exists.

## Dependencies And Integration Points
Depends on NVEC notifier/write APIs, Linux input core, platform children from the NVEC MFD, and the local keytable header.

## Risks
The global singleton prevents multiple controllers. No bounds check guards `code_tabs[_size][code]` beyond protocol assumptions. Caps Lock LED toggling uses all three LED bits due to a documented firmware bug. Synchronous probe commands can delay or fail boot.

## Test Signals
Probe/remove, base and extended key events, key release polarity, Caps Lock LED via key press and EV_LED, wake configuration commands, variable-size event suppression, and notifier unregister on remove.
