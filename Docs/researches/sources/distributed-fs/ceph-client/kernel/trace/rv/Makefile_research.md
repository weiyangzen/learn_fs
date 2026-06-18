# sources/distributed-fs/ceph-client/kernel/trace/rv/Makefile

## Purpose
`kernel/trace/rv/Makefile` maps Runtime Verification Kconfig symbols to compiled objects and adds the local include path needed for RV trace event headers.

## Important APIs, types, and functions
The main build directives are `ccflags-y += -I $(src)`, `obj-$(CONFIG_RV) += rv.o`, one `obj-$(CONFIG_RV_MON_*)` entry per monitor, and reactor object entries for `rv_reactors.o`, `reactor_printk.o`, and `reactor_panic.o`.

## Control flow
Kbuild evaluates each `obj-$(CONFIG_...)` assignment and includes only objects whose config symbol is enabled. Monitor objects are organized under `monitors/<name>/<name>.o`, matching the Kconfig source structure.

## State and persistence
The file has no runtime state. It encodes build-time persistence by determining which RV objects are part of the kernel or module build.

## Dependencies and integration points
It depends on Kconfig symbols defined in `rv/Kconfig` and monitor-specific Kconfig files. The include flag integrates generated/local trace event headers with monitor compilation.

## Risks and test signals
Risks include Kconfig/Makefile symbol mismatches, forgotten object entries for new monitors, stale entries for removed monitors, and missing include path breaking event headers. Test signals are all RV monitor config combinations building cleanly and generated monitor additions updating both Kconfig and Makefile insertion points.
