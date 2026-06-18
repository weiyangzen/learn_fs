# sources/distributed-fs/lustre-release/include/linux/lnet/lib-types.h

Purpose: internal kernel-only type system for LNet core. It defines message, MD/ME, LND, NI, net, peer, route, portal, resource container, discovery, UDSP, netlink attribute, and global `struct lnet` state.

Important APIs/types: early helpers parse NID/net expression lists. `lnet_msg` carries target/source NIDs, deadlines, health status, retry state, TX/RX commitment flags, credit flags, peer/NI pointers, MD payload vectors, event, and header. `lnet_libmd` and `lnet_me` model memory descriptors and match entries, with flags for zombie, auto-unlink, aborted, handling, and GPU. `lnet_lnd` is the driver interface with startup/shutdown/control, send/recv/eager_recv, accept, tunables, netlink, device priority, and metadata callbacks. Network state is represented by `lnet_net`, `lnet_ni`, `lnet_peer`, `lnet_peer_net`, `lnet_peer_ni`, `lnet_route`, and `lnet_remotenet`. Portal matching uses `lnet_match_table`, `lnet_portal`, and rotor modes. `struct lnet` aggregates CPTs, locks, portals, MD containers, message containers, counters, peer tables, nets, routes, ping/push buffers, discovery and monitor queues, UDSP rules, update callbacks, and workqueues.

Control flow: types encode the core runtime graph. Messages flow through peers/NIs, consume credits, match portals/MDs, and finalize events. Discovery updates peer/ping data; recovery queues drive health repair; router buffer pools mediate forwarding.

State and persistence: entirely volatile kernel state. Atomic counters, krefs, spinlocks, lists, semaphores, completions, and workqueues define lifetime and concurrency boundaries.

Dependencies/integration: depends on Linux bvec/uio/kthread/kref/generic-radix-tree, Lustre netlink compatibility, UAPI LNet control headers, and `nidstr.h`. It must stay synchronized with user-space liblnetconfig for UDSP structures and netlink attributes.

Risks and test signals: high-risk areas are list/refcount ownership, lock ordering, peer discovery state bits, ping buffer size math for large NIDs, health transitions, route aliveness, response tracker zombies, and UAPI/netlink field drift. Test signals are struct layout assertions where exposed, large-NID ping validation, peer/route lifecycle stress, dynamic config with concurrent traffic, fault rules, portal matching, and teardown leak checks.
