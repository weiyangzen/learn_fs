# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_lnode.c

## Purpose
`csio_lnode.c` implements local FCoE node management. It translates firmware link/rdev events into local-node state transitions, reads FCF/VNP parameters, starts/stops FCoE links, manages physical and NPIV lnode relationships, drives rnode state fan-out, performs FDMI management registration, handles ELS/CT management completions, exposes FC transport async events, and initializes/exits lnode resources.

## Important APIs and Functions
- Tunables: `csio_fcoe_rnodes` limits remote nodes and `csio_fdmi_enable` controls FDMI registration.
- Lookup helpers: `csio_ln_lookup_by_portid()`, `csio_ln_lookup_by_vnpi()`, and `csio_lnode_lookup_by_wwpn()` find physical or child lnodes.
- FDMI helpers build DHBA, DPRT, RHBA, and RPA CT requests through callbacks `csio_ln_fdmi_dhba_cbfn()`, `csio_ln_fdmi_dprt_cbfn()`, `csio_ln_fdmi_rhba_cbfn()`, and `csio_ln_fdmi_done()`.
- `csio_ln_vnp_read()` and `csio_ln_vnp_read_cbfn()` issue/read firmware VNP state, updating MAC, NPort ID, WWNN/WWPN, and service parameters.
- `csio_fcoe_enable_link()` sends FCoE link up/down mailbox commands and records WWNs and physical MAC on link-up responses.
- `csio_ln_read_fcf_entry()` and `csio_ln_read_fcf_cbfn()` read and persist FCF parameters.
- `csio_handle_link_up()` and `csio_handle_link_down()` process firmware link events and post lnode state-machine events.
- `csio_post_event_rns()`, `csio_cleanup_rns()`, `csio_post_event_lns()`, and `csio_ln_down()` cascade events to remote nodes and child NPIV lnodes.
- State handlers `csio_lns_uninit()`, `csio_lns_online()`, `csio_lns_ready()`, and `csio_lns_offline()` implement local-node lifecycle.
- `csio_get_phy_port_stats()` reads FCoE port stats over three mailbox reads.
- `csio_fcoe_fwevt_handler()` demultiplexes firmware FCoE link commands, RDEV payloads, and ELS/CT completions.
- Public lifecycle APIs include `csio_lnode_start()`, `csio_lnode_stop()`, `csio_lnode_close()`, `csio_lnode_init()`, and `csio_lnode_exit()`.
- Management request helpers `csio_ln_prep_ecwr()`, `csio_ln_mgmt_submit_wr()`, and `csio_ln_mgmt_submit_req()` build and submit ELS/CT work requests through the management EQ.

## Control Flow and State
Firmware link-up events call `csio_handle_link_up()`, associate or allocate an lnode for the VNP, set `fcf_flowid`/`vnp_flowid`, and post `CSIO_LNE_LINKUP`. In `uninit` or `offline`, link-up moves the lnode to `online`, reads FCF info for physical lnodes, and reads VNP parameters. Later RDEV fabric-login events map through `fwevt_to_lnevt` to `CSIO_LNE_FAB_INIT_DONE`, moving `online` to `ready` and sending FC link-up async notifications.

Link-down and driver stop paths post `CSIO_LNE_LINK_DOWN` or `CSIO_LNE_DOWN_LINK`, move ready lnodes to `offline`, fan out `CSIO_RNFE_DOWN` to rnodes, send FC link-down notifications, and remove physical FCF list entries. Close paths move lnodes to `uninit` and close rnodes. `csio_notify_lnodes()` is called by hardware state changes to start, stop, reset, or remove all lnodes.

## State and Persistence Behavior
Each `struct csio_lnode` persists WWNs, NPort ID, MAC, FCF/VNP flowids, FCF info reference, FDMI management request/DMA buffer, child list, rnode list, FC transport state, target discovery counters, flags, and stats. Root and non-root physical lnodes own FCF info allocations; NPIV lnodes share the parent's FCF info by kref. FDMI allocates one `csio_ioreq` and a 2048-byte coherent DMA buffer per eligible physical lnode.

## Dependencies and Integration Points
The file integrates with mailbox command builders, work-request submission, SCSI target discovery, FC transport async events, kernel UTS name for FDMI OS/host attributes, and rnode registration. `csio_fcoe_fwevt_handler()` is called from the firmware-event worker in the hardware module. `csio_lnode_start()`/`stop()` are invoked by probe, hardware notifications, and port disable/enable flows.

## Risks and Edge Cases
- In `csio_handle_link_up()`, the allocation path for a new VN-Port drops and reacquires `hw->lock`; code must ensure the intended `ln` pointer is updated after allocation.
- FDMI uses a single `ln->mgmt_req`; overlapping FDMI sequences on one lnode would contend for the same request/DMA buffer.
- `csio_ln_mgmt_submit_req()` uses `BUG_ON(pld_len > pld->len)`, so malformed callers can crash the kernel instead of returning an error.
- State handlers contain TODO comments for hardware reset on FCF/VNP read failure; current behavior increments errors but may leave the lnode partly online.
- FCF info reference handling differs between root, physical non-root, and NPIV lnodes; teardown ordering must avoid kref underflow or leaks.
- Management WR completion trusts the firmware cookie as an `ioreq` pointer after validating active queue membership.

## Test Signals
Important tests include link-up to ready transition, link-down to offline transition, repeated link-up/down drops, invalid FCF/VNP/rdev IDs, FDMI enable/disable, management WR completion, NPIV child allocation/removal, and SCSI scan completion heuristics in `csio_scan_done()`. Runtime signals include FC async link events, correct WWPN/WWNN attributes, FCF list membership, rnode close fan-out, and no lingering management active queue entries.
