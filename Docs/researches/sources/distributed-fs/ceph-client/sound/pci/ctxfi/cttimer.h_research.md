# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cttimer.h

## Purpose

This header declares the ctxfi PCM timer manager and timer-instance lifecycle API.

## Important APIs, types, and functions

It forward declares `struct ct_timer` and `struct ct_timer_instance`, plus constructors/destructors and prepare/start/stop functions for timer instances.

## Control flow

PCM open calls `ct_timer_instance_new()`, prepare/start/stop call the matching functions, and runtime private cleanup calls `ct_timer_instance_free()`. ATC-level setup owns `ct_timer_new()` and `ct_timer_free()`.

## State and persistence behavior

The header exposes opaque timer objects; all state lives in `cttimer.c`.

## Dependencies and integration points

It depends on Linux spinlock/timer/list declarations only for surrounding type compatibility and is included by `ctpcm.c`.

## Risks and test signals

The opaque API reduces direct misuse, but callers must free instances before the global timer. PCM lifecycle tests and module unload tests catch ordering bugs.
