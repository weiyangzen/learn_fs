<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_special_blocks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_special_blocks.h

## Purpose
Auto-generated Gaudi2 special block topology table. `GAUDI2_SPECIAL_BLOCKS` expands to initializer rows describing block type, base address, repetition counts, secondary dimensions, and address strides for nonuniform or security/debug-relevant device blocks.

## Important APIs, Types, And Functions
- `GAUDI2_SPECIAL_BLOCKS` is the only exported macro.
- Rows use `GAUDI2_BLOCK_TYPE_*` symbols such as TPC, HMMU, MME, EU_BIST, SYNC_MNGR, HIF, RTR, SRAM, EDMA, DEC, PCIE, PSOC, PLL, PDMA, CPU, PMMU, XBAR, ROT, ARC_FARM, XFT, HBM, and NIC.
- Each row provides a base address plus count/stride-like numeric fields consumed by block enumeration code.

## Control Flow
The file has no functions. Driver code expands the macro into an array of block descriptors, then iterates those descriptors for block discovery, firewall/security programming, register access classification, reset/isolation logic, or diagnostic traversal.

## State And Persistence Behavior
The macro is compile-time topology data. Runtime state is in the constructed descriptor array and hardware blocks it describes. It is not persisted, but it encodes address relationships that remain fixed for the ASIC generation.

## Dependencies And Integration Points
Depends on the consumer defining the descriptor type and `GAUDI2_BLOCK_TYPE_*` enum or macros before expansion. Integrates with Gaudi2 security/protection-block code, hardware block iteration, diagnostics, and any logic that maps an address back to a functional block.

## Risks And Edge Cases
The initializer is positional and untyped at the macro boundary, so descriptor field order must match the consumer exactly. Wrong counts or strides can omit replicated blocks or cover the wrong MMIO range. Generated topology includes nonuniform sections, zero-stride entries, and multi-dimensional patterns; consumers must not assume a simple flat stride for every block type.

## Test Signals
Signals include block enumeration counts matching expected Gaudi2 topology, protection/security setup covering all intended MMIO ranges, address-to-block classification tests, and diagnostics that can visit representative TPC, MME, DMA, HBM, NIC, and PSOC blocks without invalid MMIO access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_special_blocks.h -->
