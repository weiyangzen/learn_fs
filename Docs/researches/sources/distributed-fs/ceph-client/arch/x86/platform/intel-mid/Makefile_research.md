<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/Makefile

## Purpose
Builds Intel MID platform setup and PWRMU support when `CONFIG_X86_INTEL_MID` is enabled.

## Important APIs, Types, And Functions
The object list is `intel-mid.o pwr.o`.

## Control Flow
Kbuild includes both early platform override code and PCI PWRMU code as a unit for Intel MID kernels.

## State And Persistence
No runtime state exists in the Makefile.

## Dependencies And Integration Points
Depends on x86 platform selection and the Intel MID PCI/power-management code that consumes symbols from these objects.

## Risks And Edge Cases
Splitting the two objects under different symbols would risk missing power-off or PCI platform PM hooks. Current coupling keeps the platform coherent.

## Test Signals
Successful build with `CONFIG_X86_INTEL_MID=y` and link resolution for Intel MID PM symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/Makefile -->
