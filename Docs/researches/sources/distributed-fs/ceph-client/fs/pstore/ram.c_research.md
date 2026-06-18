# sources/distributed-fs/ceph-client/fs/pstore/ram.c

## Purpose
`ram.c` implements the `ramoops` pstore backend, carving reserved RAM into persistent dmesg, console, pmsg, and ftrace zones.

## Important APIs, types, and functions
Core state is `struct ramoops_context`, with arrays of `persistent_ram_zone` pointers, sizes, counters, ECC config, and embedded `pstore_info`. Important functions include `ramoops_probe`, `ramoops_pstore_read`, `ramoops_pstore_write`, `ramoops_pstore_write_user`, `ramoops_pstore_erase`, `ramoops_init_przs`, `ramoops_init_prz`, `ramoops_parse_dt`, and dummy module-parameter platform-device setup.

## Control flow
Probe parses platform data or device tree, rounds zone sizes down to powers of two, allocates dmesg/console/pmsg/ftrace PRZs in order, allocates the dmesg scratch buffer, sets pstore frontend flags, and registers with pstore. Reads enumerate old dmesg zones first, then console, pmsg, and ftrace. Writes route by record type; dmesg takes only part 1, zaps the target zone, writes a ramoops header, and advances the circular write counter.

## State and persistence
Persistent state is a reserved physical memory region with PRZ headers, circular data, optional ECC, and old-log snapshots saved after boot. Runtime counters track read/write positions and per-CPU ftrace merging.

## Dependencies and integration points
It depends on platform devices, reserved memory/device tree bindings, pstore core, `ram_core.c`, ECC configuration, module parameters, and optional pmsg/ftrace/console frontends.

## Risks and test signals
Risks include overlapping or undersized memory regions, old invalid headers, power-of-two truncation surprises, per-CPU ftrace allocation failure, ECC metadata sizing, and pmsg calling the wrong write path. Test signals include DT and module-param boot, all zone types, dmesg header parsing, erase/unlink, ECC correction notices, per-CPU ftrace merge, and reboot recovery.
