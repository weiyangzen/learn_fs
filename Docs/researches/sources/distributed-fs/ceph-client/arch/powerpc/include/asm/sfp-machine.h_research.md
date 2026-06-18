<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sfp-machine.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sfp-machine.h

Purpose: Supplies PowerPC machine definitions for the kernel soft-float implementation.

Important APIs/types/functions: word type sizes, multiply/divide meat macros, NaN bit patterns, exception flag mapping, rounding helpers, and endian-specific fraction packing. Source-visible declarations include: #define _FP_W_TYPE_SIZE 32; #define _FP_W_TYPE unsigned int; #define _FP_WS_TYPE signed int; #define _FP_I_TYPE int; #define __ll_B ((UWtype) 1 << (W_TYPE_SIZE / 2)); #define __ll_lowpart(t) ((UWtype) (t) & (__ll_B - 1)); #define __ll_highpart(t) ((UWtype) (t) >> (W_TYPE_SIZE / 2)); #define _FP_MUL_MEAT_S(R,X,Y) _FP_MUL_MEAT_1_wide(_FP_WFRACBITS_S,R,X,Y,umul_ppmm).

Control flow: soft-float routines expand these macros to implement IEEE operations without hardware FP. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is per-operation FP fragments and exception flags, not persistent header data. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/kernel.h>, #include <linux/sched.h>, #include <linux/types.h>, #include <asm/byteorder.h>. Integrated with Linux soft-fp library, math emulation, and no-FPU kernel paths.

Risks: rounding, endian packing, and exception flag definitions are numerically sensitive and require cross-endian tests. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 343 lines, 12676 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/sfp-machine.h -->
