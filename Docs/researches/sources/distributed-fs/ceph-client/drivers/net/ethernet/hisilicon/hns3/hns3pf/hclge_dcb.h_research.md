# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_dcb.h

## Purpose

`hclge_dcb.h` is the compile-time gate for HNS3 PF DCB support. It exposes `hclge_dcb_ops_set()` to the main PF driver when `CONFIG_HNS3_DCB` is enabled and provides an empty inline stub otherwise.

## Important API

The only API is `void hclge_dcb_ops_set(struct hclge_dev *hdev)`. With DCB enabled, the implementation in `hclge_dcb.c` installs IEEE DCB and mqprio operations on the PF netdev private info. With DCB disabled, calls compile away through the static inline stub.

## Control Flow And State

The header itself contains no runtime control flow beyond preprocessor selection and no persistent state. Its effect is to keep `hclge_main.c` simple: probe can call `hclge_dcb_ops_set(hdev)` unconditionally while the build configuration determines whether DCB operations are actually attached.

## Dependencies And Integration Points

It includes `hclge_main.h` for `struct hclge_dev`. The integration point is driver initialization in `hclge_main.c`; the operation table installed by the real implementation is later consumed by the HNAE3/netdev DCB path.

## Risks

The main risk is build-configuration divergence. DCB userspace operations silently disappear when `CONFIG_HNS3_DCB` is disabled, so tests must cover both configurations. Because the disabled stub has no logging, feature absence is visible only through missing DCB ops or userspace capability checks.

## Test Signals

Build with `CONFIG_HNS3_DCB=y` and verify DCBNL callbacks are present, then build with it disabled and verify probe still succeeds and DCB operations are absent without unresolved symbols.
