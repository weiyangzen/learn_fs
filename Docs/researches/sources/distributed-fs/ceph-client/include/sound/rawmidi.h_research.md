# sources/distributed-fs/ceph-client/include/sound/rawmidi.h

Source read summary: 203 lines, ALSA raw MIDI kernel interface.

Purpose: declares rawmidi devices, substreams, runtime buffers, file state, callbacks, creation, data transfer, kernel-open, params, drain/drop, and device tie helpers.

Important APIs, types, and functions: `struct snd_rawmidi_ops` defines open/close/trigger/drain, `struct snd_rawmidi_global_ops` handles device-level open/close/dev_register/dev_disconnect, `struct snd_rawmidi_runtime` stores buffer, size, avail/used/appl/hw pointers, xruns, locks, waitqueue, event flag, and private data. `struct snd_rawmidi_substream`, `snd_rawmidi_file`, `snd_rawmidi_str`, and `snd_rawmidi` define device topology and state. APIs include `snd_rawmidi_new()`, `set_ops()`, `init()`, `free()`, receive/transmit helpers, kernel open/release, params, drain/drop, and `snd_rawmidi_tie_devices()`.

Control flow: drivers create rawmidi devices, assign stream ops, open substreams from userspace or kernel clients, trigger input/output, move bytes through receive/transmit ring helpers, and drain/drop on close or ioctl.

State and persistence behavior: runtime ring buffers, pointer counters, avail/min/max sizes, active flags, and app/user PID state are volatile per open stream. MIDI data is not persisted.

Dependencies and integration points: depends on ALSA core/info, waitqueues, spinlocks, mutexes, and sequencer port info. Used by MPU-401, USB MIDI, virtual MIDI, and sequencer bridges.

Risks and edge cases: ring pointer wrap, xrun accounting, trigger/open races, drain waiting forever, kernel and userspace clients sharing streams, and tied-device lifetime.

Test signals: input/output byte transfer, buffer parameter changes, trigger start/stop, drain/drop, kernel open, sequencer integration, multiple subdevices, and disconnect with open streams.
