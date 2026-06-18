# sources/distributed-fs/glusterfs/xlators/features/leases/src/Makefile.am

## Purpose
Builds the server-side `leases.la` feature translator module.

## Important APIs, Types, and Functions
Compiles `leases.c` and `leases-internal.c`, lists private headers, links to `libglusterfs.la`, and adds libglusterfs, XDR/RPC, and timer-wheel include paths.

## Control Flow
The module is built when `WITH_SERVER` is enabled and installed into the feature xlator directory.

## State and Persistence
No runtime state; only build declarations.

## Dependencies and Integration Points
Timer-wheel include path is required because the leases implementation uses GlusterFS timer wheel APIs for recall expiry.

## Risks and Edge Cases
If a new leases source file is added but not listed, it will not be compiled. Missing timer-wheel include support breaks recall timer compilation.

## Test Signals
Build should produce `leases.la` and compile both public fop wrappers and internal lease logic.
