# sources/distributed-fs/ceph-client/sound/core/timer.c

## Purpose

This file implements the ALSA timer core and the `/dev/snd/timer` userspace API. It manages global/card/PCM timer devices, opens master and slave timer instances, dispatches periodic callbacks, exposes ioctl/read/poll/fasync behavior to applications, registers the built-in jiffies-based system timer, and optionally supports userspace-driven timers via anonymous file descriptors.

## Important APIs, types, and functions

The exported kernel APIs are `snd_timer_instance_new()`, `snd_timer_instance_free()`, `snd_timer_open()`, `snd_timer_close()`, `snd_timer_resolution()`, `snd_timer_start()`, `snd_timer_stop()`, `snd_timer_continue()`, `snd_timer_pause()`, `snd_timer_interrupt()`, `snd_timer_new()`, `snd_timer_notify()`, `snd_timer_global_new()`, `snd_timer_global_free()`, and `snd_timer_global_register()`. Core state is held in `struct snd_timer`, `struct snd_timer_instance`, `struct snd_timer_hardware`, and the local `struct snd_timer_user`. User ABI helpers define 32-bit and 64-bit timestamped read records, status structs, queue management, ioctl dispatch, and optional `struct snd_utimer`.

## Control Flow

Timer registration starts with `snd_timer_new()` and `snd_timer_dev_register()`, which validate hardware callbacks and add devices to `snd_timer_list` in timer-id order. `snd_timer_open()` either links a slave instance into `snd_timer_slave_list` or resolves a real timer, opens hardware on first use, references the module/card, and links matching slave/master instances. Start, stop, pause, and continue route through master or slave helpers, update instance flags, program hardware, and notify control callbacks. Hardware drivers call `snd_timer_interrupt()`, which advances active instances, queues fast callbacks on `ack_list_head`, slow callbacks on `sack_list_head`, reschedules the hardware, and runs or schedules callbacks. The character-device path opens `struct snd_timer_user`, selects a timer via ioctl, configures parameters/filter/queue mode, starts or stops the instance, and serves queued tick or timestamped events through `read()` and `poll()`. Module init allocates the timer device, registers the system timer, registers the ALSA timer char device, and creates procfs output.

## State and Persistence Behavior

Persistent kernel state is list-based: registered timers, pending slaves, open master instances, per-timer active/ack lists, and per-user ring queues. `register_mutex` protects global registration/open/close linkage; per-timer spinlocks protect active and callback lists; `slave_active_lock` coordinates slave activation. Timer instance flags encode running, start-delayed, paused, auto, exclusive, early event, slave, callback, and dead states. User state persists across file operations in `file->private_data`, including queue positions, overrun count, filter mask, timestamp mode, async wakeups, and disconnect state. The system timer keeps correction and jiffies accounting in timer private data. Optional userspace-driven timers allocate global ids with an IDA and persist until the anon fd release path frees the timer.

## Dependencies and Integration Points

The code depends on ALSA core device registration, `sound/timer.h`, controls, procfs info, minors/char device registration, module autoloading, workqueues, Linux timers, wait queues, fasync, anon inodes, IDA, and card lifetime references. Integration points include PCM and MIDI drivers using ALSA timers, loopback sound-timer mode, sequencer/OSS users that open slave timers, userspace through `snd/timer`, and optional `timer_compat.c` for compat ioctls.

## Risks

The highest-risk areas are lifetime and locking between close, callbacks, card shutdown, slave/master relinking, and userspace reads. Timer callbacks deliberately drop `timer->lock`, so dead/callback flags and close waiting are critical. User queue resizing and timestamp mode changes must stay serialized by `ioctl_lock` and `qlock`. ABI risks include 32/64-bit timestamp/status layout, old ioctl numbers, filter validation, and `read()` unit sizing. Userspace-driven timers expose triggerable global timers and need strict id/fd cleanup. Resolution checks reject too-small periods, so behavior changes can break low-latency clients.

## Test Signals

Useful signals include ALSA timer ioctl tests for select/params/status/start/stop/read/poll/fasync, compat ioctl coverage on 32-bit userspace over 64-bit kernels, concurrent close while callbacks are running, slave/master attach and detach cases, card shutdown disconnect wakeups, procfs timer listing, module autoload for timer ids, system timer drift/reschedule tests, and `CONFIG_SND_UTIMER` create/trigger/fd-release tests.
