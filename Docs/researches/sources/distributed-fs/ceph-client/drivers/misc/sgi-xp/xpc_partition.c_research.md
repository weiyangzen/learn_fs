# sources/distributed-fs/ceph-client/drivers/misc/sgi-xp/xpc_partition.c

Purpose: implements XPC partition discovery and partition activation/deactivation support. It handles reserved-page setup/teardown, remote reserved-page reads, NASID discovery, disengage timeout handling, partition active/inactive transitions, and partid-to-NASID lookups.

Important APIs/functions: exports `xpc_kmalloc_cacheline_aligned()`, `xpc_setup_rsvd_page()`, `xpc_teardown_rsvd_page()`, `xpc_get_remote_rp()`, `xpc_partition_disengaged()`, `xpc_partition_disengaged_from_timer()`, `xpc_mark_partition_active()`, `xpc_deactivate_partition()`, `xpc_mark_partition_inactive()`, `xpc_discovery()`, and `xpc_initiate_partid_to_nasids()`. It owns globals `xpc_exiting`, `xpc_rsvd_page`, `xpc_mach_nasids`, `xpc_nasid_mask_nlongs`, and `xpc_partitions`.

Control flow: local setup locates the firmware reserved page, validates partition identity, fills XPC version and NASID mask metadata, lets architecture code append transport fields, then sets `ts_jiffies` to advertise readiness. Discovery scans hardware regions/NASIDs from SAL masks, skips local or already discovered partitions, copies remote reserved pages with `xp_remote_memcpy()`, validates version and partition IDs, and requests activation. Deactivation moves the partition to deactivating, sends architecture deactivation request, starts a disengage timer, and asks channels to go down.

State and persistence: local reserved page fields are shared platform memory but initialized at runtime; `ts_jiffies` is the readiness marker and is reset to zero on teardown. Remote partition state is cached in `xpc_partition` entries, including `remote_rp_pa`, heartbeat metadata, act_state, reason, and timer state.

Dependencies and integration: depends on XP architecture hooks for reserved-page lookup/copy, heartbeat engagement, activation requests, and memory address conversion. XPC main uses these functions during init, discovery, activation, and exit.

Risks: reserved-page version or partid mismatch prevents activation. Discovery depends on correct NASID masks and region-size interpretation. `xpc_initiate_partid_to_nasids()` computes a remote mask address from `remote_rp_pa`, so stale remote reserved-page addresses after partition down would be unsafe; it guards on zero. Disengage timeout can force-assume a peer is dead.

Test signals: reserved-page setup with SAL version variants, remote copy failures, major-version mismatch, local-partition detection, discovery over region masks, activation request issuance, deactivation timeout, reactivation reason handling, and partid-to-NASID behavior when remote partition is down.
