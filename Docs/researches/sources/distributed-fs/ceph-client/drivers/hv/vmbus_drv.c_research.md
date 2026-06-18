# sources/distributed-fs/ceph-client/drivers/hv/vmbus_drv.c

## Purpose
`vmbus_drv.c` is the core Linux bus driver for Microsoft Hyper-V VMBus. It registers the `vmbus` bus, binds Hyper-V child devices to `hv_driver` implementations, dispatches channel messages and events from SynIC pages, exposes VMBus/device/channel sysfs attributes, manages dynamic driver IDs, handles MMIO window allocation, and coordinates suspend, resume, panic, kexec, and crash paths.

## Important APIs, types, and functions
Important state includes `vmbus_root_device`, `hyperv_cpuhp_online`, `vmbus_irq`, `vmbus_interrupt`, `is_confidential`, `hyperv_mmio`, `fb_mmio`, per-CPU `vmbus_evt`, per-CPU RT IRQ-thread state, and the global `hv_bus`.

Important exported functions include `vmbus_is_confidential()`, `hv_get_vmbus_root_device()`, `hv_vmbus_exists()`, `vmbus_isr()`, `__vmbus_driver_register()`, `vmbus_driver_unregister()`, `vmbus_channel_set_cpu()`, `hv_create_ring_sysfs()`, `hv_remove_ring_sysfs()`, `vmbus_device_register()`, `vmbus_device_unregister()`, `vmbus_allocate_mmio()`, and `vmbus_free_mmio()`.

## Control flow
`hv_acpi_init()` runs as a subsystem initcall. It validates Hyper-V availability, registers the platform driver, discovers ACPI or device-tree root resources, sets the VMBus interrupt model, initializes debug infrastructure, calls `vmbus_bus_init()`, and installs kexec/crash/syscore handlers. `vmbus_bus_init()` calls `hv_init()`, registers `hv_bus`, installs the IRQ or architecture callback vector, chooses confidential VMBus behavior, allocates SynIC state, initializes per-CPU SynIC contexts, connects to the host, registers the panic notifier, and requests channel offers.

Message handling starts in `vmbus_isr()`. Non-RT kernels call `__vmbus_isr()` directly; RT kernels wake a per-CPU FIFO `vmbus_irq/%u` thread. `__vmbus_on_msg_dpc()` copies the host message into private memory, validates message type and payload size, and either invokes a nonblocking handler directly or queues blocking work. Offer and rescind ordering is explicitly handled with `offer_in_progress`, workqueue selection, and `ignore_any_offer_msg` during suspend.

Driver binding uses `vmbus_match()` to handle hv_sock specially, then dynamic IDs, static ID tables, or `driver_override`. Child device registration creates the device first and then creates the `channels` kset and channel kobject/sysfs group, with comments documenting races visible to probe functions and user space.

## State and persistence behavior
The bus persists as a global kernel bus until module exit. Channel/device sysfs state persists per offered child device; dynamic IDs persist in each registered driver until removal or driver unregister. MMIO resources are parsed from ACPI/OF into a linked resource list and protected by `hyperv_mmio_lock`. Suspend tears down or invalidates transient channel state, while resume renegotiates the prior VMBus protocol version and requests fresh offers.

## Dependencies and integration points
The file depends on Hyper-V core initialization, SynIC and stimer helpers, VMBus channel protocol handlers from other hv files, Linux driver core/bus/sysfs/kobject APIs, ACPI and OF resource discovery, per-CPU IRQs, CPU hotplug, PREEMPT_RT smpboot threads, panic/kexec/crash notifiers, DMA configuration, PCI/sysfb/EFI framebuffer reservation, and optional hibernation support.

## Risks
High-risk areas include host-controlled message parsing, message ordering across workqueues, channel lifetime under RCU, sysfs races during device/channel creation, CPU target changes racing with channel closure, and MMIO range accounting. Panic/kexec/crash paths run under constrained conditions and must avoid operations that can sleep. Suspend/resume correctness depends on draining workqueues, ignoring new offers, rescinding hv_sock channels, invalidating relids, and receiving replacement offers.

## Test signals
Useful signals include bus registration and offer enumeration on Hyper-V, child driver autoload via `MODALIAS`, dynamic `new_id`/`remove_id`, `driver_override` behavior, sysfs visibility for monitor and ring attributes, channel CPU reassignment success/failure paths, event and message dispatch under normal and PREEMPT_RT kernels, confidential VMBus mode setup, MMIO allocation/free including framebuffer overlap, hibernation freeze/restore with subchannels and hv_sock, panic/kexec unload behavior, and module exit cleanup with no remaining channel references.
