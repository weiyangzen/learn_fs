# sources/distributed-fs/ceph-client/sound/core/pcm_compat.c

## Purpose

`pcm_compat.c` is included by `pcm_native.c` to implement 32-bit and x32 compatibility wrappers for ALSA PCM ioctls on 64-bit kernels. It translates structure layouts, pointer arrays, frame counters, mmap sync records, status records, and boundary values between compat userspace and native kernel PCM APIs.

## Important APIs, Types, and Functions

Important wrappers include `snd_pcm_ioctl_hw_params_compat()`, `snd_pcm_ioctl_sw_params_compat()`, `snd_pcm_ioctl_channel_info_compat()`, `snd_pcm_status_user_compat64()`, `snd_pcm_ioctl_xferi_compat()`, `snd_pcm_ioctl_xfern_compat()`, `snd_pcm_ioctl_sync_ptr_x32()`, `snd_pcm_ioctl_sync_ptr_buggy()`, and the main dispatcher `snd_pcm_ioctl_compat()`. Compat structs mirror 32-bit versions of hw/sw params, channel info, transfer descriptors, x32 mmap sync records, and historical buggy sync layouts.

## Control Flow

The dispatcher retrieves `struct snd_pcm_file`, disables compat mmap of old status/control records, then either forwards layout-compatible commands to `snd_pcm_common_ioctl()` or handles translated commands locally. HW refine/params copies a 32-bit params block into a native object, calls native refine/params, copies results back, and recalculates runtime boundary after real params. Transfer wrappers read compat user pointers, call native `snd_pcm_lib_read/write` or vector variants, then write the result field back.

## State and Persistence Behavior

Most functions are translation-only. Persistent effects are native PCM effects: hardware/software parameter changes, appl pointer updates, DMA sync, rewind/forward, stream state changes, and `pcm_file->no_compat_mmap = 1`. Boundary recalculation updates `runtime->boundary` after compat HW params.

## Dependencies and Integration Points

The file depends on Linux compat helpers, native PCM APIs from `pcm_native.c`, runtime mmap status/control structures, stream locks, DMA buffer sync, and x86 x32 ABI conditionals. It is not a standalone compilation unit; it is included into the native PCM implementation.

## Risks and Edge Cases

Layout mistakes are ABI regressions. Pointer-array transfer copies up to 128 channel pointers and rejects larger channel counts. Sync pointer handling includes a compatibility path for a historical 32-bit layout bug, and x32 has a distinct structure despite running on 64-bit kernels. Boundary conversion must keep 32-bit userspace ring pointers coherent with native wider boundaries.

## Test Signals

Run 32-bit ALSA PCM applications on a 64-bit kernel, including hw refine/params, sw params, mmap sync, status ext, interleaved and noninterleaved transfers, rewind/forward/delay, x32-specific tests where available, and regression tests for old libasound sync-pointer behavior.
