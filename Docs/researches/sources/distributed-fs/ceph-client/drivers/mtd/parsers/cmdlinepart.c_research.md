# sources/distributed-fs/ceph-client/drivers/mtd/parsers/cmdlinepart.c

Purpose: command-line MTD partition parser for `mtdparts=` syntax. It converts boot/module parameters into `struct mtd_partition` arrays matched by MTD device name.

Important APIs/types/functions: `mtdpart_setup()` stores the raw command-line string via `__setup("mtdparts=", ...)`. `mtdpart_setup_real()` parses one or more MTD definitions. `newpart()` recursively parses comma-separated partition definitions and performs one combined allocation for partition structs, names, and the per-MTD descriptor. `parse_cmdline_partitions()` resolves offsets/sizes for a concrete `mtd_info` and returns a duplicated partition array. Module parameter `mtdparts` allows runtime module input.

Control flow: parsing is lazy; the first `parse_cmdline_partitions()` call parses the saved string into a global linked list. `newpart()` handles `-` remaining-size partitions, optional `@offset`, optional `(name)`, and flags `ro`, `lk`, and `slc`. During device matching, continuous offsets are calculated, remaining sizes are expanded, oversized partitions are truncated at flash end, and zero-sized partitions are removed by `memmove()`.

State and persistence: parser state is global and lasts for module lifetime: `partitions`, `cmdline`, and `cmdline_parsed`. The returned partitions are `kmemdup()` copies so later size mutation of the global template does not directly share with MTD core callers, though the template itself is updated during resolution. It does not touch flash.

Dependencies and integration: uses `memparse()`, MTD parser registration, MTD flags, and kernel/module parameter infrastructure. Risks include recursive parsing depth, global mutable parse state, syntax ambiguity around colons in names, and accepting overlapping/out-of-order partitions by design. Test signals include complex names containing colons, fill-up partition rejection when followed by more entries, truncation at device size, zero-size removal, all flag combinations, module parameter versus boot parameter, and multiple MTD IDs.
