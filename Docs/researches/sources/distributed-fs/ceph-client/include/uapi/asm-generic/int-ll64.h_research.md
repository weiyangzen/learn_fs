# sources/distributed-fs/ceph-client/include/uapi/asm-generic/int-ll64.h

Purpose: Defines fixed-width integer typedefs for architectures where 64-bit UAPI integer types use C `long long`.

Important APIs/types/functions: Typedefs `__s8/__u8`, `__s16/__u16`, `__s32/__u32`, and `__s64/__u64`; with GCC it uses `__extension__` for long long typedefs to avoid strict C90 warnings.

Control flow: Assembly inclusion skips typedefs. Non-GCC compilers receive plain long long typedefs through the alternate branch.

State/persistence: No runtime state; typedefs define exported ABI type spelling and layout.

Dependencies/integration: Includes `asm/bitsperlong.h`; used by many architectures and generic UAPI headers.

Risks: Mismatching int-l64 vs int-ll64 can break user-space ABI compatibility even when sizes are equal because type models differ.

Test signals: Headers compile tests under GCC and non-GCC-compatible modes; ABI layout checks for structs using `__u64`.
