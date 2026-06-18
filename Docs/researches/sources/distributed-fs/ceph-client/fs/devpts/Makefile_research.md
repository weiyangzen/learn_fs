<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/devpts/Makefile -->
# sources/distributed-fs/ceph-client/fs/devpts/Makefile

Purpose: builds the `/dev/pts` virtual filesystem implementation when Unix98 PTYs are enabled.

Important APIs/types/functions: Kbuild variables `obj-$(CONFIG_UNIX98_PTYS) += devpts.o` and `devpts-$(CONFIG_UNIX98_PTYS) := inode.o`.

Control flow: if `CONFIG_UNIX98_PTYS` is set, Kbuild compiles `inode.o` into `devpts.o` and links that object into the kernel build.

State and persistence: no runtime state; it controls availability of the devpts filesystem and PTY slave node management code.

Dependencies and integration: tied to the kernel PTY subsystem and the `CONFIG_UNIX98_PTYS` option.

Risks: build omissions break Unix98 PTY support. Additional devpts source files would need explicit inclusion here.

Test signals: kernel builds with Unix98 PTYs enabled should include devpts registration and allow mounting `devpts`; disabled builds should omit it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/devpts/Makefile -->
