# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/ipu3-cio2.h

## Purpose
This header is the hardware and software contract for the IPU3 CIO2 driver. It defines CIO2 identity constants, image limits, queue sizes, MMIO register offsets and bit fields, CSI-2 timing coefficients, FBPT layout, and the core per-device/per-queue/per-buffer structures used by `ipu3-cio2.c`.

## Important APIs, types, and definitions
Important constants include `CIO2_PCI_ID`, `CIO2_DMA_MASK`, `CIO2_IMAGE_MAX_WIDTH/HEIGHT`, `CIO2_MAX_LOPS`, `CIO2_MAX_BUFFERS`, `CIO2_NUM_PORTS`, `CIO2_QUEUES`, and `CIO2_DMA_CHAN`. Register macros cover CSI receiver, MIPI backend, interrupt control, PBM, LTR, DMA channel registers, and pixel formatter state. `struct cio2_csi2_timing`, `struct cio2_buffer`, `struct csi2_bus_info`, `struct cio2_queue`, `struct cio2_device`, and packed `struct cio2_fbpt_entry` define driver state and DMA ABI. Inline helpers map V4L2 files and vb2 queues back to `struct cio2_queue`.

## Control flow and integration points
The `.c` file relies on these definitions when allocating DMA tables, calculating timing register values, programming MMIO blocks, decoding interrupts, validating media links, and walking queue rings. The packed FBPT structure is read and modified by both CPU and CIO2 DMA, so field order and size are part of the hardware interface. The device and queue structs tie together Linux PCI, media controller, V4L2 subdev, video_device, and vb2 subsystems.

## State, persistence, and dependencies
This header does not persist data by itself, but it defines every persistent in-memory object owned by the driver. Coherent dummy buffers and FBPTs are represented by DMA handles stored in `cio2_device` and `cio2_queue`. The macros depend on Linux bit, DMA, media, V4L2, and vb2 headers and on page-size assumptions for LOP and FBPT sizing.

## Risks and test signals
The main risks are ABI drift in the packed FBPT, incorrect register masks/shifts, wrong queue sizing derived from `PAGE_SIZE`, invalid DMA mask assumptions, and stale constants for CIO2 timing or interrupt layout. Build coverage for all include paths, sparse/packed-struct warnings, probe/register readback, streaming DMA completion, interrupt decoding, and suspend/resume buffer survival are the best signals.
