# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-mdio.c

## Purpose

This file implements the MDIO transport adapter for Realtek DSA switches. It translates regmap-style 16-bit register reads/writes into the Realtek MDIO indirect-access sequence, delegates common device allocation and DSA registration to the `rtl83xx` core, and exports probe/remove/shutdown helpers for chip drivers that register MDIO devices.

## Important APIs, Types, and Functions

- `REALTEK_MDIO_*` constants define the MDIO indirect control, address, data, and operation registers.
- `realtek_mdio_write()` writes address operation, target register, data, and write command under `bus->mdio_lock`.
- `realtek_mdio_read()` writes address operation and target register, issues the read command, then reads the data register under the same lock.
- `realtek_mdio_info` is a `struct realtek_interface_info` with transport read/write callbacks.
- `realtek_mdio_probe()` calls `rtl83xx_probe()`, stores the parent bus and MDIO address in `realtek_priv`, sets `write_reg_noack`, and calls `rtl83xx_register_switch()`.
- `realtek_mdio_remove()` unregisters the switch then calls `rtl83xx_remove()`.
- `realtek_mdio_shutdown()` delegates to `rtl83xx_shutdown()`.

## Control Flow

Probe is intentionally thin. The common core creates and initializes `realtek_priv` and regmaps using `realtek_mdio_info`. The MDIO-specific code fills `priv->bus`, `priv->mdio_addr`, and `priv->write_reg_noack`. Successful probe ends with common switch registration.

Register writes use a four-step indirect sequence on the parent MDIO address: select address op in control0, write target register to address register, write value to data-write register, and trigger write op in control1. Reads use the same address setup, trigger read op, and read data-read register.

## State and Persistence

Runtime transport state is stored in `realtek_priv`: parent `mii_bus`, `mdio_addr`, and no-ack write function pointer. The underlying switch register state persists in hardware. The MDIO bus lock serializes indirect transactions so address/data/control sequences are not interleaved.

## Dependencies and Integration Points

The file depends on Linux MDIO, regmap, OF-capable device probing through chip drivers, and the common `rtl83xx` core. It exports symbols in the `REALTEK_DSA` namespace so chip modules can use the transport lifecycle helpers.

## Risks and Edge Cases

The indirect access sequence assumes all MDIO operations complete synchronously and does not poll a busy bit. Any bus error aborts the sequence and returns the error. `write_reg_noack` is the same as normal write for MDIO transport, unlike SMI where reset may not ACK. Correct locking is critical because concurrent transactions would corrupt the selected indirect address.

## Test Signals

Signals include successful probe over an MDIO-described Realtek switch, correct register reads/writes through regmap, no interleaving under concurrent DSA operations, clean unregister/remove, and exported namespace symbols resolving for chip drivers. Fault tests should simulate MDIO write/read failures at each step.
