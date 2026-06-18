<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata.c -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata.c

## Purpose
Detects and patches SiFive CIP-453 and CIP-1200 errata.

## Important APIs, Types, And Functions
Defines `struct errata_info_t`, check functions for CIP-453 and CIP-1200, `errata_list`, `sifive_errata_probe()`, and `sifive_errata_patch_func()`. CIP-1200 can set `tlb_flush_all_threshold = 0` under MMU.

## Control Flow
The patch function skips early boot, probes CPU arch/implementation IDs, iterates SiFive alternative entries, validates patch IDs, and applies matching alternative text under `text_mutex`.

## State And Persistence
Persistent state is patched text and, for CIP-1200, changed TLB flush threshold policy.

## Dependencies And Integration Points
Integrated with RISC-V alternatives, text patching, vendor IDs, errata IDs, TLB flush behavior, and optional CIP-453 assembly handlers.

## Risks And Edge Cases
CPU ID range checks are the core correctness boundary. Too broad a match can apply unnecessary workarounds; too narrow can leave affected CPUs broken. Patch length and IDs must match alternative entries.

## Test Signals
Signals are boot-time alternative patching on affected SiFive cores, TLB flush threshold change for CIP-1200, and page/insn fault behavior for CIP-453.

Source read size: 109 lines, 2601 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/errata.c -->
