# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/ipu3-cio2.c

## Purpose
This is the Intel IPU3 CIO2 PCI capture driver. It exposes four CSI-2 receiver queues as V4L2 video devices and bridge subdevices, programs CIO2 CSI/MIPI/DMA registers, manages videobuf2 DMA-SG buffers through hardware FBPT/LOP tables, binds firmware-described camera sensors through the async notifier, and handles runtime and system power management.

## Important APIs, types, and functions
The file-local `formats[]` table maps supported RAW10/Y10 media-bus codes to IPU3 packed V4L2 fourccs. `cio2_find_format()` and `cio2_bytesperline()` drive format negotiation. FBPT setup is handled by `cio2_fbpt_init_dummy()`, `cio2_fbpt_entry_init_dummy()`, `cio2_fbpt_entry_init_buf()`, and `cio2_fbpt_entry_enable()`. Hardware setup and teardown are `cio2_hw_init()` and `cio2_hw_exit()`. IRQ paths are `cio2_irq()`, `cio2_irq_handle_once()`, `cio2_buffer_done()`, and `cio2_queue_event_sof()`. The vb2 operations queue, prepare, start, and stop capture through `cio2_vb2_*`; V4L2 ioctl and subdev pad operations implement format enumeration, validation, and frame-sync events. PCI entry points are `cio2_pci_probe()` and `cio2_pci_remove()`.

## Control flow and integration points
Probe first calls `ipu_bridge_init()` so missing firmware graph endpoints can be synthesized from ACPI SSDB data, then enables the PCI device, maps BAR0, enables MSI, allocates dummy DMA pages, registers media/V4L2 devices, creates four queue/subdev/video entities, requests the IRQ, and registers async sensor matches. A successful sensor bind fills `q->sensor`, CSI-2 port/lane metadata, and the per-port register base. Streaming starts from vb2: runtime PM resumes the PCI device, the media pipeline starts, CIO2 CSI/MIPI/PBM/LTR/DMA registers are programmed from active subdev format and sensor link frequency, then the remote sensor is asked to stream. Completion interrupts advance the circular FBPT queue, mark vb2 buffers done, and queue SOF frame-sync events.

## State, persistence, and dependencies
Persistent driver state lives in `struct cio2_device` and `struct cio2_queue`: current queue, streaming flag, media graph objects, active capture format, FBPT memory, queued buffer ring, dummy LOP/page safety net, frame sequence, and async notifier. Hardware state is transient MMIO programming and D0I3 runtime power state. Dependencies include PCI/MSI, DMA coherent allocation, vb2 DMA-SG, V4L2/media controller, fwnode endpoint parsing, `v4l2_get_link_freq()`, and the Intel IPU bridge.

## Risks and test signals
Risks are FBPT/LOP DMA ordering, ring index races around DMA read pointer, bad link-frequency timing, unsupported format/lane combinations, incorrect media graph validation, stale buffers across suspend, and unbalanced runtime PM on start failures. Test signals include successful probe with media graph links, `/dev/video*` and subdev nodes, `v4l2-ctl --stream-mmap` capture, SOF events, sensor stream on/off, no CSI2/DMA error logs, suspend/resume while streaming, buffer payload lengths matching `sizeimage`, and no DMA halt after queued-buffer churn.
