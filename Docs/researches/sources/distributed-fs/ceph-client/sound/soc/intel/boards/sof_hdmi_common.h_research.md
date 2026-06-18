# sources/distributed-fs/ceph-client/sound/soc/intel/boards/sof_hdmi_common.h

Purpose: Minimal shared HDMI-private-data header for Intel SOF board drivers.

Important APIs, types, and functions: It defines `IDISP_CODEC_MASK` as `0x4`, used against ACPI machine `codec_mask` to identify iDisp HDMI codec presence. `struct sof_hdmi_private` stores the HDMI codec ASoC component pointer and an `idisp_codec` boolean.

Control flow and integration: `sof_board_helpers` and SoundWire helper code embed this struct in their private card contexts. HDMI init callbacks store the component, and late-probe callbacks use the boolean and component pointer to decide whether to invoke HDA HDMI control building.

State and persistence: The header defines in-memory fields only. There is no persistence or allocation behavior.

Dependencies: ASoC component definitions.

Risks: Multiple files define or use the same numeric iDisp mask; drift would break HDMI detection. Test signals include compile coverage and HDMI-present/absent card registration paths.
