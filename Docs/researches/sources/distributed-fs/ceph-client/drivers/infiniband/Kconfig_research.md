# sources/distributed-fs/ceph-client/drivers/infiniband/Kconfig

Purpose: Top-level Kconfig for Linux InfiniBand/RDMA support in this source tree.

Important APIs/types/functions: Defines `INFINIBAND` menuconfig and major options including userspace MAD, userspace verbs/CM, user memory, on-demand paging, address translation (`INFINIBAND_ADDR_TRANS`), address-translation configfs, and virtual DMA. It sources hardware, software, and ULP subdirectory Kconfig files.

Control flow: build-time feature selection only. Nested blocks include hardware providers when appropriate and always include software RXE/SIW and ULP protocols under `INFINIBAND`.

State and persistence: kernel configuration state only.

Dependencies/integration: depends on networking, INET, DMA/IOMEM, and not ALPHA. Selects shared DMA buffer, IRQ polling, and DIMLIB. Integrates with rdma-core userspace expectations described in help text.

Risks: broad `select`s affect kernel footprint. `INFINIBAND_ADDR_TRANS` default y pulls RDMA CM support into many builds. Source ordering determines visible provider options. Dependency expressions around configfs and modules are subtle.

Test signals: config builds for core-only, userspace access, ODP, configfs, software providers, and representative hardware providers.
