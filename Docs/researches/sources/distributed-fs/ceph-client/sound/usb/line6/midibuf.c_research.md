# sources/distributed-fs/ceph-client/sound/usb/line6/midibuf.c

## Purpose
Provides a small circular MIDI message buffer with MIDI message boundary detection, optional splitting for transmit, running-status support, active-sense suppression, and Line 6 receive-channel correction.

## Important APIs and Functions
Public functions initialize/reset/destroy buffers, report bytes free/used, write bytes, read a complete message or split chunk, and ignore bytes. `midibuf_message_length()` classifies MIDI status bytes. `line6_midibuf_read()` is the core parser and supports `LINE6_MIDIBUF_READ_TX` and `LINE6_MIDIBUF_READ_RX` modes.

## Control Flow
Writes drop a trailing active-sense byte `0xfe`, clamp to free space, and copy with wraparound. Reads require at least a three-byte destination, examine the next command, correct PODxt receive status bytes `0xb2`, `0xc2`, and `0xf2` to channel-zero status, use the current or previous status byte to determine MIDI length, search for the next status byte for variable-length data, optionally return zero until a complete message is available, copy with wraparound, inject running status when needed, and clears the full flag. Ignore advances the read pointer modulo size.

## State and Persistence
`struct midi_buffer` stores heap buffer, size, split behavior, read/write positions, full flag, and previous command. State is volatile and protected by callers, usually the MIDI spinlock.

## Dependencies and Integration
Used by `midi.c` for outgoing message framing and by `driver.c` for incoming MIDI-control message parsing. Depends only on kernel allocation and memory copy helpers.

## Risks and Test Signals
Risks include incomplete SysEx messages stalling reads when split is disabled, running-status edge cases, active-sense accounting returning more consumed bytes than stored, and caller responsibility for locking. Tests should feed status/data byte sequences, wraparound cases, running status, malformed/partial SysEx, buffer-full overflow, RX channel correction, and TX split mode.
