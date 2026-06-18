# sources/distributed-fs/ceph-client/drivers/watchdog/sp5100_tco.h

## Purpose
`sp5100_tco.h` is the private register-definition header for the AMD SP5100/SB800/EFCH TCO watchdog driver. It centralizes MMIO register offsets, control bits, PM I/O ports, chipset-specific PM register indexes, hardcoded EFCH addresses, and revision threshold constants.

## Important APIs, types, and functions
The header defines no functions or types. Key macros include `SP5100_WDT_CONTROL(base)`, `SP5100_WDT_COUNT(base)`, `SP5100_WDT_START_STOP_BIT`, `SP5100_WDT_FIRED`, `SP5100_WDT_ACTION_RESET`, `SP5100_WDT_DISABLED`, and `SP5100_WDT_TRIGGER_BIT`. It also defines PM register names for SP5100, SB800, and EFCH layouts and `AMD_ZEN_SMBUS_PCI_REV`.

## Control flow
There is no executable control flow. `sp5100_tco.c` uses these constants to classify the chipset, read the PM watchdog base registers, enable decode and one-second resolution, map MMIO, and manipulate the common control/count watchdog registers.

## State and persistence behavior
The header stores no state. Its constants describe hardware state fields that persist in chipset PM and watchdog registers.

## Dependencies and integration points
It includes `<linux/bitops.h>` for `BIT()` and `GENMASK()` and is private to `sp5100_tco.c`. The macro values encode externally documented AMD/ATI register contracts.

## Risks and test signals
The main risk is incorrect magic values: a wrong address, mask, or revision threshold will make setup fail or program unrelated chipset state. Test by compiling the driver, checking macro use against datasheets for each layout, and validating detected MMIO/PM register traces on SP5100, SB800, EFCH, and Zen EFCH-MMIO systems.
