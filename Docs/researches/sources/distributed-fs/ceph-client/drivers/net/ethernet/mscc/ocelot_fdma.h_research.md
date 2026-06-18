# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_fdma.h

## Purpose
Defines FDMA registers, descriptor bits, ring sizes, buffer sizing, the FDMA static key, data structures, and function prototypes for DMA-based Ocelot extraction/injection.

## Important APIs/types/functions
Defines DCB status fields for block offset/length, processed-done, abort, SOF, and EOF; channel registers for LLP, safe, activate, disable, errors, and interrupts; channel IDs `MSCC_FDMA_XTR_CHAN` and `MSCC_FDMA_INJ_CHAN`; and ring sizes of 512 RX and 128 TX descriptors. Key structs are `ocelot_fdma_dcb`, TX/RX buffer and ring structs, and `struct ocelot_fdma`.

## Control flow, state, persistence
No executable flow. It describes ownership: TX descriptors own SKBs and mappings until cleanup; RX descriptors own page halves until packet assembly reuses or unmaps them. `ocelot_fdma_enabled` lets the netdev path cheaply select FDMA only when initialized.

## Dependencies and integration
Includes `ocelot.h` and is consumed by `ocelot_fdma.c` and `ocelot_net.c`.

## Risks and test signals
Important invariants are descriptor alignment, coherent allocation size, one-free-slot ring accounting, and RX buffer sizing around IFH/FCS/SKB shared info. Test by compiling all FDMA users and exercising DMA traffic, page reuse, and static-key routing.
