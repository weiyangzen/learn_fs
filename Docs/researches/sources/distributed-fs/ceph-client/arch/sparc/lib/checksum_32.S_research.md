# sources/distributed-fs/ceph-client/arch/sparc/lib/checksum_32.S

Purpose: SPARC32 Internet checksum and checksum-copy routines.

Important APIs/functions: Exports `csum_partial` and `__csum_partial_copy_sparc_generic`.

Control flow: `csum_partial` fixes alignment, processes large unrolled chunks, handles remaining table-sized chunks, folds carries, and consumes trailing bytes. The copy variant copies from source to destination while accumulating checksum, with exception fixups for faulting loads/stores.

State and persistence: No persistent state; mutates destination for copy variant and returns checksum/fault status.

Dependencies/integration: Includes `linux/export.h` and `asm/errno.h`; used by networking stack and copy-checksum helpers.

Risks/test signals: Carry folding, odd-byte alignment, endian behavior, and fault recovery are key. Test RFC-style checksum vectors, odd/even addresses, all tail lengths, and faulting copy paths.
