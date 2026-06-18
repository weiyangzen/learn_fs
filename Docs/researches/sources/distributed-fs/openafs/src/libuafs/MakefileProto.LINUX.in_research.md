## sources/distributed-fs/openafs/src/libuafs/MakefileProto.LINUX.in

Purpose: Defines Linux settings for libuafs builds.

Important variables: `DEFINES=-D_REENTRANT -DKERNEL -DUKERNEL`, empty `KOPTS`, `SYS_NAME=@AFS_SYSNAME@`, conditional `UAFS_CFLAGS=-fPIC` for `ppc64_linux26`, `TEST_CFLAGS=-pthread -D_REENTRANT -DAFS_PTHREAD_ENV -DAFS_LINUX_ENV $(XCFLAGS)`, empty `TEST_LDFLAGS`, and `TEST_LIBS=-lpthread @LIB_crypt@`.

Control flow: Includes generated config and install substitutions, applies Linux flags, then includes `Makefile.common`.

State and persistence: Controls generation of libuafs archives, linktest, and optional Perl bindings.

Dependencies and integration: Selects Linux-specific UKERNEL and cache manager conditionals and links pthread plus configure-selected crypt library.

Risks: The ppc64 PIC special case is narrow and may not cover all architectures requiring PIC. `-pthread` and `-lpthread` are both present through flags/libs, which is common but should be checked against toolchain behavior.

Test signals: Linux builds across x86, amd64, ppc64, and other supported sysnames; linktest; optional Perl binding; crypt dependency presence; and PIC archive link checks.
