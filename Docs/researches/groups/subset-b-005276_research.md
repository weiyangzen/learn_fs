# subset-b-005276 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/port.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/port.c

Purpose: implements the Intel SCU ISCI port object. It binds one logical port to zero or more phys, exposes port properties to the rest of the driver, forwards link and broadcast notifications to libsas, programs VIIT and port task scheduler registers, manages a dummy RNC/task hardware workaround, and gates I/O through a port state machine.

Important APIs/types/functions: public entry points include `sci_port_construct()`, `sci_port_start()`, `sci_port_stop()`, `sci_port_add_phy()`, `sci_port_remove_phy()`, `sci_port_link_up()`, `sci_port_link_down()`, `sci_port_start_io()`, `sci_port_complete_io()`, `sci_port_get_properties()`, `sci_port_setup_transports()`, `sci_port_broadcast_change_received()`, `isci_port_perform_hard_reset()`, `isci_ata_check_ready()`, `isci_port_formed()`, and `isci_port_deformed()`. Internal helpers validate PHY masks, derive local/remote SAS addresses, post/invalidate dummy remote nodes, update VIIT entries, suspend/resume the port task scheduler, and translate core events into libsas notifications.

Control flow: construction initializes the state machine in `SCI_PORT_STOPPED`, clears masks, sets a dummy logical index, installs `port_timeout()`, and leaves MMIO pointers to host setup. `sci_port_start()` allocates dummy scheduler resources, validates the current PHY mask against hardware-supported wide-port layouts, and transitions through `SCI_PORT_READY` into waiting or operational ready substates. Link-up events either activate the first PHY, verify attached SAS-address compatibility for wide ports, or report invalid link-up; link-down deactivates the PHY, optionally notifies libsas, and drops to waiting when no active phys remain. Hard reset selects an active PHY, calls `sci_phy_reset()`, starts a timeout, moves to resetting, and wakes waiters from success/failure completion.

State and persistence: runtime state is entirely in `struct isci_port`: active/enabled PHY masks, last active PHY, request count, assigned device count, hang-detection user count, not-ready reason, reset-pending bit, reserved dummy RNI/tag, PHY table, and MMIO register pointers. Hardware-visible state is persisted only while the controller is running via VIIT entries, port task scheduler control bits, PE-to-port configuration registers, and dummy RNC/task contexts. No state survives driver unload or controller reset.

Dependencies and integration points: depends on libsas for `sas_notify_port_event()`, `sas_notify_phy_event()`, `sas_phy_disconnected()`, and `asd_sas_port.lldd_port`; on ISCI host/phy/request/controller helpers for locks, timers, tag/RNI allocation, task contexts, and request posting; and on `registers.h` SCU bit definitions for MMIO programming. `isci_port_formed()` waits for host startup before mapping a libsas port to the active ISCI port; `isci_port_link_down()` marks remote devices gone before libsas removal callbacks arrive.

Risks: the state machine is sensitive to request-count balance because stop and reconfiguration completion depend on `started_request_count` reaching zero. Wide-port validation relies on both PHY mask legality and attached SAS-address equality; stale or reordered link notifications can produce invalid-link warnings or delayed libsas updates. The dummy RNC/task workaround has strict ordering, readl flushes, and microsecond delays; missed abort/invalidate sequencing can affect scheduler fairness or power-down. Hard reset suppresses user link notifications while resetting, so failure paths must synthesize link-down when the port loses all phys. Test signals include manual and automatic port layouts, SATA refusal on wide ports, broadcast-change notification, hard-reset success/timeout, start/stop with outstanding I/O, link flap during reset, and request-count underflow warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/port.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/port.h

Purpose: declares the ISCI port contract shared by host, PHY, request, and remote-device code. It defines the port state container, public port lifecycle and event APIs, state IDs, property structures, not-ready reasons, and request-count helpers.

Important APIs/types/functions: `struct isci_port` holds controller ownership, libsas-facing remote-device list, state-machine object, reset state, PHY masks, dummy scheduler resources, request counters, and MMIO pointers. `enum sci_port_states` enumerates stopped, stopping, ready, ready substates, resetting, and failed. `struct sci_port_properties` and nested endpoint properties report local/remote SAS addresses, protocols, and PHY mask. Public prototypes cover construction, start/stop, PHY add/remove, link up/down, I/O start/complete, hard reset, broadcast change, hang-detection timeout, SAS address accessors, and libsas formed/deformed callbacks.

Control flow: the header does not execute code beyond small helpers. `sci_port_decrement_request_count()` guards request-count underflow with `WARN_ONCE()`, while `sci_port_active_phy()` tests active membership. The declared functions are implemented mostly in `port.c` and are called by host startup, PHY event handling, remote-device I/O, and libsas callbacks.

State and persistence: `struct isci_port` is the authoritative in-memory state for a logical/physical port. It tracks transient masks, counters, reset status, timer state, not-ready reasons, and hardware-resource reservations; no persistent storage is defined here. The `IPORT_RESET_PENDING` bit is used as a wait condition for hard-reset completion.

Dependencies and integration points: includes libsas plus ISCI local headers for host, SAS, and PHY types. Forward declarations avoid cycles with request and remote-device types. MMIO pointer members tie the port to SCU register structs from `registers.h`.

Risks and test signals: because the struct is shared across multiple driver subsystems under `ihost->scic_lock`, field ownership must remain clear during refactors. Request-count underflow warnings, reset wait completion, state-name coverage, and compile-time prototype consistency are key signals. Tests should exercise all declared state transitions through `port.c`, plus SATA readiness checks through `isci_ata_check_ready()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/port_config.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/port_config.c

Purpose: implements the controller port-configuration agent that turns OEM/user PHY configuration and link events into valid ISCI port membership. It supports manual port configuration from OEM PHY masks and automatic port configuration that discovers narrow or wide ports from PHY SAS addresses and link timing.

Important APIs/types/functions: public functions are `sci_port_configuration_agent_construct()`, `sci_port_configuration_agent_initialize()`, and `is_port_config_apc()`. Internal helpers compare SAS addresses, find an existing matching port, validate SCU-supported port ranges, validate manual PHY masks, validate automatic same-address PHY groupings, handle MPC/APC link up/down events, and process reconfiguration timers.

Control flow: construction clears ready/configured masks, handlers, timer-pending state, and valid-port ranges. Initialization reads `ihost->oem_parameters.controller.mode_type`; manual mode validates OEM `ports[].phy_mask`, pre-adds phys to fixed logical ports, installs MPC handlers, and uses a short reconfiguration timer. Automatic mode derives valid port ranges from contiguous equal PHY SAS addresses, installs APC handlers, and uses a wait-for-link-up timer to resolve ambiguous wide-port possibilities. Link-up updates ready masks and either immediately calls `sci_port_link_up()` or delays until a timer can choose a better port grouping. Link-down removes ready/configured bits and removes phys from ports in APC mode.

State and persistence: state lives in `struct sci_port_configuration_agent` inside the host: `phy_ready_mask`, `phy_configured_mask`, `phy_valid_port_range[]`, function pointers, a timer, and `timer_pending`. OEM parameters are read-only inputs loaded elsewhere. Timer callbacks run under `ihost->scic_lock` and reconcile ready-but-unconfigured phys.

Dependencies and integration points: depends on `host.h` and therefore the host, port, and PHY APIs. It calls `sci_phy_get_sas_address()`, `sci_port_add_phy()`, `sci_port_remove_phy()`, `sci_port_link_up()`, `sci_port_link_down()`, `sci_port_is_valid_phy_assignment()`, and controller readiness helpers. It is the bridge between OEM configuration data from `probe_roms.h` and runtime port objects in `port.c`.

Risks: hardware-supported layouts are narrow: port 0 can own 0/0-1/0-3, port 1 only PHY1, port 2 PHY2 or PHY2-3, and port 3 only PHY3. Incorrect OEM masks, duplicate PHY assignment, nonmatching SAS addresses inside a manual wide port, or PHY1/PHY2 illegal grouping fail initialization. APC timer races can temporarily leave phys ready but unconfigured; controller-ready transition depends on timer completion. Test signals include valid/invalid MPC masks, APC grouping by SAS address, delayed wide-port formation, link-down while timer pending, controller start completion after APC timeout, and masks for every supported SCU topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/port_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/probe_roms.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/probe_roms.c

Purpose: locates and validates ISCI OEM parameter data from platform firmware sources. It can parse a PCI option ROM, load the `isci/isci_firmware.bin` firmware blob, or read the `RstScuO` EFI variable, each yielding a packed `struct isci_orom` used by controller initialization.

Important APIs/types/functions: `isci_request_oprom()` maps the PCI BIOS ROM and scans for `$OEM` blocks containing an `ISCUOEMB` table; `isci_request_firmware()` requests the firmware file, validates the table signature, copies it to devm memory, and applies preproduction silicon AFE defaults for older revisions; `isci_get_efi_var()` reads the EFI vendor variable, validates the OEM header, checksum, and ISCI table signature. `get_efi()` abstracts `CONFIG_EFI`.

Control flow: option-ROM parsing maps the ROM, allocates a destination, walks in `$OEM` signature-sized increments, copies the OEM header and payload, computes an additive checksum over header plus full destination table, validates the inner ISCI signature, then unmaps the ROM. Firmware loading validates minimum size and signature before devm-copying. EFI loading allocates a 1 KiB buffer, asks firmware for the variable, treats data after `struct isci_oem_hdr` as the ISCI table, and performs the same signature/checksum checks.

State and persistence: this file creates devm-managed in-memory copies of firmware tables; it does not persist changes. The returned pointers are owned by the PCI device lifetime. Firmware blobs and EFI variables are persistent platform inputs but are treated as read-only.

Dependencies and integration points: depends on Linux PCI BIOS ROM mapping, firmware loader, EFI runtime services, device-managed allocation, and ISCI silicon revision helpers such as `is_c0()`/`is_c1()`. The returned `struct isci_orom` matches definitions in `probe_roms.h` and feeds host OEM parameters used by port configuration and PHY tuning.

Risks: option-ROM scanning advances by four bytes and trusts `oem_hdr.len` enough to compute `copy_len = min(oem_hdr.len - sizeof(oem_hdr), sizeof(*rom))`; malformed short lengths can underflow before `min()`. The checksum loop always sums `sizeof(*rom)` bytes, even when less was copied from OROM. Firmware loading allocates `fw->size` bytes for a `struct isci_orom *` result, so consumers must only rely on known table layout. EFI reading assumes 1 KiB is sufficient. Test signals include missing/invalid firmware, bad signatures, checksum failures, short/oversized tables, EFI-disabled builds, and revision-specific AFE override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/probe_roms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/probe_roms.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/probe_roms.h

Purpose: defines the persistent OEM parameter table format and the user/OEM parameter structures consumed by ISCI controller, PHY, and port setup. It also declares the firmware/option-ROM/EFI loaders from `probe_roms.c`.

Important APIs/types/functions: `struct sci_user_parameters` contains per-PHY spin-up, ALIGN insertion, and max-speed settings plus controller-wide spin-up and inactivity/occupancy timeouts. `enum sci_port_configuration_mode` selects manual or automatic port configuration. `struct sci_oem_params` contains controller mode, spin-up, SSC, cable length, per-port PHY masks, per-PHY SAS addresses, and AFE TX amplitude controls. `struct isci_orom` wraps an ISCI BIOS table header plus two controller parameter blocks. Validation and lookup prototypes include `sci_oem_parameters_validate()`, `isci_request_oprom()`, `isci_request_firmware()`, and `isci_get_efi_var()`.

Control flow: the header has no runtime flow. Its constants and packed structs define the binary contract that `probe_roms.c` validates and host initialization copies into live controller settings. Comments document the interpretation of port mode: APC is selected when no explicit PHY masks are provided, while any explicit mask implies MPC.

State and persistence: `struct isci_orom` mirrors persistent firmware data. `struct sci_user_parameters` is runtime driver configuration, typically derived from defaults/module parameters. All table structs are packed, so field order and width are ABI-sensitive.

Dependencies and integration points: under `__KERNEL__`, the header includes firmware, PCI, EFI, and ISCI definitions; outside the kernel it supplies small SCI dimension constants for tooling. It is consumed by host initialization, port configuration, PHY setup, and ROM/EFI/firmware probing.

Risks and test signals: packed bitfields and versioned table constants make compatibility fragile across compilers and firmware revisions. Port masks must remain within `0x0..0xf`, max speed within generation 3, and controller count/PHY count fixed at current hardware limits. Test signals include OEM validation for each supported ROM version, APC/MPC mode derivation, boundary values for speed and PHY masks, endianness of SAS address fields, and ABI size checks for packed structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/probe_roms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/registers.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/registers.h

Purpose: defines the Intel SCU memory-mapped register layout, register offsets, bit masks, and helper macros used by the ISCI driver. It is the low-level hardware contract for SMU, SDMA, transport/link layers, port task schedulers, VIIT/IIT tables, SGPIO, AFE, scratch RAM, and protocol engine groups.

Important APIs/types/functions: generic helpers include `SCU_GEN_VALUE()`, `SCU_GEN_BIT()`, `SCU_SET_BIT()`, and many register-family-specific generators such as `SMU_*_GEN_*`, `SCU_UFQ*`, `SCU_SAS_*`, and `SCU_PTS*`. Major structs include `scu_viit_entry`, `scu_iit_entry`, `smu_registers`, `scu_sdma_registers`, `scu_transport_layer_registers`, `scu_link_layer_registers`, `scu_sgpio_registers`, `scu_port_task_scheduler_registers`, `scu_port_task_scheduler_group_registers`, `scu_afe_transceiver`, `scu_afe_registers`, `scu_peg_registers`, and top-level `scu_registers`.

Control flow: there is no executable control flow. The file provides constants and C struct overlays used with `readl()`/`writel()` from other files. Drivers compute bitfield values with the macros, then write through pointers to these structs after BAR mapping.

State and persistence: all state represented here is hardware state in MMIO registers or controller RAM windows. Software state is not stored in this header. Register effects persist until hardware reset, driver reprogramming, or power state changes.

Dependencies and integration points: consumed broadly by ISCI host, PHY, port, request, and remote-node context code. `port.c` uses VIIT status fields, link-layer control, port task scheduler control, and hang-detection registers. `remote_device.c` posts context commands through host helpers whose bit layouts come from related SCU definitions. Host initialization uses SMU, SDMA, completion queue, task-context, and AFE layouts.

Risks: this file is typo-sensitive because a single wrong mask, shift, offset, or reserved range corrupts hardware programming. There are visible suspicious definitions worth review, including `SCU_CLEAR_BIT(name, reg_value)` containing `((reg_value)$ ~(SCU_GEN_BIT(name)))`, `SCU_SDMA_UNSOLICITED_FRAME_QUEUE_GET_CYCLE_BIT_MASK` defined as `(12)` rather than a shifted mask, `SCU_UFQGP_CYCLE_BIT(value)` passing an extra argument to `SCU_UFQGP_GEN_BIT`, and `SCU_UFQGP_GET_POINTER(value)` referencing `SCU_UFQGP_GEN_VALUE` while only `SCU_UFQGP_GEN_VAL` is defined. These may be dead macros, but compile coverage should confirm.

Test signals: build tests with all ISCI paths enabled are essential because many macros are only compiled when referenced. Hardware or MMIO-emulation tests should validate register offsets with `offsetof()`, queue pointer encoding, task scheduler suspend/enable bits, VIIT programming, link-layer speed/timeout fields, SGPIO offsets, and AFE register programming against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_device.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_device.c

Purpose: implements ISCI remote-device lifecycle, RNC management, STP/SMP/SAS device state handling, I/O start/complete paths, unsolicited frame/event dispatch, abort/terminate/suspend/resume flows, and libsas device-found/device-gone integration.

Important APIs/types/functions: public functions include `sci_remote_device_suspend()`, `sci_remote_device_stop()`, `sci_remote_device_frame_handler()`, `sci_remote_device_event_handler()`, `sci_remote_device_start_io()`, `sci_remote_device_start_task()`, `sci_remote_device_complete_io()`, `sci_remote_device_post_request()`, `sci_remote_device_resume()`, `isci_remote_device_resume_from_abort()`, `isci_remote_device_found()`, `isci_remote_device_gone()`, `isci_remote_device_stop()`, `isci_remote_device_suspend_terminate()`, `isci_remote_device_terminate_requests()`, `isci_remote_device_is_safe_to_abort()`, `sci_remote_device_abort_requests_pending_abort()`, and `isci_dev_set_hang_detection_timeout()`. Internal construction splits direct-attached and expander-attached devices and shares `sci_remote_device_construct()`.

Control flow: libsas discovery calls `isci_remote_device_found()`, which allocates a device slot, links it to the port, starts construction, resumes the RNC, transitions from initial to stopped to starting, and waits for ready. Ready entry chooses STP idle for SATA, SMP idle for expanders, or generic ready for SSP end devices. I/O start first starts the port, then the RNC, then the request; STP non-NCQ commands move to CMD with a single `working_request`, NCQ commands move/stay in NCQ, SMP commands move to SMP_CMD, and reset/task paths use partial-success callbacks while the RNC resumes. Completion unwinds request, port, and device counts and transitions back to idle or await-reset as needed.

State and persistence: `struct isci_remote_device` tracks flags, kref, libsas domain device, owning port, state machine, port width, connection rate, RNC, request count, working request, not-ready reason, and abort-resume callback. Device slots are reused from `ihost->devices[]`; `IDEV_ALLOCATED`, `IDEV_GONE`, `IDEV_IO_READY`, and abort-path bits control lookup and teardown. Hardware state is held in the remote node context until destructed. No state is persistent beyond the device/controller lifetime.

Dependencies and integration points: depends on libsas `domain_device`, ISCI port/request/task/host helpers, `remote_node_context` APIs, SCU event-code decoding, unsolicited frame control, and controller request posting. Port request counts are balanced through `sci_port_start_io()`/`sci_port_complete_io()`. Device removal disables `domain_dev->lldd_dev`, marks `IDEV_GONE`, stops the RNC, waits for stop, and deconstructs when stopped.

Risks: request-count and kref balance are critical; `sci_remote_device_start_request()` increments only after successful start, and completion must call `isci_put_device()`. Abort and terminate paths wait up to 10 seconds for suspend-count changes or device emptiness; stale RNC callbacks or missing wakeups can delay error recovery. STP NCQ error handling transitions on SDB or D2H error FIS and terminates outstanding requests, so READ LOG/reset recovery must be coordinated by upper layers. `isci_remote_device_gone()` logs `idev->isci_port` before checking `idev`, so unexpected NULL `lldd_dev` would be unsafe. Test signals include discovery/removal, direct vs expander construction, SATA NCQ/non-NCQ concurrency rules, SMP single-command behavior, RNC suspend/resume events, I_T nexus timeout, abort of one request vs all requests, stop with outstanding I/O, and link-hang timeout enable/disable refcounting through the port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_device.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_device.h

Purpose: declares the ISCI remote-device data structure, state IDs, flags, reference helpers, and public lifecycle/I/O/error-recovery APIs used by libsas callbacks, request handling, and remote-node context code.

Important APIs/types/functions: `struct isci_remote_device` contains flags, `kref`, port/domain-device links, list node, state machine, port width, link rate, owning port, RNC, started request count, SATA/SMP `working_request`, not-ready reason, and abort-resume callback storage. Flags include start/stop pending, allocated, gone, I/O ready, NCQ error, link-hang detection, and abort-path state. `enum sci_remote_device_states` covers initial/stopped/starting/ready, STP idle/CMD/NCQ/error/await-reset, SMP idle/CMD, stopping/failed/resetting/final. Inline helpers implement lookup and reference management under the host lock.

Control flow: the header does not contain the state-machine implementation, but its prototypes define the callable flow: libsas calls found/gone; request code starts and completes I/O/tasks; error paths suspend, terminate, abort, resume, reset, or stop devices; RNC callbacks map back to devices with `rnc_to_dev()`.

State and persistence: remote-device lifetime is controlled by `IDEV_ALLOCATED`, `IDEV_GONE`, and `kref`. `isci_lookup_device()` refuses gone devices and bumps the reference for safe use. `sci_remote_device_decrement_request_count()` warns on underflow. All state is volatile runtime state; persistent device identity remains in libsas/domain discovery, not in this structure.

Dependencies and integration points: includes libsas, Linux kref, remote node context headers, and `port.h`. The type is central to `remote_device.c`, request execution, abort handling, and port teardown. `scics_sds_remote_node_context_callback` integration lets abort recovery preserve and chain RNC callbacks.

Risks and test signals: reference helpers must be called under `scic_lock` as documented; otherwise gone-device races are possible. Request-count underflow, stale `working_request`, abort-resume callback overwrites, and incorrect ready flag transitions are primary risks. Build tests should catch prototype drift, while runtime tests should cover lookup during removal, kref release clearing flags, and every state declared in `REMOTE_DEV_STATES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/isci/remote_device.h -->
