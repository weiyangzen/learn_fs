# sources/distributed-fs/openafs/src/audit/Makefile.in

## Purpose
This makefile builds and installs the OpenAFS audit support libraries and public `afs/audit.h` header.

## Important APIs, types, and functions
Build products are `liboafs_audit.la`, `libaudit_pic.la`, `libaudit.a`, `${TOP_LIBDIR}/libaudit.a`, and `${TOP_INCDIR}/afs/audit.h`. Object inputs are `audit.lo`, `audit-file.lo`, and `audit-sysvmq.lo`. Shared-library dependencies include rxkad and util libraries.

## Control flow
The `all` target builds shared, PIC, static, installed-library, and installed-header outputs. Object dependency rules tie audit sources to `audit.h` and `audit-api.h`. `install` and `dest` copy library/header files into package or destination trees. `dest` conditionally installs AIX audit sample files for `rs_aix*`. `clean` removes libtool outputs and generated component files.

## State and persistence
The makefile writes build artifacts under the object tree and install artifacts under `${TOP_LIBDIR}`, `${TOP_INCDIR}`, `${DESTDIR}`, or `${DEST}`. It does not modify source configuration.

## Dependencies and integration points
It includes OpenAFS config, LWP, and lwptool make fragments and participates in the larger libtool build. `liboafs_audit.la` is consumed by auth and server components that emit audit events.

## Risks
The comment says auditing was historically AIX-focused, but the makefile now builds file and SysV MQ backends when available. Install coverage for backend-specific runtime assets is mostly AIX sample oriented. Missing `HAVE_SYS_IPC_H` changes symbols compiled into `audit-sysvmq.lo`.

## Test signals
Run configure/build on Unix with and without SysV IPC headers, verify static/shared/PIC libraries, install and dest targets, AIX sample conditional paths, and clean idempotence.
