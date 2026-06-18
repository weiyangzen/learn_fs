# sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_internal.h

## Purpose
`kexec_handover_internal.h` is the private KHO header shared by core, debug, and debugfs implementations. It declares scratch globals and provides conditional debug/debugfs APIs or no-op stubs.

## Important APIs, Types, and Functions
When debugfs is enabled, `struct kho_debugfs` contains a root directory, subtree directory, and list of FDT blob wrappers; otherwise it is an empty struct. It declares `kho_scratch`, `kho_scratch_cnt`, `kho_debugfs_init()`, `kho_in_debugfs_init()`, `kho_out_debugfs_init()`, `kho_debugfs_blob_add()`, `kho_debugfs_blob_remove()`, and `kho_scratch_overlap()`.

## Control Flow
KHO core can call the debugfs and debug functions unconditionally; the header resolves them to real implementations or inline no-ops/false based on configuration.

## State and Persistence Behavior
The header exposes global scratch descriptor state. Debugfs list state exists only with `CONFIG_KEXEC_HANDOVER_DEBUGFS`.

## Dependencies and Integration Points
It includes public KHO types, list/types, and debugfs when configured. It is included by `kexec_handover.c`, `kexec_handover_debug.c`, and `kexec_handover_debugfs.c`.

## Risks and Test Signals
Stub signatures must stay compatible with real implementations so KHO core code remains config-independent. Build tests should cover every combination of KHO debug and debugfs.
