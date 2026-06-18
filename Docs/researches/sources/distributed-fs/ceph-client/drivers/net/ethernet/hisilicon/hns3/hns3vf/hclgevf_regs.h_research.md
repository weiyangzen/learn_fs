# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_regs.h

Declares the HNS3 VF register dump interface: `hclgevf_get_regs_len()` and `hclgevf_get_regs()`, with a forward declaration of `struct hnae3_handle`.

There is no runtime state or control flow in this header. It lets `hclgevf_main.c` wire register dump callbacks while keeping TLV/register-list internals in `hclgevf_regs.c`. Risks are signature drift against AE ops expectations. Test by building and invoking ethtool/HNAE3 register dump callbacks.
