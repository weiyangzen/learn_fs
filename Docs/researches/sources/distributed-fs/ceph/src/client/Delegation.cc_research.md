# sources/distributed-fs/ceph/src/client/Delegation.cc

## Purpose
`Delegation.cc` implements file delegation support. A delegation holds capability references on behalf of an application until the delegation is recalled, then enforces eventual return via a client timer.

## Important APIs, Types, and Functions
`ceph_deleg_caps_for_type()` maps `CEPH_DELEGATION_RD` and `CEPH_DELEGATION_WR` to required Ceph caps. `Delegation` construction/destruction gets and puts those cap refs on the inode. `reinit()` updates type/callback/private data. `recall()` invokes the application callback once and arms a timeout. `arm_timeout()` and `disarm_timeout()` schedule/cancel `C_Deleg_Timeout`.

## Control Flow
`Inode::set_deleg()` creates or reinitializes a `Delegation` after checking open conflicts and caps. Later conflicting opens or explicit recalls call `Delegation::recall()`. The callback is responsible for returning the delegation through client APIs; if not, `C_Deleg_Timeout::finish()` forcibly unmounts the client.

## State and Persistence Behavior
Delegation state is in-memory only: file handle pointer, private callback token, type, recall timestamp, and timer context. Capability refs are persistent only in the sense that they pin client-held MDS caps until released.

## Dependencies and Integration Points
The implementation depends on `Client`, `Inode`, `Fh`, `Timer`, and Ceph cap constants. It uses `client->timer_lock` and `client->timer`, and calls `Client::_unmount(false)` on timeout.

## Risks and Edge Cases
The timeout context stores a raw `Delegation*`; destruction must always cancel the timer before object lifetime ends. Recall callbacks run synchronously from recall path and can reenter upper layers. Timeout-triggered forced unmount is intentionally harsh and must only occur for enabled delegation timeouts. `ceph_deleg_caps_for_type()` aborts on unknown types.

## Test Signals
Cover read/write cap mapping, read-delegation skip behavior, reinit type changes, timer cancellation on return, timeout unmount, and conflicts with open-for-write/open-count logic in `Inode::set_deleg()`.
