# sources/distributed-fs/ceph-client/arch/sparc/lib/M7memset.S

Purpose: SPARC M7 optimized memset, bzero, and page-clear implementation.

Important APIs/functions: Defines `M7clear_page`, `M7clear_user_page`, `M7bzero`, and `M7memset`. Uses `asm/asi.h` and `asm/page.h`.

Control flow: Page clear loops use block-init/MRU store ASIs for full-page zeroing. `M7memset` expands the byte pattern across registers, handles leading/trailing unaligned bytes, then writes larger aligned chunks using optimized stores. `M7bzero` routes zero-fill calls through the same core logic.

State and persistence: No persistent state; modifies target memory only and uses temporary registers/ASI stores.

Dependencies/integration: Built for `CONFIG_SPARC64` and selected by `m7_patch_bzero` and `m7_patch_pageops`.

Risks/test signals: Pattern replication, tail handling, and M7 block-init semantics are the main risks. Test all small lengths, page-size clears, unaligned addresses, nonzero patterns, and CPU patch replacement of generic bzero/page clear paths.
