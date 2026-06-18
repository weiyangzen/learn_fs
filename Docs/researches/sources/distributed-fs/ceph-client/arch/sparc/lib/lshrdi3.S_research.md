# sources/distributed-fs/ceph-client/arch/sparc/lib/lshrdi3.S

Purpose: SPARC32 libgcc-compatible logical 64-bit right shift helper.

Important APIs/functions: Exports `__lshrdi3`.

Control flow: Handles shift counts below/above 32 bits without sign extension, combines high and low halves, and zero-fills vacated high bits.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Boundary counts and zero fill are key. Test values with high bit set and shift counts 0, 31, 32, and 63 against C unsigned shifts.
