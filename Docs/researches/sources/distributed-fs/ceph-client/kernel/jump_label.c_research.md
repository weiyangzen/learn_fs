# sources/distributed-fs/ceph-client/kernel/jump_label.c

## Purpose
Implements Linux jump-label/static-key runtime support: it sorts generated `__jump_table` entries, binds entries to `struct static_key`, patches branch/NOP sites through architecture hooks, and tracks module-provided jump-label sites. The file is performance critical because static branches are used across hot paths to turn feature checks into patched instructions.

## Important APIs, Types, and Functions
Exports `static_key_count`, `static_key_slow_inc`, `static_key_slow_dec`, `static_key_enable`, `static_key_disable`, deferred decrement helpers, `jump_label_rate_limit`, and `jump_label_text_reserved`. Initialization is in `jump_label_init`, `jump_label_init_ro`, and the module notifier registered by `jump_label_init_module`. Internally, `jump_label_cmp`, `jump_label_sort_entries`, `static_key_set_entries`, `jump_label_type`, `jump_label_can_update`, and `__jump_label_update` are the key mechanics. With modules enabled, `struct static_key_mod` links a key to jump entries in built-in and module tables.

## Control Flow
Boot initialization sorts `__start___jump_table` to `__stop___jump_table`, rewrites default NOPs, marks init-text entries, and stores each key's first entry pointer. Runtime enable paths transition `key->enabled` from 0 to -1 while patching and publish 1 with release ordering; disable/decrement paths only patch when the count reaches 0. `jump_label_update` resolves whether a key points directly at entries, is linked to module lists, or belongs to a module, then calls `__jump_label_update` to invoke `arch_jump_label_transform` or queued batch patching.

## State and Persistence
State is in each `static_key` (`enabled`, entry pointer/type bits, linked-list tag), in static module-list nodes allocated at module load, and in global `static_key_initialized`. `jump_label_mutex` and CPU read locks serialize table mutation and text patching against CPU/module hotplug. No disk persistence exists; state is reconstructed at boot and maintained across module load/unload.

## Dependencies and Integration Points
Depends on generated jump-table sections, architecture jump-label transform hooks, module notifier ordering, init section helpers, `kernel_text_address`, CPU hotplug locking, and static-key APIs from `linux/static_key.h`. Text patching clients use `jump_label_text_reserved` to avoid overwriting patch sites.

## Risks
Incorrect reference count transitions can patch live text in the wrong direction. Module add/remove must fold linked keys back to direct entries without leaving stale `static_key_mod` nodes. The relative-entry swap function must preserve self-relative offsets during sort. `jump_label_can_update` deliberately skips init/exit text outside legal patch windows; mistakes here can patch freed or non-text memory.

## Test Signals
`CONFIG_STATIC_KEYS_SELFTEST` runs `jump_label_test` as an early initcall, toggling true/false static branches and checking `static_key_enabled` and branch helpers. Runtime warnings cover underflow, concurrent enable/decrement ordering, missing module-list nodes, bad text addresses, and failed allocations during module notifier handling.
