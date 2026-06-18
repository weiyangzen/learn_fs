# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi_version.h

## Purpose

`hpi_version.h` centralizes the HPI driver and library version constants used by the AudioScience driver and firmware loader.

## Important APIs, types, and functions

It defines `HPI_VER` as `HPI_VERSION_CONSTRUCTOR(4, 14, 3)`, `HPI_VER_STRING` as `"4.14.03"`, `HPI_LIB_VER` as `HPI_VERSION_CONSTRUCTOR(10, 4, 0)`, plus helpers `HPI_VERSION_CONSTRUCTOR(maj, min, r)`, `HPI_VER_MAJOR(v)`, `HPI_VER_MINOR(v)`, and `HPI_VER_RELEASE(v)`.

## Control flow

There is no runtime control flow. Consumers expand these macros to compare or display versions. `hpidspcd.c` uses the major version to reject incompatible firmware images and logs a warning when the full DSP image version differs from `HPI_VER`.

## State and persistence behavior

The header stores no mutable state. Version values are compile-time constants embedded into the driver. They become compatibility gates against firmware metadata and can affect whether an adapter boots.

## Dependencies and integration points

The file is included by the DSP-code loader and can be used by HPI API/reporting code. It must stay aligned with firmware file headers generated for `asihpi/dsp*.bin` images and with documented library API versions.

## Risks and test signals

Risks include forgetting to update the version when host/DSP protocol changes, accidental octal literals if leading zeroes are used, and major-version mismatches that prevent firmware loading. Test signals are firmware load acceptance/rejection, mismatch warnings for non-identical minor/release versions, version reporting through subsystem APIs, and build checks for macro extraction.
