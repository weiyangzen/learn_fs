<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.h -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.h

Purpose: Header exposing the Xillybus class registry to core and USB drivers.

Important APIs/types/functions: Declares `xillybus_init_chrdev()`, `xillybus_cleanup_chrdev()`, and `xillybus_find_inode()`.

Control flow: no runtime flow; it defines the interface for creating/removing named device nodes and resolving an opened inode.

State and persistence: no state in the header. Runtime state lives in `xillybus_class.c`.

Dependencies and integration: included by `xillybus_core.c` and `xillyusb.c`; depends on Linux device, file-operations, inode, and module types.

Risks: prototype changes affect both PCIe/OF and USB variants. The `private_data` pointer is opaque, so caller lifetime rules are external to this header.

Test signals: compile both families and verify device-node creation/open paths use the declared API correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus_class.h -->
