# sources/distributed-fs/ceph-client/arch/xtensa/lib/lshrdi3.S

Purpose: Implements exported 64-bit logical right shift helper `__lshrdi3`.

Important APIs, types, and functions: `__lshrdi3`, endian-dependent high/low aliases, `ssr`, `src`, `srl`, ABI macros, and `EXPORT_SYMBOL`.

Control flow: For counts below 32, combines high and low words with a logical shift. For counts of 32 or more, shifts the high word into the low result and zeros the high result.

State and persistence: Register-only helper.

Dependencies and integration: Supports compiler-emitted unsigned 64-bit right shifts in kernel and modules.

Risks: Edge counts around 32 and endian word mapping are the meaningful hazards.

Test signals: Unsigned 64-bit right shift tests at counts 0, 1, 31, 32, 33, 63 with high bits set.
