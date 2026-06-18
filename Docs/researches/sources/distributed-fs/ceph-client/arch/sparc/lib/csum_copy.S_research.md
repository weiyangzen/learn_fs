# sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy.S

Purpose: SPARC64 checksum-and-copy engine used directly and as a template for user checksum copies.

Important APIs/functions: Emits `csum_partial_copy_nocheck` by default; wrapper files override `FUNC_NAME`, `LOAD`, and `STORE`.

Control flow: Aligns source, copies words to destination while accumulating checksum with carry handling, processes unrolled chunks, handles tail bytes, folds final checksum, and has fault handling controlled by macro wrappers.

State and persistence: Mutates destination buffer and returns checksum; no persistent state.

Dependencies/integration: Includes `linux/export.h`; included by `csum_copy_from_user.S` and `csum_copy_to_user.S`.

Risks/test signals: Must preserve checksum correctness while copying and handling faults. Test known checksum vectors, odd alignments, all tail sizes, and user wrappers with fault injection.
