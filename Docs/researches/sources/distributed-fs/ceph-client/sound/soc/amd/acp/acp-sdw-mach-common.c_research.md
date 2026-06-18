# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-sdw-mach-common.c

## Purpose
`acp-sdw-mach-common.c` maps SoundWire backend DAI IDs and SoundWire link IDs to AMD ACP CPU pin IDs for both legacy and SOF SoundWire machine drivers.

## Important APIs, Types, and Functions
The exported helpers are `get_acp63_cpu_pin_id()` and `get_acp70_cpu_pin_id()`. They consume SoundWire utility backend IDs such as `SOC_SDW_JACK_OUT_DAI_ID`, `SOC_SDW_AMP_OUT_DAI_ID`, and `SOC_SDW_DMIC_DAI_ID`, plus ACP pin constants from `soc_amd_sdw_common.h`.

## Control Flow
For ACP63, link 0 has separate TX/RX pins for audio0, audio1, and audio2, while link 1 maps jack/amp output to `ACP63_SW1_AUDIO0_TX` and capture/DMIC to `ACP63_SW1_AUDIO0_RX`. For ACP70/71/72, both supported links use the same audio0/audio1/audio2 TX/RX pin numbering. Invalid link or backend IDs log errors and return `-EINVAL`.

## State and Persistence
The file has no mutable state. It is pure mapping logic with debug/error logging.

## Dependencies and Integration Points
Both `acp-sdw-legacy-mach.c` and `acp-sdw-sof-mach.c` call these helpers while creating SoundWire DAI links. The constants must match CPU DAI names exposed by the AMD SoundWire DMA controller.

## Risks
Incorrect mappings break stream routing without necessarily failing card registration. ACP63 link 1 has fewer pins than link 0, so adding endpoints without updating the mapping can fail or collapse streams onto the wrong pin.

## Test Signals
Exercise all jack, amp, and DMIC playback/capture DAI IDs on ACP63 and ACP70-class systems, including invalid ACPI table cases that should return `-EINVAL` with clear logs.
