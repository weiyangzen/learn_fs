<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/thead/errata.c -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/thead/errata.c

## Purpose
Detects and applies T-Head C9xx errata for MAE, cache management operations, PMU behavior, and GhostWrite vulnerability marking.

## Important APIs, Types, And Functions
Important pieces include CSR `CSR_TH_SXSTATUS`, MAE bit `SXSTATUS_MAEE`, raw T-Head cache op encodings, `THEAD_CMO_OP`, cache operation callbacks, `errata_probe_mae()`, `errata_probe_cmo()`, `errata_probe_pmu()`, `errata_probe_ghostwrite()`, `thead_errata_probe()`, and `thead_errata_patch_func()`.

## Control Flow
Probe functions match T-Head-style zero arch/implementation IDs and stage constraints. CMO boot stage registers nonstandard cache ops and marks noncoherent support. The patch function iterates T-Head alternatives and either memcpy-patches during early boot or uses `patch_text_nosync()` later, flushing icache after early patches.

## State And Persistence
Persistent state includes patched text, registered nonstandard cache ops, `riscv_cbom_block_size`, noncoherent support flags, and GhostWrite vulnerability state.

## Dependencies And Integration Points
Integrated with RISC-V alternatives, vendor IDs, cacheflush, DMA noncoherent support, hwprobe/bugs reporting, text patching, and early boot CSR access.

## Risks And Edge Cases
Stage handling is delicate: early boot cannot use normal text patching, and late code must use `text_mutex`. The raw encoded cache instructions are vendor-specific and require correct block size. GhostWrite marking intentionally assumes broad vulnerability when xtheadvector is enabled.

## Test Signals
Signals are alternative patching on T-Head C9xx systems, registered cache maintenance callbacks, DMA coherency behavior, vulnerability reporting, and PMU workaround behavior.

Source read size: 224 lines, 6170 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/thead/errata.c -->
