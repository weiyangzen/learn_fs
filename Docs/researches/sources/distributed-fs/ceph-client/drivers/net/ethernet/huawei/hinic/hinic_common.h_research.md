# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_common.h

Declares HiNIC common utility macros, `struct hinic_sge`, and helper prototypes for endian conversion and SGE address manipulation.

There is no control flow or owned state. `struct hinic_sge` is a hardware-facing DMA segment representation, so layout stability matters. Dependencies are minimal Linux types. Risks are macro misuse with unexpected integer widths and ABI drift in the SGE structure. Test through compile coverage and DMA command format validation.
