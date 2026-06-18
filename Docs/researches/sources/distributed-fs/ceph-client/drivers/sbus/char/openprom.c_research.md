# sources/distributed-fs/ceph-client/drivers/sbus/char/openprom.c

Purpose: implements the SPARC `/dev/openprom` misc device, providing SunOS/Solaris and NetBSD-compatible ioctls for reading, navigating, and modifying the Open Firmware device tree and PROM options.

Important APIs/types/functions: per-file `openprom_private_data` stores current and last nodes. User-copy helpers `copyin()`, `getstrings()`, `copyout()`, and `copyin_string()` validate and allocate ioctl buffers. SunOS handlers include `opromgetprop()`, `opromnxtprop()`, `opromsetopt()`, `opromnext()`, `oprompci2node()`, `oprompath2node()`, and `opromgetbootargs()`. NetBSD handlers include `opiocget()`, `opiocnextprop()`, `opiocset()`, and `opiocgetnext()`. `openprom_ioctl()` dispatches by command and file mode; `openprom_open()` initializes per-file node state.

Control flow: module init registers the misc device and resolves the `/options` node. On open, each descriptor starts at the root node. SunOS ioctls operate either on `/options`, the current node, or a node selected by phandle/path/PCI tuple. NetBSD ioctls copy an `opiocdesc`, resolve the node by phandle, and get/set properties or enumerate nodes/properties. A global mutex serializes all operations.

State and persistence: per-file state tracks current traversal nodes. Global state stores `options_node`. `of_set_property()` calls can mutate the live kernel OF tree/options representation and may affect firmware-like settings exposed to user programs, but the file itself has no independent persistent storage.

Dependencies and integration: depends on SPARC PROM/Open Firmware APIs, miscdevice minor `SUN_OPENPROM_MINOR`, openprom ioctl ABI headers, saved kernel command line, and optional PCI lookup for `OPROMPCI2NODE`.

Risks and test signals: node references from `of_find_node_by_*()` are stored without consistent `of_node_put()` balancing, matching older OF lifetime assumptions but worth auditing. `opiocnextprop()` appears to copy the next property's value rather than name, which is notable for a "next property" call. `oprompci2node()` calls `pci_device_to_OF_node()` before checking whether `pci_get_domain_bus_and_slot()` returned NULL. Property set operations accept user-provided names/values under write mode. Test SunOS and NetBSD ioctl compatibility, read/write mode permission checks, maximum buffer truncation, malformed user pointers, path/phandle traversal, PCI lookup absent/present, property set/get round trips, compat ioctl coverage, and module init when `/options` is missing.
