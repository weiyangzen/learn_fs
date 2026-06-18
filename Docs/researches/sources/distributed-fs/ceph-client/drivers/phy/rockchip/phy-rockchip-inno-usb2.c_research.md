# sources/distributed-fs/ceph-client/drivers/phy/rockchip/phy-rockchip-inno-usb2.c

## Purpose
This is the main Rockchip Innosilicon USB2 PHY driver. It supports OTG and host ports across many SoCs, exports a 480 MHz PHY clock, manages extcon cable state, charger detection, linestate/ID/VBUS/host-disconnect interrupts, delayed OTG and host state machines, resets, optional USBGRF register space, and variant-specific tuning/register maps.

## Important APIs, Types, And Functions
`struct rockchip_usb2phy` owns device state, GRF/USBGRF regmaps, input clocks, 480 MHz output clock, reset, extcon, mux IRQ, charger state/type, and per-port state. `struct rockchip_usb2phy_port` stores a PHY, port id, suspend/VBUS/host-disconnect state, IRQs, mutex, delayed works, DT mode, and register config. `struct rockchip_usb2phy_cfg` and nested register tables describe each SoC instance. Register helpers `property_enable()` and `property_enabled()` implement high-word write-mask register access. PHY callbacks handle init, exit, power_on, and power_off. State machines are `rockchip_usb2phy_otg_sm_work()`, `rockchip_chg_detect_work()`, and `rockchip_usb2phy_sm_work()`.

## Control Flow
Probe gets the GRF syscon, optional USBGRF, clocks, reset, match-data config array, extcon, selects the config row matching the node `reg`, enables input clocks with devm cleanup, registers the 480 MHz clock, resets/tunes the PHY, iterates child `host-port` and `otg-port` nodes to create per-port PHYs and IRQ/work state, registers a PHY provider, and optionally requests a combined top-level IRQ. OTG init enables BVALID and ID interrupts and schedules the OTG work unless the port is host-only. Host init enables linestate and optional disconnect IRQs and schedules host work. Power-on enables the 480 MHz clock, clears PHY suspend, resets the PHY, and waits for UTMI stability; power-off sets suspend and disables the clock. Charger detection follows DCD, primary, and secondary phases and reports SDP/CDP/DCP/SLOW through extcon.

## State And Persistence
Software state includes port suspend flags, OTG state, VBUS attachment, charger state/type, DCD retries, host disconnect state, extcon cable states, and delayed work scheduling. Hardware state is spread across GRF/USBGRF registers for suspend, detection enables/status/clear bits, charger comparators, clock output, and SoC tuning. State is not persistent across reset; probe and power callbacks reconstruct it.

## Dependencies And Integration Points
The driver uses generic PHY, common clock provider APIs, extcon provider/notifier APIs, power_supply charger type enums, reset controls, syscon/regmap, platform IRQs, delayed work, USB OF mode parsing, and optional child-node IRQ naming. It binds many compatible strings from `rockchip,px30-usb2phy` through `rockchip,rk3588-usb2phy` and `rockchip,rv1108-usb2phy`, and is consumed by USB host/device controllers plus clock consumers of `clk_usbphy_480m`.

## Risks And Test Signals
This file has the highest integration risk in the subset. Register tables are SoC-specific and selected by `reg`, so DT mismatches can bind the wrong offsets. Workqueues, extcon notifications, and IRQ clear/enable order can race cable changes. Charger detection depends on comparator semantics that differ on RK3576/RK3588. Power-on always resets the PHY after unsuspend, which can affect active consumers if reference counting is wrong. Test signals include probe for every compatible/config row, child port creation, combined and per-port IRQ modes, host autosuspend/resume on linestate, OTG ID/VBUS transitions, charger type classification, 480 MHz clock provider behavior, rk3128/rk3576/rk3588 tuning writes, and cleanup of delayed work on PHY exit.
