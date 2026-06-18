# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/Kconfig

## Purpose
This Kconfig file defines the kernel configuration switches for Airoha Ethernet support. It introduces the vendor menu, the NPU support module, the main SoC Gigabit Ethernet driver, and optional flow-statistics support.

## Important APIs, Types, and Symbols
`NET_VENDOR_AIROHA` gates the vendor menu and depends on `ARCH_AIROHA || COMPILE_TEST`. `NET_AIROHA_NPU` is tristate NPU support and selects `WANT_DEV_COREDUMP` plus `REGMAP_MMIO`. `NET_AIROHA` is tristate SoC Gigabit Ethernet support, selects `NET_AIROHA_NPU` and `PAGE_POOL`, and has an effectively always-true `NET_DSA || !NET_DSA` dependency. `NET_AIROHA_FLOW_STATS` is a default-y bool gated by `NET_AIROHA && NET_AIROHA_NPU`.

## Control Flow
The selected symbols drive the sibling Makefile. `NET_AIROHA` builds the composite Ethernet object and forces NPU support. `NET_AIROHA_NPU` builds the NPU object. `NET_AIROHA_FLOW_STATS` enables optional flowtable statistics in the broader Airoha driver set.

## State and Persistence Behavior
The file has no runtime state. The selected values persist in `.config` and determine whether the driver is built in, modular, or omitted, and whether page-pool, NPU, and stats code paths are available.

## Dependencies and Integration Points
The file integrates Airoha Ethernet into the Linux networking driver tree. `ARCH_AIROHA` is the native platform dependency, while `COMPILE_TEST` broadens build coverage. `PAGE_POOL` is required by `airoha_eth.c` RX buffer management. `REGMAP_MMIO` and `WANT_DEV_COREDUMP` support the NPU side.

## Risks and Edge Cases
`depends on NET_DSA || !NET_DSA` is tautological and may confuse readers, although the implementation handles DSA conditionally. Because `NET_AIROHA` selects `NET_AIROHA_NPU`, NPU build or probe assumptions can affect Ethernet users. `NET_AIROHA_FLOW_STATS` defaults on whenever dependencies are met, so stats code must stay robust and inexpensive.

## Test Signals
Build combinations should include `NET_AIROHA=m/y`, `NET_AIROHA_NPU=m/y`, `CONFIG_NET_DSA=y/n`, `CONFIG_DEBUG_FS=y/n`, and `COMPILE_TEST=y` on non-Airoha architectures. Runtime signals are module/object availability matching selected tristates.
