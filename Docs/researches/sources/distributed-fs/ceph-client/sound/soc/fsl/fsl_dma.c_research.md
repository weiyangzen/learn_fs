# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_dma.c

## Purpose
`fsl_dma.c` is the legacy Freescale Elo DMA ASoC PCM component for MPC/Freescale SSI audio. It implements fixed-buffer PCM DMA using the platform's CCSR DMA channel registers, two reusable link descriptors in chaining mode, SSI FIFO-aware bandwidth programming, interrupt-driven period completion, and DT discovery from SSI nodes that reference DMA channel nodes.

## Important APIs, Types, and Functions
- `struct dma_object` is per-platform-channel state containing the component driver, SSI STX/SRX physical addresses, SSI FIFO depth, mapped DMA channel registers, IRQ, and assignment flag.
- `struct fsl_dma_private` is per-open-substream state with two link descriptors, channel registers, IRQ, substream, SSI data register address, link-descriptor buffer physical address, current link index, DMA buffer addresses, period size, and period count.
- `fsl_dma_hardware` describes PCM capabilities, broad format support, mmap/interleaved/joint-duplex/pause flags, period limits, and 128 KiB fixed buffer.
- `fsl_dma_isr()` handles DMA status bits, stops on transmit/programming errors, reports period elapsed on end-of-segment, updates link descriptors, and clears handled bits.
- `fsl_dma_update_pointers()` rotates one of the two link descriptors to the next period when the number of ALSA periods exceeds the descriptor count.
- `fsl_dma_new()` sets a 36-bit coherent DMA mask and allocates fixed PCM buffers.
- `fsl_dma_open()` allocates coherent private/link memory, requests IRQ, initializes ringed link descriptor `next` pointers, sets mode register for external master start/pause, interrupts, and source/destination hold.
- `fsl_dma_hw_params()` programs sample-size-dependent SSI register offsets, transfer size, bandwidth count, period descriptors, and snoop attributes.
- `fsl_dma_pointer()` reads SAR/DAR to compute the ALSA hardware pointer and detects out-of-range positions.
- `find_ssi_node()` scans compatible SSI nodes to find one whose playback/capture DMA phandle points at this DMA node.
- `fsl_soc_dma_probe()` builds and registers the component driver for compatible `fsl,ssi-dma-channel`.

## Control Flow
Probe finds the SSI node that references the DMA channel, reads SSI MMIO resource and FIFO depth, allocates `dma_object`, fills component callbacks, computes SSI STX0/SRX0 physical addresses, registers the component, maps DMA channel registers, parses IRQ, and stores drvdata.

PCM new coerces the card DMA mask to 36 bits and allocates the fixed DMA buffer. PCM open rejects non-integer periods, enforces one stream per DMA channel with `assigned`, allocates coherent `fsl_dma_private` and descriptors, requests IRQ, links the two descriptors in a ring, writes current link descriptor address registers, clears BCR, and programs DMA mode for external SSI master control plus interrupts. Playback holds destination address; capture holds source address.

`hw_params` computes sample width and period layout, adjusts SSI register address for big-endian sub-word writes, rejects unsupported packed widths, sets DMA transfer sizes, computes bandwidth count from FIFO depth and sample bytes, and initializes each descriptor for either memory-to-SSI playback or SSI-to-memory capture with appropriate snoop attributes. ISR period completions call ALSA and rotate descriptors for buffers with more periods than links. `hw_free` aborts/reset registers; close frees IRQ and coherent private memory.

## State and Persistence
Per-device state persists in `dma_object` while the platform device is bound. Per-stream state is coherent DMA memory so the hardware can read link descriptors. Hardware register state is explicitly programmed/reset on open/hw_params/hw_free. No regmap or runtime PM is used, and no disk persistence exists.

## Dependencies and Integration Points
The driver integrates with ALSA SoC component PCM callbacks, Freescale SSI register offsets from `fsl_ssi.h`, CCSR DMA register definitions from `fsl_dma.h`, OF address/IRQ/phandle helpers, big-endian MMIO accessors, DMA coherent allocation, and SSI DT properties `fsl,playback-dma`, `fsl,capture-dma`, and `fsl,fifo-depth`.

## Risks and Edge Cases
- The driver scans all `fsl,mpc8610-ssi` nodes because DT lacks a reverse DMA-to-SSI link; this is fragile for unusual DT topologies.
- `assigned` is not protected by a lock; concurrent opens on the same channel depend on higher-level serialization.
- Packed 24-bit formats are advertised in `FSLDMA_PCM_FORMATS`, but `hw_params` only accepts 8/16/32 physical widths; packed 24-bit support can fail at runtime.
- Big-endian SSI register offset logic is hardware-specific and easy to break when changing formats.
- `CCSR_DMA_MR_BWC()` uses `ilog2(x)`; invalid or zero FIFO-derived values would be problematic.
- Probe maps registers and IRQ after component registration; failures after registration are not explicitly handled.

## Test Signals
- Playback/capture on MPC SSI should produce regular EOS interrupts and period elapsed callbacks.
- Runtime `hw_params` for 8/16/32-bit samples validates SSI register offset and transfer-size programming; packed 24-bit should be checked for expected rejection.
- Error injection for DMA transmit/programming errors should stop the stream with XRUN.
- Pointer readings must stay within the fixed buffer and wrap at buffer end.
