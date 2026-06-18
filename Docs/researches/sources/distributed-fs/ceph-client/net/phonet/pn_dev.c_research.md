# sources/distributed-fs/ceph-client/net/phonet/pn_dev.c

## Purpose
`pn_dev.c` manages Phonet addresses, Phonet-capable netdevices, simple Phonet routes, per-network-namespace Phonet state, procfs entries, netdevice notifier integration, and initialization/exit of Phonet device infrastructure.

## Important APIs, types, and functions
`struct phonet_net` stores a `phonet_device_list` and `phonet_routes` table per net namespace. Address/device functions include `phonet_device_list()`, `phonet_device_get()`, `phonet_address_add()`, `phonet_address_del()`, `phonet_address_get()`, and `phonet_address_lookup()`. Route functions include `phonet_route_add()`, `phonet_route_del()`, `phonet_route_get_rcu()`, and `phonet_route_output()`.

Initialization and teardown are `phonet_device_init()` and `phonet_device_exit()`. Per-net callbacks are `phonet_init_net()` and `phonet_exit_net()`. Device notifier logic is in `phonet_device_notify()`, with helpers `phonet_device_autoconf()`, `phonet_device_destroy()`, and `phonet_route_autodel()`.

## Control flow and state
Per namespace, Phonet devices are kept in an RCU list guarded by `pndevs.lock`; each device entry has a bitmap of 64 possible 6-bit addresses. Adding an address finds or allocates the device entry and sets `addr >> 2`. Deleting clears the bit and removes the device entry when no addresses remain. Address lookup scans registered/up devices under RCU.

Source address selection prefers an address on the target device matching the destination address high bits, then falls back to the first address on the device, then recursively tries another default Phonet device. `phonet_device_get()` returns the first registered/up device with a held reference.

Routes are a 64-entry RCU table keyed by `daddr >> 2`, protected for updates by `routes.lock`. Add stores a device and takes a reference. Delete clears the slot but leaves synchronization and `dev_put()` to the caller. Device unregister destroys address state, emits address deletion notifications, removes routes pointing to the device, waits for RCU, emits route deletion notifications, and drops route-held device references.

`phonet_device_init()` registers pernet state, global `/proc/net/pnresource`, netdevice notifier, and rtnetlink handlers. Exit unregisters rtnetlink handlers, notifier, pernet state, and procfs.

## State and persistence behavior
Address and route state is in kernel memory and per net namespace except the pnresource proc entry in init_net. It is not persistent across module unload or namespace/device teardown. Device references held by routes are explicitly managed and released after RCU grace periods.

## Dependencies and integration points
The file integrates with netdevice registration/unregistration, private Phonet autoconfiguration ioctl `SIOCPNGAUTOCONF`, rtnetlink notification helpers in `pn_netlink.c`, procfs seq operations from `socket.c`, and Phonet routing decisions in `af_phonet.c`.

## Risks and edge cases
Risks include address bitmap shift semantics (`addr >> 2`), device reference leaks in route add/delete/autodel, RCU lifetime of device entries, missing notifications on failure paths, and default route fallback selecting unexpected devices. `phonet_exit_net()` warns if device entries remain, so teardown ordering with netdevices matters.

## Test signals
Test adding/deleting addresses via rtnetlink, automatic address config on ARPHRD_PHONET registration, route add/delete/dump, device unregister cleanup of addresses/routes, namespace isolation, source address selection, default route fallback, procfs entries, and refcount leak detection under repeated add/delete/unregister cycles.
