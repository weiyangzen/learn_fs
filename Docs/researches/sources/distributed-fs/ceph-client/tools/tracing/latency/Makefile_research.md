# sources/distributed-fs/ceph-client/tools/tracing/latency/Makefile

## Purpose
This Makefile builds and installs the `latency-collector` tracing utility using the Linux tools build system and feature detection for `libtraceevent` and `libtracefs`.

## Important APIs, Types, and Functions
It derives `srctree`, normalizes `OUTPUT`/`O`, defines `LATENCY-COLLECTOR` and its intermediate `LATENCY-COLLECTOR_IN`, exports compiler tools, and declares feature probes in `FEATURE_TESTS`/`FEATURE_DISPLAY`. The core build target links `latency-collector-in.o` into the final binary with `$(EXTLIBS)`. The pattern rule `latency-collector.%: fixdep FORCE` and `$(LATENCY-COLLECTOR_IN): fixdep FORCE` invoke `tools/build/Makefile.build`.

## Control Flow
Normal builds include `tools/build/Makefile.include`, then feature detection and `Makefile.config` unless the requested goal is only `clean` or `install`. `all` builds the binary. `install` creates `$(DESTDIR)/usr/bin`, installs the binary mode 755, and strips it. `clean` deletes object files, command/dependency files, the binary, `fixdep`, `FEATURE-DUMP`, and feature output.

## State and Persistence
Build artifacts are written under `OUTPUT` or the current directory. Install writes to `$(DESTDIR)$(BINDIR)`; clean removes generated files from the build tree.

## Dependencies and Integration Points
It depends on GCC, LD, AR, pkg-config, the Linux tools build framework, `libtraceevent`, `libtracefs`, and local `Makefile.config`.

## Risks and Edge Cases
The Makefile forces `CC := gcc`, which may override cross-compilation expectations unless the broader tools build environment compensates. Feature probing is skipped for `install`, so installing without a prior successful build can fail late. Clean uses `find .`, which targets the current latency directory, not a separate output tree when `O=` points elsewhere.

## Test Signals
Build with and without `O=`, missing `libtracefs`, and staged `DESTDIR`. Verify `clean` removes generated local artifacts and that feature failures are reported during normal build goals.
