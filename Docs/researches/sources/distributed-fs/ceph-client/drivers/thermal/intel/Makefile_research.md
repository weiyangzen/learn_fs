# sources/distributed-fs/ceph-client/drivers/thermal/intel/Makefile

## Purpose
Kbuild object map for Intel thermal drivers. It links selected Intel thermal modules and the `int340x_thermal/` subdirectory.

## Important APIs, Types, and Functions
No runtime APIs. It maps config symbols to objects such as `intel_tcc.o`, `intel_powerclamp.o`, `x86_pkg_temp_thermal.o`, `intel_soc_dts_iosf.o`, `intel_soc_dts_thermal.o`, `intel_quark_dts_thermal.o`, `intel_bxt_pmic_thermal.o`, `intel_pch_thermal.o`, `intel_tcc_cooling.o`, `therm_throt.o`, `intel_hfi.o`, and the int340x directory.

## Control Flow
Kbuild includes object files according to `CONFIG_*` values. `CONFIG_INT340X_THERMAL` descends into the int340x thermal subdirectory.

## State and Persistence
No runtime state. Build outputs persist in the build tree.

## Dependencies and Integration Points
Must remain synchronized with top-level Intel Kconfig, source filenames, and subdirectory Makefiles.

## Risks and Edge Cases
Object mapping typos break builds or omit selected drivers. Directory descent for `INT340X_THERMAL` must match submenu dependencies.

## Test Signals
Per-symbol build tests, allmodconfig, and module install checks should verify each configured object is produced.
