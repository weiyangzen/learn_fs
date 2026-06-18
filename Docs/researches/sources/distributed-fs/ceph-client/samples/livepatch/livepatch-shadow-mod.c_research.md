# sources/distributed-fs/ceph-client/samples/livepatch/livepatch-shadow-mod.c

Purpose: intentionally buggy support module for livepatch shadow-variable examples.

Important APIs/functions: `struct dummy`, `dummy_alloc`, `dummy_free`, `dummy_check`, global `dummy_list`, `DEFINE_MUTEX`, delayed works `alloc_dwork` and `cleanup_dwork`, `schedule_delayed_work`, `cancel_delayed_work_sync`, `list_add`, `list_for_each_entry_safe`, and `kfree`.

Control flow: init schedules periodic allocation and cleanup workers. Allocation creates dummy objects and an intentionally leaked extra allocation. Cleanup scans the list, removes expired dummies, and calls `dummy_free`. Exit cancels workers and frees remaining list entries.

State and persistence: in-memory list of dummy objects and periodic work state while loaded; intentional leak allocations persist unless livepatch fixes catch them.

Dependencies and integration: livepatch fix modules target its noinline functions by symbol name.

Risks: intentionally leaks memory before patches are applied. Workqueue and list cleanup must be synchronized on exit. Target functions must remain noinline/available for livepatching.

Test signals: load alone and observe leak behavior/logs; then load fix modules and observe leak prevention and counter extension.
