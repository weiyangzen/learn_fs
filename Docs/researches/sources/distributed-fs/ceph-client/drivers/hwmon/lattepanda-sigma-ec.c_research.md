# sources/distributed-fs/ceph-client/drivers/hwmon/lattepanda-sigma-ec.c

## Purpose
`lattepanda-sigma-ec.c` is a DMI-gated platform hwmon driver for the LattePanda Sigma embedded controller. It bypasses the ACPI EC driver because firmware declares the EC disabled and exposes CPU fan RPM plus board and CPU temperatures via direct ACPI EC I/O ports.

## Important APIs, types, and functions
The driver uses DMI matching, module parameters, raw port I/O, I/O region reservation, platform device self-registration, and hwmon `with_info`. `ec_wait_ibf_clear()` and `ec_wait_obf_set()` poll the EC status register. `ec_read_reg()` performs the EC read protocol. `ec_read_reg16()` reads paired high/low registers with a high-byte recheck to avoid rollover corruption. `lps_ec_read()` and `lps_ec_read_string()` implement hwmon operations.

## Control flow
Module init requires an exact LattePanda Sigma DMI and BIOS version 5.27 match unless `force=1` is supplied for vendor/product-only matching. It registers a platform driver and synthetic platform device. Probe reserves ports `0x62` and `0x66`, sanity-checks EC responsiveness by reading fan duty, and registers hwmon. Runtime reads directly poll EC status and read registers for fan RPM or temperatures.

## State and persistence
There is no per-device runtime data and no caching. All sensor values are read on demand. The driver performs no EC writes except command/register selection for reads. I/O port ownership is devm-managed during probe and released with the platform device.

## Dependencies and integration points
It depends on x86 ACPI EC-compatible ports being free, DMI strings matching known hardware, and the BIOS-specific EC register map. It intentionally does not use ACPI global locks because the kernel ACPI EC subsystem is not initialized on this system.

## Risks
The direct EC protocol is BIOS-version-specific. Loading with `force=1` on a different EC map can read undefined registers. Busy-wait polling can spin for up to 25 ms on failures. The comment assumes no concurrent firmware EC access; if firmware behavior changes, raw port access could race. No writes are exposed, limiting damage to reads and command traffic.

## Test signals
Test exact DMI acceptance, force-mode acceptance, nonmatching DMI refusal, port request conflicts, EC timeout paths, 16-bit RPM rollover handling, labels and values for all three channels, and behavior on BIOS versions other than 5.27 only with explicit force.
