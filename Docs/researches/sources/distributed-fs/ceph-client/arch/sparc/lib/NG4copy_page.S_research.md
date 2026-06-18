# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_page.S

Purpose: Niagara4 optimized page copy routine.

Important APIs/functions: Defines `NG4copy_user_page(dest, src, vaddr)`.

Control flow: Copies one page using NG4-friendly block load/store sequencing and prefetching. It loops over `PAGE_SIZE`, moving cacheline-size chunks from source to destination.

State and persistence: No persistent state; mutates destination page only.

Dependencies/integration: Includes `asm/asi.h` and `asm/page.h`; installed by `niagara4_patch_pageops`.

Risks/test signals: Page copy must preserve all bytes and avoid stale cache effects. Test page-boundary copies, aliasing-sensitive user-page copies, and runtime patch redirection.
