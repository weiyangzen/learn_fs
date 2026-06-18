# sources/distributed-fs/ceph-client/arch/sparc/lib/fls.S

Purpose: SPARC64 find-last-set for 32-bit values.

Important APIs/functions: Exports `fls`.

Control flow: Tests progressively smaller bit ranges to determine the highest set bit and returns a one-based bit position, or zero for input zero.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; may be patched to `NG4fls` on Niagara4.

Risks/test signals: Off-by-one around high bit and zero input are primary. Test all powers of two, zero, and random values against generic `fls`.
