# sources/distributed-fs/ceph-client/sound/core/rawmidi_compat.c

Purpose: provides 32-bit compat ioctl handling for the raw MIDI API when included by `rawmidi.c` under `CONFIG_COMPAT`.

Important APIs, types, and functions: defines packed `struct snd_rawmidi_params32` and `struct compat_snd_rawmidi_status64`, compat ioctl numbers, `snd_rawmidi_ioctl_params_compat()`, `snd_rawmidi_ioctl_status_compat64()`, and `snd_rawmidi_ioctl_compat()`.

Control flow: compat dispatch maps commands with pointer conversion through `compat_ptr()`. Simple commands delegate to native `snd_rawmidi_ioctl()`. Parameters are copied field-by-field into native `struct snd_rawmidi_params`, then routed to input or output parameter setters. Status calls native status helpers and copies size-converted availability/xrun counters back to 32-bit userspace.

State and persistence: no independent persistent state. It mutates the same `struct snd_rawmidi_file` substream runtime settings and xrun counters reached by the native ioctl path.

Dependencies and integration: depends on native rawmidi helpers in the including translation unit, Linux compat APIs, and optional UMP ioctl passthrough.

Risks: field-by-field conversion must preserve ABI layout and avoid leaking uninitialized native padding. Size truncation of `avail` and `xruns` into 32-bit compat fields can lose high bits. The compat params path does not apply the native `user_pversion` legacy-mode adjustment because it bypasses `SNDRV_RAWMIDI_IOCTL_PARAMS` native dispatch.

Test signals: 32-bit userspace ioctl tests should cover params for input/output, status32/status64, invalid stream ids, missing read/write substreams, UMP passthrough when enabled, and pointer fault paths.
