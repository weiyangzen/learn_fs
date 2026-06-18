<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_reg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_reg.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_reg.h` is a small register-include placeholder for the RTL8723B PHY layer, preserving the include boundary expected by the Realtek driver. The source was reviewed as a complete 17-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: Only the include guard `__INC_HAL8723BPHYREG_H__` is defined in this snapshot.

## Control Flow

There is no control flow. The file exists so code can include a stable PHY-register header even when register definitions are supplied elsewhere.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

Included by PHY-related implementation files that expect a chip register namespace. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Low direct risk, but moving or deleting it can break include compatibility with copied vendor code.

## Test Signals

Compile coverage of all rtl8723bs PHY objects and include-order checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_phy_reg.h -->
