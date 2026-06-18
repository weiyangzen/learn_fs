# sources/distributed-fs/ceph-client/net/ceph/Makefile

## Purpose
Builds the `libceph.o` composite object when `CONFIG_CEPH_LIB` is enabled.

## Important APIs, Types, and Functions
The key build rule is `obj-$(CONFIG_CEPH_LIB) += libceph.o`. `libceph-y` lists the component objects: common client setup, messenger v1/v2, message pools, buffers, pagelists, monitor and OSD clients, OSD maps, CRUSH, striping, debugfs, auth backends, crypto/armor, strings/hashes, page vectors, snapshots, and string tables.

## Control Flow
Kbuild compiles each listed object and links them into `libceph.o`. The order matters only where init/exit references require symbols to be linked into the composite object; runtime init order is in `ceph_common.c`.

## State and Persistence
No runtime state. It persists build composition in generated objects and modules.

## Dependencies and Integration Points
Integrates with Kbuild and `Kconfig`. The file defines the library surface available to CephFS and RBD by including protocol, crypto, placement, and client-control objects in one module.

## Risks
Missing an object from `libceph-y` causes link failures or feature loss. Adding objects with init/exit side effects requires checking `init_ceph_lib()` ordering. Build composition should stay synchronized with Kconfig crypto and networking selections.

## Test Signals
Build libceph built-in and as a module, run `modinfo`/symbol checks for exported auth, crypto, CRUSH, and client helpers, and verify no unresolved symbols under common CephFS/RBD configurations.
