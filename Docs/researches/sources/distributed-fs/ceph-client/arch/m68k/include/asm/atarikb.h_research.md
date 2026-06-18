<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarikb.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarikb.h

## Purpose
This header declares the Atari intelligent keyboard controller interface for keyboard, mouse, joystick, and MIDI-related input handling.

## Important APIs, Types, And Functions
- `ikbd_write()` sends raw commands.
- Mouse configuration functions set button action, relative/absolute mode, keyboard-emulation mode, thresholds, scaling, position get/set, origin orientation, and disable state.
- Joystick functions enable/disable events, request state, and disable joystick reporting.
- Hooks include `atari_MIDI_interrupt_hook`, `atari_input_keyboard_interrupt_hook`, and `atari_input_mouse_interrupt_hook`.
- `atari_keyb_init()` initializes the keyboard/input subsystem.

## Control Flow
Input setup initializes IKBD and installs hooks. Drivers send IKBD commands through the declared helpers. Interrupt processing calls the registered keyboard, mouse, MIDI, or joystick hooks with decoded bytes or packet data.

## State And Persistence Behavior
State is held by the IKBD hardware and the implementation: hook pointers, current mouse/joystick mode, scaling, thresholds, and position. The header exposes the mutable hook interface.

## Dependencies And Integration Points
It integrates with Atari keyboard, mouse, joystick, MIDI, serial/ACIA, and Linux input drivers.

## Risks And Edge Cases
Hook pointers are global and must be installed/removed with care. IKBD command sequences are stateful; interleaving mode changes with interrupt packets can produce misdecoded input.

## Test Signals
Keyboard scancode delivery, relative/absolute mouse events, mouse position get/set, joystick event mode, MIDI interrupt hook execution, and init failure paths are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atarikb.h -->
