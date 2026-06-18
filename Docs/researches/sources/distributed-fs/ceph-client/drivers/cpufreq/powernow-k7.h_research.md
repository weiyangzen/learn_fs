<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.h

## Purpose

Defines the AMD K7 FID/VID control and status MSR layouts consumed by `powernow-k7.c`.

## APIs, Types, And Functions

`union msr_fidvidctl` maps control fields for target FID, VID, change command bits `FIDC`/`VIDC`, `FIDCHGRATIO`, and `SGTC`. `union msr_fidvidstatus` maps current, start, and maximum FID/VID fields from the status MSR. The unions expose both bitfield views and a 64-bit `val` for `rdmsrq()`/`wrmsrq()`.

## Control Flow

The header has no executable control flow. Callers read a status MSR into `msr_fidvidstatus`, derive current or limit fields, update `msr_fidvidctl.bits`, and write the combined value back to request hardware transitions.

## State And Persistence

No software state is stored here. The definitions describe persistent processor MSR state owned by hardware.

## Dependencies And Integration Points

Integrated only by the K7 PowerNow driver and the x86 MSR accessors. Field widths and ordering are part of the ABI between the driver and AMD hardware.

## Risks And Test Signals

Bitfield layout correctness is the main risk; any compiler/architecture mismatch or wrong field width would write unsafe voltage/frequency requests. Test signals come indirectly from K7 driver transitions: status reads must reflect requested `FID`/`VID`, and SGTC-controlled transitions must complete without hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.h -->
