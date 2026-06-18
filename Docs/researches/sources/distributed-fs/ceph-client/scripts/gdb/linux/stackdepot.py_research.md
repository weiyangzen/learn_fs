# sources/distributed-fs/ceph-client/scripts/gdb/linux/stackdepot.py

## Purpose
`stackdepot.py` decodes stack depot handles and prints stored stack traces through `lx-stack_depot_lookup`.

## Important APIs, Types, and Functions
`stack_depot_fetch()` splits a handle with `union handle_parts`, computes pool index and offset, and returns stack entries plus count from `struct stack_record`. `stack_depot_print()` disassembles each entry address with `gdb.execute("x /i")`.

## Control Flow
The command validates one hex handle, casts it to an unsigned int, fetches entries, and prints instructions for each recorded frame. Invalid pool indexes return empty data; disabled stack depot raises an error.

## State and Persistence Behavior
Read-only and stateless. It reads persistent kernel stack depot pools.

## Dependencies and Integration Points
`page_owner.py` and `slab.py` call `stack_depot_print()`. It depends on `CONFIG_STACKDEPOT`, `stack_pools`, `pools_num`, `stack_depot_disabled`, and handle layout debug info.

## Risks and Test Signals
The output is instruction-oriented, not symbolic backtrace formatting. Handle-part layout drift or pool corruption can lead to wrong offsets. Test with known handles from page owner or SLUB tracks and invalid/zero handles.
