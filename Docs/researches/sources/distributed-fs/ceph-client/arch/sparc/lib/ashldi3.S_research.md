# sources/distributed-fs/ceph-client/arch/sparc/lib/ashldi3.S

Purpose: SPARC32 libgcc-compatible 64-bit arithmetic left shift helper.

Important APIs/functions: Exports `__ashldi3`.

Control flow: Takes a 64-bit value split across registers and a shift count. It handles count ranges below/above 32 bits, shifts high/low halves accordingly, clears vacated low bits, and returns the shifted 64-bit result.

State and persistence: Pure register computation; no memory state.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; built for `CONFIG_SPARC32` when compiler-generated 64-bit shifts need helper routines.

Risks/test signals: Boundary counts 0, 31, 32, and 63 are risky. Test compiler helper calls and compare against C 64-bit shifts.
