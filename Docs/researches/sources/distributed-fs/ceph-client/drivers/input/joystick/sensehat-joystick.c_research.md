# sources/distributed-fs/ceph-client/drivers/input/joystick/sensehat-joystick.c

Purpose: Platform input driver for Raspberry Pi Sense HAT joystick buttons, using a parent regmap and IRQ to report five key states.

Important APIs/types/functions: `struct sensehat_joystick` stores platform device, input device, previous button bitmap, and parent regmap. `keymap[]` maps five bits to DPAD down/right/up/select/left. `sensehat_joystick_report()` reads register `0xf2`, diffs against previous state, reports only changed keys, syncs, and updates previous state. `sensehat_joystick_probe()` obtains the parent regmap, allocates input, sets key/repeat capabilities, registers input, and requests threaded IRQ.

Control flow: Probe sets up the input before requesting IRQ. Each IRQ reads current key state through regmap, computes `changes` with `bitmap_xor()`, reports each changed key according to the map, and syncs. Failed regmap reads return `IRQ_NONE`.

State and persistence: `prev_states` tracks last reported button bits. All memory/resources are devm-managed. No persistent storage.

Dependencies and integration points: Platform bus, OF compatible `raspberrypi,sensehat-joystick`, parent regmap from Sense HAT MFD, threaded IRQ, input core with key repeat.

Risks: Initial `prev_states` is zero, so keys already pressed before first IRQ will be reported as pressed on first interrupt but there is no initial sync at probe. `bitmap_xor()` is used on scalar `unsigned long` storage; this is valid for small bitmaps but should stay aligned with keymap length. Regmap errors drop the IRQ as unhandled.

Test signals: IRQ with each of five bits changing; simultaneous changes; regmap read error; initial pressed state; key repeat capability; OF binding and missing parent regmap.
