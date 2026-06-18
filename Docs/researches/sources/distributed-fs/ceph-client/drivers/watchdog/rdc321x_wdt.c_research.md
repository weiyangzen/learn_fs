<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rdc321x_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rdc321x_wdt.c

Purpose: legacy RDC321x watchdog miscdevice backed by southbridge PCI configuration registers, with a kernel timer that keeps the short hardware watchdog enabled while userspace supplies a longer emulated heartbeat.

Important APIs, types, and functions: `rdc321x_wdt_device` stores completion, timer, queue/running flags, default ticks, lock, southbridge `pci_dev`, and base config register. Important functions are `rdc321x_wdt_trigger()`, `rdc321x_wdt_start()`, `rdc321x_wdt_stop()`, `rdc321x_wdt_reset()`, file operations, ioctl handling, probe, and remove.

Control flow: probe requires platform data containing the southbridge PCI device and a `wdt-reg` I/O resource, resets the watchdog register, initializes completion and timer, and registers `/dev/watchdog`. Enable starts the periodic timer and writes config bits that clear and enable the hardware watchdog. The timer decrements emulated `ticks`, rewrites the enable bit to feed hardware, and completes removal once queueing stops or ticks expire.

State and persistence behavior: runtime state is process-open bit, timer queue flag, `running` counter, `ticks`, and PCI register values. `rdc321x_wdt_stop()` deliberately returns `-EIO` after clearing running state, indicating hardware cannot really be disabled through the normal API.

Dependencies and integration points: uses platform data from `linux/mfd/rdc321x.h`, PCI config space read/write, Linux timers, completion, miscdevice watchdog ABI, and spinlock serialization.

Risks and edge cases: no nowayout/magic-close support is implemented despite being a watchdog miscdevice. `running` is incremented on each start and not a boolean under all paths. Remove waits for timer completion, so stale queue state can delay unload. PCI config register semantics are hardware-specific.

Test signals: platform-data absence, PCI register read/write tracing, enable/disable ioctl behavior, timer expiry path, remove while queued, and userspace keepalive extending `ticks`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rdc321x_wdt.c -->
