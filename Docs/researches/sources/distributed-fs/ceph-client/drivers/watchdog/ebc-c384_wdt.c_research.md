# sources/distributed-fs/ceph-client/drivers/watchdog/ebc-c384_wdt.c

## Purpose
This ISA watchdog driver supports the WinSystems EBC-C384 SBC. It programs fixed I/O ports to select second or minute timeout resolution and pet/stop the hardware.

## Important APIs, types, and functions
The watchdog core callbacks are `ebc_c384_wdt_start`, `ebc_c384_wdt_stop`, and `ebc_c384_wdt_set_timeout`. Probe is through an `isa_driver` and allocates a `watchdog_device`. Module init gates registration on DMI board name `EBC-C384 SBC`.

## Control Flow
Init checks DMI, registers one ISA device, and probe reserves I/O range `0x564-0x568`. Set-timeout chooses seconds mode for values up to 255 and minute mode for larger values, rounding up to minute granularity. Start writes the encoded timeout to the pet port; stop writes zero. The watchdog core provides keepalive through `.start` because no explicit `.ping` is supplied.

## State and Persistence
State is held in the hardware I/O ports and the allocated watchdog object. The driver has no persistent storage and no explicit shutdown callback; `devm_watchdog_register_device` owns registration lifetime.

## Dependencies and Integration Points
It depends on DMI matching, ISA driver infrastructure, x86 I/O port access, `devm_request_region`, module timeout/nowayout parameters, and watchdog core.

## Risks and Test Signals
Risks include DMI false positives/negatives, second-to-minute rounding surprises, absence of explicit ping op, and fixed I/O port conflicts. Tests should cover DMI gating, port reservation failure, timeout boundaries at 255/256/15300 seconds, start/stop port writes, nowayout/magic close, and module unload.
