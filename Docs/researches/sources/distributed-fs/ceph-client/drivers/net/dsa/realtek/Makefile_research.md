# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/Makefile

## Purpose

This Makefile maps Realtek DSA Kconfig symbols to common, interface, and chip-specific objects.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_NET_DSA_REALTEK) += realtek_dsa.o`
- `realtek_dsa-objs := rtl83xx.o`, with `realtek-mdio.o` and/or `realtek-smi.o` appended when their interface configs are enabled.
- `obj-$(CONFIG_NET_DSA_REALTEK_RTL8366RB) += rtl8366.o`, composed from `rtl8366-core.o`, `rtl8366rb.o`, and optional `rtl8366rb-leds.o`.
- `obj-$(CONFIG_NET_DSA_REALTEK_RTL8365MB) += rtl8365mb.o`.

## Control Flow

There is no runtime flow. Kbuild assembles the common Realtek transport/core object and chip driver objects based on config selections.

## State and Persistence

The file controls build outputs only. It does not define runtime state.

## Dependencies and Integration Points

The object layout reflects the architecture: `rtl83xx.o` provides common interface-agnostic probe/register helpers, `realtek-mdio.o` and `realtek-smi.o` provide transports, and chip modules provide variants and DSA operations. Optional RTL8366RB LED code is conditionally folded into `rtl8366.o`.

## Risks and Edge Cases

Incorrect conditional inclusion can create missing transport symbols for chip drivers that call `realtek_mdio_driver_register()` or `realtek_smi_driver_register()`. Since `realtek_dsa.o` may include one or both transports, cross-config link coverage is important.

## Test Signals

Expected build outputs are `realtek_dsa.o` with the selected transport objects, `rtl8366.o` with optional LED object, and `rtl8365mb.o` when enabled. Link tests should cover MDIO-only, SMI-only, both, and no-chip configurations.
