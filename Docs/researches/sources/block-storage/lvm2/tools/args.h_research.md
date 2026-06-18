# File Research: sources/block-storage/lvm2/tools/args.h

Purpose: provides the X-macro catalogue of LVM command-line options, including option IDs, short names, long names, value types, flags, grouping behavior, and help/man text.

Read coverage: complete file read, 1,897 lines.

Key responsibilities:
- Defines every recognized LVM tool option through repeated `arg(id, short, long, val_type, flags, groupable_count, help)` macro invocations.
- Places long-only options first, then synonym-only aliases, then short-option definitions, with `ARG_UNUSED` at the start and `ARG_COUNT` at the end.
- Captures detailed help text for command-specific and shared options, with `#command` markers used to vary descriptions by command.
- Marks countable options such as `--debug`, `--verbose`, `--quiet`, and force variants.
- Marks groupable options such as tags, devices, settings, report options, and PV-specific RAID options.
- Defines synonyms such as `--allocation`, `--available`, `--corelog`, raid-prefixed aliases, `--split`, and `--virtualoriginsize`.
- Covers general configuration/reporting options, activation and locking, devices file management, PV/VG/LV metadata, RAID, thin, cache, writecache, integrity, VDO, filesystem resize, persistent reservations, and deprecated options.
- Documents options whose value parser is overridden per command, notably `--size` and `--extents`.

Dependencies:
- Consumed by code that defines the `arg` macro to generate enums, lookup tables, parsing metadata, and documentation.
- Value type names refer to parser definitions in the tools value layer, such as `bool_VAL`, `sizemb_VAL`, `pv_VAL`, `segtype_VAL`, and VDO/cache/thin-specific values.

Risk and edge cases:
- This file is data-as-code: macro argument order and sentinel placement are part of the parser contract.
- Short option characters are reused by different logical options; command definitions disambiguate valid usage.
- Synonym options intentionally have no generated help text and must translate to standard option IDs before command matching.
- Some entries are marked not used or deprecated but remain for compatibility.
- Help strings include roff escapes and command-specific fragments, so formatting changes can affect generated man/help output.
