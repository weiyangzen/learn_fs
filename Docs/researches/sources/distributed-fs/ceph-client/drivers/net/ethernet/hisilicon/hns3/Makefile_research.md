# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/Makefile

## Purpose

The HNS3 `Makefile` defines how the Hisilicon HNS3 Ethernet driver family is compiled under Kbuild. It wires include paths and object composition for the shared HNAE3 framework, the netdev-facing HNS3 driver, PF driver, VF driver, shared command/RSS/TQP-stat code, optional DCB support, devlink, debugfs, PTP, MDIO, mailbox, and error handling components.

## Important APIs, Types, And Functions

This is build metadata, not C API code. It sets `ccflags-y` to include the root HNS3 directory plus `hns3pf`, `hns3vf`, and `hns3_common`. It builds `hnae3.o` under `CONFIG_HNS3`, `hns3.o` under `CONFIG_HNS3_ENET`, `hclgevf.o` and `hclge-common.o` under `CONFIG_HNS3_HCLGEVF`, and `hclge.o` plus `hclge-common.o` under `CONFIG_HNS3_HCLGE`. Optional `CONFIG_HNS3_DCB` adds DCB objects to netdev and PF builds.

## Control Flow

Kbuild evaluates the `obj-*` lines according to kernel configuration. Composite object variables such as `hns3-objs`, `hclge-common-objs`, `hclgevf-objs`, and `hclge-objs` determine link order inside each module or built-in object. Shared `hclge-common` code is linked for both PF and VF configurations.

## State And Persistence

The file persists build relationships only. It does not create runtime state, but it controls which runtime modules and symbols exist in a configured kernel.

## Dependencies And Integration Points

It integrates with Kbuild, HNS3 PF/VF/common source trees, `CONFIG_HNS3`, `CONFIG_HNS3_ENET`, `CONFIG_HNS3_HCLGEVF`, `CONFIG_HNS3_HCLGE`, and `CONFIG_HNS3_DCB`. The include paths allow subdirectory sources to include shared headers without relative include noise.

## Risks And Test Signals

Risks include missing objects when new source files are added, duplicate inclusion of shared common objects, link-order problems for symbol dependencies, and trailing-line formatting around the long `hclge-objs` list. Test signals include all relevant config combinations building as module and built-in, `modpost` without unresolved symbols, and PF/VF modules loading with the expected dependencies.
