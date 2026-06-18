# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/libie/Kconfig

## Purpose
`libie/Kconfig` defines Intel Ethernet common-library symbols layered above `libeth`, plus optional admin queue and firmware logging support.

## Important APIs, Types, and Symbols
`CONFIG_LIBIE` is a tristate that selects `LIBETH`. `CONFIG_LIBIE_ADMINQ` provides admin queue helper functions. `CONFIG_LIBIE_FWLOG` selects `LIBIE_ADMINQ` and enables firmware logging support with debugfs configuration and admin queue communication.

## Control Flow
There is no runtime flow. Kconfig symbol selection controls which modules and exported namespaces are built.

## State and Persistence Behavior
No runtime state. Build configuration determines module presence.

## Dependencies and Integration Points
`LIBIE` builds on `LIBETH`; `LIBIE_FWLOG` depends on admin queue helper availability. Intel Ethernet drivers can select these symbols for packet type tables, admin queue error strings, and firmware log debugfs support.

## Risks and Edge Cases
Because these are non-prompt tristates, consumer drivers must select the correct symbols. Missing `LIBIE_ADMINQ` for fwlog would break admin queue string/helper dependencies, so `LIBIE_FWLOG` selects it explicitly.

## Test Signals
Kconfig dependency validation and modular builds for `LIBIE`, `LIBIE_ADMINQ`, and `LIBIE_FWLOG` independently and as selected by consumer drivers.
