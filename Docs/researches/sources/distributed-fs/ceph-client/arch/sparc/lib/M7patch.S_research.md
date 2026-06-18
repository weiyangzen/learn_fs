# sources/distributed-fs/ceph-client/arch/sparc/lib/M7patch.S

Purpose: Runtime patcher for SPARC M7 copy, bzero/memset, and page operations.

Important APIs/functions: Defines `m7_patch_copyops`, `m7_patch_bzero`, and `m7_patch_pageops`, using a branch-and-nop patch macro.

Control flow: Each entry computes relative branch encodings from public/default routines to M7 implementations, overwrites old function entries, installs a `nop` delay slot, and flushes the instruction location.

State and persistence: Mutates kernel text permanently for the running boot session.

Dependencies/integration: Depends on M7 implementation symbols (`M7memcpy`, `M7copy_from_user`, `M7copy_to_user`, `M7bzero`, page-clear/copy routines) and CPU identification code that chooses M7 patching.

Risks/test signals: Wrong patch target or missing flush can break all memory operations. Test boot-time patch logs, symbol target disassembly, memcpy/copy-user/memset/page-clear correctness after patch, and fallback behavior on non-M7 CPUs.
