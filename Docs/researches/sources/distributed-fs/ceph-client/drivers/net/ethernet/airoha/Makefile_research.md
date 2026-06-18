# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/Makefile

## Purpose
This Makefile maps the Airoha Kconfig symbols to kernel objects. It builds the Ethernet driver from the main data-path and PPE sources, optionally adds debugfs support, and builds the NPU support object.

## Important APIs, Types, and Targets
`obj-$(CONFIG_NET_AIROHA) += airoha-eth.o` builds the main composite Ethernet object. `airoha-eth-y := airoha_eth.o airoha_ppe.o` links the core Ethernet/platform/QDMA implementation with PPE support. `airoha-eth-$(CONFIG_DEBUG_FS) += airoha_ppe_debugfs.o` adds debugfs-only PPE code. `obj-$(CONFIG_NET_AIROHA_NPU) += airoha_npu.o` builds NPU support.

## Control Flow
Kbuild expands these variables from `.config`. The main driver always includes both `airoha_eth.o` and `airoha_ppe.o` when `NET_AIROHA` is selected. Debugfs code is conditionally linked.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is the configured kernel build graph and final module/object composition.

## Dependencies and Integration Points
It depends on sibling Kconfig symbols and Linux Kbuild. `airoha_eth.o` calls PPE helpers, so the composite object keeps those references together. `airoha_ppe_debugfs.o` is a conditional extension rather than a standalone module.

## Risks and Edge Cases
The directory comment mentions "Mediatek SoCs built-in ethernet macs", which appears stale for the Airoha directory. Since PPE is always linked into the main Ethernet object, PPE build breakage breaks Ethernet. Debugfs-only code needs build coverage because it is omitted in many configs.

## Test Signals
Run `make M=drivers/net/ethernet/airoha` with `NET_AIROHA=m/y`, `NET_AIROHA_NPU=m/y`, and `CONFIG_DEBUG_FS=y/n`. Inspect module contents to confirm `airoha-eth` includes `airoha_eth.o` and `airoha_ppe.o`, with debugfs symbols only when enabled.
