# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/reg.h

Purpose: `reg.h` is the RTL8723AE register and bitfield map. It names MAC, PCIe, USB, EFUSE, CAM, interrupt, beacon, DMA, PHY, BB, RF, rate, power, and security registers and masks used throughout the driver.

Important APIs/data: definitions include register offsets (`REG_SYS_FUNC_EN`, `REG_CR`, `REG_RCR`, `REG_PCIE_CTRL_REG`, `REG_BCN_CTRL`, `REG_CAMCMD`, `REG_SECCFG`, `RFPGA0_RFMOD`, `RTXAGC_*`, `RF_CHNLBW`), alias names (`MSR`, `ISR`, `TSFR`), rate bitmaps (`RATR_*`, `RATE_*`, `RATE_ALL_*`), interrupt masks (`IMR_*`, `PHIMR_*`), EFUSE size/default/offset constants, receive-config bits (`RCR_*`), security CAM/SCR bits, LLT helpers, power/clock/function bits, BB/RF masks, and common masks such as `MASKDWORD`, `MASKBYTE*`, and `RFREG_OFFSET_MASK`.

Control flow: no code executes here. Control-flow impact is indirect: `hw.c`, `phy.c`, `rf.c`, `trx.c`, `led.c`, `sw.c`, and power-sequence macros use these constants to decide which hardware bits to read, write, poll, or preserve.

State and persistence: the header defines symbolic addresses for persistent device register state. It does not store driver state. Values written through these definitions persist in hardware until reset or subsequent writes.

Dependencies/integration: included by nearly every RTL8723AE source file. `sw.c` maps many constants into the generic `rtl_hal_cfg.maps` table so common rtlwifi code can access chip-specific addresses and bit encodings.

Risks: duplicated definitions appear for some USB registers and defaults, and several names are inherited from older 8192/92S/92C code. Incorrect constants can produce silent hardware misprogramming. The file mixes PCIe-specific and USB/SDIO definitions, so maintainers must watch interface masks and call sites. Magic values in source files often rely on these symbolic definitions being exact.

Test signals: compile coverage catches missing names but not incorrect values. Runtime signals include successful EFUSE reads, firmware download, MAC/BB/RF init, interrupt delivery, RX/TX descriptors, CAM encryption, beacon timing, RF power transitions, and stable tx power/rate behavior.
