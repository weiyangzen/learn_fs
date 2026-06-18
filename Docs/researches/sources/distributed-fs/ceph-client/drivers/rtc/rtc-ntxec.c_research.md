# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ntxec.c

Purpose: implements RTC date/time access for the Netronix embedded controller MFD used in e-book readers.

Important APIs/types/functions: `struct ntxec_rtc` stores the platform device and parent `struct ntxec`. `ntxec_read_time()` reads packed year/month, day/hour, and minute/second registers through the parent regmap, with a retry if minute/second changed. `ntxec_set_time()` writes a `reg_sequence` using `regmap_multi_reg_write()` and `ntxec_reg8()` encoding.

Control flow: probe inherits the OF node from the parent, allocates private data, gets the parent EC driver data, allocates an RTC, sets ops and 2000-2255 range, and registers. Read-time reads minute/second first, then day/hour and year/month, then re-reads minute/second; if either changed, it restarts from the beginning to avoid cross-field rollover. Set-time writes seconds as zero first, then year/month/day/hour/minute, then final seconds, preventing rollover while multi-register writes are in progress.

State and persistence: all RTC state lives in the embedded controller registers. Driver state has only the EC pointer. No alarm, IRQ, wakeup, or local cache exists.

Dependencies and integration: depends on the Netronix EC MFD, parent regmap, platform subdevice `ntxec-rtc`, and RTC class. The driver reuses the parent OF node for binding/metadata.

Risks and test signals: read retry can loop indefinitely if the EC returns unstable minute/second values. The register interface uses binary bytes rather than BCD. No validity flag is checked for backup-battery or EC time initialization. Test consistent retry around minute rollover, multi-write ordering, parent regmap errors, 2255 upper range, and absence of alarm/update features.
