# sources/distributed-fs/ceph-client/samples/Makefile

Purpose: connects sample Kconfig symbols to kbuild subdirectories and userspace sample build directories.

Important APIs/types/functions: uses `subdir-$(CONFIG_...)` for userspace sample directories and `obj-$(CONFIG_...)` for kernel modules/directories. Always includes `vfio-mdev` with `obj-y`, and conditionally includes Rust, DAMON, ftrace, trace, coresight, kmemleak, hung_task, and TSM samples.

Control flow: kbuild expands enabled `CONFIG_*` variables into directory traversal and object build lists.

State and persistence: no runtime state; build outputs persist under the kernel object tree.

Dependencies and integration: tightly coupled to `samples/Kconfig` symbol names and each child sample Makefile. Userspace samples rely on headers and host/user compiler flags supplied by kbuild.

Risks: missing or mismatched config names silently skip samples. `obj-y += vfio-mdev/` always traverses that directory, so its local Makefile must be robust even when related config is off. User program samples need `headers_install` and suitable toolchains.

Test signals: sample directory build under representative configs, `make samples`, allmodconfig builds, and clean target behavior.
