# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm-lpass-dais.c

Purpose: `q6apm-lpass-dais.c` registers AudioReach backend LPASS DAIs. It binds the common LPASS port table to APM graph operations and supplies DAI ops for DMA, I2S, and HDMI/DisplayPort backends.

Important APIs and types: `struct q6apm_lpass_dai_data` keeps one graph pointer, started flag, and `audioreach_module_config` per `APM_PORT_MAX` port. DAI ops are `q6dma_ops`, `q6i2s_ops`, and `q6hdmi_ops`, all sharing startup/prepare/shutdown/trigger behavior with format-specific `hw_params`, channel-map, or set-fmt callbacks.

Control flow: probe allocates the state object, fills `q6dsp_audio_port_dai_driver_config` with APM-specific ops, asks `q6dsp_audio_ports_set_config` for the full DAI table, then registers the component with `.of_xlate_dai_name`. Capture graphs are opened in `startup`; playback graphs are opened in `prepare` to satisfy the source-before-sink graph sequencing comment. `prepare` stops any already-started graph, sets module direction, applies PCM media format to graph modules, and sends graph prepare. `trigger` starts the graph on START/RESUME/PAUSE_RELEASE if not already started. `shutdown` stops and closes the graph.

State and persistence: graph pointers and module configs are runtime component state indexed by DAI ID. `is_port_started` prevents duplicate graph starts. Channel maps and display-port indexes persist between hw_params/set_channel_map and prepare.

Dependencies and integration points: this layer depends on the common LPASS port table in `q6dsp-lpass-ports.c`, AudioReach graph APIs from `q6apm.c`, and `q6dsp-common` channel allocation. It is selected by the `qcom,q6apm-lpass-dais` compatible.

Risks: arrays are indexed directly by `dai->id`, so DT/table IDs must be less than `APM_PORT_MAX`. HDMI `hw_params` uses the maximum channel interval rather than the exact selected channel count. Several operations assume `graph[dai->id]` is non-null; unusual trigger ordering can crash. Stop errors in prepare are not checked.

Test signals: validate all backend DAI IDs translate to names and ops, capture and playback graph open ordering, channel-map validation for DMA TX/RX sets, HDMI channel allocation, repeated prepare/start/stop/shutdown cycles, and invalid DAI ID rejection.
