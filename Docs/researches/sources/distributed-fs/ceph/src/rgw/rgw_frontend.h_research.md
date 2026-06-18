# sources/distributed-fs/ceph/src/rgw/rgw_frontend.h

## Purpose
Declares the shared RGW frontend abstraction, process frontend base, loadgen frontend, and realm reload pauser.

## Important APIs, Types, And Functions
`RGWFrontendConfig` owns parsed config and retrieval helpers. `RGWFrontend` is the lifecycle interface. `RGWProcessFrontend` owns `RGWProcess`, `RGWProcessEnv`, and a control thread. `RGWLoadGenFrontend` initializes loadgen process credentials. `RGWFrontendPauser` pauses/resumes all frontends during realm reload.

## Control Flow
Concrete frontends call `init()`, `run()`, `stop()`, and `join()` through `RGWFrontend`. `RGWProcessFrontend::run()` starts `RGWProcessControlThread`; pause/resume delegates to the process. Loadgen init reads `num_threads`, `prefix`, and required `uid`, loads the user, selects an access key, and configures the process.

## State And Persistence Behavior
No persistent state. Frontend instances own process/thread pointers and borrowed config/env pointers. Pauser holds references to a frontend vector and optional nested pauser.

## Dependencies And Integration Points
Depends on RGW request/process/process env, realm reloader, auth registry, SAL RADOS, and dmclock forward declarations.

## Risks
Ownership is raw-pointer based in `RGWProcessFrontend`. `join()` assumes `thread` is valid. Loadgen requires a user with an access key and returns errors for missing credentials. Pauser resumes frontends before optional nested pauser, which is an ordering contract worth preserving.

## Test Signals
Tests should cover lifecycle ordering, pause/resume propagation, loadgen missing uid, missing access keys, failed user load, and default config lookup.
