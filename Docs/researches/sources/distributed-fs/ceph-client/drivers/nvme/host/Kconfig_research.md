# sources/distributed-fs/ceph-client/drivers/nvme/host/Kconfig

Purpose: Defines NVMe host-side configuration for core support, PCI block driver, multipath, verbose errors, hwmon, fabrics transports, TCP TLS, in-band authentication, and Apple ANS platform support.

Important APIs and flow: `NVME_CORE` is selected by host drivers. `BLK_DEV_NVME` depends on PCI and block. `NVME_MULTIPATH`, `NVME_VERBOSE_ERRORS`, and `NVME_HWMON` extend the core. `NVME_FABRICS` selects core and optionally keyring for TCP TLS. RDMA, FC, TCP, TCP TLS, and host auth select their required dependencies. `NVME_APPLE` depends on OF, block, Apple RTKit/SART, and Apple architecture or compile testing.

State and persistence behavior: Build-time only.

Dependencies and integration points: Controls object inclusion in `host/Makefile` and selects common auth/keyring symbols.

Risks and test signals: Config tests should cover host auth with fabrics transports, TCP TLS keyring selection, core as module versus built-in, and Apple compile-test builds.
