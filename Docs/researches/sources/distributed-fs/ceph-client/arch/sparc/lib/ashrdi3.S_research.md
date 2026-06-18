# sources/distributed-fs/ceph-client/arch/sparc/lib/ashrdi3.S

Purpose: SPARC32 libgcc-compatible signed 64-bit arithmetic right shift helper.

Important APIs/functions: Exports `__ashrdi3`.

Control flow: Handles shift counts below and above 32 bits while preserving sign extension from the high half. Uses arithmetic shifts for signed high-half propagation and combines shifted halves into the 64-bit result.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Sign extension and count boundaries are key. Test negative and positive 64-bit values with counts 0, 1, 31, 32, and 63 against C arithmetic shifts.
