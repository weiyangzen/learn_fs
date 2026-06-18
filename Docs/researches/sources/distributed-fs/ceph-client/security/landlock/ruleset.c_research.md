# sources/distributed-fs/ceph-client/security/landlock/ruleset.c

## Purpose

`ruleset.c` implements Landlock ruleset storage, rule insertion, domain creation by merging nested rulesets, ruleset inheritance, lookup, and per-layer mask initialization/unmasking. It is the policy data-structure core of Landlock.

## Important APIs, Types, and Functions

`create_ruleset()` allocates a ruleset with a flexible `access_masks[]` layer array. `landlock_create_ruleset()` creates a one-layer mutable ruleset. `create_rule()`, `insert_rule()`, and `landlock_insert_rule()` manage red-black tree rules for inode objects and network ports. `merge_tree()`, `merge_ruleset()`, `inherit_tree()`, and `inherit_ruleset()` build immutable domains from a parent domain plus a new ruleset. `landlock_merge_ruleset()` creates the new domain and hierarchy. `landlock_find_rule()`, `landlock_unmask_layers()`, and `landlock_init_layer_masks()` are hot-path lookup/check helpers. `landlock_put_ruleset()` and `landlock_put_ruleset_deferred()` free rulesets synchronously or through workqueue.

## Control Flow

Unenforced rulesets have one layer at level 0 and can be extended by adding rules for the same object/port, OR-ing access rights. When `restrict_self` merges a ruleset into a domain, a new ruleset is allocated with parent layers plus one new layer, parent rules are copied, parent hierarchy is referenced, the new ruleset's handled masks are upgraded, and each new rule is inserted as a layer with a real level. Matching existing domain rules are replaced with a new rule whose layer stack is extended. Access checks initialize masks for layers that handle the requested bit and clear them with rule layers until no unfulfilled access remains.

## State and Persistence Behavior

Rulesets are reference-counted. Enforced domains are immutable and carry a hierarchy pointer. Rules are stored in red-black trees keyed by object pointer or raw port data and own references to object keys when applicable. Deferred freeing is used from credential cleanup where sleeping may be unsafe.

## Dependencies and Integration Points

The file depends on object lifetime, domain hierarchy, access masks, red-black trees, workqueues, mutexes, and optional INET support. It is called by syscalls, filesystem/network rule appenders, and enforcement hooks.

## Risks and Test Signals

Layer numbering, OR-versus-AND semantics, and object reference handling are critical. Bugs can grant access in nested domains, leak rules, or fail with use-after-free. Test nested restrict-self composition, duplicate rule insertion, max layer and max rule limits, inode and net-port lookup, deferred freeing, and Landlock KUnit/selftests.
