# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/lvm-defaults.h

Purpose: `lvm-defaults.h` defines hard-coded paths to LVM command-line tools used by GlusterFS components that manage or inspect logical volumes.

Important APIs and types: it exports only macros: `LVM_RESIZE`, `LVM_CREATE`, `LVM_CONVERT`, `LVM_REMOVE`, and `LVS`, all pointing under `/sbin`.

Control flow and state: no runtime state or logic. Callers embed these strings when invoking external commands, usually through the runner/syscall stack.

Dependencies and integration: integrates with storage-management code outside this subset. It is related to `run.h` because these command paths are ultimately executed as child processes.

Risks: hard-coded `/sbin` paths can be wrong on distributions using `/usr/sbin`, merged `/usr`, containers, or custom LVM installations. These constants should not be assumed portable without configure-time checks or override paths.

Test signals: packaging tests should assert that referenced paths exist or are configured for the target platform. Any LVM workflow tests should verify command-not-found handling and user-facing diagnostics.
