# sources/distributed-fs/ceph/src/mon/HealthMonitor.cc

## Purpose
`HealthMonitor.cc` aggregates cluster health checks from all monitor Paxos services, persists monitor-local and leader-derived health state, handles health mute commands, and renders health status.

## Important APIs, Types, and Functions
Core methods include `update_from_paxos`, `encode_pending`, `preprocess_query`, `prepare_update`, `prepare_command`, `prepare_health_checks`, `tick`, `check_member_health`, `check_leader_health`, `check_mutes`, `gather_all_health_checks`, and `get_health_status`. Leader-specific checks cover mon down, netsplit, clock skew, msgr2, colocated monitors, older versions, stretch-mode CRUSH locations, and EC profiles.

## Control Flow
Each active monitor builds local member health on tick. Peons send `MMonHealthChecks`; leaders merge those into `quorum_checks`, add leader checks, expire or adjust mutes, and propose on change. `health mute` and `health unmute` mutate `pending_mutes` and reply after commit.

## State and Persistence
Paxos stores `quorum_checks`, `leader_checks`, `mutes`, and the combined encoded health map. Pending/current netsplit maps are runtime grace-period state and reset on restart.

## Dependencies and Integration Points
It reads `Monitor`, `MonMap`, `OSDMonitor`, `OSDMap`, CRUSH topology, election netsplit tracking, monitor store stats, session map auth status, config, and health maps from all Paxos services.

## Risks
Leader synthesis depends on timely peon reports. Netsplit detection depends on topology data and grace periods. Non-sticky mutes clear on count increase, summary change, or alert disappearance, so alert wording changes can unmute.

## Test Signals
Cover member disk/auth warnings, peon reports, quorum pruning, mute TTL/count/summary/sticky behavior, output formatting, older-version delay, mon-down grace, clock skew, msgr2/stretch/netsplit/EC checks.
