# sources/distributed-fs/ceph-client/drivers/nvme/host/Makefile

Purpose: Maps NVMe host Kconfig symbols to kernel objects and modules.

Important APIs and flow: Builds `nvme-core.o`, PCI `nvme.o`, fabrics, RDMA, FC, TCP, and Apple modules as selected. `nvme-core-y` includes core/ioctl/sysfs/pr and conditionally adds verbose `constants.o`, tracing, multipath, zoned namespace support, fault injection, hwmon, and host auth. Transport modules map to their C files; `nvme-apple-y` maps to `apple.o`.

State and persistence behavior: Build-time only.

Dependencies and integration points: Integrates host core features and transport implementations with kbuild. Conditional inclusion determines whether symbols like verbose status strings and host auth lifecycle are available.

Risks and test signals: Build tests should cover modular combinations, especially `NVME_HOST_AUTH`, `NVME_VERBOSE_ERRORS`, and `NVME_APPLE`, and ensure no unresolved symbols when optional core features are disabled.
