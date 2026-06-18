# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_rnode.c

## Purpose
`csio_rnode.c` implements remote FCoE node management. It maps firmware remote-device events to rnode state-machine events, allocates and frees rnodes, reconciles firmware flow IDs with WWPN/NPort identity, validates remote parameters and roles, registers/unregisters FC rports with the transport layer, handles device-loss cleanup, and maintains rnode lifecycle state for SCSI target visibility.

## Important APIs and Functions
- Event mapping `fwevt_to_rnevt[]` translates firmware causes such as PLOGI/PRLI/LOGO/RSCN device-lost into `enum csio_rn_ev`.
- `csio_is_rnode_ready()` tests ready state; `csio_is_rnode_uninit()` is the internal uninitialized-state test.
- Lookup helpers include `csio_rn_lookup()`, `csio_rn_lookup_wwpn()`, and public `csio_rnode_lookup_portid()`.
- Duplicate detection `csio_rn_dup_flowid()` scans sibling lnodes for active rnodes using the same firmware flowid.
- Allocation/free helpers `csio_alloc_rnode()`, `csio_free_rnode()`, `csio_get_rnode()`, and public `csio_put_rnode()` manage the hardware rnode mempool and lnode rnode list.
- `csio_confirm_rnode()` is the central reconciliation routine for new firmware `fcoe_rdev_entry` data.
- `csio_rn_verify_rparams()` validates rport type, expected DID for fabric/name-server ports, nonzero WWNN/WWPN for normal/name-server ports, service class, FCP target/initiator flags, NPIV support, and copies remote identity into the rnode.
- `__csio_reg_rnode()` and `__csio_unreg_rnode()` call FC transport registration functions outside `hw->lock` and maintain target counters.
- State handlers `csio_rns_uninit()`, `csio_rns_ready()`, `csio_rns_offline()`, and `csio_rns_disappeared()` implement remote-node lifecycle.
- Public event APIs: `csio_rnode_fwevt_handler()` handles firmware event causes; `csio_rnode_devloss_handler()` closes/free disappeared rnodes.
- Initialization/exit: `csio_rnode_init()` inserts rnodes into `ln->rnhead`; `csio_rnode_exit()` removes them and asserts no host completions remain.

## Control Flow and State
Firmware RDEV payloads are first routed by lnode code to `csio_confirm_rnode()`, which finds an existing rnode by flowid, WWPN, or NPort ID for well-known ports, or allocates a new one. Once `rn->rdev_entry` is set, `csio_rnode_fwevt_handler()` maps the firmware cause to a state-machine event. Login/PLOGI events from uninit/offline/disappeared validate parameters and transition to ready with FC rport registration. PRLI events in ready refresh registration. DOWN/LOGO/NAME_MISSING events unregister the rport and move to offline or disappeared. CLOSE moves back to uninit and allows the rnode to be freed.

## State and Persistence Behavior
Each rnode stores owning lnode, firmware flowid, host completion queue, FC NPort ID, FCP flags, current/previous firmware event, role bitmap, firmware rdev entry pointer, service parameters, FC transport `rport`, supported class/frame size/SCSI ID, and stats. It is linked through the embedded `sm.sm_list` on `ln->rnhead` and allocated from `hw->rnode_mempool`.

## Dependencies and Integration Points
The file depends on SCSI FC transport and FC ELS/FS headers plus `csio_hw.h`, `csio_lnode.h`, and `csio_rnode.h`. Registration functions `csio_reg_rnode()` and `csio_unreg_rnode()` are declared in the header and implemented elsewhere. SCSI cleanup integrates through `csio_scsi_cleanup_io_q()` when unregistering rnodes with pending host completions. FDMI can be triggered when the management-server NPort appears.

## Risks and Edge Cases
- Identity reconciliation is complex: duplicate flow IDs across lnodes, same WWPN with changed SSNI, and well-known address relogin all take different branches.
- `csio_put_rnode()` asserts the rnode is uninit; callers must post CLOSE before freeing.
- `__csio_unreg_rnode()` decrements `ln->last_scan_ntgts` along with `n_scsi_tgts`; underflow is possible if counters are already zero or inconsistent.
- `csio_rn_verify_rparams()` indexes `clsp[fc_class - 1]`; malformed firmware class zero would underflow.
- Rnode registration/unregistration intentionally drops `hw->lock`, so surrounding state must remain valid across transport calls.

## Test Signals
Tests should cover fabric/name-server/regular/FDMI rport types, PRLI target/initiator flags, invalid DIDs, zero WWNs, duplicate flowid detection, WWPN relogin with changed flowid, LOGO/DOWN/NAME_MISSING/CLOSE transitions, device-loss delayed cleanup, and pending host completion cleanup on unregister. Runtime signals include FC rport registration/unregistration, target count changes, rnode allocation/free stats, and state string output.
