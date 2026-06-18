# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_maudio.c

Purpose: implements M-Audio BeBoB firmware cueing, metering specs, and special firmware support for FireWire 1814/ProjectMix-style devices with nonstandard clock/control behavior.

Important APIs/functions: `snd_bebob_maudio_load_firmware`, `snd_bebob_maudio_special_discover`, `special_get_rate`, `special_set_rate`, `avc_maudio_set_special_clk`, `special_stream_formation_set`, mixer control callbacks for clock/source/digital interfaces/sync status, `special_meter_get`, and `normal_meter_get`. It exports several `maudio_*_spec` structures.

Control flow and state: bootloader devices are sent three little-endian cues after checking firmware date. Special devices allocate `special_params`, initialize clock settings through a vendor-dependent AV/C command, add ALSA controls, synthesize stream formations from digital format and model, and set MIDI port counts. Control callbacks reject changes while streams run, update cached parameters, notify sync control, and refresh formations.

Dependencies/integration: depends on AV/C selector helpers, FCP transactions, direct FireWire transactions, ALSA controls, proc metering, and BeBoB stream startup special cases. Risks include firmware date comparison, hard-coded meter sizes/offsets, cached special params diverging from hardware, rate-setting sleeps, and controls changing channel counts while clients have constraints open. Test signals are firmware boot bus reset, correct ALSA controls, metering reads, and stream formation changes when ADAT/SPDIF modes change.
