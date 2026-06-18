<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.h

## Purpose
Declares shared RTL8723 firmware control constants, firmware version identifiers, H2C command IDs for RTL8723BE, and firmware helper prototypes.

## Important APIs, Types, And Functions
- Register and status constants: `REG_SYS_FUNC_EN`, `REG_MCUFWDL`, `REG_RSV_CTRL`, `REG_HMETFR`, `FW_8192C_PAGE_SIZE`, `FW_8723A_POLLING_TIMEOUT_COUNT`, `FW_8723B_POLLING_TIMEOUT_COUNT`, `FW_8192C_POLLING_DELAY`, `MCUFWDL_RDY`, `FWDL_CHKSUM_RPT`, and `WINTINI_RDY`.
- `enum version_8723e` distinguishes test/normal UMC and SMIC chip cuts for RTL8723A/B.
- `enum rtl8723be_cmd` names H2C commands for reserved pages, join report, scan, keep-alive, disconnect decision, offloads, power modes, P2P power save, wake-on-WLAN, RSSI report, and rate-adaptive mask.
- Prototypes expose firmware self-reset, download-mode enable, page writing, free-to-go polling, and full firmware download.

## Control Flow
The header has no control flow. It supplies constants and declarations used by firmware command/download implementations.

## State And Persistence
The declared helpers mutate firmware control registers, firmware readiness bits, and device-resident firmware state. H2C command IDs define persistent firmware ABI values.

## Dependencies And Integration Points
Included by RTL8723AE/BE firmware and software registration code. The H2C enum must match firmware expectations, while the register constants must match chip hardware.

## Risks And Edge Cases
Changing command IDs breaks host-to-firmware ABI compatibility. Polling timeout changes can make firmware load flaky or slow. Register bit definitions overlap with chip reset behavior, so incorrect values can leave the MCU stuck.

## Test Signals
Compile coverage, firmware download success, H2C command acceptance for power and rate control, WOWLAN command behavior, and readiness polling within expected timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/fw_common.h -->
