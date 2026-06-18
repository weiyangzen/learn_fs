# sources/distributed-fs/ceph-client/include/media/tuner-types.h

## Purpose
Defines numeric `TUNER_*` model identifiers for analog TV/radio tuner devices.

## Important APIs, Types, and Functions
The file is a large list of tuner type constants used by tuner-core, board tables, EEPROM parsers, and bridge drivers to identify exact tuner models and families.

## Control Flow
No runtime flow. Probe/configuration code stores or compares these IDs to select tuner operations and frequency ranges.

## State and Persistence Behavior
No state. Numeric IDs are compile-time internal ABI and often appear in board/eeprom mappings.

## Dependencies and Integration Points
Used by `tuner.h`, tuner-simple, bridge card tables, and EEPROM parsing such as Hauppauge TV EEPROM support.

## Risks
Renumbering or reusing IDs breaks board mappings. Adding IDs must preserve existing values and keep driver support aligned.

## Test Signals
Build all tuner users, EEPROM-to-tuner mapping checks, board-table probe on legacy devices, and no renumbering in diffs.
