# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_chipcommon.h

## Purpose
Defines the BCMA ChipCommon and ChipCommon-B register map, capability bits, PMU/PLL constants, flash/NAND/GPIO/watchdog support structures, and access helpers.

## Important APIs, types, and functions
- Large register catalog: chip ID/capabilities, OTP/JTAG/flash/GPIO/watchdog/clock/PMU/SPROM/NAND/serial registers and many chip-specific control bits.
- `struct bcma_chipcommon_pmu` stores PMU core, revision, and crystal frequency.
- Optional flash descriptors: `bcma_pflash`, `bcma_sflash`, and `bcma_nflash`.
- Optional `struct bcma_serial_port` supports MIPS serial setup.
- `struct bcma_drv_cc` tracks chipcommon core, capabilities, setup flags, PMU data, flash data, serial ports, ticks per ms, watchdog platform device, GPIO lock, and optional GPIO chip.
- `struct bcma_drv_cc_b` tracks ChipCommon-B core and MII mapping.
- Register macros wrap core and PMU read/write/mask/set operations.
- Exported functions cover watchdog timer programming, ALP clock, IRQ mask/status, GPIO in/out/outen/control/interrupt/pullup/pulldown, PLL/chipctl/regctl mask-set, spur avoidance, bus clock, and MII writes.

## Control flow and state
ChipCommon setup reads `BCMA_CC_ID`, `BCMA_CC_CAP`, extended capabilities, and PMU data, then initializes clock, flash, GPIO, watchdog, and serial support based on revision and capability bits. Callers use register access macros for direct operations and exported helpers for multi-step PMU/GPIO/watchdog behavior.

## State and persistence behavior
Most state is hardware MMIO state. Flash/SPROM/NAND registers address persistent storage. The driver structure caches capabilities, setup progress, clocks, flash geometry, and platform device state. GPIO register access is protected by `gpio_lock`.

## Dependencies and integration points
Depends on platform devices, Broadcom NAND platform data, GPIO driver framework, and `bcma.h` accessors. Integrated by BCMA SoC boot, MTD, GPIO, watchdog, serial, wireless, and ethernet drivers.

## Risks
Revision-specific register availability is extensive; using a register on the wrong chip revision can hang or misconfigure hardware. GPIO and PMU read/modify/write sequences require locking or helper use. Flash command constants must match vendor protocols. PMU PLL changes can destabilize the system if masks/shifts are wrong.

## Test signals
Test chipcommon setup on multiple chip IDs/revisions, GPIO operations under concurrency, watchdog programming, flash detection, NAND boot detection, PMU clock calculations, PLL update paths, and register dumps against known hardware.
