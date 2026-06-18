## sources/distributed-fs/openafs/src/libuafs/MakefileProto.FBSD.in

Purpose: Provides FreeBSD-specific settings for the common libuafs build.

Important variables: `CC=@CC@`, `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, empty `KOPTS`, `TEST_CFLAGS=-D_REENTRANT -DAFS_PTHREAD_ENV -DAFS_FBSD_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lpthread`.

Control flow: It includes base config, defines install tools, sets compiler/test flags, and delegates to `Makefile.common`.

State and persistence: Produces only the common libuafs artifacts.

Dependencies and integration: Selects FreeBSD conditionals in cache manager and UKERNEL sources through `AFS_FBSD_ENV`. The linktest inherits pthread linkage.

Risks: FreeBSD ABI and pthread flag expectations vary across releases; direct `-lpthread` may need to remain aligned with configure output. Kernel-style code compiled in userspace is sensitive to platform macro drift.

Test signals: FreeBSD libuafs build, `linktest`, optional Perl binding build, and source conditionals compiled under `AFS_FBSD_ENV`.
