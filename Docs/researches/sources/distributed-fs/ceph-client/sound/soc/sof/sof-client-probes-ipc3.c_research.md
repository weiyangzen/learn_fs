# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes-ipc3.c

Purpose: Implements IPC3-specific probe control operations for the SOF probes client.

Important APIs/types: Defines packed IPC3 probe DMA, info, add, and remove payload structs. `ipc3_probe_ops` exposes `.init`, `.deinit`, `.points_info`, `.points_add`, and `.points_remove`. Init sends one extractor DMA descriptor; deinit sends `SOF_IPC_PROBE_DEINIT`. Info supports active probe info only. Add/remove send flexible arrays of `sof_probe_point_desc` or buffer IDs.

Control flow: Each operation allocates the exact variable-size message with `struct_size()`, fills SOF IPC global probe command headers, sends via SOF client IPC, and frees temporary memory. Info allocates a max-size reply buffer, requests DMA or point info, validates reply/error, duplicates returned entries, and returns element count.

Dependencies and integration: Consumed by generic `sof-client-probes` code when the client IPC type is IPC3. Uses SOF IPC3 command IDs, SOF client max payload size, and generic probe point descriptors.

Risks: Info only supports `PROBES_INFO_ACTIVE_PROBES`; available probes returns `-EOPNOTSUPP`. Flexible-array copy sizes must match message struct layout. Reply `rhdr.error` is checked but not converted separately if `ret` is already negative. Init/deinit lifetime must be matched by higher-level client.

Test signals: Init/deinit pairing, active DMA/point info, no elements, reply error, allocation failures, add/remove multiple points, and unsupported available-probe query.
