# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/string-utils.h

## Purpose
`string-utils.h` declares small string helpers used by VDO code.

## Important APIs, Types, And Functions
`vdo_bool_to_string(bool value)` returns `"true"` or `"false"` for diagnostic output. `vdo_append_to_buffer()` appends formatted text into a bounded buffer and carries a `__printf(3, 4)` attribute for compile-time format checking.

## Control Flow
The inline boolean helper is a direct ternary. The append helper is implemented in `string-utils.c`.

## State And Persistence
No state is retained. The helpers are pure except for writes into caller-provided buffers.

## Dependencies And Integration Points
The header includes Linux kernel and string headers. `slab-depot.c` uses `vdo_bool_to_string()` in diagnostic dumps.

## Risks
The string literals are stable and safe. The append declaration relies on callers respecting buffer bounds and format/argument types.

## Test Signals
Tests should compile format-checked calls, verify boolean rendering, and exercise append truncation behavior through the implementation.
