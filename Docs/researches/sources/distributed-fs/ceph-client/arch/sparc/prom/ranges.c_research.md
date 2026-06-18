# sources/distributed-fs/ceph-client/arch/sparc/prom/ranges.c

Purpose: applies SPARC32 OpenPROM `ranges` translations to device register addresses, especially OBIO and nested bus ranges.

Important APIs/functions: exports `prom_apply_obio_ranges()` and `prom_apply_generic_ranges()`. Initialization entry is `prom_ranges_init()`. Internal helpers are `prom_adjust_regs()` and `prom_adjust_ranges()`.

Control flow: `prom_ranges_init()` finds the root `obio` node and caches its ranges. `prom_apply_obio_ranges()` translates register tuples through cached OBIO ranges. `prom_apply_generic_ranges()` reads a node's ranges, optionally composes them with parent ranges, and adjusts each register's bus space and physical address.

State and persistence: caches OBIO ranges and count in static arrays for boot lifetime.

Dependencies and integration points: called by SPARC32 PROM init and device probing code that consumes PROM `reg` properties for SBUS/OBIO devices.

Risks: range matching lacks hard failure after warning, so malformed firmware ranges can still index unexpected entries. Arithmetic overflow or wrong parent composition maps devices to incorrect physical addresses.

Test signals: probe OBIO/SBUS devices with simple and nested ranges, missing ranges, malformed ranges, and verify translated resource addresses match firmware expectations.
