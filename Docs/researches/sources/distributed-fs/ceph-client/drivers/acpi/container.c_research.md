# sources/distributed-fs/ceph-client/drivers/acpi/container.c

## Purpose
Registers ACPI generic container devices and wires them into Linux container hotplug handling. Containers represent hotpluggable physical groupings such as chassis, docks, or processor/memory containers, depending on firmware.

## Important APIs, Types, And Functions
The handler matches `ACPI0004`, `PNP0A05`, and `PNP0A06`. With `CONFIG_ACPI_CONTAINER`, `container_device_attach()` creates a `struct container_dev` and registers a device on `container_subsys`; `acpi_container_offline()` verifies that all dependent child devices are offline; `container_device_detach()` unregisters the container; and `container_device_online()` emits `KOBJ_ONLINE`. Without `CONFIG_ACPI_CONTAINER`, only a scan handler with hotplug name `"container"` is registered.

## Control Flow
`acpi_container_init()` registers the scan handler during ACPI scan setup. In the full container configuration, attach ignores dock stations, allocates a `container_dev`, sets the ACPI companion, assigns release/offline callbacks, registers the device, and stores it in `adev->driver_data`. Hotplug configuration enables demand-offline and online notification. Detach clears driver data and unregisters the device.

## State And Persistence
State is per attached ACPI container: a dynamically allocated `container_dev` and a `driver_data` link from the ACPI device. Offline readiness is computed dynamically by walking ACPI children with `acpi_scan_is_offline()`.

## Dependencies And Integration Points
Depends on ACPI scan handlers, ACPI child iteration from `bus.c`, `linux/container.h`, the container subsystem bus, and ACPI hotplug. Dock integration is explicit: dock stations are skipped to avoid creating a generic container device for them.

## Risks
Incorrect offline decisions can block or allow unsafe hot-removal. The attach path returns `1` on successful attachment, matching ACPI scan-handler conventions; callers must preserve that semantic. The non-`CONFIG_ACPI_CONTAINER` path still registers hotplug handling, so behavior differs based on kernel configuration.

## Test Signals
Expected signals are container devices appearing under the container subsystem for matching ACPI IDs, hotplug demand-offline calls refusing busy children, online uevents after attach, and no generic container device for ACPI dock stations. Tests should cover both `CONFIG_ACPI_CONTAINER` enabled and disabled builds.
