<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/Makefile

## Purpose
Maps Intel platform-x86 Kconfig symbols to subdirectories and wrapper module objects.

## Important Build Rules
Top-level subdirectories are included for AtomISP2, IFS, INT1092 SAR, INT3472, PMC, PMT, Speed Select, telemetry, WMI, and uncore frequency. Standalone files are collected into `intel-target-*`, then the `INTEL_OBJ_TARGET` macro wraps each object as an `intel-<target>.o` module, producing module names such as `intel-hid`, `intel-bytcrc-pwrsrc`, and `intel-plr-tpmi`.

## Control Flow
This is Kbuild control flow. The basename of each selected target becomes both the inner object and the wrapped object assignment, so `intel-target-$(CONFIG_INTEL_HID_EVENT) += hid.o` expands into `intel-hid-y := hid.o` and `obj-* += intel-hid.o`.

## State And Persistence
No runtime state. The generated object graph is determined by `.config`.

## Dependencies And Integration Points
Must stay synchronized with the Kconfig symbols and source filenames in this directory and child directories.

## Risks And Test Signals
Risks include stale object names, wrapping behavior that surprises module naming, and child directories selected without their provider symbols. Test with `make V=1 drivers/platform/x86/intel/` under built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/Makefile -->
