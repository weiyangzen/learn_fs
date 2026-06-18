# sources/distributed-fs/ceph-client/scripts/kconfig/qconf-cfg.sh

## Purpose
`qconf-cfg.sh` discovers Qt build flags for the graphical `xconfig` frontend and writes three output files: compiler flags, linker flags, and the Qt host binary directory.

## Important APIs, Types, and Functions
The script takes positional outputs `cflags`, `libs`, and `bin`. It uses `${HOSTPKG_CONFIG}` to query `Qt6Core Qt6Gui Qt6Widgets` first, then `Qt5Core Qt5Gui Qt5Widgets`. Qt6 receives an extra `-std=c++17` line.

## Control Flow
With `set -eu`, the script validates that `${HOSTPKG_CONFIG}` exists, checks Qt6 package availability, writes cflags/libs/libexecdir and exits on success, then falls back to Qt5 cflags/libs/host_bins. If neither Qt version is found, it prints guidance and exits 1.

## State and Persistence
The only persistent state is the three generated files specified by arguments. It does not mutate repository source files directly.

## Dependencies and Integration Points
Called by Kbuild while building `scripts/kconfig/qconf`. It depends on host `pkg-config` or a compatible tool named by `HOSTPKG_CONFIG`, and on Qt development metadata.

## Risks and Edge Cases
`${HOSTPKG_CONFIG}` is expanded unquoted in several command positions, which is conventional for build variables but sensitive to spaces. The script assumes it is invoked with all three output paths. Qt6 and Qt5 package names must match distribution pkg-config metadata.

## Test Signals
Test by running under environments with Qt6, Qt5-only, missing pkg-config, and missing Qt packages. Kbuild `make xconfig` is the integration signal.
