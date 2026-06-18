# sources/distributed-fs/ceph-client/drivers/input/joystick/twidjoy.c

Purpose: treats the original RS-232 Handykey Twiddler chording keyboard as a joystick with 18 buttons and two tilt axes.

Important APIs/types/functions: `struct twidjoy_button_spec` maps packed button bit fields to Linux button codes. `struct twidjoy` stores input device, packet index, five-byte buffer, and phys string. `twidjoy_process_packet`, `twidjoy_interrupt`, `twidjoy_connect`, and `twidjoy_disconnect` implement decode and lifecycle.

Control flow: connect allocates a `BUS_RS232` input device, declares ABS_X/ABS_Y ranges, and sets every button listed in `twidjoy_buttons`. The interrupt handler uses packet MSB conventions to resynchronize: byte 0 has MSB clear and following bytes have MSB set. Once five bytes are buffered, processing combines two 7-bit chunks into button state, reports exactly one active button per multi-value row spec, unpacks signed 8-bit-ish X/Y tilt fields, reports negated X and positive Y, syncs, and resets.

State and persistence: only current packet assembly state persists. The driver does not store key chords, layouts, or calibration.

Dependencies and integration: depends on serio protocol `SERIO_TWIDJOY` and Linux input key/axis reporting. It intentionally does not integrate with the keyboard text input stack.

Risks: malformed MSB patterns are ignored or resync the stream. The button loop uses `bitmask` both as a mask and count, which works for masks 1 and 3 but is not a generic bitmap iterator. Tilt ranges are declared -50..50 even though decoded values can be wider, so userspace should observe actual clipping/normalization behavior.

Test signals: feed valid five-byte frames, test resync on wrong MSB bytes, verify one-of-three row button behavior, validate signed tilt decode, and confirm autorepeat is absent.
