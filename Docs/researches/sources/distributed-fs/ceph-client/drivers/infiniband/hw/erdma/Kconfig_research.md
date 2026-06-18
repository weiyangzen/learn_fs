# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/Kconfig

Adds the Kconfig entry for Alibaba Elastic RDMA Adapter support.

`config INFINIBAND_ERDMA` is a tristate option depending on `PCI_MSI`, `64BIT`, `INFINIBAND_ADDR_TRANS`, and `INFINIBAND_USER_ACCESS`. Its help text describes the Alibaba cloud ERDMA device and module name `erdma`.

There is no runtime control flow. The selected value controls whether ERDMA is built in, built as a module, or omitted. The config state persists in kernel `.config` and determines whether PCI device IDs can bind to this driver.

Dependencies integrate the driver with PCI MSI and RDMA user/address-translation infrastructure. Risks are missing dependencies that allow broken builds or overly strict dependencies that hide the driver. Test signals include Kconfig visibility on expected platforms, successful `M` module builds, and no ERDMA object build when disabled.
