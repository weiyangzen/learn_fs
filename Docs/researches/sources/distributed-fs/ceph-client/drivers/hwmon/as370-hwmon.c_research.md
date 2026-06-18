# sources/distributed-fs/ceph-client/drivers/hwmon/as370-hwmon.c

## Purpose
This compact platform driver exposes the Synaptics AS370 SoC PVT temperature monitor as one hwmon temperature input.

## Important APIs, Types, And Functions
`struct as370_hwmon` holds the MMIO base pointer. `init_pvt()` powers and enables the PVT block by programming `CTRL` bits `PD`, `T_SEL`, and `EN`. `as370_hwmon_read()` reads the `STS` register, masks the 12-bit raw code with `BN_MASK`, and converts it to millidegrees using `DIV_ROUND_CLOSEST(val * 251802, 4096) - 85525`. `as370_hwmon_is_visible()` exposes only `hwmon_temp_input`.

## Control Flow And State
`as370_hwmon_probe()` allocates devm state, maps the first platform memory resource with `devm_platform_ioremap_resource()`, initializes the PVT monitor, and registers a devm hwmon device named `as370`. Runtime reads are direct MMIO reads; there is no cache, lock, interrupt, or polling state. Hardware configuration persists in the PVT registers until reset or another agent modifies them.

## Dependencies And Integration Points
The driver depends on platform device probing, device tree compatible `syna,as370-hwmon`, MMIO accessors, and the hwmon with-info API. It has no thermal-zone or regulator integration in this file.

## Risks
The conversion formula and initialization sequence are SoC-specific and not self-validating. The code does not check `EOC`, so it reports the current raw bits whether or not a conversion-complete bit is set. It also never disables or powers down the monitor on remove because all resources are devm-managed and no remove callback exists.

## Test Signals
Probe tests should cover missing MMIO resources, correct compatible matching, `CTRL` write sequence, read conversion for representative raw values, visibility limited to `temp1_input`, and behavior when `EOC` is clear if hardware or a mock can expose that condition.
