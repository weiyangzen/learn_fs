# sources/distributed-fs/ceph-client/drivers/soc/samsung/exynos-pmu.h

## Purpose

`exynos-pmu.h` is the private PMU interface for generic and SoC-specific Exynos PMU code. It defines powerdown table records, match-data shape, exported data symbols, raw PMU helpers, and secure Tensor register callbacks.

## Important APIs, Types, and Functions

`PMU_TABLE_END` terminates `struct exynos_pmu_conf` arrays. `struct exynos_pmu_data` contains optional config tables, secure-regmap and CPU-PM flags, init and powerdown callbacks, and regmap access tables. Externs expose ARM PMU data sets and `gs101_pmu_data`. `pmu_raw_writel()`, `pmu_raw_readl()`, `tensor_sec_reg_write()`, `tensor_sec_reg_read()`, and `tensor_sec_update_bits()` are declared.

## Control Flow

Generic PMU probe receives an `exynos_pmu_data` pointer from OF match data and calls the callbacks or table fields at probe and suspend/powerdown time. SoC-specific files only export data conforming to this header.

## State and Persistence Behavior

The header declares structures; runtime state lives in `exynos-pmu.c` and hardware PMU registers.

## Dependencies and Integration Points

It depends on Exynos PMU register definitions for `NUM_SYS_POWERDOWN` and on regmap access tables. It links generic PMU code to SoC-specific table files and secure GS101 support.

## Risks and Edge Cases

Table arrays must terminate with `PMU_TABLE_END`; missing terminators cause out-of-bounds writes. Callback ordering in `exynos_sys_powerdown_conf()` depends on the distinction between primary and extra tables/callbacks. ARM-data externs are conditional on `CONFIG_EXYNOS_PMU_ARM_DRIVERS`.

## Test Signals

Compile with and without ARM PMU drivers, validate every table terminator, and exercise powerdown callbacks for all `enum sys_powerdown` modes.
