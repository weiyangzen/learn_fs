# sources/distributed-fs/ceph-client/arch/sparc/lib/memcmp.S

Purpose: SPARC assembly `memcmp`.

Important APIs/functions: Exports `memcmp`.

Control flow: Loops byte-by-byte while length remains and bytes are equal. On mismatch, subtracts byte values and returns signed difference; on completion returns zero.

State and persistence: Pure read-only buffer comparison.

Dependencies/integration: Includes `linux/export.h`, `linux/linkage.h`, and `asm/asm.h`.

Risks/test signals: Return sign and zero-length behavior are main checks. Test equal buffers, first/last-byte mismatches, all byte values, and zero length.
