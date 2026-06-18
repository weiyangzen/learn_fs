# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/suni1x10gexp_regs.h

## Purpose
`suni1x10gexp_regs.h` is a register and bit-mask map for the PMC/Sierra S/UNI-1x10GE-XP PM3393 MAC/PHY used by the Chelsio `cxgb` driver. It provides symbolic addresses and masks for global reset/status, MDIO, 10G RX/TX MAC blocks, XAUI, OAM, PL4/SPI4 interfaces, FIFO provisioning, performance counters, and interrupt/status bits.

## Important APIs, Types, And Functions
This file contains macros only. Key macro groups include:
- Offset helpers for exact match filters, VLAN filters, and MSTAT counters: `mSUNI1x10GEXP_MAC_FILTER_OFFSET`, `mSUNI1x10GEXP_MAC_VID_FILTER_OFFSET`, and `mSUNI1x10GEXP_MSTAT_COUNT_OFFSET`.
- Register address constants from top-level device registers (`IDENTIFICATION`, `CONFIG_AND_RESET_CONTROL`, `MASTER_INTERRUPT_STATUS`, `GLOBAL_INTERRUPT_ENABLE`) through SERDES, RXXG/XRF/RXOAM/MSTAT/IFLX/PL4/TXXG/XTEF/TXOAM/EFLX/PL4IDU blocks.
- Dynamic register address macros for exact match address/VID registers and MSTAT counters.
- Bit-mask helpers for fixed-width fields, clearing high bits, and testing bits.
- Detailed bit masks and bit offsets for reset, loopback, device status, MDIO command/address fields, master interrupt causes, XAUI/SERDES events, RX/TX MAC controls, OAM controls, PL4 lock/error conditions, FIFO limits, and counter control.

## Control Flow And State
There is no executable control flow. The file models PM3393 state by naming hardware registers and fields. Driver code using it typically reads/writes these addresses over TPI/MDIO-like external register paths, updates MSTAT snapshots, programs MAC address filters, enables/disables RX/TX paths, and handles block-specific interrupt causes.

## Dependencies And Integration Points
It is consumed by PM3393-related MAC support in the `cxgb` tree. The names align with the vendor datasheet and allow other driver code to avoid magic offsets. Register groups map to integration points with Elmer0/TPI access, the MAC receive/transmit path, address filtering, XAUI link detection, SPI4/PL4 datapath setup, and MSTAT statistics.

## Risks And Edge Cases
The file is dense and vendor-derived, so the primary risks are incorrect offsets, stale datasheet assumptions, or confusing similarly named interrupt enable/status/visibility registers. Some macros expose raw bit masks without typed helpers, so callers must apply shifts consistently. Dynamic macros assume valid filter/counter IDs; bounds are not enforced by the preprocessor.

## Test Signals
Validation comes indirectly from PM3393 driver behavior: reset/status reads returning expected IDs, MAC address filters accepting/rejecting traffic as configured, RX/TX enable and MTU changes taking effect, MSTAT counters matching traffic, and block interrupt status bits matching link/fault events. Static build coverage should catch missing macro names but not semantic address mistakes.
