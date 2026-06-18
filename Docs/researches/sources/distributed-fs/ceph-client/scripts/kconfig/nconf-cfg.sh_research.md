# sources/distributed-fs/ceph-client/scripts/kconfig/nconf-cfg.sh

## Purpose

`nconf-cfg.sh` is the build-time probe for the `nconfig` frontend. It discovers ncurses menu, panel, and curses libraries and writes host compiler/linker flags for the build.

## Important APIs, Types, and Functions

The script accepts `cflags=$1` and `libs=$2`. It probes pkg-config packages `menuw panelw ncursesw`, then `menu panel ncurses`, then standard include directories for wide and non-wide ncurses, and finally `/usr/include/ncurses.h`.

## Control Flow

With `set -eu`, the script prefers pkg-config and preserves library order for static linking. If pkg-config cannot find packages, it writes fallback include and library flags based on header locations. On failure it prints install guidance and exits 1.

## State and Persistence Behavior

It writes only generated cflags/libs files supplied by the caller and does not touch configs or source files.

## Dependencies and Integration Points

It is invoked by the kconfig Makefile for `nconfig`. It depends on `HOSTPKG_CONFIG` if available and ncurses menu/panel development libraries.

## Risks and Edge Cases

`set -u` means unset build variables can abort. Unlike `mconf-cfg.sh`, there is no compiler-preprocessor fallback. Nonstandard sysroots require pkg-config or matching standard header paths. Static link order is intentionally encoded and should not be reordered casually.

## Test Signals

Test pkg-config wide and non-wide library paths, standard include fallback paths, static host compiler linking, missing package diagnostics, and successful `nconfig` build/link.
