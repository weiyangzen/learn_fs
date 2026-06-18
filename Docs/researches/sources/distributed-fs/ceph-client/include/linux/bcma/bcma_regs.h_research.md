# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_regs.h

## Purpose
Defines common BCMA registers shared across cores, agent reset/control/status bits, PCI config-space registers, and SoC backplane address map constants.

## Important APIs, types, and functions
- `BCMA_CLKCTLST` and clock status/request bits are shared by ChipCommon, PCIe, and 80211 cores.
- Agent registers include OOB select, `BCMA_IOCTL`, `BCMA_IOST`, `BCMA_RESET_CTL`, and `BCMA_RESET_ST`.
- NS ROM boot-device bits describe NOR/NAND/ROM boot source.
- PCI config-space constants cover BAR windows, SPROM control, IRQs, GPIO, and PCIe2 BAR window.
- SoC address constants define SDRAM, PCI memory/config, swapped SDRAM, and region 2 mappings.

## Control flow and state
BCMA core management helpers use these constants to request clocks, force/reset cores, check BIST/status, map BAR windows, and interpret boot devices.

## State and persistence behavior
All fields map hardware registers or fixed SoC physical address regions. Writes alter live core, reset, clock, GPIO, or PCI window state.

## Dependencies and integration points
Included by `bcma.h` and driver-specific BCMA code. Used by core enable/disable, clock mode, PCI host mapping, and SoC boot logic.

## Risks
Some chips invert ALP/HT status bits, and comments call out BCM4328A0 reversal. Reset and IO-control bits are shared primitives and must be sequenced carefully. Address-map constants are platform-specific.

## Test signals
Check core reset/enable flows, clock status polling, PCI BAR window programming, boot-device detection, and chip-specific clock status quirks.
