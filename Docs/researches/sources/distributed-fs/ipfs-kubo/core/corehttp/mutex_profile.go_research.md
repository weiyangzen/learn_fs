# sources/distributed-fs/ipfs-kubo/core/corehttp/mutex_profile.go

## Purpose
Adds API endpoints for changing Go runtime mutex and block profiling rates at runtime.

## Important APIs, Types, and Functions
Exports `MutexFractionOption` and `BlockProfileRateOption`, each registering a POST-only handler that parses form values and calls `runtime.SetMutexProfileFraction` or `runtime.SetBlockProfileRate`.

## Control Flow and State
Handlers reject non-POST requests, parse form data, require `fraction` or `rate`, convert it to an integer, log the change, and mutate global runtime profiling state. No persistent repo state is touched.

## Dependencies and Integration Points
Depends on Go `runtime`, net/http, Kubo logging, and the serve option pattern. It is intended for debugging endpoints mounted by daemon/API configuration.

## Risks and Test Signals
Risks include exposing expensive profiling toggles without adequate API binding controls, accepting negative values according to runtime semantics, and global side effects across all handlers. Tests should cover method rejection, missing/invalid parameters, and successful runtime setting changes.
