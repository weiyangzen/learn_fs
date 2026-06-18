# sources/distributed-fs/ceph-client/arch/x86/lib/hweight.S

Purpose: provides software Hamming-weight/popcount helpers for x86 when hardware popcount or inline implementations are not used.

Important APIs/functions: exports `__sw_hweight32` on all x86 and `__sw_hweight64` on x86-64.

Control flow: both functions implement classic parallel bit-count algorithms: subtract shifted pairs masked with `0x55...`, combine two-bit groups with `0x33...`, combine nibbles with `0x0f...`, multiply by `0x0101...`, and shift out the total count. Register saves protect temporary registers.

State and persistence behavior: pure register computation; no memory state except stack saves.

Dependencies/integration points: used by generic bit operations as fallback popcount helpers and exported for modules. Depends on Linux linkage/export macros and x86 register-size abstractions.

Risks: constants and shift widths must match operand size. Calling convention differences between 32-bit and 64-bit are handled explicitly; changing register use can break callers.

Test signals: bitops selftests comparing every small value and random 32/64-bit values, module link tests, and builds with hardware POPCNT disabled.
