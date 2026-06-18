# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes.h

Purpose: defines the shared contract between the generic SOF probes auxiliary client, platform host drivers, and IPC-specific probe implementations. It is intentionally small and contains no inline logic.

Important APIs/types: `struct sof_probes_host_ops` describes host-side compressed-stream setup callbacks: startup, shutdown, set_params, trigger, and pointer. `struct sof_probe_point_desc` is the packed userspace/IPC description with `buffer_id`, `purpose`, and `stream_tag`. `enum sof_probe_info_type` selects active or available probes. `struct sof_probes_ipc_ops` abstracts firmware IPC operations for init, deinit, point discovery, printable formatting, add, and remove. `struct sof_probes_priv` stores debugfs dentries, extractor stream tag, the temporary ASoC card, IPC-private state, and selected host/IPC operation tables.

Control flow/state: the header models state owned by `sof-client-probes.c`; the only persistent fields are the active stream tag, the embedded card object, and callback pointers. `ipc_priv` is reserved for IPC3/IPC4 implementation-private state.

Dependencies/integration: forward declares ALSA compressed and ASoC DAI types and exposes `ipc3_probe_ops`/`ipc4_probe_ops` to the generic client. Consumers must include this header when registering platform-dependent probe clients from SOF platform code.

Risks/test signals: `PROBES_INFO_AVAILABE_PROBES` is misspelled but used as an ABI-like internal enum, so renaming would require coordinated changes. The packed descriptor is parsed from debugfs integer arrays, so size/alignment assumptions should be tested on 32-bit and 64-bit builds. Build tests should cover both IPC3-only, IPC4-only, and combined configurations.
