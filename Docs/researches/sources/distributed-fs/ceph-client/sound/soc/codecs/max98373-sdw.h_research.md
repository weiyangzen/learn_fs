<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.h

## Purpose

This header defines the MAX98373 SoundWire control-port and data-port register addresses used only by the SoundWire transport driver.

## Important APIs, types, and functions

There are no functions or types. It includes `max98373.h` and provides constants for SoundWire SCP registers `0x0040` through `0x0070`, data port 1 registers and banked channel/sample/offset controls, and data port 3 registers and banked controls.

## Control flow

The header has no runtime control flow. `max98373-sdw.c` consumes these macros in its reg_defaults table, readable/volatile register filters, and SoundWire initialization logic.

## State and persistence behavior

No state is stored in the header. The constants define which transport registers may be cached, read, or treated volatile by the SoundWire regmap.

## Dependencies and integration points

The file is coupled to the Linux SoundWire register model and to `max98373-sdw.c`. DP1 is used as the sink/playback port and DP3 as the source/capture port in the bus properties.

## Risks and test signals

Risks are register-address drift against the datasheet or SoundWire core expectations, especially because the readable and volatile ranges rely on contiguous macro ranges. Test by reading regmap debugfs access permissions, checking SoundWire port enable sequences during playback/capture, and ensuring SCP/DP accesses do not fail as non-readable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/max98373-sdw.h -->
