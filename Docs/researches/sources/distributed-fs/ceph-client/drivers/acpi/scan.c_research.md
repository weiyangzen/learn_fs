# sources/distributed-fs/ceph-client/drivers/acpi/scan.c

## Purpose

`scan.c` turns ACPI namespace nodes into Linux `struct acpi_device` objects, attaches ACPI scan handlers and regular device drivers, coordinates hotplug/eject, tracks dependency deferral, and performs ACPI-specific DMA/IOMMU and resource setup. It is one of the core files connecting ACPICA namespace data to the Linux driver model.

## Important APIs, types, and functions

Global state includes `acpi_dep_list`, `acpi_scan_lock`, `acpi_scan_handlers_list`, `acpi_device_lock`, `acpi_wakeup_device_list`, the hotplug context lock, and a deferred system-device resource list. Exported scan/lifetime APIs include `acpi_scan_lock_acquire()`, `acpi_scan_lock_release()`, `acpi_initialize_hp_context()`, `acpi_fetch_acpi_dev()`, `acpi_get_acpi_dev()`, `acpi_device_hid()`, `acpi_bus_scan()`, `acpi_bus_trim()`, `acpi_bus_register_early_device()`, dependency helpers, DMA helpers, and reconfiguration notifier registration. Key internal flows are `acpi_add_single_object()`, `acpi_bus_check_add()`, `acpi_bus_attach()`, `acpi_scan_postponed()`, and `acpi_device_hotplug()`.

## Control flow

Initialization in `acpi_scan_init()` registers ACPI subsystem scan handlers, handles STAO/SPCR UART hiding, applies masked GPE settings, then scans from `ACPI_ROOT_OBJECT` under `acpi_scan_lock`. `acpi_bus_scan()` performs a two-pass walk: first it creates devices without unmet dependencies and records dependency-blocked branches, then it initializes MIPI CSI-2 software nodes, attaches created devices, and scans postponed branches. Device creation initializes PNP IDs, status, properties, flags, power/wakeup data, DMA coherency, and Linux device registration. Attachment evaluates `_EJD`, status, readiness, EC opregions, scan handlers, driver binding, platform-device default enumeration, and child recursion. Hotplug events run under both device-hotplug and ACPI scan locks, map ACPI notify codes to bus/device checks or eject, offline physical devices, detach handlers/drivers, evaluate `_LCK`/`_EJ0`, post `_OST`, and rescan if needed.

## State and persistence

ACPI device objects are dynamically allocated, attached to namespace handles with `acpi_attach_data()`, reference-counted through the Linux device model, and invalidated with `INVALID_ACPI_HANDLE` during namespace deletion. Bus ID allocation is tracked with per-HID IDAs. Wake-capable devices are linked into `acpi_wakeup_device_list`. `_DEP` records persist in `acpi_dep_list` until suppliers clear them or postponed scanning marks them for deletion. Power resource lists, PNP IDs, software-node properties, and physical-node links are owned by each `struct acpi_device` and released through `acpi_device_release()`.

## Dependencies and integration points

This file integrates with ACPICA namespace walking/evaluation, Linux device core, platform and auxiliary buses, ACPI power resources, EC opregions, dock/container/memory/processor/PCI init, MIPI DisCo for Imaging, IORT/RIMT/VIOT IOMMU configuration, DMA mapping, sysfs hotplug profiles, and ACPI reconfiguration notifiers. It also consumes `sleep.h` globals for wakeup device lists and power-resource resume.

## Risks

The highest-risk areas are lock ordering (`acpi_scan_lock`, device hotplug lock, dependency lock, physical-node lock), asynchronous deletion of namespace-backed devices, dependency deferral races, and hotplug eject rollback. Enumeration policy is full of platform exceptions: SPCR/STAO UART hiding, serial-bus slaves enumerated by parents, Apple property-based bus hints, ACPI video auxiliary devices, and ignored/honored `_DEP` HIDs. DMA/IOMMU setup intentionally ignores most IOMMU errors except probe deferral; changing that can break boot on partially described firmware.

## Test signals

Signals include boot-time ACPI namespace enumeration, hotplug bus/device/eject events with `_OST` status, dependency deferral and supplier-clear ordering, driver binding for scan-handler and platform-device paths, ACPI wakeup list population, DMA range parsing from `_DMA`, IOMMU probe deferral behavior, SPCR UART hiding when STAO requests it, and resource reservation after PCI BAR claiming.
