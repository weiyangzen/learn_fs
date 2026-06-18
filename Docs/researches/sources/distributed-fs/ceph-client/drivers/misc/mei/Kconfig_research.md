# sources/distributed-fs/ceph-client/drivers/misc/mei/Kconfig

## Purpose
This Kconfig file defines the Intel MEI driver family and feature modules for PCI ME, TXE, GSC, CSC, VSC, late binding, HDCP, PXP, and GSC proxy support.

## Important APIs, Types, and Functions
Symbols include `INTEL_MEI`, `INTEL_MEI_ME`, `INTEL_MEI_TXE`, `INTEL_MEI_GSC`, `INTEL_MEI_CSC`, `INTEL_MEI_VSC_HW`, `INTEL_MEI_VSC`, and `INTEL_MEI_LB`. It sources sub-Kconfigs for `hdcp`, `pxp`, and `gsc_proxy`.

## Control Flow
Selecting `INTEL_MEI` enables the core `/dev/mei` infrastructure. Subsymbols pull in hardware transports and MEI bus clients depending on PCI, ACPI/SPI, graphics driver availability, and platform type.

## State and Persistence
No runtime state is stored; the file controls build-time availability.

## Dependencies and Integration Points
Integrates MEI with PCI, X86 defaults, Intel graphics drivers (`i915`/`xe`), ACPI/SPI VSC transport, and downstream MEI client drivers.

## Risks
Dependency expressions gate which MEI services exist. Graphics-related MEI clients must avoid enabling when the needed DRM driver is unavailable except for compile testing.

## Test Signals
Signals are correct Kconfig dependency resolution across x86, compile-test, built-in, and module builds, plus inclusion of sourced HDCP/PXP/GSC proxy menus.
