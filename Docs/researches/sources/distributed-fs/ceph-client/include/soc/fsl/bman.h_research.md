# sources/distributed-fs/ceph-client/include/soc/fsl/bman.h

Purpose: declares Freescale/NXP BMan buffer descriptor encoding and high-level buffer-pool APIs.

Important APIs and types: `struct bm_buffer` wraps a buffer pool ID plus 48-bit DMA address in an aligned 64-bit hardware word. Inline helpers get/set the DMA address or raw 64-bit address and get/set the 8-bit BPID with big-endian conversion. Opaque `struct bman_portal` and `struct bman_pool` represent portal and pool handles. Public APIs allocate/free pools, query BPID, release/acquire 1-8 buffers, and report BMan/portal probe status.

Control flow: drivers allocate a pool, populate `bm_buffer` entries with DMA addresses and BPID, release buffers to the pool through portal rings, acquire buffers from hardware pools, and free pool objects on teardown.

State and persistence: state is runtime hardware pool contents, portal rings, BPID allocation, and pool objects. Buffer ownership moves between drivers and BMan but is not persistent.

Dependencies and integration points: depends on endian/DMA address helpers from kernel headers and integrates DPAA networking/crypto drivers with BMan portals.

Risks and test signals: risks include 48-bit address truncation, BPID high-bit confusion, releasing non-DMA-safe buffers, ring timeout handling, and probe-order races. Test pool allocation exhaustion, acquire/release counts 1-8, high DMA addresses, portal probe states, timeout paths, and driver teardown with buffers in flight.
