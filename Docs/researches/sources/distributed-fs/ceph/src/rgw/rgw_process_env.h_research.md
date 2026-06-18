# sources/distributed-fs/ceph/src/rgw/rgw_process_env.h

## Purpose
`rgw_process_env.h` defines the shared runtime dependency bundle passed into RGW request processing and frontends.

## Important APIs, Types, And Functions
`RGWLuaProcessEnv` stores Lua background and a SAL Lua manager. `RGWProcessEnv` stores pointers/owners for config store, SAL driver, site config, REST dispatcher, ops log sink, auth strategy registry, active rate limiter, KMS cache, and optional Arrow Flight server/store.

## Control Flow
There are no methods. `process_request()` and operation code read dependencies from `req_state::penv`, which references this structure.

## State And Persistence
The struct owns some services via `std::unique_ptr` and references others by raw pointer. It is process-lifetime state, not serialized metadata.

## Dependencies And Integration Points
It connects request processing to auth, Lua, KMS, ratelimiting, REST, config store, SAL driver, site config, ops logging, dedup background declarations, and optional Arrow Flight integration.

## Risks And Test Signals
Risks include raw pointer lifetime, partially initialized environments, optional feature fields, and config reload replacement semantics. Tests should construct minimal process environments for request tests and verify null handling or required-field assumptions.
