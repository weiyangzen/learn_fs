<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Makefile

## Purpose
Builds the INT1092 SAR driver.

## Important Build Rule
`obj-$(CONFIG_INTEL_SAR_INT1092) += intel_sar.o`.

## Dependencies, Risks, And Test Signals
Depends solely on the matching Kconfig symbol. Test built-in and module builds and verify the module alias from `intel_sar.c` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int1092/Makefile -->
