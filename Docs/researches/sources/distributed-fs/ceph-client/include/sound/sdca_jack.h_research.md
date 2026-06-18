<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_jack.h -->
# sources/distributed-fs/ceph-client/include/sound/sdca_jack.h

## Purpose
`sdca_jack.h` declares SDCA jack-detection helpers for mapping SDCA group/entity interrupt changes into ALSA/ASoC jack state and optional mixer controls.

## Important APIs, types, and functions
`struct jack_state` stores the ALSA kcontrol and `snd_soc_jack` associated with one SDCA jack interrupt. Public functions are `sdca_jack_alloc_state()`, `sdca_jack_process()`, `sdca_jack_set_jack()`, and `sdca_jack_report()`.

## Control flow
An interrupt is provisioned with `sdca_jack_alloc_state()`, the machine driver associates an ASoC jack via `sdca_jack_set_jack()`, an SDCA interrupt calls `sdca_jack_process()`, and reporting is performed through `sdca_jack_report()` using the interrupt's entity/control context.

## State and persistence behavior
State lives in the interrupt private data as `jack_state`. It remembers the target kcontrol and jack object between interrupts but does not persist across device removal.

## Dependencies and integration points
The header integrates `sdca_interrupt_info`/`sdca_interrupt` with ALSA controls and `struct snd_soc_jack`. It depends on SDCA interrupt population finding the jack-related controls.

## Risks and test signals
Risks include null jack association, stale kcontrol pointers, incorrect mapping from SDCA detected/selected mode to ASoC jack masks, and interrupt delivery before state allocation. Test signals include plug/unplug/type changes, jack setup after interrupt allocation, cleanup while interrupts are disabled, and mixer-control notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_jack.h -->
