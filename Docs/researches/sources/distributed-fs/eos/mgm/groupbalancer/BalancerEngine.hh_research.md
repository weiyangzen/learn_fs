# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngine.hh

## Purpose
Declares the group balancer engine interface and the reusable base class for engines that classify filesystem groups as sources or targets for balancing transfers.

## Important APIs, types, and functions
`IBalancerEngine` defines the virtual contract: `recalculate()`, `clear()`, `updateGroup()`, `updateGroups()`, transfer-pair picking, `configure()`, `get_group_sizes()`, and status rendering. `BalancerEngineData` groups the over-threshold set, under-threshold set, and group-size map. `BalancerEngine` implements common population, clearing, status, random/round-robin picking, `canPick()`, `sourceGroupCount()`, `targetGroupCount()`, and exposes `get_data()` for tests. Derived classes are expected to implement policy-specific recalculation, single-group classification, and configuration.

## Control flow
A concrete engine is configured, populated with group sizes, recalculates its threshold model, classifies groups, and then callers repeatedly ask for transfer pairs. The base class owns state transitions around complete refreshes and pair selection; subclasses only decide whether a specific group belongs in `mGroupsOverThreshold`, `mGroupsUnderThreshold`, or neither.

## State and persistence
The header defines only in-memory state. `mGroupSizes` stores the latest snapshot, while threshold sets store derived source/target classifications. `get_data()` intentionally exposes this state for unit tests and validation, not for persistence.

## Dependencies and integration points
Depends on STL maps/sets/random-related headers and `BalancerEngineTypes.hh`. It is consumed by concrete engines and factory code, and by higher-level group balancer orchestration that fetches group sizes, configures engines, invokes `pickGroupsforTransfer()`, and schedules actual transfers.

## Risks and test signals
Because `IBalancerEngine` has no virtual `populateGroupsInfo()` despite the base class providing it, callers that store only an interface pointer cannot use that helper unless they downcast or know the concrete base. The base class is abstract only because `recalculate()`, `updateGroup()`, and `configure()` remain pure; tests should instantiate concrete engines. Test signals include lifecycle sequencing (`clear`, populate, recalculate, update), `canPick()` semantics, source/target count consistency, and ensuring subclasses call `clear_threshold(group_name)` before reclassifying an individual group.
