<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_midi.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_midi.c

## Purpose
Implements ALSA rawmidi input/output for US-144MKII over proprietary bulk endpoints with packet padding and deferred processing.

## APIs, Types, and Functions
Exports `tascam_midi_in_urb_complete()`, `tascam_midi_out_urb_complete()`, and `tascam_create_midi()`. Internal callbacks include rawmidi open/close/trigger/drain operations and work handlers `tascam_midi_in_work_handler()` and `tascam_midi_out_work_handler()`.

## Control Flow, State, and Persistence
MIDI input trigger resets the FIFO, submits all IN URBs, and marks `midi_in_active`; completions enqueue raw bytes into `midi_in_fifo`, schedule work, and resubmit. The input worker consumes 9-byte device packets, strips `0xfd` padding from the first eight bytes, and feeds ALSA rawmidi. MIDI output trigger marks active and schedules work. The output worker finds a free URB bit, pulls up to eight bytes from ALSA, pads with `0xfd`, writes a final marker byte, sets the in-flight bit, and submits. Completion clears the bit and reschedules while active. Drain waits for in-flight bits to clear, cancels work, and kills anchored OUT URBs.

## Dependencies and Integration
Depends on ALSA rawmidi, USB bulk URBs, `kfifo`, spinlocks, anchors, and URBs allocated in `tascam_alloc_urbs()`.

## Risks and Test Signals
Risks include FIFO overflow not surfaced, close callbacks not clearing substream pointers, busy-wait style drain using `schedule_timeout_uninterruptible(1)`, output protocol marker/padding assumptions, and lock scope around `snd_rawmidi_transmit()`. Test signals are MIDI loopback, high-rate SysEx-like traffic, trigger stop/start cycles, disconnect during drain, and padding stripping correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_midi.c -->
