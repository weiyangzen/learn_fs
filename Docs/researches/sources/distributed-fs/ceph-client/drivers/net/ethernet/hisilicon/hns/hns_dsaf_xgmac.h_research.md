# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_xgmac.h

## Purpose

`hns_dsaf_xgmac.h` is the small public constant header for the XGMAC backend. It defines the ethtool register dump length and the LF/RF insert mode values used when enabling or disabling the XGMAC port.

## Important APIs, Types, And Functions

The header defines `HNS_XGMAC_DUMP_NUM` as 214, `HNS_XGMAC_NO_LF_RF_INSERT` as `0x0`, and `HNS_XGMAC_LF_INSERT` as `0x2`. It declares no structs or functions.

## Control Flow

The header has no executable control flow. `hns_dsaf_xgmac.c` uses the LF/RF constants in its enable/disable callbacks and uses `HNS_XGMAC_DUMP_NUM` in `hns_xgmac_get_regs_count`.

## State And Persistence

There is no runtime state in the header. Its constants constrain register dump buffer sizing and XGMAC link-fault signaling behavior.

## Dependencies And Integration Points

This header is included by the XGMAC implementation. The values must stay synchronized with the XGMAC register definitions in `hns_dsaf_reg.h` and with ethtool register dump consumers.

## Risks And Test Signals

Risks are limited but important: a wrong dump count can cause truncated or overrun register dumps, and a wrong LF insert code can affect link-fault signaling during MAC disable. Test signals include correct `ethtool -d` length and expected LF behavior when the port is administratively disabled.
