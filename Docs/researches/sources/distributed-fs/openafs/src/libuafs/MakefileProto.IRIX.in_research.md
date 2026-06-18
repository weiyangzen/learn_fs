## sources/distributed-fs/openafs/src/libuafs/MakefileProto.IRIX.in

Purpose: Provides IRIX-specific compiler and test-link flags for libuafs.

Important variables: `CC=cc`, `DEFINES=-D_SGI_MP_SOURCE -DKERNEL -DUKERNEL`, `TEST_CFLAGS=-D_SGI_MP_SOURCE -DAFS_PTHREAD_ENV -Dirix -DAFS_SGI_ENV $(XCFLAGS)`, `TEST_LDFLAGS=-ignore_minor`, and `TEST_LIBS=-lpthread -lm`.

Control flow: Standard prototype structure: include config, set install tools, define platform flags, include `Makefile.common`.

State and persistence: Controls common build outputs only.

Dependencies and integration: Selects SGI multiprocess and OpenAFS SGI conditionals. Linktest depends on pthread and math libraries plus IRIX linker behavior.

Risks: IRIX-specific flags are legacy and hard-coded. `-ignore_minor` can hide library version mismatches that should be visible in modern diagnostics.

Test signals: IRIX compile/link, linktest, source paths conditioned by `AFS_SGI_ENV`, and clean/install behavior.
