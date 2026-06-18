## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene/xgene_enet_ring2.h

Purpose: declares X-Gene2 ring configuration constants and the exported ring operation table.

Important APIs, types, and functions: constants define `X2_NUM_RING_CONFIG`, interrupt mailbox size and CSR offset, interrupt clear bit, X-Gene2-specific ring state fields for message/base address mode, interrupt line, config CRID, threshold, ring type, dequeue interrupt enable, recombination timeout, and queue length field. It declares `xgene_ring2_ops`.

Control flow, state, and dependencies: included by `xgene_enet_main.h` and implemented in `xgene_enet_ring2.c`. It carries no live state.

Integration points: selected by `xgene_enet_setup_ops` for X-Gene2 hardware.

Risks: these bitfields determine interrupt delivery and descriptor addressing. Mismatch with `xgene_enet_ring2.c` or hardware docs will cause silent ring hangs.

Test signals: compile X-Gene2 path; verify interrupt mailbox programming and RX/TX activity under traffic.
