# sources/distributed-fs/ceph-client/drivers/block/xen-blkback/Makefile

Purpose: This Makefile wires the Xen block backend driver into Kbuild. When `CONFIG_XEN_BLKDEV_BACKEND` is enabled, it builds the `xen-blkback` module/object from the backend request engine and Xenbus integration sources.

Important APIs, types, and functions: There are no C APIs or runtime types in this file. The important build declarations are `obj-$(CONFIG_XEN_BLKDEV_BACKEND) := xen-blkback.o` and `xen-blkback-y := blkback.o xenbus.o`. These Kbuild variables define the module name and its constituent objects.

Control flow: Kbuild evaluates the `obj-*` assignment based on kernel configuration. If Xen block backend support is selected, `blkback.o` and `xenbus.o` are linked into `xen-blkback.o`; otherwise this directory contributes no object for the backend.

State and persistence behavior: The file has no runtime state, persistence, or generated output by itself. Its only persistent effect is the build graph encoded in the repository: changing it changes which objects are compiled into the kernel/module.

Dependencies and integration points: The Makefile depends on the kernel Kbuild system and the `CONFIG_XEN_BLKDEV_BACKEND` Kconfig symbol. It integrates `blkback.c` (request processing, grant mapping, bio submission) with `xenbus.c` (device discovery/configuration and ring setup), matching declarations shared in `common.h`.

Risks and edge cases: Build omissions are the main risk. Removing `xenbus.o` would leave no Xenbus frontend/backend negotiation; removing `blkback.o` would leave declarations without the actual I/O engine. Renaming the module target changes module identity and aliases expected by Xen tooling.

Test signals: Build with `CONFIG_XEN_BLKDEV_BACKEND=y` and `=m` should compile/link `xen-blkback.o` from both objects. Build with the symbol disabled should skip the object. Module metadata and alias checks should confirm the resulting object includes the `xen-backend:vbd` alias from `blkback.c`.
