# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2_bridge.c

## Purpose
This file builds the firmware/software-node camera graph for AtomISP2 sensors described by ACPI and wires sensors into the V4L2 async notifier. It supplies missing port, lane, clock, GPIO, orientation, and optional VCM data.

## Important APIs and Functions
`atomisp_csi2_bridge_init()` calls `ipu_bridge_init()` and intentionally leaves successful software nodes attached. `atomisp_csi2_parse_sensor_fwnode()` derives sensor link properties. Helpers read Intel DSM data, DMI overrides, ACPI `_PR0` clock resources, set PMC clock rate, add INT3472-style GPIO mappings, and read VCM type. Async notifier callbacks bind sensors and call `atomisp_register_device_nodes()` on completion. `atomisp_csi2_bridge_parse_firmware()` parses graph endpoints and records lane counts.

## Control Flow
Bridge init exits early if a secondary fwnode already exists, otherwise `ipu_bridge_init()` discovers sensors and calls the AtomISP parser. Parsing applies HID defaults, `_PR0` clock-derived defaults, DMI/DSM overrides, lane validation, GPIO mappings, mclk/orientation, and optional VCM type. Firmware parsing initializes the notifier, walks endpoints by port, parses CSI2 properties, stores `isp->sensor_lanes[]`, and adds async remote fwnode matches.

## State and Persistence
Software nodes and faux INT3472 GPIO mapping objects are intentionally leaked for boot lifetime. Sensor binding persists in `isp->sensor_subdevs[port]`; lane counts persist in `isp->sensor_lanes[]`; async connections are notifier-owned.

## Dependencies and Integration Points
Depends on ACPI, DMI, clk, INT3472 helpers, `ipu_bridge`, V4L2 fwnode parsing, AtomISP internals, and device-node registration. It is called by CSI2 initialization and feeds later media graph setup.

## Risks
Wrong firmware quirks can select incorrect port/lane counts. Intentional leaks are acceptable only after successful one-time setup. GPIO mapping depends on ACPI CRS semantics. Some VCMs are disabled due to stream failures. Endpoint handle release on error paths must remain correct.

## Test Signals
Boot on ACPI systems without native graph data, DMI override validation, 19.2 MHz PMC clock programming, GPIO mappings visible to sensors, one sensor bound per port, lane counts from endpoints, and successful notifier completion/device-node registration are key signals.
