# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvmdio.c

## Purpose
`mvmdio.c` implements the shared Marvell Orion/NETA MDIO controller driver. It registers a Linux `mii_bus` for classic clause 22 SMI or clause 45 XSMI accesses, serializes PHY register reads and writes through the mdiobus core, optionally waits for completion through the controller error/completion interrupt, manages controller clocks, and supports both Device Tree and ACPI firmware descriptions. The file is explicitly used by Marvell Ethernet MAC drivers such as `mvneta` and `mv643xx_eth`.

## Important APIs, Types, and Functions
- `struct orion_mdio_dev` holds mapped registers, up to four clocks, optional completion IRQ, and the wait queue used when interrupt-driven completion is available.
- `enum orion_mdio_bus_type` selects classic `BUS_TYPE_SMI` or extended `BUS_TYPE_XSMI`.
- `struct orion_mdio_ops` abstracts the bus-type-specific busy/done test used by `orion_mdio_wait_ready()`.
- Clause 22 accessors are `orion_mdio_smi_read()` and `orion_mdio_smi_write()`, with completion status from `orion_mdio_smi_is_done()`.
- Clause 45 accessors are `orion_mdio_xsmi_read_c45()` and `orion_mdio_xsmi_write_c45()`, with completion status from `orion_mdio_xsmi_is_done()`.
- `orion_mdio_xsmi_set_mdc_freq()` reads the optional `clock-frequency` property and `mg_core_clk` to program XSMI MDC clock division.
- `orion_mdio_err_irq()` handles `MVMDIO_ERR_INT_SMI_DONE`, clears the interrupt cause, and wakes waiters.
- `orion_mdio_probe()` allocates and registers the mdiobus; `orion_mdio_remove()` unregisters it and disables clocks.

## Control Flow
Probe reads the firmware match data to determine SMI versus XSMI, obtains the first memory resource, allocates a devm `mii_bus` with private `orion_mdio_dev` storage, installs either clause 22 or clause 45 callbacks, maps the controller registers, and initializes the wait queue. For OF devices it acquires up to four indexed clocks, handles `-EPROBE_DEFER`, warns if more clocks exist than the static array supports, and configures XSMI MDC frequency when requested. For non-OF devices it gets one optional unnamed clock.

The optional IRQ path calls `platform_get_irq_optional()`. If the IRQ exists but the MMIO resource is too small to cover the interrupt mask register, the driver disables IRQ use and falls back to polling. Otherwise it requests a shared IRQ and enables the SMI-done interrupt mask. Finally, ACPI-described devices register through `acpi_mdiobus_register()`, while other devices register through `of_mdiobus_register()`.

Each read or write first calls `orion_mdio_wait_ready()` to ensure the controller is idle. With no completion IRQ, that helper uses `read_poll_timeout_atomic()` with a 2 microsecond poll interval and a 1 millisecond timeout. With an IRQ, it waits on `smi_busy_wait` for at least two jiffies. SMI reads then write the PHY address, register number, and read command, wait again, verify `MVMDIO_SMI_READ_VALID`, and return the low 16 bits. SMI writes post address/register/data with the write operation bit pattern. XSMI reads additionally write the clause 45 register address to `MVMDIO_XSMI_ADDR_REG`, issue the management read command with PHY and device address, wait, verify read-valid, and return 16 bits. XSMI writes similarly program address and management write data.

Remove disables the interrupt mask if used, unregisters the mdiobus, disables/unprepares clocks, and drops clock references.

## State and Persistence Behavior
The driver owns only runtime state: mapped MMIO, clock handles, wait queue, and mdiobus registration. MDIO transaction state lives in hardware busy/read-valid bits and is not persisted. Clock-frequency programming changes the live XSMI configuration register but is reconstructed on probe. There is no disk persistence or long-lived software cache of PHY register values.

## Dependencies and Integration Points
This file depends on platform devices, firmware match data, OF and ACPI MDIO registration helpers, phylib mdiobus callbacks, Linux clock APIs, interrupt APIs, wait queues, MMIO accessors, and polling helpers. OF compatibles are `marvell,orion-mdio` for SMI and `marvell,xmdio` for XSMI; ACPI IDs are `MRVL0100` and `MRVL0101`. MAC drivers consume the registered bus through phylib/phylink and PHY nodes rather than calling this file directly.

## Risks and Edge Cases
- The code manually unwinds clocks acquired with `of_clk_get()` and `clk_get_optional()`; deferred probes and partial clock arrays need cleanup coverage.
- `orion_mdio_wait_ready()` uses atomic polling when no IRQ is present, so long hardware stalls become timeout errors and can delay PHY operations.
- XSMI MDC frequency setup only works with OF and `mg_core_clk`; missing or failed clock lookup logs an error and leaves the default divider.
- If the interrupt resource exists but the MMIO resource is too short for the interrupt registers, interrupt completion is silently disabled after an error message.
- Read-valid failure returns `-ENODEV`, which can be interpreted by PHY discovery as an absent device.
- The interrupt handler writes the bitwise complement of the done bit to the cause register, matching this controller's clear semantics; wrong semantics on a variant would be destructive.

## Test Signals
- Probe tests should cover SMI and XSMI compatibles, ACPI IDs, no IRQ polling mode, IRQ completion mode, short MMIO resources, missing memory resource, and clock defer/unwind.
- MDIO transaction tests should cover valid reads/writes, busy timeout, read-valid failure, clause 45 device/register addressing, and concurrent PHY accesses through mdiobus locking.
- Device Tree tests should include multiple clocks, more than four clocks, `clock-frequency`, missing `mg_core_clk`, and child PHY discovery.
- Integration tests with `mvneta` and `mv643xx_eth` should verify PHY attach, link negotiation, WoL propagation, and remove ordering where MACs detach before the MDIO bus disappears.
