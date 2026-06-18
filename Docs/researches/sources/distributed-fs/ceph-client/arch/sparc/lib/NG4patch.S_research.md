# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4patch.S

Purpose: Runtime patcher for Niagara4 copy, bzero, page, and `fls` operations.

Important APIs/functions: Defines `niagara4_patch_copyops`, `niagara4_patch_bzero`, `niagara4_patch_pageops`, and `niagara4_patch_fls`.

Control flow: Writes branch-and-nop stubs into generic/public routine entries so they jump to NG4-specific implementations, then flushes patched instruction locations.

State and persistence: Mutates executable kernel text for the running system.

Dependencies/integration: Depends on NG4 implementation symbols and CPU feature selection. Uses SPARC branch encodings and `flush`.

Risks/test signals: Patching a wrong symbol affects core memory and bit operations. Verify patched disassembly, run copy/memset/page/fls tests after patch, and confirm non-NG4 systems do not call this path.
