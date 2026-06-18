# sources/distributed-fs/ceph-client/tools/iio/Makefile

## Purpose

This Makefile builds and installs the user-space Industrial I/O example tools: `iio_event_monitor`, `lsiio`, and `iio_generic_buffer`.

## Important Targets and Variables

It imports `../scripts/Makefile.include`, derives `srctree` when unset, disables built-in rules with `MAKEFLAGS += -r`, and augments `CFLAGS` with optimization, warnings, debug info, `_GNU_SOURCE`, and `-I$(OUTPUT)include`. `prepare` creates `$(OUTPUT)include/linux/iio` and symlinks UAPI headers `buffer.h`, `events.h`, and `types.h`. Each program has an intermediate `*-in.o` target built through `tools/build`, then a final link step with `$(CC)`. `clean` removes binaries, generated include symlinks, objects, dependency files, and command files. `install` copies programs into `$(DESTDIR)$(bindir)`.

## State, Dependencies, and Integration

Build outputs live under `$(OUTPUT)`, enabling out-of-tree builds. The Makefile depends on the kernel tools build system and UAPI IIO headers. It integrates the shared `iio_utils` object into all three tools.

## Risks and Test Signals

The symlink preparation assumes kernel source-relative paths and may fail outside the expected tree. `clean` uses `find $(or $(OUTPUT),.)`, so an unexpected empty or broad `OUTPUT` value deserves caution. Tests are `make -C tools/iio`, out-of-tree `O=` or `OUTPUT=` builds, `make clean`, and staged `make install DESTDIR=...`.
