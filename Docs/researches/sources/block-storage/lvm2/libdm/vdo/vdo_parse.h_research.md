# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_parse.h

Purpose: declares shared VDO parsing helper functions.

Read coverage: complete file read, 23 lines.

Key contents:
- Declares whitespace skipping, token equality, uint64 parsing, and operating-mode parsing helpers.
- Exposes bounded-token signatures using begin/end pointers.

Dependencies:
- Consumed by VDO status and stats parsing code.
- Does not include the enum-defining public header itself, so including compilation units must provide required type declarations before use.

Risk and edge cases:
- Function signatures use `void *context` for typed outputs in parser callbacks, so callers must pass correctly typed storage.
