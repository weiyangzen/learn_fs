# sources/distributed-fs/ceph-client/drivers/soc/samsung/gs101-pmu.c

## Purpose

`gs101-pmu.c` describes the Google Tensor GS101 PMU register access policy and secure-access hooks for PMU_ALIVE registers. It provides regmap readable/writable ranges and SMC-backed read/write/update functions for PMU registers that Linux can read directly but must write through EL3 firmware.

## Important APIs, Types, and Functions

`gs101_pmu_registers[]` enumerates readable PMU register ranges. `gs101_pmu_ro_registers[]` enumerates ranges excluded from writes. `gs101_pmu_rd_table` and `gs101_pmu_wr_table` wrap those arrays as regmap access tables. `gs101_pmu_data` sets `.pmu_secure = true`, `.pmu_cpuhp = true`, and exposes the tables. Secure helpers are `tensor_sec_reg_write()`, `tensor_sec_reg_read()`, and `tensor_sec_update_bits()`. `tensor_sec_reg_rmw()`, `tensor_set_bits_atomic()`, and `tensor_is_atomic()` implement update strategy selection.

## Control Flow

The Exynos PMU core binds `gs101_pmu_data` and configures a regmap that honors the range tables. Reads call `tensor_sec_reg_read()`, which uses normal PMU MMIO reads because all PMU registers are read-accessible to Linux. Writes call `tensor_sec_reg_write()`, which invokes SMC function `0x82000504` with the physical PMU address, write operation id, and value. Update-bits calls use atomic set/clear register aliases for PMU_ALIVE offsets when supported, otherwise a secure read-modify-write SMC. Atomic updates iterate all bits in the mask and issue one secure write per bit with set or clear alias bits folded into the register offset.

## State and Persistence Behavior

There is no driver-private mutable state. Register access tables are constant. Persistent effects are PMU register writes mediated by firmware. The SMC context is the PMU base address supplied by the regmap bus context.

## Dependencies and Integration Points

The file depends on ARM SMCCC, Linux regmap access tables, Exynos PMU core data structures, and GS101 PMU register macros. It integrates with EL3 firmware implementing the Tensor PMU secure register SMC ABI and with CPU hotplug/power management through `pmu_cpuhp`.

## Risks and Edge Cases

The register range tables are large and must match hardware exactly; an overly broad writable range can expose destructive PMU writes. `tensor_set_bits_atomic()` mutates `offset` inside the bit loop but masks alias bits each iteration, which relies on aliases only occupying `BIT(15)|BIT(14)`. SMC failures are only warned and returned; callers must handle errors. Atomic updates issue many SMC calls for wide masks, which can be slow. Registers excluded by `tensor_is_atomic()` must stay synchronized with hardware that lacks set/clear aliases.

## Test Signals

Boot on GS101 should create a PMU regmap with expected readable/writable behavior, show successful SMC writes, and avoid warnings from secure calls. Tests should cover update-bits on PMU_ALIVE atomic registers, non-atomic exceptions, read-only ranges, CPU hotplug, suspend/resume, and firmware denial paths.
