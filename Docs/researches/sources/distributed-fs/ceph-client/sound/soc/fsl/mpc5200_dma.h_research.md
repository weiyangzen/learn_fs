# sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_dma.h

## Purpose
Shared data structures and public functions for MPC5200 PSC audio DMA support.

## APIs, Types, and Functions
Defines `PSC_STREAM_NAME_LEN`, `struct psc_dma_stream`, `struct psc_dma`, helper `to_psc_dma_stream()`, and prototypes for `mpc5200_audio_dma_create()` and `mpc5200_audio_dma_destroy()`. Stream state includes runtime, active flag, BestComm task, IRQ, period indexes/counts/bytes, substream pointer, and AC97 slot bits. Device state includes PSC/FIFO register pointers, locks, SICR/sysclk/IMR/id/slots, playback/capture streams, and error counters.

## Control Flow, State, and Persistence
No executable logic beyond `to_psc_dma_stream()`. The structs define persistent PSC DMA state shared by the DMA backend and PSC protocol drivers.

## Dependencies and Integration
Depends on ALSA PCM, platform device, BestComm task, and MPC52xx PSC types through including contexts. Included by AC97, I2S, and DMA implementation files.

## Risks and Test Signals
Risks include shared mutable fields such as `slots` and `sicr` being manipulated by protocol drivers and DMA callbacks, and assumptions that substream stream IDs map directly to playback/capture members. Test signals are compile coverage across all MPC5200 PSC drivers and correct per-stream state updates during simultaneous playback/capture.
