<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-dapm.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-dapm.h

## Purpose
`soc-dapm.h` defines ASoC Dynamic Audio Power Management. It provides widget/control/route macros, power event flags, bias levels, widget/path structures, DAPM context APIs, pin controls, stream events, and graph-walking helpers.

## Important APIs, types, and functions
Macros create DAPM widgets for VMID, signal generators, inputs/outputs, mics, headphones, speakers, lines, PGAs, mixers, muxes, demuxes, supplies, regulators, pinctrl, AIFs, DACs, ADCs, clocks, and event variants. Control macros bind DAPM volume, enum, autodisable, TLV, and pin-switch handlers. Enums define stream events, power events, bias levels, widget types, and path directions. Core types are `snd_soc_dapm_route`, `snd_soc_dapm_path`, `snd_soc_dapm_widget`, `snd_soc_dapm_update`, `snd_soc_dapm_widget_list`, `snd_soc_dapm_stats`, and `snd_soc_dapm_pinctrl_priv`. APIs allocate/init/free contexts, add/delete routes, create widgets, link DAI widgets, stream events, mixer/mux power updates, pin enable/disable/force/ignore-suspend, sync, bias operations, connected-widget queries, and debugfs/sysfs support.

## Control flow
Drivers declare widgets and routes. During card/component setup, the core instantiates widgets, creates paths, links DAI endpoints, and marks dirty graph nodes. User mixer changes, pin changes, and stream events update path connectivity and trigger DAPM sync, which walks the graph, computes power states, writes register bits, and invokes pre/post event callbacks in ordered subsequences.

## State and persistence behavior
DAPM state is runtime graph state: widgets, paths, dirty/work/power lists, endpoint counts, power bits, active stream flags, connected/forced/ignore-suspend flags, kcontrol associations, bias level, stats, regulators, clocks, and pinctrl state. It is rebuilt on card registration and removed at teardown.

## Dependencies and integration points
It depends on ALSA controls, topology dynamic objects, clocks, regulators, pinctrl, DAI/runtime/card/component structures, debugfs, sysfs attributes, and ASoC mutex helpers from `soc.h`.

## Risks and test signals
Risks include inverted register values, event-order regressions, graph cycles or stale `walking` flags, missing dirty marking, route name mismatches, supply path semantics, suspend pin handling, and kcontrol/widget lifetime issues. Test signals include route add/delete, pin switches, mixer/mux updates, regulator/clock/pinctrl widgets, stream start/stop/suspend/resume, forced pins, bias transitions, connected-widget queries, topology-created widgets, and debugfs graph inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-dapm.h -->
