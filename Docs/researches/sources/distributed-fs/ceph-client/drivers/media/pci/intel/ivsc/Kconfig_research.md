# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_INTEL_VSC`, the Intel Visual Sensing Controller driver option.

## Important APIs, Types, And Data
`INTEL_VSC` is a tristate option titled "Intel Visual Sensing Controller". It depends on `INTEL_MEI`, `ACPI`, and `VIDEO_DEV`, and has an `IPU_BRIDGE || !IPU_BRIDGE` dependency to allow optional bridge integration without forcing that symbol. It selects `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, and `V4L2_FWNODE`.

## Control Flow
Selecting this option builds IVSC support split into ACE and CSI drivers. ACE controls sensor ownership between IVSC firmware and host CPU; CSI controls the CSI-2 link ownership, routing destination, and link configuration.

## State And Persistence
No runtime state exists in this build file. It controls module availability.

## Dependencies And Integration Points
The entry wires IVSC into MEI client devices, ACPI-described camera platforms, V4L2 subdev/media-controller infrastructure, and optional IPU bridge support.

## Risks And Test Signals
Misconfigured dependencies can build IVSC without required V4L2 fwnode/subdev support or hide it on valid platforms. Build tests should cover built-in and module configurations, with and without `IPU_BRIDGE`.
