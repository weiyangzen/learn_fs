# sources/distributed-fs/ceph-client/sound/pci/intel8x0.c

## Purpose
`intel8x0.c` is the ALSA PCI driver for Intel ICH-family AC'97 audio controllers plus compatible SiS7012, NVIDIA nForce, AMD, and ALi M5455 variants. It handles PCI probe, controller reset, AC'97 codec discovery, PCM stream creation, busmaster descriptor-ring DMA, interrupt handling, mixer quirks, S/PDIF routing, AC97 clock measurement, proc diagnostics, and suspend/resume.

## Important APIs, Types, and Functions
- `struct ichdev` represents one busmaster stream: register offset, BDL address, PCM substream, buffer geometry, ring indices, interrupt bit, AC97 PCM mapping, and suspend/prepared flags.
- `struct intel8x0` is the card-private state: PCI/card pointers, MMIO regions, stream array, AC97 bus/codecs, capability flags, IRQ, descriptor pages, lock, and register masks.
- Codec access is implemented by `snd_intel8x0_codec_{semaphore,read,write}()` for ICH/SIS/NVIDIA and `snd_intel8x0_ali_codec_{read,write}` for ALi.
- DMA setup and IRQ progression are handled by `snd_intel8x0_setup_periods()`, `snd_intel8x0_update()`, and `snd_intel8x0_interrupt()`.
- PCM operations include `hw_params`, `hw_free`, `prepare`, `trigger`, `pointer`, and device-specific open/close functions.
- `snd_intel8x0_mixer()` creates the AC97 bus, discovers codecs, applies quirks, assigns AC97 PCM slots, and detects multichannel/DRA/20-bit/S/PDIF features.
- `snd_intel8x0_chip_init()` and helper reset functions bring hardware to a known state.
- `intel8x0_suspend()` and `intel8x0_resume()` handle PM reinitialization and IRQ reacquisition.
- `__snd_intel8x0_probe()` wires ALSA card creation, init, mixer, PCM, proc, optional clock measurement, and registration.

## Control Flow
PCI probe creates a managed ALSA card, chooses names and quirks, initializes PCI regions and descriptor rings, resets the controller, requests IRQ, initializes AC97 mixer/codecs, creates PCM devices, registers proc info, optionally measures/tunes the AC97 clock, then registers the card. PCM open selects an `ichdev`, applies constraints, and stores it as runtime private data. `hw_params` opens the corresponding AC97 PCM slots. `prepare` fills a 32-entry buffer descriptor list and programs channel mode registers. `trigger` starts/stops DMA. Interrupts read global status, call `snd_intel8x0_update()` for active streams, advance BDL/LVI/CIV state, and notify ALSA periods. PM suspend frees IRQ and suspends codecs; resume resets hardware, reacquires IRQ, restores SDM/SPDIF settings, resumes codecs, and restores suspended stream registers.

## State and Persistence
All state is runtime kernel state. `intel8x0` persists for card lifetime and owns descriptor pages, stream state, AC97 codec objects, and capability flags. `ichdev` tracks prepared/running stream positions and ring indices. AC97 codec state is delegated to ALSA AC97 core. Hardware registers are reinitialized on resume; there is no persistent storage beyond module parameters and userspace mixer restore.

## Dependencies and Integration Points
The driver integrates with the Linux PCI driver model, ALSA core, ALSA PCM layer, AC97 core, proc info, PM ops, DMA allocation, and IRQ handling. It depends on chipset-specific PCI IDs, AC97 quirk tables, and busmaster register layouts for Intel, SiS, NVIDIA, and ALi variants.

## Risks and Test Signals
Risks include chipset-specific register differences, busy-wait loops on DMA stop, semaphore/read-timeout behavior on broken codecs, global module parameters such as `spdif_aclink` mutating per probe, descriptor-ring position races, and VM-specific pointer handling. Test signals include successful probe across supported PCI IDs, AC97 codec detection including multi-codec ICH4 SDIN routing, playback/capture/MIC/SPDIF PCM operation, period interrupts under stress, suspend/resume with active streams, AC97 clock measurement logs, and clean proc output.
