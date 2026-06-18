# sources/distributed-fs/ceph-client/sound/pci/echoaudio/mona.c

## Purpose

`mona.c` is the wrapper for Echo Mona cards. It selects Echo24/GML behavior with PCI and external ASICs, monitor controls, super-interleave, digital mode switching, external clocks, and ADAT.

## Important APIs, Types, and Functions

The topology exposes 6 analog outputs, 8 digital outputs, 4 analog inputs, and 8 digital inputs. Firmware entries include loader, 56301 and 56361 DSP images, 48/96 kHz PCI-card ASIC images for each DSP family, and an external ASIC. PCI IDs cover 56301 and 56361 revisions `0070` to `0072`. PCM caps support 8 to 96 kHz and up to 8 channels.

## Control Flow

The module includes `mona_dsp.c`, shared DSP, GML helpers, and common Echoaudio code. Card-specific DSP code chooses 56301/56361 firmware and swaps PCI-card ASICs according to rate and external clock speed.

## State and Persistence Behavior

Runtime state includes ASIC code, digital mode, auto-mute, professional S/PDIF, clock source, monitor matrix, and line levels. Static module state is firmware, PCI IDs, topology, and PCM caps.

## Dependencies and Integration Points

It integrates with GML control-register helpers, multiple Mona firmware files, ALSA PCM and controls, and common Echoaudio transport.

## Risks and Test Signals

Risks are wrong ASIC selection for 48 versus 96 kHz, external-box ASIC load failure, and invalid ADAT/double-speed combinations. Test signals include probe across supported IDs, S/PDIF/word/ADAT clock detection, sample-rate changes across 48/96 boundary, and mode switching without losing monitor state.
