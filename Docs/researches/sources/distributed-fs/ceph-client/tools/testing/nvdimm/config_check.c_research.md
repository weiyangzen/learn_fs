# sources/distributed-fs/ceph-client/tools/testing/nvdimm/config_check.c

## Purpose
`config_check.c` enforces the module configuration assumptions required by the nvdimm test stack.

## Important APIs, Types, And Functions
The single function `check()` uses `BUILD_BUG_ON()` with `IS_MODULE()` and `IS_ENABLED()` predicates for `CONFIG_LIBNVDIMM`, `CONFIG_BLK_DEV_PMEM`, `CONFIG_ND_BTT`, `CONFIG_ND_PFN`, `CONFIG_ACPI_NFIT`, `CONFIG_DEV_DAX`, and `CONFIG_DEV_DAX_PMEM`.

## Control Flow
There is no runtime branching beyond compile-time constant evaluation. If a required config is not built as a module, compilation fails. `CONFIG_ACPI_NFIT` is only required as a module when enabled.

## State And Persistence
No state is stored or modified.

## Dependencies And Integration Points
Every major test module object list includes `config_check.o`, so incompatible kernel configurations fail early at build time rather than during module insertion.

## Risks
The checks intentionally reject built-in configurations for symbols that the tests need as loadable modules. Kernel config symbol renames or dependency changes require updating this file.

## Test Signals
The primary signal is a build-time failure. A successful build means the required driver components can be replaced or supplemented by the test modules.
