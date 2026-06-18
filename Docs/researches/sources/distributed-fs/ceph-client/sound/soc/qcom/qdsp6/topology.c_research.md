# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/topology.c

Purpose: loads and interprets Qualcomm AudioReach ASoC topology firmware, building graph/subgraph/container/module objects that Q6APM later uses to configure DSP audio graphs.

Important functions: allocation helpers maintain IDRs for graph info, subgraphs, containers, and modules. Token parsers (`audioreach_parse_sg_tokens()`, `audioreach_parse_cont_tokens()`, `audioreach_parse_common_tokens()`) decode vendor tokens from topology private data. Widget loaders specialize module setup for encoders/decoders/converters, DMA/I2S/DisplayPort buffers, log modules, mixers, and PGA gain controls. Route/control loaders bind virtual mixers to module instance IDs. `audioreach_tplg_init()` requests `qcom/<driver>/<card>-tplg.bin` and invokes `snd_soc_tplg_component_load()`.

Control flow: topology load creates module hierarchy during widget callbacks, records route-derived module links, and exposes mixer/gain kcontrols through topology ops. Mixer put/get manipulates graph connection fields and DAPM power. Widget unload reverses IDR/list allocations, cascading module removal up through empty containers, subgraphs, and graph info.

State and persistence: persistent runtime state lives in the parent `q6apm` object: IDRs, graph lists, widget list, and per-module private data. Firmware topology files are external persisted inputs; parsed state is in-memory.

Dependencies and integration: depends on ASoC topology, firmware loader, AudioReach token UAPI, `q6apm`, and `audioreach` module structures and gain functions.

Risks: token parsing assumes required arrays are present and ordered well enough; missing arrays can lead to null dereferences. Dynamic module IDs depend on IDR allocation. Route names must exactly match widget names. Unload assumes non-mixer widgets have module private data.

Test signals: firmware request path succeeds, topology component load creates expected widgets/routes, duplicate module IDs fail cleanly, mixer controls update graph connections, PGA events send gain after power-up, and module unload frees IDRs without leaks.
