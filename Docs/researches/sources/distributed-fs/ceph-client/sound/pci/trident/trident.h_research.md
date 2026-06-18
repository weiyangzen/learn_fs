# sources/distributed-fs/ceph-client/sound/pci/trident/trident.h

## Purpose
This header defines the shared Trident/SiS7018 driver contract: device IDs, register offsets, bit definitions, private structures, voice and TLB memory models, exported helper prototypes, and PM ops used across `trident.c`, `trident_main.c`, and `trident_memory.c`.

## Important APIs, types, and definitions
Important constants include `TRIDENT_DEVICE_ID_DX`, `TRIDENT_DEVICE_ID_NX`, `TRIDENT_DEVICE_ID_SI7018`, voice type constants, `SNDRV_TRIDENT_PAGE_SIZE`, and `SNDRV_TRIDENT_MAX_PAGES`. Register definitions cover global control, miscellaneous interrupts, legacy DMA registers, voice start/stop/status banks, MPU-401, NX S/PDIF, joystick, NX TLB control, voice channel registers, DX/NX AC97 registers, and SI7018 AC97/serial/GPIO/S/PDIF registers.

Core structures are `struct snd_trident`, `struct snd_trident_voice`, `struct snd_trident_tlb`, `struct snd_4dwave`, `struct snd_trident_pcm_mixer`, and `struct snd_trident_port`. `struct snd_trident` is the device object containing PCI/card handles, ports, IRQ, S/PDIF state, AC97 handles, voice allocation maps, locks, TLB state, PCM devices, raw MIDI, and gameport. `struct snd_trident_voice` models each hardware channel and carries both register-programming fields and PCM/synth ownership metadata.

Public prototypes include device construction, PCM creation, gameport creation, voice allocation/free/start/stop/register write, TLB page allocation/free, and `snd_trident_pm`.

## Control flow
The header has no executable flow, but it defines the shared state transitions used by the implementation: wrapper probe calls `snd_trident_create()`, PCM open allocates `snd_trident_voice`, prepare fills voice register fields, trigger starts/stops voice banks, IRQ updates voice sync state, and close/free returns voice/TLB resources.

## State and persistence behavior
The header defines all persistent in-memory state for the module. Hardware-facing state is duplicated in cached fields such as `spdif_bits`, `spdif_ctrl`, `musicvol_wavevol`, `pcm_mixer[]`, `ChanMap[]`, `bDMAStart`, and per-voice register fields. TLB state includes both the DMA-visible table and the ALSA util memory header used to allocate virtual pages.

## Dependencies and integration points
The header depends on ALSA PCM, MPU-401, AC97, and util memory headers. It is the integration boundary among the three objects linked by the local Makefile and any related Trident synth code that uses the exported voice helpers.

## Risks and test signals
Risks include bitfield drift across DX/NX/SI7018 variants, different voice register layouts, 30-bit DMA/TLB assumptions, and structure fields that are manipulated under different locks. Test signals are compile coverage of all three objects, successful probe on all supported device IDs, TLB allocation only on NX, correct S/PDIF and rear-path controls on supported hardware, and no lockdep or race symptoms during concurrent PCM open/close/trigger.
