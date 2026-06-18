# sources/distributed-fs/ceph-client/drivers/xen/grant-table.c

Purpose: implements the core Xen grant-table subsystem: grant reference allocation/free, grant entry updates, mapping/unmapping foreign grants, page allocation for grant mappings, deferred release, grant-table setup, and version selection.

Important APIs/functions: exports grant issuing/freeing APIs, sequential grant allocation APIs, free callbacks, page allocation/cache helpers, DMA grant page helpers, batch map/copy, grant iteration helpers, map/unmap refs including async/sync variants, auto-translated frame setup/free, suspend/resume hooks, and `gnttab_init`. Core state includes `gnttab_list`, free list/bitmap counters, `gnttab_shared`, `grstatus`, `gnttab_interface`, deferred release list/timer, and `xen_auto_xlat_grant_frames`.

Control flow: init chooses grant-table v1 or v2, allocates free-list pages and bitmap, maps the initial grant table, and marks non-reserved refs free. Allocation pops refs from the free list or rebuilds/finds sequential ranges, expanding the table when needed. Granting writes domid/frame then barriers before valid flags. Ending access clears flags and either frees immediately or queues deferred retry if the remote side still maps the grant. Mapping foreign refs issues `GNTTABOP_map_grant_ref`, marks pages foreign, and installs p2m mappings; unmap clears grant refs and p2m state. Async unmap delays while page refs remain elevated. Non-PV auto-xlat setup maps grant frames through `XENMEM_add_to_physmap`.

State and persistence: grant-table pages, free reference structures, deferred entries, page caches, status frames, and auto-xlat frames persist globally. Resume remaps shared/status frames and reselects table version.

Dependencies and integration: depends on Xen grant-table and memory hypercalls, arch grant-table mapping hooks, p2m/foreign-page helpers, balloon/unpopulated page allocation, DMA APIs when enabled, timers, workqueues, and module parameters `version` and `free_per_iteration`.

Risks: grant lifecycle is sensitive to memory ordering and remote access status; sequential allocation rebuilds global free state; deferred release can leak if allocation for retry metadata fails; async unmap waits on page refs and can delay teardown; v1/v2 selection depends on address width and boot override; max grant frames are capped at boot-time maximum.

Test signals: allocate/free single and sequential refs, grant/end access while a peer maps pages, table expansion to limits, v1 and v2 layouts, grant map/copy with `GNTST_eagain`, async unmap with held page refs, suspend/resume, auto-xlat HVM setup, and DMA grant page allocate/free.
