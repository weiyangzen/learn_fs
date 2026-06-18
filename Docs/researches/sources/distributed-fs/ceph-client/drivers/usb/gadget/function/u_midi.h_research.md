## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_midi.h

Purpose: declares configfs option state for the legacy USB MIDI gadget function.

Important APIs and types:
- `struct f_midi_opts` embeds `usb_function_instance` and stores ALSA card index/id, interface string, number of IN/OUT virtual MIDI ports, request buffer length, queue length, plus `lock` and `refcnt`.

Control flow and integration:
- Configfs initializes port counts, ALSA identity, and transfer sizing before bind.
- The MIDI function uses these options to create USB MIDI descriptors and an ALSA rawmidi/card interface.

State and persistence:
- Per-function-instance in-memory configuration; strings may be dynamically allocated by configfs store paths in the implementation.

Dependencies:
- USB composite framework and ALSA/MIDI implementation files.

Risks:
- Large `buflen`/`qlen` values increase memory use and endpoint latency; small values can drop/fragment MIDI events.
- Port counts must match descriptor generation and ALSA substream setup.

Test signals:
- Bind with several IN/OUT port combinations, enumerate on host, send MIDI events both directions, and verify ALSA rawmidi devices.
