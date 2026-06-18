# sources/distributed-fs/ceph-client/arch/xtensa/lib/ashrdi3.S

Purpose: Implements exported 64-bit arithmetic right shift helper `__ashrdi3`.

Important APIs, types, and functions: `__ashrdi3`, endian-dependent `uh/ul`, `ssr`, `src`, `sra`, `srai`, ABI macros, and `EXPORT_SYMBOL`.

Control flow: For counts below 32, shifts the high word arithmetically and combines high/low with `src`. For counts at least 32, shifts the high word into the low result and sign-fills the high result.

State and persistence: Register-only arithmetic helper.

Dependencies and integration: Provides libgcc-compatible helper behavior for signed 64-bit right shifts emitted by the compiler and used by modules.

Risks: Sign extension and endian high/low mapping are critical; C semantics for large shift counts depend on compiler lowering assumptions.

Test signals: Signed 64-bit shift tests for positive and negative values across counts around 31/32 and endian variants.
