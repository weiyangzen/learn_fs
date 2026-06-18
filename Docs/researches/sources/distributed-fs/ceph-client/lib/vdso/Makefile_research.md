<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/Makefile -->
# sources/distributed-fs/ceph-client/lib/vdso/Makefile

## Purpose
Build glue for the generic vDSO library directory.

## APIs, Types, and Functions
Adds `datastore.o` to `obj-y` when `CONFIG_HAVE_GENERIC_VDSO` is enabled.

## Control Flow, State, and Persistence
Declarative kbuild only. It does not build `gettimeofday.c` or `getrandom.c` directly here because those are included or built through architecture vDSO build rules.

## Dependencies and Integration
Depends on kbuild and `CONFIG_HAVE_GENERIC_VDSO`. Integrates with architecture-specific vDSO makefiles that pull generic sources as needed.

## Risks and Test Signals
Risks include assuming all generic vDSO files are built from this makefile, or missing `datastore.o` when an architecture selects generic vDSO. Test signals are per-architecture build logs and symbol presence for generic vvar datastore support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vdso/Makefile -->
