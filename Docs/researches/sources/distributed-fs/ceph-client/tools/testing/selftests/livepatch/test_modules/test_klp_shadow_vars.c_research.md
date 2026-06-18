# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/test_klp_shadow_vars.c

## Purpose

`test_klp_shadow_vars.c` is a kernel module that exercises the livepatch shadow-variable API over multiple objects and IDs, while producing address-independent log output for shell verification.

## Important APIs, Types, and Functions

It wraps `klp_shadow_get()`, `klp_shadow_alloc()`, `klp_shadow_get_or_alloc()`, `klp_shadow_free()`, and `klp_shadow_free_all()`. It defines `shadow_ctor()`, `shadow_dtor()`, pointer aliasing helpers using a list, constants `NUM_OBJS`, `SV_ID1`, and `SV_ID2`, and a local `struct test_object`.

## Control Flow and State

Module init registers pointer IDs, verifies initial NULL lookup, allocates char and int shadow variables for three objects, verifies retrieval, confirms get-or-alloc returns existing entries, frees all `SV_ID1` entries with destructors, verifies `SV_ID2` remains, then frees all `SV_ID2` entries. Error cleanup frees all known IDs and pointer alias records.

## Dependencies and Integration Points

It depends on livepatch shadow-variable internals, slab allocation, kernel lists, and `test-shadow-vars.sh`.

## Risks and Test Signals

Risks are memory leaks, constructor data mishandling, nondeterministic destructor ordering, and raw pointer logs making tests unstable. Signals are normalized `PTRn` logs matching allocation, lookup, destructor, and final NULL expectations.
