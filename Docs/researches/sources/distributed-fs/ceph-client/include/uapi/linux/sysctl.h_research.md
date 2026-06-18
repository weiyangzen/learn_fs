# sources/distributed-fs/ceph-client/include/uapi/linux/sysctl.h

## Purpose
Defines the legacy binary `sysctl()` UAPI: `struct __sysctl_args` and numeric MIB names for kernel, VM, network, filesystem, device, ABI, and architecture-specific controls. The header warns that numbering is exported and must not be changed.

## Important APIs, Types, and Constants
`CTL_MAXNAME` limits path components. `struct __sysctl_args` contains user pointers for name vector, old value/length, new value/length, and unused padding. Top-level enums include `CTL_KERN`, `CTL_VM`, `CTL_NET`, `CTL_FS`, `CTL_DEBUG`, `CTL_DEV`, `CTL_ABI`, `CTL_CPU`, `CTL_SUNRPC`, and others. Large enum groups define kernel settings (`KERN_*`), VM settings (`VM_*`), network families and protocol controls (`NET_*`), filesystem controls (`FS_*`), device controls (`DEV_*`), and ABI controls.

## Control Flow, State, and Persistence
Userspace passes an integer path and optional old/new buffers to the binary syscall. Kernel sysctl tables resolve the path, copy data out/in, and may mutate runtime kernel state. The numeric path values are persistent ABI, even for obsolete or removed entries.

## Dependencies and Integration Points
Depends on `<linux/const.h>`, `<linux/types.h>`, and `<linux/compiler.h>`. Integrates with the deprecated `sysctl()` syscall, procfs `/proc/sys`, networking sysctls, SUNRPC debug, filesystem tunables, and legacy tools such as old `strace` builds.

## Risks and Test Signals
Risks are severe ABI breakage from renumbering, stale entries that no longer correspond to active procfs files, pointer-size compatibility through `__user` members, and security-sensitive write controls. Test by compiling old sysctl callers, checking numeric stability, verifying unsupported paths fail compatibly, and comparing binary/sysctl-proc behavior where still implemented.
