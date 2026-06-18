# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/fw.h

## Purpose
This header defines the in-memory firmware bundle model used by ZL3073x devlink flash update.

## Important APIs and types
`enum zl3073x_fw_component_id` identifies utility, firmware, and config components. `struct zl3073x_fw_component` stores component ID, size, and data pointer. `struct zl3073x_fw` stores an array of optional component pointers. It declares load/free/flash APIs.

## State, dependencies, risks, and tests
The types represent transient heap state only. They depend on `struct zl3073x_dev` from the core at use sites. Tests should confirm all enum entries align with `component_info[]` in `fw.c` and that absent optional components are skipped safely.
