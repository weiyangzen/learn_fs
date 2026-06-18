# sources/distributed-fs/ceph-client/arch/sparc/lib/GENmemcpy.S

Purpose: Generic SPARC64 memcpy engine used directly as `GENmemcpy` and indirectly by generic copy-to/from-user wrappers.

Important APIs/functions: Emits `GENmemcpy` unless `FUNC_NAME` is overridden. Also emits local exception-return helpers such as `GEN_retl_o4_1`, `GEN_retl_g1_8`, `GEN_retl_o2_4`, and `GEN_retl_o2_1` when not building a user-copy specialization.

Control flow: Rejects lengths with high bits set via `tne`. For nonzero copies, it chooses small-copy, aligned xword-copy, or byte-copy paths. It aligns destination/source compatibility, copies leading bytes to alignment, transfers xwords in a loop, and handles tails with 32-bit or byte operations. `LOAD`, `STORE`, `EX_LD`, `EX_ST`, `PREAMBLE`, and `EX_RETVAL` are macro hooks for userspace-safe variants.

State and persistence: Stateless; returns destination for memcpy mode or a wrapper-selected residual value for user-copy mode.

Dependencies/integration: Requires `linux/linkage.h` in kernel builds and is included by `GENcopy_from_user.S` and `GENcopy_to_user.S`. Patched into public copy functions by `GENpatch.S`.

Risks/test signals: Alignment arithmetic, trap-on-large-length behavior, and exception residual helpers are fragile. Test zero, 1-16 byte, aligned, cross-aligned, unaligned, and oversized lengths; compare data against C memcpy and verify user-copy fault residuals.
