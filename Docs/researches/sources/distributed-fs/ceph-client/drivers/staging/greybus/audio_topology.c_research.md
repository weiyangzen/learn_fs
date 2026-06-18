# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_topology.c

## Purpose

`audio_topology.c` converts Greybus-provided audio topology blobs into dynamic ASoC controls, DAPM widgets, routes, jack capabilities, and lookup tables used by the codec and module drivers.

## Important APIs, Types, and Functions

Exported functions are `gbaudio_tplg_parse_data()` and `gbaudio_tplg_release()`. Internal groups include module/control/widget name mapping, enum-string generation, ALSA mixer get/put/info callbacks, DAPM mixer/mux callbacks, widget event handling, topology object constructors, and processors for controls, widgets, routes, and headers.

## Control Flow

Parsing starts by reading counts and block sizes from `struct gb_audio_topology`, computing offsets for DAI, controls, widgets, and routes. It processes controls into `snd_kcontrol_new` entries and `gbaudio_control` lookup records, processes widgets into `snd_soc_dapm_widget` entries and widget-control records, rewrites names with `GB <dev_id>` prefixes, maps routes from numeric IDs to names/control text, and records jack/button masks. Runtime ALSA get/put callbacks locate the owning module from the prefixed control/widget name, perform Greybus control operations under runtime PM, and update DAPM power for mixer/mux changes. Widget events enable/disable remote widgets and call `gbaudio_module_update()` for AIF stream transitions.

## State and Persistence Behavior

The parser fills `struct gbaudio_module_info` arrays and lists for controls, widget controls, widgets, routes, device masks, and jack masks. Many names and control metadata point into the topology buffer; release removes lists and devm allocations, while the topology buffer is freed by the module driver.

## Dependencies and Integration Points

It depends on Greybus audio topology structs, ASoC kcontrol/DAPM APIs, runtime PM, codec state, module state, and protocol helpers for remote control/widget operations.

## Risks and Edge Cases

The parser trusts topology header sizes and counts when computing offsets into a variable-length blob; there is no strong whole-buffer bounds validation in this file. Name rewriting mutates topology memory in place and assumes names fit `NAME_SIZE`. `find_gb_module()` parses names with `sscanf("%s %d")`, so naming convention changes break routing. DAPM enum put drops the runtime PM reference after get, then reacquires for set, leaving a race window. Widget-control error cleanup clears the whole module widget-control list, which can remove earlier successfully parsed controls. The DAI block size is accounted for but DAI parsing is not implemented.

## Test Signals

Fuzz topology blobs for inconsistent counts/sizes, invalid widget/control/route IDs, long names, enum string lengths, stereo controls, unsupported iface/type, and malformed route controls. Runtime tests should exercise ALSA mixer get/put, DAPM mux/mixer changes, widget PRE_PMU/POST_PMD, module unplug during control access, and repeated parse/release cycles.
