# sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6dsp-lpass-ports.h

Source read summary: 248 lines, 7859 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/sound/qcom,q6dsp-lpass-ports.h` declares ASoC device-tree constants for the Qualcomm subsystem binding, such as codec electrical options, mux endpoint IDs, DAI/port indexes, clock selectors, jack-detect modes, or audio routing selectors.

Important APIs, types, and functions: The file exports 227 visible constants or packing macros; representative names are `HDMI_RX`, `SLIMBUS_0_RX`, `SLIMBUS_0_TX`, `SLIMBUS_1_RX`, `SLIMBUS_1_TX`, `SLIMBUS_2_RX`, `SLIMBUS_2_TX`, `SLIMBUS_3_RX`, `SLIMBUS_3_TX`, `SLIMBUS_4_RX`, `SLIMBUS_4_TX`, `SLIMBUS_5_RX`, `SLIMBUS_5_TX`, `SLIMBUS_6_RX`, `SLIMBUS_6_TX`, `PRIMARY_MI2S_RX` and 211 more. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: Audio machine descriptions include the header in DTS properties; codec, controller, or graph-card drivers parse the numeric values while constructing DAI links, clocks, widgets, and jack or microphone-bias configuration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Bad values can silently route audio to the wrong DAI, select an unsafe analog bias or over-current threshold, or misprogram a codec pin. Many options are valid only for one codec revision.

Test signals: Compile DTS users, run ASoC probe and route-graph validation, verify jack/mic-bias/clock behavior where applicable, and compare macro values with codec or controller datasheets.
