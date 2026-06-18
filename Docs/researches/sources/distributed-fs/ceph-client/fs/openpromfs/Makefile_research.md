## sources/distributed-fs/ceph-client/fs/openpromfs/Makefile

### Purpose
This Makefile wires the Sun OpenPROM pseudo filesystem into the kernel build when `CONFIG_SUN_OPENPROMFS` is enabled.

### Important APIs, types, and functions
- `obj-$(CONFIG_SUN_OPENPROMFS) += openpromfs.o` declares the module or built-in object.
- `openpromfs-objs := inode.o` states that `inode.c` is the sole implementation object.

### Control flow
Kbuild evaluates the config symbol and includes `openpromfs.o`; the composite object is linked from `inode.o`.

### State and persistence behavior
No runtime state is managed here. It controls build-time inclusion only.

### Dependencies and integration points
Depends on the architecture/configuration exposing `CONFIG_SUN_OPENPROMFS` and on `inode.c` providing module init and exit hooks.

### Risks
The only material risk is build drift if additional source files are added without updating `openpromfs-objs`.

### Test signals
Build with `CONFIG_SUN_OPENPROMFS=y` and `m` should produce the expected object/module and resolve the filesystem registration symbols from `inode.c`.
