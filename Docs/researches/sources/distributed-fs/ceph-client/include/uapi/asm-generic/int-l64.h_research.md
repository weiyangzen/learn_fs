# sources/distributed-fs/ceph-client/include/uapi/asm-generic/int-l64.h

Purpose: Defines fixed-width signed/unsigned integer typedefs for architectures where C `long` is the 64-bit type.

Important APIs/types/functions: Under non-assembly builds, typedefs `__s8/__u8`, `__s16/__u16`, `__s32/__u32`, and `__s64/__u64` with `__s64` as signed long and `__u64` as unsigned long.

Control flow: Preprocessor guard excludes typedefs for assembly and lets include guards prevent duplication.

State/persistence: No runtime state; typedefs influence UAPI struct layout.

Dependencies/integration: Includes `asm/bitsperlong.h`; used by architectures following the LP64 long-based UAPI model.

Risks: Selecting this header for an architecture whose ABI uses long long for 64-bit UAPI types would alter type compatibility and layout.

Test signals: Compile installed headers and verify `sizeof(__u64)` and struct layouts on LP64 targets.
