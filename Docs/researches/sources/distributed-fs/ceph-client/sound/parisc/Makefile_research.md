# sources/distributed-fs/ceph-client/sound/parisc/Makefile

## Purpose

This Makefile wires the PA-RISC ALSA Harmony driver into kbuild.

## Important APIs, Types, and Functions

It defines `snd-harmony-y := harmony.o` and adds `snd-harmony.o` to `obj-$(CONFIG_SND_HARMONY)`.

## Control Flow

When `CONFIG_SND_HARMONY=y`, `harmony.o` is linked into the built-in sound object graph as `snd-harmony.o`. When set to `m`, kbuild emits `snd-harmony.ko`. When disabled, nothing from this directory is built.

## State and Persistence

The file has no runtime state. It affects object composition and module naming.

## Dependencies and Integration Points

It depends on `sound/parisc/Kconfig` for the `CONFIG_SND_HARMONY` symbol and on `harmony.c` as the only object in the module.

## Risks and Edge Cases

The module is single-object, so adding companion files later requires updating `snd-harmony-y`. A mismatched Kconfig symbol would silently omit the driver, but the current symbol matches.

## Test Signals

Kbuild with `CONFIG_SND_HARMONY=y` and `m`, and `make M=sound/parisc` style builds when supported by the tree.
