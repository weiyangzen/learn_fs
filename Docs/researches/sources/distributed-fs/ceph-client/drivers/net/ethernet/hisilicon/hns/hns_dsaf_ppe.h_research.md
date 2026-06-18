# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_ppe.h

## Purpose

`hns_dsaf_ppe.h` defines the public PPE contract for the HNS DSAF Ethernet driver. It describes PPE topology constants, RSS sizing, dump/stat counts, queue-id and port modes, common block modes, statistics storage, and the control-block layout consumed by `hns_dsaf_ppe.c`, RCB, MAC, and AE integration code.

## Important APIs, Types, And Functions

Important constants include `HNS_PPE_SERVICE_NW_ENGINE_NUM`, `HNS_PPE_DEBUG_NW_ENGINE_NUM`, `HNS_PPE_COM_NUM`, `PPE_COMMON_REG_OFFSET`, `PPE_REG_OFFSET`, `ETH_PPE_DUMP_NUM`, `ETH_PPE_STATIC_NUM`, `HNS_PPEV2_RSS_IND_TBL_SIZE`, `HNS_PPEV2_RSS_KEY_SIZE`, `HNS_PPEV2_RSS_KEY_NUM`, and `HNS_PPEV2_MAX_FRAME_LEN`.

`enum ppe_qid_mode` maps SoC DSAF modes to PPE queue-id interpretation. `enum ppe_port_mode` distinguishes GE and XGE PPE channel modes, while `enum ppe_common_mode` distinguishes debug and service common blocks. `struct hns_ppe_hw_stats` stores cumulative RX/TX PPE counters. `struct hns_ppe_cb` contains the per-channel device pointer, common backpointer, hardware stats, index, MMIO base, IRQ placeholder, RSS indirection shadow, and RSS key shadow. `struct ppe_common_cb` stores the dev/device pointers, common MMIO base, mode, index, channel count, and flexible array of `hns_ppe_cb`.

The prototypes expose PPE initialization, reset, uninitialization, FIFO drain, stats, registers, strings, TSO, RSS key, and RSS indirection programming.

## Control Flow

This header itself contains no executable control flow, but it shapes PPE lifecycle calls. Higher layers allocate a `ppe_common_cb` sized with `struct_size(..., ppe_cb, ppe_num)`, call `hns_ppe_init` during DSAF initialization, use the RSS/TSO setters when netdev or ethtool features change, call stats and register helpers through AE callbacks, and call `hns_ppe_uninit` or `hns_ppe_reset_common` during device teardown or reset.

## State And Persistence

State represented here is entirely in memory and MMIO-backed. The RSS key and indirection table arrays are driver shadows for v2 hardware state. `hns_ppe_hw_stats` persists cumulative counter snapshots for the life of the control block but is lost across driver unload.

## Dependencies And Integration Points

The header includes Linux platform-device types and HNS DSAF headers for `struct dsaf_device`, MAC control blocks, and RCB APIs. It is included by PPE implementation code and by other DSAF code that needs PPE reset, stats, or feature toggles.

## Risks And Test Signals

The main risks are ABI drift between constants and hardware register dump layout, flexible-array allocation mistakes, and mismatched RSS sizing versus ethtool or PPEv2 hardware. Test signals are successful compile-time integration, no out-of-bounds register dump accesses for `ETH_PPE_DUMP_NUM`, valid `ethtool -x/-X` behavior on v2 hardware, and matching stat-string count to `ETH_PPE_STATIC_NUM`.
