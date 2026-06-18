# sources/distributed-fs/ceph-client/sound/soc/codecs/rt711-sdca-sdw.h

## Purpose
`rt711-sdca-sdw.h` provides default register tables for the RT711 SDCA SoundWire wrapper. It seeds the normal SDCA regmap and the MBQ regmap used by `rt711-sdca-sdw.c`, covering SDCA control defaults, HID/jack codec state, function-unit mute/volume defaults, private/vendor indexes, and calibration-related addresses.

## Important APIs, Types, And Definitions
The header defines two static default arrays: `rt711_sdca_reg_defaults[]` for 8-bit SDCA/SoundWire registers and `rt711_sdca_mbq_defaults[]` for 16-bit MBQ registers. Entries include direct SoundWire/SDCA registers such as `0x201a`, `0x2025`, `0x2230..0x2239`, and `0x2f*`, plus SDCA control addresses generated with `SDW_SDCA_CTL()` for jack codec, HID, and mic-array entities. Defaults set several user function-unit mutes to muted, sample frequency index to `0x09`, requested power state to D3, and volume/gain defaults to zero.

## Control Flow Role
This header has no executable functions. Probe in `rt711-sdca-sdw.c` passes the arrays into two `regmap_config` objects. The regmap cache uses them before hardware attach and while recovering from cache-only suspend. Shared codec logic in `rt711-sdca.c` relies on these defaults when programming SDCA controls and when regcache sync restores state after SoundWire detach/reattach.

## State And Persistence Behavior
The defaults define the software baseline for two separate persistent register domains: normal SDCA 8-bit controls and MBQ 16-bit controls. Because both regmaps use Maple cache, these tables influence which values are considered default, dirty, or sync-worthy. MBQ defaults include private vendor register windows and volume/gain controls that are likely visible to ALSA mixers in the shared component implementation.

## Dependencies And Integration Points
The header includes regmap and SoundWire SDCA register definitions and depends on RT711 SDCA entity/control constants from `rt711-sdca.h`, included before it by the C file. It is private to the SoundWire wrapper and coupled to `rt711_sdca_readable_register()`, `rt711_sdca_mbq_readable_register()`, and the shared component's control layout.

## Risks
Incorrect defaults can cause muted/unmuted state, sample-rate indexes, power state, or volume values to restore incorrectly after PM transitions. Adding controls in shared RT711 SDCA code without matching readable/default coverage can create regcache holes. Because `SDW_SDCA_CTL()` encodes function/entity/control/channel fields, wrong entity constants affect the wrong SDCA control while still compiling.

## Test Signals
Build success validates constant availability. Runtime signals include stable mute/volume defaults on first probe, correct state restoration after suspend/resume, jack/HID controls remaining readable and volatile where expected, no regcache sync errors for MBQ addresses, and expected codec power state after initialization.
