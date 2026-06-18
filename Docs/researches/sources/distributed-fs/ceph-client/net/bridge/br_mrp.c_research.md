<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_mrp.c

Purpose: implements bridge Media Redundancy Protocol (MRP) runtime behavior. It creates and deletes MRP ring instances, assigns primary/secondary/interconnect ports, manages ring and interconnect states and roles, generates or monitors MRP test frames in software when hardware does not offload them, registers an ETH_P_MRP frame handler, and forwards or consumes MRP control frames according to ring and interconnect roles.

Important APIs, types, and functions:

- Instance lifecycle: `br_mrp_add()`, `br_mrp_del()`, `br_mrp_port_del()`, and `br_mrp_enabled()`.
- Configuration APIs: `br_mrp_set_port_state()`, `br_mrp_set_port_role()`, `br_mrp_set_ring_state()`, `br_mrp_set_ring_role()`, `br_mrp_start_test()`, `br_mrp_set_in_state()`, `br_mrp_set_in_role()`, and `br_mrp_start_in_test()`.
- Frame handling: `br_mrp_process()`, `br_mrp_rcv()`, `br_mrp_mrm_process()`, `br_mrp_mra_process()`, and `br_mrp_mim_process()`.
- Timed software work: `br_mrp_test_work_expired()` and `br_mrp_in_test_work_expired()`.
- skb construction helpers create ring test and interconnect test frames with MRP TLVs and common headers.
- Important state lives in `struct br_mrp`: ring ID, interconnect ID, port RCU pointers, role/state fields, transition counters, sequence ID, test intervals/end times/max-miss counters, monitor mode, and offload flags.

Core control flow:

- `br_mrp_add()` validates unique ring ID, valid primary/secondary ports, and that no selected port is already part of another MRP instance. It allocates `struct br_mrp`, marks the two ports forwarding and `BR_MRP_AWARE`, registers the MRP frame type if this is the first instance, initializes delayed work, adds the instance to `br->mrp_list`, and asks switchdev to add the instance. Failure unwinds through `br_mrp_del_impl()`.
- `br_mrp_del_impl()` cancels software test work, disables hardware/software test generation, disables ring/interconnect roles, deletes switchdev objects, restores ports to normal bridge state, clears `BR_MRP_AWARE`, removes the instance from the RCU list, frees it by RCU, and unregisters the frame type when the list becomes empty.
- Ring role and interconnect role setters call switchdev. If hardware fully handles the role, software detection/generation is suppressed; if hardware supports only software backup, delayed work and software forwarding remain active; if unsupported, configuration fails.
- `br_mrp_start_test()` and `br_mrp_start_in_test()` first attempt switchdev test-frame generation. On software fallback they set interval, end time, max-miss, monitor state, reset miss counters, and queue delayed work on `system_percpu_wq`.
- Test work increments miss counters until max miss; when a closed ring or monitored MRA stops seeing expected frames, it notifies userspace through port-open events. If not in monitor mode, it builds and transmits MRP Test frames on primary and secondary ports. Interconnect test work sends InTest frames on primary, secondary, and interconnect ports.
- `br_mrp_rcv()` handles MRP frames on aware ports. Ring frames are consumed by MRM behavior or monitored by MRA/MRC behavior, then forwarded when role rules allow. Interconnect frames are forwarded or suppressed based on ring port, interconnect port, MIM/MIC role, ring port blocking state, frame TLV type, and whether a received InTest belongs to this MIM.

State and persistence behavior:

- MRP state is per-bridge runtime state in `br->mrp_list`; instances are RCU visible and administratively mutated under RTNL. Port pointers are RCU assignments.
- Port state is directly changed to forwarding/blocking/disabled and `BR_MRP_AWARE` is set while a port participates. Deletion restores normal forwarding or disabled state based on the bridge device running state.
- Sequence IDs and transition counters are monotonic within an instance. Miss counters and timers are transient. Lost continuity flags are set in `br_mrp_netlink.c` notification helpers.
- Software-generated test frames are scheduled only for the requested period; work exits once `test_end` or `in_test_end` is reached.

Dependencies and integration points:

- Netlink parsing and reporting live in `br_mrp_netlink.c`. Hardware offload shims live in `br_mrp_switchdev.c`.
- It registers a custom frame type through `br_add_frame()`/`br_del_frame()` in `br_input.c`, and forwards MRP frames through normal `br_forward()` egress.
- It depends on switchdev MRP objects/attributes, delayed workqueues, RCU, RTNL, bridge port state, and userspace notifications for ring/interconnect open or closed events.
- MRP is rejected by netlink when STP is enabled, so MRP owns loop prevention for its participating ports.

Risks and edge cases:

- Instance teardown must cancel delayed work before freeing the RCU object; otherwise software test work could access freed MRP state.
- Hardware support classification matters. Treating partial support as full hardware offload would stop required software monitoring; treating full support as software could duplicate protocol frames.
- MRP forwarding rules are role-specific and TLV-specific. Incorrect suppression can create loops on a closed ring or break interconnect continuity detection.
- Port uniqueness across primary, secondary, and interconnect roles prevents ambiguous forwarding and teardown; bypassing it could corrupt multiple rings.
- `sizeof(oui)` is used in one option length expression where `oui` is a pointer variable; this should be checked against protocol layout expectations.

Test signals:

- Configure add/delete rings with valid, duplicate, missing, and reused ports. Verify frame handler registration only while instances exist.
- Test MRM, MRC, and MRA roles with hardware full, software-backup, and unsupported switchdev responses.
- Validate software Ring Test and InTest frame generation intervals, period expiry, sequence increments, and miss/open notifications.
- Feed ring and interconnect TLV frames for MIM/MIC/MRA/MRM combinations and verify forwarding destinations.
- Delete ports participating in MRP and confirm work cancellation, port state restoration, switchdev cleanup, and RCU-safe teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_mrp.c -->
