# sources/distributed-fs/ceph/src/rgw/rgw_process.cc

## Purpose
`rgw_process.cc` implements RGW request queue processing and the main authenticated request pipeline. It ties frontend I/O, REST handler selection, authentication, authorization, OPA, Lua hooks, dmclock scheduling, rate limiting, tracing, logging, bucket logging, and operation execution together.

## Important APIs, Types, And Functions
`RGWProcess::RGWWQ` implements enqueue/dequeue/process for the thread pool. `schedule_request()` integrates dmclock. `rate_limit()` checks global, user, anonymous, and bucket rate-limit settings. `rgw_process_authenticated()` runs the post-auth operation pipeline. `process_request()` handles the full request lifecycle from client I/O init to cleanup and logging.

## Control Flow
`process_request()` initializes client I/O, creates `req_state`, sets user and ids, gets a REST handler/op, schedules through dmclock, verifies requester, transforms legacy auth if needed, runs `postauth_init()`, rejects suspended users, executes pre-request Lua, starts tracing, and delegates to `rgw_process_authenticated()`. That function initializes permissions, retargets, reads permissions, initializes op/quota, checks op mask, optionally calls OPA, verifies permissions and params, runs `pre_exec()`, checks rate limits, runs post-auth Lua, executes the op, and completes the response. The done path runs post-request Lua, completes client I/O, logs ops and bucket logs, records tracing attrs, returns status, and releases handler/op.

## State And Persistence
Request state is transient but may trigger persistent effects through operations, rate-limit token accounting, user attr reads for STS users, ops logs, bucket logs, and Lua side effects. Perf counters track request count, queue length, and active queue count.

## Dependencies And Integration Points
This file depends on auth registry, REST handlers, RGW operations, OPA, perf counters, Lua, tracing, ratelimit, bucket logging, dmclock scheduler, frontend I/O, and SAL driver/user/bucket/object abstractions.

## Risks And Test Signals
Risks include goto cleanup correctness, null identity assumptions, OPA ordering versus native permissions, Lua failure policy, rate-limit token giveback, queue counter underflow on exceptions, health-check bypasses, and trace/log consistency on early abort. Tests should cover successful and aborted requests, auth failures, suspended users, OPA allow/deny, pre/post Lua deny and failure, dmclock `-EAGAIN`, user/bucket/anonymous rate limits, STS attr reads, health checks, and client I/O completion exceptions.
