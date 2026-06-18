<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_ratelimit.h -->
# sources/distributed-fs/ceph-client/include/net/net_ratelimit.h

## Purpose
`net_ratelimit.h` declares the global network ratelimit state shared by networking log sites.

## Important APIs, types, and functions
It exposes `extern struct ratelimit_state net_ratelimit_state` after including `<linux/ratelimit.h>`.

## Control flow
Callers pass the global state to ratelimit helpers when logging repeated network events.

## State and persistence
The state object is defined elsewhere and tracks ratelimit counters/timing globally for networking.

## Dependencies and integration points
It depends on kernel ratelimit infrastructure and integrates with net logging call sites.

## Risks and test signals
Risks are global suppression hiding per-device bursts and callers forgetting ratelimit checks. Tests should exercise repeated warnings and ratelimit reset behavior.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_ratelimit.h` completely for this pass (9 lines, 220 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_ratelimit.h -->
