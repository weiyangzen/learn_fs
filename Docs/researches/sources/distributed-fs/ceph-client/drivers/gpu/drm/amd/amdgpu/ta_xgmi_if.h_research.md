# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_xgmi_if.h

## Purpose

`ta_xgmi_if.h` defines the shared-memory ABI for the XGMI trusted application. It lets the driver initialize XGMI topology state, obtain local node and hive IDs, get/set topology information, and query peer link counts or extended peer port mappings.

## Important APIs, Types, And Functions

Commands include initialize, get node ID, get hive ID, get/set topology info, get peer links, and get extended peer links. Constants define up to 64 connected nodes, 32 internal state entries, 128 internal-state buffer entries, and 8 ports per peer. `struct ta_xgmi_node_info` records node ID, hop count, sharing state, and assigned SDMA engine. Peer link structures support simple link counts and extended source/destination port pairs. `struct ta_xgmi_shared_memory` includes command/response IDs, status, pagination flag for extended link records, capability flags, and command input/output unions.

## Control Flow, State, And Dependencies

The driver initializes the TA, queries IDs, sends or receives topology arrays, and may paginate extended link records by toggling `flag_extend_link_record`. State persists in TA topology/session state, XGMI hive configuration, peer sharing flags, SDMA engine assignment, and firmware capability flags. The ABI integrates with AMDGPU XGMI and PSP TA services.

## Risks And Test Signals

Risks include exceeding fixed node/port limits, partial extended-link pagination, confusing peer link formats with and without port numbers, signed SDMA engine enum handling, and stale topology state after hot reset. Tests should cover initialize, node/hive ID retrieval, valid and invalid topology arrays, sharing enablement, simple and extended peer link queries, pagination for more than 128 link records, and TA status error handling.
