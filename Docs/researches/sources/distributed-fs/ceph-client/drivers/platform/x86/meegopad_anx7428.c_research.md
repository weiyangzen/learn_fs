<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/meegopad_anx7428.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/meegopad_anx7428.c

## Purpose
This I2C driver powers on the Analogix ANX7428 USB Type-C crosspoint switch on MeeGoPad T8/T9 Cherry Trail boxes. Firmware leaves the chip powered off, so the driver asserts GPIOs and waits for the on-chip microcontroller.

## Important APIs, Types, And Functions
The driver defines ACPI GPIO mappings for `enable-gpios` and `reset-gpios`, a DMI allowlist for the MeeGoPad board, and an ACPI match for `ANXO7418` even though the hardware is ANX7428. `anx7428_probe()` performs board gating, GPIO sequencing, `TX_STATUS` polling for `OCM_STARTUP`, and vendor/device ID reads.

## Control Flow
Probe refuses unknown boards unless `force=1`. It adds ACPI GPIO mappings, obtains enable GPIO high, waits 10 ms, obtains reset GPIO low, polls `TX_STATUS` up to 50 ms, then reads `VENDOR_ID` and `DEVICE_ID` registers for diagnostics.

## State And Persistence
The driver keeps no runtime state after probe. GPIO descriptors are devm-managed but only used for power sequencing. The ANX7428 autonomous firmware owns Type-C and DisplayPort behavior after startup.

## Dependencies And Integration Points
It depends on ACPI-enumerated I2C, DMI matching, gpiolib ACPI mapping, SMBus byte/word reads, and delay/poll helpers. It intentionally does not integrate with USB Type-C role or alternate-mode frameworks.

## Risks And Edge Cases
The DMI allowlist uses generic firmware strings, so `force` exists for unknown boards but can power unexpected hardware. GPIO sequencing is undocumented and copied from downstream sources. Failure to start OCM means no Type-C switching. The ACPI ID mismatch may surprise maintainers.

## Test Signals
Validation should include DMI allow/deny behavior, force probing, GPIO sequencing on a scope or trace, OCM startup polling, ID register reads, and USB3/DisplayPort functionality after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/meegopad_anx7428.c -->
