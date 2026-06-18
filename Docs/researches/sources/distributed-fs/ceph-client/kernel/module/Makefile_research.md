# sources/distributed-fs/ceph-client/kernel/module/Makefile

## Purpose
Selects the object files that implement the kernel module subsystem for the active configuration.

## Important APIs, Types, And Functions
This Kbuild file always builds `main.o`, `strict_rwx.o`, and `kmod.o`. Optional objects include `dups.o`, `decompress.o`, `signing.o`, `livepatch.o`, `tree_lookup.o`, `debug_kmemleak.o`, `kallsyms.o`, `procfs.o`, `sysfs.o`, `kdb.o`, `version.o`, `tracking.o`, and `stats.o`. It also disables KCOV instrumentation for `main.o`.

## Control Flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_...)` assignments and links only the enabled support files into the kernel. The object selection mirrors the Kconfig feature matrix.

## State And Persistence
No runtime state is stored here. It persists build graph decisions and instrumentation policy.

## Dependencies And Integration Points
Integrates module Kconfig symbols with the kernel build. `KCOV_INSTRUMENT_main.o := n` prevents noisy or unsafe coverage from hot module loader paths called by SLUB stack tracing.

## Risks And Edge Cases
Missing an object breaks references declared in `internal.h`; adding an object without the right Kconfig guard can create dead code or unresolved symbols. Instrumenting `main.o` could produce excessive or misleading coverage.

## Test Signals
Build coverage across module configurations is the primary signal, especially combinations of `CONFIG_MODULES`, `CONFIG_SYSFS`, `CONFIG_KALLSYMS`, `CONFIG_MODULE_SIG`, `CONFIG_MODULE_DECOMPRESS`, and `CONFIG_MODULE_UNLOAD`.
