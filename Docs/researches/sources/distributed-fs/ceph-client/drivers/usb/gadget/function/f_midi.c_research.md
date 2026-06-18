# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_midi.c

## Purpose

`f_midi.c` implements a USB MIDI 1.0 class function for the composite gadget framework. It bridges USB MIDIStreaming bulk endpoints to ALSA rawmidi substreams, supporting configurable cable counts, request sizes, queue depth, ALSA card index/id, and interface string through configfs.

## Important APIs, Types, and Functions

`struct f_midi` owns the USB function, IN/OUT bulk endpoints, ALSA card/rawmidi objects, endpoint request FIFO, work item, port counts, queue sizing, transmit lock, active output bitmap, and an array of `struct gmidi_in_port` for ALSA-output-to-USB-IN state. `struct gmidi_in_port` tracks the rawmidi substream, cable number, active flag, MIDI parser state, and buffered status/data bytes.

Descriptor construction uses AudioControl and MIDIStreaming descriptors plus dynamically generated jack descriptors for up to `MAX_PORTS` cables. USB request handling is in `f_midi_complete()`, `f_midi_handle_out_data()`, and `f_midi_read_data()`. MIDI byte packetization is in `f_midi_transmit_byte()` and `f_midi_do_transmit()`, while `f_midi_transmit()` and `f_midi_in_work()` drive queued transmission. ALSA callbacks are `f_midi_in_open/close/trigger()` for rawmidi output to USB IN and `f_midi_out_open/close/trigger()` for USB OUT to rawmidi input.

## Control Flow

`f_midi_alloc_inst()` creates configfs defaults: `buflen=512`, `qlen=32`, one input and one output port. `f_midi_alloc()` copies options, allocates the flexible `f_midi` instance, initializes cable numbers, allocates a FIFO of preallocated IN requests, and wires USB function callbacks. `f_midi_bind()` registers the ALSA card, assigns strings and two interfaces, autoconfigures bulk endpoints, builds jack and endpoint descriptors according to configured port counts, and copies FS/HS/SS descriptor sets.

When the host selects the MIDIStreaming alternate setting, `f_midi_set_alt()` enables endpoints, preallocates IN requests into `in_req_fifo`, allocates and queues OUT requests, and leaves completions to recycle requests. USB OUT completions decode four-byte USB MIDI event packets and deliver MIDI bytes to active ALSA input substreams. ALSA output triggers queue high-priority work that drains rawmidi bytes through the MIDI state machine into USB MIDI event packets and queues IN requests. Disable tears down endpoints, frees queued IN requests, and drops pending ALSA output.

## State and Persistence Behavior

Runtime state is volatile. MIDI running status, SysEx assembly, active cable flags, rawmidi substream pointers, and queued USB requests live in `struct f_midi`. `transmit_lock` serializes use of the IN request FIFO and parser state. `free_ref` coordinates lifetime between the USB function and ALSA rawmidi private free path. Configfs options are locked by `f_midi_opts.lock` and become immutable after active references. No MIDI data or configuration is persisted by the driver.

## Dependencies and Integration Points

The driver depends on the USB composite framework, USB Audio/MIDI descriptor definitions, `linux/usb/func_utils.h` request helpers, ALSA core/rawmidi, `kfifo`, workqueues, and configfs. It registers as `DECLARE_USB_FUNCTION_INIT(midi, ...)`, exposing a `midi` function in configfs. User space sees an ALSA rawmidi card named `MIDI Gadget` and a USB MIDIStreaming interface on the host side.

## Risks and Test Signals

Risks include MIDI parser correctness for running status, SysEx termination, real-time interleaving, and malformed USB MIDI CIN values; request leaks or double-free during disable and disconnect; endpoint queue failure recovery that halts OUT; unbounded config choices for `buflen` and `qlen`; port-count edge cases at 0 or 16; and lifetime coupling between ALSA card closure and USB function free.

Strong test signals include ALSA rawmidi loopback across all configured cables, SysEx and real-time message streams, short packets and disconnect while transfers are pending, repeated set-alt/disable cycles, FS/HS/SS descriptor validation, configfs writes rejected while bound, port-count boundary tests, and host interoperability with Linux/macOS/Windows class drivers.
