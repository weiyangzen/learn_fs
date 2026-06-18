# sources/distributed-fs/ceph-client/net/atm/signaling.c

## Purpose
`signaling.c` bridges kernel SVC sockets to a privileged userspace ATM signaling daemon (`atmsigd`). It queues requests to the daemon, receives daemon replies, updates VCC state, and purges SVCs if the daemon exits.

## Important APIs, Types, and Functions
- Global `struct atm_vcc *sigd`: current signaling daemon meta VCC.
- `sigd_attach`: attaches a privileged socket as the signaling daemon using a synthetic `sigd_dev`.
- `sigd_enq2` / `sigd_enq`: allocate `struct atmsvc_msg` skbs and enqueue requests to the daemon.
- `sigd_send`: device send callback for daemon replies; validates opaque VCC pointers via `find_get_vcc`, then handles `as_okay`, `as_error`, `as_indicate`, `as_close`, `as_modify`, `as_addparty`, and `as_dropparty`.
- `modify_qos`: invokes driver `change_qos` and reports success/failure back to the daemon.
- `sigd_close`: clears `sigd`, purges pending requests, and releases registered SVC VCCs.

## Control Flow
`ioctl.c` calls `sigd_attach` for `ATMSIGD_CTRL`. SVC operations enqueue messages with `sigd_enq*` and sleep on `ATM_VF_WAITING`. The daemon reads those skbs from its receive queue and writes replies through the synthetic device send path, which is `sigd_send`. Reply handling updates socket errors, VCC flags, local/remote/PVC/QoS fields, accept queues, or party status, then wakes waiting sockets with `sk_state_change`.

## State and Persistence
Persistent state includes the singleton daemon pointer, VCC flags (`META`, `READY`, `WAITING`, `REGIS`, `RELEASED`), socket errors, accept queues, session ids for point-to-multipoint connects, and queued `atmsvc_msg` skbs. The daemon protocol stores kernel VCC pointers as opaque tokens, which is why `sigd_send` revalidates pointers by scanning `vcc_hash`.

## Dependencies and Integration
Integrates tightly with `svc.c`, `ioctl.c`, the global VCC hash/list locks, ATM device callback semantics, and userspace atmsigd. It also calls `vcc_release_async` to tear down sockets.

## Risks and Test Signals
Risks are high because userspace carries opaque kernel pointers: privilege gating, pointer validation, socket lifetime, and reference balancing are critical. Additional risks include unbounded allocation retry loops, daemon disappearance while sockets wait, and accept queue handling for `as_indicate`. Test signals include daemon attach exclusivity, SVC bind/connect/listen/accept/release flows, daemon crash cleanup, invalid VCC pointer rejection, QoS modification replies, and add/drop party status propagation.
