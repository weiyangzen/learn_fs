# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_nport.h

## Purpose
`efc_nport.h` declares the local nport and vport lifecycle API used by domain and fabric code.

## Important APIs, Types, And Functions
Exports include `efc_nport_find`, `efc_nport_alloc`, `efc_nport_free`, `efc_nport_attach`, nport/vport state handlers, and `efc_vport_start`.

## Control Flow And State
The lifecycle is allocate under a domain, attach after an FC_ID is known, transition through attached state, and free after child nodes have drained. Vport-specific declarations show an initial VPI allocation path followed by FDISC or hard-coded FC_ID attach.

## Dependencies And Integration Points
It depends on `struct efc_domain`, `struct efc_nport`, `struct efc_sm_ctx`, and `enum efc_sm_event`. Domain code allocates physical nports; fabric code attaches vports after FDISC; transport code may request vport start/delete through higher-level wrappers.

## Risks And Test Signals
Risks include callers assuming `efc_nport_find` returns a borrowed pointer when it actually takes a reference in the implementation. Test signals include reference-balanced find/release paths, physical and virtual attach success/fail, and shutdown while children remain.
