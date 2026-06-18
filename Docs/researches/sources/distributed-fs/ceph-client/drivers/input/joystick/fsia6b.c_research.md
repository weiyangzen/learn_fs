# sources/distributed-fs/ceph-client/drivers/input/joystick/fsia6b.c

Purpose: Serio driver for FlySky FS-iA6B iBus RC receiver, exposing 14 servo channels as ABS axes and optional discrete switch positions as buttons.

Important APIs/types/functions: `IBUS_SERVO_COUNT` fixes 14 channels. `fsia6b_axes[]` maps channels to ABS codes. `switch_config` module parameter supplies 14 characters, each 0-3, describing switch positions per channel. `struct ibus_packet` stores parser state, offset, rolling 16-bit input buffer, and channel values. `fsia6b_serio_irq()` implements SYNC/COLLECT/PROCESS byte parser and event reporting. `fsia6b_serio_connect()` validates switch config, sets axis ranges, opens serio, and registers input.

Control flow: Interrupt handler shifts each incoming byte into a 16-bit word. It waits for sync `0x4020`, skips one collect word, then records 14 channel words. Once complete, it reports all ABS channels, maps channel values above 1900 or below 1100 to switch states according to `switch_config`, syncs input, and returns to SYNC.

State and persistence: Per-device parser state persists across serial bytes. Switch configuration is module-global and read at connect. No persistent storage.

Dependencies and integration points: Uses serio RS232 protocol `SERIO_FSIA6B`, input core, and module parameter parsing.

Risks: There is no checksum validation visible in this parser, so line noise can produce false channel data once sync is acquired. `switch_config` is indexed for 14 channels; too-short strings would be unsafe if module parameter validation elsewhere does not enforce length. Thresholds are hard-coded for typical FS-i6 output.

Test signals: Valid iBus frames for all 14 channels; corrupted sync and partial frames; switch_config values 0,1,2,3 and invalid characters; channel threshold edges 1100/1900; serio disconnect cleanup.
