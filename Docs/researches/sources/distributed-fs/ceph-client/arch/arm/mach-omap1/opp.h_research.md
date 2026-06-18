<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp.h

## Purpose
Defines the OMAP1 MPU operating-point/rate-table structure shared by clock setup code and the OMAP1 rate data file.

## Important APIs, Types, and Functions
Provides `struct mpu_rate` with MPU rate, crystal rate, PLL rate, CKCTL value, DPLL_CTL value, and flags, plus extern `omap1_rate_table[]`.

## Control Flow
No runtime flow. Clock code iterates the table declared here to select valid OMAP1 clock register settings.

## State and Persistence Behavior
No state in the header. It describes immutable rate-table entries held in `opp_data.c`.

## Dependencies and Integration Points
Uses Linux integer types and flag values such as `CK_1710`, `CK_16XX`, `CK_1510`, and `CK_7XX` from clock headers.

## Risks
Structure field order is hardware-sensitive: wrong CKCTL or DPLL_CTL values can destabilize CPU, DSP, peripheral, or LCD clocks.

## Test Signals
Build clock code that consumes `omap1_rate_table[]`; runtime cpufreq/clock tests should verify selected rates match crystal frequency and SoC flags.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/opp.h -->
