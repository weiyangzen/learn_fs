# sources/distributed-fs/ceph-client/scripts/gdb/linux/modules.py

## Purpose
`modules.py` provides module enumeration, lookup, and text-address diagnostics for GDB sessions.

## Important APIs, Types, and Functions
`module_list()` walks the global `modules` list. `find_module_by_name()` matches `struct module.name`. `$lx_module()` returns the matched module object. `lx-lsmod` prints module text base, aggregate memory size, refcount, and source users. `lx-getmod-by-textaddr` maps an address to a module text range.

## Control Flow
Commands use `lists.list_for_each_entry()` over `struct module.list`, then read `module.mem[LX_MOD_*]`, refcounts, and `source_list` entries. Address lookup compares against `LX_MOD_TEXT` base and size.

## State and Persistence Behavior
Read-only. Module state is live target state and may be inconsistent on a running target without stop-the-world debugging.

## Dependencies and Integration Points
`symbols.py` uses `module_list()` for symbol loading. The module memory layout depends on constants generated from the target kernel.

## Risks and Test Signals
No module support returns empty iterators; command output assumes modern `struct module.mem[]` layout. Refcount output subtracts one, matching kernel `lsmod` semantics. Test with loaded modules, users, and addresses inside and outside module text.
