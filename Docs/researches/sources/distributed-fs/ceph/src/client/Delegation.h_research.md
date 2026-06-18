# sources/distributed-fs/ceph/src/client/Delegation.h

## Purpose
`Delegation.h` declares the client-side delegation container and public delegation constants fallback. Delegations let applications rely on a set of caps until the client recalls them.

## Important APIs, Types, and Functions
The file defines `CEPH_DELEGATION_NONE`, `CEPH_DELEGATION_RD`, and `CEPH_DELEGATION_WR` when the public header has not already done so. `ceph_deleg_caps_for_type()` exposes cap calculation. `Delegation` exposes `get_fh()`, `get_type()`, `is_recalled()`, `is_write_delegated()`, `reinit()`, and `recall()`.

## Control Flow
Instances are owned by `Inode::delegations`. The inode creates them for successful delegation requests, invokes `recall()` on conflicting activity, and erases them on unset. The private timer helpers are used by `recall()` and the destructor.

## State and Persistence Behavior
The class stores only volatile process state: `Fh*`, callback private pointer, type, recall callback, recall time, and timeout event pointer. The associated cap refs are managed in the implementation and reflected in inode cap state.

## Dependencies and Integration Points
It depends on Ceph time/timer context and `ceph_ll_client.h` for callback and delegation command ABI. `Inode` and `Client` provide ownership and timer/cap integration.

## Risks and Edge Cases
The file does not own `Fh`; callers must ensure the file handle outlives the delegation. Callback and timeout lifetimes are tightly coupled. Tests should ensure duplicate declarations stay compatible with public headers.

## Test Signals
Compile-time ABI compatibility, delegation callback invocation, write delegation detection, recalled-state transition, and object lifetime under unset/close paths.
