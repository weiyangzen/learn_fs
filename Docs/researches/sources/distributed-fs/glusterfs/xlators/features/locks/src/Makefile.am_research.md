# sources/distributed-fs/glusterfs/xlators/features/locks/src/Makefile.am

## Purpose
Builds the server-side locks/posix-locks translator module.

## Important APIs, Types, and Functions
Compiles `common.c`, `posix.c`, `entrylk.c`, `inodelk.c`, `reservelk.c`, and `clear.c`; lists private headers; links with `libglusterfs.la`; and installs a `posix-locks.so` symlink to `locks.so`.

## Control Flow
`locks.la` is built only when `WITH_SERVER` is enabled. Install/uninstall hooks manage the compatibility symlink.

## State and Persistence
No runtime state. Build artifacts include the translator shared object and symlink.

## Dependencies and Integration Points
Includes libglusterfs and RPC/XDR headers, and uses `-fno-strict-aliasing`, likely because the locks code uses alias-heavy internal structs.

## Risks and Edge Cases
Symlink install hooks must remain in sync with module naming. Adding/removing locks sources requires updating `locks_la_SOURCES`.

## Test Signals
Build/install tests should verify both `locks.so` and `posix-locks.so` are available for server deployments.
