# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd.h

## Purpose
This private EFALND header defines module constants, core runtime structures, state enums, inline helpers, and cross-file function prototypes for the EFA LNet driver.

## Important APIs, Types, And Functions
Important constants include EFALND version numbers, MTU/message sizes, TX pool and fragment limits, scheduler thread defaults, static small-NID CM QKEY, RDMA threshold, connection hash bits, invalid connection marker, maximum peer QPs, and large-NID field offsets. Main structures are `kefa_data`, `kefa_tunables`, `kefa_peer_ni`, `kefa_obj_pool`, `kefa_rx`, `kefa_qp`, `kefa_cq`, `kefa_fmr`, `kefa_dev`, `kefa_tx`, `kefa_ni`, `kefa_conn`, `kefa_cm_deamon`, and `kefa_sched`. Enums describe init state, FMR state, connection state, and connection type. Inline helpers build/extract large NIDs, compute LND version, stop threads, and set message epoch.

## Control Flow
The header is the shared contract between main transport, connection handling, peer metadata, modparams, and debugfs. Runtime flow is represented by state fields: FMRs move inactive/activating/active/deactivating, connections move inactive through TCP/EFA probe, establishment, active, and deactivating, and TXs carry refs and optional sync-completion state.

## State, Persistence, And Dependencies
All structures are in-memory kernel state. The large-NID layout is an inter-node protocol/address contract: bytes 0-1 store CM QP number, 2-3 store QKEY, and 4-15 store the nonconstant EFA GID suffix. The header depends on libcfs, LNet library internals, LNet RDMA helpers, Linux rhashtable/list/spin/kref APIs, and `efa_verbs.h`.

## Integration Points
Every EFALND C file includes this header. It also bridges to LNet `struct lnet_ni`, `struct lnet_msg`, `struct lnet_nid`, ioctl EFALND tunables, and protocol structures from `efalnd_proto.h`.

## Risks
Structure fields are highly coupled to completion handlers and cleanup code; changing list ownership, ref counters, or state enums can introduce races. The large-NID helper assumes the first four GID bytes are constant and reconstructs them as `fe80::`, which must match EFA behavior. `peer_ni_params` keys only `remote_nid_addr`, so small-NID uniqueness depends on the generated address scheme.

## Test Signals
Tests should compile all EFALND files against this header, validate large-NID create/extract round trips, exercise connection and FMR state transitions, run lock/refcount checking on peer-NI and TX lifetimes, and verify version/protocol constants match wire compatibility expectations.
