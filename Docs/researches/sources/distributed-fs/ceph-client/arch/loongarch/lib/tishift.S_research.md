# sources/distributed-fs/ceph-client/arch/loongarch/lib/tishift.S

Purpose: supplies compiler runtime helpers for 128-bit integer shifts on LoongArch.

Important APIs, types, and functions: exported `__ashlti3`, `__ashrti3`, and `__lshrti3` implement arithmetic left, arithmetic right, and logical right shifts for TImode values split across two registers.

Control flow: each helper combines shifts from high and low 64-bit halves, uses mask instructions to select paths for shift counts with bit 64 set, and returns shifted low/high halves in ABI return registers.

State and persistence: no state.

Dependencies and integration points: referenced by compiler-generated code when `CONFIG_ARCH_SUPPORTS_INT128` is enabled and exported for modules.

Risks: boundary shifts around 0, 63, 64, and 127 are the critical cases. ABI register ordering must match compiler expectations.

Test signals: compiler runtime tests for `__int128` shifts, module link tests, and randomized comparison against C reference shifts.
