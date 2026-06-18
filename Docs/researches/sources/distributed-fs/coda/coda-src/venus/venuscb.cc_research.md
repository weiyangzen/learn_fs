# sources/distributed-fs/coda/coda-src/venus/venuscb.cc

## Purpose
This file implements the Venus callback server subsystem. It exports the callback RPC2 subsystem, starts callback server vprocs, receives callback requests from servers, breaks file/volume callbacks, supports server backfetch of reintegration shadow data, and records callback connection ids.

## Important APIs, Types, and Functions
`CallBackInit()` sets `MaxCBServers`, exports `SUBSYS_CB`, and creates `callbackserver` instances. `callbackserver::main()` loops on `RPC2_GetRequest()`, validates callback connection state, handles bad clients, and dispatches generated callback RPC stubs through `cb_ExecuteRequest()`. `VENUS_CallBack()` handles callback breaks/probes. `VENUS_CallBackFetch()` transfers a shadow file to a server through SMARTFTP. `VENUS_CallBackConnect()` handles new callback connections and marks the server up. Globals include `MaxCBServers` and `cbbreaks`.

## Control Flow
Callback servers block waiting for RPC2 requests. RPC2 connection errors reset the associated server or unbind unknown handles. Normal callback packets are executed by generated callback dispatch. A break callback maps Vice fid plus server realm id to `VenusFid`, logs to mariner, ignores volume-zero probes, breaks FSDB file callbacks and VDB volume callbacks, and increments `cbbreaks` when a file break cannot find the fid. Backfetch finds the fsobj, ensures a shadow exists, verifies file/full-data state, opens the shadow container, initializes/checks SMARTFTP side effect transfer, and accounts transferred bytes on read-write volumes.

## State and Persistence Behavior
The subsystem is transient but invalidates cached persistent filesystem state by breaking callbacks. `VENUS_CallBackFetch()` may create a missing shadow in a recovery transaction, then streams shadow file contents. Callback connection setup updates `srvent` runtime state via `ServerUp()`.

## Dependencies and Integration Points
It depends on RPC2 callback stubs, side-effect transfer, server database lookup by callback cid, FSDB/VDB callback-break methods, fsobj shadow/container APIs, reint volume accounting, mariner logging, and worker/vproc infrastructure.

## Risks and Test Signals
Risks include unauthenticated callback TODOs, unknown callback cid handling, callback break races around newly created files, shadow-file assumptions, SMARTFTP error translation, and server reset/unbind correctness. Tests should cover probe callbacks, file and volume callback breaks, unknown cid replies, backfetch success/failure/no-shadow cases, and callback new-connection updates.
