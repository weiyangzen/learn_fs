## sources/distributed-fs/openafs/src/libuafs/MakefileProto.DFBSD.in

Purpose: Provides DragonFly BSD-specific settings for libuafs.

Important variables: `CC=@CC@`, `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, empty `KOPTS`, `TEST_CFLAGS=-D_REENTRANT -DAFS_PTHREAD_ENV -DAFS_DFFBSD_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lpthread`.

Control flow: After configuration and install substitutions, the file declares platform flags and includes `Makefile.common`.

State and persistence: Only influences common build outputs. No runtime state.

Dependencies and integration: Integrates with DragonFly pthread and OpenAFS environment macros. The `<all>` marker is part of OpenAFS's makefile prototype filtering system.

Risks: The environment macro spelling `AFS_DFFBSD_ENV` is easy to confuse with other BSD variants and must match source conditionals. The direct `-lpthread` dependency assumes system naming.

Test signals: DragonFly build, linktest, conditional compilation paths selected by `AFS_DFFBSD_ENV`, and prototype preprocessing around `<all>`.
