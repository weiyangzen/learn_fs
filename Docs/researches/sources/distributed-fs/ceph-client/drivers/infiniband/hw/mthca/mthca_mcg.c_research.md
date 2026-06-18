# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mcg.c

Purpose: manages Mellanox mthca multicast group membership records (MGMs) for InfiniBand QPs, including hash-bucket MGMs and chained auxiliary MGMs.

Important APIs/functions: defines the packed firmware-facing `struct mthca_mgm`; implements `mthca_multicast_attach`, `mthca_multicast_detach`, `mthca_init_mcg_table`, and `mthca_cleanup_mcg_table`. The internal `find_mgm` hashes a GID with `mthca_MGID_HASH`, follows `next_gid_index` chains via `mthca_READ_MGM`, and reports whether the matching GID, an empty primary slot, or no auxiliary entry exists.

Control flow: attach allocates a mailbox, locks `dev->mcg_table.mutex`, finds or creates the MGM/AMGM entry, installs the QP number with the high valid bit set, writes the entry, and links a newly allocated AMGM from the previous chain element. Detach finds the entry, removes the QP by swapping the final occupied slot into its position, writes the MGM, and if the entry became empty either clears the primary MGM or unlinks/frees an AMGM.

State and persistence: multicast membership is persisted in HCA multicast table entries through firmware commands; the driver only tracks AMGM allocation via `dev->mcg_table.alloc` and serializes updates with the table mutex. The `lid` argument is unused in this implementation.

Dependencies and integration: depends on `mthca_cmd` mailbox commands, the common allocator in `mthca_alloc`, `dev->limits.num_mgms/num_amgms`, and RDMA core multicast attach/detach hooks registered by `mthca_provider.c`.

Risks: chain corruption or firmware command failure can leave hardware membership partially updated; full MGMs return `-ENOMEM`; invalid zero GIDs in AMGM entries are treated as corruption. Cleanup only tears down allocator state and does not verify that all memberships were detached.

Test signals: exercise RDMA multicast join/leave on UD QPs, duplicate attach idempotence, full-group behavior, AMGM chain creation/removal, and firmware failure unwinding under `mthca_multicast_attach`.
