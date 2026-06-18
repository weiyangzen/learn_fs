# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/Kconfig

Purpose: Kconfig entry for the Intel Ethernet Protocol Driver for RDMA (`INFINIBAND_IRDMA`), covering Intel IPU E2000, E810, and X722 RDMA support.

Important symbols: `INFINIBAND_IRDMA` is a tristate option with help text describing RoCEv2 and iWARP device support. It depends on `INET`, `IPV6 || !IPV6`, `PCI`, and the Ethernet drivers `IDPF`, `ICE`, and `I40E`. It selects `GENERIC_ALLOCATOR`, `AUXILIARY_BUS`, and `CRC32`.

Control flow: kernel configuration determines whether the irdma driver is built in, built as a module, or omitted. Dependency selection ensures networking, PCI, auxiliary device support, allocator support, checksum helpers, and the required Intel Ethernet providers are available before compiling the RDMA driver.

State and persistence: no runtime state. This file controls build-time configuration and module availability.

Dependencies and integration: pairs with the irdma Makefile and parent InfiniBand Kconfig tree. The hard dependency on multiple Ethernet drivers reflects that irdma attaches through Intel networking devices and auxiliary bus plumbing.

Risks: depending on all listed Ethernet drivers may make the RDMA driver unavailable in configurations that only enable one supported NIC family. Kconfig dependency drift can surface as unresolved symbols or missing auxiliary devices during build/probe.

Test signals: `olddefconfig`, `allmodconfig`, module build with IPv6 enabled and disabled, and probe tests on IPU E2000/E810/X722 platforms.
