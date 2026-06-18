<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/byteorder.h

Purpose: selects UAPI byteorder definitions for little-endian or big-endian Xtensa. It includes `linux/byteorder/little_endian.h` when `__XTENSA_EL__` is defined, `linux/byteorder/big_endian.h` when `__XTENSA_EB__` is defined, and errors otherwise.

Control flow is preprocessor selection. State is not runtime state, but it defines ABI interpretation for multi-byte values in UAPI structs and ioctl payloads. Dependencies are compiler-provided Xtensa endian macros. Integration points include exported headers, SysV IPC struct time-field ordering, networking, filesystems, and userspace builds. Risks are toolchain macro mismatch or unsupported bi-endian build paths. Test signals include big/little endian builds, headers_install, userspace compile tests, and ABI layout checks for endian-sensitive structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/byteorder.h -->
