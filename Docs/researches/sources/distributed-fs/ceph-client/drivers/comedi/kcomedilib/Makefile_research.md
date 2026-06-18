# sources/distributed-fs/ceph-client/drivers/comedi/kcomedilib/Makefile

## Purpose
This Makefile builds the kernel COMEDI library object for in-kernel users of comedilib-like helpers.

## Important APIs, Types, And Functions
It sets `ccflags-$(CONFIG_COMEDI_DEBUG) := -DDEBUG`, adds `kcomedilib.o` when `CONFIG_COMEDI_KCOMEDILIB` is enabled, and defines `kcomedilib-objs := kcomedilib_main.o`.

## Control Flow
Kbuild evaluates the config-dependent object line and links `kcomedilib_main.o` into `kcomedilib.o` when selected.

## State And Persistence
No runtime state exists. The file controls build output only.

## Dependencies And Integration Points
It integrates with Kbuild, `CONFIG_COMEDI_DEBUG`, and `CONFIG_COMEDI_KCOMEDILIB`. The resulting object exports symbols from `kcomedilib_main.c`.

## Risks And Edge Cases
Any additional source file for the library must be added to `kcomedilib-objs`. Debug behavior depends on the global COMEDI debug config.

## Test Signals
Build signals are whether `kcomedilib.o` appears only under `CONFIG_COMEDI_KCOMEDILIB` and whether `-DDEBUG` is present only under `CONFIG_COMEDI_DEBUG`.
