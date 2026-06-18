# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/peer.sh

Purpose: Tests the netdevsim `link_device` peer facility across network namespaces, including validation of bad link arguments and data connectivity through linked simulated devices.

Important APIs/functions: Local helpers create/delete namespaces, test carrier state via `/sys/class/net/.../carrier`, and require `socat`. Sysfs controls are `/sys/bus/netdevsim/new_device`, `del_device`, `link_device`, and `unlink_device`.

Control flow: The script loads netdevsim, creates two devices, moves them into server/client namespaces, assigns IPv4 addresses, and brings links up. It verifies linking fails for non-existent peer ifindex, non-existent namespace fd, self-link, and malformed arguments. It then links devices, checks carrier propagation across down/up and unlink/relink, runs a TCP transfer with `socat`, unlinks, deletes devices, removes namespaces, and unloads the module.

State and persistence: Creates two netdevsim devices, two namespaces, namespace file descriptors, and a temp file for received data. Cleanup is mostly explicit at the end rather than trap-heavy.

Dependencies and integration: Requires `socat`, root, namespace support, sysfs netdevsim controls, and TCP stack in namespaces.

Risks: Lack of a comprehensive trap means interruption can leave namespaces/devices. Carrier checks are synchronous and can race with link updates. The hard-coded TCP port can collide inside the test namespace.

Test signals: Expected results are rejected invalid link requests, successful valid link, carrier changes matching peer state, successful `HI` transfer, and zero final error count.
