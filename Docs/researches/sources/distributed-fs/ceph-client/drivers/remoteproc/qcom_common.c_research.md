# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_common.c

## Purpose

`qcom_common.c` implements shared Qualcomm remoteproc helpers used by multiple Qualcomm peripheral loader drivers. It provides minidump coredump segment collection, GLINK and SMD rpmsg subdevice lifecycle glue, ELF dump-segment registration, subsystem restart (SSR) notifier registration and remoteproc subdev notifications, and a Protection Domain Mapper auxiliary device subdev.

## Important APIs, types, and functions

- Minidump structures mirror Qualcomm SMEM table-of-contents layouts: `minidump_region`, `minidump_subsystem`, and `minidump_global_toc`.
- `qcom_minidump()` locates the global minidump ToC in SMEM item 602, validates subsystem state/encryption, replaces normal coredump segments with SMEM-provided regions, runs coredump by sections, and cleans up.
- `qcom_register_dump_segments()` adds coredump segments for ELF PT_LOAD entries while skipping Qualcomm MDT hash segments and zero-sized segments.
- `qcom_add_glink_subdev()` / `qcom_remove_glink_subdev()` manage `glink-edge` child nodes and GLINK SMEM registration.
- `qcom_add_smd_subdev()` / `qcom_remove_smd_subdev()` manage `smd-edge` child nodes and SMD edge registration.
- `qcom_register_ssr_notifier()` and `qcom_unregister_ssr_notifier()` manage SRCU notifier chains by subsystem name.
- `qcom_add_ssr_subdev()` wires remoteproc prepare/start/stop/unprepare to SSR before/after powerup and shutdown notifications.
- `qcom_add_pdm_subdev()` / `qcom_remove_pdm_subdev()` create and remove an auxiliary `pd-mapper` device during remoteproc prepare/unprepare.

## Control flow

For minidumps, a crashing driver calls `qcom_minidump()` with a minidump id and dump callback. The function fetches the SMEM global ToC, checks id bounds and subsystem validity, falls back to normal `rproc_coredump()` when the subsystem ToC is not ready/enabled, skips when encryption is not done, clears existing coredump segments, maps the region table, adds valid regions as custom segments, emits a section-based coredump, and then frees the temporary segment list.

GLINK and SMD helpers are called by concrete remoteproc drivers during probe. They look for child nodes under the parent DT node, configure `rproc_subdev` callbacks, and add subdevices. During remoteproc start/stop, those callbacks register or unregister GLINK/SMD transport edges.

SSR helpers maintain a global list of named subsystems protected by a mutex. Remoteproc subdev callbacks emit SRCU notifications at before powerup, after powerup, before shutdown, and after shutdown. PDM helpers create an auxiliary bus device named `pd-mapper` at prepare and remove it at unprepare.

## State and persistence behavior

Global SSR subsystem state persists in `qcom_ssr_subsystem_list` for the module lifetime; entries are not removed when remoteprocs unregister. Minidump state is transient, using SMEM as authoritative persistent storage and the rproc dump segment list as temporary state. GLINK/SMD edge pointers and PDM auxiliary device pointers live in per-remoteproc helper structs and are nulled during stop/unprepare. Device-tree node references are held until remove helpers run.

## Dependencies and integration points

The file depends on remoteproc internals, Qualcomm SMEM, MDT loader flags, GLINK SMEM, SMD, QMI SSR data types, auxiliary bus, notifier/SRCU, firmware ELF headers, and DT child nodes. It exports helper symbols for Qualcomm platform remoteproc drivers and also exports SSR notifier registration for other kernel clients.

## Risks and edge cases

- `qcom_add_minidump_segments()` can return early on `kstrndup()` allocation failure without unmapping the mapped region table in that branch.
- `qcom_ssr_get_subsys()` allocates global subsystem entries but does not free them later; acceptable for long-lived subsystem names, but not for dynamic unbounded names.
- Minidump cleanup replaces the remoteproc dump segment list temporarily; errors must always clean up to avoid dangling custom segment names.
- `qcom_add_glink_subdev()` returns if no `glink-edge` node, but if `kstrdup_const()` fails after `of_get_child_by_name()`, the node reference is not released in that path.
- PDM auxiliary device creation happens in prepare; failure there can abort remoteproc boot and must be tested with auxiliary bus errors.
- SSR notifications use SRCU chains, so callbacks may sleep but ordering and crash-state values must match clients' expectations.

## Test signals

Build Qualcomm remoteproc helpers with GLINK, SMD, SMEM, auxiliary bus, and optional sysmon users. Tests should cover minidump SMEM absent, invalid id, disabled subsystem fallback, encryption-not-ready skip, valid region custom dumps, ELF dump segment filtering, GLINK/SMD DT node absence and lifecycle, SSR notifier ordering and unregister, PDM auxiliary add/delete failures, and memory-leak checks on probe/remove error paths.
