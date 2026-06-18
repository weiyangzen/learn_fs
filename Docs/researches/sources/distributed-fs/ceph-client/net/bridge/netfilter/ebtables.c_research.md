# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebtables.c

## Purpose
Implements the legacy ebtables core: bridge-family rule evaluation, table registration/lazy templates, sockopt get/set ABI, userspace table replacement validation, counters, match/watcher/target module loading, per-net table lifetime, and 32-bit compat translation.

## Important APIs, Types, And Functions
Exported APIs include `ebt_do_table`, `ebt_register_table`, `ebt_unregister_table_pre_exit`, `ebt_unregister_table`, `ebt_register_template`, and `ebt_unregister_template`. Important internals include `struct ebt_pernet`, `struct ebt_template`, `ebt_basic_match`, `ebt_check_match`, `ebt_check_watcher`, `ebt_verify_pointers`, `ebt_check_entry_size_and_hooks`, `check_chainloops`, `translate_table`, `do_replace`, `do_replace_finish`, `update_counters`, `copy_everything_to_user`, compat conversion helpers, and sockopt handlers.

## Control Flow
Packet evaluation locks the active table, selects the base chain for the bridge hook, evaluates basic Ethernet/device/logical bridge matches, then extension matches, watchers, and targets. Standard verdicts accept/drop/return/continue or jump to user-defined chains through a per-CPU chain stack. Userspace replacement copies a table blob, verifies hook pointers and entry sizes, detects chain loops, resolves and validates match/watcher/target modules, swaps the active table under lock, snapshots counters, and cleans old modules/resources. Get paths copy active or initial tables back to userspace with extension names restored. Compat paths resize 32-bit entries and embedded match/watcher/target data before reuse of normal validation.

## State And Persistence Behavior
Per-net state is a live table list and dead-table list. Each table has rwlock-protected active `ebt_table_info`, vmalloced entries, per-CPU counters, optional per-CPU chain stacks, module references, and nf hook ops. State is memory-only and controlled through legacy sockopts requiring `CAP_NET_ADMIN`. Counters are accumulated per CPU and copied/updated atomically under write locks.

## Dependencies And Integration Points
Depends on x_tables, netfilter bridge hooks, nf sockopts, pernet generic storage, module autoloading, audit logging, usercopy, vmalloc, bridge private logical in/out device lookup, and all legacy ebtables table/match/target modules. It provides the common runtime for `ebtable_*` table files and `ebt_*` extensions.

## Risks And Test Signals
Highest risks are user-supplied blob validation, pointer/offset arithmetic, chain-loop detection, compat resizing, module refcount cleanup on partial failure, counter size overflow, concurrent table replacement versus packet evaluation, and namespace teardown. Strong signals include syzkaller/usercopy fuzzing, KASAN/KCSAN runs, 32-bit compat ebtables tests, table replace/get/counter round trips, loop/jump validation tests, module autoload/unload tests, per-net namespace teardown, and packet traversal tests for base chains and user-defined chains.
