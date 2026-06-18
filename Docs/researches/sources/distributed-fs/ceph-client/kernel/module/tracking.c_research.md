# sources/distributed-fs/ceph-client/kernel/module/tracking.c

## Purpose
Tracks unloaded modules that had taint flags, preserving diagnostic evidence after the module is gone.

## Important APIs, Types, And Functions
Exports `try_add_tainted_module` and `print_unloaded_tainted_modules`. Debugfs support defines seq operations and an `unloaded_tainted` file under `mod_debugfs_root`. State entries use `struct mod_unload_taint`.

## Control Flow
During module free, `main.c` calls `try_add_tainted_module`. The helper ignores untainted modules, increments an existing entry if the same module name and taints were already seen, or allocates a new list entry. `print_unloaded_tainted_modules` appends the tracked list to module diagnostics. Debugfs seq iteration exposes the same list.

## State And Persistence
State is an in-memory RCU list `unloaded_tainted_modules` containing module name, taint mask, and count. It persists until reboot.

## Dependencies And Integration Points
Depends on module taint formatting from `main.c`, `module_mutex` for mutation, RCU list traversal, debugfs, and seq_file.

## Risks And Edge Cases
Allocation failure loses diagnostics but should not block unload. Matching requires overlapping taint bits for the same name; changed taint combinations may create separate entries. Debugfs iteration must use RCU.

## Test Signals
Unload tainted modules multiple times, inspect oops/module print output and debugfs `unloaded_tainted`, and verify untainted unloads do not create entries.
