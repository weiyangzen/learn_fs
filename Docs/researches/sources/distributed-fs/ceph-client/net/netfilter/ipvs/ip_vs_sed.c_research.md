# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sed.c

## Purpose
Implements the IPVS shortest expected delay scheduler `sed`. It selects the destination minimizing `(active connections + 1) / weight`, modeling the expected delay for the incoming connection.

## Important APIs, Types, and Functions
`ip_vs_sed_dest_overhead()` returns `activeconns + 1`. `ip_vs_sed_schedule()` finds the eligible server with the lowest weighted expected delay using cross multiplication. `ip_vs_sed_scheduler` registers scheduler name `sed`.

## Control Flow
The scheduler first finds an eligible non-overloaded positive-weight destination to seed the comparison, then continues scanning the destination list for a lower expected delay. If no eligible destination exists, it reports an error and returns `NULL`. Module init and exit register/unregister the scheduler and wait for RCU readers.

## State and Persistence
No private scheduler state exists. Decisions derive from current active connection counters and destination weights.

## Dependencies and Integration Points
Uses IPVS destination lists, atomic counters and weights, common scheduler registry, and debug logging. It is closely related to `nq`, but without the immediate idle-server shortcut.

## Risks
It ignores inactive connections entirely. The `+1` incoming-job model can prefer a higher-weight server even when raw active counts are higher. The initial seed path must skip zero-weight and overloaded destinations to avoid divide-by-zero-equivalent comparisons.

## Test Signals
Test weighted expected-delay choices across heterogeneous weights, all-busy versus idle cases, zero-weight quiescing, overload exclusion, and no-destination logs. Compare against `wlc` and `nq` for expected differences.
