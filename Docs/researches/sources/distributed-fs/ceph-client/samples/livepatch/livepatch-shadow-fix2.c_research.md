# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-fix2.c

Purpose: second shadow-variable livepatch that extends in-flight dummy objects with a check counter while preserving leak cleanup.

Important APIs/functions: `klp_shadow_get_or_alloc`, `klp_shadow_get`, `klp_shadow_free`, `klp_shadow_free_all`, replacement `livepatch_fix2_dummy_check` and `livepatch_fix2_dummy_free`, shadow IDs `SV_LEAK` and `SV_COUNTER`.

Control flow: patched check allocates/increments a per-dummy counter and returns expiry status. Patched free releases any leak pointer and counter before freeing the dummy. Exit frees all remaining counters.

State and persistence: per-object shadow counters and leak pointers during object lifetime.

Dependencies and integration: targets `dummy_check` and `dummy_free` in `livepatch_shadow_mod`, often layered after fix1.

Risks: combining multiple livepatches requires compatible replacement semantics. `GFP_NOWAIT` counter allocation can fail, resulting in missing counts.

Test signals: load shadow module, fix1, then fix2; observe check counters printed at cleanup and no unbounded leaked allocations.
