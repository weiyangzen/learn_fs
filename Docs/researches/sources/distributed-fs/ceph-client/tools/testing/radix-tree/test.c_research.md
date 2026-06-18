# sources/distributed-fs/ceph-client/tools/testing/radix-tree/test.c

Purpose: shared userspace test helpers for radix-tree and XArray tests, providing `struct item` lifecycle, assertions, gang scans, tag copying, tag consistency verification, tree cleanup, and height checks.

Important APIs/types/functions: wrappers `item_tag_set()`, `item_tag_clear()`, `item_tag_get()`; allocation/lifecycle helpers `item_create()`, `item_insert()`, `item_sanity()`, `item_free()`, `item_delete()`, `item_delete_rcu()`; lookup assertions; `item_gang_check_present()` and `item_full_scan()`; `tag_tagged_items()` modeled after page writeback tagging; recursive `verify_node()`/`verify_tag_consistency()`; `item_kill_tree()`; `tree_verify_min_height()`.

Control flow: helpers are called by tests rather than run directly. `tag_tagged_items()` locks an XArray, walks marked entries, sets a second mark, periodically pauses/unlocks and waits for RCU to exercise iterator restart. `item_kill_tree()` iterates the XArray, frees non-value entries, clears slots, and asserts emptiness.

State and persistence: no private persistent state; operates on caller-owned trees and heap items. RCU deletion defers freeing through `call_rcu()`.

Dependencies/integration: includes Linux type/kernel/bitops shims and exposes prototypes via `test.h`. It reaches normally private radix-tree helpers such as `entry_to_node()`, `root_tag_get()`, `node_maxindex()`, and `shift_maxindex()` for structural validation.

Risks and test signals: helpers rely heavily on `assert()`, so disabled assertions would weaken the suite. `item_sanity()` is central for multi-order correctness, ensuring covered indexes share the same order mask.
