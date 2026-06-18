# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/reg.h

Purpose: Defines the RTL8192D register map, firmware/EEPROM offsets, bit masks, rate constants, interrupt masks, CAM constants, BB/RF register addresses, and helper macros used throughout the driver.

Important APIs/types: Major groups cover system configuration (`REG_SYS_*`, `REG_APS_FSMCO`, `REG_MCUFWDL`), MACTOP/firmware mailboxes, TX/RX DMA, PCIe DBI/descriptors, protocol/rate/aggregation, EDCA/beacon/TSF, WMAC/RCR/security, efuse/EEPROM layout, RCR/SECCFG/power bits, LLT operation fields, rate bitmaps, interrupt masks, TXAGC/IQK registers, and RF6052 register addresses. Helper macros pack LLT fields and define masks like `BLSSIREADBACKDATA`, `RF_CHNLBW`, `RF_T_METER`.

Control flow: No executable flow, but constants drive all control sequences in firmware download, MAC init, LLT init, RF power, rate control, beacon handling, descriptor setup, key programming, and calibration.

State and persistence: Represents hardware and efuse address contracts. EEPROM/efuse offsets describe persistent device calibration and identity storage; runtime registers describe volatile device state.

Dependencies and integration: Included by almost every rtl8192d/rtl8192de source file. Relies on kernel `BIT`, `BIT0`, `BIT1`, `GENMASK`, and rtlwifi rate/queue conventions.

Risks: Mistyped values directly corrupt hardware sequencing. Some definitions are compatibility aliases for 8192C naming and some use raw numeric offsets later in C files, so consistency matters. EEPROM offsets and default power constants are critical for regulatory TX power. Interrupt masks reuse names across normal/extended status bits.

Test signals: Build coverage, hardware init traces, efuse reads, firmware mailbox operation, interrupt handling, RF calibration, TX power table programming, and descriptor/rate behavior.
