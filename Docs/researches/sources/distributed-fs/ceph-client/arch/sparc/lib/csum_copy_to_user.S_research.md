# sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy_to_user.S

Purpose: SPARC64 checksum-and-copy-to-user wrapper.

Important APIs/functions: Defines `FUNC_NAME csum_and_copy_to_user` and ASI-based guarded `STORE`, then includes `csum_copy.S`.

Control flow: Reads kernel source, computes checksum while storing to user memory. Store faults are exception-table routed; successful copies follow the shared checksum-copy loops.

State and persistence: Mutates user destination and returns checksum/fault status.

Dependencies/integration: Depends on `csum_copy.S`, user ASI store semantics, and networking send/copy paths.

Risks/test signals: Partial user destination faults must not hide incomplete copies. Test protected destinations, odd alignments, all tail lengths, and checksum reference comparisons.
