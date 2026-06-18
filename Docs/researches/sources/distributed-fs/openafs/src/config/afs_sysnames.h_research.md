# sources/distributed-fs/openafs/src/config/afs_sysnames.h

Purpose: assigns stable numeric IDs to OpenAFS `SYS_NAME` platform strings.

Important APIs/types/functions: defines `SYS_NAME_ID_*` constants for historical and current AFS platforms, including Darwin, AIX, Solaris, Linux architectures, FreeBSD/NetBSD/OpenBSD/DragonFly, HP-UX, Windows, ARM, and ppc64le, plus realm-size constants `AFS_REALM_SZ` and `AFS_NUM_LREALMS`.

Control flow: no runtime flow. Platform `param.*.h` files set `SYS_NAME` and `SYS_NAME_ID` to one of these constants, allowing conditional compilation and system-name exchange to use stable IDs.

State and persistence: no runtime state; the file is a persistent registry of ABI/build identifiers.

Dependencies and integration: installed as `afs/afs_sysnames.h` by `src/config/Makefile.in` and included by generated `param.h` consumers.

Risks and test signals: risks are duplicate IDs, missing IDs for new `param.*.h` files, and accidental renumbering that breaks compatibility. Signals are compiling every platform header and verifying each `SYS_NAME_ID` reference resolves uniquely.
