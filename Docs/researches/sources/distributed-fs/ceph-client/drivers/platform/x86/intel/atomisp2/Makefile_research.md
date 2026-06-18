<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Makefile

## Purpose
Builds AtomISP2 helper modules.

## Important Build Rules
`intel_atomisp2_led-y := led.o` and `obj-$(CONFIG_INTEL_ATOMISP2_LED)` create the LED helper. `intel_atomisp2_pm-y += pm.o` and `obj-$(CONFIG_INTEL_ATOMISP2_PM)` create the PM helper.

## Control Flow And State
The file has only build-time behavior. Its module object names must match the Kconfig help text and the platform-x86 parent Makefile directory selection.

## Dependencies, Risks, And Test Signals
Depends on the two AtomISP2 Kconfig symbols. A wrong object name drops a helper silently from configured builds. Test with built-in and module builds for each option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/atomisp2/Makefile -->
