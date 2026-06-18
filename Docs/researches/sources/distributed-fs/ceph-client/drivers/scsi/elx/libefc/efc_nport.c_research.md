# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_nport.c

## Purpose
`efc_nport.c` implements local FC port and NPIV vport lifecycle management: allocation, attach, backend registration, shutdown, vport persistence records, and reconstruction after domain attach.

## Important APIs, Types, And Functions
Public functions include `efc_nport_cb`, `efc_nport_alloc`, `efc_nport_free`, `efc_nport_find`, `efc_nport_attach`, `efc_vport_start`, `efc_nport_vport_new`, `efc_nport_vport_del`, `efc_vport_del_all`, and `efc_vport_create_spec`. State handlers include allocated, vport init/wait alloc/allocated, attached, wait shutdown, and wait port free.

## Control Flow And State
Allocation checks duplicate WWNs, initializes xarray/refcount/state, copies domain service parameters, adds the nport to `domain->nport_list`, and references the domain. Attach stores the nport in domain lookup by FC_ID, updates display names, and sends `REG_VPI`. Attached entry calls `efc->tt.new_nport`; exit calls `del_nport`. Shutdown marks `shutting_down`, handles vport link-down references, either frees immediately if no nodes exist or posts shutdown to each node and waits for `ALL_CHILD_NODES_FREE`. Vport specs persist requested WWNN/WWPN/FC_ID/backend data and are started when the domain enters ready.

## Dependencies And Integration Points
The file depends on domain lookup and list ownership, node shutdown, ELS LOGO for vport logout, `efc_cmd_nport_*`, backend nport callbacks, and spinlocks for `efc->lock` and `vport_lock`.

## Risks And Test Signals
Risks include vport spec and nport reference mismatches, shutdown while VPI attach is pending, domain lookup erasure ordering, and duplicate WWN handling. Test signals include physical nport attach, NPIV FDISC path, vport creation/deletion across link down/up, node-drain shutdown, attach failure, backend callback ordering, and duplicate vport rejection.
