# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/module.mk.in

## Purpose

`module.mk.in` is the OrangeFS build-system fragment for the ZOID BMI method. It conditionally adds the ZOID BMI sources to the relevant library/server source lists only when configure sets `BUILD_ZOID`.

## Important APIs, variables, and targets

- `ifneq (,$(BUILD_ZOID))` gates all content behind configure-time ZOID support.
- `DIR := src/io/bmi/bmi_zoid` defines the source directory used in top-level source lists.
- `cfiles := zoid.c server.c zbmi_pool.c` lists the C files compiled for this module.
- `src := $(patsubst %,$(DIR)/%,$(cfiles))` expands the source paths.
- `LIBSRC += $(src)`, `SERVERSRC += $(src)`, and `LIBBMISRC += $(src)` register the same sources for the broader OrangeFS build categories.
- `MODCFLAGS_$(DIR)` adds include paths for ZOID headers and the ZBMI implementation under `@ZOID_SRCDIR@`.

## Control flow

The make fragment is declarative. If `BUILD_ZOID` is empty, the build ignores this module entirely. If it is non-empty, the three source files are added to OrangeFS build lists, and directory-specific compiler flags are set to find ZOID/ZBMI headers.

## State and persistence behavior

There is no runtime state. The persistent behavior is build configuration state produced by `configure`: `BUILD_ZOID` and `@ZOID_SRCDIR@` determine whether this module compiles and where it finds external ZOID headers.

## Dependencies and integration points

This file integrates with OrangeFS's generated make infrastructure and depends on configure substituting `@ZOID_SRCDIR@`. It deliberately omits `dlmalloc.c` because `zbmi_pool.c` includes that source file directly after setting allocator configuration macros. It also depends on external ZOID headers in `include`, `zbmi`, and `zbmi/implementation`.

## Risks and edge cases

- Because `dlmalloc.c` is included from `zbmi_pool.c`, tools that look only at make source lists may miss the allocator implementation.
- The same source set is added to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`; changes to these files can affect both library and server build surfaces.
- If `@ZOID_SRCDIR@` is wrong or stale, compile failures will appear as missing ZOID/ZBMI headers rather than local source errors.
- If `BUILD_ZOID` is accidentally set in an environment without compatible ZOID libraries, the build may progress to later link failures.

## Test signals

Regenerate or run configure with ZOID enabled and disabled. With `BUILD_ZOID` enabled, verify that `zoid.c`, `server.c`, and `zbmi_pool.c` compile with the substituted include paths and that no separate `dlmalloc.c` object is expected. With `BUILD_ZOID` disabled, verify the build excludes this module cleanly.
