# File Research: sources/block-storage/lvm2/tools/vals.h

Purpose: macro table defining command value types accepted by LVM2 options and positional arguments, including parser callbacks, symbolic names used in command definitions, and usage strings.

Read coverage: complete file read, 165 lines.

Key responsibilities:
- Documents the `val(enum, parser, name, usage)` convention used by command definitions and option definitions.
- Defines generic values such as boolean, number, signed number, string, VG/LV/PV name, tag, and select.
- Defines specialized values for activation mode, cache metadata format, cache mode, discards, mirror log, size/extents variants, permissions, metadata type, units, segment type, allocation policy, lock type, readahead, metadata copies, poll operation, write-mostly PV, sync action, report/config formats, repair/dump type, and headings.
- Uses build-time lock-manager support macros to include only supported lock type strings in usage text.
- Ends with `VAL_COUNT` sentinel.

Dependencies:
- Consumed by generated command/argument metadata code through a caller-defined `val` macro.
- Parser callback names are declared in `tools.h` and implemented in the tools argument parsing layer.

Risks and edge cases:
- Usage strings are intentionally not always the full accepted language; parsing functions may accept legacy or hidden values.
- Specialized values require parser behavior, implementation behavior, and usage text to remain synchronized.
- Because this is a macro table, syntax errors or enum reorderings can break generated command metadata broadly.
