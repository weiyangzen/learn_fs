<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.c -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.c

Purpose: Shared class and character-device registry for Xillybus and XillyUSB. It creates `/dev/xillybus_*` or enumerated `/dev/xillyusb_##_*` device nodes from IDT-provided stream names and maps inodes back to driver-private endpoint/channel indices.

Important APIs/types/functions: `struct xilly_unit` tracks one registered cdev range, private endpoint pointer, name prefix, major/minor span, and list node. `xillybus_init_chrdev()` allocates a char-dev region, cdev, and device nodes. `xillybus_cleanup_chrdev()` destroys nodes and unregisters the range. `xillybus_find_inode()` maps an inode major/minor to private data and stream index. Module init/exit registers the `xillybus` class.

Control flow: registration optionally enumerates a unique unit name, allocates `num_nodes` minors, adds one cdev covering the range, scans the NUL-separated IDT name list, creates class devices named `<unit>_<idt-name>`, validates that name data is neither short nor long, and records the unit. Cleanup finds the unit by private pointer, destroys every minor, deletes cdev, unregisters the range, removes the list entry, and frees state. Inode lookup scans the unit list under a mutex and returns the matching private pointer plus minor offset.

State and persistence: `unit_list` and `unit_mutex` are module-global runtime state. Device nodes exist while endpoints are registered but are removed on endpoint cleanup or module unload.

Dependencies and integration: used by PCIe/OF Xillybus core and XillyUSB. It depends on class devices, cdev, dynamic major allocation, and IDT name strings from hardware discovery.

Risks: IDT name-list length must exactly match `num_nodes`; otherwise registration unrolls. Device names are built into a 48-byte stack buffer and unit names into 16 bytes, so truncation/uniqueness behavior matters. `xillybus_find_inode()` relies on the unit list remaining stable until callers take their own references; XillyUSB adds `kref_mutex` around that gap.

Test signals: register/remove units with multiple nodes, long/short/malformed name lists, duplicate prefixes with enumeration, open devices before and during disconnect, and verify no stale majors/minors or class devices remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.c -->
