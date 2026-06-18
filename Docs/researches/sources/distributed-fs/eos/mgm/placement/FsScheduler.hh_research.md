<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FsScheduler.hh -->
# sources/distributed-fs/eos/mgm/placement/FsScheduler.hh

Source read size: 99 lines, 4129 bytes.

## Purpose

Declares the EOS filesystem scheduler facade and its cluster-manager provider interface.

## Important APIs, Types, and Functions

Defines `ClusterMapT`, abstract `ClusterMgrHandler`, concrete `EosClusterMgrHandler`, and `FSScheduler` with scheduling, access, cluster update, disk status/weight mutation, strategy configuration, state dump, and running-state APIs.

## Control Flow

The header fixes the dependency-injection point: tests or alternate providers can supply a custom `ClusterMgrHandler`, while the default constructor uses `EosClusterMgrHandler`. The private `get_cluster_mgr` looks up space-specific state from the RCU map.

## State and Persistence Behavior

State fields are `mIsRunning`, `scheduler`, `cluster_handler`, RCU-protected `cluster_mgr_map`, atomic `placement_strategy`, RCU-protected `space_strategy_map`, and `cluster_rcu_mutex`.

## Dependencies and Integration Points

Used by MGM file placement/open paths and admin diagnostics. Depends on `ClusterMap` and `FlatScheduler`.

## Risks and Edge Cases

The API allows scheduling before `updateClusterData`, which returns empty/error results. Strategy reads and map reads share the same RCU mutex, so writers must avoid long critical sections.

## Test Signals

Mock handler tests for constructor injection, cluster update, scheduling/access before and after initialization, disk mutation APIs, strategy override visibility, and state string behavior for missing spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FsScheduler.hh -->
