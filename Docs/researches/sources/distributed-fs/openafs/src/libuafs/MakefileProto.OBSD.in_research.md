## sources/distributed-fs/openafs/src/libuafs/MakefileProto.OBSD.in

Purpose: Provides OpenBSD-specific settings for libuafs.

Important variables: `CC=gcc`, `DEFINES=-DKERNEL -DUKERNEL`, empty `KOPTS`, `TEST_CFLAGS=-DAFS_OBSD_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and empty `TEST_LIBS`.

Control flow: Standard platform proto: include generated config, define install tools and OS flags, include `Makefile.common`.

State and persistence: Controls common build artifacts only.

Dependencies and integration: Selects OpenBSD source conditionals through `AFS_OBSD_ENV`. Does not explicitly opt into pthread environment.

Risks: Hard-coded `gcc` and no pthread flags may not match current OpenBSD compiler/linker defaults. Because common rules compile kernel-style sources in userspace, missing reentrancy flags could expose platform-specific build failures.

Test signals: OpenBSD build, linktest, optional Perl binding if supported, and source conditionals selected by `AFS_OBSD_ENV`.
