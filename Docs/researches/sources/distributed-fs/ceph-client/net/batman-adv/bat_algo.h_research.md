# sources/distributed-fs/ceph-client/net/batman-adv/bat_algo.h

## Purpose
`bat_algo.h` declares the routing algorithm management API used by batman-adv core code, netlink, and algorithm providers.

## Important APIs
- Exposes `batadv_routing_algo` module parameter storage.
- Declares initialization, lookup, registration, mesh selection, and netlink dump functions.

## Control Flow and Integration
Core initialization calls `batadv_algo_init`; algorithm implementations call `batadv_algo_register`; mesh-interface setup calls `batadv_algo_select`; netlink code calls `batadv_algo_dump`.

## State and Persistence
No state is stored in the header, but it exposes the global selected-name buffer and the registration API that populates the algorithm list.

## Risks and Test Signals
Risks are API signature drift with `bat_algo.c` and unintended external mutation of `batadv_routing_algo`. Test signals are compile coverage for BATMAN IV-only and BATMAN V-enabled builds, plus netlink routing algorithm dumps.
