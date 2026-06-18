# sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound.h

Purpose: Provides shared definitions for the legacy OSS dmasound core and platform backends. It defines minor-device constants, endian conversion macros, ioctl helpers, buffer sizing policy, machine callback interface, translation callback table, global sound settings, and shared write queue state.

Important APIs/types/functions: Key types are `SETTINGS`, `MACHINE`, `TRANS`, `struct sound_settings`, and `struct sound_queue`. Key helpers/macros are `IOCTL_IN`, `IOCTL_OUT`, `ioctl_return()`, `dmasound_set_volume()`, `dmasound_set_bass()`, `dmasound_set_treble()`, `dmasound_set_gain()`, `WAKE_UP`, `write_sq`, and `catchRadius`. It declares `dmasound_init()`, `dmasound_deinit()`, global `dmasound`, conversion tables, and `dmasound_write_sq`.

Control flow: Platform backends fill a `MACHINE` struct with callbacks for allocation, IRQ setup, init/silence, format/mixer controls, playback, queue setup, and state reporting. The core calls these callbacks and uses `TRANS` conversion routines to copy userspace audio into DMA-ready queue buffers.

State and persistence: Global runtime state is in `struct sound_settings dmasound` and `struct sound_queue dmasound_write_sq`, including hardware/soft format settings, mixer values, current minor device, queue fragments, active buffer counts, wait queues, and xrun/died flags.

Dependencies/integration: Depends on Linux types, OSS `soundcard.h` users in C files, platform-defined conversion tables, and dmasound core implementation. Risks include global mutable state, callback nullability, legacy ioctl semantics, queue concurrency around non-volatile counters, fixed buffer limits, and platform-specific assumptions in shared macros. Test signals are OSS device open/write/sync behavior, mixer ioctl round trips, queue wakeups, format conversion correctness, and platform backend init/deinit.
