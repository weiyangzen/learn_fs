# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_status.c

Purpose: parses VDO device-mapper target status strings into `struct dm_vdo_status`.

Read coverage: complete file read, 199 lines.

Key responsibilities:
- Parses a whitespace-separated VDO status line containing device, operating mode, recovering marker, index state, compression state, used blocks, and total blocks.
- Provides small enum parsers for compression state, recovering marker, and index state.
- Uses shared VDO parsing helpers for whitespace, token equality, operating mode, and uint64 fields.
- Stores human-readable parse failures in `dm_vdo_status_parse_result.error`.
- Supports allocation either from a supplied `dm_pool` or heap allocation.

Important entry point:
- `dm_vdo_status_parse(struct dm_pool *mem, const char *input, struct dm_vdo_status_parse_result *result)`

Dependencies:
- Includes public libdevmapper definitions unless built in the dmeventd plugin context.
- Uses `vdo/vdo_parse.h` and standard string/ctype/varargs helpers.

Risk and edge cases:
- The parser requires exactly the expected token count and rejects extra trailing tokens.
- On heap-backed failure it frees the duplicated device string and status object; pool-backed failed allocations remain pool-owned.
- Unknown operating/index/compression tokens produce explicit parse errors.
- The recovering field accepts only `recovering` or `-`.
