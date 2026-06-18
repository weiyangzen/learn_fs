# sources/distributed-fs/ceph-client/drivers/uio/uio_netx.c

## Purpose
`uio_netx.c` exposes Hilscher netX, netPLC, and PLX-bridged fieldbus PCI cards as UIO devices. It maps the card dual-port memory into a UIO memory region and provides a small interrupt handler that validates and disables device interrupts so userspace can acknowledge device-specific causes and re-enable them as needed.

## Important APIs, Types, And Functions
- `netx_pci_ids` matches Hilscher native PCI IDs and PLX 9030 subdevice IDs for NXSB-PCA/NXPCA variants.
- `netx_handler()` reads `DPM_HOST_INT_EN0` and `DPM_HOST_INT_STAT0`, checks `DPM_HOST_INT_MASK`, and clears `DPM_HOST_INT_GLOBAL_EN`.
- `netx_pci_probe()` allocates `struct uio_info`, enables the PCI function, requests regions, chooses BAR 0 or BAR 2, maps dual-port memory, initializes UIO metadata, disables interrupts, and registers the UIO device.
- `netx_pci_remove()` disables interrupts, unregisters UIO, releases PCI regions, disables the device, and unmaps memory.
- `module_pci_driver(netx_pci_driver)` supplies module load/unload registration.

## Control Flow
Probe starts by enabling PCI and reserving all BAR regions. Device identity selects the UIO name and BAR containing dual-port memory. The BAR is mapped with `ioremap`, then `uio_info.mem[0]` is filled as `UIO_MEM_PHYS`, IRQ sharing is enabled, and the device interrupt enable register is cleared before `uio_register_device()`. Interrupt delivery enters `netx_handler()`, which returns `IRQ_NONE` unless an enabled masked status bit belongs to this device, then disables the global interrupt enable bit and returns `IRQ_HANDLED`.

## State And Persistence Behavior
State is limited to `struct uio_info`, PCI driver data, the mapped BAR pointer, and hardware interrupt-enable bits. No persistent storage is written. The interrupt-disabled state persists in hardware until userspace or removal changes it.

## Dependencies And Integration Points
The file integrates Linux PCI, MMIO, IRQ, and UIO subsystems. Userspace receives `/dev/uioX`, maps dual-port memory, observes UIO interrupt notifications, performs card-specific acknowledgement, and re-enables interrupts through the mapped registers.

## Risks And Edge Cases
Most probe failures collapse to `-ENODEV`, losing detailed causes. BAR selection depends on the device ID and may expose no memory if firmware or board routing differs. Interrupt handling assumes BAR memory remains mapped and that the enable/status register offsets are valid for all matched boards. Because userspace owns detailed interrupt acknowledgement, a faulty userspace driver can leave interrupts disabled or unacknowledged.

## Test Signals
Build with `CONFIG_UIO` and target PCI IDs. Bind a supported or emulated PCI ID and check that `/sys/class/uio/uio*/maps/map0` matches the selected BAR. Trigger a device interrupt and confirm the UIO event count increments once and the card interrupt enable register is cleared. Validate remove/unbind leaves PCI regions released and no stale mapping is used.
