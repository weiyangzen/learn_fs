# sources/distributed-fs/ceph-client/arch/sparc/lib/checksum_64.S

Purpose: SPARC64 Internet checksum implementation.

Important APIs/functions: Exports `csum_partial`.

Control flow: Aligns the buffer, accumulates 32-bit words using SPARC carry chains, processes unrolled chunks, handles end cruft bytes/halfwords, folds carries, and returns the partial checksum.

State and persistence: Pure read-only checksum computation; no persistent state.

Dependencies/integration: Includes `linux/export.h`; used by networking checksum paths on SPARC64.

Risks/test signals: Odd alignment and carry folding errors break network checksums. Test known checksum vectors, all start alignments, small tails, and large buffers.
