# sources/distributed-fs/ceph-client/drivers/media/rc/ir-imon-decoder.c

Purpose: generic rc-core raw decoder and encoder for the iMON IR protocol. It parses 30-bit iMON waveforms, supports the iMON pad's keyboard/mouse toggle behavior, reports mouse events for stick movement in mouse mode, and emits `RC_PROTO_IMON` key events.

Important APIs, types, and functions: timing constants define 416 us units, 30 data bits, and a check-bit mask. `enum imon_state` models inactive, check, data, finished, and error states. `ir_imon_decode_scancode()` postprocesses the decoded 30-bit value, toggles stick keyboard mode for the keyboard/mouse key, converts stick movement to arrow scancodes in keyboard mode or input relative/mouse-button events in mouse mode, and calls `rc_keydown()`. `ir_imon_decode()` is the raw state machine. `ir_imon_encode()` builds raw events from a scancode using iMON check-bit rules. `ir_imon_register()` initializes per-device stick mode. `imon_handler` registers protocol, decode/encode hooks, carrier, raw register hook, and min timeout.

Control flow: raw rc-core dispatch passes timing events to `ir_imon_decode()`. It consumes events in unit-sized chunks, alternates check and data fields, validates dynamic check bits, enters error state on invalid timing/checks, and requires a long space before leaving error. When finished, it decodes/report the scancode and returns inactive. Module init registers the raw handler.

State and persistence behavior: per-rc-device decoder state lives in `dev->raw->imon`: state, bit count, bits, last check value, and stick keyboard flag. Mouse events are reported directly through the rc device's input device; scancode events go through rc-core.

Dependencies and integration points: depends on `rc-core-priv.h`, raw event timing helpers, input reporting for relative/mouse events, `lirc`/rc-core scancode emission through `rc_keydown()`, and module registration.

Risks and edge cases: protocol ambiguity means an incomplete message can look like one with low bits set, so the error-state long-space rule is important. Stick movement handling mutates `imon->bits` to arrow-key scancodes in keyboard mode. Mouse mode reports input relative/button events in addition to rc-keydown, so consumers may observe mixed input types.

Test signals: decode known iMON scancodes, encode/decode round trips, invalid check-bit handling, long-space recovery after error, keyboard/mouse toggle, stick arrow conversion, and mouse relative/button reporting.
