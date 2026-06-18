# sources/distributed-fs/ceph-client/include/uapi/linux/module.h

## Purpose
Defines flags accepted by `finit_module(2)` for loading kernel modules with version/vermagic override behavior or compressed module input.

## Important APIs, Types, And Functions
Exports `MODULE_INIT_IGNORE_MODVERSIONS`, `MODULE_INIT_IGNORE_VERMAGIC`, and `MODULE_INIT_COMPRESSED_FILE`.

## Control Flow
Userspace passes these flags to `finit_module`; the kernel module loader either enforces or bypasses selected compatibility checks and optionally treats the file as compressed.

## State, Persistence, And Dependencies
Successful calls persist by loading module state into the kernel. The header has no dependencies.

## Integration Points
Used by module-loading tools such as kmod/insmod and kernel selftests.

## Risks
Ignoring modversions or vermagic can load incompatible modules and destabilize the kernel. Compressed-file support is kernel-configuration dependent.

## Test Signals
Test flag acceptance/rejection, compressed module loading, incompatible vermagic/modversion behavior, and permission/capability enforcement.
