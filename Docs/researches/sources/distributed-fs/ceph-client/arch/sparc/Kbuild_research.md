<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sparc/Kbuild

## Purpose
This top-level SPARC Kbuild file selects architecture subdirectories for the kernel build.

## Important APIs, Types, and Functions
It adds `kernel/`, `mm/`, `math-emu/`, `net/`, and `crypto/` to `obj-y`, and adds `vdso/` only when `CONFIG_SPARC64` is enabled.

## Control Flow
Kbuild includes this file after architecture configuration; object-directory traversal follows the `obj-y` list.

## State and Persistence Behavior
There is no runtime state. Build state is the set of subdirectories compiled into the SPARC kernel.

## Dependencies and Integration Points
It depends on standard Kbuild object directory semantics and `CONFIG_SPARC64`. It connects the arch root to SPARC kernel, MM, math emulation, networking, crypto, and vDSO code.

## Risks
Omitting a directory silently drops architecture functionality. Adding `vdso/` to 32-bit builds would break because the included vDSO rules are SPARC64-specific.

## Test Signals
Build SPARC32 and SPARC64 defconfigs and confirm the expected subdirectories are visited, with `arch/sparc/vdso` only in 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/Kbuild -->
