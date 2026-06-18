## sources/distributed-fs/openafs/src/libuafs/Makefile.common.in

Purpose: Common make logic for building the userspace AFS client library `libuafs`, a PIC archive, a link smoke-test, and optional SWIG Perl bindings.

Important targets and variables: `MODULE_CFLAGS`, `LT_objs`, `MODULE_INCLUDE`, source directory variables, `all`, `libuafs.a`, `libuafs_pic.la`, `linktest`, `LIBUAFS_BUILD_PERL`, `PERLUAFS/ukernel.*`, `clean`, `install`, `dest`, and `h`. `LT_objs` aggregates AFS cache manager, vnode operation, RX, rxkad, auth, rxstat, generated XDR/RPC, utility, and UKERNEL support objects.

Control flow: Platform `MakefileProto.*` files define compiler and OS flags, then include this file. The `h` target generates a fake `h/` include tree before object compilation. Each `.lo` rule compiles a source file from its original subsystem into the libuafs object set. `linktest` links a small program against `libuafs.a` and required support libraries. Optional Perl bindings run SWIG on `ukernel_swig.i`, compile the wrapper with Perl embed flags, and link it with `libuafs_pic.a`.

State and persistence: Produces archives, generated `h/`, `PERLUAFS/`, `AFS_component_version_number.c`, linktest, and installed libraries/bindings. No runtime persistence.

Dependencies and integration: Bridges kernel-oriented AFS cache manager code into userspace by compiling with `-DKERNEL -DUKERNEL` and UKERNEL headers. It depends on generated fsint, vlserver, auth, and rxstat files in the object tree.

Risks: This file is build-system critical and highly coupled to source layout. The fake header tree is an intentional workaround and can mask include hygiene problems. SWIG/Perl embedding is optional but sensitive to platform flags. The object list must track subsystem changes manually.

Test signals: Full libuafs builds on each platform proto, `linktest`, Perl binding build when enabled, install/dest contents, clean idempotence, and rebuild after generated RPC files change.
