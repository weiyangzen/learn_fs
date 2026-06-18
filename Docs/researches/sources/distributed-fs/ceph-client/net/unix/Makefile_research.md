<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/Makefile -->
# sources/distributed-fs/ceph-client/net/unix/Makefile

## Purpose
The Makefile maps Unix domain socket configuration symbols to kernel objects.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_UNIX) += unix.o` builds the core AF_UNIX object.
- `unix-y := af_unix.o garbage.o` always includes the main socket implementation and SCM_RIGHTS garbage collector in core UNIX support.
- `unix-$(CONFIG_SYSCTL) += sysctl_net_unix.o` adds sysctl support.
- `unix-$(CONFIG_BPF_SYSCALL) += unix_bpf.o` adds sockmap/BPF integration.
- `obj-$(CONFIG_UNIX_DIAG) += unix_diag.o` and `unix_diag-y := diag.o` build the diagnostic interface separately.

## Control Flow
Kbuild links selected component objects into `unix.o` and optionally `unix_diag.o`. Runtime init order is then controlled by initcalls and module init in the C files.

## State and Persistence
No runtime state is present. The file persists only build composition.

## Dependencies and Integration Points
It ties `Kconfig` symbols to `af_unix.c`, `garbage.c`, `sysctl_net_unix.c`, `unix_bpf.c`, and `diag.c`.

## Risks and Edge Cases
Build composition must keep `garbage.o` with `af_unix.o` because the main file calls SCM_RIGHTS GC hooks unconditionally. Optional `unix_bpf.o` must only be included when BPF syscall support provides sockmap helpers.

## Test Signals
Compile with and without `CONFIG_SYSCTL`, `CONFIG_BPF_SYSCALL`, and `CONFIG_UNIX_DIAG`; verify there are no unresolved symbols and the expected modules/objects appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/Makefile -->
