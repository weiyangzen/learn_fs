# sources/distributed-fs/ceph-client/sound/usb/line6/midi.c

## Purpose
Implements the ALSA raw MIDI interface for Line 6 devices that transport control data as MIDI over USB interrupt endpoints.

## Important APIs and Functions
`line6_init_midi()` creates a duplex rawmidi device and initializes input/output `midi_buffer` objects. `line6_midi_receive()` forwards parsed incoming MIDI bytes to the active ALSA input substream. `line6_midi_transmit()` drains ALSA rawmidi output into the MIDI buffer and submits complete chunks asynchronously. `send_midi_async()` allocates one interrupt URB per outgoing MIDI chunk, and `midi_sent()` frees it and continues draining.

## Control Flow
Output trigger stores the transmit substream, takes the MIDI spinlock, and starts transmission only when no send URBs are active. Transmission peeks from ALSA, writes into `midibuf_out`, acknowledges bytes, reads complete/splittable MIDI messages, and sends them asynchronously. Completion decrements `num_active_send_urbs`; if it reaches zero, it tries to transmit more and wakes drain waiters if still idle. Input trigger sets or clears the receive substream; incoming parsed data from `driver.c` calls `line6_midi_receive()`.

## State and Persistence
`struct snd_line6_midi` stores active input/output substreams, active send URB count, spinlock, waitqueue, and MIDI buffers. State exists only while the rawmidi device/card exists.

## Dependencies and Integration
Depends on ALSA rawmidi, USB interrupt URBs, `driver.h` endpoint properties, and `midibuf.c` message framing. `driver.c` initializes MIDI only for `LINE6_CAP_CONTROL_MIDI` and feeds received data.

## Risks and Test Signals
Risks include URB transfer buffer leak on `usb_urb_ep_type_check()`/submit failure because the error path frees the URB but not the duplicated transfer buffer, async sends after disconnect, and lock-held calls that may enqueue many URBs. Tests should cover MIDI input/output, running status, drain waits, endpoint validation failure injection, disconnect during active sends, and buffer overflow handling.
