# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/reg.h

## Purpose
This header is the RTL8192CE/RTL8192C register and bit-field map. It names MAC, PCIe, DMA, firmware mailbox, beacon, security CAM, EFUSE, power, GPIO, RF, CCK, OFDM, TXAGC, and PHY diagnostic registers plus the masks used by the driver.

## Important APIs, Types, And Functions
The file provides register offsets such as `REG_SYS_FUNC_EN`, `REG_MCUFWDL`, `REG_LLT_INIT`, descriptor base registers, `REG_BCN_CTRL`, `REG_RCR`, `REG_CAMCMD`, `REG_SECCFG`, and PHY addresses like `RFPGA0_RFMOD`, `ROFDM0_*`, and `RTXAGC_*`. It defines link modes, rate bitmaps, CAM algorithms, interrupt masks, EEPROM offsets/defaults, receive-control bits, power/clock bits, LLT helpers, EDCA/SIFS helpers, RF register addresses, and BB mask constants.

## Control Flow
The header has no executable control flow. Driver code uses these constants to compose register writes in initialization, interrupts, beacon/media changes, TX/RX DMA setup, security CAM updates, EFUSE parsing, RF power transitions, channel/bandwidth changes, TX-power programming, and calibration.

## State And Persistence
No in-memory state is declared. The constants address mutable device hardware state and read-only persistent EFUSE/EEPROM offsets. Values written to registers persist until reset, power transition, or later writes.

## Dependencies And Integration Points
It is included by almost every CE source file and by `rtl8192c/phy_common.c`. It is the shared contract between table data, hardware code, PHY/RF code, and rtlwifi generic helpers.

## Risks And Edge Cases
Incorrect offsets or masks can corrupt unrelated device registers. Several USB-oriented definitions are present in this PCI header because it covers the broader 8192C family; callers must choose interface-appropriate registers. Many masks are magic hardware ABI values and are not type-safe. Duplicate aliases such as `RCR_APPFCS`/`APP_FCS` and overlapping beacon/TSF offsets require careful use.

## Test Signals
Build coverage is necessary but insufficient. Runtime signals include successful init/register programming, descriptor DMA operation, interrupts, EFUSE decode, security CAM operation, channel/bandwidth changes, RF calibration, rate control, and register dumps matching Realtek documentation.
