# sources/distributed-fs/ceph-client/sound/soc/sof/sof-audio.c

Purpose: Implements SOF topology runtime orchestration for widgets, routes, pipelines, D0i3 stream checks, and object lookup helpers.

Important APIs/state: Exports `sof_widget_setup()`, `sof_widget_free()`, `snd_sof_dsp_only_d0i3_compatible_stream_active()`, DAI parameter getters, and lookup helpers. Internal state includes widget `use_count`, `prepared`, `setup_mutex`, route `setup`, pipeline `complete`, core masks/refcounts, PCM stream pipeline lists, and DAPM widget lists.

Control flow: Widget setup increments use count, recursively sets up dynamic scheduler widgets, powers required DSP cores, calls IPC widget setup, sends DAI config, and restores kcontrols. Free decrements use count, resets/free routes, frees DAI config and widget, powers down scheduler cores, clears pipeline completion, and frees dynamic scheduler references. Widget-list prepare walks connected DAPM paths from AIF/DAI starts, skips virtual and aggregated DAI widgets, runs IPC prepare/unprepare, then setup creates widgets, routes, and completes pipelines. Route setup ignores virtual widgets and only binds routes whose endpoints are set up. Error paths free and unprepare already processed widgets.

Dependencies and integration: Used by PCM hw_params/prepare/hw_free and PM pipeline restore/tear-down. Depends on ASoC DAPM path walking, IPC topology ops, DSP core get/put wrappers, tracepoints, and topology-loaded lists on `sdev`.

Risks: Recursive DAPM walking must avoid cycles with `p->walking`. Use count and prepared flags must stay balanced across errors, aggregated DAI skips, and repeated hw_params. Dynamic pipeline widgets recursively reference scheduler widgets; missing `spipe` or `pipe_widget` is fatal. Direction-valid logic controls loopback/cross-direction routes and can skip required connections if topology is wrong.

Test signals: Dynamic/static pipelines, aggregated DAIs, virtual widgets, same-direction and cross-direction routes, setup failure unwind, DAI config hw_params/free, kcontrol restore, D0i3-compatible stream detection, lookup by name/component, and DAI MCLK/BCLK/TDM param retrieval.
