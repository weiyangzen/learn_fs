<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/rings.c -->
# sources/distributed-fs/ceph-client/net/ethtool/rings.c

## Purpose
Provides ethtool netlink GET and SET support for NIC ring parameters, including legacy pending queue counts and newer kernel-only ring attributes such as RX buffer length, TCP data split, CQE size, TX/RX push, TX push buffer length, and header-data-split thresholds.

## APIs, Types, and Functions
Defines `struct rings_req_info`, `struct rings_reply_data`, `ethnl_rings_get_policy`, `ethnl_rings_set_policy`, and `ethnl_rings_request_ops`. The main functions are `rings_prepare_data()`, `rings_reply_size()`, `rings_fill_reply()`, `ethnl_set_rings_validate()`, and `ethnl_set_rings()`.

## Control Flow, State, and Persistence
GET requires `dev->ethtool_ops->get_ringparam`, snapshots `supported_ring_params`, seeds `kernel_ringparam.tcp_data_split` and `hds_thresh` from `dev->cfg`, calls the driver, and serializes only supported/nonzero maximums plus selected kernel fields. SET first gates each requested attribute against `ops->supported_ring_params`, then reads current ring configuration with `ethtool_ringparam_get_cfg()`, applies netlink updates into local copies, and exits with no notification if nothing changed. Before invoking the driver it rejects TCP data split with single-buffer XDP, rejects disabling TCP data split or setting nonzero HDS threshold while a memory provider is enabled, bounds requested counts against driver maxima, and bounds TX push buffer length. Pending HDS settings are staged in `dev->cfg_pending`, while durable device state is set by `ops->set_ringparam()`.

## Dependencies and Integration
Depends on ethtool core helpers, netdev queue helpers, XDP single-buffer checks, memory-provider channel checks, and driver `get_ringparam`/`set_ringparam` callbacks. The request ops emit `ETHTOOL_MSG_RINGS_NTF` when changes are accepted.

## Risks and Test Signals
Risks include stale maxima if a driver reports inconsistent current configuration, arithmetic mistakes in `rings_reply_size()`, staged `cfg_pending` values when a driver later fails, and cross-feature conflicts around XDP or page-pool memory providers. Test signals include unsupported attribute extacks, max-bound failures, no-op SET returning zero, XDP/HDS conflict rejection, TX push buffer max validation, and notification on successful mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/rings.c -->
