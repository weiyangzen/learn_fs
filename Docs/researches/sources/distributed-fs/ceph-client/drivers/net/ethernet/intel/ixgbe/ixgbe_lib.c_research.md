# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_lib.c

## Purpose

`ixgbe_lib.c` provides core ixgbe queue topology, ring-to-register mapping, interrupt-vector allocation, q_vector lifetime, and advanced Tx context descriptor emission. It is the central setup/teardown helper used by probe, reset, DCB reconfiguration, FCoE enable/disable, SR-IOV changes, and transmit offload paths.

## Important APIs and Functions

The public functions are `ixgbe_init_interrupt_scheme()`, `ixgbe_clear_interrupt_scheme()`, and `ixgbe_tx_ctxtdesc()`. Queue topology helpers include `ixgbe_set_num_queues()` with feature-specific branches for DCB+SR-IOV, DCB, SR-IOV, and RSS. Ring register mapping mirrors that order via `ixgbe_cache_ring_register()`, `ixgbe_cache_ring_dcb_sriov()`, `ixgbe_cache_ring_dcb()`, `ixgbe_cache_ring_sriov()`, and `ixgbe_cache_ring_rss()`. Interrupt helpers include `ixgbe_acquire_msix_vectors()`, `ixgbe_set_interrupt_capability()`, and `ixgbe_reset_interrupt_capability()`. q_vector helpers include `ixgbe_alloc_q_vector()`, `ixgbe_alloc_q_vectors()`, `ixgbe_free_q_vector()`, and `ixgbe_free_q_vectors()`.

## Control Flow

`ixgbe_init_interrupt_scheme()` first computes queue counts from enabled features, then chooses interrupt mode, allocates q_vectors/rings, caches ring register indices, logs queue counts, and marks the adapter down. Queue selection starts from a single queue and tries the most complex enabled combinations first. DCB+SR-IOV and DCB paths size pools/traffic classes, disable RSS or ATR where incompatible, and map netdev traffic classes. SR-IOV sizes VMDq pools and per-pool RSS queues, adjusts FCoE queue sharing/reservation, disables ATR, and constrains netdev traffic classes for macvlan offload. RSS is the base multiqueue path, optionally enabling Flow Director hash capability when ATR sampling is active and reserving FCoE queues near the end of the ring array.

Interrupt setup tries MSI-X first. Requested vectors are based on max Rx/Tx/XDP queues, capped by online CPUs and hardware maximum, plus non-queue vectors. If MSI-X allocation fails, the driver disables or reduces features that require multiple vectors: DCB, SR-IOV, RSS, and related DCB state. It recalculates queues, sets one q_vector, and attempts MSI before falling back to legacy interrupts.

`ixgbe_alloc_q_vectors()` distributes Rx, Tx, and XDP rings across q_vectors. When enough vectors exist, Rx-only vectors are allocated first; remaining vectors get balanced ring counts via `DIV_ROUND_UP`. `ixgbe_alloc_q_vector()` allocates NUMA-local q_vector memory, initializes NAPI, adaptive interrupt moderation values, ring containers, ring indices, XDP locks, FCoE ring state, and the 82599 UDP zero checksum workaround. Freeing deletes NAPI and uses `kfree_rcu()` so stats readers cannot use freed rings immediately after NAPI deletion.

`ixgbe_tx_ctxtdesc()` writes an advanced context descriptor at `next_to_use`, wraps the ring index, sets descriptor extension/context type bits, and stores VLAN/MAC/IP lengths, FCoE EOF or IPsec SA index field, type/TU command flags, and MSS/L4 length fields.

## State and Persistence Behavior

All state is runtime adapter state. The file mutates queue counts, pool counts, `ring_feature[]` indices/masks/offsets, feature flags such as MSI-X/MSI/FDIR/SR-IOV/DCB, q_vector pointers, ring arrays, NAPI instances, and netdev traffic-class mappings. No state persists across driver unload, but these decisions affect hardware register programming after reset and the visible number of netdev queues.

## Dependencies and Integration Points

The file depends on `ixgbe.h`, `ixgbe_sriov.h`, PCI MSI/MSI-X APIs, NAPI, NUMA allocation, CPU masks, DCB config, XDP rings, FCoE feature hooks, Flow Director/ATR flags, and ixgbe descriptor definitions. It is called from `ixgbe_main.c` probe/open/reset paths, DCB netlink reconfiguration, and FCoE enable/disable paths. Tx context descriptors are consumed by TSO/checksum, IPsec, and FCoE transmit paths.

## Risks and Test Signals

Queue topology is high-risk because off-by-one masks or offsets can map rings to the wrong hardware queue, especially with DCB, SR-IOV, and FCoE combined. MSI-X fallback deliberately disables features; tests must verify state is fully consistent after partial vector allocation failure. q_vector allocation must handle NUMA fallback and unwind without stale ring pointers. `kfree_rcu()` is important for stats/NAPI lifetime safety. XDP queues are stacked with Tx queues and need distinct indexing. Test signals include probe under varying CPU counts, forced MSI-X allocation failure, DCB TC changes, SR-IOV enable/disable, FCoE queue reservation, XDP attach/detach, reset/reinit loops, Tx descriptor validation for TSO/IPsec/FCoE, and static checks for ring array bounds.
