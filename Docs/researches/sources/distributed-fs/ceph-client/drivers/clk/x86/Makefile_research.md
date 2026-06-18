<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/x86/Makefile

## Purpose

The x86 clock Makefile selects AMD FCH, Intel LPSS/PMC Atom, and LGM CGU clock drivers.

## Important APIs, Types, And Functions

`CONFIG_X86_AMD_PLATFORM_DEVICE` builds `clk-fch.o`; `CONFIG_X86_INTEL_LPSS` builds Atom LPSS and PMC platform clock drivers; `CONFIG_CLK_LGM_CGU` builds CGU common, PLL, and LGM inventory objects.

## Control Flow

Kbuild links the chosen objects. FCH/LPSS/PMC drivers are built-in platform drivers; LGM is also built-in via platform driver.

## State And Persistence Behavior

No runtime state exists here. Object grouping ensures common LGM helpers link with the SoC table file.

## Dependencies And Integration Points

It integrates x86 platform-device clock support with the common clock framework.

## Risks And Test Signals

Risks are config/object mismatch causing missing helper symbols. Build all three config families and test probe on AMD ST, Intel Atom, and LGM platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/x86/Makefile -->
