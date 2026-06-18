<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/andes/errata.c -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/andes/errata.c

## Purpose
Handles Andes AX45MP IOCP/cache-management errata detection and platform noncoherent DMA setup.

## Important APIs, Types, And Functions
Important constants include AX45MP marchid/mimpid and Andes SBI extension/function IDs. Functions are `ax45mp_iocp_sw_workaround()`, `errata_probe_iocp()`, and `andes_errata_patch_func()`.

## Control Flow
At boot alternative stage, the probe checks config, runs once, matches AX45MP IDs, calls the Andes SBI workaround query, and if needed sets `riscv_cbom_block_size` and marks noncoherent support. There are currently no text patches.

## State And Persistence
Persistent state includes the static `done` guard and global noncoherent/cache block state.

## Dependencies And Integration Points
Integrated with SBI, RISC-V alternatives, vendor extension IDs, cacheflush, and noncoherent DMA support.

## Risks And Edge Cases
A wrong SBI result or CPU ID match can enable noncoherent handling incorrectly or miss required cache maintenance. The function intentionally returns without patching text.

## Test Signals
Signals are boot logs/noncoherent DMA behavior on AX45MP platforms and no-op behavior on other Andes or non-Andes CPUs.

Source read size: 75 lines, 1890 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/andes/errata.c -->
