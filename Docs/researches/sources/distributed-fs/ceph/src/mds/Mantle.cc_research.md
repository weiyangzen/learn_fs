# sources/distributed-fs/ceph/src/mds/Mantle.cc

## Purpose
Implements the Lua-backed MDS balancer policy runner. It loads a policy script, exposes local rank and per-rank metrics to Lua, executes the script, and parses returned target weights.

## Important APIs, Types, And Functions
`Mantle::balance` takes a script, local rank, metric vector, and output target map. `Mantle::Mantle` creates a Lua state, opens a limited library set, and registers `BAL_LOG`. `dout_wrapper` bridges Lua logging to Ceph debug logs.

## Control Flow
Each balance call clears the Lua stack, compiles the script, sets global `whoami`, builds global `mds`, executes with one expected return, validates a table return, and copies integer-key/numeric-value pairs into `my_targets`. Errors return `-EINVAL`.

## State And Persistence Behavior
The Lua VM persists for the Mantle object lifetime, but scripts/results are not persisted. Globals are overwritten per call. Caller owns script and target map lifecycle.

## Dependencies And Integration Points
Depends on Lua C API, Ceph logging, rank types, and balancer callers such as MDBalancer that supply metrics and consume target weights.

## Risks
Scripts run inside the MDS process and can consume resources. Output validation does not check rank range, negative weights, or NaN. `my_targets` is not cleared. Metric table indexing uses `lua_seti` with vector indices.

## Test Signals
Valid policy output, compile/runtime errors, malformed returns, malformed key/value pairs, BAL_LOG, repeated calls, multiple metric rows, and caller validation of ranks/weights.
