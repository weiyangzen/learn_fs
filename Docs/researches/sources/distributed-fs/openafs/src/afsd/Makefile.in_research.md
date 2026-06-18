# sources/distributed-fs/openafs/src/afsd/Makefile.in

Purpose: automake-style template for building and installing OpenAFS client daemons/utilities: kernel `afsd`, optional FUSE `afsd.fuse`, and `vsys`.

Important APIs/targets: includes `Makefile.config`, `Makefile.pthread`, and `Makefile.version`. Targets include `all`, `afsd`, `afsd.fuse`, `vsys`, object rules, `clean`, `install`, `dest`, and `system`. Library groups are `AFSLIBS`, `UAFSLIBS`, `FUSE_LIBS`, `AFSD_LIBS`, crypto/roken/thread libs, and AIX-only `AFSD_KERNEL_LDFLAGS`.

Control flow: `all` builds `afsd`, `vsys`, and optionally FUSE. `afsd` links `afsd.o` and `afsd_kernel.o` statically with auth/cmd/sys/util/opr libraries. `afsd.fuse` compiles with UKERNEL and FUSE flags and links `libuafs.a`. `install` writes binaries to `${sbindir}`; `dest` writes legacy client tree paths and OS-specific rc scripts/configs based on `${SYS_NAME}`.

State and persistence: build output includes binaries and objects; install/dest persist daemons, `vsys`, and platform startup scripts into package/image directories.

Dependencies and integration points: ties user-space daemon build to libafs syscall export on AIX, UKERNEL/libuafs for FUSE, and platform rc script inventory in `src/afsd`. The daemon configures the cache manager whose kernel code is represented by the `afs` source files in this group.

Risks: platform case patterns must match configured `SYS_NAME`; missing rc script paths break packaging. Static link library order matters. FUSE build depends on substituted `@ENABLE_FUSE_CLIENT@`, `@FUSE_CFLAGS@`, and `@FUSE_LIBS@`. AIX needs `afsl.exp` import for syscall linkage.

Test signals: build default, FUSE-enabled, and AIX variants; run `make install DESTDIR=...` and `make dest DEST=...` staging checks; verify clean removes generated binary/object/version files; check OS rc script selection for Linux, Darwin, FreeBSD, Solaris, HPUX, AIX, and SGI names.
