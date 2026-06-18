# sources/distributed-fs/ceph-client/drivers/soc/rockchip/io-domain.c

## Purpose

`io-domain.c` keeps Rockchip SoC IO-domain voltage selector bits synchronized with regulator voltages. It programs GRF/PMUGRF bits initially and through regulator notifiers so hardware IO voltage domains track external 1.8 V or 3.3 V rails.

## Important APIs, Types, and Functions

`struct rockchip_iodomain_supply` binds one regulator to an index and notifier. `struct rockchip_iodomain_soc_data` defines GRF offset, supply names, optional init, and optional write callback. `rockchip_iodomain_notify()` reacts to regulator pre/post/abort voltage events. `rockchip_iodomain_write()` handles generic hiword-mask writes; `rk3568_iodomain_write()` handles split selector registers. Per-SoC init functions switch special domains from GPIO/static control into framework control.

## Control Flow

Probe selects SoC data, resolves GRF regmap from parent syscon or legacy `rockchip,grf` phandle, then iterates up to 16 supply names. For each present regulator it reads current voltage, rejects voltages above 3.6 V, writes the selector, and registers a notifier. After all supplies, optional SoC init writes special control bits. Remove unregisters notifiers in reverse order.

## State and Persistence Behavior

Driver state stores regulator pointers and notifier blocks. GRF selector bits persist in hardware. Notifier events adjust hardware before voltage increases using the maximum requested voltage, after voltage changes, or after aborts.

## Dependencies and Integration Points

It depends on syscon/regmap, regulator consumer/notifier APIs, OF/platform probing, and Rockchip GRF bindings. It is safety-critical for pin electrical limits and peripheral operation.

## Risks and Edge Cases

The notifier must program selectors before external voltage rises; wrong event handling can overvoltage IO pads. Voltage thresholds rely on datasheet maximums and classify anything above 1.98 V as 3.3 V. Missing optional regulators are ignored, leaving bootloader defaults. `rk3568_iodomain_write()` intentionally skips some indexes, so SoC data ordering is critical. If probe fails mid-way, registered notifiers are unwound, but already-written GRF bits remain.

## Test Signals

Test initial selector programming for every supported SoC data table, regulator pre-change/commit/abort paths, too-high voltage rejection, missing optional supplies, probe deferral, notifier unregister on remove, and special init bits for PX30/RK3288/RK3308/RK3328/RK3368/RK3399.
