# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3vf/hclgevf_devlink.h

## Purpose
`hclgevf_devlink.h` declares the VF devlink integration interface and private devlink storage for the HNS3 VF driver.

## Important APIs And Types
- `struct hclgevf_devlink_priv` holds the `struct hclgevf_dev *hdev` back pointer retrievable through `devlink_priv()`.
- `hclgevf_devlink_init(struct hclgevf_dev *hdev)` allocates/registers devlink state for a VF.
- `hclgevf_devlink_uninit(struct hclgevf_dev *hdev)` unregisters/frees devlink state.

## State, Dependencies, And Integration
The header includes `hclgevf_main.h` so it has the full VF device type. It is used by VF probe/remove code and by `hclgevf_devlink.c`. The private structure links devlink callbacks back to VF runtime state and cached firmware version.

## Risks And Test Signals
The header creates a direct include dependency on VF main definitions; include cycles or changing `struct hclgevf_dev` visibility could affect build ordering. Runtime validation should cover successful devlink init/uninit, probe allocation failure, and devlink callbacks using the expected private pointer.
