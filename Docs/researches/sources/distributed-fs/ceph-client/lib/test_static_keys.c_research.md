# sources/distributed-fs/ceph-client/lib/test_static_keys.c

## Purpose

`sources/distributed-fs/ceph-client/lib/test_static_keys.c` verifies old and new static key APIs, including internal keys and external keys exported by `test_static_key_base.c`. It checks that static key enabled state matches branch macro results before and after toggling. The source was read as a complete 240-line file.

## Important APIs, Types, and Functions

Local keys are `old_true_key`, `old_false_key`, `true_key`, and `false_key`. External keys are the eight `base_*` symbols from the base module. `struct test_key` binds an expected initial state, `struct static_key *`, and a function pointer that evaluates a branch. `test_key_func` generates branch-testing functions for `static_key_true`, `static_key_false`, `static_branch_likely`, and `static_branch_unlikely`. Helpers are `invert_key`, `invert_keys`, `verify_keys`, and `test_static_key_init`.

## Control Flow

On load, `test_static_key_init` builds a table covering internal old/new keys and external old/new keys, including both likely and unlikely branch forms for new-style keys. It first verifies all keys match expected initial states, then toggles each unique key once with `invert_keys` and verifies every state and branch result is inverted, then toggles back and verifies the original state again. It returns the first `-EINVAL` failure or `0`.

## State and Persistence Behavior

Internal static keys are module globals. External static keys are owned by `test_static_key_base`. The test temporarily mutates all unique keys twice and is intended to leave them in their initial expected states when successful. There is no storage persistence.

## Dependencies and Integration Points

Direct includes are `<linux/module.h>` and `<linux/jump_label.h>`. Integration points include static key old APIs, static branch likely/unlikely APIs, generated jump-label patching, and exported symbols from `test_static_key_base.c`.

## Risks and Edge Cases

The test depends on the base module being present and initialized so inverted external keys have the expected states. `invert_keys` assumes duplicate key entries are adjacent, which is true for the local table and avoids toggling likely/unlikely variants twice. A reordered table could break that assumption. Static branch behavior can be architecture-sensitive because jump labels patch code.

## Test Signals

Successful module load returns `0`. Failures return `-EINVAL` from `verify_keys` when either `static_key_enabled()` or the generated branch predicate disagrees with the expected state.
