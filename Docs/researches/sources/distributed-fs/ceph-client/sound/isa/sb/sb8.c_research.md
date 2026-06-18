# sources/distributed-fs/ceph-client/sound/isa/sb/sb8.c

## Purpose
This is the card-level ISA driver for Sound Blaster 1.0, 2.0, and Pro class cards and compatible devices. It resolves legacy resources, creates the low-level SB DSP object, adds PCM, mixer, OPL3, and MIDI devices, and registers the ALSA card.

## Important APIs, Types, and Functions
Module parameters are `index`, `id`, `enable`, `port`, `irq`, and `dma8`. `struct snd_sb8` stores the FM reservation and `struct snd_sb *chip`. `snd_sb8_interrupt()` routes the single ISA interrupt to either PCM or MIDI handling depending on `chip->open & SB_OPEN_PCM`. `snd_sb8_match()` validates enabled slots and requires explicit IRQ and DMA. `snd_sb8_probe()` constructs the card. Optional PM callbacks save and restore mixer state.

## Control Flow
Probe creates a devm ALSA card, reserves 0x388 for FM conflict avoidance, and either probes the requested DSP base or auto-probes 0x220, 0x240, and 0x260. It rejects SB16-class detections and suggests the SB16 or ALS100 driver. It then creates SB8 PCM, mixer controls, OPL3 hwdep at either base+8 for SB1/SB2 or base/base+2 for Pro, creates SB8 MIDI rawmidi, fills card strings, registers the card, and stores driver data.

## State and Persistence
State is limited to module parameter arrays, the ALSA card private area, the shared `struct snd_sb`, and mixer hardware registers. Suspend marks the card D3hot and saves mixer registers; resume resets the DSP, restores mixer registers, and marks D0. No disk persistence exists.

## Dependencies and Integration Points
The file uses the Linux ISA driver framework, devm resource management, ALSA core, SB common DSP creation, SB8 PCM, SB mixer, SB8 MIDI, and OPL3 hwdep.

## Risks and Edge Cases
Auto-probing legacy IO ports can collide with unrelated ISA devices on real hardware. IRQ and DMA are mandatory because there is no reliable autodetection here. Interrupt routing depends on `chip->open`, so incorrect open state can send MIDI interrupts to PCM or vice versa. SB Pro stereo and older DSP behavior are handled in `sb8_main.c`, not here.

## Test Signals
Module load should create one card per enabled slot with expected `SB8` or `SB Pro` names. Playback/capture devices should be half-duplex. Mixer controls should match the detected hardware generation. MIDI rawmidi should work when PCM is not open. Suspend/resume should preserve mixer values.
