# sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_core.c

## Purpose

`dmasound_core.c` is the machine-independent OSS compatibility core for the legacy DMA sound stack used by Atari, Amiga, and Q40 style low-level drivers. It registers `/dev/dsp` or `/dev/audio`, `/dev/mixer`, and `/dev/sndstat` through the old sound core APIs, owns the playback queue, translates user audio samples through a low-level `TRANS` table, and dispatches hardware operations through the global `dmasound.mach` `MACHINE` callback table.

## Important APIs, Types, and Functions

The public exports are `dmasound`, `dmasound_init()`, `dmasound_deinit()`, `dmasound_write_sq`, `dmasound_catchRadius`, and, when enabled, `dmasound_ulaw2dma8` / `dmasound_alaw2dma8`. Low-level modules fill `dmasound.mach` before calling `dmasound_init()`.

Important internal entry points are `sq_open()`, `sq_write()`, `sq_ioctl()`, `sq_poll()`, `sq_release()`, `mixer_ioctl()`, and `state_open()`/`state_read()`. Queue setup is handled by `sq_allocate_buffers()`, `sq_setup()`, `sq_reset_output()`, `sq_fsync()`, and `set_queue_frags()`. Format/rate/channel settings flow through `sound_set_format()`, `sound_set_speed()`, and `sound_set_stereo()`, while user-copy conversion is centralized in `sound_copy_translate()`.

## Control Flow

Initialization starts in `dmasound_init()`: it registers the DSP file operations, registers the status device, registers the mixer, invokes `dmasound.mach.irqinit()`, and logs the core and machine editions. A low-level driver is responsible for assigning machine callbacks first. Open acquires `dmasound_core_mutex`, takes the low-level module reference with `try_module_get()`, allocates default playback buffers, rejects read mode because this core instance does not implement capture, and resets shared soft/hard settings if no owner exists.

Playback is lazy. `sq_write()`, `SNDCTL_DSP_GETBLKSIZE`, `SNDCTL_DSP_GETOSPACE`, and `poll()` force `sq_setup()` if the queue is not locked. `sq_setup()` calls the hardware `init()` callback, computes internal block sizes from user fragment settings and soft-to-hard sample geometry, resets queue counters, and invokes `write_sq_setup()` if the backend provides it. `sq_write()` appends to a partial rear fragment when possible, waits on `action_queue` when `count >= max_active`, copies/translates user data into DMA buffers, advances queue indices, and calls the backend `play()` callback to start or continue hardware output.

`sq_ioctl()` implements OSS reset, sync, format, channel, speed, fragment, block-size, space, and capability calls. Mixer ioctls first satisfy generic `OSS_GETVERSION` and `SOUND_MIXER_INFO`, then pass unknown mixer commands to `dmasound.mach.mixer_ioctl()`. `/dev/sndstat` snapshots machine revision, low-level status, soft/hard settings, and playback queue counters into a fixed-size buffer.

## State and Persistence

Persistent runtime state is held in global statics and `dmasound`: registered unit numbers, `irq_installed`, module parameters `numWriteBufs`, `writeBufSize`, and `dmasound_catchRadius`, mixer busy/modify counters, status buffer position, `shared_resource_owner`, `shared_resources_initialised`, and the exported `dmasound_write_sq`. There is no disk persistence. Register state is delegated to low-level callbacks; buffer memory is allocated with `dmasound.mach.dma_alloc()` and released on close/deinit.

Concurrency uses `dmasound_core_mutex` around open/release/ioctl/status/mixer state and `dmasound.lock` around queue flags touched by write and interrupt-capable low-level paths. The queue uses `action_queue` for writer space and `sync_queue` for drain completion.

## Dependencies and Integration Points

The file depends on legacy OSS headers, sound core registration (`register_sound_dsp`, `register_sound_mixer`, `register_sound_special`), Linux user-copy helpers, module references, wait queues, mutexes, and the local `dmasound.h` contracts. It integrates with backends through the `MACHINE` callbacks: DMA allocation, IRQ lifecycle, init/silence/play, format/volume/tone setters, mixer hooks, queue setup, and status hooks.

## Risks and Edge Cases

The driver is globally stateful and effectively single-playback-queue. Comments call out race risks when multiple threads share an O_RDWR file descriptor, though read is currently rejected. Queue parameter changes after first write are mostly rejected through `queues_are_quiescent()`, but speed changes can invalidate resources and rely on deferred re-init. `sq_setup()` does integer scaling between soft and hard formats and has several bounds repairs rather than strict validation. `state_open()` uses deterministic lengths but still uses `sprintf()` into a fixed buffer and relies on low-level `state_info()` respecting `LOW_LEVEL_STAT_ALLOC`. `dmasound_setup()` references `catchRadius` via macro and accepts legacy boot parameters without power-of-two buffer enforcement.

## Test Signals

Useful tests are build coverage for all dmasound backends, module load/unload with IRQ init failure paths, OSS open/write/poll/fsync/ioctl smoke tests, `SNDCTL_DSP_SETFRAGMENT` boundary checks, nonblocking writes returning `-EAGAIN`, signal interruption during write and sync, `/dev/sndstat` buffer-length validation, mixer ioctl pass-through, and repeated open/close to catch buffer release and module reference leaks.
