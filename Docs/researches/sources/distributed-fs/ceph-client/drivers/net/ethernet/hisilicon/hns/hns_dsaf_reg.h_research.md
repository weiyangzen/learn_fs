# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_reg.h

## Purpose

`hns_dsaf_reg.h` is the central register-map and MMIO helper header for the HNS DSAF, PPE, RCB, GMAC, and XGMAC blocks. It names topology limits, register offsets, bit fields, masks, and small inline helpers used throughout the Hisilicon HNS driver.

## Important APIs, Types, And Functions

The file groups definitions for DSAF topology (`DSAF_MAX_PORT_NUM`, `DSAF_SERVICE_NW_NUM`, `DSAF_TOTAL_QUEUE_NUM`, TCAM/line counts), subsystem clock/reset/status registers, SerDes/HILINK registers, DSAF core SRAM/config/interrupt/stat registers, inode/SBM/XOD/VOQ/table registers, PPE common/channel/RSS registers, RCB common/ring registers, GMAC registers, XGMAC registers and 64-bit stat offsets, and bit-field masks for DSAF, PPE, RCB, GMAC, and XGMAC controls.

The helper API consists of `dsaf_write_reg`, `dsaf_read_reg`, `dsaf_write_syscon`, `dsaf_read_syscon`, `dsaf_set_reg_field`, `dsaf_get_reg_field`, `dsaf_write_b`, `dsaf_read_b`, `hns_mac_reg_read64`, and macros such as `dsaf_write_dev`, `dsaf_read_dev`, `dsaf_set_field`, `dsaf_set_bit`, `dsaf_get_field`, `dsaf_get_bit`, `dsaf_set_dev_field`, `dsaf_set_dev_bit`, `dsaf_get_dev_field`, and `dsaf_get_dev_bit`.

## Control Flow

This header is mostly declarative, but its inline helpers define the common read-modify-write pattern for register fields. Callers pass a control block with `io_base`; `dsaf_*_dev` macros offset into that base. Field macros mask and shift values consistently before writeback. The `hns_mac_reg_read64` macro reads XGMAC 64-bit MIB counters from the MAC stats region.

## State And Persistence

The file itself holds no runtime state. Its constants define how runtime state is persisted in device registers. Because many register values control reset, clock, interrupt masks, descriptor bases, queues, MAC enablement, pause, counters, and table entries, correctness of these constants directly governs hardware behavior and diagnostics.

## Dependencies And Integration Points

It includes `<linux/regmap.h>` for syscon access and is consumed by DSAF main, PPE, RCB, GMAC, and XGMAC implementation files. It provides the shared ABI between driver code and hardware manuals, and it underpins ethtool register dumps produced by several blocks.

## Risks And Test Signals

Risks are high because a wrong offset, mask, or shift can silently program unrelated hardware state. Special attention is needed around v1/v2 alternate registers, 64-bit `1ULL` masks narrowed into 32-bit registers, register dump array sizes, and read-modify-write races when hardware also updates bits. Test signals include successful probe/reset on each supported SoC revision, accurate ethtool register dumps, no unexpected interrupt storms, valid RSS/RCB/PPE/XGMAC behavior, and hardware manual review for every changed offset or bit field.
