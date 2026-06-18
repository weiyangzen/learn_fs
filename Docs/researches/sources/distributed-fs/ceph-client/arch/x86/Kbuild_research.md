# sources/distributed-fs/ceph-client/arch/x86/Kbuild

## Purpose
Top-level x86 architecture Kbuild file selecting major x86 subdirectories for compilation.

## Important APIs, Types, and Functions
Adds branch-profiling disable define for `CONFIG_TRACE_BRANCH_PROFILING`, then includes boot startup, confidential computing, entry, perf events, KVM, Xen, PVH, Hyper-V, realmode, kernel, mm, crypto, IA32 emulation, platform, net, kexec purgatory, and virt subtrees based on configuration. Also lists `boot` and `tools` for cleaning.

## Control Flow, State, and Persistence
No runtime state. It controls build graph inclusion for x86 kernels.

## Dependencies and Integration Points
Used by top-level Kbuild for x86. Although adjacent to UML in this subset, it is a generic x86 build selector and not UML-specific.

## Risks and Test Signals
Risks are config-conditional directory omissions, branch profiling entering noinstr code, or clean targets missing generated files. Test x86 defconfigs, KVM/Xen/Hyper-V toggles, tracing configs, and `make clean`.
