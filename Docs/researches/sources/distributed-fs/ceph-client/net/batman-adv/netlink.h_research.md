# sources/distributed-fs/ceph-client/net/batman-adv/netlink.h

## Purpose
Declares the batman-adv generic netlink integration points used by module setup, subsystem dump callbacks, and throughput-meter reporting.

## APIs, Types, and Functions
Exports `batadv_netlink_register()`, `batadv_netlink_unregister()`, `batadv_netlink_get_meshif()`, `batadv_netlink_get_hardif()`, `batadv_netlink_tpmeter_notify()`, and `batadv_netlink_family`.

## Control Flow
The header itself has no executable flow. Module init registers the family; exit unregisters it. Dump callbacks use the callback-based mesh/hardif lookup helpers to resolve request attributes and must release returned references. Throughput-meter code calls `batadv_netlink_tpmeter_notify()` when sessions finish.

## State and Persistence
No storage is defined here except the external family object implemented in `netlink.c`. Returned mesh and hardif objects carry increased references whose lifetime must be handled by callers.

## Dependencies and Integration
Depends on `main.h`, netlink callback types, and integer types. It is included by multicast, originator, throughput-meter, and other dump-capable subsystems that need the family object for `genlmsg_put()` or lookup helpers.

## Risks
The lookup helpers encode ownership contracts that are easy to misuse: successful mesh lookups require `dev_put()`, and successful hardif lookups require `batadv_hardif_put()`. The exported family object couples all subsystem dumps to the command IDs and policy in `netlink.c`.

## Test Signals
Compile coverage should verify all subsystem dumps include the header cleanly. Runtime signals include correct reference release in dump paths, successful family registration/unregistration, and throughput-meter notifications delivered with the exported family.
