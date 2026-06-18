# sources/distributed-fs/ceph-client/include/sound/compress_driver.h

## Purpose
`compress_driver.h` defines the in-kernel driver interface for ALSA compressed offload devices. It models compressed streams, runtime buffer accounting, DSP callback operations, optional accelerator tasks, device registration, wakeups, drain completion, DMA buffer assignment, and error-stop helpers.

## Important APIs, Types, and Functions
Key types are `struct snd_compr_task_runtime`, `struct snd_compr_runtime`, `struct snd_compr_stream`, `struct snd_compr_ops`, and `struct snd_compr`. Driver callbacks include `open`, `free`, `set_params`, `get_params`, metadata get/set, `trigger`, `pointer`, optional `copy`, `mmap`, `ack`, capability queries, and optional task operations. APIs include `snd_compress_new()`, `snd_compr_fragment_elapsed()`, `snd_compr_drain_notify()`, `snd_compr_set_runtime_buffer()`, page allocation/free, `snd_compr_stop_error()`, and `snd_compr_task_finished()` when acceleration is enabled.

## Control Flow
The compress core opens streams, asks the DSP driver to set codec parameters, accepts writes or mmap acknowledgements, triggers start/pause/drain/stop, polls timestamps, and wakes sleepers when fragments or drains complete. Error handling can force stream state transitions through delayed work.

## State and Persistence Behavior
Runtime state includes PCM-like stream state, ring counters, buffer geometry, DMA area, wait queue, private data, stream flags, and optional task lists/counters. It persists only for the open stream.

## Dependencies and Integration Points
It depends on ALSA core, compressed-offload UAPI, PCM state types, DMA buffers, wait queues, mmap, and optional `CONFIG_SND_COMPRESS_ACCEL`.

## Risks and Test Signals
Risks include inconsistent state transitions around drain and pause, copy-vs-mmap callback misuse, counter wrap, DMA lifetime errors, and task completion races. Test signals include open/set_params/trigger ioctl tests, poll wakeups, drain/partial-drain behavior, mmap and copy modes, error-stop paths, and accelerator task lifecycle tests.
