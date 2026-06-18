## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ring.h

Purpose: defines v2 DMA descriptor count/size, descriptor bitfields, DMA control/status registers, and descriptor helper prototypes.

Important APIs, types, and functions: constants include descriptor count, descriptor size, buffer count, empty-slot marker, `DMATX/RXDESCL/H`, `DMATX/RXCTRL`, `DMATX/RXSTATUS`, and fields such as `E`, `PKT_ADDRL/H`, `PKT_SIZE`, `NEXT_DESC_ADDRL/H`, `D`, `TXPKTCOUNT`, and `RXPKTCOUNT`. `struct xge_raw_desc` represents descriptor words `m0` through `m2`. Macros `GET_BITS` and `SET_BITS` pack/unpack fields. It declares descriptor setup and address update helpers.

Control flow, state, and dependencies: included by `main.h` and used by TX/RX/refill paths in `main.c` and setup in `ring.c`.

Integration points: hardware descriptor format and CSR definitions must match the v2 linked-list DMA engine.

Risks: field position/length errors directly affect DMA addresses, ownership bits, packet lengths, and interrupt/status accounting. `SET_BITS` truncates through masks, so callers must pass correct width values.

Test signals: DMA to/from high addresses, descriptor wraparound, packet length correctness, RX error bit handling, and TX/RX status count acknowledgement.
