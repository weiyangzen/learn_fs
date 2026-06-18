# File Research: sources/block-storage/lvm2/libdm/dm-tools/Makefile.in

## Purpose
Builds and installs device-mapper command-line tools, primarily `dmsetup`, `dmvdostats` via symlink, and optionally `dmfilemapd`.

## Main Responsibilities
- Always builds under the `device-mapper` aggregate target.
- Builds `dmsetup` from `dmsetup.o` and `dmvdostats.o`.
- Optionally includes `dmfilemapd.c` and builds `dmfilemapd` when `@BUILD_DMFILEMAPD@` is enabled.
- Supports shared and static tool variants depending on configure substitutions.
- Installs tool binaries and compatibility symlinks.

## Key Build Behavior
- Shared builds produce `dmsetup` and optionally `dmfilemapd`.
- Static builds produce `dmsetup.static` and optionally `dmfilemapd.static`.
- `dmsetup` install creates `dmstats` and `dmvdostats` symlinks.
- Static install creates `dmstats.static` and `dmvdostats.static` symlinks.
- Tool linking uses `-L$(interfacebuilddir) -ldevmapper`.

## Edge Cases and Invariants
- `install` depends on `install_device-mapper` and `install_dmfilemapd`; `install_dmfilemapd` only has concrete prerequisites when dmfilemapd support is enabled.
- `CLEAN_TARGETS` includes all possible dynamic/static tool outputs.
