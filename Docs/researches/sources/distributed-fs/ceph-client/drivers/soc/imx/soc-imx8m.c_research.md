
# sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx8m.c

## Purpose
i.MX8M SoC identity driver. It detects i.MX8MQ/MM/MN/MP machines, reads revision and UID from ATF, OCOTP, or anatop depending on variant, registers a SoC bus device, and optionally creates an `imx-cpufreq-dt` platform device.

## Important APIs, Types, and Functions
- `struct imx8_soc_data` describes per-SoC name, OCOTP compatible, revision callback, and UID callback.
- Revision/UID helpers include `imx8mq_soc_revision_from_atf()`, `imx8mq_soc_revision()`, `imx8mm_soc_revision()`, `imx8m_soc_uid()`, and `imx8mp_soc_uid()`.
- `imx8m_soc_probe()` registers SoC attributes and cpufreq device.
- `imx8_soc_init()` registers the platform driver/device at `device_initcall()`.

## Control Flow
The initcall checks OF machine compatibility and self-registers a platform driver plus simple platform device. Probe allocates attributes/drvdata, reads machine, obtains match data, maps/enables OCOTP clock through `imx8m_soc_prepare()`, reads revision and UID, unprepares OCOTP, formats revision/serial, registers `soc_device`, registers devm cleanup, logs SoC revision, and optionally registers cpufreq platform device with devm unregister.

## State and Persistence
State is devm-managed probe data and registered SoC/cpufreq platform devices. Hardware fuse data is read-only. No file persistence.

## Dependencies and Integration Points
Depends on OF machine matching, SMCCC for i.MX8MQ ATF revision if enabled, OCOTP/anatop syscon mappings, clocks, SoC bus core, and optional `CONFIG_ARM_IMX_CPUFREQ_DT`.

## Risks
- OCOTP clock/map failures fail probe even when partial identity might be possible.
- i.MX8MP serial combines two 64-bit halves; formatting depends on nonzero high half.
- The driver unregisters the platform driver if device registration fails, but a successful simple platform device has no explicit unregister in init path.
- Revision can be `"unknown"` if hardware/ATF provides zero.

## Test Signals
Machine matching for each i.MX8M compatible, ATF supported/unsupported paths, OCOTP/anatop map failures, clock enable failure, UID formatting for i.MX8MP, cpufreq device registration, and `/sys/devices/soc0` attribute verification.
