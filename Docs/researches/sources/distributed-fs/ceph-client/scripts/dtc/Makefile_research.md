# sources/distributed-fs/ceph-client/scripts/dtc/Makefile

## Purpose
This Makefile wires the device tree compiler host tools into the Linux build, producing `dtc` when `CONFIG_DTC` or `CHECK_DTBS` requires it and `fdtoverlay` when `CONFIG_DTC` is enabled.

## Important APIs, Types, and Functions
It defines `hostprogs-always-*` entries, `dtc-objs`, `libfdt-objs`, `libfdt`, and `fdtoverlay-objs`. `HOST_EXTRACFLAGS` adds the userspace libfdt include path and defines `NO_YAML`. Generated lexer/parser object flags add the source tree include path. The lexer object explicitly depends on the parser-generated header.

## Control Flow and State
There is no runtime control flow. Kbuild expands object lists and host flags to build generated and static C sources into host utilities.

## Dependencies and Integration
It depends on Kbuild host program rules, flex/bison outputs, libfdt sources under `scripts/dtc/libfdt`, and the Linux config variables controlling DTC.

## Risks and Test Signals
Object lists must stay synchronized with source files and `.gitignore`. `NO_YAML` removes YAML output support from this kernel build. Test host builds with `CONFIG_DTC=y`, `CHECK_DTBS=y`, generated lexer/parser ordering, and fdtoverlay link coverage.
