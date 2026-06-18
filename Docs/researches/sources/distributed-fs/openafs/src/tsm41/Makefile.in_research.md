# sources/distributed-fs/openafs/src/tsm41/Makefile.in

## Purpose
Builds AIX TSM/LAM dynamic authentication modules for OpenAFS. It creates legacy AFS password modules, Kerberos-authenticated variants, and an AIX 5 Kerberos 5 `aklog` dynamic auth module.

## Important APIs, Types, And Functions
Outputs are `afs_dynamic_auth`, `afs_dynamic_kerbauth`, optional `aklog_dynamic_auth`, and optional Kerberos 5 targets controlled by `@MAKE_KRB5@`. Object groups are `AUTH_OBJS`, `AUTH_KRB_OBJS`, and `AUTH_KRB5_OBJS`. Library sets `AFSLIBS` and `KAFSLIBS` pull kauth/prot/ubik/auth/rxkad/sys/crypto/rx/lwp/cmd/com_err/audit/util/opr variants. Link entry points are `-eafs_initialize` and `-eaklog_initialize`.

## Control Flow
The makefile compiles platform-specific `aix_auth.o` from `aix41_auth.c` for AIX 4 or `aix5_auth.c` for AIX 5+, builds `aix_ktc.c` twice with or without `AFS_KERBEROS_ENV`, adds Kerberos 5 CPP flags for `aix_aklog.o`, and links dynamic auth modules with AIX TSM imports/libs. `dest` installs outputs into the client `usr/vice/etc` area.

## State And Persistence
Build artifacts are dynamic auth binaries and objects. Installed modules become persistent client authentication plugins consumed by AIX login/security infrastructure.

## Dependencies And Integration Points
The file integrates OpenAFS static libraries with AIX security method loader conventions and configured Kerberos/roken libraries. It is highly platform-specific to `rs_aix*` `SYS_NAME` values and AIX import/export behavior.

## Risks And Test Signals
Risks include stale AIX-only library names, conditional object selection that silently skips unsupported `SYS_NAME`, duplicate header/prototype quirks in the source set, and missing Kerberos 5 flags. Signals are AIX 4/AIX 5 build coverage, dynamic loader entry-point validation, install location checks, and login-method smoke tests using each generated module.
