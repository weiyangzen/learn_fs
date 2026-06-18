# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_mem.h

## Purpose
`idpf_mem.h` defines the IDPF DMA memory descriptor used for control queues and convenience macros for reading and writing mailbox MMIO registers relative to a mapped mailbox BAR region.

## Important APIs, types, and functions
- `struct idpf_dma_mem` stores CPU virtual address `va`, DMA address `pa`, and allocation `size`.
- `idpf_mbx_wr32()`, `idpf_mbx_rd32()`, `idpf_mbx_wr64()`, and `idpf_mbx_rd64()` wrap `writel/readl/writeq/readq` against `a->mbx.vaddr + reg`.

## Control flow
This header has no runtime control flow. Callers allocate/free `struct idpf_dma_mem` through helpers in `idpf_lib.c` and use the mailbox macros to access admin/control queue registers.

## State and persistence behavior
`idpf_dma_mem` records DMA allocation metadata needed to free a coherent DMA block. The mailbox macros directly mutate or observe hardware MMIO state; they do not add locking, barriers beyond the MMIO accessors, or bounds checks.

## Dependencies and integration points
The header includes `linux/io.h` and is used by mailbox/control queue code throughout the IDPF driver. The DMA allocation/free implementation is in `idpf_lib.c`, while BAR mapping is initialized from `idpf_main.c`.

## Risks and edge cases
- Callers must ensure `mbx.vaddr` is valid and `reg` is within the mapped mailbox region; the macros do no validation.
- 64-bit MMIO access requires the target register and platform to support `readq/writeq` semantics.
- `struct idpf_dma_mem` must be kept in sync with allocation attributes; freeing with a stale size or address would corrupt DMA state.

## Test signals
Mailbox initialization, virtchnl send/receive traffic, DMA allocation/free failure injection, control queue teardown under reset/remove, and MMIO tracing for expected register offsets provide coverage.
