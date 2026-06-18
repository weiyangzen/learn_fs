# sources/distributed-fs/ceph-client/drivers/scsi/elx/efct/efct_xport.c

## Purpose
`efct_xport.c` is the EFCT transport/lifecycle bridge between PCI driver probe/remove, HW initialization, SCSI/FC transport registration, target-core setup, debugfs, link control, stats, Scsi_Host objects, and NPIV vports. It owns the top-level `struct efct_xport` allocation, attach/initialize/detach/free flow, FC transport templates, and host attribute callbacks.

## Important APIs, Types, and Functions
Lifecycle APIs are `efct_xport_alloc`, `efct_xport_attach`, `efct_xport_initialize`, `efct_xport_detach`, `efct_xport_control`, `efct_xport_status`, and `efct_xport_free`. SCSI/FC registration APIs are `efct_scsi_new_device`, `efct_scsi_del_device`, `efct_scsi_reg_fc_transport`, `efct_scsi_release_fc_transport`, `efct_scsi_new_vport`, and `efct_scsi_del_vport`. FC transport callbacks include host port ID/type/state/speed/fabric name, stats get/reset, LIP issue, and vport create/delete/disable. Debugfs helpers create/remove an `efct/sessions` tree.

## Control Flow
Probe-side attach calls `efct_hw_setup`, parses receive filters, and creates the software IO pool sized by HW SGL capability. Initialize sets pending-IO counters/lists, calls `efct_hw_init`, initializes the target device and Scsi_Host, starts the stats timer, and creates debugfs. Detach tears target and Scsi_Host state down, deletes the stats timer, tears HW down, and removes debugfs. Free releases the IO pool and xport object.

Port control maps xport commands to HW link init/shutdown. Shutdown gracefully downs the link unless a reset is required, registers a domain-free completion callback, waits for domain shutdown with timeout, unregisters the callback, and deletes saved vports. Status calls return configured state, derived online/offline state from link speed, cached stats, or synchronous stat reset via mailbox completion callbacks.

FC host setup allocates a target-mode `Scsi_Host`, stores `struct efct_vport` in hostdata, sets queue depth/SGL/CDB limits, attaches the FC transport template, adds the host with DMA, and fills symbolic name, classes, supported speeds, WWNN/WWPN, and NPIV limit. NPIV vport creation allocates a separate Scsi_Host with the vport transport template and stores it in `fc_vport->dd_data`.

## State and Persistence Behavior
All state is volatile. `struct efct_xport` holds pending IO list/counters, configured link state, requested WWNs, cached FC stats, FCP counters, and stats timer. Static globals hold FC transport templates and debugfs root/count. Stats are refreshed every 3 seconds through asynchronous HW mailbox calls and copied into FC host statistics on request.

## Dependencies and Integration Points
This file integrates with the PCI-owned `struct efct`, HW layer, IO pool, target-core glue, SCSI midlayer, FC transport class, fc_vport APIs, EFC domain shutdown callbacks, debugfs, timers, completions, and SLI link capability reporting. Probe/remove paths in `efct_driver.c` call into this lifecycle.

## Risks
The stats timer reinitializes with `timer_setup` on each refresh before `mod_timer`, which is unusual and should be checked for races with detach. Detach uses `timer_delete` only if pending; a callback already running may still access xport/HW. `efct_scsi_new_device` and `efct_scsi_new_vport` can leak `Scsi_Host` allocations if `scsi_add_host_with_dma` fails without `scsi_host_put`. Debugfs root refcounting is global and assumes balanced per-device session dirs. `dd_fcvport_size` is hard-coded to 128 with a comment indicating it should be a real sizeof. Shutdown timeout still proceeds after warning, so tests should ensure resources remain valid.

## Test Signals
Probe/remove, attach failure, HW init failure, target init failure, Scsi_Host add failure, debugfs create/remove with multiple devices, stats timer during detach, FC transport register/unregister, link online/offline/LIP, domain shutdown timeout, NPIV create/delete, host attribute reads under no-domain and online-domain states, and stats reset completion behavior are the key signals.
