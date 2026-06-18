# sources/distributed-fs/ceph-client/scripts/kconfig/mconf-cfg.sh

## Purpose

`mconf-cfg.sh` is the build-time probe for the `menuconfig` ncurses frontend. It discovers usable ncurses compiler and linker flags and writes them to caller-provided files.

## Important APIs, Types, and Functions

The script accepts output files `cflags` and `libs`. It probes `HOSTPKG_CONFIG` packages `ncursesw` then `ncurses`, checks default include directories `/usr/include/ncursesw` and `/usr/include/ncurses`, and finally asks `${HOSTCC} -E` whether `<ncurses.h>` is available.

## Control Flow

With `set -eu`, it first prefers pkg-config if available, then filesystem fallbacks, then a compiler preprocessor fallback. On success it writes flags and exits 0. On failure it prints package-install guidance and exits 1.

## State and Persistence Behavior

It creates or overwrites only the generated cflags/libs files passed by the build. It does not write source or user configuration files.

## Dependencies and Integration Points

It is invoked by the kconfig Makefile before building `mconf`. It depends on `HOSTPKG_CONFIG` when available and `HOSTCC` for the final fallback.

## Risks and Edge Cases

`set -u` makes unset `HOSTPKG_CONFIG` or `HOSTCC` hazardous depending on the path taken. Library detection is intentionally simple and may miss sysroot or nonstandard installs if neither pkg-config nor `HOSTCC` exposes them. The fallback links plain `-lncurses`, not menu/panel libraries, because `mconf` uses only base ncurses.

## Test Signals

Test with ncursesw pkg-config, ncurses pkg-config, no pkg-config but standard headers, sysroot compiler fallback, and complete absence of ncurses.
