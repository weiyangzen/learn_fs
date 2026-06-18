# sources/distributed-fs/ceph-client/drivers/infiniband/core/Makefile

Purpose: kbuild definitions for RDMA core modules and optional core components.

Important APIs/types/functions: Builds `ib_core.o`, `ib_cm.o`, `iw_cm.o`, `rdma_cm.o`, `rdma_ucm.o`, `ib_umad.o`, and `ib_uverbs.o` based on Kconfig. `ib_core-y` includes core files such as `addr.o`, `verbs.o`, `device.o`, `cache.o`, `netlink.o`, `sa_query.o`, and more. Optional objects are added for security, RDMA cgroups, user memory, and ODP.

Control flow: build-time object aggregation only.

State and persistence: none beyond module composition.

Dependencies/integration: maps `CONFIG_INFINIBAND_ADDR_TRANS` to RDMA CM/UCMA, and userspace features to `ib_umad`/`ib_uverbs`. Adds include path for `cma_trace.o`.

Risks: object membership affects exported symbols and module dependencies. `addr.o` is always in `ib_core-y`, so address resolution is part of core whenever InfiniBand is enabled.

Test signals: representative configs should link built-in and modular core variants, including address translation on/off and user access on/off.
