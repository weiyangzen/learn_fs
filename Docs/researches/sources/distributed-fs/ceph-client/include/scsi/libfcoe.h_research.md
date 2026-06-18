<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libfcoe.h -->
# sources/distributed-fs/ceph-client/include/scsi/libfcoe.h

## Purpose
This header defines the shared FCoE and FIP interface used by Open-FCoE software transports and low-level drivers. It is a contract layer between Ethernet `net_device` handling, libfc local/remote-port logic, FCoE sysfs objects, and driver-owned private state.

## Important APIs, Types, And Functions
The central state types are `struct fcoe_ctlr`, `struct fcoe_fcf`, `struct fcoe_rport`, `struct fcoe_transport`, `struct fcoe_percpu_s`, and `struct fcoe_port`. `enum fip_state` models controller progress from disabled/link-wait through auto, fabric FIP, non-FIP, and VN2VN probing/claim/up states. `enum fip_mode` is the low-level-driver selected target mode and is fixed after `fcoe_ctlr_init()`.

Controller APIs include `fcoe_ctlr_init()`, `fcoe_ctlr_destroy()`, `fcoe_ctlr_link_up()`, `fcoe_ctlr_link_down()`, `fcoe_ctlr_els_send()`, `fcoe_ctlr_recv()`, and `fcoe_ctlr_recv_flogi()`. Library helpers cover libfc setup, WWN derivation and formatting, CRC/trailer work, link-speed and LESB updates, vport validation, pending receive queues, and transport registration through `fcoe_transport_attach()` and `fcoe_transport_detach()`.

## Control Flow
Drivers allocate a controller plus private data, initialize it with a FIP mode, attach it to an `fc_lport`, and provide send/MAC callbacks. Link-up enters the configured discovery mode; received FIP SKBs are queued on `fip_recv_list` and processed by work items/timers. FCF advertisements populate the `fcfs` list, then selection updates `sel_fcf`, destination MACs, keepalive timers, and libfc login behavior. Data-plane receives flow through `fcoe_percpu_s` queues and `fcoe_port` pending-queue throttling.

## State And Persistence
All state is in-memory kernel state. Timers track solicitation, selection, and keepalive deadlines in jiffies. `fcoe_ctlr` combines mutex-protected controller state with a spinlock for `flogi_req`; `fcoe_percpu_s` uses a `local_lock_t`. No durable state is written here, but sysfs device objects expose selected controller/FCF state.

## Dependencies And Integration Points
The header depends on Ethernet, SKB, workqueue, timer, libfc, FCoE FC framing, and fcoe sysfs headers. It integrates with FC transport vports, netdev-backed software HBAs, module aliasing for FCoE PCI drivers, and per-netdev transport mapping.

## Risks
FIP state transitions are timing and locking sensitive. Incorrect callback implementations can leak SKBs, race MAC updates, or select an invalid FCF. MTU/CRC/trailer constants must match FC-over-Ethernet framing. VN2VN login retry limits and FCF selection limits are policy-sensitive and can affect discovery convergence.

## Test Signals
Useful validation includes link up/down sequencing, FIP advertisement selection, FLOGI receive/send paths, VN2VN probe/claim behavior, pending receive queue backpressure, CRC/trailer generation, sysfs controller create/destroy, vport validation, and module alias/transport attach-detach coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libfcoe.h -->
