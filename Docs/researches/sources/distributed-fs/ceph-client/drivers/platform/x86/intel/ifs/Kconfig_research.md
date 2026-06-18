<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Kconfig

## Purpose
Defines `INTEL_IFS`, the Intel In Field Scan driver option.

## Important Symbol
`INTEL_IFS` is a tristate depending on x86, Intel CPU support, 64-bit, and SMP. It builds module `intel_ifs`.

## Control Flow And State
No runtime flow. Build selection determines whether the IFS misc devices can be registered on CPUs advertising the required integrity capability MSRs.

## Dependencies And Integration Points
The dependency set matches IFS runtime assumptions: Intel x86 CPUs, SMP core sibling coordination, and 64-bit MSR paths.

## Risks And Test Signals
Risks are enabling on unsupported CPUs or missing feature-guarded build dependencies. Test with target Intel server CPUs and negative boots on unsupported x86 systems where probe should return `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/Kconfig -->
