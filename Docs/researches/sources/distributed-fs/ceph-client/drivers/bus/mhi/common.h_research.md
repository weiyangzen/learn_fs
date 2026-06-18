# sources/distributed-fs/ceph-client/drivers/bus/mhi/common.h

Purpose: shared MHI protocol register, bitfield, ring-element, context, command, event, and state definitions used by host and endpoint code. It is the local protocol contract for MHI MMIO, BHI/BHIE boot interfaces, command/event TRE encoding, channel/event/command contexts, and state stringification.

Important APIs and types: defines MHI/BHI/BHIE register offsets and masks, TRE helper macros for command, event, data, and RSC descriptors, `enum mhi_pkt_type`, `enum mhi_ev_ccs`, `enum mhi_ch_state`, `enum mhi_cmd_type`, `struct mhi_event_ctxt`, `struct mhi_chan_ctxt`, `struct mhi_cmd_ctxt`, `struct mhi_ring_element`, and inline `mhi_state_str()`.

Control flow role: no executable flow besides the state-string switch, but the macros drive all ring encoding/decoding and context parsing in MHI host and endpoint. Consumers use endian helpers to produce or interpret host-visible descriptors.

State and persistence: describes MMIO registers and host/device shared memory layouts. The structures point to ring base/length/read/write pointers that persist in DMA-coherent shared memory while the controller is active.

Dependencies and integration: depends on `linux/bitfield.h` and public `linux/mhi.h`. It is included by endpoint internals and host boot/debugfs internals.

Risks: bitfield or endian mistakes corrupt cross-host/device protocol state. The RSC pointer macro uses high-bit length packing and must match the MHI spec. Test signals include descriptor round trips, ring context dumps, state string output, host firmware boot, endpoint channel transfers, and sparse/build checks for packed/aligned context fields.
