# sources/distributed-fs/ceph-client/scripts/kconfig/gconf-cfg.sh

## Purpose

`gconf-cfg.sh` is a build-time probe for the GTK frontend. It verifies that host `pkg-config` is available and that GTK+ 3 development files can be found, then writes compiler and linker flags to files provided by the caller.

## Important APIs, Types, and Functions

The script is linear shell code with inputs `cflags=$1` and `libs=$2`. It uses `HOSTPKG_CONFIG`, package name `gtk+-3.0`, `command -v`, `pkg-config --exists`, `pkg-config --cflags`, and `pkg-config --libs`.

## Control Flow

With `set -eu`, missing variables or failed commands abort. The script first checks for `${HOSTPKG_CONFIG}` in `PATH`, prints a user-facing diagnostic and exits on absence, then checks for GTK+ 3. If found, it writes cflags and libs to the requested output files.

## State and Persistence Behavior

It persists only two generated build fragments: the host compiler flags file and host libraries file. It does not mutate repository sources.

## Dependencies and Integration Points

It is invoked by the kconfig Makefile when building `gconfig`. It depends on host GTK+ 3 development packages and the build-system-provided `HOSTPKG_CONFIG` variable.

## Risks and Edge Cases

Because `set -u` is active, an unset `HOSTPKG_CONFIG` fails before the friendly diagnostic. The script has no fallback include/library probing, unlike the ncurses cfg scripts, so environments without pkg-config cannot build `gconfig` even if GTK headers are manually available.

## Test Signals

Test with valid GTK/pkg-config, missing pkg-config, missing GTK package, and output paths in generated build directories. Build-level signal is successful compilation/linking of `gconf`.
