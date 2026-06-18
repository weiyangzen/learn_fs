
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/Kconfig

## Purpose

This Kconfig file exposes Hisilicon Ethernet driver build options, including older ARM/ARM64 platform MACs, HNS/HNS3 framework drivers, and the PCI-based HIBMCGE BMC Gigabit Ethernet driver.

## Important APIs, Types, and Functions

- `NET_VENDOR_HISILICON` gates the vendor menu and depends on `OF || ACPI`.
- `HIX5HD2_GMAC`, `HISI_FEMAC`, and `HIP04_ETH` enable platform MAC drivers and select required PHY, reset, MFD, and MDIO support.
- `HI13X1_GMAC` is a bool variant depending on `HIP04_ETH`.
- `HNS`, `HNS_MDIO`, `HNS_DSAF`, and `HNS_ENET` configure the HNS framework and first-generation acceleration/enet drivers.
- `HNS3`, `HNS3_HCLGE`, `HNS3_DCB`, `HNS3_HCLGEVF`, and `HNS3_ENET` configure the PCI HNS3 stack.
- `HIBMCGE` enables the BMC GE PCI driver and selects `PHYLIB`, `FIXED_PHY`, Motorcomm/Realtek PHY drivers, and `PAGE_POOL`.

## Control Flow

There is no runtime control flow. Kconfig dependency resolution controls which objects Kbuild compiles and whether related subsystems are selected.

## State and Persistence

State is kernel configuration state in `.config`. Those choices persist into build artifacts and module availability.

## Dependencies and Integration Points

The file integrates Hisilicon Ethernet drivers with PHYLIB, reset controller support, MFD/syscon, HNS MDIO, HNAE/HNS/HNS3 frameworks, PCI/MSI, devlink, DIMLIB, PTP optional support, fixed PHY, and page pool.

## Risks and Edge Cases

Incorrect dependencies can produce unresolved symbols, especially around PCI/MSI, PHY drivers, reset APIs, or page-pool use. Several platform drivers are guarded by `ARM || ARM64 || COMPILE_TEST`, while `HIBMCGE` is outside that block and depends on PCI/MSI only. The `HIP04_ETH` help text and `HNS_DSAF` help contain typos, but they do not affect builds.

## Test Signals

Build matrix signals include `allmodconfig`, `COMPILE_TEST`, `HIBMCGE=m/y`, legacy platform drivers as modules, HNS/HNS3 combinations, and disabled `NET_VENDOR_HISILICON`. Link success and expected module objects are the main validation signals.
