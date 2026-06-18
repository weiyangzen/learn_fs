# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_regs.h

## Purpose
This header names the TN40xx MMIO register map and bit fields used by the TN40 driver. It covers FIFO configuration/read/write pointers, interrupt registers, firmware initialization registers, MAC/VLAN/multicast registers, MDIO registers, reset controls, RX filter bits, frame-size fields, and PLL lock/reset bits.

## Important APIs, Types, and Functions
The file exports constants only. Important groups are `TN40_REG_TXD_*`, `TN40_REG_RXF_*`, `TN40_REG_RXD_*`, `TN40_REG_TXF_*`, `TN40_REG_ISR/IMR/ISR_MSK0`, `TN40_REG_INIT_SEMAPHORE`, `TN40_REG_INIT_STATUS`, `TN40_REG_MDIO_*`, `TN40_REG_CTRLST`, `TN40_REG_RST_*`, `TN40_REG_DIS_*`, interrupt bits such as `TN40_IR_RX_DESC_0` and `TN40_IR_TX_FREE_0`, RX filter bits such as `TN40_GMAC_RX_FILTER_*`, and helpers `TN40_GET_MDIO_BUSY`/`TN40_GET_MDIO_RD_ERR`.

## Control Flow and State
There is no direct control flow. The constants define how `tn40.c` persists hardware state: FIFO base addresses, cached software pointers, hardware pointer registers, interrupt masks/status, MAC filters, VLAN tables, reset state, MDIO transactions, and PLL lock detection. The combined `TN40_IR_EXTRA` mask controls which non-data-path interrupts receive extra handling.

## Dependencies and Integration Points
This file is included by `tn40.h`, making its constants available to all TN40 module objects. It depends on bitfield macros from Linux headers included before use. It is coupled to magic register programming in `tn40_set_link_speed`, `tn40_hw_start`, and `tn40_sw_reset`, some of which uses raw offsets not named here.

## Risks and Test Signals
Register-map mistakes are severe because they can corrupt hardware state. `TN40_REG_CTRLST_BASE` references `REG_CTRLST_PRM_ENA` instead of `TN40_REG_CTRLST_PRM_ENA`, which is a latent compile risk if the macro is used. Tests should include allmodconfig/randconfig compile coverage, MDIO transaction checks, interrupt mask behavior, reset sequencing, VLAN/multicast programming, and hardware smoke tests for link and traffic.
