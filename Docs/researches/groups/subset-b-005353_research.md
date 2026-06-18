# subset-b-005353 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_iscsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_iscsi.c

## Purpose

`scsi_transport_iscsi.c` implements the Linux SCSI iSCSI transport class. It is the shared control plane between iSCSI low-level drivers, the SCSI midlayer, and userspace iSCSI management daemons. It publishes iSCSI transport, endpoint, interface, host, session, connection, and flashnode objects through the Linux device model; dispatches NETLINK_ISCSI userspace commands; emits asynchronous iSCSI events; coordinates session blocking and recovery; and provides BSG vendor passthrough for host-level iSCSI requests.

This file is not a PDU data-path implementation. Software and offload drivers provide a `struct iscsi_transport` callback table, and this class turns those callbacks into stable SCSI/sysfs/netlink APIs used by open-iscsi, firmware-offload tools, and the SCSI error handler.

## Important APIs, Types, and Functions

`struct iscsi_internal` wraps a `struct scsi_transport_template`, the registered `struct iscsi_transport`, the transport-class device, and transport containers for sessions and connections. Registered transports are tracked on `iscsi_transports` under `iscsi_transport_lock`; `iscsi_register_transport()` and `iscsi_unregister_transport()` are the public attach/release points.

Endpoint APIs are `iscsi_create_endpoint()`, `iscsi_destroy_endpoint()`, `iscsi_lookup_endpoint()`, and `iscsi_put_endpoint()`. Endpoints are numbered from an IDR beginning at 1 for userspace compatibility and expose a handle under `/sys/class/iscsi_endpoint`.

Interface and firmware flashnode APIs include `iscsi_create_iface()`, `iscsi_destroy_iface()`, `iscsi_create_flashnode_sess()`, `iscsi_create_flashnode_conn()`, `iscsi_find_flashnode_sess()`, `iscsi_find_flashnode_conn()`, `iscsi_destroy_flashnode_sess()`, and `iscsi_destroy_all_flashnode()`. Attribute visibility is delegated to `transport->attr_is_visible()`.

Session and connection lifecycle APIs include `iscsi_alloc_session()`, `iscsi_add_session()`, `iscsi_remove_session()`, `iscsi_free_session()`, `iscsi_force_destroy_session()`, `iscsi_alloc_conn()`, `iscsi_add_conn()`, `iscsi_remove_conn()`, `iscsi_get_conn()`, and `iscsi_put_conn()`. Recovery helpers include `iscsi_block_session()`, `iscsi_unblock_session()`, `iscsi_block_scsi_eh()`, `iscsi_session_chkready()`, and `iscsi_is_session_online()`.

Event APIs include `iscsi_recv_pdu()`, `iscsi_offload_mesg()`, `iscsi_conn_error_event()`, `iscsi_conn_login_event()`, `iscsi_post_host_event()`, `iscsi_ping_comp_event()`, and `iscsi_session_event()`. Debug hooks are exposed through exported tracepoints and `iscsi_dbg_trace()`.

## Control Flow

Module initialization registers the iSCSI transport, endpoint, and iface classes; the host, connection, and session transport classes; the flashnode bus; a NETLINK_ISCSI socket; and the `iscsi_conn_cleanup` workqueue. Exit unwinds those registrations and releases the netlink socket and cleanup workqueue.

Transport registration creates a device under `iscsi_transport`, exposes the transport handle and capabilities, registers host/connection/session attribute containers, sets the SCSI user scan hook, and appends the transport to the global list. Unregistration takes `rx_queue_mutex`, removes the transport from the list, unregisters all containers, removes the sysfs group, and unregisters the transport device so netlink dispatch cannot race a disappearing transport.

Userspace commands arrive in `iscsi_if_rx()`. The function serializes receive processing with `rx_queue_mutex`, validates netlink message sizes, calls `iscsi_if_recv_msg()`, and replies by unicast unless the command sent its own bulk response. `iscsi_if_recv_msg()` requires `CAP_SYS_ADMIN`, resolves the transport handle, pins the transport module, computes the trailing payload length, and dispatches create/destroy session, bind/start/stop connection, send PDU, endpoint connect/poll/disconnect, discovery, parameter, path, iface, ping, CHAP, flashnode, and host-stat operations.

Connection commands are split by state needs. Create, destroy, and stop are handled directly. Bind, start, and send PDU run under `conn->ep_mutex`; they first reject work if kernel cleanup has claimed the connection. A successful bind marks the connection `ISCSI_CONN_BOUND` and links the endpoint to the connection when endpoint callbacks exist. A successful start marks it `ISCSI_CONN_UP`.

Session creation calls the driver `create_session()` callback, records the userspace creator portid, and returns host and session IDs. `iscsi_add_session()` allocates a session ID, creates a per-session workqueue, assigns or allocates a target ID, registers the session device and transport attributes, inserts it on `sesslist`, and emits `ISCSI_KEVENT_CREATE_SESSION`. Removal deletes the session from lookup, cancels recovery/blocking work, marks the session free, unblocks SCSI to fail queued commands, flushes scans and unbinds, removes child connections, unregisters transport state, destroys the workqueue, and deletes the device.

Recovery flow is asynchronous. `iscsi_block_session()` queues work that marks the session failed, blocks targets, and optionally starts `recovery_work`. `iscsi_unblock_session()` cancels block/recovery work, marks the session logged in, unblocks the SCSI target, and flushes completion before returning. If recovery times out, `session_recovery_timedout()` moves failed sessions to free, unblocks targets as transport offline, and calls the driver timeout hook.

## State and Persistence Behavior

All persistence is volatile kernel state. Session IDs come from an atomic counter; SCSI target IDs may be assigned by the caller or allocated from `iscsi_sess_ida`; endpoint IDs are held in `iscsi_ep_idr`. Sessions and connections are also kept in global lookup lists protected by spinlocks. Session state includes `LOGGED_IN`, `FAILED`, and `FREE`; target binding state tracks unbound, allocated, scanned, and unbinding.

Device-model lifetime is central. Sessions hold a SCSI host reference until their release callback; connections hold a parent session device reference; iface release drops its parent host reference; endpoint release removes the IDR entry and frees memory. Flashnode release frees dynamically allocated string fields. Endpoint binding is protected by `conn->ep_mutex` so userspace endpoint disconnect and kernel cleanup do not free offload resources while attributes or callbacks are active.

The `recovery_tmo` sysfs attribute is transport-owned state. Userspace can override it unless the session is already failed/free; netlink parameter setting honors this override. During system shutdown, cleanup forces finite recovery timeouts to zero unless the user explicitly configured a non-timeout behavior.

## Dependencies and Integration Points

The file depends on the SCSI midlayer, transport class framework, Linux device model/sysfs, netlink, workqueues, IDR/IDA allocators, BSG, tracepoints, and UAPI structures from `iscsi_if.h` and `scsi_bsg_iscsi.h`. It integrates with userspace through NETLINK_ISCSI groups for iscsid and offload UIP, with SCSI EH through readiness/blocking helpers, and with driver callbacks for all transport-specific operations.

Drivers decide which attributes exist through `attr_is_visible()` and implement callbacks for endpoint connection, connection/session creation, start/stop/bind/send, parameter get/set, discovery, ping, CHAP, flashnode operations, host stats, BSG requests, and recovery timeout notification.

## Risks and Edge Cases

Connection cleanup is race-prone. Kernel error cleanup, userspace stop/disconnect, endpoint references, and connection state transitions are coordinated with `ISCSI_CLS_CONN_BIT_CLEANUP`, `ep_mutex`, and work flushing; missed ordering can leave resources leaked or callbacks run after endpoint teardown.

Netlink payload validation is uneven because many commands carry non-attribute trailing data. The file checks high-level lengths and string termination before parameter callbacks, but drivers still receive raw blobs for iface, path, CHAP, and flashnode operations.

The session and connection lookup helpers return pointers after dropping spinlocks without taking object references, relying on the serialized userspace/control-plane lifecycles around the lists. Destroy paths that remove from lookup before asynchronous teardown are particularly sensitive.

Attribute permission and visibility are callback-driven. Incorrect driver `attr_is_visible()` or getter behavior can expose unsupported or sensitive fields. Several credential fields are gated by `CAP_SYS_ADMIN` for reads, but the actual returned content is driver supplied.

Flashnode helpers assume a session has at most one flashnode connection child in lookup paths such as login/logout/set-param. Firmware implementations with unexpected child layouts would not be represented well.

## Test Signals

Useful signals include transport register/unregister with all sysfs containers present; endpoint create/lookup/destroy with ID reuse only after release; iface and flashnode visibility for IPv4, IPv6, CHAP, and firmware parameters; create/bind/start/send/stop/destroy connection netlink flows; endpoint disconnect races with `iscsi_conn_error_event()`; session block, unblock, recovery timeout, unbind, and target scan behavior; `iscsi_block_scsi_eh()` return values for failed versus free sessions; host and connection stats multicast responses; CHAP and flashnode netlink operations; BSG vendor command validation; and module unload after active transports have been unregistered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_iscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_sas.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_sas.c

## Purpose

`scsi_transport_sas.c` implements the Linux SCSI Serial Attached SCSI transport class. It models SAS hosts, local PHYs, ports, remote PHYs, end devices, and expanders in the Linux device model, exposes their properties through sysfs, provides SMP BSG passthrough queues, and links SAS topology events to SCSI scanning and target removal.

This is shared infrastructure for SAS LLDDs, not a hardware driver. Drivers attach with `sas_attach_transport()` and use exported allocation/add/delete helpers to publish the SAS topology they discover.

## Important APIs, Types, and Functions

`struct sas_host_attrs` is per-host transport state stored in `shost_data`: the remote-PHY list, a mutex, optional host SMP BSG queue, and monotonically increasing target, expander, and port IDs. `struct sas_internal` is allocated by `sas_attach_transport()` and stores the SCSI transport template, callback table, and attribute containers for host, phy, port, rphy, end-device, and expander classes.

Topology APIs include `sas_phy_alloc()`, `sas_phy_add()`, `sas_phy_free()`, `sas_phy_delete()`, `sas_port_alloc()`, `sas_port_alloc_num()`, `sas_port_add()`, `sas_port_free()`, `sas_port_delete()`, `sas_port_add_phy()`, `sas_port_delete_phy()`, `sas_port_get_phy()`, `sas_port_mark_backlink()`, `sas_end_device_alloc()`, `sas_expander_alloc()`, `sas_rphy_add()`, `sas_rphy_remove()`, `sas_rphy_free()`, `sas_rphy_delete()`, and `sas_rphy_unlink()`.

Removal helpers are `sas_remove_children()` and `sas_remove_host()`. Device predicates include `scsi_is_sas_phy()`, `scsi_is_sas_port()`, and `scsi_is_sas_rphy()`. Device capability helpers include `sas_get_address()`, `sas_tlr_supported()`, `sas_enable_tlr()`, `sas_disable_tlr()`, `sas_is_tlr_enabled()`, `sas_ata_ncq_prio_supported()`, and `sas_read_port_mode_page()`.

## Control Flow

Module initialization registers six transport classes: host, phy, port, generic SAS device/rphy, end device, and expander. `sas_attach_transport()` registers one transport container per class, fills attribute arrays according to the provided `sas_function_template`, installs `sas_user_scan()` as the SCSI user scan hook, and sets `host_size` to hold `struct sas_host_attrs`.

Host setup initializes the remote-PHY list and counters, creates a host BSG queue if the driver has an SMP handler, and derives `shost->opt_sectors` from the DMA device's optimal mapping size. Host removal removes the BSG queue.

A local PHY is allocated under either a host or expander rphy, named by host and PHY number, initialized with `enabled = 1`, and prepared with `transport_setup_device()`. `sas_phy_add()` publishes it with `device_add()`, `transport_add_device()`, and `transport_configure_device()`. Deletion requires that it is no longer linked into any port, then removes the transport/device state and drops the final reference.

A SAS port is allocated under a host or expander and may be numbered by the caller or by the host/expander counter. PHYs are linked into ports with reciprocal sysfs links. Adding an already-linked PHY is permitted only when it is already on the same port; otherwise the code logs and BUGs because a PHY cannot belong to two ports. Deleting a port first deletes any attached rphy, unlinks all member PHYs, removes optional backlink sysfs state, and tears down the device.

Remote PHY add enforces one rphy per port, publishes the rphy, adds optional per-rphy BSG, inserts it into the host `rphy_list`, assigns SCSI target IDs for end devices that advertise SSP, STP, or SATA target protocols, and scans the SCSI target. SSP devices are scanned for wildcard LUNs; STP/SATA devices scan LUN 0. Remote PHY remove removes SCSI targets for end devices or recursively removes children for expanders, unlinks the parent port, removes BSG, and deletes transport/device state.

Manual scans route channel 0 through the SAS rphy list and delegate other channels to the generic SCSI selected scan. Wildcard scans do both channel 0 SAS topology scans and normal scans across channels 1 through `max_channel`.

## State and Persistence Behavior

State is in-memory and scoped to the SCSI host lifetime. The host mutex protects the rphy list and ID counters. Port membership is protected by each port's `phy_list_mutex`. Parent references keep host, port, and rphy devices alive until child release callbacks run.

The topology model preserves no state on disk. Target IDs and expander IDs are increment-only while the host exists. End-device fields such as TLR support, TLR enablement, port mode-page data, and expander strings are cached in their rphy-specific structures and exposed through sysfs.

BSG queues are created for the host and for each rphy only when the driver supplies `smp_handler`. `sas_smp_dispatch()` passes host-level jobs with `rphy == NULL` and rphy-level jobs with the target rphy pointer.

## Dependencies and Integration Points

The file integrates with the SCSI midlayer for host/user scan, target scan, and target removal; the transport class framework for sysfs objects; the device model for topology naming and links; BSG for SMP passthrough; DMA helpers for optimal transfer sizing; and VPD/mode-page helpers for TLR, NCQ priority, and port timing information.

Driver callbacks in `struct sas_function_template` supply SMP handling, PHY setup/release, link error refresh, PHY speed changes, PHY reset, PHY enable/disable, and optional enclosure/bay identifiers. libsas and hardware-specific SAS drivers are the natural producers of these topology objects.

## Risks and Edge Cases

Topology lifetime ordering is strict. A PHY must be removed from its port before `sas_phy_delete()`, and a port's rphy must be removed before port teardown completes. Violations intentionally BUG in several places because the sysfs topology would otherwise become inconsistent.

`sas_rphy_free()` removes the rphy from `rphy_list` even though the list insertion happens in `sas_rphy_add()`. The documented safe use says free is for never-added or removed rphys, so callers must not free an object that was never on the list unless list state has been initialized appropriately.

The file uses incremental IDs rather than IDR reuse, so long-lived hosts with repeated topology churn can grow IDs monotonically. That is expected but visible in sysfs names and target IDs.

Attribute output uses small `snprintf(buf, 20, ...)` buffers for many simple values; this is adequate for fixed numeric SAS fields but would be fragile if reused for longer formatted content. Expander string fields are printed directly from cached driver-provided strings.

SMP BSG dispatch only checks for reply payload space before calling the driver. Request semantic validation and completion behavior are driver responsibilities.

## Test Signals

Useful signals include class registration and release; host attach with optional SMP BSG queue; PHY add/delete and driver setup/release callbacks; link reset, hard reset, enable, speed, and link-error sysfs paths; port creation with one and multiple PHY links; refusal of a PHY already attached to a different port; end-device and expander rphy add/remove; recursive expander child deletion; SCSI target scan behavior for SSP versus SATA/STP devices; manual user scans for channel 0 and wildcard channels; TLR VPD and port mode-page reads; NCQ priority from VPD page 0x89; and BSG SMP dispatch for host and rphy devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_sas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_spi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_spi.c

## Purpose

`scsi_transport_spi.c` implements the SCSI Parallel Interface transport class. It exposes per-host and per-target SPI negotiation attributes through sysfs, derives target capabilities from inquiry data, performs SPI domain validation, formats transfer agreements, builds negotiation/tag messages for LLDDs, and optionally decodes SCSI message bytes for logging.

The file serves legacy parallel SCSI HBAs that attach with `spi_attach_transport()` and provide a `struct spi_function_template` for reading and setting bus negotiation parameters.

## Important APIs, Types, and Functions

`struct spi_internal` wraps a `struct scsi_transport_template` and the LLDD `struct spi_function_template`. Target state lives in `struct spi_transport_attrs` stored in `scsi_target->starget_data`; host state lives in `struct spi_host_attrs` stored in transport host data.

Public transport lifecycle APIs are `spi_attach_transport()` and `spi_release_transport()`. Domain validation APIs are `spi_dv_device()` and `spi_schedule_dv_device()`. Negotiation/logging helpers are `spi_display_xfer_agreement()`, `spi_populate_width_msg()`, `spi_populate_sync_msg()`, `spi_populate_ppr_msg()`, `spi_populate_tag_msg()`, and `spi_print_msg()`.

Important internal functions include `spi_device_configure()` for inquiry-derived capabilities, `spi_setup_transport_attrs()` for default target negotiation state, `target_attribute_is_visible()` for sysfs visibility and writability, `spi_dv_device_internal()` for the validation algorithm, `spi_dv_retrain()` for fallback negotiation, and echo/inquiry compare helpers for validation tests.

## Control Flow

Module initialization registers an SPI-specific SCSI device-info list, seeds a small blacklist that disables Information Units on known tape models, registers the target transport class, registers an anonymous SCSI-device class used for device configuration, and registers the host class. Exit unregisters classes and removes the device-info list.

Attaching a transport allocates `struct spi_internal`, registers target and host containers, sets target and host private data sizes, and stores the driver callback table. The host setup path initializes signalling to unknown. Host configure makes the `signalling` sysfs attribute writable only if the driver has `set_signalling()`.

When a SCSI device is configured, the anonymous device class reads inquiry-derived capabilities: sync, wide, double-transition, DT-only, Information Units, and QAS. The SPI blacklist can force IU support off. Target setup initializes conservative transfer state: invalid period, async offset, narrow width, IU/QAS disabled but max-capable, validation flags clear, and a mutex for domain validation.

Target sysfs attributes are visible only if both the target capability and driver callbacks support them. Period, offset, width, IU, DT, QAS, flow-control, stream, RTI, precompensation, and hold-MCS settings read through optional driver getters and write through driver setters. Max attributes clamp writes to cached maximums. `revalidate` triggers domain validation on the first child SCSI device.

Domain validation can run synchronously with `spi_dv_device()` or asynchronously with `spi_schedule_dv_device()`. The synchronous path blocks suspend/resume with `lock_system_sleep()`, takes runtime-PM and SCSI-device references, prevents duplicate validation with `dv_in_progress`, allocates a double echo buffer, quiesces the device and target, sets `dv_pending`, takes the target DV mutex, runs `spi_dv_device_internal()`, then resumes and clears state.

The validation algorithm starts at narrow asynchronous transfer and verifies stable inquiry reads. It attempts wide transfer if supported, disables wide if inquiry comparison fails, then negotiates the fastest allowed synchronous/DT settings: max offset, minimum period, optional QAS, IU and IU-related options for fast periods, DT based on bus signalling and target support, and width last. It validates with repeated inquiry reads, reads the actual DT state, optionally discovers an echo buffer, and if present performs write/read pattern tests. On failures, `spi_dv_retrain()` disables IU, then QAS, then backs off the transfer period until validation succeeds or falls back to asynchronous mode.

## State and Persistence Behavior

State is volatile. Per-target fields cache current and maximum negotiation values, capability-derived support bits, DV pending/in-progress flags, and whether initial DV completed. Per-host state caches the SPI signalling mode. There is no persistent store; all settings are rebuilt from driver callbacks, inquiry data, sysfs writes, and domain validation for the life of the SCSI target/host.

DV state has two layers: `spi_dv_pending()` prevents scheduling duplicate work, and `spi_dv_in_progress()` prevents concurrent synchronous validation. The target DV mutex serializes the actual validation body. SCSI runtime-PM references, device references, quiesce/resume, and system sleep locking protect against validation during suspend/resume or device teardown.

## Dependencies and Integration Points

The file depends on the SCSI midlayer, transport classes, SCSI inquiry capability helpers, SCSI device-info blacklist infrastructure, SCSI command execution, runtime PM, system sleep locking, workqueues, target quiesce/resume, tagged-queue helpers, and optional SCSI constants for message decoding.

LLDDs provide `get_*` and `set_*` callbacks for SPI negotiation fields, signalling callbacks, optional `deny_binding()` to suppress transport binding for targets, and callback behavior for actual hardware negotiation. The exported message builders are used by drivers when constructing WDTR, SDTR, PPR, and tag messages.

## Risks and Edge Cases

Domain validation is intrusive: it issues commands, quiesces devices, changes negotiation parameters, and falls back on errors. Incorrect driver setters or devices that misreport echo-buffer support can cause unnecessary speed downgrades; the code handles one known class by skipping write tests on invalid-field WRITE BUFFER responses.

Capability visibility is dynamic. Sysfs attributes appear only when target support and callbacks align, and `spi_target_configure()` forces group updates after capabilities are populated. Drivers that update support bits later must ensure sysfs visibility remains coherent.

Several store paths parse numbers with `simple_strtoul()` and minimal validation. Invalid trailing characters are not rejected for simple numeric attributes. Period parsing accepts fractional nanoseconds but rounds into PPR or SDTR period fields and clamps only high values or minimum-period requirements.

The asynchronous DV wrapper clears `dv_pending` after `spi_dv_device()` also manipulates pending state. The ordering is intentional but depends on the SCSI device reference and work item lifetime being correct.

The transfer-rate display and period conversion tables cover defined PPR periods and then fall back to period * 4 ns. Reserved or future encodings can display as `FAST-?` or `reserved`.

## Test Signals

Useful signals include module init adding and removing the SPI device-info list; host sysfs attributes for signalling, width, and HBA ID; target attributes appearing only for supported capabilities and callbacks; blacklist behavior disabling IU for matching inquiry strings; sysfs writes clamping max offset/width/IU/QAS and minimum period; manual `revalidate` triggering DV; DV fallback from IU to QAS to slower periods to async; echo-buffer discovery and skip handling; runtime-PM and suspend/resume exclusion during DV; formatted transfer agreement logs for async, narrow/wide, ST/DT, and IU/QAS options; and correctness of WDTR, SDTR, PPR, queue tag, and message printing helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_spi.c -->
