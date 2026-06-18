# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2.h

## Purpose
This header declares the AtomISP CSI2 subdevice interface, pad indices, per-port device structure, entity lifecycle functions, ACPI/software-node bridge entry points, and stream-time receiver configuration hook.

## Important APIs and Types
`CSI2_PAD_SINK`, `CSI2_PAD_SOURCE`, and `CSI2_PADS_NUM` define topology. `struct atomisp_mipi_csi2_device` embeds a V4L2 subdev, pads, active formats, control handler, and `atomisp_device` pointer. Functions cover format setting, init/cleanup, registration, firmware parsing, and CSI2 configuration.

## Control Flow
Probe initializes CSI2 entities with `atomisp_mipi_csi2_init()`, firmware parsing registers async sensor matches, media registration calls the register helper, and stream start calls `atomisp_csi2_configure()`.

## State and Persistence
CSI2 state is per embedded `atomisp_mipi_csi2_device` in `atomisp_device`. Active formats persist in the device struct; try formats live in V4L2 framework state.

## Dependencies and Integration Points
Includes GPIO/property and V4L2 subdev/control headers plus AtomISP UAPI definitions. `atomisp_internal.h` includes it so the main device can embed CSI2 ports.

## Risks
Fixed port and pad counts must match hardware and firmware graph parsing. New CSI2 controls would need control-handler lifetime updates.

## Test Signals
Build integration, media pad counts, subdev registration for every port, async sensor-port matching, and stream-time receiver configuration validate this header.
