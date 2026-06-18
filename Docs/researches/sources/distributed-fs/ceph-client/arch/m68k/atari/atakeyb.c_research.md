# sources/distributed-fs/ceph-client/arch/m68k/atari/atakeyb.c

Purpose: Atari IKBD/ACIA keyboard, mouse, joystick, and MIDI interrupt handling plus command helpers.

Important exports include `atari_input_keyboard_interrupt_hook`, `atari_input_mouse_interrupt_hook`, and `atari_keyb_init()`. Optional hook `atari_MIDI_interrupt_hook` lets MIDI serial code participate. The core parser uses `KEYBOARD_STATE` with states `KEYBOARD`, `AMOUSE`, `RMOUSE`, `JOYSTICK`, `CLOCK`, and `RESYNC`.

Interrupt flow repeatedly checks MIDI and keyboard ACIA status, handles overruns by resynchronizing packet state, decodes keyboard make/break scancodes, records broken keys during IKBD self-test, and dispatches keyboard or mouse packets to input hooks. Error bits log communication problems, and the handler loops to drain additional pending bytes.

Command APIs such as `ikbd_write()`, mouse mode/scale/threshold commands, joystick commands, and disable helpers poll ACIA transmit readiness and send fixed IKBD command bytes. `atari_keyb_init()` requests `IRQ_MFP_ACIA`, resets both ACIAs, configures baud/control based on `atari_switches`, enables the interrupt, performs the IKBD self-test, disables mouse/joystick, and marks initialization done.

State includes hook pointers, parser buffer/state, self-test flags/timestamps, `broken_keys`, ACIA hardware registers, and `atari_keyb_done`. Exports integrate with input drivers and optional joystick code.

Risks and test signals: overrun/resync mistakes can interpret mouse bytes as key events; polling writes can take milliseconds; self-test waits spin on jiffies. Test keyboard make/break, mouse relative packets, MIDI hook dispatch, ACIA overrun recovery, and reentrant init calls.
