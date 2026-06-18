# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/xgmac_mdio.c

## Purpose
Implements the Freescale/NXP QorIQ 10G MDIO platform driver for FMan XGMAC/MEMAC MDIO controllers. It registers an `mii_bus` supporting Clause 22 and Clause 45 accesses over memory-mapped MDIO registers.

## Important APIs, Types, And Functions
`struct tgec_mdio_controller` maps the hardware registers; `struct mdio_fsl_priv` holds the MMIO base, optional clock, requested MDC frequency, endianness, and erratum flags. Bus callbacks are `xgmac_mdio_read_c22()`, `xgmac_mdio_write_c22()`, `xgmac_mdio_read_c45()`, and `xgmac_mdio_write_c45()`. Probe configures `mii_bus` and registers it through OF or ACPI.

## Control Flow
Probe obtains the memory resource, allocates a managed `mii_bus`, maps BAR/register memory without exclusive request, determines endianness and errata properties, optionally suppresses preamble, optionally programs MDC divider from `clock-frequency`, then registers the bus with OF or ACPI firmware nodes. Each read/write selects Clause 22 or Clause 45 encoding, waits for the bus to be idle, writes port/dev/register fields, initiates transfer, waits for completion, and returns data or error.

## State And Persistence
State is the live MMIO controller and `mii_bus` private data. MDC divider and preamble suppression persist only in controller registers while powered. There is no remove callback because devm and platform-driver lifetime handle registration cleanup in this source snapshot.

## Dependencies And Integration Points
Uses Linux MDIO/PHY, OF MDIO, ACPI MDIO, clock, platform, and MMIO APIs. Device-tree compatibles are `fsl,fman-xmdio` and `fsl,fman-memac-mdio`; ACPI ID is `NXP0006`. PHY drivers above this bus perform actual link management.

## Risks
Polling loops use a fixed iteration count with `cpu_relax()` rather than time-based delays, so behavior depends on CPU speed. Erratum A009885 disables local interrupts around read completion to meet a 16-MDC-cycle window; mishandling can affect latency. A011043 suppresses read-error handling. Divider programming rejects out-of-range values but leaves existing hardware state.

## Test Signals
Probe on OF and ACPI systems, `mdiobus` registration, Clause 22/45 read/write against known PHYs, timeout/error behavior with absent PHYs, endianness property coverage, MDC divider programming with valid and invalid clocks, suppress-preamble behavior, and erratum-specific read paths.
