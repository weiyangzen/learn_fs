# sources/distributed-fs/coda/coda-src/vicedep/srv.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/srv.h` is the main private/public server dependency header for Coda file-server modules. It defines core server macros, client and host connection structures, operation counters, timing helpers, and cross-module prototypes for volume, vnode, callback, RPC, and resolution services.

## Important APIs, Types, and Functions

Key macros include `ThisHostAddr`, `VolToHostAddr`, `VolToServerId`, `ISDIR`, `VSLEEP`, `STREQ`, `STRNEQ`, `SetAccessList`, operation counter aliases, data-size buckets, `START_TIMING`, and `END_TIMING`. Types include `HostTable` and `ClientEntry`. It declares server globals (`HostAddress`, `ThisServerId`, `SystemId`, `AnyUserId`, `SrvDebugLevel`, `StartTime`, `CurrentConnections`, `Authenticate`, `Counters`, `NullFid`, `MaxVols`, `CodaSrvIp`, etc.) and many APIs from codaproc, codaproc2, srv, srvproc2, vicecb, resolution, lookaside, coppend, and volutil.

## Control Flow

There is no executable control flow, but the macros shape runtime flow: `SetAccessList` asserts directory vnodes before returning ACL storage, timing macros wrap operations under `CODA_DEBUG`, and counter IDs are used by RPC dispatch/statistics paths. The declared functions define the flow between RPC handlers, volume/vnode acquisition, version-vector updates, callback breaks, and resolution support.

## State and Persistence Behavior

The header declares in-memory server connection structures and globals. Persistent state is accessed through declared volume/vnode helpers rather than stored in this header. `HostTable` tracks callback connection handles, host address/port, activity timestamps, and synchronization lock; `ClientEntry` tracks RPC connection, CPS/authentication, user id, side-effect type, last op, unbind state, username, and token expiration.

## Dependencies and Integration Points

It integrates RPC2, LWP locks, PRS/auth, Coda wire types, vnode/volume types, and deprecation annotations. Most Coda server translation units include it to share connection structures, counters, callbacks, resolution hooks, and object-management APIs.

## Risks and Edge Cases

Global mutable state and macros make coupling tight. `SetAccessList` assumes a directory vnode and asserts otherwise, so callers must fetch the correct parent/target object. Operation counter aliases depend on generated `srvOPARRAYSIZE` and RPC opcode names. `HostAddress` is marked single-homing-sensitive. `ClientEntry` stores fixed-size usernames and timestamps; connection cleanup must hold the `HostTable` lock consistently.

## Test Signals

Compile all server modules after generated RPC headers are refreshed; run connection lifecycle and callback tests that exercise `HostTable` locking; verify statistics counters map to expected opcodes; test ACL callers with non-directory objects to confirm semantic checks prevent macro assertion paths.
