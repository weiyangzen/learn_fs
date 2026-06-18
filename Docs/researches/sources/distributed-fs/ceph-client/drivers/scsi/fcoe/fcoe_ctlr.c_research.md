# sources/distributed-fs/ceph-client/drivers/scsi/fcoe/fcoe_ctlr.c

## Purpose

`fcoe_ctlr.c` implements the libfcoe FIP controller. It owns fabric FCF discovery/selection, FIP-encapsulated ELS handling, keep-alives, Clear Virtual Link processing, non-FIP fallback, VN2VN negotiation/discovery, VLAN discovery replies, WWN derivation, and libfc configuration for FCoE lports.

## Important APIs, types, and functions

Exported lifecycle/API functions include `fcoe_ctlr_init()`, `fcoe_ctlr_destroy()`, `fcoe_ctlr_link_up()`, `fcoe_ctlr_link_down()`, `fcoe_ctlr_recv()`, `fcoe_ctlr_els_send()`, `fcoe_ctlr_recv_flogi()`, `fcoe_wwn_from_mac()`, `fcoe_libfc_config()`, `fcoe_fcf_get_selected()`, and `fcoe_ctlr_set_fip_mode()`. Important internal paths include FCF add/delete/select/age, advertisement parsing, FLOGI retention/retry, FIP ELS parsing, VN2VN probe/claim/beacon handlers, and VLAN request parsing/reply.

## Control flow

Initialization sets `FIP_ST_LINK_WAIT`, initializes FCF lists, locks, timer, work items, and receive queue. Link-up in fabric/auto mode calls `fc_linkup()` and multicasts discovery solicitations; non-FIP mode moves directly to mapped Ethernet behavior; VN2VN starts a timer-driven port-ID negotiation sequence. Incoming FIP frames are queued to `recv_work`, validated for destination/version/length/state, then dispatched to advertisement, ELS, CVL, VN2VN, or VLAN handlers.

Fabric advertisements become `struct fcoe_fcf` records, optionally mirrored to sysfs, solicited for MTU validation, aged by timer, and selected after startup delay. FLOGI ELS frames are intercepted, stored as `flogi_req`, encapsulated in FIP once an FCF is selected, and retried against alternate FCFs after rejects. VN2VN mode probes for a port ID, claims it, sets mapped source MAC/local ID, beacons, creates/updates remote ports, and ages neighbors.

## State and persistence behavior

`struct fcoe_ctlr` stores mode/state, selected FCF, FCF list/count, FLOGI skb and OXID, MAC callback state, timers for selection/keepalive/VN beacons, VN2VN random/probe state, VLAN responder flag, and work queues. FCF records persist until timeout, link reset, or controller destruction. Sysfs FCF devices mirror selected records when the caller allocated a controller device.

## Dependencies and integration points

The file depends on FC/FIP/FCoE protocol headers, libfc lport/discovery/exchange APIs, libfcoe sysfs helpers, skbs, timers, workqueues, Ethernet helpers, and VLAN tags. Lower drivers provide send/update-MAC/get-source-MAC callbacks.

## Risks and edge cases

Descriptor parsing is length/order sensitive. Locking spans `ctlr_mutex`, `ctlr_lock`, discovery locks, sysfs locks, timers, and workqueues. FCF selection returns NULL on conflicting fabric/VFID/FC-MAP advertisements. FLOGI skb ownership across retention, clone, retry, and destruction is delicate. VN2VN collision resolution and beacon aging are timer/probability dependent.

## Test signals

Test malformed/valid advertisements, FCF add/update/delete and sysfs mirroring, FCF conflict rejection, FLOGI LS_ACC/LS_RJT retry, non-FIP fallback, CVL resets, keepalive scheduling, controller destroy with queued frames, VN2VN collision/beacon aging, VLAN responder behavior, and disabled-mode mode switching.
