# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_regs.c

Provides HNS3 VF ethtool/HNAE3 register dump support. It exports `hclgevf_get_regs_len()` and `hclgevf_get_regs()`, using TLV groups for command queue, common VF, per-ring, and per-TQP interrupt registers plus a magic VF header.

Control flow is deterministic: compute total dump bytes from fixed groups, `hdev->num_tqps`, and `hdev->num_msi_used - 1`; then serialize header/TLVs and read MMIO registers from VF base or per-TQP queue bases. It does not modify persistent state and reports firmware version through the caller-provided version pointer.

Dependencies are `hclgevf_ae_get_hdev()`, HCLGE common register constants, `hclgevf_main.h` offsets, and `hclgevf_regs.h`. Risks are dump length/write mismatch, queue/vector count changes during dump, per-ring base offset assumptions, and external diagnostic ABI changes. Test via ethtool register dump on varying queue/vector counts and during reset windows.
