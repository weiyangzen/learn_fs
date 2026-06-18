# File Research: sources/block-storage/lvm2/lib/format_text/flags.c

This file converts LVM status bitmasks to and from text metadata flag arrays. It defines static flag tables for VG, PV, and LV flags. Each entry has a bit mask, optional text description, and kind: status flag, compatible flag, or segment-type flag.

Flag tables intentionally include many internal-only flags with `NULL` descriptions. These bits are recognized so exports can clear them from the "unknown leftovers" check without writing them to metadata.

`print_flags` selects the table by object type, walks set bits, emits matching descriptions for the requested kind into a comma-separated quoted array, and warns if any unrecognized status bits remain. This is used by `export.c` for `status = [...]` and `flags = [...]`.

`read_flags` parses config values back into a status bitmask. It accepts empty arrays, requires string values, and has compatibility behavior for historical metadata:
- `CACHE_VOL` may be read as either status or compatible flag.
- Old VG `PARTIAL` status is accepted for backup restore compatibility even though live metadata no longer writes it.
- Unknown status flags are fatal.

`read_lvflags` parses extra LV flags embedded in a segment `type` string as `+FLAG` suffixes. These are intentionally treated as incompatible with old LVM versions. Unknown segtype flags produce a warning and failure.

`print_segtype_lvflags` appends all set `SEGTYPE_FLAG` LV flags to a buffer as `+FLAG` suffixes. This pairs with `read_lvflags` for metadata round-tripping of segment-level incompatibility markers.
