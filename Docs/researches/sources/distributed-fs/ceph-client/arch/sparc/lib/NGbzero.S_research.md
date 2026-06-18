# sources/distributed-fs/ceph-client/arch/sparc/lib/NGbzero.S

Purpose: Niagara optimized memset, bzero, clear-user, and bzero patch support.

Important APIs/functions: Defines `NGmemset`, `NGbzero`, `NGclear_user`, and `niagara_patch_bzero`.

Control flow: `NGmemset` builds repeated byte patterns and jumps into `NGbzero` core paths. `NGbzero` handles zero length, leading bytes, medium xword stores, large block-init zeroing, and byte tails. `NGclear_user` sets `%asi` to `ASI_AIUS`, routes to the shared clear path, and uses exception-table guarded stores. The patcher redirects default bzero/memset routines to Niagara versions.

State and persistence: Memory writes only, except patcher text mutation. Clear-user temporarily changes `%asi`.

Dependencies/integration: Depends on `asm/asi.h`, exception-table fixups, and Niagara runtime patching.

Risks/test signals: User clear faults must return remaining bytes; patching must not break `memset`. Test user fault injection, zero/nonzero memset, page-sized bzero, and patched boot behavior.
