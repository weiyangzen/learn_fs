<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Makefile

## Purpose
Builds the Intel In Field Scan module.

## Important Build Rules
`obj-$(CONFIG_INTEL_IFS) += intel_ifs.o` and `intel_ifs-y := core.o load.o runtest.o sysfs.o` link CPU matching, firmware loading, test execution, and sysfs interfaces into one module.

## Dependencies, Risks, And Test Signals
The file depends on the four implementation objects staying in sync with `ifs.h`. Test by building `CONFIG_INTEL_IFS=y` and `m`; missing any object breaks exported symbols such as `ifs_load_firmware()` or `do_core_test()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Makefile -->
