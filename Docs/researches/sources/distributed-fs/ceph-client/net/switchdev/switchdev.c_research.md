# sources/distributed-fs/ceph-client/net/switchdev/switchdev.c

## Purpose
This file implements the core switchdev API: deferred switchdev operations, blocking and atomic notifier chains, helpers for propagating bridge/LAG/FDB/object/attribute events to hardware switch drivers, and bridge port offload replay hooks.

## Important APIs, Types, And Functions
Exported APIs include `switchdev_deferred_process()`, `switchdev_port_attr_set()`, `switchdev_port_obj_add()`, `switchdev_port_obj_del()`, `switchdev_port_obj_act_is_deferred()`, notifier registration/call functions, FDB/object/attribute handling helpers, and bridge port offload/unoffload/replay functions. Internal state uses a global deferred list protected by `deferred_lock`, `struct switchdev_deferred_item`, an atomic notifier chain, and a raw blocking notifier chain.

## Control Flow
Callers either perform switchdev operations immediately under RTNL or enqueue them with `SWITCHDEV_F_DEFER`. Deferred work holds a netdevice reference, copies the attr/object payload, schedules `deferred_process_work`, and later replays under RTNL. Notifier wrappers package attr/object/FDB information, call registered drivers, translate notifier results, and enforce the "handled" contract. Recursive helpers walk lower devices under bridges or LAGs, avoid propagating across bridge masters where inappropriate, and optionally mirror events from foreign devices in the same bridge domain.

## State And Persistence
Runtime state is transient: deferred operations, netdevice references, and notifier registrations. There is no persistent storage. Correct lock state is central: immediate paths assert RTNL, deferred queue uses a bottom-half spinlock, and blocking notifier registration is protected by RTNL.

## Dependencies And Integration Points
Dependencies include netdevice stacking APIs, bridge helpers, notifier chains, rtnetlink locking, VLAN/MDB/FDB switchdev object definitions from `<net/switchdev.h>`, and exported symbols consumed by switchdev-capable drivers and bridge code.

## Risks And Test Signals
Risks include deferred object lifetime/copy-size mismatches, missed `handled` updates, recursion through complex bridge/LAG topologies, foreign-device loop prevention, and driver callbacks returning hard errors versus `-EOPNOTSUPP`. The source snapshot has duplicated text in several places, including a repeated struct member line and repeated conditional line in the delete helper, which should be build-checked. Test signals include switchdev driver builds, bridge VLAN/MDB/FDB offload tests, LAG-under-bridge event propagation, deferred add/del ordering, extack error propagation, and bridge port replay during offload attach.
