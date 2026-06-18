# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes-ipc4.c

Purpose: Implements IPC4-specific probe module control operations for the SOF probes client.

Important APIs/state: Defines IPC4 DMA/node types, runtime param IDs, probe gateway config, probe point encoding helpers, and IPC4 probe info structs. `sof_ipc4_probe_get_module_info()` locates and caches the probe module manifest entry by hard-coded UUID in `sof_probes_priv->ipc_priv`. `ipc4_probe_ops` exposes init/deinit/info/print/add/remove.

Control flow: Init builds `MOD_INIT_INSTANCE` for the probe module, with host-input DMA node derived from `stream_tag - 1`, buffer size, invalid pipeline ID, core 0, and config size. Deinit sends `MOD_DELETE_INSTANCE`. Points info sends large-config GET for active or available points, allocates max payload, converts returned IPC4 points to generic descriptors, and frees the IPC buffer. Point print resolves the module/instance to a widget and formats type/index/connection text. Add converts generic descriptors to IPC4 points and sends large-config SET for `SOF_IPC4_PROBE_POINTS`; remove sends large-config SET for disconnect IDs.

Dependencies and integration: Depends on IPC4 manifest/module lookup helpers, SOF client large config `set_get_data`, IPC4 header macros, topology widget lookup by module ID/instance, and generic probes client descriptors.

Risks: Probe module UUID is hard-coded; firmware manifest changes break probing. `stream_tag - 1` assumes valid nonzero stream tags. Info trusts returned `num_elems` to size allocation from the max payload buffer. Point printing can continue with unknown widget but logs an error. Init uses invalid pipeline ID and core 0, so multi-core/pipeline probe support would need changes.

Test signals: Probe module found/missing, init/deinit, active and available point info, malformed num_elems, add/remove multiple probe points, point print for known/unknown widgets, stream tag boundary, and IPC4 large-config failures.
