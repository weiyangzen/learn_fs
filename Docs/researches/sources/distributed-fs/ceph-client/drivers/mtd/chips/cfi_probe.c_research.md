## sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_probe.c

Purpose: implements the CFI-specific chip probe used by the generic NOR probe framework. It enters CFI query mode, confirms the `QRY` signature, reads the CFI identification table, discovers manufacturer/device IDs, applies early fixups, and registers the `cfi_probe` chip driver.

Important APIs, types, and functions: `cfi_probe()` delegates to `mtd_do_chip_probe()`. `cfi_probe_chip()` validates a candidate base address, enters query mode, handles alias detection, and records additional chips. `cfi_chip_setup()` allocates and fills `struct cfi_ident`, byteswaps CFI fields, reads autoselect manufacturer/id values, and applies `cfi_early_fixup_table`. `fixup_s70gl02gs_chips()` corrects bad Spansion/S70GL02GS geometry before generic chip enumeration relies on it.

Control flow: generic probing calls `cfi_probe_chip()` for geometry permutations and map offsets. The first successful base triggers `cfi_chip_setup()`, which reads erase-region count and the variable-length CFI table while in query mode, then exits query mode before autoselect. Later bases are compared with earlier chip locations to reject aliases before marking new chip bits.

State and persistence: the file populates `cfi_private` fields: `cfiq`, `cfi_mode`, `sector_erase_cmd`, `mfr`, `id`, number of chips, interleave, and device type. No persistent storage exists beyond the CFI structures passed to command-set drivers.

Dependencies and integration points: uses `linux/mtd/xip.h` guards for execute-in-place builds, `cfi_qry_mode_on/off()`, `cfi_qry_present()`, `cfi_send_gen_cmd()`, `gen_probe.h`, and chip-driver registration in `chipreg.c`.

Risks: probing manipulates live flash modes and disables interrupts briefly under XIP. Alias detection can be fooled when actual flash contents equal CFI markers or IDs. Bad CFI tables require early fixups because `chipshift` and chip count are derived immediately after the first setup.

Test signals: detection logs with expected bank width/interleave, correct CFI table byteswapping on big/little-endian maps, no duplicate alias chips, S70GL02GS split geometry, XIP boot stability, and successful handoff to primary or alternate command-set drivers.
