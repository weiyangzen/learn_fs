# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_local.h

## Purpose

`ac97_local.h` declares private cross-file helpers for the ALSA AC97 codec module, primarily shared between `ac97_codec.c` and optional procfs support.

## Important APIs, Types, and Functions

It declares `snd_ac97_get_name()` and `snd_ac97_update_bits_nolock()` for internal codec use. Under `CONFIG_SND_PROC_FS`, it declares bus and codec proc init/done helpers: `snd_ac97_bus_proc_init()`, `snd_ac97_bus_proc_done()`, `snd_ac97_proc_init()`, and `snd_ac97_proc_done()`. Without procfs, those helpers become no-op macros.

## Control Flow

There is no runtime control flow in the header. Its conditional declarations decide whether `ac97_codec.c` calls real procfs helpers or compiles calls away.

## State and Persistence

The header stores no state. Procfs helper implementations, when enabled, manage diagnostic entries outside this file.

## Dependencies and Integration Points

It depends on public AC97 types being visible before inclusion. It integrates `ac97_codec.c`, `ac97_proc.c`, and the `CONFIG_SND_PROC_FS` object selection in `sound/pci/ac97/Makefile`.

## Risks and Edge Cases

The no-op macros must match the call signatures of the real helpers. `snd_ac97_update_bits_nolock()` is explicitly lockless and assumes callers already hold `reg_mutex` or otherwise serialize register/cache access. Misuse can corrupt the AC97 register cache.

## Test Signals

Build AC97 with `CONFIG_SND_PROC_FS=y` and `n`, and run lockdep-oriented tests around control writes that call the nolock update helper through already-locked paths.
