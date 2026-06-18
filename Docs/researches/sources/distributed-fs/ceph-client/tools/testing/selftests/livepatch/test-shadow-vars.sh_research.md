# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test-shadow-vars.sh

## Purpose

`test-shadow-vars.sh` validates the livepatch shadow variable API by loading a module that allocates, retrieves, and frees shadow variables for several simulated objects.

## Important APIs, Types, and Functions

The shell script uses `load_mod()`, `unload_mod()`, and `check_result()` with module `test_klp_shadow_vars`. The module exercises `klp_shadow_get()`, `klp_shadow_alloc()`, `klp_shadow_get_or_alloc()`, `klp_shadow_free()`, and `klp_shadow_free_all()`.

## Control Flow and State

The script delegates behavior to module init, then checks a long normalized dmesg transcript using pointer placeholders such as `PTR1`. The module creates shadow state for multiple object/id pairs, confirms lookups, frees one ID per object, verifies the other ID remains, and frees all remaining entries.

## Dependencies and Integration Points

It depends on the livepatch shadow variable API, deterministic module logging, and harness dmesg filtering.

## Risks and Test Signals

Risks are duplicate allocation, missing constructor/destructor calls, freeing wrong object/id pairs, and pointer-address nondeterminism. Signals are exact ordered log lines showing expected NULL lookups, stable pointer aliases, destructor calls for single frees, and NULL results after `free_all`.
