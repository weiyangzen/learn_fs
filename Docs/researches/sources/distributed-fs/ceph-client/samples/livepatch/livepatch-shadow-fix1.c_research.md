# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-fix1.c

Purpose: first livepatch fix for the shadow-variable demo, preventing a deliberate memory leak by attaching leaked pointers as shadow variables.

Important APIs/functions: `klp_shadow_alloc`, `klp_shadow_get`, `klp_shadow_free`, `klp_shadow_free_all`, `shadow_leak_ctor`, replacement `livepatch_fix1_dummy_alloc` and `livepatch_fix1_dummy_free`, and livepatch metadata targeting `livepatch_shadow_mod`.

Control flow: patched allocation creates dummy plus extra allocation, then stores the extra pointer in shadow variable `SV_LEAK`. Patched free retrieves and frees the shadow leak before freeing dummy. Exit frees remaining `SV_LEAK` variables.

State and persistence: shadow variables associated with dummy object addresses while objects exist.

Dependencies and integration: targets `dummy_alloc` and `dummy_free` symbols in `livepatch-shadow-mod.c`.

Risks: objects allocated before patch lack shadow variables and are reported as leaked. Constructor failure unwinds allocations. Shadow variable ID must not collide with other livepatches for the same objects.

Test signals: load buggy module, then fix1, watch logs for prevented leaks, disable/remove and verify shadow cleanup.
