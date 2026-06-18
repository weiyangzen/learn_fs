# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_domain.c

## Purpose
`efc_domain.c` implements the FC domain lifecycle and top-level receive-frame dispatch. A domain represents the fabric/loop context containing local nports and remote nodes.

## Important APIs, Types, And Functions
Key public functions are `efc_domain_cb`, `efc_domain_alloc`, `efc_domain_free`, `efc_register_domain_free_cb`, `efc_domain_attach`, `efc_domain_post_event`, `efc_dispatch_frame`, `efc_domain_dispatch_frame`, and `efc_node_dispatch_frame`. State handlers include init, wait alloc, allocated, wait attach, ready, wait nports free, wait shutdown, and wait domain lost.

## Control Flow And State
Hardware domain callbacks enter under `efc->lock` and translate found/lost/alloc/attach/free results into state-machine events. On `DOMAIN_FOUND`, the code allocates a domain and physical nport, chooses requested or default WWNs, handles loop topology, allocates hardware domain resources, and starts fabric login through the FLOGI node. Attach stores the nport in `domain->lookup`, registers the domain, marks `attached`, accepts held frames, and broadcasts `DOMAIN_ATTACH_OK` to nodes. Domain loss holds frames, shuts down nports, waits for `ALL_CHILD_NODES_FREE`, frees hardware, and may replay a pending found record.

## Dependencies And Integration Points
The file integrates hardware callbacks, `efc_cmd_domain_*`, nport/node allocation, fabric/device state machines, xarray lookups, pending-frame queues, and base-driver frame free callbacks. `efc_dispatch_frame` is the receive ingress point from hardware.

## Risks And Test Signals
Risks include pending-frame ordering during hold/unhold, domain replacement while callbacks still reference old objects, xarray lookup lifetime, and unsolicited frame creation of nodes before topology is final. Test signals include domain found/lost during alloc and attach, private loop and public loop paths, P2P fallback dispatch, FCP frame drops with invalid D_ID, pending frame flush, and correct sequence freeing on handled vs unhandled frames.
