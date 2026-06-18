# sources/distributed-fs/ceph-client/drivers/phy/lantiq/phy-lantiq-rcu-usb2.c

## Purpose
Lantiq XWAY RCU-based USB 1.1/2.0 PHY provider. It configures host mode, DMA endianness, optional analog tuning, and controls PHY/core resets and the PHY gate clock.

## Important APIs, types, and functions
- `struct ltq_rcu_usb2_bits` describes SoC-specific bit positions and analog-config presence.
- `struct ltq_rcu_usb2_priv` stores parent RCU regmap offsets, clocks, resets, device, and PHY.
- `ltq_rcu_usb2_of_parse()` gets match data, parent syscon, `reg` offsets, `phy` clock, `ctrl` reset, and optional `phy` reset.
- `ltq_rcu_usb2_phy_init()` writes analog cfg where available, host mode, and endianness.
- Power ops deassert/assert PHY reset and enable/disable clock.

## Control flow
Probe parses resources, deasserts shared USB core reset, asserts PHY reset, creates one PHY, and registers simple xlate. Init writes RCU bits. Power-on deasserts PHY reset, enables clock, and waits 100-200 us; power-off reverses.

## State and persistence
No persistent state. Runtime state is RCU register bits, reset lines, and clock enable.

## Dependencies and integration points
Uses generic PHY, clk, reset, syscon/regmap, OF address parsing, and SoC-specific compatible data. Consumed by USB controller nodes.

## Risks and test signals
Risks include ignoring regmap update errors in init, optional reset handling, and fixed big-endian host DMA assumption. Test all compatible bit layouts, analog-config variants, reset/clock failures, and USB host enumeration.
