# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/reg.h

## Purpose
This header is the shared register map for the rtw88 Realtek wireless driver family. It gives the rest of the driver symbolic names for MAC, system, DMA, beacon, EDCA, RX/TX, baseband, RF, firmware mailbox, coexistence, USB, and LTE-coexistence registers, plus bit masks and field constructors used by chip-specific code such as `rtw8703b.c`, `rtw8723d.c`, common MAC/PHY helpers, firmware download, efuse access, coexistence, and bus glue.

## Important APIs, Types, And Functions
The file is macro-only; its API is the collection of `REG_*`, `BIT_*`, `BITS_*`, `MASK*`, and field helper definitions. Major areas include power and firmware boot registers (`REG_SYS_FUNC_EN`, `REG_SYS_PW_CTRL`, `REG_MCUFW_CTRL`, `FW_READY`, `FW_READY_LEGACY`), efuse access (`REG_EFUSE_CTRL`, `REG_EFUSE_ACCESS`, efuse address/data masks), DMA and queue layout (`REG_RQPN`, `REG_RQPN_NPQ`, `REG_AUTO_LLT`, `REG_TXDMA_PQ_MAP`, `REG_RXDMA_MODE`), MAC timing/filter registers (`REG_CR`, `REG_RCR`, `REG_BCN_CTRL`, `REG_TBTT_PROHIBIT`, `REG_EDCA_*`, `REG_RXFLTMAP*`), RF/baseband control (`REG_FPGA0_RFMOD`, `REG_OFDM*`, `REG_CCK*`, `REG_IQK_*`, `RF_*`), coexistence (`REG_BT_COEX_*`, `LTE_COEX_*`), and USB PHY controls.

Several field macros wrap common packed register fields, for example `BIT_RQPN_HLP()`, `BIT_TXDMA_*_MAP()`, `BIT_RXPSF_*`, `BIT_SET_RXPSF_*`, and RF channel masks. These are consumed by read/modify/write helpers throughout rtw88 rather than being invoked as functions.

## Control Flow
There is no runtime control flow in this header. The control-flow effect is indirect: chip code includes it to drive register programming sequences, calibration routines, firmware readiness polling, DMA queue setup, RX filter setup, and coexistence state changes. The same numeric register can have chip-generation aliases in this file, so call sites decide which definition applies based on the chip info and operation callbacks.

## State And Persistence
The macros name hardware state rather than storing driver state. Writes to these registers persist in device hardware until reset, power transition, firmware restart, or later driver reprogramming. The most sensitive persistent domains are power/clock enable bits, firmware download status bits, LLT/FIFO page allocation, RX/TX enable and filter bits, baseband/RF calibration state, and coexistence grants. Because the header is shared, incorrect masks or aliases can corrupt state across many chip families.

## Dependencies And Integration Points
The header depends on Linux bit helpers such as `BIT()`, `GENMASK()`, and common mask constants visible through included driver headers. It integrates with nearly every rtw88 subsystem: `mac.c` for MAC enable/filter/timing, `fw.c` for mailbox and firmware status, `phy.c` for BB/RF and calibration, `coex.c` for Bluetooth/LTE coexistence, bus backends for USB/SDIO/PCI power and interrupt details, and chip files that pass register constants into generic helper APIs.

## Risks
The main risks are silent hardware misprogramming from wrong offsets, duplicate aliases, masks that do not match a specific chip generation, or field helpers used with values outside the intended width. Many names cover undocumented vendor-derived registers, so maintainers rely on empirical behavior and neighboring chip support. Shared definitions also make refactors risky: a change intended for one chip can affect firmware download, power sequencing, RX filters, calibration, or coexistence on another.

## Test Signals
Useful signals are successful firmware download and `FW_READY` polling, stable power on/off and low-power transitions, correct efuse reads, working TX/RX after MAC enable, valid channel changes, calibration completion, RX PHY status reporting, beacon operation, coexistence debug output, and no register-access warnings across PCI/USB/SDIO variants. Regression tests should include devices from more than one rtw88 generation because this header is broad and shared.
