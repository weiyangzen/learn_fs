# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_pci.h

## Purpose

`aic79xx_pci.h` defines the 64-bit PCI/subsystem identity constants and masks used by the AIC79xx PCI OS glue and hardware configuration code. It is a small data header that keeps known adapter IDs separate from attach logic.

## Important APIs, Types, and Functions

- Mask constants include `ID_ALL_MASK`, `ID_ALL_IROC_MASK`, `ID_DEV_VENDOR_MASK`, `ID_9005_GENERIC_MASK`, and `ID_9005_GENERIC_IROC_MASK`.
- Device identity constants cover AIC7901, AIC7901A, AIC7902, AIC7902_B, and retail/OEM AHA-29320/AHA-39320 variants, including Dell and HP subsystem IDs.
- No functions or types are declared in this file.

## Control Flow and State

The header contributes no runtime flow. Its constants are consumed by the Linux `pci_device_id` table in `aic79xx_osm_pci.c` and the core identity table in `aic79xx_pci.c`. The constants encode device/vendor/subdevice/subvendor in the ordering expected by `ahd_compose_id()` and ID table macros.

## Dependencies and Integration Points

The file depends only on integer literal support. It integrates with PCI matching, hardware identity lookup, and generic probe masks. Consistency between these constants and Linux `ID()`, `ID16()`, `ID2C()`, and `IDIROC()` macros elsewhere is required.

## Risks

- A malformed 64-bit ID silently prevents binding or binds the wrong setup routine.
- Generic masks can match devices broader than intended, especially when HostRAID/IROC bits are masked.
- Adding new OEM IDs requires updates in both the Linux PCI table and the core identity table if the device needs a specific name or setup path.

## Test Signals

- Build-time use in both ID tables.
- Runtime `lspci`-matched devices should bind to the expected adapter name in driver logs.
- Generic ID fallback should bind unknown but compatible AIC790x devices without stealing unrelated Adaptec devices.
