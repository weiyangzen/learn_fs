<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_rss.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_rss.h

Purpose: defines Receive Side Scaling parameter storage shared by NIC configuration and hardware RSS programming.

Important APIs/types: `struct aq_rss_parameters` stores base CPU number, indirection table size, hash secret key size, the 40-byte hash key as `u32` words, and the maximum 64-entry indirection table.

Control flow: `aq_nic_rss_init` fills this structure with the default Toeplitz-style key and queue indirection based on vector count. A0/B0 hardware ops consume it in `hw_rss_set` and `hw_rss_hash_set` to program RSS redirection and hash-key registers.

State and persistence: stored inside `aq_nic_cfg_s`; it persists only for the lifetime of the NIC instance and is reprogrammed during init/reconfiguration.

Dependencies and integration: includes `aq_common` and `aq_cfg` for sizes and common hardware constants. It is a small contract between generic queue sizing and chip register programming.

Risks: indirection values assume power-of-two RSS queue counts; size constants must match hardware register packing; changes affect packet distribution and CPU affinity. Test signals include multiqueue RX distribution, RSS disabled fallback, ethtool RSS inspection if wired elsewhere, and vector-count changes from IRQ/CPU constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_rss.h -->
