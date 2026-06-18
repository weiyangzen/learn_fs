# sources/distributed-fs/eos/mgm/groupbalancer/GroupsInfoFetcher.hh

## Purpose
Declares the injectable interface and EOS implementation for building `group_size_map` snapshots consumed by balancer engines.

## Important APIs, types, and functions
`IGroupsInfoFetcher` exposes `fetch()`. `OnGroupStatusFilter` accepts only `GroupStatus::ON`. `eosGroupsInfoFetcher` stores a space name, type-erased callable status filter, and `do_average` flag. Templated constructors accept any callable taking `GroupStatus`; `should_average()` controls aggregation mode.

## Control flow
Production code instantiates the fetcher with a space name and optional status predicate. Tests can replace the fetcher through the interface or use custom predicates to include drain groups.

## State and persistence
Only transient configuration is stored: `spaceName`, `status_filter_fn`, and `do_average`.

## Dependencies and integration points
Depends on `BalancerEngineTypes.hh`, C++ memory utilities, and `FsView` in the implementation. `GroupBalancer` uses the default ON filter; `GroupDrainer` supplies a DRAIN-or-ON predicate.

## Risks and test signals
The type-erased filter owns arbitrary callable state, so move-only/lifetime cases deserve coverage. Tests should verify default filtering, lambda filtering, toggling `should_average()`, and interface substitution.
