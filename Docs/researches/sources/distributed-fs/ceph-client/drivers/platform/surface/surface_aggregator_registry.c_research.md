# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_aggregator_registry.c

## Purpose
Provides the SSAM platform/meta-hub registry for Surface devices whose SSAM clients cannot be auto-discovered. It defines software nodes for virtual SSAM devices and maps ACPI/OF platform IDs to model-specific node groups.

## Important APIs, Types, And Functions
The file defines many `struct software_node` instances following the `ssam:dd:cc:tt:ii:ff` naming scheme: root, KIP/base hubs, batteries, AC adapter, performance profile, thermal sensors, fan, tablet switches, DTX, and HID functions. Node groups cover generations and models including Surface Book, Surface Laptop, Surface Laptop Studio, Surface Laptop Go, Surface Pro Intel, and ARM/QCOM variants. Driver functions are `ssam_platform_hub_probe()` and `ssam_platform_hub_remove()`.

## Control Flow
Probe selects a node group from ACPI match data or OF machine match data, binds to the SSAM controller for ordering and access, registers the software-node group, sets the root software node as the platform device's secondary fwnode, and calls `__ssam_register_clients()` to instantiate SSAM child devices. Remove reverses this by removing clients, clearing the secondary fwnode, and unregistering the node group.

## State And Persistence Behavior
The registry stores only static const node definitions and the selected node-group pointer in platform driver data. No runtime state is persisted. Child-device lifetime is tied to software-node registration and platform hub binding.

## Dependencies And Integration Points
Depends on ACPI IDs, OF compatible matching, software nodes, property entries, platform bus, and SSAM device registration helpers. It is the source of virtual devices later consumed by drivers such as battery, HID, hub, tablet switch, performance profile, fan, and DTX drivers.

## Risks
Model mapping mistakes can instantiate missing, duplicate, or wrong SSAM clients. Some nodes with identical names intentionally appear under different parents; parent relationships must be preserved. New Surface models require careful ACPI/OF ID assignment and selection of fan/sensor/tablet-switch variants. Probe registers nodes before child creation and must clean up correctly on partial failure, which it does for missing root and child-registration failure.

## Test Signals
Test each ACPI ID and OF compatible maps to the intended node group, software nodes register/unregister cleanly, child devices appear with expected modaliases, parented hub children register only under their hub, probe defer occurs when controller is absent, and remove unloads all child clients.
