<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-iim.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/imx-iim.c

## Purpose
Provides read-only NVMEM access to the older i.MX IC Identification Module eFuse banks.

## Important APIs, Types, And Functions
`struct imx_iim_drvdata` carries the number of byte registers per SoC. `struct iim_priv` stores MMIO base and clock. `imx_iim_read()` enables the clock, maps byte offsets to IIM bank/register offsets with `IIM_BANK_BASE()`, reads one byte per 32-bit register, and disables the clock. `imx_iim_probe()` registers `imx-iim`.

## Control Flow
OF match selects SoC register count. Probe maps resource 0, gets the clock, fills a read-only byte-addressed config, and registers. Reads walk every requested byte while the clock is enabled.

## State And Persistence
Runtime state is MMIO base and clock handle. eFuse data is persistent hardware state and cannot be modified by this driver.

## Dependencies And Integration Points
Depends on platform MMIO, clocks, OF match data, and NVMEM provider core. Consumers retrieve per-SoC fuse values through NVMEM cells.

## Risks
Every byte read is a separate 32-bit MMIO access; incorrect nregs match data can expose invalid addresses. Clock enable failures propagate. No locking is used, assuming read-only operations and clock framework serialization are sufficient.

## Test Signals
Probe each supported compatible, read first/last cells, verify clock prepare/disable balance, and compare bank/register offset mapping with reference manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-iim.c -->
