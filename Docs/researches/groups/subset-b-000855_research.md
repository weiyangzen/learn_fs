# subset-b-000855 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.c

### Purpose
This file is the userspace side of UML vector networking. It parses interface specifications and opens host TAP, raw packet, GRE, L2TPv3, BESS Unix socket, inherited-fd, and VDE transports for vector net devices.

### Important APIs, Types, And Functions
Key APIs include `uml_parse_vector_ifspec()`, `uml_vector_fetch_arg()`, `uml_vector_user_open()`, transport-specific `user_init_*_fds()` helpers, vnet-header helpers, batched I/O wrappers, and BPF creation/attach/detach helpers. `struct arglist` and `struct vector_fds` are the main data carriers.

### Control Flow
The config string is split in place into token/value pairs. `uml_vector_user_open()` dispatches on `transport=` and each initializer allocates fd state, opens/binds/connects host resources, optionally runs an ifup helper, and returns RX/TX descriptors. I/O wrappers retry `EINTR` and normalize nonblocking no-progress cases to zero.

### State, Persistence, And Dependencies
State persists as host fds, socket addresses, attached filters, TAP devices, and helper processes. Dependencies include host networking syscalls, Linux tun/packet/socket UAPI, UML `os_*` wrappers, `run_helper()`, and `um_malloc`.

### Integration Points And Risks
Risks include unchecked `MAXVARGS` parser capacity, in-place config mutation, prefix transport matching, partial cleanup paths, inherited fd ownership surprises, and unvalidated BPF file sizing. Integration is with the kernel vector network driver and host-side packet batching.

### Test Signals
Exercise malformed specs, every transport, dynamic TAP naming, helper failure, vnet-header setup, nonblocking EAGAIN/ENOBUFS paths, BPF load/attach/detach, and partial initialization cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.h -->
## sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.h

### Purpose
`vector_user.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/drivers`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct arglist`; `struct vector_fds`; `struct arglist *parsed`; `struct arglist *ifspec,`; `extern struct arglist *uml_parse_vector_ifspec(char *arg);`; `extern int uml_vector_recvmsg(int fd, void *hdr, int flags);`; `extern int uml_vector_sendmsg(int fd, void *hdr, int flags);`; `extern int uml_vector_writev(int fd, void *hdr, int iovcount);`; `extern void *uml_vector_default_bpf(const void *mac);`; `extern void *uml_vector_user_bpf(char *filename);`; `extern int uml_vector_attach_bpf(int fd, void *bpf);`; `extern int uml_vector_detach_bpf(int fd, void *bpf);`; `extern bool uml_raw_enable_qdisc_bypass(int fd);`; `extern bool uml_raw_enable_vnet_headers(int fd);`; `extern bool uml_tap_enable_vnet_headers(int fd);`; `#define __UM_VECTOR_USER_H`. The file has 107 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vfio_kern.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/vfio_kern.c

### Purpose
This file is the kernel-facing UML VFIO passthrough driver. It turns host VFIO PCI devices into virtual UM PCI devices and routes MSI-X eventfds into UML IRQs.

### Important APIs, Types, And Functions
Important types are `uml_vfio_device`, `uml_vfio_group`, and `uml_vfio_intr_ctx`. Key functions manage the shared VFIO container, group refcounts, config/BAR `um_pci_ops`, MSI-X capability/table tracking, IRQ activation, command-line parameters, mconsole config, init, and exit.

### Control Flow
Init collects requested devices, opens the VFIO container/group/device through `vfio_user.c`, reads MSI-X metadata, allocates interrupt contexts, then registers an embedded `um_pci_device`. Config and BAR accesses forward to VFIO. Guest MSI-X table writes create or close eventfds, register fd-backed UML IRQs, and deliver `generic_handle_irq()`.

### State, Persistence, And Dependencies
Persistent state is held in global mutex-protected device/group lists, shared container fd/user count, per-device VFIO metadata, MSI-X table information, and interrupt contexts. Dependencies include `virt-pci`, `vfio_user`, mconsole, SIGIO IRQ helpers, and Linux PCI register definitions.

### Integration Points And Risks
Risks include assuming MSI-X support and MSI-X guest drivers, subtle container/group refcounting, trusting guest-programmed MSI-X data, no mconsole remove support, and failure cleanup across several resource layers. Integration is with the UML virtual PCI host bridge.

### Test Signals
Test missing groups, duplicate devices, devices without MSI-X, VFIO ioctl errors, config/BAR widths, MSI-X enable/table writes, eventfd draining, and teardown after partial opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vfio_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vfio_user.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/vfio_user.c

### Purpose
This file wraps host VFIO syscalls for the UML VFIO driver. It is the raw `/dev/vfio` and sysfs access layer.

### Important APIs, Types, And Functions
It exposes container open/version checks, IOMMU setup, IOMMU-group discovery, group open/attach/detach, device setup/teardown, IRQ eventfd programming, and bounded config/BAR read/write helpers.

### Control Flow
The setup flow opens `/dev/vfio/vfio`, verifies API/IOMMU support, attaches a group to the container, maps UML shared physical memory into the type1 IOMMU, opens the device fd, discovers region offsets/sizes, reads MSI-X IRQ count, and initializes all IRQ slots as disabled until activated.

### State, Persistence, And Dependencies
Caller-owned `struct uml_vfio_user_device` persists the device fd, region table, IRQ fd array, and counts. Host persistent state includes VFIO container/group bindings, DMA mappings, eventfds, and device fds.

### Integration Points And Risks
Risks include short `pread`/`pwrite` not being retried, `sprintf()` into PATH_MAX buffers, only mapping memory visible through UML physmem backing, region-bound arithmetic, and requiring MSI-X. Integration is only through `vfio_user.h`/`vfio_kern.c`.

### Test Signals
Test API mismatch, unsupported IOMMU, malformed sysfs group links, group attach/detach failure, region bounds checks, IRQ count zero, eventfd lifecycle, and DMA-map rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vfio_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vfio_user.h -->
## sources/distributed-fs/ceph-client/arch/um/drivers/vfio_user.h

### Purpose
`vfio_user.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/drivers`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct uml_vfio_user_device`; `int uml_vfio_user_open_container(void);`; `int uml_vfio_user_setup_iommu(int container);`; `int uml_vfio_user_get_group_id(const char *device);`; `int uml_vfio_user_open_group(int group_id);`; `int uml_vfio_user_set_container(int container, int group);`; `int uml_vfio_user_unset_container(int container, int group);`; `void uml_vfio_user_teardown_device(struct uml_vfio_user_device *dev);`; `int uml_vfio_user_activate_irq(struct uml_vfio_user_device *dev, int index);`; `void uml_vfio_user_deactivate_irq(struct uml_vfio_user_device *dev, int index);`; `int uml_vfio_user_update_irqs(struct uml_vfio_user_device *dev);`; `#define __UM_VFIO_USER_H`. The file has 44 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vfio_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vhost_user.h -->
## sources/distributed-fs/ceph-client/arch/um/drivers/vhost_user.h

### Purpose
This header defines the vhost-user protocol ABI consumed by `virtio_uml.c`.

### Important APIs, Types, And Functions
It provides message flags, feature/protocol bits, supported masks, master/slave request enums, packed header/config/vring/memory structures, a payload union, and `struct vhost_user_msg`.

### Control Flow
There is no executable flow. The exact packed layouts control how requests, replies, fd-passing memory tables, vring state, and slave notifications are serialized.

### State, Persistence, And Dependencies
State is per-message and backend-owned protocol state. Dependencies are Linux integer and bit macros plus vhost-user peer ABI compatibility.

### Integration Points And Risks
Risks include protocol extension drift, strict size/layout assumptions, and the hard-coded two memory-region array. Integration is with Unix socket control channels in the virtio-UML transport.

### Test Signals
Validate layout sizes, feature masks, malformed message-size handling, fd-passing memory-table exchange, and interoperability with vhost-user backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vhost_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.c

### Purpose
This file implements the UML virtual PCI host bridge. It maps synthetic config/BAR spaces through `logic_iomem`, supports endpoint registration, and provides a small MSI domain.

### Important APIs, Types, And Functions
Key APIs are `um_pci_device_register()`, `um_pci_device_unregister()`, platform registration helpers, logic_iomem map callbacks, config/BAR operation dispatchers, MSI message composition, IRQ-domain allocation/free, and `pci_root_bus_fwnode()`.

### Control Flow
Device init registers config/iomem/platform windows, allocates a host bridge and MSI domain, maps per-slot config windows, and probes the PCI bus. Registered devices occupy one of eight slots and trigger rescans. Config/BAR accesses recover the endpoint and call its `um_pci_ops`.

### State, Persistence, And Dependencies
State is global: bridge, fwnode, IRQ domain, eight device slots, platform device pointer, mapped config windows, and MSI allocation bitmap. Dependencies include PCI core, MSI helpers, `logic_iomem`, UML IRQ allocation, and `virt-pci.h`.

### Integration Points And Risks
Risks include eight-device and no-multifunction limits, simplistic INTx mapping, init-failure cleanup gaps for ioremaps, MSI vector exhaustion, and trusting endpoint callbacks. Integration is used by VFIO and PCI-over-virtio.

### Test Signals
Test enumeration, slot exhaustion, register/unregister, config/BAR width validation, MSI allocation/free, platform window mapping, OF node lookup, and removal during rescan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.h -->
## sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.h

### Purpose
`virt-pci.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/drivers`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct um_pci_device`; `struct um_pci_ops`; `int um_pci_device_register(struct um_pci_device *dev);`; `void um_pci_device_unregister(struct um_pci_device *dev);`; `int um_pci_platform_device_register(struct um_pci_device *dev);`; `void um_pci_platform_device_unregister(struct um_pci_device *dev);`; `#define __UM_VIRT_PCI_H`. The file has 41 lines and includes or relies on `linux/pci.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/pci.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virt-pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virtio_pcidev.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/virtio_pcidev.c

### Purpose
This file exposes PCI devices to UML over a virtio transport. It translates PCI config/BAR operations into `virtio_pcidev_msg` commands and receives INTx/MSI/PME messages on an IRQ virtqueue.

### Important APIs, Types, And Functions
Important pieces are `virtio_pcidev_device`, the fixed command buffer pool, `virtio_pcidev_send_cmd()`, config/BAR `um_pci_ops`, command and IRQ virtqueue callbacks, vq setup, virtio probe/remove/shutdown, and platform simple-bus mode.

### Control Flow
Probe initializes virtqueues, primes IRQ receive buffers, registers a virtual PCI or platform endpoint, and marks wake/no-suspend behavior. Posted writes are queued without waiting; reads poll for their own completion with `max_delay_us`. IRQ messages call `generic_handle_irq()` for INTx or MSI payloads.

### State, Persistence, And Dependencies
State includes the virtio device, command/IRQ queues, buffer bitmap, extra allocations for posted payloads, wait status, and platform flag. Dependencies include virtio/vring core, `virt-pci`, `logic_iomem`, OF platform code, MSI, and `linux/virtio_pcidev.h`.

### Integration Points And Risks
Risks include busy-wait timeouts, fixed posted-write buffer capacity, payload lifetime for copied versus external buffers, limited IRQ chaining, and opcode correctness in bulk set paths. Integration is the host-backend bridge for UML PCI-over-virtio.

### Test Signals
Test config/BAR read/write round trips, posted write saturation, broken queue timeout, IRQ/MSI messages, platform population, suspend/resume, and remove while commands are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virtio_pcidev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virtio_uml.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/virtio_uml.c

### Purpose
This is the UML virtio transport for vhost-user sockets. It negotiates vhost-user features, passes memory-table fds, configures vrings, handles kicks/calls, supports config access and slave requests, and creates devices from devicetree, command line, or mconsole.

### Important APIs, Types, And Functions
Key types are `virtio_uml_device`, `virtio_uml_platform_data`, and `virtio_uml_vq_info`. Important APIs include vhost-user send/receive helpers, feature/protocol negotiation, slave-request IRQ setup, config get/set, memory/vring programming, `vu_notify()`, `vu_interrupt()`, virtio config ops, command-line parsing, and suspend/resume.

### Control Flow
Probe connects to the backend socket, negotiates owner/features/protocol features, optionally registers a slave-request pipe IRQ, registers a virtio device, and later `find_vqs()` sends the memory table, creates vrings, sets call/kick fds or in-band notifications, sends vring layout, and enables rings. Slave requests record config changes or queue-call bits and are dispatched through the UML IRQ handler.

### State, Persistence, And Dependencies
Persistent state includes socket/request fds, UML IRQ number, negotiated features, max queue count, status byte, suspend flags, vq IRQ bitmap, and platform-device ownership. Dependencies include vhost-user ABI, UML `os_*` fd/socket helpers, time-travel support, `phys_mapping()`, virtio/vring core, platform/OF, and mconsole.

### Integration Points And Risks
Risks include protocol drift, the 64-vq bitmap limit, shared-memory visibility excluding the UML image/reserved range, stack/global DMA hazards, blocking waits during socket failure, ACK ordering under `sock_lock`, and wake behavior in time-travel/suspend modes.

### Test Signals
Test feature negotiation, queue limits, memory-table fd passing, eventfd versus in-band notifications, config get/set, slave config-change and queue-call messages, connection reset, command-line/mconsole creation, and suspend/resume wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/virtio_uml.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/xterm.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/xterm.c

### Purpose
`xterm.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/drivers`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `struct xterm_chan`; `struct termios tt;`; `struct xterm_chan *data;`; `struct xterm_chan *data = d;`; `static void *xterm_init(char *str, int device, const struct chan_opts *opts)`; `if (data == NULL)`; `static int __init xterm_setup(char *line, int *add)`; `if (line == NULL)`; `if (*line)`; `if (access(argv[4], X_OK) < 0)`; `static void xterm_close(int fd, void *d)`; `if (data->pid != -1)`; `printk(UM_KERN_ERR "xterm_open : neither $DISPLAY nor $WAYLAND_DISPLAY is set.\n");`; `close(fd);`; `sprintf(title, data->title, data->device);`; `CATCH_EINTR(err = tcgetattr(new, &data->tt));`. The file has 226 lines and depends on `stddef.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `errno.h`, `string.h`, `termios.h`, `chan_user.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `stddef.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `errno.h`, `string.h`, `termios.h`, `chan_user.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/xterm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/xterm.h -->
## sources/distributed-fs/ceph-client/arch/um/drivers/xterm.h

### Purpose
`xterm.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/drivers`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern int xterm_fd(int socket, int *pid_out);`; `#define __XTERM_H__`. The file has 12 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/xterm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/xterm_kern.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/xterm_kern.c

### Purpose
`xterm_kern.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/drivers`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `struct xterm_wait`; `struct completion ready;`; `struct xterm_wait *xterm = data;`; `struct xterm_wait *data;`; `static irqreturn_t xterm_interrupt(int irq, void *data)`; `if (ret == -EAGAIN)`; `if (ret < 0)`; `else if (ret != sizeof(xterm->pid))`; `int xterm_fd(int socket, int *pid_out)`; `complete(&xterm->ready);`; `printk(KERN_ERR "xterm_fd : failed to allocate xterm_wait\n");`; `init_completion(&data->ready);`; `wait_for_completion(&data->ready);`; `um_free_irq(XTERM_IRQ, data);`; `kfree(data);`. The file has 83 lines and depends on `linux/slab.h`, `linux/completion.h`, `linux/irqreturn.h`, `asm/irq.h`, `irq_kern.h`, `os.h`, `xterm.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/slab.h`, `linux/completion.h`, `linux/irqreturn.h`, `asm/irq.h`, `irq_kern.h`, `os.h`, `xterm.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/xterm_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/Kbuild -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/Kbuild

### Purpose
`Kbuild` is a build-system file for `sources/distributed-fs/ceph-client/arch/um/include/asm`. It selects objects, generated headers, or generic wrappers used when building this part of UML.

### Important APIs, Types, And Functions
Important build entries include the file primarily supplies build or include glue with few named C symbols. The file has 28 lines and is consumed by Kbuild rather than by runtime code.

### Control Flow
Kbuild reads the assignments and rules during configuration/build, expands conditionals from Kconfig, and produces generated sources or include wrappers before compiling the UML objects.

### State, Persistence, And Dependencies
There is no runtime state. Persistent effects are build outputs such as generated source files, wrapper headers, object lists, or linker inputs. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks are stale object lists, missing generic wrappers, conditional object drift, or fragile shell/sed rules. Integration is with the Linux kernel build system and the surrounding UML directory.

### Test Signals
Run the relevant UML build configurations, clean rebuilds, and header export checks where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/archrandom.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/archrandom.h

### Purpose
`archrandom.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `static inline size_t __must_check arch_get_random_longs(unsigned long *v, size_t max_longs)`; `if (ret < 0)`; `static inline size_t __must_check arch_get_random_seed_longs(unsigned long *v, size_t max_longs)`; `ssize_t os_getrandom(void *buf, size_t len, unsigned int flags);`; `#define __ASM_UM_ARCHRANDOM_H__`. The file has 25 lines and includes or relies on `linux/types.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/types.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/archrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/asm-prototypes.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/asm-prototypes.h

### Purpose
`asm-prototypes.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern void cmpxchg8b_emu(void);`. The file has 6 lines and includes or relies on `asm-generic/asm-prototypes.h`, `asm/checksum.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/asm-prototypes.h`, `asm/checksum.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/bpf_perf_event.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/bpf_perf_event.h

### Purpose
`bpf_perf_event.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include the file primarily supplies build or include glue with few named C symbols. The file has 9 lines and includes or relies on `asm-generic/bpf_perf_event.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/bpf_perf_event.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/cache.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/cache.h

### Purpose
`cache.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define __UM_CACHE_H`; `#define L1_CACHE_BYTES		(1 << L1_CACHE_SHIFT)`. The file has 18 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/cacheflush.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/cacheflush.h

### Purpose
`cacheflush.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define __UM_ASM_CACHEFLUSH_H`; `#define flush_cache_vmap flush_tlb_kernel_range`; `#define flush_cache_vunmap flush_tlb_kernel_range`. The file has 9 lines and includes or relies on `asm/tlbflush.h`, `asm-generic/cacheflush.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm/tlbflush.h`, `asm-generic/cacheflush.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/common.lds.S -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/common.lds.S

### Purpose
`common.lds.S` contributes assembly/linker-script layout for UML. It controls section placement and linker-provided symbols for this source tree area.

### Important APIs, Types, And Functions
Important symbols/macros visible in the file include `RO_DATA(4096)`; `EXCEPTION_TABLE(0)`; `INIT_SETUP(0)`; `PERCPU_SECTION(32)`; `PROVIDE (etext = .);`; `PROVIDE (sdata = .);`; `PROVIDE (_unprotected_end = .);`. It depends on `asm-generic/vmlinux.lds.h`.

### Control Flow
The assembler or linker consumes the directives at build time; runtime code later relies on the emitted section ranges, alignment, and symbols.

### State, Persistence, And Dependencies
Runtime persistence is the final binary layout, not mutable C state. Build-time state is the generated object or linker script output. Dependencies include `asm-generic/vmlinux.lds.h`.

### Integration Points And Risks
Risks include alignment regressions, missing section ranges, symbol-name drift, or layout changes that break early boot, init/exit scanning, alternatives, or syscall stubs.

### Test Signals
Link UML, inspect generated symbols/sections, and boot configurations that use the affected init, exit, exception, or stub sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/common.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/cpufeature.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/cpufeature.h

### Purpose
`cpufeature.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `test_bit(bit, (unsigned long *)((c)->x86_capability))`; `test_cpu_cap(c, bit)`; `x86_this_cpu_test_bit(bit, cpu_info.x86_capability))`; `static __always_inline bool _static_cpu_has(u16 bit)`; `extern void setup_clear_cpu_cap(unsigned int bit);`; `#define _ASM_UM_CPUFEATURE_H`; `#define X86_CAP_FMT "%s"`; `#define x86_cap_flag(flag) x86_cap_flags[flag]`; `#define test_cpu_cap(c, bit)						\`; `#define CHECK_BIT_IN_MASK_WORD(maskname, word, bit)	\`; `#define cpu_has(c, bit)							\`. The file has 141 lines and includes or relies on `asm/processor.h`, `asm/asm.h`, `linux/bitops.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm/processor.h`, `asm/asm.h`, `linux/bitops.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/current.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/current.h

### Purpose
`current.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct task_struct;`; `static __always_inline struct task_struct *get_current(void)`; `#define __ASM_CURRENT_H`; `#define current get_current()`. The file has 24 lines and includes or relies on `linux/compiler.h`, `linux/threads.h`, `shared/smp.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/compiler.h`, `linux/threads.h`, `shared/smp.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/delay.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/delay.h

### Purpose
`delay.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `static inline void um_ndelay(unsigned long nsecs)`; `static inline void um_udelay(unsigned long usecs)`; `time_travel_ndelay(nsecs);`; `ndelay(nsecs);`; `time_travel_ndelay(1000 * usecs);`; `udelay(usecs);`; `#define __UM_DELAY_H`; `#define ndelay(n) um_ndelay(n)`; `#define udelay(n) um_udelay(n)`. The file has 30 lines and includes or relies on `asm-generic/delay.h`, `linux/time-internal.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/delay.h`, `linux/time-internal.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/dma.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/dma.h

### Purpose
`dma.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define __UM_DMA_H`; `#define MAX_DMA_ADDRESS (uml_physmem)`. The file has 11 lines and includes or relies on `asm/io.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm/io.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/fpu/api.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/fpu/api.h

### Purpose
`api.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm/fpu`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `static inline bool irq_fpu_usable(void)`; `#define _ASM_UM_FPU_API_H`; `#define kernel_fpu_begin() (void)0`; `#define kernel_fpu_end() (void)0`. The file has 22 lines and includes or relies on `linux/types.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/types.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/fpu/api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/futex.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/futex.h

### Purpose
`futex.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `int arch_futex_atomic_op_inuser(int op, u32 oparg, int *oval, u32 __user *uaddr);`; `#define _ASM_UM_FUTEX_H`. The file has 14 lines and includes or relies on `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/hardirq.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/hardirq.h

### Purpose
`hardirq.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `static inline void ack_bad_irq(unsigned int irq)`; `DECLARE_PER_CPU_SHARED_ALIGNED(irq_cpustat_t, irq_stat);`; `pr_crit("unexpected IRQ trap at vector %02x\n", irq);`; `#define __ASM_UM_HARDIRQ_H`; `#define __ARCH_IRQ_EXIT_IRQS_DISABLED 1`; `#define __ARCH_IRQ_STAT`; `#define inc_irq_stat(member)	this_cpu_inc(irq_stat.member)`. The file has 31 lines and includes or relies on `linux/cache.h`, `linux/threads.h`, `linux/irq.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/cache.h`, `linux/threads.h`, `linux/irq.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/io.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/io.h

### Purpose
`io.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `static inline void __iomem *ioremap(phys_addr_t offset, size_t size)`; `static inline void iounmap(void __iomem *addr)`; `#define _ASM_UM_IO_H`; `#define ioremap ioremap`; `#define iounmap iounmap`. The file has 26 lines and includes or relies on `linux/types.h`, `asm-generic/logic_io.h`, `asm-generic/io.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/types.h`, `asm-generic/logic_io.h`, `asm-generic/io.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/irq.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/irq.h

### Purpose
`irq.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define __UM_IRQ_H`; `#define TIMER_IRQ		0`; `#define UMN_IRQ			1`; `#define UBD_IRQ			2`; `#define UM_ETH_IRQ		3`; `#define ACCEPT_IRQ		4`. The file has 40 lines and includes or relies on `asm-generic/irq.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/irq.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/irqflags.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/irqflags.h

### Purpose
`irqflags.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `static inline unsigned long arch_local_save_flags(void)`; `static inline void arch_local_irq_restore(unsigned long flags)`; `static inline void arch_local_irq_enable(void)`; `static inline void arch_local_irq_disable(void)`; `int um_get_signals(void);`; `int um_set_signals(int enable);`; `void block_signals(void);`; `void unblock_signals(void);`; `return um_get_signals();`; `um_set_signals(flags);`; `unblock_signals();`; `block_signals();`; `#define __UM_IRQFLAGS_H`; `#define arch_local_save_flags arch_local_save_flags`; `#define arch_local_irq_restore arch_local_irq_restore`; `#define arch_local_irq_enable arch_local_irq_enable`. The file has 38 lines and includes or relies on `asm-generic/irqflags.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/irqflags.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/kasan.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/kasan.h

### Purpose
`kasan.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `void kasan_init(void);`; `#define __ASM_UM_KASAN_H`; `#define KASAN_SHADOW_OFFSET _AC(CONFIG_KASAN_SHADOW_OFFSET, UL)`; `#define KASAN_SHADOW_SCALE_SHIFT 3`; `#define KASAN_HOST_USER_SPACE_END_ADDR 0x00007fffffffffffUL`; `#define KASAN_SHADOW_SIZE ((KASAN_HOST_USER_SPACE_END_ADDR + 1) >> \`; `#define KASAN_SHADOW_START (KASAN_SHADOW_OFFSET)`. The file has 31 lines and includes or relies on `linux/init.h`, `linux/const.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/init.h`, `linux/const.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/kvm_para.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/kvm_para.h

### Purpose
`kvm_para.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include the file primarily supplies build or include glue with few named C symbols. The file has 1 lines and includes or relies on `asm-generic/kvm_para.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/kvm_para.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/mmu.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/mmu.h

### Purpose
`mmu.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct mm_id id;`; `struct mutex turnstile;`; `struct list_head list;`; `#define __ARCH_UM_MMU_H`; `#define INIT_MM_CONTEXT(mm)						\`. The file has 32 lines and includes or relies on `linux/types.h`, `linux/mutex.h`, `linux/spinlock.h`, `mm_id.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/types.h`, `linux/mutex.h`, `linux/spinlock.h`, `mm_id.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/mmu_context.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/mmu_context.h

### Purpose
`mmu_context.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct task_struct *tsk)`; `extern int init_new_context(struct task_struct *task, struct mm_struct *mm);`; `extern void destroy_context(struct mm_struct *mm);`; `#define __UM_MMU_CONTEXT_H`; `#define init_new_context init_new_context`; `#define destroy_context destroy_context`. The file has 29 lines and includes or relies on `linux/sched.h`, `linux/mm_types.h`, `linux/mmap_lock.h`, `asm/mm_hooks.h`, `asm/mmu.h`, `asm-generic/mmu_context.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/sched.h`, `linux/mm_types.h`, `linux/mmap_lock.h`, `asm/mm_hooks.h`, `asm/mmu.h`, `asm-generic/mmu_context.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/msi.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/msi.h

### Purpose
`msi.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include the file primarily supplies build or include glue with few named C symbols. The file has 1 lines and includes or relies on `asm-generic/msi.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/msi.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/msi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/page.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/page.h

### Purpose
`page.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct page;`; `#define __UM_PAGE_H`; `#define clear_page(page)	memset((void *)(page), 0, PAGE_SIZE)`; `#define copy_page(to,from)	memcpy((void *)(to), (void *)(from), PAGE_SIZE)`; `#define copy_user_page(to, from, vaddr, pg)	copy_page(to, from)`; `#define pmd_val(x)	((x).pmd)`; `#define __pmd(x) ((pmd_t) { (x) } )`. The file has 98 lines and includes or relies on `linux/const.h`, `vdso/page.h`, `linux/pfn.h`, `linux/types.h`, `asm/vm-flags.h`, `mem.h`, `asm-generic/memory_model.h`, `asm-generic/getorder.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/const.h`, `vdso/page.h`, `linux/pfn.h`, `linux/types.h`, `asm/vm-flags.h`, `mem.h`, `asm-generic/memory_model.h`, `asm-generic/getorder.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pci.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/pci.h

### Purpose
`pci.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `void *pci_root_bus_fwnode(struct pci_bus *bus);`; `#define __ASM_UM_PCI_H`; `#define pci_root_bus_fwnode	pci_root_bus_fwnode`. The file has 19 lines and includes or relies on `linux/types.h`, `asm/io.h`, `asm-generic/pci.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/types.h`, `asm/io.h`, `asm-generic/pci.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgalloc.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/pgalloc.h

### Purpose
`pgalloc.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `set_pmd(pmd, __pmd(_PAGE_TABLE + (unsigned long) __pa(pte)))`; `tlb_remove_ptdesc((tlb), page_ptdesc(pte))`; `tlb_remove_ptdesc((tlb), virt_to_ptdesc(pmd))`; `tlb_remove_ptdesc((tlb), virt_to_ptdesc(pud))`; `extern pgd_t *pgd_alloc(struct mm_struct *);`; `#define __UM_PGALLOC_H`; `#define pmd_populate_kernel(mm, pmd, pte) \`; `#define pmd_populate(mm, pmd, pte) 				\`; `#define __pte_free_tlb(tlb, pte, address)	\`; `#define __pmd_free_tlb(tlb, pmd, address)	\`; `#define __pud_free_tlb(tlb, pud, address)	\`. The file has 45 lines and includes or relies on `linux/mm.h`, `asm-generic/pgalloc.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/mm.h`, `asm-generic/pgalloc.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable-2level.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable-2level.h

### Purpose
`pgtable-2level.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `pte_val(e))`; `pgd_val(e))`; `#define __UM_PGTABLE_2LEVEL_H`; `#define PGDIR_SHIFT	22`; `#define PGDIR_SIZE	(1UL << PGDIR_SHIFT)`; `#define PGDIR_MASK	(~(PGDIR_SIZE-1))`; `#define PTRS_PER_PTE	1024`; `#define USER_PTRS_PER_PGD ((TASK_SIZE + (PGDIR_SIZE - 1)) / PGDIR_SIZE)`. The file has 42 lines and includes or relies on `asm-generic/pgtable-nopmd.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/pgtable-nopmd.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable-2level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable-4level.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable-4level.h

### Purpose
`pgtable-4level.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `pte_val(e))`; `pmd_val(e))`; `pud_val(e))`; `pgd_val(e))`; `set_pud(pud, __pud(_PAGE_TABLE + __pa(pmd)))`; `set_p4d(p4d, __p4d(_PAGE_TABLE + __pa(pud)))`; `static inline int pgd_needsync(pgd_t pgd)`; `static inline void pud_clear (pud_t *pud)`; `static inline void p4d_clear (p4d_t *p4d)`; `static inline unsigned long pte_pfn(pte_t pte)`; `set_pud(pud, __pud(_PAGE_NEEDSYNC));`; `set_p4d(p4d, __p4d(_PAGE_NEEDSYNC));`; `return phys_to_pfn(pte_val(pte));`; `return __pmd((page_nr << PAGE_SHIFT) | pgprot_val(pgprot));`; `#define __UM_PGTABLE_4LEVEL_H`; `#define PGDIR_SHIFT	39`. The file has 110 lines and includes or relies on `asm-generic/pgtable-nop4d.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/pgtable-nop4d.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable-4level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable.h

### Purpose
This is UMLs central page-table contract, defining PTE flags, protections, vmalloc layout, PTE manipulation, TLB sync marking, and swap PTE encoding.

### Important APIs, Types, And Functions
It defines `_PAGE_*` bits, selects 2- or 4-level geometry, declares `swapper_pg_dir`, defines `PAGE_*` protections, helpers such as `set_pte()`, `set_ptes()`, `um_tlb_mark_sync()`, `pte_same()`, `pfn_pte()`, `pte_modify()`, and swap-entry/exclusive helpers.

### Control Flow
PTE writes mark `_PAGE_NEEDSYNC`; batched `set_ptes()` marks the mm context range for later host mmap/munmap synchronization. Flush helpers also mark ranges, while kernel range flushes sync immediately through TLB code.

### State, Persistence, And Dependencies
State is page-table memory plus `mm->context.sync_tlb_range_from/to` protected by `sync_tlb_lock`. Dependencies include Linux mm types, selected page-table-level headers, UML address layout, and TLB sync implementation.

### Integration Points And Risks
Risks include execute-as-read semantics, `set_ptes()` PFN arithmetic, swap bit packing limits, `_PAGE_NEEDSYNC` comparisons, and lost sync range updates under concurrency. Integration is with generic mm, SKAS page faults, and host TLB synchronization.

### Test Signals
Run mmap/mprotect/munmap, prot-none, swap-entry, vmalloc, fork, and SKAS TLB synchronization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/processor-generic.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/processor-generic.h

### Purpose
`processor-generic.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct pt_regs;`; `struct task_struct;`; `struct mm_struct;`; `struct thread_struct`; `struct pt_regs *segv_regs;`; `struct task_struct *prev_sched;`; `struct arch_thread arch;`; `struct pt_regs regs;`; `int (*proc)(void *);`; `extern unsigned long __get_wchan(struct task_struct *p);`; `#define __UM_PROCESSOR_GENERIC_H`; `#define INIT_THREAD \`; `#define TASK_SIZE (task_size)`; `#define STACK_ROOM	(stacksizelim)`; `#define STACK_TOP	(TASK_SIZE - 2 * PAGE_SIZE)`; `#define STACK_TOP_MAX	STACK_TOP`. The file has 88 lines and includes or relies on `asm/ptrace.h`, `sysdep/archsetjmp.h`, `linux/prefetch.h`, `asm/cpufeatures.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm/ptrace.h`, `sysdep/archsetjmp.h`, `linux/prefetch.h`, `asm/cpufeatures.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/processor-generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/ptrace-generic.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/ptrace-generic.h

### Purpose
`ptrace-generic.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct pt_regs`; `struct uml_pt_regs regs;`; `struct task_struct;`; `extern unsigned long getreg(struct task_struct *child, int regno);`; `extern int putreg(struct task_struct *child, int regno, unsigned long value);`; `extern int poke_user(struct task_struct *child, long addr, long data);`; `extern int peek_user(struct task_struct *child, long addr, long data);`; `extern int arch_set_tls(struct task_struct *new, unsigned long tls);`; `extern void clear_flushed_tls(struct task_struct *task);`; `extern int syscall_trace_enter(struct pt_regs *regs);`; `extern void syscall_trace_leave(struct pt_regs *regs);`; `#define __UM_PTRACE_GENERIC_H`; `#define arch_has_single_step()	(1)`; `#define EMPTY_REGS { .regs = EMPTY_UML_PT_REGS }`; `#define PT_REGS_IP(r) UPT_IP(&(r)->regs)`; `#define PT_REGS_SP(r) UPT_SP(&(r)->regs)`. The file has 49 lines and includes or relies on `sysdep/ptrace.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `sysdep/ptrace.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/ptrace-generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/sections.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/sections.h

### Purpose
`sections.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define __UM_SECTIONS_H`. The file has 10 lines and includes or relies on `asm-generic/sections.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/sections.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/setup.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/setup.h

### Purpose
`setup.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define SETUP_H_INCLUDED`; `#define COMMAND_LINE_SIZE 4096`. The file has 11 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/smp.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/smp.h

### Purpose
`smp.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `void arch_smp_send_reschedule(int cpu);`; `void arch_send_call_function_single_ipi(int cpu);`; `void arch_send_call_function_ipi_mask(const struct cpumask *mask);`; `#define __UM_SMP_H`; `#define raw_smp_processor_id() uml_curr_cpu()`. The file has 20 lines and includes or relies on `linux/cpumask.h`, `shared/smp.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/cpumask.h`, `shared/smp.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/stacktrace.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/stacktrace.h

### Purpose
`stacktrace.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct stack_frame`; `struct stack_frame *next_frame;`; `struct stacktrace_ops`; `get_frame_pointer(struct task_struct *task, struct pt_regs *segv_regs)`; `if (!task || task == current)`; `void (*address)(void *data, unsigned long address, int reliable);`; `return KSTK_EBP(task);`; `return (unsigned long *)KSTK_ESP(task);`; `void dump_trace(struct task_struct *tsk, const struct stacktrace_ops *ops, void *data);`; `#define _ASM_UML_STACKTRACE_H`. The file has 43 lines and includes or relies on `linux/uaccess.h`, `linux/ptrace.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/uaccess.h`, `linux/ptrace.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/syscall-generic.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/syscall-generic.h

### Purpose
`syscall-generic.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct pt_regs *regs)`; `struct pt_regs *regs,`; `struct uml_pt_regs *r = &regs->regs;`; `static inline int syscall_get_nr(struct task_struct *task, struct pt_regs *regs)`; `static inline void syscall_set_nr(struct task_struct *task, struct pt_regs *regs, int nr)`; `return PT_REGS_SYSCALL_NR(regs);`; `return regs_return_value(regs);`; `PT_REGS_SET_SYSCALL_RETURN(regs, (long) error ?: val);`; `#define __UM_SYSCALL_GENERIC_H`. The file has 86 lines and includes or relies on `asm/ptrace.h`, `linux/err.h`, `linux/sched.h`, `sysdep/ptrace.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm/ptrace.h`, `linux/err.h`, `linux/sched.h`, `sysdep/ptrace.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/syscall-generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/thread_info.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/thread_info.h

### Purpose
`thread_info.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct thread_info`; `#define __UM_THREAD_INFO_H`; `#define THREAD_SIZE_ORDER CONFIG_KERNEL_STACK_ORDER`; `#define THREAD_SIZE ((1 << CONFIG_KERNEL_STACK_ORDER) * PAGE_SIZE)`; `#define INIT_THREAD_INFO(tsk)			\`; `#define TIF_SYSCALL_TRACE	0	/* syscall trace active */`; `#define TIF_SIGPENDING		1	/* signal pending */`. The file has 62 lines and includes or relies on `asm/types.h`, `asm/page.h`, `asm/segment.h`, `sysdep/ptrace_user.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm/types.h`, `asm/page.h`, `asm/segment.h`, `sysdep/ptrace_user.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/timex.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/timex.h

### Purpose
`timex.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define __UM_TIMEX_H`; `#define CLOCK_TICK_RATE (HZ)`. The file has 9 lines and includes or relies on `asm-generic/timex.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm-generic/timex.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/tlb.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/tlb.h

### Purpose
`tlb.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define __UM_TLB_H`. The file has 11 lines and includes or relies on `linux/mm.h`, `asm/tlbflush.h`, `asm/cacheflush.h`, `asm-generic/tlb.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/mm.h`, `asm/tlbflush.h`, `asm/cacheflush.h`, `asm-generic/tlb.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/tlbflush.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/tlbflush.h

### Purpose
`tlbflush.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern int um_tlb_sync(struct mm_struct *mm);`; `extern void flush_tlb_all(void);`; `extern void flush_tlb_mm(struct mm_struct *mm);`; `um_tlb_mark_sync(vma->vm_mm, address, address + PAGE_SIZE);`; `um_tlb_mark_sync(vma->vm_mm, start, end);`; `um_tlb_mark_sync(&init_mm, start, end);`; `um_tlb_sync(&init_mm);`; `#define __UM_TLBFLUSH_H`. The file has 59 lines and includes or relies on `linux/mm.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/mm.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/uaccess.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/uaccess.h

### Purpose
`uaccess.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `static inline int __access_ok(const void __user *ptr, unsigned long size)`; `extern unsigned long raw_copy_from_user(void *to, const void __user *from, unsigned long n);`; `extern unsigned long raw_copy_to_user(void __user *to, const void *from, unsigned long n);`; `extern unsigned long __clear_user(void __user *mem, unsigned long len);`; `static inline int __access_ok(const void __user *ptr, unsigned long size);`; `return __addr_range_nowrap(addr, size) && __under_task_size(addr, size);`; `#define __UM_UACCESS_H`; `#define __under_task_size(addr, size) \`; `#define __addr_range_nowrap(addr, size) \`; `#define __access_ok __access_ok`; `#define __clear_user __clear_user`; `#define INLINE_COPY_FROM_USER`. The file has 67 lines and includes or relies on `asm/elf.h`, `linux/unaligned.h`, `sysdep/faultinfo.h`, `asm-generic/uaccess.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm/elf.h`, `linux/unaligned.h`, `sysdep/faultinfo.h`, `asm-generic/uaccess.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/unwind.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/unwind.h

### Purpose
`unwind.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define _ASM_UML_UNWIND_H`. The file has 8 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/vmalloc.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/vmalloc.h

### Purpose
`vmalloc.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define _ASM_UM_VMALLOC_H`. The file has 4 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/vmlinux.lds.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/vmlinux.lds.h

### Purpose
`vmlinux.lds.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include the file primarily supplies build or include glue with few named C symbols. The file has 2 lines and includes or relies on `asm/thread_info.h`, `asm-generic/vmlinux.lds.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm/thread_info.h`, `asm-generic/vmlinux.lds.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/vmlinux.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/linux/smp-internal.h -->
## sources/distributed-fs/ceph-client/arch/um/include/linux/smp-internal.h

### Purpose
`smp-internal.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/linux`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `void prefill_possible_map(void);`; `#define __UM_SMP_INTERNAL_H`. The file has 17 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/linux/smp-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/linux/time-internal.h -->
## sources/distributed-fs/ceph-client/arch/um/include/linux/time-internal.h

### Purpose
`time-internal.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/linux`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct time_travel_event`; `struct list_head list;`; `void (*fn)(struct time_travel_event *d))`; `static inline void time_travel_propagate_time(void)`; `if (time_travel_mode == TT_MODE_EXTERNAL)`; `static inline void time_travel_wait_readable(int fd)`; `static inline void time_travel_sleep(void)`; `static inline void time_travel_add_irq_event(struct time_travel_event *e)`; `void (*fn)(struct time_travel_event *d);`; `void time_travel_sleep(void);`; `void __time_travel_propagate_time(void);`; `__time_travel_propagate_time();`; `void __time_travel_wait_readable(int fd);`; `__time_travel_wait_readable(fd);`; `void time_travel_add_irq_event(struct time_travel_event *e);`; `bool time_travel_del_event(struct time_travel_event *e);`. The file has 96 lines and includes or relies on `linux/list.h`, `asm/bug.h`, `shared/timetravel.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/list.h`, `asm/bug.h`, `shared/timetravel.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/linux/time-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/linux/virtio-uml.h -->
## sources/distributed-fs/ceph-client/arch/um/include/linux/virtio-uml.h

### Purpose
`virtio-uml.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/linux`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define __VIRTIO_UML_H__`. The file has 13 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/linux/virtio-uml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/arch.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/arch.h

### Purpose
`arch.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern void arch_check_bugs(void);`; `extern int arch_fixup(unsigned long address, struct uml_pt_regs *regs);`; `extern void arch_examine_signal(int sig, struct uml_pt_regs *regs);`; `void mc_set_rip(void *_mc, void *target);`; `#define __ARCH_H__`. The file has 17 lines and includes or relies on `sysdep/ptrace.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `sysdep/ptrace.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/as-layout.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/as-layout.h

### Purpose
`as-layout.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct task_struct;`; `struct siginfo;`; `extern int linux_main(int argc, char **argv, char **envp);`; `extern void uml_finishsetup(void);`; `extern void (*sig_info[])(int, struct siginfo *si, struct uml_pt_regs *, void *);`; `#define __START_H__`; `#define STUB_START stub_start`; `#define STUB_CODE STUB_START`; `#define STUB_DATA (STUB_CODE + UM_KERN_PAGE_SIZE)`; `#define STUB_DATA_PAGES 2`; `#define STUB_SIZE ((1 + STUB_DATA_PAGES) * UM_KERN_PAGE_SIZE)`. The file has 57 lines and includes or relies on `generated/asm-offsets.h`, `sysdep/ptrace.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `generated/asm-offsets.h`, `sysdep/ptrace.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/as-layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/elf_user.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/elf_user.h

### Purpose
`elf_user.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define __ELF_USER_H__`; `#define AT_SYSINFO 32`; `#define AT_SYSINFO_EHDR 33`. The file has 19 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/elf_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/frame_kern.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/frame_kern.h

### Purpose
`frame_kern.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct pt_regs *regs, sigset_t *mask);`; `#define __FRAME_KERN_H_`. The file has 15 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/frame_kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/init.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/init.h

### Purpose
`init.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct uml_param`; `struct __uml_non_empty_string_struct_##dummyname		\`; `typedef int (*initcall_t)(void);`; `typedef void (*exitcall_t)(void);`; `int (*setup_func)(char *, int *);`; `#define _LINUX_UML_INIT_H`; `#define __init		__section(".init.text")`; `#define __initdata	__section(".init.data")`; `#define __exitdata	__section(".exit.data")`; `#define __exit_call	__used __section(".exitcall.exit")`; `#define __exit		__section(".exit.text")`. The file has 127 lines and includes or relies on `linux/compiler_types.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/compiler_types.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/irq_kern.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/irq_kern.h

### Purpose
`irq_kern.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct time_travel_event *));`; `struct time_travel_event *))`; `static inline bool um_irq_timetravel_handler_used(void)`; `void um_free_irq(int irq, void *dev_id);`; `void free_irqs(void);`; `#define __IRQ_KERN_H__`; `#define UM_IRQ_ALLOC	-1`. The file has 80 lines and includes or relies on `linux/interrupt.h`, `linux/time-internal.h`, `asm/ptrace.h`, `irq_user.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/interrupt.h`, `linux/time-internal.h`, `asm/ptrace.h`, `irq_user.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/irq_kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/irq_user.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/irq_user.h

### Purpose
`irq_user.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `enum um_irq_type`; `struct siginfo;`; `struct uml_pt_regs *regs, void *mc);`; `void sigio_run_timetravel_handlers(void);`; `extern void free_irq_by_fd(int fd);`; `extern void deactivate_fd(int fd, int irqnum);`; `extern int deactivate_all_fds(void);`; `#define __IRQ_USER_H__`. The file has 27 lines and includes or relies on `sysdep/ptrace.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `sysdep/ptrace.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/irq_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/kern.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/kern.h

### Purpose
`kern.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern int printf(const char *fmt, ...);`; `extern void *sbrk(int increment);`; `extern int pause(void);`; `extern void exit(int);`; `#define __KERN_H__`. The file has 22 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/kern_util.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/kern_util.h

### Purpose
`kern_util.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct siginfo;`; `struct pt_regs;`; `extern unsigned long alloc_stack(int order, int atomic);`; `extern void free_stack(unsigned long stack, int order);`; `extern void do_signal(struct pt_regs *regs);`; `extern void interrupt_end(void);`; `extern unsigned int do_IRQ(int irq, struct uml_pt_regs *regs);`; `extern void initial_thread_cb(void (*proc)(void *), void *arg);`; `extern void timer_handler(int sig, struct siginfo *unused_si, struct uml_pt_regs *regs);`; `extern void uml_pm_wake(void);`; `extern int start_uml(void);`; `extern void uml_cleanup(void);`; `extern void do_uml_exitcalls(void);`; `extern int __uml_cant_sleep(void);`; `extern int get_current_pid(void);`; `extern int copy_from_user_proc(void *to, void *from, int size);`. The file has 70 lines and includes or relies on `sysdep/ptrace.h`, `sysdep/faultinfo.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `sysdep/ptrace.h`, `sysdep/faultinfo.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/kern_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/longjmp.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/longjmp.h

### Purpose
`longjmp.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern int setjmp(jmp_buf);`; `extern void longjmp(jmp_buf, int);`; `#define __UML_LONGJMP_H`; `#define UML_LONGJMP(buf, val) do { \`; `#define UML_SETJMP(buf) ({				\`. The file has 23 lines and includes or relies on `sysdep/archsetjmp.h`, `os.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `sysdep/archsetjmp.h`, `os.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/longjmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/mem.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/mem.h

### Purpose
`mem.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `static inline unsigned long uml_to_phys(void *virt)`; `static inline void *uml_to_virt(unsigned long phys)`; `extern int phys_mapping(unsigned long phys, unsigned long long *offset_out);`; `return(((unsigned long) virt) - uml_physmem);`; `return((void *) uml_physmem + phys);`; `#define __MEM_H__`. The file has 22 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/mem_user.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/mem_user.h

### Purpose
`mem_user.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `#define _MEM_USER_H`; `#define ROUND_4M(n) ((((unsigned long) (n)) + (1 << 22)) & ~((1 << 22) - 1))`. The file has 42 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/mem_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/os.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/os.h

### Purpose
This is the main declaration surface for UML host OS wrappers. It isolates kernel-like UML code from direct libc/syscall details.

### Important APIs, Types, And Functions
It defines `CATCH_EINTR`, file type/access constants, `OS_LIB_PATH`, `uml_stat`, fluent `openflags` helpers, and declarations for file, socket, fd passing, mmap, process, helper, signal, time, SKAS, IRQ, SIGIO, random, futex, SMP, and time-travel functions.

### Control Flow
Callers build `openflags`, invoke `os_*` wrappers, and receive Linux-style negative errno values. The implementations own blocking, EINTR, close-on-exec, fd-passing, epoll, and host process details.

### State, Persistence, And Dependencies
State is mostly host process state: fds, mappings, helper threads/processes, signals, timers, epoll registrations, backing files, and CPU host threads. Dependencies span arch/um/os-Linux and kernel implementation files.

### Integration Points And Risks
Risks include broad coupling, inconsistent errno conventions if wrappers drift, accidental blocking in atomic contexts, and include conflicts between host and kernel headers. Integration is nearly every UML subsystem.

### Test Signals
Cover file/socket/fd-passing, helper process, signal, timer, futex, mmap/remap, epoll IRQ, random, and SMP wrapper behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/ptrace_user.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/ptrace_user.h

### Purpose
`ptrace_user.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern int ptrace_getregs(long pid, unsigned long *regs_out);`; `extern int ptrace_setregs(long pid, unsigned long *regs_in);`; `#define __PTRACE_USER_H__`. The file has 15 lines and includes or relies on `sys/ptrace.h`, `sysdep/ptrace_user.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `sys/ptrace.h`, `sysdep/ptrace_user.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/ptrace_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/registers.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/registers.h

### Purpose
`registers.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern int init_pid_registers(int pid);`; `extern void get_safe_registers(unsigned long *regs, unsigned long *fp_regs);`; `extern int get_fp_registers(int pid, unsigned long *regs);`; `extern int put_fp_registers(int pid, unsigned long *regs);`; `#define __REGISTERS_H`. The file has 16 lines and includes or relies on `sysdep/ptrace.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `sysdep/ptrace.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/sigio.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/sigio.h

### Purpose
`sigio.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern void sigio_lock(void);`; `extern void sigio_unlock(void);`; `#define __SIGIO_H__`. The file has 12 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/sigio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/skas/mm_id.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/skas/mm_id.h

### Purpose
`mm_id.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared/skas`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct mm_id`; `struct mutex *__get_turnstile(struct mm_id *mm_id);`; `void enter_turnstile(struct mm_id *mm_id) __acquires(__get_turnstile(mm_id));`; `void exit_turnstile(struct mm_id *mm_id) __releases(__get_turnstile(mm_id));`; `void notify_mm_kill(int pid);`; `#define __MM_ID_H`; `#define STUB_MAX_FDS 4`. The file has 30 lines and includes or relies on `linux/compiler_types.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/compiler_types.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/skas/mm_id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/skas/skas.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/skas/skas.h

### Purpose
`skas.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared/skas`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern void new_thread_handler(void);`; `extern void handle_syscall(struct uml_pt_regs *regs);`; `extern unsigned long current_stub_stack(void);`; `extern struct mm_id *current_mm_id(void);`; `extern void current_mm_sync(void);`; `void initial_jmpbuf_lock(void);`; `void initial_jmpbuf_unlock(void);`; `#define __SKAS_H`. The file has 21 lines and includes or relies on `sysdep/ptrace.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `sysdep/ptrace.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/skas/skas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/skas/stub-data.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/skas/stub-data.h

### Purpose
`stub-data.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared/skas`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `struct stub_init_data`; `enum stub_syscall_type`; `struct stub_syscall`; `enum stub_syscall_type syscall;`; `struct stub_data`; `struct stub_syscall syscall_data[(UM_KERN_PAGE_SIZE - 128) / sizeof(struct stub_syscall)] __aligned(16);`; `struct stub_data_arch arch_data;`; `#define __STUB_DATA_H`; `#define FUTEX_IN_CHILD 0`; `#define FUTEX_IN_KERN 1`; `#define STUB_NEXT_SYSCALL(s) \`. The file has 76 lines and includes or relies on `linux/compiler_types.h`, `as-layout.h`, `sysdep/tls.h`, `sysdep/stub-data.h`, `mm_id.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `linux/compiler_types.h`, `as-layout.h`, `sysdep/tls.h`, `sysdep/stub-data.h`, `mm_id.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/skas/stub-data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/smp.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/smp.h

### Purpose
`smp.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `int uml_curr_cpu(void);`; `void uml_start_secondary(void *opaque);`; `void uml_ipi_handler(int vector);`; `#define __UM_SHARED_SMP_H`; `#define uml_ncpus 1`; `#define uml_curr_cpu() 0`. The file has 20 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/timetravel.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/timetravel.h

### Purpose
`timetravel.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `enum time_travel_mode`; `static inline void time_travel_print_bc_msg(void)`; `if (time_travel_should_print_bc_msg)`; `void _time_travel_print_bc_msg(void);`; `_time_travel_print_bc_msg();`; `#define _UM_TIME_TRAVEL_H_`; `#define time_travel_mode TT_MODE_OFF`; `#define time_travel_should_print_bc_msg 0`. The file has 30 lines and includes or relies on the surrounding UML/Linux build context.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/timetravel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/um_malloc.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/um_malloc.h

### Purpose
`um_malloc.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern void *uml_kmalloc(int size, int flags);`; `extern void kfree(const void *ptr);`; `extern void *vmalloc_noprof(unsigned long size);`; `extern void vfree(const void *ptr);`; `#define __UM_MALLOC_H__`; `#define vmalloc(...)		vmalloc_noprof(__VA_ARGS__)`. The file has 20 lines and includes or relies on `generated/asm-offsets.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `generated/asm-offsets.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/um_malloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/user.h -->
## sources/distributed-fs/ceph-client/arch/um/include/shared/user.h

### Purpose
`user.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/shared`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `extern void panic(const char *fmt, ...)`; `extern int _printk(const char *fmt, ...)`; `static inline int printk(const char *fmt, ...)`; `__attribute__ ((format (printf, 1, 2)));`; `extern int in_aton(char *str);`; `extern size_t strlcat(char *, const char *, size_t);`; `extern size_t sized_strscpy(char *, const char *, size_t);`; `#define __USER_H__`; `#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))`; `#define UM_KERN_EMERG	KERN_EMERG`; `#define UM_KERN_ALERT	KERN_ALERT`; `#define UM_KERN_CRIT	KERN_CRIT`; `#define UM_KERN_ERR	KERN_ERR`. The file has 68 lines and includes or relies on `generated/asm-offsets.h`, `linux/types.h`, `stddef.h`, `sys/types.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `generated/asm-offsets.h`, `linux/types.h`, `stddef.h`, `sys/types.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/shared/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/uapi/asm/Kbuild -->
## sources/distributed-fs/ceph-client/arch/um/include/uapi/asm/Kbuild

### Purpose
`Kbuild` is a build-system file for `sources/distributed-fs/ceph-client/arch/um/include/uapi/asm`. It selects objects, generated headers, or generic wrappers used when building this part of UML.

### Important APIs, Types, And Functions
Important build entries include the file primarily supplies build or include glue with few named C symbols. The file has 1 lines and is consumed by Kbuild rather than by runtime code.

### Control Flow
Kbuild reads the assignments and rules during configuration/build, expands conditionals from Kconfig, and produces generated sources or include wrappers before compiling the UML objects.

### State, Persistence, And Dependencies
There is no runtime state. Persistent effects are build outputs such as generated source files, wrapper headers, object lists, or linker inputs. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks are stale object lists, missing generic wrappers, conditional object drift, or fragile shell/sed rules. Integration is with the Linux kernel build system and the surrounding UML directory.

### Test Signals
Run the relevant UML build configurations, clean rebuilds, and header export checks where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/Makefile -->
## sources/distributed-fs/ceph-client/arch/um/kernel/Makefile

### Purpose
`Makefile` is a build-system file for `sources/distributed-fs/ceph-client/arch/um/kernel`. It selects objects, generated headers, or generic wrappers used when building this part of UML.

### Important APIs, Types, And Functions
Important build entries include the file primarily supplies build or include glue with few named C symbols. The file has 65 lines and is consumed by Kbuild rather than by runtime code.

### Control Flow
Kbuild reads the assignments and rules during configuration/build, expands conditionals from Kconfig, and produces generated sources or include wrappers before compiling the UML objects.

### State, Persistence, And Dependencies
There is no runtime state. Persistent effects are build outputs such as generated source files, wrapper headers, object lists, or linker inputs. Dependencies include the surrounding UML/Linux build context.

### Integration Points And Risks
Risks are stale object lists, missing generic wrappers, conditional object drift, or fragile shell/sed rules. Integration is with the Linux kernel build system and the surrounding UML directory.

### Test Signals
Run the relevant UML build configurations, clean rebuilds, and header export checks where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/asm-offsets.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/asm-offsets.c

### Purpose
`asm-offsets.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `void foo(void)`; `void foo(void);`; `DEFINE(KERNEL_MADV_REMOVE, MADV_REMOVE);`; `DEFINE(UM_KERN_PAGE_SIZE, PAGE_SIZE);`; `DEFINE(UM_KERN_PAGE_MASK, PAGE_MASK);`; `DEFINE(UM_KERN_PAGE_SHIFT, PAGE_SHIFT);`; `DEFINE(UM_GFP_KERNEL, GFP_KERNEL);`; `DEFINE(UM_GFP_ATOMIC, GFP_ATOMIC);`; `DEFINE(UM_THREAD_SIZE, THREAD_SIZE);`; `DEFINE(UM_NSEC_PER_SEC, NSEC_PER_SEC);`; `DEFINE(UM_NSEC_PER_USEC, NSEC_PER_USEC);`; `DEFINE(UM_KERN_GDT_ENTRY_TLS_ENTRIES, GDT_ENTRY_TLS_ENTRIES);`; `DEFINE(UM_SECCOMP_ARCH_NATIVE, SECCOMP_ARCH_NATIVE);`; `DEFINE(HOSTFS_ATTR_MODE, ATTR_MODE);`; `DEFINE(HOSTFS_ATTR_UID, ATTR_UID);`; `#define COMPILE_OFFSETS`. The file has 49 lines and depends on `linux/stddef.h`, `linux/sched.h`, `linux/elf.h`, `linux/crypto.h`, `linux/kbuild.h`, `linux/audit.h`, `linux/fs.h`, `asm/mman.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/stddef.h`, `linux/sched.h`, `linux/elf.h`, `linux/crypto.h`, `linux/kbuild.h`, `linux/audit.h`, `linux/fs.h`, `asm/mman.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/config.c.in -->
## sources/distributed-fs/ceph-client/arch/um/kernel/config.c.in

### Purpose
`config.c.in` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `static int __init print_config(char *line, int *add)`; `printf("%s", config[i]);`; `exit(0);`. The file has 26 lines and depends on `stdio.h`, `stdlib.h`, `init.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `stdio.h`, `stdlib.h`, `init.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/config.c.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/dtb.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/dtb.c

### Purpose
`dtb.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `void uml_dtb_init(void)`; `static int __init uml_dtb_setup(char *line, int *add)`; `pr_err("invalid DTB %s\n", dtb);`; `memblock_free(area, size);`; `early_init_fdt_scan_reserved_mem();`; `unflatten_device_tree();`. The file has 42 lines and depends on `linux/init.h`, `linux/of_fdt.h`, `linux/printk.h`, `linux/memblock.h`, `init.h`, `um_arch.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/init.h`, `linux/of_fdt.h`, `linux/printk.h`, `linux/memblock.h`, `init.h`, `um_arch.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/dtb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/dyn.lds.S -->
## sources/distributed-fs/ceph-client/arch/um/kernel/dyn.lds.S

### Purpose
`dyn.lds.S` contributes assembly/linker-script layout for UML. It controls section placement and linker-provided symbols for this source tree area.

### Important APIs, Types, And Functions
Important symbols/macros visible in the file include `OUTPUT_FORMAT(ELF_FORMAT)`; `OUTPUT_ARCH(ELF_ARCH)`; `ENTRY(_start)`; `INIT_TEXT_SECTION(PAGE_SIZE)`; `KEEP (*(.init))`; `KEEP (*(.fini))`; `INIT_TASK_DATA(KERNEL_STACK_SIZE)`; `SORT(CONSTRUCTORS)`; `KEEP (*crtbegin.o(.ctors))`; `KEEP (*(EXCLUDE_FILE (*crtend.o ) .ctors))`; `PROVIDE (__executable_start = START);`; `PROVIDE_HIDDEN(__rel_iplt_start = .);`; `PROVIDE_HIDDEN(__rel_iplt_end = .);`; `PROVIDE_HIDDEN(__rela_iplt_start = .);`; `PROVIDE_HIDDEN(__rela_iplt_end = .);`; `PROVIDE (edata = .);`. It depends on `asm/vmlinux.lds.h`, `asm/page.h`, `asm/common.lds.S`.

### Control Flow
The assembler or linker consumes the directives at build time; runtime code later relies on the emitted section ranges, alignment, and symbols.

### State, Persistence, And Dependencies
Runtime persistence is the final binary layout, not mutable C state. Build-time state is the generated object or linker script output. Dependencies include `asm/vmlinux.lds.h`, `asm/page.h`, `asm/common.lds.S`.

### Integration Points And Risks
Risks include alignment regressions, missing section ranges, symbol-name drift, or layout changes that break early boot, init/exit scanning, alternatives, or syscall stubs.

### Test Signals
Link UML, inspect generated symbols/sections, and boot configurations that use the affected init, exit, exception, or stub sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/dyn.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/early_printk.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/early_printk.c

### Purpose
`early_printk.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `static void early_console_write(struct console *con, const char *s, unsigned int n)`; `static int __init setup_early_printk(char *buf)`; `um_early_printk(s, n);`; `register_console(&early_console_dev);`; `early_param("earlyprintk", setup_early_printk);`. The file has 32 lines and depends on `linux/kernel.h`, `linux/console.h`, `linux/init.h`, `os.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/kernel.h`, `linux/console.h`, `linux/init.h`, `os.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/early_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/exec.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/exec.c

### Purpose
`exec.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `void flush_thread(void)`; `void start_thread(struct pt_regs *regs, unsigned long eip, unsigned long esp)`; `arch_flush_thread(&current->thread.arch);`; `current_pt_regs()->regs.fp);`; `clear_thread_flag(TIF_SINGLESTEP);`; `EXPORT_SYMBOL(start_thread);`. The file has 37 lines and depends on `linux/stddef.h`, `linux/module.h`, `linux/fs.h`, `linux/ptrace.h`, `linux/sched/mm.h`, `linux/sched/task.h`, `linux/sched/task_stack.h`, `linux/slab.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/stddef.h`, `linux/module.h`, `linux/fs.h`, `linux/ptrace.h`, `linux/sched/mm.h`, `linux/sched/task.h`, `linux/sched/task_stack.h`, `linux/slab.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/exitcode.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/exitcode.c

### Purpose
`exitcode.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `struct proc_dir_entry *ent;`; `static int exitcode_proc_show(struct seq_file *m, void *v)`; `static int exitcode_proc_open(struct inode *inode, struct file *file)`; `if (copy_from_user(buf, buffer, size))`; `if ((*end != '\0') && !isspace(*end))`; `static int make_proc_exitcode(void)`; `seq_printf(m, "%d\n", val);`; `return single_open(file, exitcode_proc_show, NULL);`; `__initcall(make_proc_exitcode);`. The file has 79 lines and depends on `linux/ctype.h`, `linux/init.h`, `linux/kernel.h`, `linux/module.h`, `linux/proc_fs.h`, `linux/seq_file.h`, `linux/types.h`, `linux/uaccess.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/ctype.h`, `linux/init.h`, `linux/kernel.h`, `linux/module.h`, `linux/proc_fs.h`, `linux/seq_file.h`, `linux/types.h`, `linux/uaccess.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/exitcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/gprof_syms.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/gprof_syms.c

### Purpose
`gprof_syms.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `extern void mcount(void);`; `EXPORT_SYMBOL(mcount);`. The file has 9 lines and depends on `linux/module.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/module.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/gprof_syms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/initrd.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/initrd.c

### Purpose
`initrd.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `int __init read_initrd(void)`; `if (!initrd)`; `if (!area)`; `static int __init uml_initrd_setup(char *line, int *add)`. The file has 46 lines and depends on `linux/init.h`, `linux/memblock.h`, `linux/initrd.h`, `asm/types.h`, `init.h`, `os.h`, `um_arch.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/init.h`, `linux/memblock.h`, `linux/initrd.h`, `asm/types.h`, `init.h`, `os.h`, `um_arch.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/initrd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/irq.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/irq.c

### Purpose
This file is UMLs fd/signal-backed interrupt controller. It maps host epoll/SIGIO readiness to Linux IRQs, supports read/write events, dynamic IRQ allocation, suspend/resume wake state, and optional time-travel IRQ delivery.

### Important APIs, Types, And Functions
Important types are `irq_reg` and `irq_entry`. Key APIs are `um_request_irq()`, `um_request_irq_tt()`, `um_free_irq()`, `free_irq_by_fd()`, `deactivate_fd()`, `deactivate_all_fds()`, `do_IRQ()`, `init_IRQ()`, SIGIO/SIGCHLD handlers, PM helpers, and arch interrupt display.

### Control Flow
Registration makes fds async, creates or updates an epoll entry under `irq_lock`, stores read/write event registrations, optionally attaches time-travel handlers, and calls `request_irq()`. SIGIO processing polls triggered entries, invokes time-travel handlers or `do_IRQ()`, coalesces reentry through active/pending flags, and frees deferred IRQs.

### State, Persistence, And Dependencies
State includes the active fd list, allocated IRQ bitmap, per-fd registrations, suspended/wakeup flags, pending time-travel events, and per-CPU IRQ stats. Dependencies include host epoll wrappers, SIGIO management, Linux IRQ core, time-travel APIs, and UML signal register handling.

### Integration Points And Risks
Risks include lockless epoll assumptions, fd reuse races, dynamic IRQ range interactions with MSI, pending-event handling during suspend, and cleanup ordering when handlers unregister themselves. Integration is used by xterm, virtio, VFIO, network, and other fd-backed drivers.

### Test Signals
Test read/write fd IRQs, duplicate registrations, handler reentry, dynamic IRQ exhaustion, free-by-fd, suspend/resume wake, external time-travel handlers, SIGCHLD, and `/proc/interrupts` counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/kmsg_dump.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/kmsg_dump.c

### Purpose
`kmsg_dump.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `struct kmsg_dump_detail *detail)`; `struct console *con;`; `if (con)`; `if (!spin_trylock_irqsave(&lock, flags))`; `static int __init kmsg_dumper_stdout_init(void)`; `static DEFINE_SPINLOCK(lock);`; `console_srcu_read_unlock(cookie);`; `kmsg_dump_rewind(&iter);`; `printf("kmsg_dump:\n");`; `printf("%s", line);`; `spin_unlock_irqrestore(&lock, flags);`; `return kmsg_dump_register(&kmsg_dumper);`; `__uml_postsetup(kmsg_dumper_stdout_init);`. The file has 65 lines and depends on `linux/kmsg_dump.h`, `linux/spinlock.h`, `linux/console.h`, `linux/string.h`, `shared/init.h`, `shared/kern.h`, `os.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/kmsg_dump.h`, `linux/spinlock.h`, `linux/console.h`, `linux/string.h`, `shared/init.h`, `shared/kern.h`, `os.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/kmsg_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/ksyms.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/ksyms.c

### Purpose
`ksyms.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `EXPORT_SYMBOL(um_get_signals);`; `EXPORT_SYMBOL(um_set_signals);`; `EXPORT_SYMBOL(os_stat_fd);`; `EXPORT_SYMBOL(os_stat_file);`; `EXPORT_SYMBOL(os_access);`; `EXPORT_SYMBOL(os_set_exec_close);`; `EXPORT_SYMBOL(os_getpid);`; `EXPORT_SYMBOL(os_open_file);`; `EXPORT_SYMBOL(os_read_file);`; `EXPORT_SYMBOL(os_write_file);`; `EXPORT_SYMBOL(os_seek_file);`; `EXPORT_SYMBOL(os_lock_file);`; `EXPORT_SYMBOL(os_ioctl_generic);`; `EXPORT_SYMBOL(os_pipe);`. The file has 48 lines and depends on `linux/module.h`, `os.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/module.h`, `os.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/load_file.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/load_file.c

### Purpose
`load_file.c` implements UML runtime behavior in `sources/distributed-fs/ceph-client/arch/um/kernel`. It is part of the user-mode Linux architecture support code carried in this source tree.

### Important APIs, Types, And Functions
Important local functions, types, declarations, or macros include `static int __init __uml_load_file(const char *filename, void *buf, int size)`; `void *uml_load_file(const char *filename, unsigned long long *size)`; `if (!filename)`; `if (err)`; `os_close_file(fd);`; `printk(KERN_ERR "\"%s\" is empty\n", filename);`; `memblock_free(area, *size);`. The file has 59 lines and depends on `linux/memblock.h`, `os.h`, `um_arch.h`.

### Control Flow
Control flow follows Linux arch-driver conventions: initialization or exported entry points set up UML state, callbacks are reached from generic kernel subsystems, and host operations are performed through UML `os_*` wrappers where needed.

### State, Persistence, And Dependencies
State is held in file-scope globals, embedded kernel objects, caller-owned structs, host fds/processes, or mm/IRQ/task structures depending on the callbacks used. Dependencies include `linux/memblock.h`, `os.h`, `um_arch.h`.

### Integration Points And Risks
Risks include host errno handling, resource cleanup on partial failures, locking against signal/IRQ callbacks, and assumptions made by generic Linux code when running inside a host process. Integration is with the adjacent UML arch code and generic kernel subsystems.

### Test Signals
Exercise initialization, teardown, error paths, callback entry points, host-resource failures, and any related generic kernel subsystem selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/load_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/mem.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/mem.c

### Purpose
This file initializes UML memory-management state after early physical memory setup.

### Important APIs, Types, And Functions
It implements optional KASAN init, defines `swapper_pg_dir`, `kmalloc_ok`, `arch_mm_preinit()`, `mem_init()`, `arch_zone_limits_init()`, no-op `free_initmem()`, `pgd_alloc()`, `uml_kmalloc()`, the protection map, and `mark_rodata_ro()`.

### Control Flow
Preinit enables KASAN after jump labels, maps/frees the post-brk reserved area into memblock, updates `uml_reserved` and PFN bounds, and later enables normal kmalloc. `pgd_alloc()` copies kernel-half PGD entries into new mms.

### State, Persistence, And Dependencies
State includes swapper page directory, `kmalloc_ok`, brk boundary, memblock zones, PFN limits, protection map, and rodata page permissions. Dependencies include memblock, slab, KASAN, UML address layout, `map_memory()`, host `sbrk()`, and pgtable helpers.

### Integration Points And Risks
Risks include early allocation ordering, brk/reserved mapping correctness, no freeing of kernel image initmem, KASAN enable timing, and rodata alignment. Integration is with generic mm boot and page-table allocation.

### Test Signals
Boot with KASAN on/off, varied memory sizes, fork/exec PGD copying, rodata write protection, and early allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/physmem.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/physmem.c

### Purpose
This file creates and maps UMLs host-backed physical memory file.

### Important APIs, Types, And Functions
It defines `physmem_fd`, exported `high_physmem`, `map_memory()`, `setup_physmem()`, exported `phys_mapping()`, and `mem=` setup parsing.

### Control Flow
`setup_physmem()` validates the requested memory, creates a backing file, maps memory after the executable image, writes the syscall stub page into the backing file, registers/reserves memblock ranges, and sets low PFN bounds. `phys_mapping()` maps physical offsets to the backing fd.

### State, Persistence, And Dependencies
Persistent state is the backing fd, host mappings, memblock records, `high_physmem`, PFN bounds, and `physmem_size`. Dependencies include host memory-file/mmap wrappers, linker symbols, memblock, address conversion macros, and syscall stub sections.

### Integration Points And Risks
Risks include host `vm.max_map_count` failures, too-small `mem=`, backing-file visibility limits for DMA, and single-range assumptions. Integration feeds SKAS, vhost-user, VFIO, and generic memory management.

### Test Signals
Boot with varied `mem=`, trigger low-memory failure, validate vhost/VFIO memory mapping, and execute syscall stub paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/physmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/process.c -->
## sources/distributed-fs/ceph-client/arch/um/kernel/process.c

### Purpose
This file implements UML task switching, thread creation, idle behavior, exitcall execution, and wait-channel reporting.

### Important APIs, Types, And Functions
Key APIs include `cpu_tasks`, stack alloc/free, `__switch_to()`, `interrupt_end()`, `new_thread_handler()`, `copy_thread()`, `initial_thread_cb()`, `arch_dup_task_struct()`, idle hooks, `__uml_cant_sleep()`, `do_uml_exitcalls()`, `uml_strdup()`, `copy_from_user_proc()`, `singlestepping()`, `arch_align_stack()`, and `__get_wchan()`.

### Control Flow
Context switch updates the per-CPU current task, jumps between saved buffers, and invokes subarch switch code. Fork seeds either copied user registers or kernel-thread safe registers, creates a jump buffer targeting a fork/new-thread handler, optionally sets TLS, and eventually enters `userspace()`. `interrupt_end()` drains reschedule, signal, and notify work.

### State, Persistence, And Dependencies
State includes per-CPU current task pointers, per-task jump buffers/registers, task stacks, UML exitcall sections, and time-travel idle behavior. Dependencies include scheduler core, SKAS switching, subarch TLS/register helpers, signal handling, random stack alignment, and task stack helpers.

### Integration Points And Risks
Risks include jump-buffer corruption, init_task dynamic-size handling, TLS ordering, recursive scheduling in work-mask loops, and heuristic wait-channel stack scanning. Integration is central to all UML process and kernel-thread execution.

### Test Signals
Test fork/clone/kernel threads, exec, TLS, context switching under SMP, signals after interrupts, idle with time travel, UML exitcalls, and wait-channel reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/kernel/process.c -->
