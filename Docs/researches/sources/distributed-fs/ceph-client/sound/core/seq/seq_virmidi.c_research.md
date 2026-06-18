# sources/distributed-fs/ceph-client/sound/core/seq/seq_virmidi.c

## Purpose
`seq_virmidi.c` implements virtual rawmidi devices backed by ALSA sequencer ports. A normal rawmidi device file can be connected to arbitrary sequencer clients, allowing raw MIDI applications and sequencer applications to interoperate.

## Important APIs, Types, and Functions
- `snd_virmidi_new()` creates a rawmidi device with virtual MIDI global and stream ops.
- `snd_virmidi_dev_attach_seq()` creates the backing sequencer kernel client and port in dispatch mode.
- `snd_virmidi_event_input()` receives sequencer events for the virmidi port.
- `snd_virmidi_dev_receive_event()` decodes sequencer events to raw MIDI bytes for each open input file.
- `snd_vmidi_output_work()` parses rawmidi output bytes into sequencer events and dispatches them.
- Rawmidi stream ops open/close/trigger/drain allocate per-file parser state and manage work.
- Subscription/use callbacks gate output-to-rawmidi and rawmidi-to-sequencer directions with module references.

## Control Flow
Device creation allocates a duplex rawmidi with 16 input and 16 output substreams, initializes a `snd_virmidi_dev`, and installs global/stream ops. On registration in dispatch mode, a kernel sequencer client and duplex software port are created. Rawmidi input opens allocate a `snd_virmidi`, create a decode parser, and add it to the device file list. Rawmidi output opens allocate a parser and work item.

Sequencer-to-rawmidi delivery iterates open input files under either spin/read lock or rwsem depending on atomic context, decodes events to MIDI bytes, and feeds each triggered substream. Rawmidi-to-sequencer delivery runs in a high-priority workqueue, reads bytes while triggered, encodes complete sequencer events, and dispatches them.

## State and Persistence
State is runtime-only in `snd_virmidi_dev` and per-open `snd_virmidi` objects. The device tracks file list, client/port, flags for subscription/use, mode, and locks. Each open file owns its parser, trigger flag, and pending event/work.

## Dependencies and Integration Points
Depends on rawmidi core, sequencer kernel clients, MIDI event parser, variable-event dump helpers, and ALSA card module refcounts. It can operate in dispatch mode with its own port or attach mode against an existing client/port.

## Risks
File-list locking switches between atomic and sleepable modes; mistakes could deadlock or race close. Dispatch mode drops rawmidi output unless the port is subscribed. Workqueue processing must be canceled on close to avoid use-after-free. Subscription/use flags are coarse per device, not per open file.

## Test Signals
Test multiple rawmidi opens with independent input buffers, trigger on/off behavior, dispatch mode with and without subscriptions, sysex delivery, workqueue drain/close ordering, attach mode validation, module refcount on subscribe/use, and duplex routing.
