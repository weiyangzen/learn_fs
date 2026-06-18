# sources/distributed-fs/ceph-client/tools/include/uapi/linux/const.h

Purpose: provides constant-construction and alignment macros that work in both C and assembler UAPI contexts. It prevents C suffixes/casts from leaking into assembly while still giving C code typed constants.

Important APIs/types: macros include `_AC`, `_AT`, `_UL`, `_ULL`, `_BITUL`, `_BITULL`, optional `_BIT128`, `__ALIGN_KERNEL`, `__ALIGN_KERNEL_MASK`, and `__KERNEL_DIV_ROUND_UP`. There are no structs or functions.

Control flow, state, and persistence: all behavior is preprocessor-time. The header branches on `__ASSEMBLY__`; C builds concatenate suffixes and cast expressions, while assembler builds leave constants unannotated. No runtime or persistent state is defined.

Dependencies and integration points: widely included by UAPI headers that need bit masks, alignment, or typed constants, such as `kvm.h`. It interacts with compiler support for `typeof` and `unsigned __int128` in C-only paths.

Risks and test signals: macro changes can break assembly preprocessing, constant width, or ABI bit positions. `_BIT128` is explicitly C-only and can fail if used in assembler-facing macros. Tests should preprocess representative C and assembly users, validate generated constants on 32-bit and 64-bit builds, and check alignment/division macros for side effects and overflow-prone inputs.
