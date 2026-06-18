# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hisi-inno-usb2.c

## Purpose
HiSilicon INNO USB2 PHY provider for one or two host ports. It enables ref clocks, controls POR and per-port UTMI resets, and writes vendor test-register sequences for PHY clock enable across two hardware register formats.

## Important APIs, types, and functions
- `struct hisi_inno_phy_priv` stores MMIO, ref clock, POR reset, type, and two port states.
- `struct hisi_inno_phy_port` stores per-port UTMI reset and back-pointer.
- `hisi_inno_phy_write_reg()` encodes test data/address/port/write/clock/reset fields differently for `PHY_TYPE_0` and `PHY_TYPE_1`.
- `hisi_inno_phy_init()` enables refclk, deasserts POR, writes setup register, then deasserts UTMI reset.
- Probe iterates child nodes and creates up to two PHYs.

## Control flow
Probe maps MMIO, gets refclk and POR reset, reads compatible data for type, walks child nodes to get per-port reset controls and create PHYs, sets bus width 8, and registers simple xlate. Init/exit are per port but POR/refclk are shared, so consumers must be balanced.

## State and persistence
No persistent state. Runtime state includes reset lines, clock enable count, port array, and MMIO test interface state.

## Dependencies and integration points
Depends on clk, reset controller, MMIO, platform/OF, and generic PHY. Child PHY nodes provide per-port resets.

## Risks and test signals
Risks include shared POR/refclk controlled by independent ports without reference counting, leaked reset controls from `of_reset_control_get_exclusive()` unless devm-managed by core cleanup, and accepting more children than supported with a warning. Test one-port and two-port DTs, simultaneous port users, missing child resets, and both type encodings.
