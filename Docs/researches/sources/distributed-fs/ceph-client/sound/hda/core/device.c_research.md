# sources/distributed-fs/ceph-client/sound/hda/core/device.c

## Purpose
`device.c` implements the HD-audio codec core device model, including device initialization/registration, codec identity discovery, widget range/sysfs refresh, verb helpers, runtime PM wrappers, vendor naming, stream-format conversion, supported PCM querying, and power-state synchronization.

## Important APIs, Types, and Functions
Exports include `snd_hdac_device_init/exit/register/unregister()`, `snd_hdac_device_set_chip_name()`, `snd_hdac_codec_modalias()`, `snd_hdac_exec_verb()`, `snd_hdac_read()`, `_snd_hdac_read_parm()`, `snd_hdac_read_parm_uncached()`, `snd_hdac_override_parm()`, `snd_hdac_get_sub_nodes()`, `snd_hdac_refresh_widgets()`, `snd_hdac_get_connections()`, PM helpers, `snd_hdac_stream_format_bits()`, `snd_hdac_stream_format()`, `snd_hdac_spdif_stream_format()`, `snd_hdac_query_supported_pcm()`, `snd_hdac_is_supported_format()`, codec read/write wrappers, and power-state checks.

## Control Flow
Device init initializes the Linux device, links it to `snd_hda_bus_type`, adds it to the bus, reads vendor/subsystem/revision IDs, discovers AFG/MFG nodes, refreshes widgets, reads power caps and subsystem ID fallback, derives vendor/chip names, and leaves runtime PM active with a held reference. Registration adds the device and initializes widget sysfs under `widget_lock`.

## State and Persistence Behavior
State includes codec identity fields, AFG/MFG IDs, node ranges, widget sysfs state, vendor/chip strings, power caps, runtime PM counters, `in_pm`, and bus membership. Exit balances runtime PM, marks suspended, removes from bus, and frees names. Regmap may cache parameter and verb state.

## Dependencies and Integration Points
It depends on Linux device core, runtime PM, HDA regmap, widget sysfs, PCM params, and the HDA bus type. Codec drivers build on these helpers for probing, module aliases, verbs, format checks, and PM.

## Risks
Initialization performs hardware reads before full driver binding; failures must drop the device reference correctly. Connection-list parsing handles malformed codec data but can return zero on repeated nulls. PCM query code must match HDA format bits to ALSA formats and subformats correctly. PM helper misuse can deadlock recursive PM paths.

## Test Signals
Test codec registration/unregistration, modalias generation, widget sysfs refresh, vendor-name fallback, verb encoding bounds checks, connection-list short/long/range parsing, supported PCM/rate/format queries, PM reference balance, and power-state wait behavior on codecs that report errors.
