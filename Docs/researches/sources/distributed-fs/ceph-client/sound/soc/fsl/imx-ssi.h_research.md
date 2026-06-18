# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-ssi.h

## Purpose
Private SSI header for i.MX sound drivers. It defines SSI register offsets/bitfields, buffer sizing, driver names, and external FIQ symbols used by the legacy FIQ PCM path.

## APIs, Types, and Functions
Defines `DRV_NAME`, SSI register offsets such as STX/RX, SCR, SIER, STCCR/SRCCR, SFCSR, SOR, bit masks for enable, interrupt, FIFO, clock, network and AC97 behavior, and extern symbols for FIQ handler boundaries and FIQ buffer/base variables.

## Control Flow, State, and Persistence
No executable logic is in the header. The register constants drive CPU DAI setup and FIQ assembly behavior; extern globals persist the DMA buffer addresses and SSI base used by the installed FIQ handler.

## Dependencies and Integration
Included by `imx-pcm-fiq.c` and SSI CPU DAI implementations. It is tied to ARM FIQ support, i.MX SSI hardware, and ALSA PCM buffer configuration.

## Risks and Test Signals
Risks include register definition drift across SSI variants, global FIQ symbol coupling, and bitfield misuse in callers. Test signals are build coverage with SSI and FIQ enabled, correct register programming under playback/capture, and FIQ pointer updates using the exported symbols.
