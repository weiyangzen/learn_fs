# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vport.c

## Purpose
`lpfc_vport.c` implements LPFC NPIV virtual-port lifecycle management. It creates, enables, disables, deletes, and enumerates LPFC virtual ports requested through the Fibre Channel transport, coordinating VPI allocation, service-parameter reads, WWN validation, fabric FDISC/LOGO/DA_ID sequences, SCSI host registration/removal, sysfs/debugfs attributes, discovery quiesce waits, and reference management.

## Important APIs, Types, And Functions
Public entry points are `lpfc_vport_set_state()`, `lpfc_alloc_vpi()`, `lpfc_vport_create()`, `lpfc_vport_disable()`, `lpfc_vport_delete()`, `lpfc_create_vport_work_array()`, and `lpfc_destroy_vport_work_array()`. Internal helpers include `lpfc_free_vpi()`, `lpfc_vport_sparm()`, `lpfc_valid_wwn_format()`, `lpfc_unique_wwpn()`, `lpfc_discovery_wait()`, `lpfc_send_npiv_logo()`, `disable_vport()`, and `enable_vport()`.

`lpfc_vport_set_state()` mirrors FC transport state into `fc_vport->vport_state` and maps failure-like states to `LPFC_VPORT_FAILED`. `lpfc_alloc_vpi()` and `lpfc_free_vpi()` manage the HBA VPI bitmap, reserving VPI 0 for the physical port and updating SLI-4 `vpi_used`. `lpfc_vport_sparm()` issues a blocking READ_SPARM mailbox and copies service parameters into the vport identities.

## Control Flow
Create flow validates NPIV support (`sli_rev >= 3`, `cfg_enable_npiv`) and rejects creation when NVMe target support is enabled. It allocates a VPI, obtains a driver instance number, creates the port, initializes debugfs, reads service parameters, overlays transport-supplied WWNN/WWPN, validates WWN format and uniqueness, allocates sysfs attributes, configures FCP-only FC4 support, attaches the vport to `fc_vport->dd_data`, sets FDMI flags, and handles SLI-4 VPI initialization. If link/fabric state is not ready or the request is initially disabled, it sets transport state and returns success without FDISC. Otherwise it finds the physical fabric node and issues initial FDISC when fabric NPIV support is advertised.

Disable flow optionally sends NPIV LOGO, stops host I/O, cleans RPI/default-RPI state, stops timers, unregisters VPI, marks SLI-4 vport as needing INIT_VPI, and sets `FC_VPORT_DISABLED`. Enable flow checks link/topology, marks loading, performs deferred INIT_VPI or sets `FC_VPORT_NEEDS_REG_VPI`, then issues FDISC if fabric state permits.

Delete flow rejects physical-port deletion and static-vport deletion except during driver unload. It marks unloading, waits for creation/discovery to settle when not unloading the physical port, takes an early SCSI host reference, removes sysfs/debugfs, optionally issues DA_ID and fabric LOGO, waits for discovery quiesce, removes FC/SCSI hosts, runs LPFC cleanup/host-down/timer stop, unregisters RPIs/VPI or releases the host reference directly, frees the VPI, removes the vport from `port_list`, and drops references.

## State And Persistence
State is volatile per-HBA and per-vport memory. The VPI bitmap persists for the HBA lifetime. Vport state spans FC transport state, `port_state`, `fc_flag`, `load_flag`, `vpi_state`, FDMI masks, sysfs/debugfs attributes, timers, node lists, and discovery counters. There is no disk persistence; static vport policy is represented by runtime flags and transport configuration.

## Dependencies And Integration Points
The file integrates with the SCSI host and FC transport (`fc_vport`, `fc_remove_host()`, `scsi_remove_host()`), LPFC mailbox and SLI helpers, discovery (`lpfc_initial_fdisc()`, `lpfc_set_disctmo()`), name server (`lpfc_ns_cmd()`), ELS LOGO, RPI/VPI unregister paths, sysfs/debugfs, and HBA port-list locking. It uses Linux spinlocks, waitqueues, signals, timers, kthreads/scheduler headers, and PCI/SCSI transport declarations.

## Risks And Edge Cases
Create and delete have many partial-resource paths. VPI allocation, instance allocation, port creation, service-parameter mailbox, sysfs allocation, SLI-4 INIT_VPI, and fabric discovery must unwind consistently. Delete has delicate SCSI host reference ordering: the early `scsi_host_get()` must happen before `scsi_remove_host()`, and unreg_vpi completion may drop a reference. DA_ID and LOGO are best-effort, so fabric may retain stale entries. Discovery waits use bounded sleeps and can return after timeout with teardown continuing. Duplicate WWPN checks rely on `port_list_lock` and must not race list insertion/removal.

## Test Signals
Useful tests include NPIV disabled rejection, NVMe-target rejection, max-VPI exhaustion, service-parameter mailbox timeout and signal paths, invalid and duplicate WWN rejection, create during link down, create before VFI registration, disabled-create then enable, fabric without NPIV support, disable/enable with LOGO and deferred INIT_VPI, delete during active discovery, static-vport delete rejection, driver unload delete path, refcount leak checks, and repeated create/delete stress.
