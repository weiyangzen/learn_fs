<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/cacheflush.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/cacheflush.c

## Purpose
`cacheflush.c` implements RISC-V instruction-cache flush and CBO block-size initialization, plus prctl control for userspace `fence.i` context behavior.

## Important APIs, Types, And Functions
`flush_icache_all()`, `flush_icache_mm()`, `flush_icache_pte()`, `riscv_init_cbo_blocksizes()`, and `riscv_set_icache_flush_ctx()` are key APIs. Globals export CBOM, CBOZ, and CBOP block sizes.

## Control Flow
On SMP, global icache flush runs local `fence.i`, orders prior data writes with `RISCV_FENCE(w,o)`, then uses SBI remote fence or IPIs. Per-mm flush marks all harts stale, flushes local, and flushes active remote harts or defers work for later context switch. CBO init reads DT CPU nodes or ACPI RHCT. The prctl path toggles per-process/per-thread flush permissions and marks icaches stale when disabling user fence.i.

## State And Persistence
State includes exported CBO block sizes and per-mm/per-thread icache stale/force flags. No disk persistence exists.

## Dependencies And Integration Points
It depends on SBI rfence, SMP IPIs, mm context `icache_stale_mask`, OF/ACPI discovery, PTE cache-clean flags, and RISC-V prctl ABI.

## Risks
Incorrect ordering can let remote harts execute stale instructions. CBO block-size mismatches across harts are warned but still globally recorded. The prctl state must preserve migration-time icache coherency guarantees.

## Test Signals
JIT/self-modifying-code tests, BPF/module execution, SMP migration tests, OF/ACPI CBO discovery, and prctl fence.i selftests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/cacheflush.c -->
