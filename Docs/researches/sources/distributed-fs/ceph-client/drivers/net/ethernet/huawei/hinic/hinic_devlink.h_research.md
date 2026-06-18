# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_devlink.h

Defines firmware image constants, section enums, required-section masks, image/header structures, and devlink/health reporter prototypes for HiNIC. Key constants include `HINIC_MAGIC_NUM`, `UPDATEFW_IMAGE_HEAD_SIZE`, `MAX_FW_FRAGMENT_LEN`, and cold/hot update flags.

There is no runtime control flow. `enum hinic_fw_type`, `struct fw_image_st`, and `struct host_image_st` are consumed by firmware validation/flashing. Dependencies are devlink and `hinic_dev.h`. Risks are firmware ABI layout drift and bitmask overflow if section enum values change. Test image validation masks and devlink lifecycle builds.
