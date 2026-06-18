# sources/distributed-fs/ceph-client/drivers/ptp/ptp_idt82p33.h Research

## Purpose
`ptp_idt82p33.h` defines constants, limits, firmware record layout, and private state structures for the IDT 82P33xxx PHC driver.

## Important APIs, Types, And Functions
The header defines firmware name `idt82p33xxx.bin`, PHC/trigger/output limits, ToD byte count, DCO and adjustment thresholds, firmware mask addresses, default masks, write-phase limits and phase resolution. `struct idt82p33_channel` stores PTP caps, PTP clock, parent pointer, PLL mode, adjtime workaround work, current frequency, double-DCO flag, output mask, EXTTS trigger bookkeeping, and register addresses. `struct idt82p33` stores all channels, device, masks, delayed EXTTS work, event routing, shared lock/regmap/MFD, and overhead timing. `struct idt82p33_fwrc` is the packed firmware record.

## Control Flow
The header has no executable flow. Its work structures and fields are used by `ptp_idt82p33.c` to schedule delayed adjustment restoration and EXTTS polling.

## State And Persistence
These structures are the durable software state for each probed chip. Many fields mirror hardware state: PLL masks, output masks, trigger selections, DPLL register addresses, current frequency, and ToD overhead estimate.

## Dependencies And Integration Points
It depends on `linux/mfd/idt82p33_reg.h` for register definitions and on regmap/ktime/PTP clock types. It is private to the 82P33 driver.

## Risks
Hardware limits and default masks in the header shape runtime registration. Incorrect `MAX_*` values can cause out-of-bounds pin/event handling or prevent valid hardware features. Packed firmware record layout must match the binary firmware format exactly.

## Test Signals
Validation includes checking struct initialization for each PLL, firmware record parsing alignment, pin count and channel bounds, phase/frequency threshold behavior, and consistency between header limits and advertised PTP caps.
