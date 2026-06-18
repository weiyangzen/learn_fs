# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/reg.h

## Purpose

`reg.h` is the RTL8821AE/RTL8812AE register and bitfield map. It defines MAC, DMA, PCIe, USB/SIE, beacon, EDCA, security, WoWLAN, power, efuse, BB, OFDM, CCK, RF, TX AGC, IQK, RFE, ODM, and aggregation constants used throughout the local driver. It contains no executable code, but it is the naming layer for the register programming in `phy.c`, `hw.c`, `rf.c`, `dm.c`, `trx.c`, and power sequencing.

## Important Register Groups and Constants

Major MAC groups include system/power registers (`REG_SYS_FUNC_EN`, `REG_APS_FSMCO`, `REG_RF_CTRL`, `REG_MAC_PHY_CTRL`, `REG_MCUFWDL`, `REG_SYS_CFG`), interrupts (`REG_HIMR`, `REG_HISR`, `REG_HSIMR`, `REG_HSISR`, `IMR_*`), DMA and queues (`REG_CR`, `REG_PBP`, `REG_TRXDMA_CTRL`, `REG_RQPN`, `REG_RXDMA_CONTROL`, PCIe descriptor registers), protocol/rate/beacon/EDCA controls, receive filtering/security (`REG_RCR`, `RCR_*`, CAM and `SCR_*` bits), efuse/EEPROM offsets/defaults, and USB/SIE aliases.

PHY/BB/RF groups include RF access registers (`RA_LSSIWRITE_8821A`, `RB_LSSIWRITE_8821A`, `RHSSIREAD_8821AE`, PI/SI readback registers), OFDM/CCK controls (`RRFMOD`, `ROFDMCCKEN`, `RADC_BUF_CLK`, `RCCK_SYSTEM`), TX AGC maps (`RTXAGC_A_*`, `RTXAGC_B_*`), IQK registers, RF path registers (`RF_CHNLBW`, `RF_APK`, `RF_T_METER_8812A`, `RF_WE_LUT`), RFE controls (`RA_RFE_PINMUX`, `RB_RFE_PINMUX`, `RA_RFE_INV`, `RB_RFE_INV`), and ODM helper constants.

## Control Flow

`reg.h` does not execute control flow. Its constants are consumed by initialization, power sequencing, channel/bandwidth switching, TX power programming, efuse parsing, interrupt handling, DMA queue setup, receive filtering, security CAM programming, and dynamic-management logic.

## State and Persistence Behavior

The header defines symbolic names for hardware state. Register state persists in the device until overwritten, reset, or powered down. Efuse/EEPROM offsets describe nonvolatile data; changing them changes how identity, regulatory, and calibration state is interpreted. Bit masks determine partial-register updates, so incorrect masks can corrupt neighboring fields.

## Dependencies and Integration Points

The file depends on kernel bit macros supplied by surrounding includes. It is included by local RTL8821AE implementation files and must stay aligned with vendor tables in `table.h`, power-sequence offsets in `pwrseq.h`, and common `rtlwifi` abstractions for CAM/security, RX filters, interrupts, queues, and rate bitmaps.

## Risks and Edge Cases

- Some constants are duplicated with the same values, including USB register aliases, density values, clock-valid bits, vendor ID, and default legacy HT power diff.
- Several comments and names come from older chip families; applicability to RTL8821AE/RTL8812AE must be verified before reuse.
- Register aliases sharing offsets are context-dependent.
- Bitfield helper macros silently mask/truncate inputs.
- Efuse defaults and offsets are safety-critical for MAC address, regulatory domain, thermal meter, crystal cap, board type, and TX power.
- TX AGC and IQK maps are tightly coupled to `phy.c` switch statements and calibration code.
- Vendor typos in macro names are part of the API and should not be renamed casually.

## Test Signals

Build all RTL8821AE objects after changes. Search all changed names to ensure call sites were updated. On hardware, test probe, firmware download, efuse read, interrupts, DMA queues, scan/association, encryption, WoWLAN/suspend, channel switching, and TX power programming. For mask changes, compare register readback before and after writes to confirm only intended bits changed.
