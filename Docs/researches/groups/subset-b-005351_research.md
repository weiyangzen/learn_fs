# subset-b-005351 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_logging.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_logging.h

## Purpose

`scsi_logging.h` defines the SCSI mid-layer's compile-time gated diagnostic logging macros. It divides the global `scsi_logging_level` word into ten 3-bit fields covering error recovery, timeout handling, scanning, mid-layer queue/complete, low-level queue/complete, high-level queue/complete, and ioctl paths. Call sites use category-specific macros so debug output can be turned on by category and level without sprinkling bit arithmetic through the SCSI code.

## Important APIs, types, and functions

The important public surface is macro-based. `SCSI_LOG_*_SHIFT` and `SCSI_LOG_*_BITS` define each category's bitfield. `SCSI_LOG_LEVEL(SHIFT, BITS)` extracts the active level from `scsi_logging_level` when `CONFIG_SCSI_LOGGING` is enabled and returns zero otherwise. `SCSI_CHECK_LOGGING(SHIFT, BITS, LEVEL, CMD)` conditionally executes an arbitrary logging command if the configured category level is greater than the requested level. The call-site macros, such as `SCSI_LOG_SCAN_BUS()`, `SCSI_LOG_TIMEOUT()`, and `SCSI_LOG_HLCOMPLETE()`, bind those generic helpers to a category.

## Control flow

There is no runtime function body in this header. Control flow is injected at macro expansion sites throughout the SCSI core and upper-level drivers. With logging enabled, each macro performs a cheap level extraction and an `unlikely()` branch around the caller-supplied logging statement. With logging disabled, the macros collapse to no-ops and the supplied logging command is not emitted into the object code.

## State and persistence behavior

The only state dependency is the externally defined `unsigned int scsi_logging_level`, implemented in `scsi.c` and exposed through the `scsi_logging_level` module parameter and the `dev/scsi/logging_level` sysctl. The header itself persists nothing. Logging settings persist only as kernel memory/module/sysctl state until changed or until module/kernel teardown.

## Dependencies and integration points

This header is included by SCSI core files such as scanning, procfs, queueing, completion, and upper-level drivers. It depends on common kernel branch prediction and printk-style logging infrastructure through its call sites. `scsi_sysctl.c` is the administrative integration point for the sysctl path, while `scsi.c` provides the global variable and module parameter.

## Risks and edge cases

The ten 3-bit fields consume 30 bits of the word, so adding categories requires changing the packing scheme. The macro condition uses configured level `>` requested level rather than `>=`, which matters for call-site expectations. Because `CMD` is arbitrary code, it must be side-effect-free except for logging; otherwise behavior would differ between `CONFIG_SCSI_LOGGING` builds and non-logging builds. Since the global value is read locklessly, callers should treat it as best-effort diagnostic state.

## Test signals

Compile coverage should verify both `CONFIG_SCSI_LOGGING=y` and `n` builds. Runtime checks can set the module parameter or sysctl and confirm category-specific logs appear only at expected levels, especially scan logs from `scsi_scan.c`, timeout logs from `sg.c`, and queue/complete logs from `scsi_lib.c` and `sd.c`. Static checks should confirm each shift/width pair stays within the integer width and that new logging categories have sysctl/module parameter reachability through the shared global.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_logging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_netlink.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_netlink.c

## Purpose

`scsi_netlink.c` implements the SCSI transport netlink endpoint for `NETLINK_SCSITRANSPORT`. It creates a kernel netlink socket, validates inbound SCSI transport messages, dispatches supported message classes, and exports `scsi_nl_sock` so transport implementations such as Fibre Channel can multicast events through the same socket.

## Important APIs, types, and functions

`struct sock *scsi_nl_sock` is the exported socket handle. `scsi_netlink_init()` registers the netlink endpoint with `netlink_kernel_create(&init_net, NETLINK_SCSITRANSPORT, ...)`, using `scsi_nl_rcv_msg()` as the receive callback and `SCSI_NL_GRP_CNT` multicast groups. `scsi_netlink_exit()` releases the socket with `netlink_kernel_release()`. The receive path parses `struct nlmsghdr` and `struct scsi_nl_hdr`, checks `SCSI_TRANSPORT_MSG`, `SCSI_NL_VERSION`, `SCSI_NL_MAGIC`, `CAP_SYS_ADMIN`, message length, transport id, and message type.

## Control flow

`scsi_nl_rcv_msg()` loops over every aligned netlink message in the incoming skb. It rejects malformed headers, unsupported message types, invalid protocol version/magic, unprivileged senders, and partial payloads. For `SCSI_NL_TRANSPORT` it currently recognizes `SCSI_NL_SHOST_VENDOR` but only returns `-ESRCH` because no driver dispatch is implemented here; unknown SCSI transport message types get `-EBADR`, and unknown transports get `-ENOENT`. If an error occurred or the sender requested `NLM_F_ACK`, the callback sends `netlink_ack()` before advancing to the next aligned message.

## State and persistence behavior

The persistent state is the global kernel socket pointer. The receive path does not keep per-client sessions or durable message state. Multicast group membership is owned by the netlink core. Message handling is synchronous with skb parsing, and every error is transient except for socket registration failure during init.

## Dependencies and integration points

The file depends on Linux netlink APIs, capability checks, `scsi/scsi_netlink.h`, and `scsi_priv.h` declarations. It integrates with the SCSI subsystem initialization/exit path through `scsi_netlink_init()` and `scsi_netlink_exit()`. Other transport files use `scsi_nl_sock` for event delivery; `scsi_transport_fc.c` checks it and calls `nlmsg_multicast()` to publish FC events.

## Risks and edge cases

The vendor message path is effectively a stub, so user-space requests of that kind receive an error even though the message type is recognized. The parser must be strict about `nlmsg_len`, `hdr->msglen`, and `skb_pull()` alignment to avoid walking malformed skbs. Because `scsi_netlink_exit()` releases the socket but does not clear `scsi_nl_sock`, callers must rely on subsystem teardown ordering to avoid use after release. All inbound messages require `CAP_SYS_ADMIN`, so any future message type added here must consciously preserve or adjust that privilege boundary.

## Test signals

Build with `CONFIG_SCSI_NETLINK` enabled and disabled to validate the real and inline-stub declarations in `scsi_priv.h`. Runtime tests can send invalid netlink type, bad magic/version, partial payloads, and unprivileged messages and assert the expected `netlink_ack()` errors. Transport event tests should enable a producer such as FC transport and confirm multicast events use `scsi_nl_sock` only after successful initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_pm.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_pm.c

## Purpose

`scsi_pm.c` supplies SCSI bus power-management operations. It coordinates system suspend/resume/freeze/thaw/poweroff/restore for SCSI devices, integrates runtime PM with block queue PM, and exposes helper functions for SCSI core and transports to hold and release runtime PM references on devices, targets, and hosts.

## Important APIs, types, and functions

`const struct dev_pm_ops scsi_bus_pm_ops` is the exported PM operations table consumed by `scsi_bus_type` in `scsi_sysfs.c`. System-sleep helpers include `scsi_bus_prepare()`, `scsi_bus_suspend_common()`, and `scsi_bus_resume_common()`, with small callback wrappers for driver PM hooks: `do_scsi_suspend()`, `do_scsi_freeze()`, `do_scsi_poweroff()`, `do_scsi_resume()`, `do_scsi_thaw()`, and `do_scsi_restore()`. Runtime PM helpers include `sdev_runtime_suspend()`, `sdev_runtime_resume()`, and `scsi_runtime_idle()`. Exported or internal reference helpers are `scsi_autopm_get_device()`, `scsi_autopm_put_device()`, `scsi_autopm_get_target()`, `scsi_autopm_put_target()`, `scsi_autopm_get_host()`, and `scsi_autopm_put_host()`.

## Control flow

For system sleep, the bus prepare hook waits for asynchronous scans to complete for host devices. For SCSI device objects, suspend-like paths first call `scsi_device_quiesce()`, then invoke the bound SCSI driver's PM callback if one exists. If the callback fails, the device is resumed to undo quiescing. Resume-like paths call the driver PM callback first and then always call `scsi_device_resume()`.

Runtime suspend for a SCSI device calls `blk_pre_runtime_suspend()` on the request queue, then the driver's `runtime_suspend()`, then `blk_post_runtime_suspend()` with the driver result. Runtime resume mirrors this with `blk_pre_runtime_resume()`, optional driver `runtime_resume()`, and `blk_post_runtime_resume()`. Runtime idle autosuspends SCSI devices and returns `-EBUSY` to keep the PM core from treating the device as fully idle immediately.

## State and persistence behavior

The file mutates runtime PM usage counters and request-queue PM state through the PM core and block layer. It does not own durable storage. System suspend temporarily quiesces device I/O and restores it on resume or suspend failure. `scsi_autopm_get_*()` increments runtime PM references; matching put calls are required to avoid keeping hardware permanently active.

## Dependencies and integration points

The file depends on `linux/pm_runtime.h`, `linux/blk-pm.h`, SCSI device/driver/host types, and `scsi_priv.h`. It integrates with `scsi_sysfs.c` through `scsi_bus_type.pm`, with scanning via `scsi_complete_async_scans()`, with discovery/removal via `scsi_autopm_get_host()`/`put_host()`, and with target/device registration in sysfs code through target and device autopm calls.

## Risks and edge cases

Suspend ordering is sensitive: scanning must finish before host suspend, and device queues must be quiesced before driver callbacks. Runtime PM get helpers treat `-EACCES` as a non-fatal disabled-runtime-PM case but roll back other negative errors; callers need to understand that success can mean PM was forbidden. Missing put calls leak PM references. The target get/put helpers ignore return values, unlike device and host helpers. Driver callbacks may run while transport-specific hooks are absent; the comments explicitly leave host/target/transport runtime hooks for future insertion.

## Test signals

System tests should cover suspend/resume with synchronous and asynchronous scanning, failed driver suspend callbacks, and resume after queued I/O. Runtime PM tests should verify block queue PM transitions, autosuspend scheduling, disabled-runtime-PM behavior, and balanced autopm references during scan, add, remove, and sysfs registration. Compile tests should cover `CONFIG_PM_SLEEP` off, where sleep hooks become `NULL`, and `CONFIG_PM` off, where `scsi_priv.h` supplies stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_priv.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_priv.h

## Purpose

`scsi_priv.h` is the internal SCSI mid-layer header. It gathers private cross-file declarations for host initialization, command setup, device-info tables, error handling, queueing, procfs, scanning, sysctl, sysfs, netlink, power management, device handlers, and BSG registration. It is not a public driver API; it is the glue used by implementation files under `drivers/scsi`.

## Important APIs, types, and functions

The header defines `SCSI_CMD_RETRIES_NO_LIMIT`, internal `enum scsi_ml_status` values, `scsi_ml_byte()`, `SCSI_EH_ABORT_SCHEDULED`, `SCSI_SENSE_VALID()`, and `SCSI_DEVICE_BLOCK_MAX_TIMEOUT`. It declares major SCSI core entry points including `scsi_init_hosts()`, `scsi_init_command()`, `scsi_timeout()`, `scsi_error_handler()`, `scsi_decide_disposition()`, `scsi_queue_insert()`, `scsi_io_completion()`, `scsi_run_host_queues()`, `scsi_scan_host_selected()`, `scsi_forget_host()`, `scsi_sysfs_add_sdev()`, `scsi_sysfs_device_initialize()`, `__scsi_remove_device()`, `scsi_bus_type`, `scsi_shost_groups`, and `blank_transport_template`.

Feature-guarded sections provide real declarations or no-op stubs for procfs, sysctl, netlink, PM, and SCSI device handlers. This allows core initialization and teardown code to call subsystem hooks without scattering `#ifdef`s.

## Control flow

There is no runtime control flow except inline helpers and stubs. The important design is compile-time routing: when optional features are enabled, callers link to the implementing file; when disabled, the inline definitions return success or do nothing. The header therefore centralizes SCSI core feature boundaries and keeps the rest of the mid-layer source files simpler.

## State and persistence behavior

The header owns no state. It exposes stateful objects owned elsewhere, such as `scsi_nl_sock`, `scsi_bus_type`, `scsi_shost_groups`, and the PM operations table. The inline stubs deliberately avoid state changes when a subsystem is disabled.

## Dependencies and integration points

It depends on Linux device infrastructure, `scsi/scsi_device.h`, and `linux/sbitmap.h`, plus forward declarations for SCSI core structures. Nearly every file in this work item includes it: netlink uses socket declarations, PM uses scan declarations, procfs uses scan and host declarations, scanning uses sysfs and PM declarations, and sysfs uses PM and scan helpers. It also bridges to transport classes and upper-level driver registration through `blank_transport_template` and `scsi_bus_type`.

## Risks and edge cases

Because this header is private but broad, changing a declaration can break many SCSI core files at once. Stub semantics matter: returning zero for disabled procfs/sysctl or doing nothing for disabled PM/netlink must match caller assumptions. Internal status values must not leak to low-level drivers, as the comments warn. `SCSI_SENSE_VALID()` only recognizes fixed-format sense with `0x70` response code; callers must not treat it as a universal sense validator.

## Test signals

Build matrix coverage should toggle `CONFIG_SCSI_PROC_FS`, `CONFIG_SYSCTL`, `CONFIG_SCSI_NETLINK`, `CONFIG_PM`, `CONFIG_SCSI_DH`, and `CONFIG_SCSI_LOGGING` to validate both declarations and stubs. Static checks should ensure functions declared here still match their definitions and exports. Integration tests should exercise initialization/exit with optional features disabled to confirm callers tolerate stub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_proc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_proc.c

## Purpose

`scsi_proc.c` implements the legacy `/proc/scsi` interface. It creates `/proc/scsi/scsi` for listing attached SCSI devices and for manual add/remove commands, and it manages per-host-template proc directories and per-host proc files used by older low-level drivers for debugging, statistics, and driver-specific commands.

## Important APIs, types, and functions

`scsi_init_procfs()` and `scsi_exit_procfs()` create and remove the top-level proc entries. `scsi_proc_hostdir_add()` and `scsi_proc_hostdir_rm()` maintain one directory per `scsi_host_template` that implements `show_info`. `scsi_proc_host_add()` and `scsi_proc_host_rm()` create and remove host-number files inside that template directory. `scsi_template_proc_dir()` is exported for drivers that need the template proc directory.

The file's local state is `proc_scsi`, `global_host_template_mutex`, and `scsi_proc_list`, whose entries are `struct scsi_proc_entry` records containing the host template, proc directory, and `present` host count. Proc operations are split between host-specific files (`proc_scsi_ops`) and the global device list/control file (`scsi_scsi_proc_ops`).

## Control flow

For host-specific proc files, open uses `single_open_size()`, show delegates to `shost->hostt->show_info()`, and write copies at most `PROC_BLOCK_SIZE` bytes from user memory before calling `shost->hostt->write_info()`. Host template directory creation is reference-counted by `present`: the first host for a template creates `/proc/scsi/<proc_name>`, later hosts reuse it, and the last removal deletes it.

For `/proc/scsi/scsi`, read uses a `seq_file` iterator over `scsi_bus_type` devices, filters for SCSI device objects, and prints host/channel/id/lun plus INQUIRY vendor/model/rev/type/ANSI data. Write accepts only `scsi add-single-device H C I L` and `scsi remove-single-device H C I L`. Add looks up the host and calls a transport `user_scan()` hook or `scsi_scan_host_selected(..., SCSI_SCAN_MANUAL)`. Remove looks up the host and device and calls `scsi_remove_device()`.

## State and persistence behavior

Procfs entries persist while SCSI procfs is initialized and while host templates/hosts remain registered. The host-template list is protected by `global_host_template_mutex`. Writes to `/proc/scsi/scsi` persist by changing the live SCSI device graph: add may allocate and publish devices through the scan/sysfs path, while remove unregisters devices. The proc files themselves do not store command history.

## Dependencies and integration points

The file depends on procfs, seq_file, user-copy helpers, SCSI host/device/transport APIs, `scsi_priv.h`, and `scsi_logging.h`. It integrates with host registration in `hosts.c`, with scanning in `scsi_scan.c`, with removal in `scsi_sysfs.c`, and with low-level driver callbacks `show_info` and `write_info`. Drivers such as `esas2r` use the exported `scsi_template_proc_dir()`.

## Risks and edge cases

The interface is legacy and string-parsed. `proc_scsi_write()` uses fixed command prefixes and `simple_strtoul()` parsing, so malformed spacing or missing fields can silently become zero values before the called scan/remove path rejects or acts. Host proc writes allocate a single page and pass raw data to low-level drivers; those drivers own validation. The template directory lifetime depends on balanced hostdir add/remove calls and `present` accounting. Device iteration must correctly put references in seq start/next/stop paths; missing puts would leak devices, and extra puts would race with removal.

## Test signals

Procfs tests should verify `/proc/scsi/scsi` creation/removal, attached-device listing, manual add/remove commands, malformed command rejection, and host-template directory reference counting with multiple hosts using the same template. Driver callback tests should cover `show_info` and `write_info` paths. Concurrency tests should read the seq file while devices are added and removed and should exercise repeated host add/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_proto_test.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_proto_test.c

## Purpose

`scsi_proto_test.c` is a KUnit test suite for selected layout definitions in `<scsi/scsi_proto.h>`. It verifies that packed SCSI protocol structures expose expected bitfields and big-endian fields when overlaid on known byte arrays.

## Important APIs, types, and functions

The single test function `test_scsi_proto()` covers `struct scsi_io_group_descriptor`, `struct scsi_stream_status`, and `struct scsi_stream_status_header`. It uses unions containing the protocol struct and an equally sized byte array, then checks bitfields such as `io_advice_hints_mode`, `st_enble`, `cs_enble`, `ic_enable`, `acdlu`, `rlbsr`, `lbm_descriptor_type`, `perm`, and `rel_lifetime`. Multi-byte protocol fields are checked through `get_unaligned_be16()` and `get_unaligned_be32()`. The suite is registered as `scsi_proto` with `kunit_test_suite()`.

## Control flow

When KUnit runs the suite, it invokes `test_scsi_proto()`. The test initializes constant byte arrays, reads the corresponding struct fields, and issues `KUNIT_EXPECT_EQ()` assertions. It has no setup or teardown and no device interaction.

## State and persistence behavior

The test has no persistent state. All data is static constant test input or local KUnit assertion state. It does not register devices, issue SCSI commands, or alter global SCSI settings.

## Dependencies and integration points

The file depends on KUnit, unaligned big-endian access helpers, and `<scsi/scsi_proto.h>`. It integrates with the kernel KUnit test runner and protects consumers of SCSI protocol structs by catching accidental layout or bitfield-order changes in the public protocol header.

## Risks and edge cases

The test relies on C bitfield layout matching the protocol header's intended representation on supported architectures; bitfields are historically compiler- and endian-sensitive, so this suite is valuable but may need architecture coverage. It covers only a small subset of `scsi_proto.h`; passing this suite does not validate every CDB or descriptor definition. The field name `st_enble`/`cs_enble` is intentionally tested as declared, so spelling changes in the header require coordinated test updates.

## Test signals

Run the KUnit suite named `scsi_proto`. Useful signals are all expectations passing on little-endian and big-endian configurations, plus compile success when `scsi_proto.h` changes. Additional future tests should add more representative byte overlays for other protocol descriptors and CDB structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_proto_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_sas_internal.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_sas_internal.h

## Purpose

`scsi_sas_internal.h` defines the private container used by the SAS transport implementation to extend the generic `scsi_transport_template` with SAS-specific function templates, attribute storage, and transport containers. It is an internal bridge between SAS transport code and the shared SCSI sysfs/transport class machinery.

## Important APIs, types, and functions

The header defines fixed attribute-count constants for SAS host, PHY, port, remote port, end-device, and expander attributes. `struct sas_internal` embeds `struct scsi_transport_template t`, pointers to `struct sas_function_template` and `struct sas_domain_function_template`, private arrays of `struct device_attribute`, transport containers for each SAS object class, and null-terminated attribute pointer arrays used by `scsi_sysfs.c`/transport code. `to_sas_internal(tmpl)` maps a generic transport template pointer back to the surrounding SAS-private object.

## Control flow

There is no function flow in the header. SAS transport setup code populates the embedded template, private attributes, and attribute pointer arrays, then passes the generic transport template into SCSI core paths. Later callbacks recover the full SAS object through `to_sas_internal()`.

## State and persistence behavior

Instances of `struct sas_internal` persist as transport-template state allocated by SAS transport registration. The arrays hold per-transport attribute definitions, not per-device dynamic data. The header itself owns no allocation or teardown logic.

## Dependencies and integration points

The header assumes the SAS transport implementation has included definitions for `struct scsi_transport_template`, SAS function templates, device attributes, and transport containers. It integrates with `scsi_transport_sas.c`, generic transport class registration, and sysfs attribute generation for SAS PHYs, ports, remote PHYs, end devices, and expanders.

## Risks and edge cases

The fixed attribute counts must match the number of attributes populated by SAS transport code; under-counting causes array overflow, and over-counting can leave unexpected empty entries. The null-terminated pointer arrays reserve one extra slot; writers must preserve termination. Because the generic template is embedded as the first named member used by `container_of()`, any refactor must keep `to_sas_internal()` synchronized with the struct layout.

## Test signals

Compile SAS transport support and boot with SAS hardware or emulated SAS objects. Sysfs tests should verify expected attribute counts and names for host, PHY, port, rphy, end-device, and expander objects. Static checks should compare the count constants against the initializer code in the SAS transport implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_sas_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_scan.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_scan.c

## Purpose

`scsi_scan.c` implements SCSI target and logical-unit discovery. It allocates targets and devices, probes LUNs with INQUIRY and REPORT LUNS, applies device quirk flags, configures request queues and transport state, publishes discovered devices through sysfs, supports synchronous/asynchronous scanning, manual rescans, device resume/rescan helpers, host teardown, and pseudo-device allocation for host-internal commands.

## Important APIs, types, and functions

Public or cross-file entry points include `scsi_enable_async_suspend()`, `scsi_complete_async_scans()`, `scsi_sanitize_inquiry_string()`, `__scsi_add_device()`, `scsi_add_device()`, `scsi_resume_device()`, `scsi_rescan_device()`, `scsi_scan_target()`, `scsi_scan_host_selected()`, `scsi_scan_host()`, `scsi_forget_host()`, and `scsi_get_pseudo_sdev()`. Target/device internals are centered on `scsi_alloc_target()`, `scsi_target_reap()`, `scsi_alloc_sdev()`, `scsi_probe_lun()`, `scsi_add_lun()`, `scsi_probe_and_add_lun()`, `scsi_report_lun_scan()`, and `scsi_sequential_lun_scan()`.

Important state includes module parameters `max_luns`, `scan`, and `inq_timeout`; `async_scan_lock`; `scanning_hosts`; `struct async_scan_data`; target `reap_ref`; host lists `__targets` and `__devices`; `shost->scan_mutex`; and per-device queue/budget/VPD/inquiry fields initialized during allocation and probing.

## Control flow

Host scanning begins in `scsi_scan_host()`. Unless `scan=none` or `scan=manual`, it obtains a host runtime-PM reference, prepares an asynchronous scan when allowed, and either schedules `do_scan_async()` or runs `do_scsi_scan_host()` synchronously. The default scanner calls `scsi_scan_host_selected()` with wildcards; host templates can override this with `scan_start()`/`scan_finished()` polling.

`scsi_scan_host_selected()` validates channel/id/lun bounds, serializes through `scan_mutex`, waits for earlier async scans when needed, obtains host runtime PM, and scans channels/targets. `__scsi_scan_target()` skips the host adapter id, allocates or finds a target, probes LUN 0, and then chooses REPORT LUNS or sequential scanning. REPORT LUNS uses a temporary LUN-0 device if necessary, resizes the response buffer if the target reports more LUN data than initially allocated, and probes each returned LUN. Sequential scanning walks LUNs with quirk-controlled limits until the first missing non-sparse LUN.

Each LUN probe allocates a `scsi_device` if no existing visible device matches. `scsi_probe_lun()` issues INQUIRY in up to three passes, tolerating unit attention and some timeouts, sanitizes vendor/model/rev strings, derives device flags, records SCSI level, and decides whether LUN bits belong in CDB[1]. `scsi_add_lun()` copies inquiry data, sets device type/removability/queueing/quirk fields, transitions the device to running or blocked, configures transport and queue limits, calls low-level `sdev_configure()`, attaches VPD/CDL data, and either publishes immediately through `scsi_sysfs_add_sdev()` or defers publication during async scan. Async completion waits for previous async scans in list order, then publishes all deferred devices with `scsi_sysfs_add_devices()`.

## State and persistence behavior

Discovery persists as live `scsi_target` and `scsi_device` objects on host lists, with sysfs visibility added later by `scsi_sysfs.c`. Target lifetime is controlled by both device references and `reap_ref`; targets allocated during scans are destroyed if no child device becomes visible. Per-device persistent state includes INQUIRY copies, vendor/model/rev pointers, quirk flags, queue depth, budget map, runtime PM state, VPD pages, CDL support, and transport configuration. Module parameters influence all later scans until changed. Async scan ordering persists through `scanning_hosts` completions so devices discovered by earlier scans are announced first.

## Dependencies and integration points

The file depends on block-mq queues and queue limits, SCSI command execution, device-info quirks, transport templates, device handlers, VPD/CDL helpers, PM helpers from `scsi_pm.c`, sysfs add/remove functions from `scsi_sysfs.c`, and logging macros from `scsi_logging.h`. It is called by host registration, procfs/sysfs manual scan paths, transport code such as SAS, and exported `scsi_add_device()` consumers. It calls low-level driver hooks including `target_alloc`, `target_destroy`, `sdev_init`, `sdev_configure`, `change_queue_depth`, and host-template scan callbacks.

## Risks and edge cases

Scan code is race-sensitive. It must avoid duplicate targets while allowing a dying target to finish teardown, balance target reap references, and not publish devices out of async order. INQUIRY handling deliberately works around broken devices; changes can regress legacy USB, RBC/MMC, sparse LUN, floptical, and SCSI-2 behavior. REPORT LUNS fallback decisions depend on SCSI level, host `max_lun`, and blacklist flags; incorrect fallback can miss devices or hang on broken targets. Queue budget map reallocation freezes queues when resizing and must preserve the old map on failure. Manual and automatic scans must respect `scan=none`, `scan=manual`, host state, and runtime PM.

## Test signals

High-value tests include host scans with sync and async modes, `scan=manual`/`none`, manual sysfs/proc scans, LUN 0 absent/present combinations, REPORT LUNS success/failure/fallback, sparse LUN quirks, SCSI-2 LUN-in-CDB behavior, BLIST flags such as `NOREPORTLUN`, `FORCELUN`, `MAX5LUN`, `INQUIRY_36`, and `KEY`, and removal while scanning. KUnit or fault-injection tests should cover allocation failures, queue budget map resize failures, INQUIRY retries, malformed short inquiry data, and async scan completion ordering. Runtime validation should confirm sysfs devices appear only after successful `scsi_sysfs_add_sdev()` and that teardown through `scsi_forget_host()` removes pseudo devices last.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_sysctl.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_sysctl.c

## Purpose

`scsi_sysctl.c` registers the SCSI sysctl table under `dev/scsi`. Its only current knob is `logging_level`, which exposes the shared `scsi_logging_level` bitmask used by `scsi_logging.h`.

## Important APIs, types, and functions

`scsi_table[]` is a `struct ctl_table` array containing the `logging_level` entry. The entry points `scsi_init_sysctl()` and `scsi_exit_sysctl()` register and unregister the table. `scsi_table_header` stores the registration handle returned by `register_sysctl()`.

## Control flow

During SCSI subsystem initialization, `scsi_init_sysctl()` calls `register_sysctl("dev/scsi", scsi_table)` and returns `-ENOMEM` if registration fails. During teardown, `scsi_exit_sysctl()` unregisters the saved header. Reads and writes are handled by `proc_dointvec_minmax`, with lower bound `SYSCTL_ZERO` and upper bound `SYSCTL_INT_MAX`.

## State and persistence behavior

The file persists only the sysctl registration header. The exposed value is `scsi_logging_level`, owned by `scsi.c`. Writes through sysctl immediately affect future logging macro decisions and persist until changed or until the module/kernel state is torn down.

## Dependencies and integration points

It depends on Linux sysctl infrastructure, `scsi_logging.h`, and `scsi_priv.h`. It integrates with the logging macros and the same global logging word exposed as a module parameter.

## Risks and edge cases

The upper bound is `INT_MAX`, while the logging word is unsigned and defines bitfields up to bit 29. This is enough for the defined categories but would need review if categories expanded into the sign bit. Teardown assumes `scsi_table_header` was initialized only after successful registration. Disabled `CONFIG_SYSCTL` builds use stubs from `scsi_priv.h`.

## Test signals

Build with `CONFIG_SYSCTL` enabled and disabled. Runtime tests should read and write `/proc/sys/dev/scsi/logging_level`, verify negative values are rejected, and confirm changed bits affect category logging. Init failure injection around `register_sysctl()` should return `-ENOMEM` cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_sysfs.c

## Purpose

`scsi_sysfs.c` implements the SCSI bus, SCSI device class, host/device sysfs attributes, SCSI driver registration, device publication, and removal paths. It is the main bridge between discovered `scsi_device`/`scsi_target` objects and the Linux driver model.

## Important APIs, types, and functions

Exported or cross-file APIs include `scsi_device_state_name()`, `scsi_host_state_name()`, `scsi_bus_type`, `scsi_sysfs_register()`, `scsi_sysfs_unregister()`, `scsi_sysfs_add_sdev()`, `__scsi_remove_device()`, `scsi_remove_device()`, `scsi_remove_target()`, `__scsi_register_driver()`, `scsi_register_interface()`, `scsi_sysfs_add_host()`, `scsi_sysfs_device_initialize()`, `scsi_is_sdev_device()`, `scsi_shost_groups`, and `blank_transport_template`.

Host attributes include scan, host state, supported/active mode, reset, EH deadline, queue/SG/protection limits, busy count, proc name, blk-mq state, and hardware queue count. Device attributes include type, SCSI level, vendor/model/rev, busy/blocked counts, timeouts, rescan/delete/state, queue depth/type/ramp-up, VPD and inquiry binary data, I/O counters, modalias, events, WWID, serial, blacklist flags, device-handler state, access state, preferred path, and CDL support/enablement.

## Control flow

`scsi_sysfs_register()` registers the `scsi` bus and the `scsi_device` class; unregister reverses that order. The bus match function only binds true SCSI device objects, rejects `no_uld_attach`, and requires connected peripheral qualifier. Bus probe/remove/shutdown delegate to `struct scsi_driver` callbacks. `__scsi_register_driver()` fills in legacy wrapper callbacks when a driver supplied generic driver callbacks instead of SCSI-specific ones, then registers the driver on `scsi_bus_type`.

Host sysfs `scan` parses `channel id lun` strings and calls the transport `user_scan()` hook or `scsi_scan_host_selected(..., SCSI_SCAN_MANUAL)`. Host reset and EH deadline attributes call low-level template hooks or update host fields under `host_lock`.

`scsi_sysfs_device_initialize()` initializes the generic SCSI device and class device, names both with `host:channel:id:lun`, attaches default groups, configures initial LUN-in-CDB behavior, sets up transport state, links the device into host and target lists, and increments the target reap reference. `scsi_sysfs_add_sdev()` ensures the target is visible, enables PM, attaches device handlers, adds the generic device and class device, adds transport state, marks the device visible, and optionally registers a BSG queue.

Removal begins with `scsi_remove_device()` taking `scan_mutex` and calling `__scsi_remove_device()`. The internal remover makes visible devices cancel/deleted, unregisters BSG, unregisters the class device, removes transport/sysfs visibility, destroys the request queue, releases tag-set references, cancels requeue work, invokes low-level `sdev_destroy()`, destroys transport state, reaps the target, and puts the final device reference. Target removal walks host devices matching the target and removes each before reaping target visibility.

## State and persistence behavior

This file persists driver-model state: registered bus/class, sysfs attribute groups, generic devices, class devices, target visibility, runtime PM enablement, BSG queues, transport devices, and list membership. Device release frees request queues, budget maps, inquiry data, events, and VPD pages using RCU replacement/freeing. Sysfs stores mutate live SCSI state such as device state, queue timeouts, queue depth, event support bits, EH deadlines, runtime scan results, device-handler state, and CDL enablement.

## Dependencies and integration points

The file depends on the Linux device model, class/bus APIs, block queues, PM runtime, BSG, SCSI hosts/devices/drivers/device handlers/transports/devinfo, and `scsi_priv.h`. It is tightly coupled with `scsi_scan.c` for device initialization/publication/removal, `scsi_pm.c` for `scsi_bus_pm_ops`, low-level driver templates for host/device callbacks, upper-level SCSI drivers for bus binding, and transport classes for transport setup/add/remove/configure/destroy.

## Risks and edge cases

Sysfs store paths are user-facing mutation points and need strict parsing and state checks. Delete uses `sysfs_break_active_protection()` to safely remove the active attribute while handling concurrent writes; changing that path risks deadlocks or duplicate removal. Removal is not reentrant beyond the explicit `SDEV_DEL` guard and depends on state transitions to stop new I/O before queue teardown. VPD pages are RCU-protected and must be replaced under `inquiry_mutex` before delayed free. Attribute visibility depends on feature availability and populated VPD pointers. Host and device state name helpers return `NULL` for unknown states, so callers must handle invalid states.

## Test signals

Tests should cover bus/class registration, SCSI driver binding and legacy callback wrapping, host sysfs scans/resets/deadline updates, device state transitions, timeout and queue-depth stores, VPD/inquiry binary reads, event toggles, blacklist rendering, device handler attributes, CDL enablement, BSG registration failures, and repeated add/remove cycles. Concurrency tests should write `delete` multiple times, remove targets while scanning, read VPD while pages are freed, and exercise removal with pending queue/requeue work. Build tests should cover `CONFIG_PM`, `CONFIG_SCSI_DH`, and `CONFIG_BLK_DEV_BSG` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_trace.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_trace.c

## Purpose

`scsi_trace.c` formats SCSI command descriptor blocks for tracepoints. It turns common CDB opcodes into compact human-readable strings containing LBA, transfer length, protection, allocation length, zone, service action, and related command fields.

## Important APIs, types, and functions

The exported parser is `scsi_trace_parse_cdb(struct trace_seq *p, unsigned char *cdb, int len)`. It dispatches to helpers for READ/WRITE 6, 10, 12, 16, and 32 byte commands; UNMAP; SERVICE ACTION IN(16); MAINTENANCE IN/OUT; ZBC IN/OUT; WRITE ATOMIC(16); variable-length commands; and a miscellaneous fallback. `SERVICE_ACTION16()` and `SERVICE_ACTION32()` decode service-action fields. Helpers use `trace_seq_buffer_ptr()`, `trace_seq_printf()`, `trace_seq_puts()`, `trace_seq_putc()`, and unaligned big-endian accessors.

## Control flow

Tracepoint code calls `scsi_trace_parse_cdb()` with a CDB. The top-level switch uses `cdb[0]` to pick a formatter. READ/WRITE helpers decode command-specific LBA and transfer length widths. Variable-length commands dispatch by 32-byte service action. Service-action and maintenance helpers map known service actions to command names and print `UNKNOWN` for unsupported actions. All helpers terminate the trace string with a NUL in the trace sequence; unsupported opcodes print `-`.

## State and persistence behavior

The file owns no persistent state. It only appends transient formatted text to the supplied `trace_seq`. It does not issue commands, mutate devices, or store decoded data.

## Dependencies and integration points

It depends on kernel trace sequence APIs, unaligned big-endian helpers, SCSI opcode definitions, and `trace/events/scsi.h`. It integrates with SCSI trace events that need CDB decoding for diagnostics and performance analysis.

## Risks and edge cases

The helpers assume the passed CDB has enough bytes for the opcode-specific fields; the `len` parameter is accepted but not used for bounds checks. Callers must therefore provide valid CDB storage. UNMAP computes `(regions - 8) / 16` on an unsigned value, so malformed region lengths below eight can produce a large decoded count. Opcode/service-action coverage is partial, so many valid SCSI commands intentionally fall back to `-` or `UNKNOWN`. Formatters must stay synchronized with SCSI opcode constants and command layouts.

## Test signals

Trace tests should feed representative CDBs for all handled opcodes and assert formatted strings, including WRITE SAME unmap bits, protection fields, 32-byte service actions, maintenance service actions, ZBC options, and WRITE ATOMIC boundary size. Negative tests should cover unknown opcodes and unknown service actions. Fuzz or KUnit tests with short CDB buffers would highlight the current lack of `len` validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_api.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_api.h

## Purpose

`scsi_transport_api.h` is a tiny internal transport-facing declaration header. It exposes `scsi_schedule_eh()` to transport code without including a broader private SCSI core header.

## Important APIs, types, and functions

The sole declaration is `void scsi_schedule_eh(struct Scsi_Host *shost);`, which schedules SCSI error handling for a host. The header relies on `struct Scsi_Host` being declared before use or by the including context.

## Control flow

The header has no runtime flow. Transport implementations include it and call `scsi_schedule_eh()` when a transport-level condition requires host error handling.

## State and persistence behavior

No state is owned here. Calls to the declared function affect host error-handler scheduling state in the SCSI core implementation.

## Dependencies and integration points

It integrates with transport code such as libsas, where `sas_scsi_host.c` calls `scsi_schedule_eh(ha->shost)`. It avoids exposing all of `scsi_priv.h` to transport users that only need this one hook.

## Risks and edge cases

Because the header does not include the definition or forward declaration of `struct Scsi_Host`, include ordering matters unless callers already have the type from SCSI host headers. Any signature change must be coordinated with the implementation and all transport callers.

## Test signals

Compile transport users that include this header, especially SAS/libsas. Runtime tests should induce transport errors that call `scsi_schedule_eh()` and confirm the host error handler runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_transport_api.h -->
