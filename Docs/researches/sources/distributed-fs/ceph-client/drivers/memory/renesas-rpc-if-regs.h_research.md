# sources/distributed-fs/ceph-client/drivers/memory/renesas-rpc-if-regs.h

## Purpose
`renesas-rpc-if-regs.h` defines register offsets and bitfield constructors for the Renesas R-Car/RZ RPC Interface memory controller used by SPI, HyperFlash, and Octa/DDR-capable direct or manual access paths.

## Important APIs, Types, And Functions
The header defines offsets for common control/status (`RPCIF_CMNCR`, `RPCIF_SSLDR`, `RPCIF_CMNSR`), direct-read path registers (`RPCIF_DRCR`, `RPCIF_DRCMR`, `RPCIF_DREAR`, `RPCIF_DROPR`, `RPCIF_DRENR`, `RPCIF_DRDMCR`, `RPCIF_DRDRENR`), manual mode registers (`RPCIF_SMCR`, `RPCIF_SMCMR`, `RPCIF_SMADR`, `RPCIF_SMOPR`, `RPCIF_SMENR`, read/write data registers, `RPCIF_SMDMCR`, `RPCIF_SMDRENR`), and PHY control/status (`RPCIF_PHYADD`, `RPCIF_PHYWR`, `RPCIF_PHYCNT`, `RPCIF_PHYOFFSET1`, `RPCIF_PHYOFFSET2`, `RPCIF_PHYINT`).

Most macros are field constructors, for example command/opcode insertion, bus-width selection, dummy-cycle programming, burst length, PHY memory mode, Octa/DDR/high-speed options, and RZ/G2L-specific clock selection.

## Control Flow
The header has no control flow. It is included by the RPC-IF implementation that performs regmap/MMIO programming.

## State And Persistence
It defines no state. The macros describe hardware register state managed by the consuming driver.

## Dependencies And Integration Points
It depends on `linux/bits.h` for `BIT()` and `GENMASK()`. The corresponding implementation file `renesas-rpc-if.c` uses these definitions for hardware initialization, direct mapping, manual transactions, PHY setup, and PM restore.

## Risks
Field constructors mask inputs but do not validate semantic ranges such as burst length before subtracting one. Some fields are documented as only valid on specific SoCs, so consumers must select macros according to compatible data. Register offset comments reflect availability differences across R-Car and RZ/G2 variants.

## Test Signals
Compile coverage of RPC-IF consumers is the main direct signal. Hardware tests should verify manual read/write transactions, direct-map reads, dummy-cycle programming, PHY calibration bits, Octa/DDR mode setup, and SoC-specific fields on R-Car versus RZ/G2L devices.
