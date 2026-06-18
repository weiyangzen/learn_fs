# sources/distributed-fs/ceph-client/security/landlock/ruleset.h

## Purpose

`ruleset.h` declares the Landlock policy data model: layers, rule keys, rules, rulesets/domains, lifetime helpers, mask accessors, and lookup/check APIs.

## Important APIs, Types, and Functions

`struct landlock_layer` stores a layer level and allowed access bits. `union landlock_key` holds an object pointer or raw data. `enum landlock_key_type` identifies inode and network-port trees. `struct landlock_rule` stores an RB node, key, and flexible layer stack. `struct landlock_ruleset` stores inode and optional network RB roots, hierarchy, refcount/lock/rule count/layer count, and per-layer access masks. Public APIs include `landlock_create_ruleset()`, `landlock_insert_rule()`, `landlock_merge_ruleset()`, `landlock_find_rule()`, `landlock_unmask_layers()`, and `landlock_init_layer_masks()`.

## Control Flow

Callers create a mutable one-layer ruleset, append rules, then merge it with a parent domain to produce a new immutable domain. Enforcement hooks use accessors to build layer masks and find matching rules by object or port key.

## State and Persistence Behavior

Rulesets/domains are reference-counted and may be freed synchronously or deferred. Access masks are immutable after domain creation. Rule layer stacks are persistent until ruleset free.

## Dependencies and Integration Points

The header connects filesystem, network, syscall, credential, and task code. It depends on object wrappers, access masks, mutexes, RB trees, workqueues, and optional INET compilation.

## Risks and Test Signals

Flexible array sizing and layer count limits must stay aligned with `limits.h`. File and network key types must use compatible tree roots. Test compile-time assertions, max layer boundaries, and both `CONFIG_INET` modes.
