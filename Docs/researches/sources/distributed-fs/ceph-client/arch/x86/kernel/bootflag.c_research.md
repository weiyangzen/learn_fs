# sources/distributed-fs/ceph-client/arch/x86/kernel/bootflag.c

## Purpose
This file implements the Simple Boot Flag 2.0 CMOS update used during boot.

## Important APIs, Types, and Functions
`sbf_port` is set earlier by ACPI boot code. `sbf_read()` and `sbf_write()` serialize CMOS access with `rtc_lock`. `sbf_value_valid()` checks reserved bits and parity. `sbf_init()` validates and rewrites the flag, clearing BOOTING and DIAG and optionally setting PNPOS for ISA PnP.

## Control Flow
At `arch_initcall`, `sbf_init()` exits if no port was found, reads the CMOS byte, logs invalid values, masks reserved/status bits, sets policy bits, recalculates parity in `sbf_write()`, and writes back.

## State and Persistence
The only kernel variable is init-only `sbf_port`. The persistent state is the CMOS boot flag byte, which survives reboots and communicates boot status to firmware or other OS components.

## Dependencies and Integration Points
The file depends on ACPI discovery of the SBF CMOS port, RTC CMOS helpers, parity helpers, and optional ISA PnP configuration. It integrates with early architecture init and firmware boot status conventions.

## Risks and Test Signals
Risks include writing the wrong CMOS location, parity mistakes, or racing RTC access. Test signals include boot log messages, valid CMOS parity after boot, correct BOOTING/DIAG clearing, and no RTC/CMOS regressions on systems without SBF.
