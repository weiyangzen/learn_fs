# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4memset.S

Purpose: Niagara4 optimized memset and bzero routines.

Important APIs/functions: Defines `NG4memset` and `NG4bzero`.

Control flow: `NG4memset` expands a byte pattern to wider registers, writes leading bytes until aligned, uses xword and block-init stores for larger spans, then writes tails. `NG4bzero` provides the zero-fill entry and shares the optimized store paths.

State and persistence: No persistent state; writes target memory only.

Dependencies/integration: Includes `asm/asi.h`; installed by `niagara4_patch_bzero`.

Risks/test signals: Pattern expansion, block-store alignment, and tail completion are primary risks. Test zero/nonzero patterns, 0-128 byte ranges, page-sized ranges, and unaligned destinations.
