# sources/distributed-fs/ceph-client/sound/soc/sdw_utils/soc_sdw_utils.c

Purpose: central SoundWire ASoC helper library. It defines the codec capability registry, generic widgets/controls, codec lookup helpers, runtime initialization, SoundWire stream operation wrappers, DAI-link construction helpers, endpoint counting/parsing, and card cleanup/late-probe hooks.

Important APIs and data: `codec_info_list[]` maps SoundWire vendor/part/version IDs and ACPI IDs to `asoc_sdw_codec_info` entries, DAI descriptors, widgets, controls, init/exit/rtd callbacks, quirks, auxiliary components, and optional card late probes. Lookup exports include `asoc_sdw_find_codec_info_part()`, `_acpi()`, and `_dai()`. `asoc_sdw_rtd_init()` installs controls/widgets once per runtime, calls codec-specific `rtd_init`, constructs speaker component metadata, and marks DAI init complete. Stream exports `asoc_sdw_startup()`, `prepare()`, `trigger()`, `hw_params()`, `hw_free()`, and `shutdown()` wrap SoundWire stream APIs and channel-map setup. Link helpers create `snd_soc_dai_link` objects. Endpoint helpers count and parse ACPI SoundWire endpoint descriptions into internal endpoint/dailink structures.

Control flow and state: machine creation first counts endpoints, parses links, builds DAI links, then runtime init executes per codec DAI. Static `codec_info_list` contains mutable fields such as `amp_num`, `rtd_init_done`, and late-probe callbacks; `asoc_sdw_mc_dailink_exit_loop()` resets `rtd_init_done` and calls registered exits. Endpoint parsing handles aux components, sidecar amps, quirks, SDCA function presence, aggregation groups, and per-stream link masks.

Dependencies and integration: depends on Linux SoundWire bus/slave APIs, ACPI SoundWire descriptors, SDCA function metadata, and many codec-specific helper files exported under `SND_SOC_SDW_UTILS`. Generic machine drivers use this as their discovery and setup layer.

Risks: mutable global codec registry state must be reset on card teardown and may be sensitive to multiple cards. Endpoint filtering mixes quirks and BIOS SDCA data; wrong quirk polarity can drop endpoints. `asoc_sdw_get_codec_name()` depends on exact generated SoundWire device names and unique-ID rules. Channel-map logic requires capture channels divisible by codec count.

Test signals: mockup entries exercise parsing; real boards should validate endpoint counts, aggregated DAI grouping, card component strings, DAPM controls/widgets, SDCA endpoint filtering, SoundWire prepare/trigger/deprepare sequences, and teardown cleanup of software nodes.
