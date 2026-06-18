# sources/distributed-fs/ceph-client/include/linux/atalk.h

## Purpose
Defines internal AppleTalk protocol structures, DDP/AARP headers, route/interface/socket state, exported global tables, and subsystem init/cleanup hooks.

## Important APIs, Types, And Functions
Structures include `atalk_route`, `atalk_iface`, `atalk_sock`, `ddpehdr`, `elapaarp`, and `aarp_iter_state`. Inline helpers convert `struct sock` to `atalk_sock` and locate DDP/AARP headers in skb transport data. Constants define AARP timing, hash size, retransmit limit, interface probe flags, and AARP operation codes. Exports include datalink protocols, route/interface/socket lists and locks, default route, AARP init/send/probe/proxy/remove/cleanup functions, address and route lookups, sysctl/proc init/exit with config stubs, and `aarp_seq_ops`.

## Control Flow, State, And Persistence
AppleTalk keeps global route, interface, and socket lists protected by rwlocks. Interfaces can be probing or failed. AARP maintains resolution state and timers. DDP send flow resolves hardware addresses via AARP before transmitting. Proc/sysctl registration is optional by config.

## Dependencies And Integration Points
Depends on network socket/skbuff/device types, Ethernet address length, and UAPI AppleTalk definitions. Integrates the AppleTalk socket family, datalink layer, AARP, procfs, sysctl, and net devices via `dev->atalk_ptr`.

## Risks And Test Signals
Global list locking, device removal, and AARP timeout handling are the key risks. Tests should cover interface bring-up/down, address probe collision, AARP resolution and retransmit limit, route lookup/default route, socket list iteration, proc/sysctl availability, and build behavior without CONFIG_ATALK where only selected helpers exist.
