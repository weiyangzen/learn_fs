# sources/distributed-fs/ceph-client/arch/sh/math-emu/math.c

Purpose: emulates SH floating-point instructions in software for systems without hardware FPU support or when FPU traps are routed to emulation.

Important APIs and functions: exported-to-arch `do_fpu_inst`, internal `fpu_emulate`, `fpu_init`, instruction decoders `id_fnmx`, `id_fnxd`, `id_fxfd`, `id_sys`, arithmetic operations (`fadd`, `fsub`, `fmul`, `fdiv`, `fmac`), moves (`fmov_*`), conversions (`ffloat`, `ftrc`, `fcnvsd`, `fcnvds`), and FPSCR operations.

Control flow: `do_fpu_inst` records a perf emulation fault, initializes per-thread soft-FPU state on first use, then decodes the 16-bit instruction. `0xf000` forms dispatch through floating arithmetic/move tables; system forms move FPSCR/FPUL to and from registers or memory. Soft-fp macros unpack, operate, and repack single/double values according to FPSCR precision and register banking.

State and persistence: mutates current task `thread.xstate->softfpu`, `TS_USEDFPU`, FPUL/FPSCR, FPU register arrays, general registers for load/store addressing, and user memory for FPU memory operations.

Dependencies and integration: invoked from `traps_32.c` reserved/illegal-slot handlers, depends on Linux soft-fp headers, `sfp-util.h`, uaccess helpers, and SH thread/FPU structures.

Risks: several advanced operations are placeholders that print "not yet done" but return success, which can hide unsupported instruction behavior. Memory helpers return `-EFAULT`; callers must convert that correctly to trap/signal flow. Endian/register-bank handling is subtle for double-precision and extended registers.

Test signals: floating-point instruction suites on no-FPU SH, signal behavior for bad memory operands, perf emulation counters, and comparisons against hardware-FPU results.
