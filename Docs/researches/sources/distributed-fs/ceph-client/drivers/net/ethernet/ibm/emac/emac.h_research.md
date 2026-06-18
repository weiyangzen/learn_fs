
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/emac.h

## Purpose
`emac.h` defines the IBM PowerPC 4xx EMAC hardware register layout and bitfields used by `core.c`. It covers common EMAC registers plus EMAC4 and EMAC4SYNC layout variants, mode registers, RX/TX controls, interrupt bits, MDIO/STACR fields, FIFO threshold helpers, and descriptor status bits.

## Important APIs, Types, and Functions
`struct emac_regs` maps the MMIO register block with unions for EMAC4 and EMAC4SYNC differences. Important bit groups include `EMAC_MR0_*` for reset/TX/RX enable/idleness, `EMAC_MR1_*` and `EMAC4_MR1_*` for duplex, flow control, speed, FIFO size, jumbo, and OPB clock control, `EMAC_RMR_*` for receive filtering, `EMAC_ISR_*`/`EMAC4_ISR_*` for interrupt/error status, `EMAC_STACR_*`/`EMACX_STACR_*` for MDIO access, and `EMAC_TX_*`/`EMAC_RX_*` descriptor status masks. Macros `EMAC_TMR1()`, `EMAC4_TMR1()`, `EMAC4_MR1_OBCI()`, and `EMAC_STACR_OPBC()` encode timing/frequency fields.

## Control Flow
The header has no function control flow. `core.c` uses these definitions during reset, configuration, MDIO transactions, multicast filtering, TX descriptor creation/reclamation, RX descriptor validation, and interrupt accounting.

## State and Persistence
The state represented here is hardware state in EMAC registers and MAL descriptor control words. The C struct layout must match the device’s big-endian MMIO layout; accesses are made with `in_be32()`/`out_be32()` by callers. There is no persistent state.

## Dependencies and Integration Points
It includes Linux types and PHY interface definitions. It is tightly coupled to device-tree compatible strings handled in `core.c` because those determine whether EMAC4/EMAC4SYNC register unions and bit interpretations are used.

## Risks
Register-layout drift or wrong compatible matching can point callers at the wrong union member. Many macros encode hardware-specific constants with little type checking. Descriptor error masks directly affect packet drop/error accounting and checksum behavior, especially when TAH is present.

## Test Signals
Hardware bring-up, `ethtool -d` register dumps, MDIO read/write success, interrupt counter increments for injected errors, multicast filter behavior, and jumbo-speed configuration all validate this header indirectly. Cross-building for EMAC4 and EMAC4SYNC variants catches missing field references.
