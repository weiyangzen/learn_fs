<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sram.h -->
# sources/distributed-fs/ceph-client/include/linux/sram.h

Purpose: Declares a generic SRAM executable-copy helper.

Important APIs/types/functions: `sram_exec_copy(struct gen_pool *pool, void *dst, void *src, size_t size)`.

Control flow: When `CONFIG_SRAM_EXEC` is enabled, an external implementation copies executable content into SRAM from a gen_pool-backed allocation. Otherwise the inline stub returns `NULL`.

State and persistence behavior: No state in the header; implementation likely affects SRAM contents and instruction-cache coherency.

Dependencies: Forward-declares `struct gen_pool` and uses `size_t`.

Integration points: Platform code needing to execute small routines from SRAM, often for low-power or timing-sensitive paths.

Risks: Callers must handle `NULL` when SRAM execution is disabled or unavailable. Executable memory copying requires cache, permissions, and pool-lifetime correctness.

Test signals: Build coverage with and without `CONFIG_SRAM_EXEC`; platform tests validating copied code executes and fallback paths handle `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sram.h -->
