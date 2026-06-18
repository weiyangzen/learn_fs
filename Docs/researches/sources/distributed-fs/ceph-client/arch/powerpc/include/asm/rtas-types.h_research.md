<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-types.h

Purpose: Defines the packed firmware data structures shared by RTAS core code, pSeries firmware calls, error logging, and hotplug/event handling.

Important APIs/types/functions: `rtas_arg_t`, `struct rtas_args`, `struct rtas_t`, `struct rtas_error_log`, `struct rtas_ext_event_log_v6`, `struct pseries_errorlog`, and hotplug log payload unions. Source-visible declarations include: #define _ASM_POWERPC_RTAS_TYPES_H; typedef __be32 rtas_arg_t;; struct rtas_args {; struct rtas_t {; struct device_node *dev; /* virtual address pointer */; struct rtas_error_log {; struct rtas_ext_event_log_v6 {; struct pseries_errorlog {.

Control flow: RTAS callers fill big-endian argument buffers and firmware writes status or event data into these structures. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: serializes persistent firmware state and platform event records crossing the OS/firmware boundary. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compiler_attributes.h>. Integrated with PAPR RTAS firmware, pSeries error logging, event scan, hotplug, and sys_rtas paths.

Risks: all structure sizes, endian annotations, and packed layouts are ABI-sensitive firmware contracts. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 114 lines, 2910 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-types.h -->
