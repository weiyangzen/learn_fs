# sources/distributed-fs/ceph-client/include/media/tveeprom.h

## Purpose
Defines structures and helpers for reading and parsing Hauppauge analog TV EEPROMs.

## Important APIs, Types, and Functions
`enum tveeprom_audio_processor` identifies audio processor class. `struct tveeprom` stores parsed radio/IR/MAC presence, primary/secondary tuner type/formats/model, audio/decoder processor, model, revision, serial, revision string, and MAC address. APIs are `tveeprom_hauppauge_analog()` and `tveeprom_read()`.

## Control Flow
Bridge drivers read EEPROM bytes over I2C using `tveeprom_read()`, then parse 256-byte Hauppauge data with `tveeprom_hauppauge_analog()` to fill board configuration fields.

## State and Persistence Behavior
Parsed data is stored in caller-owned `struct tveeprom`; EEPROM contents are persistent device manufacturing data.

## Dependencies and Integration Points
Depends on I2C client and Ethernet address sizing. Integrates Hauppauge card autodetection with tuner type IDs, analog standards, IR support, and optional MAC address setup.

## Risks
Short reads or malformed EEPROM data can misconfigure tuners, standards, IR, or network MAC. `len` should be at least 256 for Hauppauge parsing.

## Test Signals
EEPROM read success/failure, known EEPROM image parsing, tuner and format mapping, MAC extraction, IR capability bits, and handling truncated data.
