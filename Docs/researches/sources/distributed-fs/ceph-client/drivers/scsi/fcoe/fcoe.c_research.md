# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe.c

## Purpose

`fcoe.c` is the software FCoE initiator driver that binds libfc/libfcoe to a Linux Ethernet netdevice. It registers the default `fcoe_sw` transport, creates/destroys FCoE controller and local-port instances, encapsulates and decapsulates FC frames over Ethernet, handles FIP control traffic entry/exit points, reacts to netdevice/DCB events, exposes FC transport operations including NPIV vports, and delegates DDP/offload hooks to lower network drivers.

## Important APIs, types, and functions

Important state includes `fcoe_config_mutex`, `fcoe_wq`, `fcoe_hostlist`, per-CPU `fcoe_percpu`, `struct fcoe_interface`, and per-lport `struct fcoe_port`. Key templates are `fcoe_sysfs_templ`, `fcoe_libfc_fcn_templ`, FC transport function templates for nports/vports, and `fcoe_shost_template`. Major paths are `fcoe_interface_create/setup/remove/cleanup()`, `fcoe_if_create/destroy()`, `fcoe_xmit()`, `fcoe_rcv()`, `fcoe_recv_frame()`, `fcoe_filter_frames()`, `fcoe_fip_recv()`, `fcoe_fip_send()`, `fcoe_elsct_send()`, `fcoe_device_notification()`, `fcoe_create/destroy/enable/disable()`, DDP callbacks, and NPIV vport callbacks.

## Control flow

Module init creates the workqueue, registers the software transport, initializes per-CPU receive queues, installs netdevice/DCB notifiers, and attaches FC transport templates. Creation locks `fcoe_config_mutex` and RTNL, rejects duplicate netdevices, allocates a sysfs controller plus `struct fcoe_ctlr`/`struct fcoe_interface`, registers packet handlers and MAC filters, creates the master libfc local port, configures SCSI/FC host attributes, allocates exchange managers, records DCB priorities, and starts fabric login.

Transmit starts from libfc `.frame_send = fcoe_xmit`. ELS frames may be diverted to FIP encapsulation. Normal frames get CRC/EOF trailers, optional CRC/LSO offload flags, Ethernet/VLAN headers, controller-selected MAC addresses, stats updates, and delivery through `fcoe_port_send()` with retry queue fallback. Receive starts in packet handlers, validates link and MAC/FCoE framing, queues to a per-CPU worker by exchange ID, then linearizes, checks version/CRC/EOF, and delivers valid frames to `fc_exch_recv()`.

## State and persistence behavior

Runtime state is in kernel memory and netdevice filter registrations. `fcoe_hostlist` maps active netdevices to interfaces under RTNL. `struct fcoe_interface` stores packet handlers, logical/real netdevices, multicast/unicast filter state, offload EM pointer, removal flag, and priority. `struct fcoe_port` stores pending transmit queue, retry timer, source MAC, queue-depth watermarks, and destroy work. Per-CPU state holds receive queues and reusable trailer pages.

## Dependencies and integration points

The file integrates Linux networking, VLAN/DCB/notifier APIs, SCSI midlayer, FC transport, libfc, libfcoe, and lower netdevice FCoE hooks such as `ndo_fcoe_enable`, `ndo_fcoe_disable`, WWN/HBA info getters, and DDP hooks. It registers a `struct fcoe_transport` consumed by `fcoe_transport.c`.

## Risks and edge cases

`fcoe_hostlist_lookup()` computes a controller pointer before checking whether the interface lookup returned NULL. Teardown crosses packet handlers, `synchronize_net()`, RTNL, `fcoe_config_mutex`, workqueues, SCSI host removal, libfc cleanup, and sysfs deletion, so ordering is fragile. FIP/non-FIP/VN2VN mode changes affect multicast filters and MAC mapping. FDMI error handling returns without freeing the allocated buffer on lower-driver failure. Receive CPU selection and per-CPU cleanup are sensitive to exchange IDs and CPU hotplug.

## Test signals

Test module load/unload, create/destroy on physical and VLAN devices, link and MTU/feature notifier paths, FIP discovery and non-FIP fallback, VN2VN switching, FLOGI/LOGO MAC updates, NPIV create/delete/disable, DDP and non-DDP devices, transmit retry queue behavior, and teardown under KASAN/KCSAN/lockdep.
