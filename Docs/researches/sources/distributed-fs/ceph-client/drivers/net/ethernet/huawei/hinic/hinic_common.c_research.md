# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_common.c

Provides shared HiNIC helpers for in-place 32-bit endian conversion and DMA scatter-gather entry handling. APIs are `hinic_cpu_to_be32()`, `hinic_be32_to_cpu()`, `hinic_set_sge()`, and `hinic_sge_to_dma()`.

The endian helpers iterate over `len / sizeof(u32)` words and ignore trailing bytes. SGE helpers split/reconstruct a DMA address into high/low 32-bit fields plus length. There is no persistent state. Dependencies are byteorder helpers, Linux types, and `hinic_common.h`. Risks are caller alignment/length mistakes and DMA address width assumptions. Test with buffer conversion round trips and SGE DMA address round trips in management/data paths.
