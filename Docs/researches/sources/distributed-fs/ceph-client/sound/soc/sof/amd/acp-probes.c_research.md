# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-probes.c

Purpose: SOF debug probe host callbacks for AMD ACP using compressed capture streams.

Important APIs/types/functions: `acp_probes_compr_startup()` allocates an ACP stream for probe capture and returns its stream tag. `acp_probes_compr_set_params()` maps the compressed runtime DMA buffer into ACP PTEs and writes buffer size to scratch. `acp_probes_compr_pointer()` reports cumulative captured bytes and sampling rate. `acp_probes_register()`/`acp_probes_unregister()` register the `acp-probes` SOF client.

Control flow: startup stores the compressed stream in the ACP stream and in runtime private data, and records `adata->probe_stream` for IRQ position updates. set_params configures stream pages similarly to PCM. IRQ handling in `acp-ipc.c` updates `cstream_posn` and calls `snd_compr_fragment_elapsed()`. shutdown releases the stream and clears references.

State and persistence: `adata->probe_stream` is a single active probe stream pointer. `stream->cstream`, runtime private data, and `cstream_posn` carry compressed capture state.

Dependencies and integration points: SOF client probes framework, ALSA compressed ops, ACP stream config, and probe position register described by chip descriptors.

Risks: only one probe stream is tracked globally. set_params releases the stream on config failure but startup state must remain consistent. Sampling rate is inferred from DAI capture rate bits and may be ambiguous if multiple rates are set.

Test signals: probe client registration, compressed probe startup/set_params/shutdown, position interrupts, and trace/probe stream resource contention.
