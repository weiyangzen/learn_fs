# sources/distributed-fs/ceph-client/drivers/watchdog/omap_wdt.h

## Purpose
`omap_wdt.h` defines OMAP watchdog register offsets, timeout bounds, prescaler value, and conversion macros used by `omap_wdt.c`.

## Important APIs, types, and functions
Key definitions include offsets for `REV`, `CNTRL`, `CRR`, `LDR`, `TGR`, `WPS`, and `SPR`; timeout bounds `TIMER_MARGIN_MIN/DEFAULT/MAX`; prescaler `PTV`; and macros `GET_WLDR_VAL(secs)` and `GET_WCCR_SECS(val)`.

## Control flow
There is no runtime control flow. The driver uses these constants to wait on posted-write status bits, write load/reload/control registers, and convert seconds to/from the 32 kHz counter domain.

## State and persistence
The header describes MMIO state and conversion policy. Timeout limits are software policy, not persistent state.

## Dependencies and integration points
It is private to the OMAP watchdog driver and assumes the non-secure 32 kHz watchdog register layout and `PTV == 0` conversion.

## Risks and test signals
Risks include conversion overflow for future larger timeout limits and mismatch with SoC variants using different prescalers or layouts. Test signals include compile coverage, boundary conversions for min/default/max timeout, and get-timeleft/load round trips.
