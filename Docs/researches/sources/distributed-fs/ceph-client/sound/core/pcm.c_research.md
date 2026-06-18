# sources/distributed-fs/ceph-client/sound/core/pcm.c

## Purpose

`pcm.c` is the ALSA midlevel PCM registry and lifecycle implementation. It creates PCM devices and streams, manages substreams and runtime allocation, exposes control ioctls for PCM enumeration/info, registers device nodes and procfs/sysfs entries, handles disconnect/suspend teardown, and provides the OSS notifier hook used by `pcm_oss.c`.

## Important APIs, Types, and Functions

Public APIs include `snd_pcm_format_name()`, `snd_pcm_new_stream()`, `snd_pcm_new()`, `snd_pcm_new_internal()`, `snd_pcm_attach_substream()`, `snd_pcm_detach_substream()`, and `snd_pcm_notify()`. Global state includes `snd_pcm_devices`, `register_mutex`, and, when OSS is enabled, `snd_pcm_notify_list`. Device callbacks are `snd_pcm_dev_register()`, `snd_pcm_dev_disconnect()`, and `snd_pcm_dev_free()`.

## Control Flow

PCM creation allocates a `struct snd_pcm`, initializes locks and wait queues, creates playback and capture streams, and registers an ALSA device object. Stream creation allocates stream devices, procfs roots, substream objects, self groups, and mmap counters. Registration inserts the PCM in sorted global order, registers playback/capture device nodes, initializes timers, and calls OSS notifiers. Opening a substream selects an available or preferred subdevice, handles half-duplex exclusion, allocates runtime/status/control pages, initializes wait queues and buffer locks, sets state to OPEN, stores the current PID, and returns the substream.

Disconnect removes the PCM from the global list, wakes waiters, marks live runtimes DISCONNECTED, stops running streams, sync-stops substreams, notifies OSS, unregisters devices, and removes channel maps. Freeing invokes unregister notifiers, private cleanup, preallocation cleanup, stream/substream freeing, and PCM object free.

## State and Persistence Behavior

Persistent PCM state includes the global device list, each PCM's streams, substreams, open counts, proc roots, sysfs devices, channel-map controls, and runtime objects while open. Runtime status/control pages are separately allocated to support mmap-visible state. OSS setup lists are stream-persistent when OSS support is built in.

## Dependencies and Integration Points

This file depends on ALSA card/device/control/timer/info core, PCM native file ops, procfs, sysfs device registration, PM callbacks, and optional OSS notification. User control ioctls call into `snd_pcm_info_user()`, while PCM device nodes use file ops declared elsewhere.

## Risks and Edge Cases

Registration and disconnect are lock-sensitive because the global PCM list, open waiters, device nodes, and runtime state can change concurrently. Preferred subdevice and `O_APPEND` reopen semantics are subtle. Runtime detach must avoid timer races by clearing `substream->runtime` under timer lock when needed. Missing notifier cleanup can leave stale OSS minors.

## Test Signals

Validate PCM enumeration via control ioctls, playback/capture device registration, substream open/close, preferred subdevice behavior, half-duplex exclusion, suspend/disconnect while open, procfs status files, sysfs `pcm_class`, and OSS notifier registration/unregistration.
