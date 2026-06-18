# sources/distributed-fs/ceph-client/sound/core/timer_compat.c

## Purpose

This included source provides the 32-bit compat ioctl bridge for the ALSA timer userspace API. It adapts timer structures whose layout differs between ILP32 and LP64 processes and forwards compatible commands into the shared timer ioctl implementation.

## Important APIs, Types, and Functions

The local ABI types are packed `struct snd_timer_gparams32` and `struct snd_timer_info32`. `snd_timer_user_gparams_compat()` copies a 32-bit global-params request and calls `timer_set_gparams()`. `snd_timer_user_info_compat()` builds a 32-bit info record for the currently selected timer. `__snd_timer_user_ioctl_compat()` maps compat command numbers to native handlers or compat-specific helpers. `snd_timer_user_ioctl_compat()` serializes access with the same per-file `ioctl_lock` used by native ioctl.

## Control Flow

The file is included from `timer.c` only when `CONFIG_COMPAT` is enabled. Most commands are layout-compatible and are forwarded to `__snd_timer_user_ioctl(..., compat=true)` after converting the argument with `compat_ptr()`. Commands with `long` or alignment-sensitive layout use local compat command numbers and local copy logic. Unsupported commands return `-ENOIOCTLCMD`, allowing higher ioctl layers to report the appropriate failure.

## State and Persistence Behavior

This file owns no standalone state. It reads and writes `struct snd_timer_user` stored on the open file, reads selected timer metadata, and can update global timer parameters through `timer_set_gparams()`. Serialization and persistence are inherited from `timer.c`.

## Dependencies and Integration Points

It depends on `linux/compat.h` and on static symbols from the including translation unit, including `timer_set_gparams()`, `snd_timer_user_status32()`, `snd_timer_user_status64()`, and `__snd_timer_user_ioctl()`. It is wired into `snd_timer_f_ops.compat_ioctl`.

## Risks

The main risks are ABI drift, wrong ioctl direction/size constants, packed alignment mismatches, and differences from native info retrieval. Notably the compat info path reports `t->hw.resolution` directly rather than `snd_timer_hw_resolution()`, so dynamic-resolution timers may differ from native `SNDRV_TIMER_IOCTL_INFO`. Missing coverage for newly added native ioctls would strand 32-bit applications.

## Test Signals

Run 32-bit ALSA timer clients against a 64-bit kernel for `PVERSION`, `TREAD`, `GINFO`, `GPARAMS`, `GSTATUS`, `SELECT`, `PARAMS`, both status layouts, and start/stop/continue/pause. Compare native and compat info/status output for dynamic-resolution timers and verify invalid pointers return `-EFAULT`.
