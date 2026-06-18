# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_procfs.c

## Purpose

This file implements `/proc/fb`, listing registered framebuffer numbers and fixed IDs when legacy fbdev device support is enabled. The complete 62-line source was read.

## Important APIs, Types, and Functions

Important functions are `fb_seq_start()`, `fb_seq_stop()`, `fb_seq_next()`, `fb_seq_show()`, `fb_init_procfs()`, and `fb_cleanup_procfs()`. Static state is `fb_proc_dir_entry`.

## Control Flow

Initialization creates a seq_file proc entry named `fb`. Seq iteration locks `registration_lock`, walks positions from 0 to `FB_MAX - 1`, and prints `<node> <fix.id>` for non-NULL `registered_fb[i]`. Cleanup removes the proc entry.

## State and Persistence Behavior

The proc entry is in-memory virtual filesystem state. Output reflects the live `registered_fb[]` array and has no persistence.

## Dependencies and Integration Points

It depends on procfs seq APIs and fbdev registration globals from `fb_internal.h`. It is part of the legacy userspace interface controlled by `CONFIG_FB_DEVICE`.

## Risks and Edge Cases

The seq iterator holds `registration_lock` across iteration, so long reads serialize framebuffer registration changes. Missing or failed proc creation returns `-ENOMEM` to core init. Output depends on drivers setting meaningful `fix.id`.

## Test Signals

Test proc creation/removal, empty output with no framebuffers, multiple registered framebuffers, concurrent register/unregister while reading, and `fix.id` formatting.
