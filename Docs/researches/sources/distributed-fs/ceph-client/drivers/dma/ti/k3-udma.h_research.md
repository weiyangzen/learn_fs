# sources/distributed-fs/ceph-client/drivers/dma/ti/k3-udma.h

## Purpose
`k3-udma.h` is the local private header shared by the K3 UDMA provider, its private-export shim, and the glue layer. It defines hardware register offsets, capability-field decoders, runtime control bits, PDMA static TR bitfield helpers, the K3 address-space-select shift, the TISCI resource-manager wrapper structure, resource range identifiers, forward declarations, and the `xudma_*` private API declarations.

## Important APIs, Types, And Constants
The header defines global MMR offsets such as `UDMA_REV_REG`, `UDMA_CAP_REG()`, and RX flow event registers; channel runtime offsets such as `UDMA_CHAN_RT_CTL_REG`, `UDMA_CHAN_RT_PEER_STATIC_TR_XY_REG`, `UDMA_CHAN_RT_PEER_BCNT_REG`, and byte/packet counters; and capability decoders for UDMA, BCDMA, and PKTDMA counts. Runtime control bits include `UDMA_CHAN_RT_CTL_EN`, teardown, pause, flush teardown, error, and peer enable/teardown/pause/flush/idle bits. PDMA helpers define static TR X/Y/Z masks and the ACC32/BURST flags. `K3_ADDRESS_ASEL_SHIFT` defines where PKTDMA/BCDMA ASEL bits are inserted into DMA addresses.

`enum udma_rm_range` names TISCI resource ranges for bchan, tchan, rchan, rflow, and tflow. `struct udma_tisci_rm` groups the TI SCI handle, UDMAP RM ops, DMA controller device id, PSI-L ops, NAVSS device id, and resource range pointers. The declared API covers PSI-L pair/unpair, provider lookup from OF, device/ringacc/TISCI/PSI-L-base accessors, GP RX flow range allocation, tchan/rchan/rflow get/put/id helpers, runtime register read/write helpers, GP-flow classification, PKTDMA detection, and PKTDMA flow IRQ lookup.

## Control Flow
This header does not implement control flow, but it defines the contract used by the implementation. `k3-udma.c` uses the register offsets and bit definitions for runtime channel control, setup, status, and debug. `k3-udma-private.c` implements the declared `xudma_*` functions by delegating into provider internals. `k3-udma-glue.c` consumes those declarations to request resources, program runtime registers, pair PSI-L threads, and convert PKTDMA CPPI5 addresses.

## State And Persistence
The header stores no state. Its declarations describe runtime resources owned by `struct udma_dev`, `struct udma_tchan`, `struct udma_rchan`, and `struct udma_rflow`, all forward-declared here and defined in the provider implementation. The bit definitions directly affect persistent hardware register state when used by callers.

## Dependencies And Integration Points
It includes `linux/soc/ti/ti_sci_protocol.h` for TI SCI types and is consumed by K3 UDMA C files in this directory. It is part of the private source-level boundary between the DMAengine provider and the exported glue API, not a public UAPI header.

## Risks And Edge Cases
Incorrect register offsets or bit masks would affect all K3 UDMA paths. Capability decoders are SoC-specific, so adding new controller variants requires validating the bit layout. ASEL insertion at bit 48 assumes DMA addresses and masks are consistent with the 48-bit coherent mask used in the provider and glue paths. Because private API declarations expose opaque resource types, mismatches between declarations and included implementation can cause subtle ownership bugs.

## Test Signals
Validation comes from build coverage of all C files using the header, probe-time resource counts decoded from capability registers, runtime register writes producing expected channel state, PDMA static TR programming for supported endpoints, ASEL address conversion tests, and private API consumers linking against the expected symbols.
