# Research: subset-b-000851

This grouped report covers the requested `sources/distributed-fs/ceph-client/arch/sparc/lib` files. Each section is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENcopy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/GENcopy_from_user.S

Purpose: Generic SPARC64 raw copy-from-user implementation wrapper. It parameterizes `GENmemcpy.S` so loads come from user address space through `ASI_AIUS` and the generated function is `GENcopy_from_user`.

Important APIs/functions: Defines `EX_LD`, `LOAD(type,addr,dest)`, `EX_RETVAL(x)`, `PREAMBLE`, and `FUNC_NAME`. The included body emits `GENcopy_from_user(dst, src, len)`.

Control flow: On kernel builds the preamble reads `%asi`; if the current address-space identifier is not `ASI_AIUS`, it branches to `raw_copy_in_user`. Otherwise the generic byte/word/xword copy loops in `GENmemcpy.S` run with exception-table guarded user loads.

State and persistence: No persistent state. It temporarily relies on `%asi`, integer registers, and exception-table metadata.

Dependencies/integration: Depends on `GENmemcpy.S`, `raw_copy_in_user`, SPARC alternate address spaces, and the kernel exception-table fixup mechanism. It is selected by generic CPU patching and built for `CONFIG_SPARC64`.

Risks/test signals: Highest risks are wrong residual count on a user fault, `%asi` mismatch handling, and bad branch/fixup targets. Test with fault-injection user copies, kernel/user address-limit transitions, zero/small/unaligned/large lengths, and SPARC64 boot smoke tests that exercise patched copy routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENcopy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENcopy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/GENcopy_to_user.S

Purpose: Generic SPARC64 raw copy-to-user wrapper. It specializes `GENmemcpy.S` so stores target user address space via `ASI_AIUS` and the generated function is `GENcopy_to_user`.

Important APIs/functions: Defines `EX_ST`, `STORE(type,src,addr)`, `EX_RETVAL(x)`, `PREAMBLE`, and `FUNC_NAME`. The included implementation emits `GENcopy_to_user(dst, src, len)`.

Control flow: The preamble checks `%asi` before copying and falls back to `raw_copy_in_user` when the active ASI is not the expected user ASI. Copying then follows `GENmemcpy.S` alignment, 64-bit, 32-bit, and byte tail paths with exception-table protected stores.

State and persistence: No stored state. It relies on `%asi`, temporary registers, and exception fixup entries.

Dependencies/integration: Depends on `GENmemcpy.S`, user store ASI encoding, `raw_copy_in_user`, and generic copyops patching. Integrated by `Makefile` under `CONFIG_SPARC64`.

Risks/test signals: Store faults must return correct uncopied byte counts and must not corrupt kernel state. Validate with protected/unmapped user destinations, unaligned lengths, KERNEL_DS-style `%asi` checks, and copy-to-user regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENcopy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENmemcpy.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/GENmemcpy.S

Purpose: Generic SPARC64 memcpy engine used directly as `GENmemcpy` and indirectly by generic copy-to/from-user wrappers.

Important APIs/functions: Emits `GENmemcpy` unless `FUNC_NAME` is overridden. Also emits local exception-return helpers such as `GEN_retl_o4_1`, `GEN_retl_g1_8`, `GEN_retl_o2_4`, and `GEN_retl_o2_1` when not building a user-copy specialization.

Control flow: Rejects lengths with high bits set via `tne`. For nonzero copies, it chooses small-copy, aligned xword-copy, or byte-copy paths. It aligns destination/source compatibility, copies leading bytes to alignment, transfers xwords in a loop, and handles tails with 32-bit or byte operations. `LOAD`, `STORE`, `EX_LD`, `EX_ST`, `PREAMBLE`, and `EX_RETVAL` are macro hooks for userspace-safe variants.

State and persistence: Stateless; returns destination for memcpy mode or a wrapper-selected residual value for user-copy mode.

Dependencies/integration: Requires `linux/linkage.h` in kernel builds and is included by `GENcopy_from_user.S` and `GENcopy_to_user.S`. Patched into public copy functions by `GENpatch.S`.

Risks/test signals: Alignment arithmetic, trap-on-large-length behavior, and exception residual helpers are fragile. Test zero, 1-16 byte, aligned, cross-aligned, unaligned, and oversized lengths; compare data against C memcpy and verify user-copy fault residuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENmemcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENpage.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/GENpage.S

Purpose: Generic SPARC64 page copy and clear implementations plus patch routine to redirect page operations to them.

Important APIs/functions: Defines `GENcopy_user_page`, `GENclear_page`, `GENclear_user_page`, and exported patch hook `generic_patch_pageops`.

Control flow: `GENcopy_user_page` loops over `PAGE_SIZE` in 64-byte chunks using eight 64-bit loads/stores per iteration. `GENclear_page` and `GENclear_user_page` loop similarly with zero stores. `generic_patch_pageops` rewrites `copy_user_page`, `_clear_page`, and `clear_user_page` entry stubs with unconditional branch instructions to generic implementations and flushes patched instruction addresses.

State and persistence: The copy/clear paths are stateless. The patch function persistently modifies text instructions at runtime.

Dependencies/integration: Depends on `asm/page.h`, SPARC branch encoding, instruction cache flush, and runtime CPU patching.

Risks/test signals: Text patch offset encoding and page-size loop count are critical. Validate page copy/clear correctness, runtime patch execution, instruction-cache coherency, and boot behavior on generic SPARC64 CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENpage.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENpatch.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/GENpatch.S

Purpose: Runtime patcher that redirects default Ultra-I copy routines to generic SPARC64 copy routines.

Important APIs/functions: Defines `generic_patch_copyops` and macro `GEN_DO_PATCH(OLD, NEW)`.

Control flow: For each old entry (`memcpy`, `raw_copy_from_user`, `raw_copy_to_user`), computes the relative branch displacement to the new generic implementation, writes a `ba` instruction over the old entry, writes a `nop` delay slot, and flushes the patched instruction.

State and persistence: Persistently mutates kernel text. No separate data state.

Dependencies/integration: Depends on `GENmemcpy`, `GENcopy_from_user`, `GENcopy_to_user`, SPARC instruction encoding, and CPU setup code that invokes this patcher.

Risks/test signals: Bad displacement math can redirect execution into invalid text. Test that patched symbols land on the expected functions, copying still works after boot patching, and instruction cache flushes are sufficient on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/GENpatch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7copy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/M7copy_from_user.S

Purpose: M7/T4-style optimized copy-from-user wrapper over `M7memcpy.S`.

Important APIs/functions: Defines exception-table wrappers for integer and floating-point loads, `FUNC_NAME M7copy_from_user`, ASI-based `LOAD`, `EX_RETVAL(0)`, and a preamble that checks `%asi` before falling back to `raw_copy_in_user`.

Control flow: The included M7 copy engine handles alignment, block/VIS paths, and tails while all user loads are guarded through exception-table records. On load fault, fixup returns a residual count appropriate for raw copy-from-user semantics.

State and persistence: No persistent data; transiently uses `%asi`, VIS/FPU state through the included implementation, and exception metadata.

Dependencies/integration: Depends on `M7memcpy.S`, `Memcpy_utils.S` residual helpers, `asm/asi.h`, VIS support, and M7 patching.

Risks/test signals: M7-specific ASIs and VIS paths must fault cleanly and restore state. Test user-source page faults, all alignments, large block copies, and fallback to `raw_copy_in_user` when ASI context changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7copy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7copy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/M7copy_to_user.S

Purpose: M7 optimized copy-to-user wrapper using the shared `M7memcpy.S` copy engine with user-space stores.

Important APIs/functions: Defines integer/FP store exception wrappers, `FUNC_NAME M7copy_to_user`, `STORE(type,src,addr)` using `%asi`, `STORE_ASI ASI_BLK_INIT_QUAD_LDD_AIUS`, `EX_RETVAL(0)`, and a `%asi` preamble.

Control flow: Verifies user ASI before copying, then dispatches through M7 alignment and block-copy paths. Store faults are routed through exception-table entries to residual helpers.

State and persistence: No persistent storage. Temporarily manipulates `%asi` and VIS/FPU registers through included code.

Dependencies/integration: Depends on `M7memcpy.S`, `Memcpy_utils.S`, SPARC M7 block-init ASIs, `raw_copy_in_user`, and `m7_patch_copyops`.

Risks/test signals: Risks include incorrect store ASI selection, missed FP-state restoration after fault, and wrong residual counts. Test protected user destinations, unaligned sizes, large streaming copies, and post-fault FPU/VIS state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7copy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7memcpy.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/M7memcpy.S

Purpose: High-performance SPARC M7 memory copy implementation and template for M7 user-copy variants.

Important APIs/functions: Emits `M7memcpy` unless overridden by wrappers. Macro hooks include `LOAD`, `STORE`, `STORE_INIT`, `STORE_INIT_MRU`, `EX_LD`, `EX_ST`, `EX_RETVAL`, and `PREAMBLE`.

Control flow: The function checks length sanity, handles alignment, then uses M7-specific VIS and block-init store strategies for large copies. It has dedicated paths for destination alignment, source alignment, medium sizes, small/tail copies, and cleanup labels such as `.Lexit_cp`. User-copy variants replace memory access and exception behavior through macro definitions.

State and persistence: Stateless data movement. It relies on temporary integer registers, VIS/FPU state, memory barriers, and `%asi` when specialized.

Dependencies/integration: Includes `asm/visasm.h` and `asm/asi.h`, relies on `Memcpy_utils.S` residual helpers, and is activated by `M7patch.S`.

Risks/test signals: This is performance-critical and architecture-sensitive. Test with randomized overlap-free buffers, cacheline/page-boundary alignments, large block sizes, user-copy fault injection, VIS state preservation, and comparisons against generic memcpy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7memset.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/M7memset.S

Purpose: SPARC M7 optimized memset, bzero, and page-clear implementation.

Important APIs/functions: Defines `M7clear_page`, `M7clear_user_page`, `M7bzero`, and `M7memset`. Uses `asm/asi.h` and `asm/page.h`.

Control flow: Page clear loops use block-init/MRU store ASIs for full-page zeroing. `M7memset` expands the byte pattern across registers, handles leading/trailing unaligned bytes, then writes larger aligned chunks using optimized stores. `M7bzero` routes zero-fill calls through the same core logic.

State and persistence: No persistent state; modifies target memory only and uses temporary registers/ASI stores.

Dependencies/integration: Built for `CONFIG_SPARC64` and selected by `m7_patch_bzero` and `m7_patch_pageops`.

Risks/test signals: Pattern replication, tail handling, and M7 block-init semantics are the main risks. Test all small lengths, page-size clears, unaligned addresses, nonzero patterns, and CPU patch replacement of generic bzero/page clear paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7patch.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/M7patch.S

Purpose: Runtime patcher for SPARC M7 copy, bzero/memset, and page operations.

Important APIs/functions: Defines `m7_patch_copyops`, `m7_patch_bzero`, and `m7_patch_pageops`, using a branch-and-nop patch macro.

Control flow: Each entry computes relative branch encodings from public/default routines to M7 implementations, overwrites old function entries, installs a `nop` delay slot, and flushes the instruction location.

State and persistence: Mutates kernel text permanently for the running boot session.

Dependencies/integration: Depends on M7 implementation symbols (`M7memcpy`, `M7copy_from_user`, `M7copy_to_user`, `M7bzero`, page-clear/copy routines) and CPU identification code that chooses M7 patching.

Risks/test signals: Wrong patch target or missing flush can break all memory operations. Test boot-time patch logs, symbol target disassembly, memcpy/copy-user/memset/page-clear correctness after patch, and fallback behavior on non-M7 CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/M7patch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/Makefile

Purpose: Builds SPARC architecture library objects for 32-bit and 64-bit kernel configurations.

Important APIs/functions: Uses `lib-$(CONFIG_SPARC32)`, `lib-$(CONFIG_SPARC64)`, `lib-y`, and `obj-*` lists. Adds `asflags-y := -DST_DIV0=0x02`.

Control flow: Kbuild conditionally includes arithmetic helpers, checksums, memory/string routines, copy routines, CPU-specific SPARC64 copy/page variants, atomics, tracing support, and I/O helpers based on `CONFIG_SPARC32`, `CONFIG_SPARC64`, and `$(BITS)`.

State and persistence: No runtime state. It controls build artifacts and link composition.

Dependencies/integration: Integrates every file in this subset into kernel build output. It selects generated variants (`GEN*`), UltraSPARC (`U1`, `U3`), Niagara (`NG`, `NG2`, `NG4`), and M7 routines so runtime patchers can redirect public symbols.

Risks/test signals: Missing or incorrectly conditioned objects cause unresolved symbols or wrong CPU patch availability. Test both SPARC32 and SPARC64 builds, verify object lists for selected configs, and run `nm`/link checks for exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/Memcpy_utils.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/Memcpy_utils.S

Purpose: Shared SPARC64 exception-return helpers for copy/memcpy implementations, especially CPU-specific user-copy variants.

Important APIs/functions: Defines `__restore_asi_fp`, `__restore_asi`, and many `memcpy_retl_*` helpers that compute residual byte counts from registers such as `%o2`, `%o3`, `%o4`, `%o5`, and `%g1`.

Control flow: Helpers branch to ASI restore paths, optionally execute `VISExitHalf`, restore `%asi` to `ASI_AIUS`, calculate the value returned in `%o0`, and return. FP-suffixed helpers restore VIS/FPU state before returning.

State and persistence: No persistent state; restores transient `%asi` and FPU state after exceptional or partial copy paths.

Dependencies/integration: Includes `linux/linkage.h`, `asm/asi.h`, and `asm/visasm.h`. Used by M7, NG4, and similar copy engines through exception-table fixup targets.

Risks/test signals: Residual arithmetic must match the exact faulting copy stage. Test page-fault injection at many byte offsets, verify `%asi` restoration after faults, and run VIS/FPU state preservation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/Memcpy_utils.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG2copy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG2copy_from_user.S

Purpose: Niagara2 optimized copy-from-user wrapper over `NG2memcpy.S`.

Important APIs/functions: Defines guarded `EX_LD` and `EX_LD_FP`, `FUNC_NAME NG2copy_from_user`, `%asi` user loads, block loads via `ASI_BLK_AIUS_4V`, and `EX_RETVAL(0)`.

Control flow: The preamble checks `%asi` and diverts non-user ASI cases to `raw_copy_in_user`. The included NG2 engine then selects alignment, VIS/block, medium, and tail paths; user loads are exception-table protected.

State and persistence: Stateless beyond temporary registers, VIS state, `%asi`, and exception-table entries.

Dependencies/integration: Depends on `NG2memcpy.S`, Niagara2 ASI definitions, `raw_copy_in_user`, and `niagara2_patch_copyops`.

Risks/test signals: User fault fixups, 4V block ASI behavior, and VIS restore are sensitive. Test user source faults, all alignments, large block paths, and patched runtime selection on Niagara2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG2copy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG2copy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG2copy_to_user.S

Purpose: Niagara2 optimized copy-to-user wrapper over `NG2memcpy.S`.

Important APIs/functions: Defines `EX_ST`, `EX_ST_FP`, `FUNC_NAME NG2copy_to_user`, user stores through `ASI_AIUS`, block stores through `ASI_BLK_AIUS_4V`, and `STORE_ASI ASI_BLK_INIT_QUAD_LDD_AIUS`.

Control flow: Checks `%asi`, falls back to `raw_copy_in_user` when needed, then runs NG2 copy paths with store exception fixups for faults.

State and persistence: No persistent data. Uses `%asi`, VIS/FPU registers, and exception-table records.

Dependencies/integration: Depends on `NG2memcpy.S`, SPARC 4V user block ASIs, `Memcpy_utils`/local residual helpers, and Niagara2 patching.

Risks/test signals: Store faults at block boundaries and tail copies must return accurate residuals. Test protected user destinations, partial copies, ASI fallback, and large copy throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG2copy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG2memcpy.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG2memcpy.S

Purpose: Niagara2 optimized memcpy engine and template for NG2 copy-to/from-user routines.

Important APIs/functions: Emits `NG2memcpy` by default, defines `__restore_fp`, `__restore_asi`, several `NG2_retl_*` residual helpers, and macro hooks for loads, stores, block operations, and store initialization.

Control flow: Validates length, handles tiny copies, aligns destination, chooses block/VIS paths for larger copies, uses store-init ASIs for cache-friendly writes, and falls back to word/byte tail loops. Wrapper files override access macros and exception behavior.

State and persistence: Stateless memory movement with transient VIS/FPU and ASI state.

Dependencies/integration: Includes `linux/linkage.h`, `asm/visasm.h`, and `asm/asi.h`; built under `CONFIG_SPARC64`; patched by `NG2patch.S`.

Risks/test signals: Complex alignment thresholds and block stores are risky. Test exact boundary lengths around 16, 64, and block thresholds, all source/destination low bits, user fault recovery, and comparison to generic memcpy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG2memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG2patch.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG2patch.S

Purpose: Runtime patcher that redirects copy operations to Niagara2 implementations.

Important APIs/functions: Defines `niagara2_patch_copyops` and a branch patch macro.

Control flow: Replaces public/default `memcpy`, `raw_copy_from_user`, and `raw_copy_to_user` entry points with branches to `NG2memcpy`, `NG2copy_from_user`, and `NG2copy_to_user`, then flushes patched instruction addresses.

State and persistence: Permanently patches kernel text during boot/runtime CPU setup.

Dependencies/integration: Depends on NG2 copy symbols and SPARC instruction encoding. Called by CPU feature selection for Niagara2-class systems.

Risks/test signals: Branch displacement and CPU selection must be correct. Test patched symbol disassembly, copy correctness after patch, and non-NG2 fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG2patch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4clear_page.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4clear_page.S

Purpose: Niagara4 optimized page clear implementation.

Important APIs/functions: Defines `NG4clear_page` and `NG4clear_user_page`.

Control flow: Iterates over `PAGE_SIZE`, using `stxa` with `ASI_ST_BLKINIT_MRU_P` to zero cacheline-sized/page chunks efficiently. `clear_user_page` aliases the same implementation while accepting an unused virtual-address argument.

State and persistence: No persistent state; writes zeros to the destination page.

Dependencies/integration: Includes `asm/asi.h` and `asm/page.h`; patched into `_clear_page` and `clear_user_page` by `NG4patch.S`.

Risks/test signals: Store ASI choice and page loop count are critical. Test full-page zeroing, page alignment, cache coherency, and patch activation on NG4 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4clear_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_from_user.S

Purpose: Niagara4 optimized copy-from-user wrapper using `NG4memcpy.S`.

Important APIs/functions: Defines guarded load macros, `FUNC_NAME NG4copy_from_user`, `%asi` user loads, `EX_RETVAL(0)`, and `%asi` preamble.

Control flow: Validates the active ASI, falls back to `raw_copy_in_user` if needed, then executes NG4 alignment, prefetch, VIS/block, and tail paths with exception-protected loads.

State and persistence: Stateless except for temporary `%asi`, VIS, and exception-table fixup metadata.

Dependencies/integration: Depends on `NG4memcpy.S`, `Memcpy_utils.S`, `raw_copy_in_user`, and `niagara4_patch_copyops`.

Risks/test signals: Fault recovery through VIS paths and prefetch/copy interactions require testing. Exercise unmapped user sources, boundary lengths, and patched copy-from-user calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_page.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_page.S

Purpose: Niagara4 optimized page copy routine.

Important APIs/functions: Defines `NG4copy_user_page(dest, src, vaddr)`.

Control flow: Copies one page using NG4-friendly block load/store sequencing and prefetching. It loops over `PAGE_SIZE`, moving cacheline-size chunks from source to destination.

State and persistence: No persistent state; mutates destination page only.

Dependencies/integration: Includes `asm/asi.h` and `asm/page.h`; installed by `niagara4_patch_pageops`.

Risks/test signals: Page copy must preserve all bytes and avoid stale cache effects. Test page-boundary copies, aliasing-sensitive user-page copies, and runtime patch redirection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_to_user.S

Purpose: Niagara4 optimized copy-to-user wrapper over `NG4memcpy.S`.

Important APIs/functions: Defines guarded store macros, `FUNC_NAME NG4copy_to_user`, user stores through `%asi`, `STORE_ASI ASI_BLK_INIT_QUAD_LDD_AIUS`, and `EX_RETVAL(0)`.

Control flow: Checks `%asi`, diverts non-user ASI cases to `raw_copy_in_user`, then uses NG4 copy paths with exception-table protected stores.

State and persistence: No persistent data; transiently uses `%asi`, VIS state, and fixup table entries.

Dependencies/integration: Depends on `NG4memcpy.S`, `Memcpy_utils.S`, SPARC ASIs, and `NG4patch.S`.

Risks/test signals: Store faults in large optimized paths must leave correct residuals and restored state. Test destination faults, short and long copies, and post-fault continued kernel execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4fls.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4fls.S

Purpose: Niagara4-specific find-last-set implementation.

Important APIs/functions: Defines `NG4fls` and `__NG4fls`.

Control flow: Uses SPARC integer bit operations to locate the highest set bit, with a public `fls`-style entry and an internal helper form. It returns zero for zero input and one-based bit position for nonzero input.

State and persistence: Pure register computation; no persistent state.

Dependencies/integration: Includes `linux/linkage.h`; patched into `fls` by `niagara4_patch_fls` when appropriate.

Risks/test signals: Off-by-one and zero-input behavior are the main risks. Test zero, powers of two, all-ones, and random 32-bit values against generic `fls`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4fls.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4memcpy.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4memcpy.S

Purpose: Niagara4 optimized memcpy engine and copy-user template.

Important APIs/functions: Emits `NG4memcpy` by default; macro hooks include `LOAD`, `STORE`, `STORE_INIT`, `EX_LD`, `EX_ST`, `EX_LD_FP`, `EX_ST_FP`, `FUNC_NAME`, and `PREAMBLE`.

Control flow: Checks length, handles tiny copies, aligns destination, prefetches source, uses VIS-assisted larger copy paths, and finishes with xword/byte tails. Wrapper files override memory access macros and exception target behavior.

State and persistence: Stateless data movement with temporary VIS/FPU and ASI state. Uses shared `Memcpy_utils.S` helpers for exceptional exits.

Dependencies/integration: Includes `linux/linkage.h`, `asm/visasm.h`, and `asm/asi.h`; patched by `NG4patch.S`.

Risks/test signals: Alignment-specific labels and prefetch/VIS interactions are high risk. Test all low-bit alignment combinations, exact threshold sizes, faulting user-copy variants, and throughput/correctness against generic routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4memset.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4memset.S

Purpose: Niagara4 optimized memset and bzero routines.

Important APIs/functions: Defines `NG4memset` and `NG4bzero`.

Control flow: `NG4memset` expands a byte pattern to wider registers, writes leading bytes until aligned, uses xword and block-init stores for larger spans, then writes tails. `NG4bzero` provides the zero-fill entry and shares the optimized store paths.

State and persistence: No persistent state; writes target memory only.

Dependencies/integration: Includes `asm/asi.h`; installed by `niagara4_patch_bzero`.

Risks/test signals: Pattern expansion, block-store alignment, and tail completion are primary risks. Test zero/nonzero patterns, 0-128 byte ranges, page-sized ranges, and unaligned destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4patch.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4patch.S

Purpose: Runtime patcher for Niagara4 copy, bzero, page, and `fls` operations.

Important APIs/functions: Defines `niagara4_patch_copyops`, `niagara4_patch_bzero`, `niagara4_patch_pageops`, and `niagara4_patch_fls`.

Control flow: Writes branch-and-nop stubs into generic/public routine entries so they jump to NG4-specific implementations, then flushes patched instruction locations.

State and persistence: Mutates executable kernel text for the running system.

Dependencies/integration: Depends on NG4 implementation symbols and CPU feature selection. Uses SPARC branch encodings and `flush`.

Risks/test signals: Patching a wrong symbol affects core memory and bit operations. Verify patched disassembly, run copy/memset/page/fls tests after patch, and confirm non-NG4 systems do not call this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NG4patch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGbzero.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NGbzero.S

Purpose: Niagara optimized memset, bzero, clear-user, and bzero patch support.

Important APIs/functions: Defines `NGmemset`, `NGbzero`, `NGclear_user`, and `niagara_patch_bzero`.

Control flow: `NGmemset` builds repeated byte patterns and jumps into `NGbzero` core paths. `NGbzero` handles zero length, leading bytes, medium xword stores, large block-init zeroing, and byte tails. `NGclear_user` sets `%asi` to `ASI_AIUS`, routes to the shared clear path, and uses exception-table guarded stores. The patcher redirects default bzero/memset routines to Niagara versions.

State and persistence: Memory writes only, except patcher text mutation. Clear-user temporarily changes `%asi`.

Dependencies/integration: Depends on `asm/asi.h`, exception-table fixups, and Niagara runtime patching.

Risks/test signals: User clear faults must return remaining bytes; patching must not break `memset`. Test user fault injection, zero/nonzero memset, page-sized bzero, and patched boot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGbzero.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGcopy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NGcopy_from_user.S

Purpose: First-generation Niagara copy-from-user wrapper over `NGmemcpy.S`.

Important APIs/functions: Defines guarded loads, `FUNC_NAME NGcopy_from_user`, `LOAD`, `LOAD_TWIN`, `EX_RETVAL(%g0)`, and ASI-checking preamble.

Control flow: Checks `%asi`, falls back to `raw_copy_in_user`, then runs the windowed `NGmemcpy.S` implementation. User loads and twin loads are exception protected.

State and persistence: Stateless; uses register-window state from the included implementation plus `%asi` and exception tables.

Dependencies/integration: Depends on `NGmemcpy.S`, `raw_copy_in_user`, and `niagara_patch_copyops`.

Risks/test signals: `NGmemcpy.S` uses input registers and save/restore style, so fault paths must match register conventions. Test user-source faults, all length buckets, and patched copy-from-user calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGcopy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGcopy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NGcopy_to_user.S

Purpose: First-generation Niagara copy-to-user wrapper over `NGmemcpy.S`.

Important APIs/functions: Defines guarded stores, `FUNC_NAME NGcopy_to_user`, user stores through `ASI_AIUS`, `STORE_ASI ASI_BLK_INIT_QUAD_LDD_AIUS`, `EX_RETVAL(%g0)`, and ASI preamble.

Control flow: Verifies active ASI, branches to `raw_copy_in_user` if not user ASI, then executes NG copy paths with exception-protected stores.

State and persistence: No persistent state; relies on `%asi`, register-window locals, and exception-table fixups.

Dependencies/integration: Depends on `NGmemcpy.S` and Niagara copyops patching.

Risks/test signals: Store fixups must map from NG register-window residual helpers back to raw-copy semantics. Test protected destinations, short and long copies, and after-patch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGcopy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGmemcpy.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NGmemcpy.S

Purpose: First-generation Niagara optimized memcpy engine and template for NG user-copy routines.

Important APIs/functions: Emits `NGmemcpy` by default. Defines `__restore_asi` and many `NG_ret_*` residual helpers. Macro hooks include `LOAD`, `LOAD_TWIN`, `STORE`, `STORE_INIT`, `EX_LD`, `EX_ST`, and `FUNC_NAME`.

Control flow: Uses a register window (`save`) and input registers for copy state. It checks lengths, aligns destination, uses paired loads/stores and block-init stores for large aligned spans, then handles medium and tiny copies. User wrappers override access macros for fault handling.

State and persistence: Stateless, but uses register-window state and temporary `%asi`.

Dependencies/integration: Includes `linux/linkage.h`, `asm/asi.h`, and `asm/thread_info.h`; patched by `NGpatch.S`.

Risks/test signals: Register-window conventions and residual helpers are fragile. Test every alignment low bit, length thresholds around 16/64, copy correctness, and user-copy faults at each stage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGmemcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGpage.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NGpage.S

Purpose: Niagara optimized copy-page and clear-page routines plus patch hook.

Important APIs/functions: Defines `NGcopy_user_page`, `NGclear_page`, `NGclear_user_page`, and `niagara_patch_pageops`.

Control flow: `NGcopy_user_page` uses prefetch and optimized chunked copy loops for a full page. `NGclear_page`/`NGclear_user_page` use block-init zero stores over `PAGE_SIZE`. The patcher redirects public page operations to NG routines.

State and persistence: Page operations are stateless; patcher modifies kernel text.

Dependencies/integration: Includes `asm/asi.h` and `asm/page.h`; called through CPU patch selection.

Risks/test signals: Page aliasing, cache behavior, and branch patching are sensitive. Test full-page copy/clear, user-page interfaces, and patched routine targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGpage.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGpatch.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/NGpatch.S

Purpose: Runtime patcher for first-generation Niagara copy operations.

Important APIs/functions: Defines `niagara_patch_copyops`.

Control flow: Computes branch offsets and overwrites `memcpy`, `raw_copy_from_user`, and `raw_copy_to_user` entries with branches to NG implementations, followed by flushed `nop` delay slots.

State and persistence: Mutates kernel text.

Dependencies/integration: Depends on `NGmemcpy`, `NGcopy_from_user`, `NGcopy_to_user`, and CPU setup.

Risks/test signals: Patch target mistakes can break all copy operations. Validate target disassembly and run memory/user-copy tests after Niagara patching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/NGpatch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/PeeCeeI.c -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/PeeCeeI.c

Purpose: Implements SPARC PCI-style string I/O helpers for byte, word, and long transfers.

Important APIs/functions: Exports `outsb`, `outsw`, `outsl`, `insb`, `insw`, and `insl`.

Control flow: Output helpers iterate over source buffers and write each element to an I/O address with the appropriate width and endian conversion where needed. Input helpers read repeated I/O values into memory. Long variants include alignment-aware byte assembly/disassembly so unaligned buffers are handled correctly.

State and persistence: No persistent driver state; effects are external I/O port writes/reads and destination buffer mutation.

Dependencies/integration: Includes `linux/module.h`, `asm/io.h`, and `asm/byteorder.h`. Exported symbols support drivers that use generic port-string APIs on SPARC.

Risks/test signals: Endianness and unaligned buffer handling are main risks. Test with emulated PCI I/O regions, odd counts, unaligned buffers, and byte/word/long ordering checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/PeeCeeI.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U1copy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/U1copy_from_user.S

Purpose: UltraSPARC-I/II/IIi/IIe optimized raw copy-from-user wrapper.

Important APIs/functions: Defines `FUNC_NAME raw_copy_from_user`, guarded integer/FP loads, `LOAD`, `LOAD_BLK`, `EX_RETVAL(0)`, and ASI preamble before including `U1memcpy.S`.

Control flow: Checks `%asi` and falls back to `raw_copy_in_user` for non-user ASI. The included U1 engine performs alignment setup, VIS/block copying, and tails while load exceptions return residual counts.

State and persistence: Stateless; uses `%asi`, VIS/FPU state, and exception-table records.

Dependencies/integration: Depends on `U1memcpy.S`, `asm/asi.h`, `asm/visasm.h`, and public raw-copy callers.

Risks/test signals: This is the default raw copy-from-user symbol for U1-class CPUs. Test user faults, small/large lengths, VIS state restoration, and fallback branch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U1copy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U1copy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/U1copy_to_user.S

Purpose: UltraSPARC-I/II/IIi/IIe optimized raw copy-to-user wrapper.

Important APIs/functions: Defines `FUNC_NAME raw_copy_to_user`, guarded integer/FP stores, `STORE`, `STORE_BLK`, `EX_RETVAL(0)`, and ASI preamble before including `U1memcpy.S`.

Control flow: Validates `%asi`, falls back to `raw_copy_in_user` when needed, then executes U1 copy paths with store fault fixups.

State and persistence: No persistent data. It temporarily uses ASI and VIS/FPU state.

Dependencies/integration: Depends on `U1memcpy.S`, user ASI constants, and raw-copy callers.

Risks/test signals: Store exception residuals and FPU cleanup are key. Test protected destinations, unaligned copies, and KERNEL_DS-style ASI fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U1copy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U1memcpy.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/U1memcpy.S

Purpose: UltraSPARC-I/II-family optimized memcpy and template for U1 raw user-copy functions.

Important APIs/functions: Emits `memcpy` by default, exports `FUNC_NAME`, and defines many U1 residual helpers (`U1_g1_1_fp`, `U1_gs_80_fp`, `U1_o2_0`, etc.) plus macros for VIS alignment and block loops.

Control flow: Checks length, handles tiny and medium copies, aligns the destination, enters VIS mode for large copies, runs one of eight unrolled alignment-specific block loops, completes residual VIS chunks, then handles tails. User-copy wrappers replace loads/stores and exception handling.

State and persistence: Stateless, but manipulates VIS/FPU state and uses memory barriers before/after block operations.

Dependencies/integration: Includes `linux/export.h`, `linux/linkage.h`, `asm/visasm.h`, and `asm/asi.h`; used by U1 copy wrappers.

Risks/test signals: VIS alignment dispatch and fault helpers are complex. Test all source alignment classes, boundary sizes around 16 and 320 bytes, randomized data comparisons, and user-copy faults inside VIS loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U1memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U3copy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/U3copy_from_user.S

Purpose: UltraSPARC-III/Cheetah optimized copy-from-user wrapper.

Important APIs/functions: Defines guarded loads, `FUNC_NAME U3copy_from_user`, ASI-based `LOAD`, and `EX_RETVAL(0)` before including `U3memcpy.S`.

Control flow: Uses the U3 copy engine with user-space loads and exception fixups. Unlike U1 wrappers, this file does not define an explicit ASI preamble in the wrapper, so behavior follows `U3memcpy.S` defaults plus user load macros.

State and persistence: Stateless; uses `%asi`, VIS/FPU state, and exception-table entries.

Dependencies/integration: Depends on `U3memcpy.S` and `cheetah_patch_copyops`.

Risks/test signals: Verify expected ASI setup by callers/patching and correct residuals on load faults. Test U3 patched copy-from-user, page faults, and alignment variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U3copy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U3copy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/U3copy_to_user.S

Purpose: UltraSPARC-III/Cheetah optimized copy-to-user wrapper.

Important APIs/functions: Defines guarded stores, `FUNC_NAME U3copy_to_user`, `STORE`, `STORE_BLK`, `EX_RETVAL(0)`, and ASI preamble before including `U3memcpy.S`.

Control flow: Checks `%asi`, falls back to `raw_copy_in_user`, then uses U3 copy paths with exception-protected stores and block stores.

State and persistence: No persistent state; temporary VIS/FPU and ASI use.

Dependencies/integration: Depends on `U3memcpy.S`, ASI constants, and `U3patch.S`.

Risks/test signals: Store fault recovery and ASI fallback must match raw copy semantics. Test protected destinations, VIS/block paths, and patched Cheetah systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U3copy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U3memcpy.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/U3memcpy.S

Purpose: UltraSPARC-III/Cheetah optimized memcpy engine and template for U3 user-copy routines.

Important APIs/functions: Emits `U3memcpy` by default. Defines `__restore_fp`, many `U3_retl_*` residual helpers, and macro hooks for `LOAD`, `STORE`, `STORE_BLK`, `PREAMBLE`, and `FUNC_NAME`.

Control flow: Validates length, aligns destination, uses VIS and prefetch for large copies, handles less-than-192-byte and less-than-16-byte paths separately, and returns through helper labels on exceptions. Wrappers override memory access and exception behavior.

State and persistence: Stateless; transiently uses VIS/FPU state and ASI.

Dependencies/integration: Includes `linux/linkage.h`, `asm/visasm.h`, and `asm/asi.h`; patched by `U3patch.S`.

Risks/test signals: Cheetah-specific prefetch/VIS loops and exception helpers can miscount residuals. Test random aligned/unaligned copies, lengths around 16 and 192, user faults, and comparison with generic memcpy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U3memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U3patch.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/U3patch.S

Purpose: Runtime patcher for UltraSPARC-III/Cheetah copy operations.

Important APIs/functions: Defines `cheetah_patch_copyops`.

Control flow: Replaces default/public `memcpy`, `raw_copy_from_user`, and `raw_copy_to_user` entries with branches to U3/Cheetah routines and flushes patched instructions.

State and persistence: Mutates kernel text.

Dependencies/integration: Depends on U3 implementation symbols and CPU detection.

Risks/test signals: Incorrect patching breaks fundamental memory operations. Validate branch targets, boot-time CPU selection, and copy tests after patch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/U3patch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/VISsave.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/VISsave.S

Purpose: Saves/restores or prepares VIS/FPU state for kernel VIS-using routines.

Important APIs/functions: Exports `VISenter`.

Control flow: `VISenter` inspects floating-point register state in `%fprs` and thread metadata (`TI_FPSAVED`). It saves dirty lower/upper FP register halves into the current thread as needed, updates saved flags, issues synchronization barriers, enables FPRS state, and returns through the caller-supplied `%g7` continuation.

State and persistence: Persists FP/VIS register contents into current thread save areas and updates thread flags.

Dependencies/integration: Includes `asm/ptrace.h`, `asm/visasm.h`, `asm/thread_info.h`, `asm/page.h`, and ASI definitions. Used by assembly memory routines that rely on VIS.

Risks/test signals: Incorrect save/restore corrupts user FP state. Test context switches around VIS-using kernel paths, signal delivery with FP state, and stress copy/memset routines under FP-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/VISsave.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/ashldi3.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/ashldi3.S

Purpose: SPARC32 libgcc-compatible 64-bit arithmetic left shift helper.

Important APIs/functions: Exports `__ashldi3`.

Control flow: Takes a 64-bit value split across registers and a shift count. It handles count ranges below/above 32 bits, shifts high/low halves accordingly, clears vacated low bits, and returns the shifted 64-bit result.

State and persistence: Pure register computation; no memory state.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; built for `CONFIG_SPARC32` when compiler-generated 64-bit shifts need helper routines.

Risks/test signals: Boundary counts 0, 31, 32, and 63 are risky. Test compiler helper calls and compare against C 64-bit shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/ashldi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/ashrdi3.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/ashrdi3.S

Purpose: SPARC32 libgcc-compatible signed 64-bit arithmetic right shift helper.

Important APIs/functions: Exports `__ashrdi3`.

Control flow: Handles shift counts below and above 32 bits while preserving sign extension from the high half. Uses arithmetic shifts for signed high-half propagation and combines shifted halves into the 64-bit result.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Sign extension and count boundaries are key. Test negative and positive 64-bit values with counts 0, 1, 31, 32, and 63 against C arithmetic shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/ashrdi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/atomic32.c -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/atomic32.c

Purpose: Implements atomic and cmpxchg/xchg helpers for SPARC32 using spinlock serialization.

Important APIs/functions: Exports `arch_atomic_add_return`, `arch_atomic_fetch_add/and/or/xor`, `arch_atomic_xchg`, `arch_atomic_cmpxchg`, `arch_atomic_fetch_add_unless`, `arch_atomic_set`, `sp32___set_bit`, `sp32___clear_bit`, `sp32___change_bit`, `__cmpxchg_u8/u16/u32/u64`, and `__xchg_u32`.

Control flow: Hashes target addresses to a small spinlock array when SMP or uses a dummy lock otherwise. Each operation locks, reads/modifies/writes the target, unlocks, and returns old or new values per API contract.

State and persistence: Maintains static spinlocks. Mutates atomic variables and bit words.

Dependencies/integration: Includes `linux/atomic.h`, `linux/spinlock.h`, and `linux/module.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Lock hashing affects contention and correctness. Test atomic API litmus cases, cmpxchg sizes, SMP stress, interrupt context assumptions, and bit operation return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/atomic32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/atomic_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/atomic_64.S

Purpose: SPARC64 atomic integer and atomic64 operations using compare-and-swap loops.

Important APIs/functions: Exports `arch_atomic_{add,sub,and,or,xor}`, return/fetch variants, `arch_atomic64_*` equivalents, and `arch_atomic64_dec_if_positive`.

Control flow: Macros generate loops that load current value, compute new value, attempt `cas`/`casx`, and retry with `BACKOFF_SPIN` on contention. Return variants return new value; fetch variants return old value. `dec_if_positive` decrements only if the old value is nonnegative after decrement semantics allow it.

State and persistence: Mutates atomic memory locations; no separate state.

Dependencies/integration: Includes `asm/asi.h` and `asm/backoff.h`; built for `CONFIG_SPARC64`.

Risks/test signals: Memory ordering, retry loops, and signed dec-if-positive behavior are critical. Run atomic selftests, concurrency stress, and compare return/fetch semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/atomic_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/bitext.c -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/bitext.c

Purpose: Simple bitmap allocator utilities for SPARC bit-map structures.

Important APIs/functions: Defines `bit_map_string_get`, `bit_map_clear`, and `bit_map_init`.

Control flow: `bit_map_string_get` scans a bitmap for a contiguous zero run of requested length aligned to the requested boundary, marks it allocated, and returns offset or `-1`. `bit_map_clear` clears a range. `bit_map_init` initializes metadata and clears the backing bitmap.

State and persistence: Mutates the caller-provided `struct bit_map` backing bitmap and metadata counters.

Dependencies/integration: Includes `linux/string.h`, `linux/bitmap.h`, and `asm/bitext.h`.

Risks/test signals: Off-by-one range scans and alignment handling are primary risks. Test allocation/free cycles, full maps, exact-size allocations, alignment > 1, and fragmentation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/bitext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/bitops.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/bitops.S

Purpose: SPARC64 atomic bit operation primitives.

Important APIs/functions: Exports `test_and_set_bit`, `test_and_clear_bit`, `test_and_change_bit`, `set_bit`, `clear_bit`, and `change_bit`.

Control flow: Computes the target word and bit mask, loads the word, applies set/clear/xor, attempts atomic `casx`, retries with `BACKOFF_SPIN` on failure, and returns the previous bit state for test-and variants.

State and persistence: Mutates caller-provided bitmaps atomically.

Dependencies/integration: Includes `linux/export.h`, `linux/linkage.h`, `asm/asi.h`, and `asm/backoff.h`; used by generic kernel bitops on SPARC64.

Risks/test signals: Bit numbering, word address calculation, and return-old-bit semantics are critical. Run bitops selftests and SMP contention stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/bitops.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/blockops.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/blockops.S

Purpose: SPARC32 one-page zero and copy block helpers.

Important APIs/functions: Exports `bzero_1page` and `__copy_1page`.

Control flow: `bzero_1page` loops over `PAGE_SIZE` using a macro that writes a block of zeros at multiple offsets. `__copy_1page` loops over a page using a macro that loads source words and stores them to destination.

State and persistence: Mutates a single destination page; no persistent state.

Dependencies/integration: Includes `asm/page.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Loop count and block offsets must cover exactly one page. Test full page clear/copy, page alignment, and comparison against generic page helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/blockops.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/bzero.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/bzero.S

Purpose: SPARC64 baseline `memset`, `__bzero`, and `__clear_user`.

Important APIs/functions: Exports `memset`, `__bzero`, and `__clear_user`.

Control flow: `memset` replicates the byte pattern and enters `__bzero`-style fill loops. `__bzero` handles leading bytes, aligned large xword stores with prefetch, medium chunks, and byte tails. `__clear_user` mirrors zeroing through user ASI stores protected by exception-table entries and returns remaining bytes on fault.

State and persistence: Mutates target memory; user clear temporarily uses `%asi` and exception metadata.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; may be patched by CPU-specific bzero patchers.

Risks/test signals: Tail logic and clear-user residuals are sensitive. Test all small sizes, unaligned addresses, nonzero memset patterns, user faults, and CPU patch replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/bzero.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/checksum_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/checksum_32.S

Purpose: SPARC32 Internet checksum and checksum-copy routines.

Important APIs/functions: Exports `csum_partial` and `__csum_partial_copy_sparc_generic`.

Control flow: `csum_partial` fixes alignment, processes large unrolled chunks, handles remaining table-sized chunks, folds carries, and consumes trailing bytes. The copy variant copies from source to destination while accumulating checksum, with exception fixups for faulting loads/stores.

State and persistence: No persistent state; mutates destination for copy variant and returns checksum/fault status.

Dependencies/integration: Includes `linux/export.h` and `asm/errno.h`; used by networking stack and copy-checksum helpers.

Risks/test signals: Carry folding, odd-byte alignment, endian behavior, and fault recovery are key. Test RFC-style checksum vectors, odd/even addresses, all tail lengths, and faulting copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/checksum_32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/checksum_64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/checksum_64.S

Purpose: SPARC64 Internet checksum implementation.

Important APIs/functions: Exports `csum_partial`.

Control flow: Aligns the buffer, accumulates 32-bit words using SPARC carry chains, processes unrolled chunks, handles end cruft bytes/halfwords, folds carries, and returns the partial checksum.

State and persistence: Pure read-only checksum computation; no persistent state.

Dependencies/integration: Includes `linux/export.h`; used by networking checksum paths on SPARC64.

Risks/test signals: Odd alignment and carry folding errors break network checksums. Test known checksum vectors, all start alignments, small tails, and large buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/checksum_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/clear_page.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/clear_page.S

Purpose: Baseline SPARC64 page clear and user-page clear implementation.

Important APIs/functions: Exports `_clear_page` and `clear_user_page`.

Control flow: Handles page clear through VIS/block store sequences, with cache/page-color considerations from SPARC headers. `clear_user_page` reaches common clear code after any needed setup, and the common loop writes zeros over `PAGE_SIZE`.

State and persistence: Mutates destination page only; uses transient VIS/FPU state.

Dependencies/integration: Includes `linux/pgtable.h`, `asm/visasm.h`, `asm/thread_info.h`, `asm/page.h`, `asm/spitfire.h`, and `asm/head.h`. CPU-specific page patchers may replace it.

Risks/test signals: VIS state and cache alias behavior are important. Test page clear correctness, user-page clear, CPU patch interaction, and FP/VIS state preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/clear_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/copy_in_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/copy_in_user.S

Purpose: Raw copy between two user-space addresses on SPARC64.

Important APIs/functions: Exports `raw_copy_in_user`.

Control flow: Uses ASI-based loads and stores for both source and destination, protected by exception table entries. It chooses aligned xword, 32-bit, and byte-copy paths similar to generic memcpy and returns remaining bytes on fault.

State and persistence: No persistent state; mutates user destination and uses `%asi`.

Dependencies/integration: Includes `linux/export.h`, `linux/linkage.h`, and `asm/asi.h`; used as fallback by copy-to/from-user wrappers when the current ASI is not the expected one.

Risks/test signals: Dual user-source/user-destination faults and residual counts are key. Test source fault, destination fault, overlap expectations, and all alignment/length paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/copy_in_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/copy_page.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/copy_page.S

Purpose: Baseline and Cheetah-patchable SPARC64 page copy implementation.

Important APIs/functions: Exports `copy_user_page` and defines `cheetah_patch_copy_page`.

Control flow: Copies a page using VIS/block load-store paths with prefetch and cache considerations. The Cheetah patch hook modifies specific instructions to tune page-copy behavior for that CPU class.

State and persistence: Page copy mutates destination only; patch hook modifies instruction text.

Dependencies/integration: Includes VIS, thread, page, pgtable, Spitfire, and head headers. May be superseded by NG/NG4/GEN page patchers.

Risks/test signals: Patchable instruction locations and cache aliasing are high risk. Test full page copies, COW/user-page paths, Cheetah patch application, and data integrity across page colors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/copy_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/copy_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/copy_user.S

Purpose: SPARC32 user-copy implementation with exception handling.

Important APIs/functions: Exports `__copy_user` and marks `__copy_user_begin`/`__copy_user_end`.

Control flow: Contains optimized dword/word/byte copy paths, alignment tables, and fixup labels for big chunks, last chunks, half chunks, and short chunks. Exception table macros redirect faults to code that computes remaining bytes and returns.

State and persistence: No persistent state; mutates destination and relies on exception-table metadata.

Dependencies/integration: Includes `asm/ptrace.h`, `asm/asmmacro.h`, `asm/page.h`, and `asm/thread_info.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Fixup tables must cover every faulting access. Test user copy fault injection, alignment table paths, small/large copies, and begin/end metadata consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/copy_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy.S

Purpose: SPARC64 checksum-and-copy engine used directly and as a template for user checksum copies.

Important APIs/functions: Emits `csum_partial_copy_nocheck` by default; wrapper files override `FUNC_NAME`, `LOAD`, and `STORE`.

Control flow: Aligns source, copies words to destination while accumulating checksum with carry handling, processes unrolled chunks, handles tail bytes, folds final checksum, and has fault handling controlled by macro wrappers.

State and persistence: Mutates destination buffer and returns checksum; no persistent state.

Dependencies/integration: Includes `linux/export.h`; included by `csum_copy_from_user.S` and `csum_copy_to_user.S`.

Risks/test signals: Must preserve checksum correctness while copying and handling faults. Test known checksum vectors, odd alignments, all tail sizes, and user wrappers with fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy_from_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy_from_user.S

Purpose: SPARC64 checksum-and-copy-from-user wrapper.

Important APIs/functions: Defines `FUNC_NAME csum_and_copy_from_user` and ASI-based guarded `LOAD`, then includes `csum_copy.S`.

Control flow: User loads are wrapped in exception-table entries that return through a fault path; successful flow follows `csum_copy.S` alignment/chunk/tail checksum-copy logic.

State and persistence: Mutates kernel destination and returns checksum/fault indication; no persistent state.

Dependencies/integration: Depends on `csum_copy.S`, `asm/asi.h` behavior through included code, and networking/usercopy callers.

Risks/test signals: Faulting source pages must not produce misleading checksums. Test user faults at each alignment/tail position and compare successful checksums to software reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy_from_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy_to_user.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy_to_user.S

Purpose: SPARC64 checksum-and-copy-to-user wrapper.

Important APIs/functions: Defines `FUNC_NAME csum_and_copy_to_user` and ASI-based guarded `STORE`, then includes `csum_copy.S`.

Control flow: Reads kernel source, computes checksum while storing to user memory. Store faults are exception-table routed; successful copies follow the shared checksum-copy loops.

State and persistence: Mutates user destination and returns checksum/fault status.

Dependencies/integration: Depends on `csum_copy.S`, user ASI store semantics, and networking send/copy paths.

Risks/test signals: Partial user destination faults must not hide incomplete copies. Test protected destinations, odd alignments, all tail lengths, and checksum reference comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/csum_copy_to_user.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/divdi3.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/divdi3.S

Purpose: SPARC32 libgcc-compatible signed 64-bit division helper.

Important APIs/functions: Exports `__divdi3`.

Control flow: Normalizes operand signs, performs multiword division using shift/subtract loops for several operand-size cases, then reapplies result sign. It handles 64-bit numerator/divisor values split across registers.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h`; built for `CONFIG_SPARC32` to satisfy compiler helper calls.

Risks/test signals: Division by edge values, sign handling, and overflow-like `INT64_MIN / -1` behavior are sensitive. Test positive/negative combinations, small/large divisors, and compare with C 64-bit division.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/divdi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/ffs.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/ffs.S

Purpose: SPARC64 find-first-set helpers.

Important APIs/functions: Exports `ffs` and `__ffs`.

Control flow: Handles zero specially for `ffs`, then uses bit tests/shifts to locate the least significant set bit. `ffs` returns one-based index or zero; `__ffs` returns zero-based index for nonzero input.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`.

Risks/test signals: Zero handling and one-based vs zero-based return contracts can be confused. Test zero, powers of two, all-ones, and random values against generic helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/ffs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/fls.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/fls.S

Purpose: SPARC64 find-last-set for 32-bit values.

Important APIs/functions: Exports `fls`.

Control flow: Tests progressively smaller bit ranges to determine the highest set bit and returns a one-based bit position, or zero for input zero.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; may be patched to `NG4fls` on Niagara4.

Risks/test signals: Off-by-one around high bit and zero input are primary. Test all powers of two, zero, and random values against generic `fls`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/fls.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/fls64.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/fls64.S

Purpose: SPARC64 find-last-set helper for 64-bit values.

Important APIs/functions: Exports `__fls`.

Control flow: Determines the highest set bit through staged tests/shifts across the 64-bit input and returns a zero-based index for nonzero values.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`.

Risks/test signals: High-half/low-half boundary and return indexing are critical. Test bit 0, bit 31, bit 32, bit 63, all-ones, and random values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/fls64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/hweight.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/hweight.S

Purpose: SPARC64 population-count helpers.

Important APIs/functions: Exports `__arch_hweight8`, `__arch_hweight16`, `__arch_hweight32`, and `__arch_hweight64`.

Control flow: Uses the SPARC population-count instruction/sequence to count set bits in the requested operand width and returns the count.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; used by generic bit-count APIs.

Risks/test signals: Width masking must match API expectations. Test zero, all-ones for each width, sparse bits, and random values against generic hweight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/hweight.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/iomap.c -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/iomap.c

Purpose: Minimal SPARC I/O port mapping helpers.

Important APIs/functions: Exports `ioport_map`, `ioport_unmap`, and `pci_iounmap`.

Control flow: `ioport_map` converts an I/O port number to an `__iomem` address using SPARC I/O encoding. `ioport_unmap` and `pci_iounmap` are no-op unmap stubs for this architecture mapping model.

State and persistence: No persistent state or allocation.

Dependencies/integration: Includes `linux/pci.h`, `linux/module.h`, and `asm/io.h`; used by generic PCI/I/O code.

Risks/test signals: Address translation must match SPARC I/O accessor expectations. Test drivers using port I/O, mapping/unmapping smoke tests, and sparse address annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/ipcsum.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/ipcsum.S

Purpose: Fast IPv4 header checksum routine.

Important APIs/functions: Exports `ip_fast_csum`.

Control flow: Accumulates the fixed and variable IPv4 header words using carry-propagating additions based on `ihl`, folds carries, complements the result, and returns the 16-bit checksum.

State and persistence: Pure read-only computation over the IP header.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; used by IPv4 networking fast paths.

Risks/test signals: Header-length handling and carry folding are key. Test minimum 20-byte headers, option-bearing headers, odd data patterns, and compare to generic checksum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/ipcsum.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/libgcc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/libgcc.h

Purpose: Shared type definitions for SPARC libgcc-style helper implementations.

Important APIs/functions: Defines `word_type` with GCC `mode(__word__)`.

Control flow: Header-only; no runtime control flow.

State and persistence: No state.

Dependencies/integration: Includes `asm/byteorder.h`; supports arithmetic helper files that need compiler word-sized types.

Risks/test signals: Type width must match compiler ABI. Test by building SPARC32 arithmetic helpers and checking generated symbol ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/libgcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/locks.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/locks.S

Purpose: SPARC32 low-level read/write lock primitives.

Important APIs/functions: Exports `___rw_read_enter`, `___rw_read_exit`, `___rw_read_try`, and `___rw_write_enter`.

Control flow: Implements spinning paths for entering/exiting read locks and acquiring write locks. It checks lock word state, spins when writer bits are set, updates counters atomically with architecture primitives, and returns success/failure for try-lock.

State and persistence: Mutates lock words supplied by callers.

Dependencies/integration: Includes `asm/ptrace.h`, `asm/psr.h`, `asm/smp.h`, and `asm/spinlock.h`; used by SPARC32 locking code.

Risks/test signals: Reader count, writer bit, and SMP interrupt interactions are critical. Test lock torture, try-lock semantics, and contention on SMP SPARC32.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/locks.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/lshrdi3.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/lshrdi3.S

Purpose: SPARC32 libgcc-compatible logical 64-bit right shift helper.

Important APIs/functions: Exports `__lshrdi3`.

Control flow: Handles shift counts below/above 32 bits without sign extension, combines high and low halves, and zero-fills vacated high bits.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Boundary counts and zero fill are key. Test values with high bit set and shift counts 0, 31, 32, and 63 against C unsigned shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/lshrdi3.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/mcount.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/mcount.S

Purpose: SPARC64 ftrace/mcount instrumentation entry code.

Important APIs/functions: Exports `_mcount`, `mcount`, defines `ftrace_stub`, `ftrace_caller`, patch sites `ftrace_call` and `ftrace_graph_call`, plus `ftrace_graph_caller` and `return_to_handler`.

Control flow: Saves enough call-frame state, checks tracing recursion/patch state, calls dynamic ftrace or graph tracing hooks through patchable call sites, and restores return paths. Graph tracing can redirect returns through `return_to_handler`.

State and persistence: Interacts with ftrace runtime patch state and call graph return stacks; no private persistent data here.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; integrated with kernel ftrace and function graph tracer.

Risks/test signals: Register-window and return-address handling are delicate. Test dynamic ftrace enable/disable, graph tracing, module tracing, and recursion protection under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/mcount.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memcmp.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/memcmp.S

Purpose: SPARC assembly `memcmp`.

Important APIs/functions: Exports `memcmp`.

Control flow: Loops byte-by-byte while length remains and bytes are equal. On mismatch, subtracts byte values and returns signed difference; on completion returns zero.

State and persistence: Pure read-only buffer comparison.

Dependencies/integration: Includes `linux/export.h`, `linux/linkage.h`, and `asm/asm.h`.

Risks/test signals: Return sign and zero-length behavior are main checks. Test equal buffers, first/last-byte mismatches, all byte values, and zero length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memcmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memcpy.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/memcpy.S

Purpose: SPARC32 optimized `memcpy` and `memmove`.

Important APIs/functions: Exports `memcpy` and `memmove`; uses local macro `FUNC` for symbol definitions and multiple alignment tables.

Control flow: `memmove` detects overlap and uses reverse-copy when needed. `memcpy` aligns source/destination, uses dword/word copy tables for large aligned cases, handles non-aligned cases by shifting/combining words, and finishes with short/tail byte paths.

State and persistence: Mutates destination buffer; no persistent state.

Dependencies/integration: Includes `linux/export.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Overlap handling, table jumps, and unaligned word assembly are risky. Test overlapping memmove, non-overlap memcpy, all alignments, tiny sizes, and randomized buffer comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memmove.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/memmove.S

Purpose: SPARC64 `memmove` implementation.

Important APIs/functions: Exports `memmove`.

Control flow: Compares destination/source ranges. If forward copy is safe, copies bytes/xwords forward with alignment checks. If ranges overlap with destination after source, it copies backward from the end to preserve source bytes.

State and persistence: Mutates destination buffer only.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; built for `CONFIG_SPARC64`.

Risks/test signals: Overlap direction and tail handling are primary. Test identical pointers, forward/backward overlap, unaligned starts, zero length, and random memmove comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memmove.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memscan_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/lib/memscan_32.S

Purpose: SPARC32 memory scan helpers.

Important APIs/functions: Exports `memscan`, `__memscan_zero`, and `__memscan_generic`.

Control flow: `__memscan_zero` has optimized zero-byte scanning with alignment setup, word-at-a-time zero detection, and byte resolution. `memscan`/`__memscan_generic` scan for an arbitrary byte value through byte loops.

State and persistence: Pure read-only scan; returns pointer to found byte or end.

Dependencies/integration: Includes `linux/export.h`; built for 32-bit memory/string API support.

Risks/test signals: End pointer, zero-length behavior, and word-scan false positives are key. Test zero and nonzero searches, aligned/unaligned buffers, no-match cases, and matches at first/last byte.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/lib/memscan_32.S -->
