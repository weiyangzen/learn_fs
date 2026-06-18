# sources/distributed-fs/ceph-client/scripts/gdb/linux/utils.py

## Purpose
`utils.py` is the shared foundation for the Linux GDB helper suite: type caching, `container_of`, endian-aware memory reads, architecture and gdbserver detection, vmcore parsing, vmlinux lookup, and pagination control.

## Important APIs, Types, and Functions
`CachedType` caches GDB type lookups and invalidates on new objfiles. Scalar type getters expose common kernel types. `container_of()` and `$container_of()` compute enclosing structures. `read_u16/u32/u64/ulong/atomic_long()` decode target memory. `is_target_arch()`, `get_gdbserver_type()`, `qemu_phy_mem_mode()`, `parse_vmcore()`, `get_vmlinux()`, and `pagination_off()` support higher-level commands.

## Control Flow
Helpers are called directly by other modules. Type caching lazily resolves types and attaches a one-shot new-objfile handler. `qemu_phy_mem_mode()` and `pagination_off()` are context managers that save state, apply a temporary mode, and restore it.

## State and Persistence Behavior
Global caches store type, endianness, architecture, and gdbserver detection results. These are GDB-session state only; target kernel memory is not modified.

## Dependencies and Integration Points
Almost every helper imports this module. It relies on Python GDB APIs, inferior memory reads, monitor packets for QEMU physical-memory mode, and objfile metadata.

## Risks and Test Signals
`offset_of()` uses a null pointer expression and string parsing; unusual GDB formatting can break it. Cached endianness/architecture may go stale if the target changes. Test type invalidation after `symbol-file`, memory read decoding on big/little endian targets, and QEMU/KGDB detection paths.
