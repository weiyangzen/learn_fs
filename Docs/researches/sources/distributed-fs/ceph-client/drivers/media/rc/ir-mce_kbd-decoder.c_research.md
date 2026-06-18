# sources/distributed-fs/ceph-client/drivers/media/rc/ir-mce_kbd-decoder.c

Purpose: raw decoder/encoder for the MCIR-2 keyboard and mouse protocol used by Microsoft Remote Keyboard for Windows Media Center. It converts IR keyboard reports to Linux input key events, mouse reports to relative/button events, emits lirc scancode events, and supports raw transmission.

Important APIs, types, and functions: `kbd_keycodes[256]` maps HID-like usage bytes to Linux keycodes. `mce_kbd_rx_timeout()` releases all keys after inactivity. `mce_kbd_mode()` interprets header mode. `ir_mce_kbd_process_keyboard_data()` reports modifier and up to two key bytes. `ir_mce_kbd_process_mouse_data()` decodes signed 7-bit X/Y and buttons. `ir_mce_kbd_decode()` is the Manchester-like state machine for 5-bit header plus 29-bit mouse or 32-bit keyboard body. `ir_mce_kbd_register()` initializes timer/spinlock; `ir_mce_kbd_unregister()` deletes the timer. `ir_mce_kbd_encode()` builds raw events using `ir_raw_gen_manchester()`. `mce_kbd_handler` registers keyboard and mouse protocol bits.

Control flow: decoding starts on the prefix pulse, reads header bits, selects keyboard or mouse body length, reads body bits, and on a finishing space processes the report. Keyboard reports update key state under `keylock`, arm or delete a release timer, send lirc scancode events, emit `MSC_SCAN`, and sync input. Mouse reports emit relative movement and button state. Raw registration initializes per-device support structures.

State and persistence behavior: per-device state in `dev->raw->mce_kbd` includes decode state, header/body/count, wanted bits, timer, and keylock. Keyboard key state persists in the input subsystem until updated or cleared by timeout.

Dependencies and integration points: depends on rc-core raw handler infrastructure, input subsystem key/relative reporting, lirc scancode events, timers, and spinlocks. Media keys that look like stock MCE RC6 are intentionally left to the RC6 decoder.

Risks and edge cases: key release depends on timer behavior; missed empty keyboard reports can leave keys pressed until timeout. The keycode table contains many reserved slots, so unknown usages are ignored or report reserved. Mouse signed conversion must preserve 7-bit two's-complement values. Header mode rejection prevents unrelated RC6-like frames from being misreported.

Test signals: decode keyboard single key, modifier combinations, all-keys-release report, timeout release, mouse movement/buttons, lirc scancode emission for both protocols, encode keyboard and mouse scancodes, and unregister while timer is pending.
