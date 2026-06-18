# sources/distributed-fs/ceph-client/drivers/regulator/qcom_smd-regulator.c

## Purpose
This driver registers regulators controlled by Qualcomm SMD RPM firmware. It converts regulator enable, voltage, and load requests into key/value SMD RPM messages for many PMIC families, including PM8916, PM8941, PM8994, PM8998, PM660, PM6125, PM2250, PMS405, PMR735A, and MP5496 variants.

## Important APIs, Types, and Functions
`struct qcom_rpm_reg` stores the SMD RPM resource type/id, descriptor, cached enable/voltage/load values, and dirty bits for each property. `struct rpm_regulator_req` is the packed key/nbytes/value message element using keys `"swen"`, `"uv"`, and `"ma"`. Important functions are `rpm_reg_write_active()`, `rpm_reg_enable()`, `rpm_reg_disable()`, `rpm_reg_set_voltage()`, `rpm_reg_set_load()`, `rpm_regulator_init_vreg()`, and `rpm_reg_probe()`. Descriptor templates encode voltage ranges and ops for SMPS/LDO, fixed regulators, switches, BOB, and MP5496-specific behavior.

## Control Flow
Probe obtains the parent `qcom_smd_rpm`, rejects a second distinct RPM instance through the global `smd_vreg_rpm`, selects match data, and iterates available child nodes. Each node is matched by name against the PMIC table, then a descriptor copy is registered with `devm_regulator_register()`. Runtime ops mark a field dirty, update the cache, and call `rpm_reg_write_active()`, which emits only dirty fields and only sends voltage/load values while the regulator is enabled. On successful SMD write, dirty bits are cleared; on failure, the changed cache field is rolled back by the caller.

## State and Persistence
Driver state is volatile per-regulator memory plus a global SMD RPM pointer. Cached `is_enabled`, `uV`, and `load` are what getter paths report. Dirty bits preserve pending changes across write attempts. Voltage and load changes while disabled are cached but not sent until enable causes a fresh active-state write. There is no on-disk persistence.

## Dependencies and Integration Points
The driver depends on `linux/soc/qcom/smd-rpm.h`, platform/OF match data, the regulator core, linear voltage range helpers, and parent SMD RPM device setup. It exposes child-node regulator names via PMIC tables and integrates with standard regulator supplies and constraints from DT.

## Risks and Test Signals
Risk areas include the single global RPM pointer preventing multiple independent RPM instances, cache-only voltage/load updates while disabled, broad PMIC table maintenance, and lack of locking around cached state changes. Test signals include probing all compatible tables, multi-PMIC mismatch handling, SMD write failure rollback, enable after deferred voltage/load changes, switch-only regulators, fixed-voltage descriptors, and userspace regulator summary consistency.
