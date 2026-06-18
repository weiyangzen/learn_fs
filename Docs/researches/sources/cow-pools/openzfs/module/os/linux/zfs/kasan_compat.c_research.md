# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/kasan_compat.c

## Purpose

Provides a compatibility workaround for kernels where `kasan_enabled()` depends on a GPL-only symbol.

## Behavior

When `HAVE_KASAN_ENABLED_GPL_ONLY` is defined, the file defines:

- `struct static_key_false kasan_flag_enabled = STATIC_KEY_FALSE_INIT;`

This satisfies references from header-based kernel code without linking against the GPL-only kernel symbol.

## Notes

The workaround effectively makes OpenZFS code see KASAN as disabled for the affected symbol path, avoiding build/link failures caused by inaccessible kernel internals.
