# sources/distributed-fs/ceph-client/sound/core/hwdep_compat.c

## Purpose
`hwdep_compat.c` is included by `hwdep.c` when compat support is enabled. It translates 32-bit hardware-dependent DSP image ioctls into native `snd_hwdep_dsp_image` calls.

## Important APIs, Types, and Functions
The main compat type is `snd_hwdep_dsp_image32`, with 32-bit fields for `image` and `driver_data`. `snd_hwdep_dsp_load_compat()` copies index/name prefix, converts the 32-bit image pointer with `compat_ptr()`, copies length and driver data, and calls `snd_hwdep_dsp_load()`. `snd_hwdep_ioctl_compat()` dispatches native-compatible ioctls through `snd_hwdep_ioctl()` and handles `SNDRV_HWDEP_IOCTL_DSP_LOAD32`; unknown commands go to `hw->ops.ioctl_compat` or return `-ENOIOCTLCMD`.

## Control Flow and State
The file has no state of its own. It operates on the open file's `struct snd_hwdep` and preserves the same `dsp_loaded` behavior implemented by the native helper.

## Dependencies and Integration Points
It depends on `linux/compat.h`, the native hwdep ioctl implementation, and driver optional compat callbacks. Because it is textually included, it can call static `snd_hwdep_dsp_load()`.

## Risks and Test Signals
Risks are pointer truncation/extension mistakes, struct layout drift, and inconsistent unknown-command behavior versus native. Tests should run 32-bit userspace DSP status/load ioctls, verify pointer conversion, duplicate load behavior, and fallback to driver `ioctl_compat`.
