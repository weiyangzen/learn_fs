# sources/distributed-fs/ceph-client/include/linux/firmware/samsung/exynos-acpm-protocol.h

## Purpose
This header defines the client handle and operation table for Samsung Exynos ACPM firmware protocol services. It focuses on firmware-mediated DVFS clock rates and PMIC register access.

## APIs, types, and control flow
`struct acpm_dvfs_ops` supplies `set_rate()` and `get_rate()` keyed by ACPM channel and clock id. `struct acpm_pmic_ops` supplies single, bulk, write, bulk-write, and masked update register operations keyed by channel plus PMIC type/register/channel fields. `struct acpm_ops` groups the service tables, and `struct acpm_handle` embeds those ops. Consumers obtain a handle by device tree node through `devm_acpm_get_by_node()`, then call the handle's function pointers.

## State and dependencies
State is opaque to clients and represented by `struct acpm_handle`. The API depends on `struct device_node`, device-managed acquisition, and `CONFIG_EXYNOS_ACPM_PROTOCOL`; when disabled, handle lookup returns `NULL`.

## Integration, risks, and tests
Clock, regulator, PMIC, and SoC power drivers integrate through this protocol instead of programming hardware directly. Risks include unchecked `NULL` handles, channel-id mismatches, register width/count misuse, and firmware serialization or timeout failures hidden behind callback-style ops. Test signals are devm cleanup, disabled-config fallback, DVFS set/get consistency, PMIC bulk count bounds, masked update correctness, and firmware error propagation.
