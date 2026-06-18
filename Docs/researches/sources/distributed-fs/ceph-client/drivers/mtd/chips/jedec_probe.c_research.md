## sources/distributed-fs/ceph-client/drivers/mtd/chips/jedec_probe.c

Purpose: probes legacy JEDEC/autoselect NOR flash chips that do not provide usable CFI tables. It contains a static manufacturer/device table and synthesizes CFI-like geometry so generic command-set drivers can operate the chips.

Important APIs, types, and functions: `jedec_table[]` describes name, manufacturer ID, device ID, size, erase regions, command set, supported device widths, and unlock-address variant. `jedec_probe_chip()` is the probe callback. `jedec_match()` validates IDs, size fit, device width, unlock addresses, and ID disappearance after reset. `cfi_jedec_setup()` allocates and fills synthetic `struct cfi_ident`. `jedec_reset()`, `jedec_read_mfr()`, and `jedec_read_id()` drive autoselect access.

Control flow: generic probe calls the JEDEC callback across geometry permutations. For the first chip, the callback iterates unlock-address variants, enters autoselect, reads IDs, scans the table, and sets up synthetic CFI data on a match. Later chips must match the same mfr/id and are checked against previous chip locations for aliases. Each successful probe resets the device back to read mode.

State and persistence: persistent output is the synthetic `cfi_private` fields: command set, `DevSize`, erase-region table, manufacturer/id, `addr_unlock1/2`, and `CFI_MODE_JEDEC`. The huge table is static read-only device knowledge.

Dependencies and integration points: uses `mtd_do_chip_probe()`, CFI command/address helpers, and chip-driver registration as `jedec_probe`. It hands AMD/Intel/SST-page-style command-set IDs to the same command-set dispatch used by real CFI probes.

Risks: legacy ID probing is inherently ambiguous when flash data resembles IDs or when parts have width-specific IDs not in the table. Unlock-address guessing can issue command sequences to the wrong offsets. The table must be maintained carefully for region order and boot-block variants.

Test signals: known JEDEC chips detected with correct size and erase map, 8-bit versus 16-bit rejection for incompatible entries, alias rejection on mirrored maps, reset returning the array to read mode, and correct command-set handoff for AMD, Intel, SST, and FWH-like devices.
