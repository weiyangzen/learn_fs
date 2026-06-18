# sources/distributed-fs/coda/coda-src/partition/partition.c

Purpose: central partition registry for Coda server storage. It reads `vicetab`, initializes matching host partitions with the right backend, records them in `DiskPartitionList`, and exposes lookup/usage/lock helpers.

APIs and flow: `DP_Init` filters `Partent` records by hostname, resolves backend type, calls backend `init`, and inserts a `DiskPartition`. `DP_InitPartition` checks unique device numbers and sets usage. `DP_Find` and `DP_Get` search by device/name. `DP_SetUsage` uses `statvfs`/`statfs` to compute 1K free/usable/minfree values. `DP_ResetUsage` refreshes all partitions with LWP yields. Lock helpers are currently disabled.

State/dependencies: owns global list state and per-partition backend pointers/private data. Risks include assertions on config/runtime errors, questionable `DP_Get` behavior on empty lists, disabled locking, and free-space accounting being approximate. Test signal is vicetab-driven partition tests.
