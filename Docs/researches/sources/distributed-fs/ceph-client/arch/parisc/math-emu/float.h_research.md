# sources/distributed-fs/ceph-client/arch/parisc/math-emu/float.h

Purpose: defines the core PA-RISC floating-point emulation data model: raw bit fields for single, double, quad, extended mantissas, fixed-point helper types, format constants, status register bits, exception encodings, condition fields, and operation codes.

Important APIs/types/functions: single macros (`Ssign`, `Sexponent`, `Smantissa`), double macros (`Dsign`, `Dexponent`, `Dmantissap1/2`), deposit/test variants, `sgl_floating_point`, `dbl_floating_point`, `dbl_integer`, `dbl_unsigned`, rounding mode constants, exception masks, `Fpustatus_register` helpers, and operation encodings such as `FADD`, `FDIV`, `FCNVFX`, and `FCMP`.

Control flow: there are no functions. Other files include this header to inspect and mutate raw 32-bit words and status bits. Status macros assume a local variable or pointer named `status` and map `Fpustatus_register` to `*status` unless a file overrides it.

State and dependencies: no storage, but macros mutate caller lvalues and `*status`. Depends on `fpbits.h`, `hppa.h`, and `fpu.h` with `LOCORE` set to get FPU capability flags without C PDC structures.

Risks: this header is the central contract; any bit-position error breaks the emulator globally. Macros are not type-safe and often rely on caller naming conventions. Quad support is skeletal. Status/trap bit encodings must match PA-RISC architecture and Linux signal translation.

Test signals: build coverage of every math-emu file, bitfield extraction/deposit unit tests, status flag/trap enable tests, operation decoder tests, and cross-checks against hardware FPU behavior for representative classes.
