# sources/distributed-fs/ceph-client/arch/arm64/lib/tishift.S

Purpose: supplies compiler helper routines for 128-bit integer shifts on ARM64.

Important APIs/types/functions: `__ashlti3`, `__ashrti3`, `__lshrti3`, each exported for left shift, arithmetic right shift, and logical right shift of a two-register 128-bit value.

Control flow: each routine handles shift count zero directly. For counts below 64, it shifts low/high halves and transfers cross-boundary bits. For counts >=64, it moves the remaining high/low half into position and fills the other half with zero or sign bits for arithmetic right shift.

State and persistence: pure register computation. No memory or persistent state.

Dependencies/integration: used by compiler-generated code when 128-bit shifts are emitted; depends on AAPCS register return conventions.

Risks: shift counts outside compiler-expected ranges could produce undefined helper behavior. Arithmetic right shift must preserve sign extension exactly.

Test signals: compiler runtime tests for `__int128` shifts, counts 0, 1, 63, 64, 65, 127, signed negative values for `__ashrti3`, and comparison with compiler/emulator reference results.
