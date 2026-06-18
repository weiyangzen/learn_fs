# sources/distributed-fs/ceph-client/include/dt-bindings/sound/madera.h

Source read summary: 26 lines, 638 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/madera.h` declares ASoC device-tree constants for the audio codec binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 10 visible constants or packing macros; representative names are `MADERA_INMODE_DIFF`, `MADERA_INMODE_SE`, `MADERA_INMODE_DMIC`, `MADERA_DMIC_REF_MICVDD`, `MADERA_DMIC_REF_MICBIAS1`, `MADERA_DMIC_REF_MICBIAS2`, `MADERA_DMIC_REF_MICBIAS3`, `CS47L35_DMIC_REF_MICBIAS1B`, `CS47L35_DMIC_REF_MICBIAS2A`, `CS47L35_DMIC_REF_MICBIAS2B`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
