# sources/distributed-fs/ceph-client/arch/mips/kernel/prom.c

## Purpose
Provides generic MIPS device-tree/platform discovery helpers: machine name storage, early DT setup, DT bus population, and weak default device-tree unflattening.

## Important APIs, Types, and Functions
- `mips_set_machine_name()` stores a bounded machine name, logs it, and updates the dump-stack architecture description.
- `mips_get_machine_name()` returns the stored name.
- `__dt_setup_arch()` scans the flat DT and derives the machine name.
- `__dt_register_buses()` builds an OF match table for up to two bus compatibles and calls `of_platform_populate()`.
- `device_tree_init()` is a weak default that calls `unflatten_and_copy_device_tree()`.

## Control Flow
Platform setup may call `__dt_setup_arch()` with a boot parameter header. If `early_init_dt_scan()` succeeds, the flat DT machine name becomes the MIPS machine name. Later `__dt_register_buses()` requires a populated DT and turns selected buses into platform devices, panicking on missing DT or population failure.

## State and Persistence
The only persistent runtime state is the static `mips_machine_name[64]`, initialized to `"Unknown"`. DT nodes are copied/unflattened into normal kernel DT storage.

## Dependencies and Integration Points
Integrates with OF/flat-tree boot code, memblock-reserved DT handling in setup, debug/dump-stack descriptions, and proc cpuinfo machine-name reporting.

## Risks
Bus compatible strings are copied into a static local match table, so callers must fit OF compatible sizes. `__dt_register_buses()` panics instead of returning recoverable errors, appropriate for early platform bring-up but high impact. Machine names longer than 63 bytes are truncated.

## Test Signals
Boot with a DT should log `MIPS: machine is ...`, `/proc/cpuinfo` should show the same machine, and platform devices under the registered buses should appear. Missing DT for DT-only platforms should panic early and clearly.
