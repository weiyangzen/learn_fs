# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_rx.h

Purpose: Declares the receive-side data formats and state containers for the Octeon EP VF driver. It documents the hardware output queue descriptor format, hardware response headers, receive offload bits, per-buffer bookkeeping, per-queue stats, interface stats, and the software output queue object.

Important APIs/types/functions: `struct octep_vf_oq_desc_hw` is the 16-byte hardware descriptor containing a DMA buffer pointer and currently unused info pointer. `struct octep_vf_oq_resp_hw` is the big-endian 8-byte length header written at the start of each received buffer. `struct octep_vf_oq_resp_hw_ext` carries optional firmware checksum/offload flags. `struct octep_vf_rx_buffer` tracks the backing page and decoded length. `struct octep_vf_oq_stats`, `struct octep_vf_iface_rx_stats`, and `struct octep_vf_oq` hold stats and queue state. Macros define descriptor/response sizes and checksum/offload flag tests.

Control flow and integration: `octep_vf_rx.c` uses these structures to allocate coherent descriptor rings, DMA-map pages into descriptors, parse hardware response headers, manage host read/refill indices, and update stats. The main driver and ethtool paths consume stats structures. Firmware capability bits decide whether the extended response header is present.

State and persistence: `struct octep_vf_oq` is the persistent runtime object for an Rx queue while the network device is open. It links software indices, stats, descriptor memory, DMA addresses, register pointers, NAPI context, and queue configuration. The hardware descriptor and response structs define shared-memory state exchanged through DMA.

Dependencies: Requires Linux DMA, page, NAPI, and networking types supplied by surrounding includes. The `static_assert()` checks bind C layout to the hardware ABI.

Risks: Bitfield and structure layout must match hardware and compiler expectations; the static size checks help but cannot validate endian interpretation or bit ordering. `max_single_buffer_size` depends on response header sizes matching firmware. Misinterpreted checksum flags could mark corrupt packets as valid.

Test signals: Compile-time structure size assertions, Rx with and without firmware offload header support, checksum-offload validation, jumbo frame fragmentation, and ethtool/stat reads are the strongest coverage points.
