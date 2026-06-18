# sources/distributed-fs/ceph-client/drivers/uio/uio.c

## Purpose
`uio.c` is the Userspace I/O core. It creates the `uio` character-device major and class, registers `/dev/uioN` devices for provider drivers, exposes maps and port regions in sysfs, delivers interrupt events through blocking reads/poll/fasync, supports userspace IRQ masking through writes, and maps provider-declared memory regions into userspace.

## Important APIs, Types, And Functions
Exported APIs are `uio_event_notify()`, `__uio_register_device()`, `__devm_uio_register_device()`, and `uio_unregister_device()`. Important internal types are `struct uio_map`, `struct uio_portio`, and `struct uio_listener`. The file operations are `uio_open()`, `uio_release()`, `uio_read()`, `uio_write()`, `uio_poll()`, `uio_mmap()`, and `uio_fasync()`.

Sysfs support includes device attributes `name`, `version`, and `event`, per-map attributes `name`, `addr`, `size`, `offset`, and per-port attributes `name`, `start`, `size`, `porttype`. Memory mapping supports `UIO_MEM_PHYS`, `UIO_MEM_IOVA`, `UIO_MEM_LOGICAL`, `UIO_MEM_VIRTUAL`, `UIO_MEM_DMA_COHERENT`, and provider-specific `mmap_prepare`.

## Control Flow And State
Module init allocates a character-device region for `UIO_MAX_DEVICES`, creates a `cdev`, and registers the `uio` class. Provider registration allocates a `struct uio_device`, assigns a minor through `idr`, creates the device, adds map/port sysfs objects, and requests a threaded IRQ unless the provider uses custom/no IRQ. The hard IRQ handler calls the provider handler and wakes the threaded handler on `IRQ_HANDLED`; the thread increments `idev->event`, wakes waiters, and sends SIGIO.

Open pins the device and owner module, allocates a listener with the current event count, and calls provider `open`. Read requires a 32-bit count, blocks until `idev->event` changes, then copies the new event count. Write requires a 32-bit value and calls provider `irqcontrol`. Mmap validates the map index encoded in `vm_pgoff`, requested size, and memory type before remapping physical, logical/vmalloc, DMA coherent, or provider-custom memory.

State is protected by `minor_lock` for the IDR and `idev->info_lock` for provider data lifetime. Unregister removes sysfs, frees IRQ, nulls `idev->info`, wakes readers with hangup, frees the minor, and unregisters the device while open file references can drain later.

## Dependencies And Integration Points
The core depends on Linux device class/cdev/idr/kobject/sysfs infrastructure, wait queues, fasync, IRQ threading, DMA mapping, VM fault/remap helpers, and `linux/uio_driver.h`. All UIO leaf drivers depend on these exported APIs and `struct uio_info`.

## Risks And Edge Cases
UIO intentionally exposes hardware to userspace, so provider correctness and permissions are critical. `uio_dev_del_attributes()` assumes map/port kobjects were created for every nonzero region. DMA coherent mapping is explicitly warned as discouraged. Providers must not free IRQ resources before unregister unless following the documented ordering. Event counters are 32-bit and can wrap; userspace should compare for inequality rather than monotonic distance.

## Test Signals
Test registration/unregistration with open FDs, blocking and nonblocking reads, poll/fasync, irqcontrol writes, custom IRQ/no IRQ devices, every memory type mmap path, sysfs map/port attributes, minor exhaustion, provider `open`/`release` errors, unregister wakeups returning errors, and module init/exit cleanup.
