# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek.h

## Purpose

This header defines shared Realtek DSA switch data structures, variant operations, common runtime state, VLAN/MIB helper structures, and exported helper prototypes used by the Realtek common core, transport drivers, and chip-specific drivers.

## Important APIs, Types, and Functions

- `REALTEK_HW_STOP_DELAY` and `REALTEK_HW_START_DELAY` define reset timing constants.
- `struct rtl8366_mib_counter` describes MIB counter layout for RTL8366-style helpers.
- `struct rtl8366_vlan_mc` and `struct rtl8366_vlan_4k` describe member-table and 4K VLAN entries.
- `struct realtek_priv` is the central driver state: device/reset/GPIOs, regmaps, locks, user and parent MDIO buses, MDIO address, variant pointer, embedded DSA switch, IRQ domain, LED-disable flag, CPU/port/VLAN/MIB metadata, operation vtable, no-ACK write hook, VLAN enable state, buffer, and per-chip private data.
- `struct realtek_ops` is the chip operation vtable for detect/reset/setup, MIB, VLAN member table, VLAN 4K table, MC index, VLAN enablement, port enablement, and PHY read/write.
- `struct realtek_variant` ties DSA ops, chip ops, phylink ops, SMI command/delay parameters, and chip-private allocation size together.
- Prototypes expose RTL8366 VLAN and ethtool-stat helper functions plus external variant instances `rtl8366rb_variant` and `rtl8365mb_variant`.

## Control Flow

The header has no direct control flow. It defines how control moves between layers: transport drivers provide regmap access and call common `rtl83xx` helpers; common/chip code stores state in `realtek_priv`; chip variants fill `realtek_variant` and `realtek_ops`; DSA callbacks use helper prototypes for VLAN and stats behavior.

## State and Persistence

`realtek_priv` holds all per-device state for the Realtek family, including both transport state (GPIOs, MDIO bus/address, regmaps) and switch state (CPU port, number of ports, VLAN enabled flags, IRQ domain, MIB counter metadata, chip data). Hardware state such as VLAN tables, port enablement, MIB counters, and PHY registers persists in the switch and is manipulated through the operation vtable.

## Dependencies and Integration Points

The header depends on Linux PHY, platform device, GPIO, DSA, and reset APIs. It is shared by MDIO and SMI transport files and chip drivers such as RTL8366RB and RTL8365MB. The external variants are integration points used by the common probe logic to bind compatible strings to chip-specific behavior.

## Risks and Edge Cases

Because `realtek_priv` embeds a `struct dsa_switch`, lifetime and drvdata setup must be consistent across transports and common code. The vtable contains many optional-looking operations but chip drivers must provide the operations used by their DSA callbacks. `buf[4096]` is a fixed scratch buffer that requires careful bounds discipline in users. State flags `vlan_enabled` and `vlan4k_enabled` must remain synchronized with hardware. Transport-specific fields are present in the shared struct, so chip code must not assume MDIO and SMI fields are always populated.

## Test Signals

Compile coverage across MDIO, SMI, RTL8366RB, and RTL8365MB validates type contracts. Runtime signals include successful common probe allocation, correct variant selection, DSA operations reaching chip ops, VLAN helper correctness, MIB stat reporting, PHY read/write through the selected transport, and clean shutdown/remove without stale IRQ domains or buses.
