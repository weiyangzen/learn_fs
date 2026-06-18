# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_internal.h

## Purpose
This header defines AtomISP's central internal device model, hardware IDs, timeout and queue sizing constants, input descriptors, saved register state, DFS mode, and `struct atomisp_device`.

## Important APIs and Types
It defines PCI IDs/revision macros, image dimension limits, queue depths, event counts, timeout durations, raw-frame/stat/metadata sizing, `struct atomisp_input_subdev`, `enum atomisp_dfs_mode`, `struct atomisp_regs`, `struct atomisp_device`, and `v4l2_dev_to_atomisp_device()`.

## Control Flow
The header shapes probe and runtime control flow: setup fills `atomisp_device`, initializes CSI2 ports and the ISP subdev, loads firmware, parses sensors, and registers media/video nodes. Runtime modules pass this structure as shared context.

## State and Persistence
`atomisp_device` is persistent per PCI device. It owns V4L2/media devices, one ISP subdev, async notifier, firmware, MMIO base, CSS env, PM/QoS, CSI2 ports, sensor input tables, saved registers, fatal/error state, assert recovery work, DFS data, and CSS initialization state.

## Dependencies and Integration Points
Includes AtomISP platform, V4L2 media/async/subdev, IA CSS, CSI2/subdev/compat, GP device, IRQ, firmware, PM QoS, IDR, and vmalloc headers. It is included by most PCI driver modules.

## Risks
Broad includes and embedded concrete types make changes high-blast-radius. The single embedded `asd` encodes a one-ISP-subdev design. Very large max dimension constants rely on other code for practical bounds. Firmware timeout/queue constants must match CSS assumptions.

## Test Signals
Build coverage, probe on supported PCI IDs/revisions, media-device registration, async notifier setup, PM/QoS behavior, saved-register reset paths, and lockdep around mutex/spinlock fields.
