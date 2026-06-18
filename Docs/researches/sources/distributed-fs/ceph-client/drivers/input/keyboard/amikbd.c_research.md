# sources/distributed-fs/ceph-client/drivers/input/keyboard/amikbd.c

Purpose: implements the Amiga keyboard driver for Linux/m68k, reading CIAA serial keyboard scancodes and exposing them through the Linux input subsystem.

Important APIs/types/functions: `amikbd_keycode` maps Amiga scancodes to Linux keycodes when VT is enabled. `amikbd_init_console_keymaps` rewrites console keymaps to match Amiga scancode positions. `amikbd_messages` maps keyboard controller/error codes. `amikbd_interrupt` handles CIAA serial-port interrupts. `amikbd_probe` allocates/registers the input device and IRQ.

Control flow: probe allocates a devm input device, sets `BUS_AMIGA`, enables key and repeat events, marks scancodes 0..0x77 as keys, initializes console keymaps, configures CIAA serial direction/control, requests `IRQ_AMIGA_CIAA_SP`, registers input, and stores drvdata. On interrupt, the handler reads and inverts `ciaa.sdr`, toggles CIAA CRA bit 0x40 for the required 85 us handshake, derives press/release from bit 0, shifts to the scancode, reports normal keys or special CapsLock press+release toggle behavior, syncs, or logs controller messages for scancodes 0x78..0x7f.

State and persistence: there is no heap driver state beyond the input device. Console keymap modifications occur during init when VT support is present and persist in kernel keymap memory.

Dependencies and integration: depends on AMIGA architecture hardware headers, CIAA registers, Amiga IRQ definitions, platform driver probing, Linux input, and optional VT keyboard maps.

Risks: direct hardware register manipulation and microsecond handshake timing are architecture-specific. Console keymap rewriting is global and init-time only. CapsLock behavior intentionally emits a pulse rather than hold state. Error scancode logging indexes `amikbd_messages` and assumes only 0x78..0x7f error codes.

Test signals: Amiga hardware or emulator tests for key press/release, CapsLock toggle, controller error scancodes, CIAA handshake timing, VT keymap correctness, and platform probe/IRQ request failures.
