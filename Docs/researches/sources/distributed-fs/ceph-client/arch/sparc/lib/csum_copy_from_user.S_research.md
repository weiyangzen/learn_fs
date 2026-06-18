# sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy_from_user.S

Purpose: SPARC64 checksum-and-copy-from-user wrapper.

Important APIs/functions: Defines `FUNC_NAME csum_and_copy_from_user` and ASI-based guarded `LOAD`, then includes `csum_copy.S`.

Control flow: User loads are wrapped in exception-table entries that return through a fault path; successful flow follows `csum_copy.S` alignment/chunk/tail checksum-copy logic.

State and persistence: Mutates kernel destination and returns checksum/fault indication; no persistent state.

Dependencies/integration: Depends on `csum_copy.S`, `asm/asi.h` behavior through included code, and networking/usercopy callers.

Risks/test signals: Faulting source pages must not produce misleading checksums. Test user faults at each alignment/tail position and compare successful checksums to software reference.
