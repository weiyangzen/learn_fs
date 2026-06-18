## sources/distributed-fs/openafs/src/libuafs/MakefileProto.AIX.in

Purpose: Supplies AIX-specific compiler, archive, and test-link settings before including `Makefile.common`.

Important variables: `DEFINES=-DKERNEL -DUKERNEL`, `AR=/usr/bin/ar`, `ARFLAGS=-r`, `RANLIB=/bin/ranlib`, `CC=$(MT_CC)`, `DEF_LIBPATH`, `TEST_CFLAGS`, `TEST_LDFLAGS`, `TEST_LIBS`, and `AFS_OS_CLEAN`.

Control flow: The file includes generated OpenAFS make configuration, sets install tool substitutions, declares AIX flags, and delegates all real targets to `Makefile.common`.

State and persistence: Controls generated build outputs only. AIX-specific clean removes export files such as `*.exp` and `export.h`.

Dependencies and integration: Integrates with threaded AIX compiler settings and pthread libraries. It relies on the common file for all object compilation, linktest, install, and dest logic.

Risks: Hard-coded tool paths and `DEF_LIBPATH` can become stale on newer AIX installations. The test link uses `-lpthreads`, which is platform-specific and can differ from modern pthread naming.

Test signals: AIX build of `libuafs.a`, `libuafs_pic.a`, and `linktest`; clean removes AIX export artifacts; install/dest match common expectations.
