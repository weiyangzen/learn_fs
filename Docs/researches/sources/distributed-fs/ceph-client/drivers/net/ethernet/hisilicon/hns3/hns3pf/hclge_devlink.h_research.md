# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_devlink.h

## Purpose

`hclge_devlink.h` declares the HNS3 PF devlink integration points and private devlink storage. It is a small bridge between `hclge_main.c` and `hclge_devlink.c`.

## Important API And Types

`HCLGE_DEVLINK_FW_SCC_LEN` sizes the SCC firmware version string buffer. `struct hclge_devlink_priv` stores the owning `struct hclge_dev *`. The exported functions are `int hclge_devlink_init(struct hclge_dev *hdev)` and `void hclge_devlink_uninit(struct hclge_dev *hdev)`.

## Control Flow And State

The header has no runtime control flow. Its private structure is allocated inside devlink private memory and used by devlink callbacks to recover the PF device pointer.

## Dependencies And Integration Points

It includes `hclge_main.h` for `struct hclge_dev`. `hclge_main.c` calls the declared functions during probe/remove, and devlink callbacks in `hclge_devlink.c` use the private structure.

## Risks

The header assumes devlink support is available through the broader build context. Any change to private data must stay synchronized with `devlink_alloc()` sizing in `hclge_devlink.c`.

## Test Signals

Build the PF driver with devlink enabled, verify probe allocates/registers devlink, remove unregisters/frees it, and devlink callbacks can safely dereference `priv->hdev`.
