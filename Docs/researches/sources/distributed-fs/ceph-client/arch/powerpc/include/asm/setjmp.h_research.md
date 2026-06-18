<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setjmp.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setjmp.h

Purpose: Declares the minimal PowerPC kernel setjmp/longjmp ABI.

Important APIs/types/functions: `JMP_BUF_LEN`, `jmp_buf`, `setjmp()`, and `longjmp()`. Source-visible declarations include: #define _ASM_POWERPC_SETJMP_H; #define JMP_BUF_LEN 23; typedef long jmp_buf[JMP_BUF_LEN];; extern int setjmp(jmp_buf env) __attribute__((returns_twice));; extern void longjmp(jmp_buf env, int val) __attribute__((noreturn));.

Control flow: low-level code snapshots nonlocal control-flow state and later restores it through assembly helpers. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: jump buffers persist in caller-provided storage. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with xmon/debug and low-level recovery paths.

Risks: buffer length and saved register convention must match assembly or longjmp corrupts execution state. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 15 lines, 400 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/setjmp.h -->
