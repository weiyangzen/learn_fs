# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754.h

Purpose: public common header for the MIPS software FPU IEEE-754 emulator. It defines the raw single/double union layouts, operation prototypes, class and exception constants, compare masks, and access to the emulated FPU control/status register.

Important APIs/types: `union ieee754sp` and `union ieee754dp` expose sign, biased exponent, mantissa, and raw `bits`. The header declares arithmetic, conversion, compare, sqrt, fused multiply-add, min/max, class, abs, and neg APIs for both precisions. `struct _ieee754_csr` maps FCR31 fields such as rounding mode, exception cause/sticky/mask bits, `nan2008`, `abs2008`, and `nod`.

Control flow: inline helpers get/set rounding mode, current exceptions, and sticky exceptions. The macro `ieee754_csr` resolves to `current->thread.fpu.fcr31`, so all operations implicitly act on the current task's FPU state.

State and persistence: persistent state is per-task FPU control state. Helpers mutate exception cause/sticky bits and rounding mode but do not allocate memory or keep global state.

Dependencies and integration: includes Linux types, scheduler state, byte order, and MIPS bitfield helpers. It is consumed by `cp1emu.c` and all `sp_*`/`dp_*` emulator files.

Risks and test signals: because it maps a bitfield over FCR31, ABI bit ordering and endianness must be correct. Tests should validate exception masks, sticky flag accumulation, condition code fields, NaN-2008 toggles, and raw bit output for all public operations.
