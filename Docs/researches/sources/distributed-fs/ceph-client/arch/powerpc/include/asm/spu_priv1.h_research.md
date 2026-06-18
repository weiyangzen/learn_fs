<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_priv1.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_priv1.h

Purpose: Defines the privileged SPU register operation dispatch table.

Important APIs/types/functions: `struct spu_priv1_ops`, global `spu_priv1_ops`, and inline wrappers for interrupt mask/stat, MFC SR1, SPU run control, status, and TLB invalidation. Source-visible declarations include: #define _SPU_PRIV1_H; struct spu;; struct spu_context;; struct spu_priv1_ops {; extern const struct spu_priv1_ops* spu_priv1_ops;; static inline void; static inline void; static inline void.

Control flow: platform-specific backend operations are installed and generic SPU code invokes them through wrappers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: backend pointer persists globally; hardware state is in privileged SPU registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/types.h>. Integrated with native Cell, hypervisor/Beat SPU backends, and SPU interrupt/MMU control.

Risks: a missing backend or wrong op ordering breaks privileged SPU control and can lose interrupts. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 221 lines, 5077 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_priv1.h -->
