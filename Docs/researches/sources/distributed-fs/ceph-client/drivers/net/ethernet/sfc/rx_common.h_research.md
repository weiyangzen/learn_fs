# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/rx_common.h

Purpose: this header declares shared RX queue, buffer, GRO, RSS, filter, and RFS helpers used by NIC-specific receive code and the generic RX datapath.

Important APIs: constants define preferred refill batch size, maximum fragments per packet, and 10G recycle ring sizing. Inline helpers compute RX buffer virtual addresses, read packet hash values from RX prefixes with aligned or bytewise access, and sync DMA for CPU access. Declarations cover slow fill, page recycling/discard, RX queue lifecycle, buffer initialization/unmapping/freeing, page split config, fast descriptor push, GRO delivery, RSS context/default table helpers, filter spec helpers, optional RFS functions, and filter table probe/remove.

Control flow and integration: NIC-specific event/RX code calls these helpers when completions arrive or descriptors need refill. `rx.c` uses GRO and buffer helpers for delivery. Filter and RSS code use the common hash/equality/context functions.

State and risks: the header itself owns no state, but functions operate on `struct efx_rx_queue`, `struct efx_channel`, and `struct efx_nic` fields defined in `net_driver.h`. Risks include callers forgetting required serialization for refill, using hash offsets without a valid prefix, or calling RFS helpers without the feature enabled. Test signals include compile coverage with and without `CONFIG_RFS_ACCEL`, RX traffic, RSS hash reporting, descriptor refill, and XDP/GRO paths.
