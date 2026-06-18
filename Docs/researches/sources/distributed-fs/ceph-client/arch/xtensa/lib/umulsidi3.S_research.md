# sources/distributed-fs/ceph-client/arch/xtensa/lib/umulsidi3.S

Purpose: Implements exported unsigned 32x32-to-64 multiply helper `__umulsidi3`.

Important APIs, types, and functions: `__umulsidi3`, endian-dependent high/low return words, `mull/muluh` fast path, MUL16/MUL32/MAC16 partial-product paths, no-multiply helper `.Lmul_mulsi3`, CALL0 and windowed ABI save/restore, and `EXPORT_SYMBOL`.

Control flow: With `MUL32_HIGH`, computes low and high directly. Otherwise splits inputs into 16-bit halves, computes partial products, accumulates carries, and returns 64-bit product. On cores without multiply hardware, calls an internal nibble-at-a-time helper with ABI-specific calling conventions.

State and persistence: Register and stack save/restore only; no global state.

Dependencies and integration: Compiler-generated widening multiplication, floating-point/helper code, core feature macros, and ABI conventions.

Risks: Carry propagation and ABI register preservation are complex; no-multiply CALL0 path is not a normal leaf and uses custom helper conventions; endian return ordering must be correct.

Test signals: Widening multiply tests for high/low halves, overflow products, zero/max operands, CALL0/windowed builds, and cores with each multiply feature combination.
