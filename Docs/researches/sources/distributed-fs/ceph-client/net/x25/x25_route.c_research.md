# sources/distributed-fs/ceph-client/net/x25/x25_route.c

Purpose: manages the global X.25 address-prefix route table and route ioctl handling.

Important APIs/functions: `x25_get_route()` performs longest-prefix route lookup; `x25_route_ioctl()` handles `SIOCADDRT` and `SIOCDELRT`; `x25_route_device_down()` removes routes for a disappearing device; `x25_dev_get()` validates X.25 netdevices; and `x25_route_free()` releases all routes on module exit.

Control flow: add-route rejects duplicate prefix/device-length pairs, pads address strings with zeros, stores significant digit count and device pointer, and inserts under write lock. Delete-route finds an exact prefix/significant-digits/device match and removes it. Lookup scans all routes and returns a refcounted longest prefix match.

State and persistence: runtime global `x25_route_list` is protected by `x25_route_list_lock`; each route has address prefix, significant digit count, device pointer, and refcount. No durable persistence exists beyond ioctl-created runtime state.

Dependencies and integration: called by AF_X25 connect and forwarding, controlled by privileged socket ioctls, and cleaned from netdevice notifier paths.

Risks and test signals: route lifetime and prefix matching are central. Tests should cover invalid significant digits, down or non-ARPHRD_X25 device rejection, duplicate add, longest-prefix selection, route deletion while referenced, device down cleanup, and CAP_NET_ADMIN enforcement in caller.
