# sources/distributed-fs/ceph-client/kernel/debug/Makefile

## Purpose
This Makefile wires the kernel debugger objects into the build. It builds the KGDB core and GDB remote stub when `CONFIG_KGDB` is enabled and descends into the KDB frontend directory when `CONFIG_KGDB_KDB` is enabled.

## Important APIs, types, and functions
There are no C APIs or runtime types. The important build variables are `obj-$(CONFIG_KGDB) += debug_core.o gdbstub.o` and `obj-$(CONFIG_KGDB_KDB) += kdb/`.

## Control flow
Kbuild evaluates the config-controlled object lists. Enabling KGDB compiles and links `debug_core.o` and `gdbstub.o`; enabling KGDB_KDB additionally includes the `kdb/` subdirectory in the build.

## State and persistence behavior
The file affects build outputs only. It does not generate source, write runtime state, or expose persistent configuration beyond compiled object inclusion.

## Dependencies and integration points
It integrates with Kconfig symbols `CONFIG_KGDB` and `CONFIG_KGDB_KDB`, and with the child KDB Makefile for frontend commands and generated KDB command data.

## Risks and edge cases
Misconfiguring this file can omit required debugger objects or include KDB without the core objects. Because `gdbstub.o` is tied to `CONFIG_KGDB`, downstream KDB/GDB transition helpers depend on this build linkage.

## Test signals
Build matrix checks should cover `CONFIG_KGDB=n`, `CONFIG_KGDB=y CONFIG_KGDB_KDB=n`, and both enabled. Link errors in KGDB symbols or missing KDB directory objects are the main signals.
