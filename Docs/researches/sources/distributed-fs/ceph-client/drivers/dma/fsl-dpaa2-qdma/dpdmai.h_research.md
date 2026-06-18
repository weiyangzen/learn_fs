# sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.h

### Purpose
`dpdmai.h` defines the DPDMAI Management Complex ABI constants and public data structures used by the DPAA2 QDMA driver and `dpdmai.c` command wrapper.

### Important APIs, Types, And Functions
It defines supported DPDMAI version `3.3`, command ID formatting helpers, command IDs, maximum queue and priority counts, queue option bits, and MC command token bit positions. Main types are `struct dpdmai_cfg`, `struct dpdmai_attr`, `enum dpdmai_dest`, `struct dpdmai_dest_cfg`, `struct dpdmai_rx_queue_cfg`, `struct dpdmai_rx_queue_attr`, and `struct dpdmai_tx_queue_attr`. It declares all DPDMAI control and queue APIs implemented in `dpdmai.c`.

### Control Flow, State, And Persistence
The header has no runtime control flow. It establishes the firmware contract used to open a token-bound DPDMAI control session, read immutable object attributes, and configure queue state in MC firmware. Queue attributes persist in the DPDMAI object rather than in the Linux wrapper.

### Dependencies, Integration Points, Risks, And Test Signals
This file depends on FSL MC IO types and fixed-width kernel integer types. It integrates with MC firmware, DPAA2 QDMA setup, DPIO destination programming, and FQID discovery. Risks are firmware ABI mismatch, command-version skew for queue commands, stale supported version constants, and assuming no more than eight queues or two priorities. Test signals include compile coverage for callers, successful DPDMAI open/get-attributes across firmware versions, queue option combinations, and FQID consistency with DPIO notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-dpaa2-qdma/dpdmai.h -->
