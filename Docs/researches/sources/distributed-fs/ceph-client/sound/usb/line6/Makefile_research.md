# sources/distributed-fs/ceph-client/sound/usb/line6/Makefile

## Purpose
Builds the shared Line 6 USB module and the device-specific companion modules.

## Build Integration
`snd-usb-line6-y` combines capture, driver, MIDI, MIDI buffer, PCM, and playback objects. Device-specific objects build into `snd-usb-pod`, `snd-usb-podhd`, `snd-usb-toneport`, and `snd-usb-variax`. `obj-$(CONFIG_...)` lines connect objects to the Kconfig symbols.

## Dependencies and Risks
The shared object list must stay in sync with exported functions used by device modules. Playback is included even though not part of this work item, so capture/PCM references to playback helpers depend on that object. Build drift is the main risk.

## Test Signals
Kernel builds for each Line 6 configuration and module load tests catch missing object or symbol issues.
