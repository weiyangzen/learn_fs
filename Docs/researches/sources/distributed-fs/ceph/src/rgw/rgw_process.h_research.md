# sources/distributed-fs/ceph/src/rgw/rgw_process.h

## Purpose
`rgw_process.h` declares the RGW process abstraction, work queue, load generator process, and request-processing entry points.

## Important APIs, Types, And Functions
`RGWProcess` owns `CephContext`, `RGWProcessEnv`, thread pool, request throttle, frontend config, socket fd, URI prefix, and nested `RGWWQ`. It exposes `run()`, `handle_request()`, `pause()`, `unpause_with_new_config()`, and `close_fd()`. `RGWProcessControlThread` runs a process. `RGWLoadGenProcess` generates loadgen requests. Free functions `process_request()` and `rgw_process_authenticated()` expose the main pipeline.

## Control Flow
Concrete frontends subclass `RGWProcess` and enqueue requests into `RGWWQ`; worker threads call `handle_request()`, which typically calls `process_request()`. Pause/unpause controls the thread pool during config reload.

## State And Persistence
The class stores only runtime process state. Persistence occurs through operations invoked by `process_request()`, not the process wrapper itself.

## Dependencies And Integration Points
It depends on work queues, throttle, REST, ACL/user types, frontend config, dmclock scheduler, client I/O, and `RGWProcessEnv`. All RGW frontends use this interface to normalize request execution.

## Risks And Test Signals
Risks include throttle sizing, socket lifetime, pause/unpause interaction with live requests, queue ownership, and virtual `handle_request()` correctness in each frontend. Tests should cover queue operations, close fd idempotence, loadgen request generation, frontend-specific subclasses, and `process_request()` integration.
