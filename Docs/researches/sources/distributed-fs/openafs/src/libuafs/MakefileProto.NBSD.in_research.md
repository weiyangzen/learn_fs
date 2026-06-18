## sources/distributed-fs/openafs/src/libuafs/MakefileProto.NBSD.in

Purpose: Provides NetBSD-specific settings for libuafs.

Important variables: `CC=gcc`, `DEFINES=-DKERNEL -DUKERNEL`, empty `KOPTS`, `TEST_CFLAGS=-DAFS_NBSD_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and empty `TEST_LIBS`.

Control flow: Includes config and install substitutions, defines the minimal NetBSD platform flags, then includes `Makefile.common`.

State and persistence: Only affects common build outputs.

Dependencies and integration: Selects NetBSD conditionals in userspace AFS code. Unlike several other BSD protos, it does not define `AFS_PTHREAD_ENV` or link pthreads here.

Risks: Lack of explicit pthread flags is notable because common code and linktest may depend on threading depending on configuration. Hard-coded `gcc` ignores `@CC@`, which can limit modern toolchain selection.

Test signals: NetBSD build and linktest, no-pthread configuration coverage, and compatibility with configured compiler expectations.
