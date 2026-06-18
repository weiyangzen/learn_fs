<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/config.h -->
# sources/distributed-fs/ceph-client/fs/dlm/config.h

Purpose: defines the public internal configuration contract for DLM configfs state and tunables.

Important APIs/types/functions: defines `DLM_MAX_SOCKET_BUFSIZE`, `DLM_MAX_ADDR_COUNT`, protocol constants `DLM_PROTO_TCP` and `DLM_PROTO_SCTP`, `struct dlm_config_node`, `struct dlm_config_info`, external `dlm_rhash_rsb_params`, external global `dlm_config`, and prototypes for config lifecycle and lookup helpers.

Control flow: DLM startup calls `dlm_config_init`; shutdown calls `dlm_config_exit`; membership/recovery code calls `dlm_config_nodes`; communication code calls `dlm_comm_seq`, `dlm_our_nodeid`, and `dlm_our_addr` to derive configured network state.

State and persistence: the header models snapshots of configfs state. `dlm_config_node` carries active/gone/new member data plus comm sequence and recovery release flags. `dlm_config_info` carries cluster-wide tunables including port, buffer size, hash table size, recovery/scanning timers, logging flags, protocol, packet mark, new resource count, callback recovery behavior, and cluster name.

Dependencies and integration: used by DLM config, lockspace, recovery, member, and communication code. It depends on DLM constants for lockspace name length and on socket storage declarations through including translation units.

Risks: fields in `dlm_config_info` are global mutable runtime tunables, so consumers must understand which can change while DLM is running. `dlm_our_nodeid` assumes a local comm has been configured. `dlm_config_nodes` allocates memory for callers to free, so ownership must be clear in callers.

Test signals: compile coverage, configfs membership snapshots, communication address lookup, and transport/timer tunable consumption validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/config.h -->
