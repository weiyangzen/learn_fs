# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/Kconfig

## Purpose

This Kconfig file defines build options for the Realtek DSA switch family, split into a common family menu, transport interface drivers (MDIO and SMI), chip drivers (RTL8365MB and RTL8366RB), and optional RTL8366RB LED support.

## Important APIs, Types, and Functions

- `NET_DSA_REALTEK` is the family-level tristate option and selects `FIXED_PHY`, `IRQ_DOMAIN`, `REALTEK_PHY`, and `REGMAP`.
- `NET_DSA_REALTEK_MDIO` and `NET_DSA_REALTEK_SMI` are bool interface options gated by OF support.
- `NET_DSA_REALTEK_RTL8365MB` depends on either interface and selects the `RTL8_4` DSA tagger.
- `NET_DSA_REALTEK_RTL8366RB` depends on either interface and selects the `RTL4_A` DSA tagger.
- `NET_DSA_REALTEK_RTL8366RB_LEDS` is a hidden bool defaulting to the RTL8366RB driver when LED class linkage permits.

## Control Flow

There is no runtime control flow. The dependency graph ensures that at least one transport interface can be enabled for chip drivers, and that chip drivers pull in the correct tag protocols.

## State and Persistence

State consists of kernel config selections persisted in `.config`. These selections determine which objects are built into `realtek_dsa.o`, `rtl8366.o`, and `rtl8365mb.o`.

## Dependencies and Integration Points

The options integrate with DSA, OF, regmap, IRQ domains, fixed PHY support, Realtek PHY support, tag protocol drivers, and LED class support. The menu help explicitly notes that a family driver needs both an interface driver and at least one chip subdriver to be useful.

## Risks and Edge Cases

Because MDIO/SMI are bools under a tristate family option, build combinations must be checked for built-in/module linkage with chip drivers. Chip drivers depend on an interface being configured but the interface alone cannot register a useful switch without a chip variant. LED support follows the RTL8366RB symbol by default and can be disabled indirectly by LED class constraints.

## Test Signals

Build matrix signals include Realtek family disabled, family enabled without chip drivers, MDIO-only, SMI-only, both interfaces, RTL8365MB and RTL8366RB as built-in/modules, and LED-compatible/incompatible configurations. Runtime signals are correct transport registration and tagger availability for selected chips.
