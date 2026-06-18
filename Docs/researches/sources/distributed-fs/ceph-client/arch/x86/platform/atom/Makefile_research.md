<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/atom/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/atom/Makefile

## Purpose
This Makefile selects the Intel Atom Punit debug driver when configured.

## Important APIs, types, and functions
It contains a single Kbuild rule: `obj-$(CONFIG_PUNIT_ATOM_DEBUG) += punit_atom_debug.o`.

## Control flow
There is no runtime control flow. At build time, the object is compiled into the kernel or module set only when `CONFIG_PUNIT_ATOM_DEBUG` is enabled.

## State and persistence behavior
No runtime state. The only persistent effect is build inclusion of `punit_atom_debug.c`.

## Dependencies and integration points
It is reached from `arch/x86/platform/Makefile` and depends on Kconfig selecting `CONFIG_PUNIT_ATOM_DEBUG`.

## Risks and edge cases
If the config symbol is renamed or the object name changes, the debugfs/s2idle Atom diagnostics disappear from builds.

## Test signals
Enable and disable `CONFIG_PUNIT_ATOM_DEBUG` and confirm `punit_atom_debug.o` appears only in the enabled build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/atom/Makefile -->
