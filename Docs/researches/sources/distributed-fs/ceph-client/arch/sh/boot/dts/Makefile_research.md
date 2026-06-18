# sources/distributed-fs/ceph-client/arch/sh/boot/dts/Makefile



Source read size: 2 lines, 117 bytes.



Purpose: Kbuild hook for built-in SH device-tree blobs.

Important APIs/types/functions: `obj-$(CONFIG_BUILTIN_DTB)` adds `$(CONFIG_BUILTIN_DTB_NAME).dtb.o` to the boot build.

Control flow: when built-in DTB support is enabled, Kbuild converts the named DTB into an object and links it into the kernel image.

State and persistence: generated DTB object becomes immutable boot-time firmware data embedded in the image.

Dependencies and integration points: depends on `CONFIG_BUILTIN_DTB` and `CONFIG_BUILTIN_DTB_NAME`, DTS build rules, and SH DT boot support.

Risks and test signals: an incorrect name silently selects the wrong or missing DTB object. Test built-in DTB boot and compare `/proc/device-tree/model` with the expected board.
