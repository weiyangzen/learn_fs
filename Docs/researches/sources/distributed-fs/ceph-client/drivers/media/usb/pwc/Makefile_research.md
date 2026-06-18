## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/Makefile

### Purpose
`Makefile` composes the `pwc` kernel module from its interface, control, V4L2, decompression, and mode-table objects.

### Important APIs, Types, And Functions
`pwc-objs` includes `pwc-if.o`, `pwc-misc.o`, `pwc-ctrl.o`, `pwc-v4l.o`, `pwc-uncompress.o`, `pwc-dec1.o`, `pwc-dec23.o`, `pwc-kiara.o`, and `pwc-timon.o`. `obj-$(CONFIG_USB_PWC) += pwc.o` connects the object list to the Kconfig symbol.

### Control Flow
There is no runtime flow. The object list determines link order and whether data tables/decompressors are present in the final driver.

### State, Persistence, And Dependencies
The file contributes to build-system state only. All driver runtime state lives in the linked objects.

### Integration Points
The Makefile integrates PWC with the kernel kbuild system and `CONFIG_USB_PWC`.

### Risks
Omitting any table or decompressor object would produce unresolved symbols or runtime feature loss. Adding new chipset support requires updating this object list.

### Test Signals
Build tests should verify `CONFIG_USB_PWC=m` produces `pwc.ko` and that all expected symbols resolve.
