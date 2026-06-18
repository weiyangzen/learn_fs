# sources/distributed-fs/ceph-client/drivers/pci/switch/switchtec.c

## Purpose
`switchtec.c` is the Microsemi/Microchip Switchtec PCIe switch management driver. It binds supported management or bridge-class PCI functions, maps switch MMIO regions, exposes `/dev/switchtecN`, forwards MRPC commands between userspace and firmware, reports flash and event state through ioctls, and handles switch events and link notifications.

## Important APIs, types, and functions
Module parameters are `max_devices`, `use_dma_mrpc`, and `nirqs`. The file exports `switchtec_class`. Important runtime types are `struct switchtec_dev` from shared headers and local `struct switchtec_user`, which tracks one open-file MRPC command, completion waitqueue, data buffer, and event counter. File operations include `switchtec_dev_open()`, `switchtec_dev_release()`, `switchtec_dev_write()`, `switchtec_dev_read()`, `switchtec_dev_poll()`, and `switchtec_dev_ioctl()`. Core helpers include MRPC queue/completion functions, flash/event/PFF ioctl helpers, `switchtec_init_pci()`, `switchtec_init_isr()`, `switchtec_pci_probe()`, and `switchtec_pci_remove()`.

## Control flow and behavior
Probe creates a character device object, enables the PCI device, sets a 64-bit DMA mask, maps BAR0 in write-combining mode for MRPC and normal mode for GAS registers, discovers partition and PFF topology, optionally allocates coherent DMA MRPC memory, registers interrupts, enables event headers, enables DMA MRPC, and adds the cdev/device.

Userspace writes a buffer containing an MRPC command plus payload. The driver validates size, restricts GAS read/write MRPC commands to `CAP_SYS_ADMIN`, copies the command into the per-open `switchtec_user`, queues it, and starts execution if no other command is running. Completion arrives from the MRPC event work item, DMA MRPC IRQ, or timeout polling. The completion path reads status, return code, and output data from either coherent DMA memory or MMIO registers, wakes the waiting file, removes it from the queue, and submits the next command. Reads wait unless nonblocking, copy the return code and response payload to userspace, translate hardware status to errno, and return the user state to idle.

Ioctls expose flash layout for gen3/gen4+, per-partition active/running state, event summaries, event control flags, and PFF-to-port mappings. The event ISR handles MRPC completions, link-state events, masks occurred events, increments `event_cnt`, and wakes poll waiters. Removal deletes the cdev, marks the device dead, wakes queued users, disables DMA MRPC, frees coherent memory, drops the PCI reference, and releases the device object.

## State and persistence
Persistent runtime state includes device minors from an IDA, `alive`, `mrpc_queue`, `mrpc_busy`, work items, waitqueues, coherent DMA MRPC buffer and DMA address, MMIO base pointers, partition/PFF topology, event counters, and per-open `switchtec_user` state. Hardware state includes MRPC registers, event-header masks, DMA MRPC enable/address registers, and PCI bus mastering.

## Dependencies and integration points
It depends on `linux/switchtec.h`, `linux/switchtec_ioctl.h`, PCI core probe/remove, cdev and class infrastructure, DMA APIs, IRQ vector allocation, workqueues, waitqueues, poll, user copy helpers, and NTB/autoload integration via `request_module_nowait("ntb_hw_switchtec")` for bridge-class functions.

## Risks
The user ABI is hardware-management sensitive. MRPC command ordering depends on `mrpc_mutex` and the single active queue head. Firmware reset can make BARs inaccessible; `is_firmware_running()` and `alive` protect many paths but MMIO access remains hardware-sensitive. Event index handling must avoid out-of-range MMIO; the port-to-PFF path uses `array_index_nospec()` for bounds hardening. DMA MRPC setup must be disabled and freed on every failure/removal path.

## Test signals
Test probe/remove, module unload with open files and queued commands, blocking and nonblocking MRPC reads, DMA and non-DMA MRPC modes, firmware-not-running timeout behavior, event poll notifications, all ioctl bounds checks, gen3 versus gen4 flash partition reporting, MSI/MSI-X vector allocation, and hot reset or surprise removal.
