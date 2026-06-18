<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/solos-attrlist.c -->
# sources/distributed-fs/ceph-client/drivers/atm/solos-attrlist.c

## Purpose

This file is an include-time attribute list for `solos-pci.c`. It enumerates Solos modem parameter names once and lets the parent source expand them first into `DEVICE_ATTR` declarations and later into an attribute pointer array.

## Important APIs, types, and functions

There are no functions or standalone data definitions. The file relies on caller-defined macros `SOLOS_ATTR_RO(name)` and `SOLOS_ATTR_RW(name)`. Read-only attributes include version, status, bitrate, line quality, vendor, error, and counter fields. Read-write attributes include `Action`, `ActivateLine`, `HostControl`, `AutoStart`, `Failsafe`, `ShowtimeLed`, `Retrain`, `Defaults`, line/profile settings, noise detection, and SNR/margin controls.

## Control flow

The C preprocessor includes this file twice from `solos-pci.c`: once to emit `static DEVICE_ATTR(...)` objects and once to populate `solos_attrs[]`. At runtime all attributes share `solos_param_show()` and optional `solos_param_store()`, which send command packets to firmware and wait for responses.

## State and persistence behavior

The file itself stores no state. The attributes expose and mutate firmware-side modem state through command packets, so user writes may persist in device firmware depending on firmware semantics.

## Dependencies and integration points

It depends entirely on the macro context supplied by `solos-pci.c` and integrates with sysfs groups named `parameters` on each ATM device.

## Risks

Because names become sysfs ABI, renaming or changing RO/RW status can break userspace. The macro-include pattern is compact but fragile: including the file without defining the macros will not compile, and adding an attribute with invalid identifier characters is impossible through this pattern.

## Test signals

Compile `solos-pci.c`, enumerate `/sys/class/atm/*/parameters/`, confirm every listed attribute appears with expected mode, and test representative read/write commands with firmware responses `OK`, `ERROR`, timeout, and unexpected payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/atm/solos-attrlist.c -->
