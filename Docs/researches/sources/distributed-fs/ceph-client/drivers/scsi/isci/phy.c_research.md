# sources/distributed-fs/ceph-client/drivers/scsi/isci/phy.c

## Purpose

`phy.c` implements Intel SCU phy initialization, link training, event and frame handling, hard/link reset control, libsas phy-control callbacks, and the phy state machine for the `isci` driver. It translates hardware OSSP/link events and unsolicited frames into libsas-visible link-up/link-down, SAS identify-frame, SATA signature-FIS, broadcast-change, and phy counter behavior.

## Important APIs, Types, and Functions

Public/exported functions include `sci_phy_linkrate()`, `phy_get_non_dummy_port()`, `sci_phy_set_port()`, `sci_phy_initialize()`, `sci_phy_setup_transport()`, `sci_phy_resume()`, `sci_phy_get_sas_address()`, `sci_phy_get_attached_sas_address()`, `sci_phy_get_protocols()`, `sci_phy_start()`, `sci_phy_stop()`, `sci_phy_reset()`, `sci_phy_consume_power_handler()`, `sci_phy_event_handler()`, `sci_phy_frame_handler()`, `sci_phy_construct()`, `isci_phy_init()`, and `isci_phy_control()`.

Hardware setup is split into `sci_phy_transport_layer_initialization()` and `sci_phy_link_layer_initialization()`. Internal helpers include `phy_to_host()`, `sciphy_to_dev()`, `phy_sata_timeout()`, `sci_phy_suspend()`, `sci_phy_start_sas_link_training()`, `sci_phy_start_sata_link_training()`, `sci_phy_complete_link_training()`, `phy_event_name()`, `scu_link_layer_set_txcomsas_timeout()`, `scu_link_layer_stop_protocol_engine()`, `scu_link_layer_start_oob()`, and `scu_link_layer_tx_hard_reset()`.

## Control Flow

Initialization writes transport-layer defaults, invalidates the STP remote-node index, enables STP write-data prefetch, programs identify data, source SAS address, phy ID, OOB reset, phy capabilities and parity, spin-up insertion controls, ALIGN insertion frequencies, revision-specific lookup/timeouts, max link rate, rate-change timeout, arbitration timer for A2 hardware, and disables link-layer hang detection. The phy then enters `SCI_PHY_STOPPED`.

Starting requires `SCI_PHY_STOPPED` and transitions into `SCI_PHY_STARTING`. The starting entry stops/suspends the protocol engine, starts OOB, clears protocol/broadcast state, notifies link down if restarting from ready, and enters the starting substate chain. Events then drive protocol selection and speed negotiation: SAS detected moves to SAS speed wait; SATA spin-up hold moves to SATA power wait; SAS/SATA speed events record negotiated link rate; identify timeouts extend TX COMSAS timeout and restart; link failures reset to starting. SAS identify frames are consumed in `SCI_PHY_SUB_AWAIT_IAF_UF`; SATA signature FIS frames are consumed in `SCI_PHY_SUB_AWAIT_SIG_FIS_UF`.

Power gating is coordinated with `host.c`: SAS or SATA power substates enqueue the phy with controller power control. `sci_phy_consume_power_handler()` either enables notify-enable-spinup for SAS or releases SATA spin-up hold and restarts OOB. Successful final substates enter `SCI_PHY_READY`, which calls `sci_controller_link_up()`. Exiting ready suspends the phy and clears STP RNI. Stopped entry deletes SATA timers, stops the protocol engine, and notifies link down for non-initial transitions.

The libsas `isci_phy_control()` callback implements disable, link reset, hard reset, and event counter retrieval. Link reset stops and restarts OOB under `scic_lock`; hard reset delegates to port reset logic; counter retrieval reads link-layer error counters into `struct sas_phy`.

## State and Persistence Behavior

Per-phy runtime state lives in `struct isci_phy`: base state machine, owning port, negotiated speed, protocol, phy index, delayed broadcast-change flag, link-training flag, SATA timer, transport/link register pointers, libsas phy object, SAS address, and last received identify frame or signature FIS. No persistent storage is written. The frame data is protected by `sas_phy.frame_rcvd_lock` when copied from unsolicited frames.

## Dependencies and Integration Points

The file depends on SCU event codes, register bit macros, OEM/user parameters from probe ROM structures, host power-control and link notification APIs, port activation/broadcast APIs, unsolicited-frame control, libsas phy objects, ATA FIS definitions, and PCI revision helpers. It is called from `host.c` during controller initialization, completion/event dispatch, controller start, deinit, and libsas phy management.

## Risks and Edge Cases

The start substate machine has many restart paths for mixed SAS/SATA indications, repeated hardware events, identify timeouts, and link failures. Incorrect state acceptance can strand a phy in link training or report a false link. SATA signature FIS timeout is long, and cancellation relies on the `sci_timer.cancel` convention. `sci_phy_get_attached_sas_address()` copies directly from the received identify frame and is only valid after SAS frame handling. Broadcast changes arriving before port assignment are deferred through `bcn_received_while_port_unassigned`; missed replay would hide topology changes. The hard reset path differs for SSP and non-SSP protocols, so SATA and SAS reset tests must be separate.

## Test Signals

Useful signals include link training at 1.5/3/6 Gbps for SAS and SATA devices, expander identify-frame handling, SATA signature FIS capture, spin-up throttling with multiple direct-attached disks, broadcast-change delivery before and after port assignment, link reset and hard reset through sysfs/libsas, phy counter reads, hotplug link-failure recovery, and suspend/resume reinitializing register pointers and timers.
