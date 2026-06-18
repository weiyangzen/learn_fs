## sources/distributed-fs/ceph-client/drivers/mtd/chips/gen_probe.c

Purpose: common probing layer for CFI-like NOR probes. It tries bus/interleave/device-width permutations, identifies all non-aliased chips in a map, then dispatches to the command-set driver advertised by the populated CFI/Jedec identification data.

Important APIs, types, and functions: `mtd_do_chip_probe()` is exported and called by `cfi_probe.c` and `jedec_probe.c`. `genprobe_ident_chips()` builds the final `cfi_private` and `flchip` array. `genprobe_new_chip()` iterates interleave and device type. `check_cmd_set()` selects built-in command sets or `cfi_cmdset_unknown()` to request `cfi_cmdset_%04X`.

Control flow: the first chip must probe at offset zero. Its CFI/Jedec `DevSize` plus interleave determine `chipshift`, which bounds the chip bitmap. The helper probes each possible chip slot, copies valid slot starts into the allocated `cfi_private`, and initializes each chip as `FL_READY`. It then tries the primary command set, then the alternate command set, and trims MTD visibility to the map size if needed.

State and persistence: allocates the persistent `cfi_private`, `cfi_ident`, chip array, mutexes, and wait queues used by command-set drivers. Temporary state includes stack `cfi_private` and chip bitmap.

Dependencies and integration points: bridges probe-specific `struct chip_probe` callbacks to command-set modules `cfi_cmdset_0001`, `0002`, and `0020`. It depends on module symbol lookup for command sets that are not directly configured.

Risks: first-chip geometry controls all later probing, so a bad table or false match mis-sizes the whole map. Missing command-set support leaves allocated CFI data to be freed here. Symbol/module lookup is string-based for unknown command sets.

Test signals: correct detection across bank widths and interleave values, alias rejection from probe callbacks, proper fallback to alternate command set, module autoload of command-set drivers, and clean failure when no command set supports a detected chip.
