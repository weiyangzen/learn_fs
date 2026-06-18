# sources/distributed-fs/ceph-client/sound/pci/ymfpci/ymfpci.h

Purpose: Defines the Yamaha DS-XG/YMFPCI hardware register map, PCI legacy configuration bits, DMA bank structures, voice/PCM/chip state, PM save lists, and cross-file function prototypes.

Important APIs/types/functions: `YMFREG()` maps register names to MMIO offsets. `YDSXGR_*` constants cover interrupt flags, global/mode/control registers, AC97 command/status, mixer volumes, capture formats/slots, playback/capture/effect/work base registers, and DSP/controller instruction RAM. `PCIR_DSXG_*` constants define PCI config legacy/FM/MPU/joy bases. Bank structs (`snd_ymfpci_playback_bank`, `capture_bank`, `effect_bank`) mirror hardware DMA/control memory layouts. `struct snd_ymfpci_voice` tracks one playback voice and its interrupt callback. `struct snd_ymfpci_pcm` tracks ALSA runtime state for playback/capture routing. `struct snd_ymfpci` is the primary persistent chip object.

Control flow: No executable flow, but the header defines the state machines used by `ymfpci_main.c`: voices are allocated from 64 playback slots, playback/capture/effect banks are double-buffered, `active_bank` selects the current hardware bank, `start_count` gates DSP engine start/stop, and saved register arrays define suspend/resume restore order.

State and persistence: `struct snd_ymfpci` stores MMIO mapping, old legacy PCI state, DMA work allocation, bank base addresses, voice pool, AC97 bus/codec, rawmidi/timer/PCM devices, capture/effect substream pointers, SPDIF bits, per-PCM mixer controls, locks/waitqueue, firmware pointers, and saved registers. This is the cross-module persistence contract for the entire driver.

Dependencies/integration: Includes ALSA PCM/rawmidi/ac97/timer, Linux gameport, and is shared by `ymfpci.c` and `ymfpci_main.c`. It exposes creation functions for PCM, mixer, timer, and PM ops used by the PCI wrapper.

Risks: Hardware structure packing and endianness are critical because these structs are written into DMA memory consumed by the DSP. Register constants and saved register lists must match chip revisions. The voice pool and `src441_used` special slot are shared mutable state protected by locks; new code must honor those locks. Firmware size constants must match requested blobs.

Test signals: Compile both YMFPCI objects, verify firmware download writes instruction RAM, run playback/capture/SPDIF/4ch paths, suspend/resume restore saved registers, and use lockdep or stress playback to catch voice/bank state races.
