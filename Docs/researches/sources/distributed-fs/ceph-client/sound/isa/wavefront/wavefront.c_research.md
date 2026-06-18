# sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront.c

## Purpose
This is the card-level driver for Turtle Beach WaveFront family cards, including Maui, Tropez, and Tropez+. It combines CS4232/WSS PCM, OPL3, optional CS4232 MPU-401, ICS2115 wavetable synth hwdep, WaveFront internal/external MIDI, and optional YSS225 FX processor support.

## Important APIs, Types, and Functions
Module parameters configure CS4232 PCM port/IRQ/DMA, CS4232 MPU port/IRQ, ICS2115 port/IRQ, FM port, PnP enablement, and whether to use the hidden CS4232 MIDI interface. PnP resource import is in `snd_wavefront_pnp()`. ICS2115 IRQ dispatch is `snd_wavefront_ics2115_interrupt()`. Constructors include `snd_wavefront_new_synth()`, `snd_wavefront_new_fx()`, `snd_wavefront_new_midi()`, `snd_wavefront_card_new()`, and common `snd_wavefront_probe()`.

## Control Flow
PnP detection activates the CS4232 WSS logical device, optional CS4232 MPU logical device, and ICS2115 synth logical device, then copies resources into module arrays. Common probe creates WSS PCM and timer, optional OPL3 hwdep, reserves the ICS2115 IO window, requests the ICS2115 IRQ, initializes wavefront interrupt and MIDI locks/waitqueue, detects and starts the WaveFront synth, creates the synth hwdep, creates WSS mixer, optionally creates CS4232 MPU, creates internal and external ICS2115 rawmidi devices, creates the FX hwdep if the synth detection reported FX support, fills card strings, and registers the card.

The shared ICS2115 interrupt handler routes interrupts to MIDI or internal synth logic based on `acard->wavefront.interrupts_are_midi`. The first WaveFront MIDI device initialization sets the MIDI base and starts the ICS2115 UART/virtual MIDI mode; subsequent internal/external rawmidi devices share that initialized interface.

## State and Persistence
State is stored in `snd_wavefront_card_t` and nested `snd_wavefront_t`: IRQ, base ports, resources, interrupt mode, waitqueue, MIDI locks/state, and FX initialized flag. Module parameter arrays hold configured or PnP-discovered resources. There is no suspend/resume implementation in this file, and no persistent storage.

## Dependencies and Integration Points
This file depends on Linux ISA, PnP, IRQ, ALSA core, WSS, OPL3, MPU-401, and WaveFront synth/FX/MIDI APIs declared in `sound/snd_wavefront.h` and implemented by sibling object files.

## Risks and Edge Cases
The ISA path requires explicit CS4232 and ICS2115 ports. PnP device comments indicate some logical devices are ignored. The `snd_wavefront_new_midi()` helper uses a static `first` flag, which can be problematic for multiple cards because it is module-global rather than per-card. Suspend/resume is marked FIXME, so state and firmware may not survive power transitions.

## Test Signals
Successful probe should show WSS PCM/timer/mixer, optional OPL3, synth hwdep with ICS2115 interface, two WaveFront MIDI rawmidi devices, optional CS4232 MPU, and optional YSS225 FX hwdep on Tropez+. Verify ICS2115 IRQs switch to MIDI after MIDI start and that internal/external rawmidi devices both transmit.
