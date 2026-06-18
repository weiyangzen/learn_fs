# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/farch_regs.h

## Purpose
`farch_regs.h` is the Falcon/Siena hardware register, table, descriptor, and event bitfield catalogue used by the Solarflare `sfc/falcon` driver. It contains no executable logic; instead it defines the address offsets, row counts, strides, bit low-bit numbers, widths, and enumerated values consumed by register accessor and datapath code. The naming scheme encodes the hardware family and revision applicability, for example `FR_AZ_*` for register addresses, `FRF_*` for register fields, `FSF_*` for host-memory/event descriptor fields, and `FSE`/`FFE` for enumerators.

## Important APIs, Types, And Definitions
The major register groups cover PCI/BIU initialization and interrupts (`FR_AZ_INT_EN_KER`, `FR_AZ_INT_ADR_KER`, `FR_AZ_FATAL_INTR_KER`), SPI/VPD access (`FR_AB_EE_SPI_*`, `FR_AB_EE_VPD_*`), reset and GPIO control (`FR_AB_GLB_CTL`, `FR_AB_GPIO_CTL`), event queues and timers (`FR_BZ_EVQ_RPTR*`, `FR_AZ_EVQ_CTL`, `FR_BZ_TIMER_TBL`), RX/TX datapath setup (`FR_AZ_RX_CFG`, `FR_AZ_TX_CFG`, descriptor update registers, descriptor pointer tables), buffer table entries (`FR_BZ_BUF_FULL_TBL`, `FR_BZ_BUF_HALF_TBL`), hardware filters (`FR_BZ_RX_FILTER_TBL0`, `FR_CZ_RX_MAC_FILTER_TBL0`, `FR_CZ_TX_FILTER_TBL0`, `FR_CZ_TX_MAC_FILTER_TBL0`), MAC/PHY management (`FR_AB_MD_*`, `FR_AB_MAC_CTRL`, GMAC/XGMAC/XAUI blocks), MSI-X tables, and event/descriptor layouts (`EVENT_ENTRY`, `RX_EV`, `TX_EV`, `RX_KER_DESC`, `TX_KER_DESC`, user descriptors).

Several pseudo-fields make raw hardware definitions safer or more convenient for C code: descriptor-update dword addresses use `BUILD_BUG_ON_ZERO` to ensure Falcon A/B aliases stay equal, split 48-bit MAC filter fields are exposed as low/high 32-bit pieces, combined frame-size fields abstract low/high hardware splits, and all-lane XAUI status aliases combine per-lane fields.

## Control Flow
There is no runtime control flow in this header. It supports control flow elsewhere by giving common code stable constants for register tests, register dumps, queue setup, interrupt handling, filter programming, MDIO transactions, and event decoding. Revision suffixes are critical control inputs: callers such as register dump code select entries based on `efx->type->revision` and must not use fields outside their hardware range.

## State And Persistence
The file defines persistent hardware state locations rather than driver-owned state. Writes to these addresses affect NIC configuration, DMA queue state, event queue pointers, SRAM buffer tables, MAC state, PHY-management transactions, VPD/SPI contents, and filter tables. Descriptor and event field definitions describe persistent DMA memory contracts between host and NIC.

## Dependencies And Integration Points
This header is included by Falcon architecture code such as `nic.c`, low-level queue/event/filter implementations, MAC/PHY code, and register self-tests. It depends on the bitfield helper layer for constructing and extracting fields by `_LBN` and `_WIDTH` pairs. Its constants also integrate with Linux ethtool register dumps, interrupt setup, MTD/SPI support, MDIO management, RSS, RFS, and network queue programming.

## Risks
The primary risk is silent hardware corruption from incorrect offsets or field widths: many registers are wide, revision-specific, write-only, read-clear, or table-mapped. Misusing A/B/C revision constants can read undefined state or write an incompatible control bit. Descriptor-update aliases and pseudo-fields are especially sensitive because they encode hardware workarounds. Register dumps must avoid write-only and read-clear registers; this file documents many such cases through names and comments but relies on callers to honor them.

## Test Signals
Useful validation comes from register self-tests, ethtool register dumps, interrupt tests, queue flush tests, RX/TX datapath traffic, RSS/filter tests, MDIO read/write tests, and MAC statistic DMA checks. Compile-time validation through `BUILD_BUG_ON_ZERO` catches some descriptor alias assumptions, while runtime failures typically appear as timeout, interrupt, queue ownership, RX/TX checksum, filter miss, or MAC link faults.
