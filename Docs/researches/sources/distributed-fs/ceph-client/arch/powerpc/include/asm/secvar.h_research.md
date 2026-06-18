<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secvar.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secvar.h

Purpose: Defines the secure-variable backend operations used by PowerPC secure boot platforms.

Important APIs/types/functions: `struct secvar_operations`, global `secvar_ops`, and optional `set_secvar_ops()` registration. Source-visible declarations include: #define SECVAR_OPS_H; extern const struct secvar_operations *secvar_ops;; struct secvar_operations {; static inline int set_secvar_ops(const struct secvar_operations *ops) { return 0; }.

Control flow: a platform backend registers get/set/format/sysfs callbacks that higher-level secure variable code invokes. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: backend pointer and firmware variables persist globally once registered. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/errno.h>, #include <linux/sysfs.h>. Integrated with OPAL/pSeries secure-variable backends, sysfs, and secure boot policy code.

Risks: backend registration must be one-time and callbacks must validate firmware buffer sizes and permissions. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 39 lines, 954 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/secvar.h -->
