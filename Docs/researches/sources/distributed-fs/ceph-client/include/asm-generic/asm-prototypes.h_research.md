# sources/distributed-fs/ceph-client/include/asm-generic/asm-prototypes.h

Purpose: Declares generic C prototypes for memory routines that may be called from assembly or compiler-generated code, avoiding macro substitutions.

Important APIs, types, and functions: Undefines and declares `__memset`, `__memcpy`, `__memmove`, `memset`, `memcpy`, and `memmove` with `__kernel_size_t` sizes.

Control flow: No runtime logic; this is a declaration header.

State and persistence: No state.

Dependencies and integration points: Includes `linux/bitops.h` for type/dependency setup. Integrates with architecture assembly, lib/string implementations, and symbol export/CFI handling.

Risks and test signals: Risks include prototype mismatch with actual implementations, macro leakage, and calling-convention mismatch from assembly. Test builds with LTO/CFI, all architectures using generic prototypes, and string routine symbol resolution.
