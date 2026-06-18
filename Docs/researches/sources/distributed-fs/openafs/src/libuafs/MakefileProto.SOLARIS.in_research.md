## sources/distributed-fs/openafs/src/libuafs/MakefileProto.SOLARIS.in

Purpose: Supplies Solaris-specific flags for libuafs.

Important variables: `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, `TEST_CFLAGS=-mt -DAFS_PTHREAD_ENV -Dsolaris -DAFS_SUN5_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lsocket -lnsl -lthread -lm -ldl`.

Control flow: Includes config and install substitutions, declares Solaris threading and networking flags, and delegates to `Makefile.common`.

State and persistence: Controls common build artifacts only.

Dependencies and integration: Selects Solaris 5 conditionals and links socket, nsl, thread, math, and dl libraries for linktest and related test binaries.

Risks: Uses legacy `-mt` and `-lthread` conventions; modern Solaris-like environments may prefer pthread defaults. Network library order matters on Solaris.

Test signals: Solaris libuafs build, linktest, source conditionals with `AFS_SUN5_ENV`, and install/dest packaging.
