# sources/distributed-fs/ceph-client/drivers/scsi/libsas/Kconfig

## Purpose

This Kconfig file defines the build-time feature switches for the libsas helper library. It exposes the core SAS domain-device transport helper, optional libata/SATA support, and optional host-side SMP interpretation.

## Important APIs, Types, and Functions

The symbols are `SCSI_SAS_LIBSAS`, `SCSI_SAS_ATA`, and `SCSI_SAS_HOST_SMP`. `SCSI_SAS_LIBSAS` is a tristate depending on `SCSI` and selecting `SCSI_SAS_ATTRS`. `SCSI_SAS_ATA` is a bool depending on libsas and on libata being built-in or matching the libsas linkage, and it selects `SATA_HOST`. `SCSI_SAS_HOST_SMP` is a bool defaulting to yes when libsas is enabled.

## Control Flow

There is no runtime control flow. The symbols determine which objects the libsas Makefile links into `libsas.o`. The dependency `ATA = y || ATA = SCSI_SAS_LIBSAS` prevents building libsas ATA support in a linkage combination that cannot satisfy libata references.

## State and Persistence Behavior

The file persists only kernel configuration choices. Runtime state is created by the C files selected through these symbols.

## Dependencies and Integration Points

`SCSI_SAS_LIBSAS` integrates with the SCSI core and SAS transport attributes. `SCSI_SAS_ATA` integrates libsas with libata and SATA host infrastructure. `SCSI_SAS_HOST_SMP` integrates host-side SMP request handling used by the SAS transport BSG path.

## Risks and Edge Cases

The main risk is invalid build composition. Disabling `SCSI_SAS_ATA` removes SATA/STP support from libsas even if discovery sees SATA devices. Disabling `SCSI_SAS_HOST_SMP` saves a small amount of code but removes the virtual SMP interpreter for SAS hosts.

## Test Signals

Build matrix signals are core libsas as built-in/module, ATA enabled and disabled, host SMP enabled and disabled, and verification that selected symbols produce the expected objects and exported symbols without unresolved references.
