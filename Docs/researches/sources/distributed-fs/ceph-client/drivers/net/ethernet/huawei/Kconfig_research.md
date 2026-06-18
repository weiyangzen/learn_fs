# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/Kconfig

Defines the top-level Huawei Ethernet vendor Kconfig gate `NET_VENDOR_HUAWEI`, defaulting to `y`. When enabled, it sources child Kconfig files for `hinic` and `hinic3`.

There is no runtime state; the persistent output is `.config` selection. The integration point is the kernel networking Kconfig tree, and disabling this vendor gate hides the child driver prompts. Risks are source path mistakes or expectation that the vendor symbol itself builds a driver. Test through menuconfig/allconfig combinations and child prompt visibility.
