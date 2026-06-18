# sources/distributed-fs/ceph-client/samples/vfio-mdev/mtty.c

## Purpose
`mtty.c` is a sample mediated VFIO PCI serial device driver. It emulates one- or two-port 16550-compatible UART devices over mdev, including guest-visible PCI config/BAR access, INTx/MSI eventfd signaling, and VFIO migration state transfer.

## APIs, Types, And Functions
Key types are `struct serial_port`, `struct rxtx`, `struct mtty_data`, `struct mtty_migration_file`, and `struct mdev_state`. The driver exposes two mdev types via `mtty_types`. Major functions include PCI setup (`mtty_create_config_space()`), config/BAR emulation (`handle_pci_cfg_write()`, `handle_bar_write()`, `handle_bar_read()`, `mdev_access()`), migration (`mtty_set_state()`, `mtty_step_state()`, `mtty_save_device_data()`, `mtty_resume_device_data()`), IRQ wiring (`mtty_set_irqs()`), and VFIO callbacks in `mtty_dev_ops`.

## Control Flow
Module init registers a char device, mdev driver, class, parent device, and mdev parent. Probe allocates a VFIO emulated device. Init reserves available UART ports atomically, initializes locks and config space, and advertises VFIO migration/logging callbacks. Guest reads/writes enter VFIO read/write methods, are split into aligned chunks, and then decode region index from the high VFIO offset bits. UART register writes update FIFO, divisor, line control, modem control, and interrupt conditions; reads synthesize RX/IIR/LSR/MSR values.

## State And Persistence
Runtime state is in memory: virtual PCI config, per-port UART registers, FIFO contents, eventfd contexts, migration state, and migration anon-inode files. Migration serializes `mtty_data` with magic/version/port count and per-port `serial_port` snapshots; resume validates the header before loading port state. There is no storage persistence.

## Dependencies And Integration Points
The file depends on VFIO/mdev, eventfd, anon inodes, Linux serial register definitions, PCI config constants, iommufd emulation helpers, and kernel synchronization primitives. It integrates with VFIO userspace through PCI regions, `VFIO_DEVICE_SET_IRQS`, and VFIO migration state-machine callbacks.

## Risks And Test Signals
Risk is concentrated in emulated device semantics, lock ordering between `state_mutex` and `reset_mutex`, eventfd lifetime, and migration file disabling. The sample intentionally has simplified dirty logging. Test signals include mdev creation capacity accounting, one- and two-port BAR behavior, interrupt trigger/mask/unmask paths, VFIO reset during migration, save/resume validation, and module unload after active work.
