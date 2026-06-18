<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-core.c

Purpose: PCI core for the NXP SAA7164 bridge driver. It owns module parameters, PCI probe/remove, MMIO resource mapping, MSI/shared IRQ setup, firmware boot handoff, board detection, port initialization, debugfs, and top-level registration of DVB, MPEG encoder, and VBI child interfaces.

Important APIs, types, and functions: `saa7164_initdev()` allocates `struct saa7164_dev`, registers the V4L2 device, enables PCI, maps BAR0/BAR2, requests IRQs, boots firmware, registers I2C buses, enumerates firmware subdevices, and calls per-port register functions. `saa7164_finidev()` performs the reverse. `saa7164_irq()` dispatches command, TS, encoder, and VBI interrupts by firmware interrupt id. `saa7164_port_init()` seeds each `struct saa7164_port` with type, work item, lists, locks, wait queues, and histogram state.

Control flow: probe starts with PCI/V4L2 setup, then firmware download, descriptor extraction, command bus setup, I2C registration, card setup, dynamic endpoint enumeration, and conditional child registration based on board port roles. TS IRQs feed DVB demux directly; encoder/VBI IRQs schedule deferred work that copies completed DMA buffers to read buffers and wakes readers. Remove stops debug firmware logging, unregisters children, removes I2C buses, frees IRQ/MSI, unmaps MMIO, and unregisters V4L2.

State and persistence: state is in `saa7164_dev`, six `saa7164_port` objects, global `saa7164_devlist`, module parameters, firmware status registers, and runtime histograms. No filesystem persistence is used; debugfs exposes live command ring state.

Dependencies and integration points: depends on PCI, V4L2, DVB, I2C, debugfs, workqueues, kthreads, firmware-command helpers, buffer helpers, card tables, and API/bus/cmd layers.

Risks: firmware/descriptor failure can leave only a partially registered device; several paths log and continue after bus/API failures. Deferred work assumes stable port and buffer lists. `BUG_ON` in IRQ paths can panic on unexpected hardware counters. Resource unwind is complex and should be checked on probe failures.

Test signals: probe/remove with known Hauppauge boards, firmware load messages, `/dev/dvb` and `/dev/video` creation, TS playback, MPEG/VBI reads, shared IRQ/MSI fallback, debugfs ring dumps, CRC/guard-buffer diagnostics, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-core.c -->
