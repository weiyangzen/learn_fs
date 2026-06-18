# sources/distributed-fs/ceph-client/drivers/media/pci/tw686x/tw686x-core.c

## Purpose
`tw686x-core.c` is the PCI driver core for Intersil/Techwell TW6864/TW6865/TW6868/TW6869 video frame grabber devices. It owns module parameters, PCI probe/remove, device lifetime, interrupt dispatch, and the shared DMA channel enable/reset path used by the video and audio subdrivers. The file is intentionally conservative around hardware access because the header comments document stress-test failures where DMA register programming while streaming could freeze the host or the PCIe link could disappear.

## Important APIs, Types, And Functions
The public functions exported to sibling source files are `tw686x_enable_channel()` and `tw686x_disable_channel()`, both operating on `struct tw686x_dev` and channel bit numbers. Module parameters are `dma_interval`, written to `DMA_TIMER_INTERVAL`, and `dma_mode`, parsed through `tw686x_dma_mode_set()` as `memcpy`, `contig`, or `sg`. `tw686x_irq()` is the central IRQ handler. `tw686x_probe()` allocates `struct tw686x_dev`, channel arrays, enables PCI/MMIO/DMA, resets hardware, initializes video and audio, requests the IRQ, and stores drvdata. `tw686x_remove()` tears down IRQ, media devices, timer, MMIO, PCI resources, and marks `dev->pci_dev = NULL` under `dev->lock` before dropping the final V4L2 reference.

## Control Flow
Probe starts with allocation and 32-bit DMA mask setup, maps BAR0, resets system and decoder blocks, disables DMA, configures FIFO/error handling and DMA timing, then calls `tw686x_video_init()` and `tw686x_audio_init()`. IRQ handling reads `INT_STATUS` and `VIDEO_FIFO_STATUS`, returns `IRQ_NONE` if neither standard interrupts nor FIFO errors are present, then coalesces video channel events, audio requests, and DMA timeout handling. Video requests go to `tw686x_video_irq()` with `pb_status` and FIFO state; audio requests go to `tw686x_audio_irq()`. Channels needing reset are disabled via `tw686x_reset_channels()` and re-enabled later by `tw686x_dma_delay()`.

## State And Persistence
Persistent runtime state is in `struct tw686x_dev`: PCI pointer, MMIO base, DMA mode ops selected by video init, per-channel arrays, audio settings, a shared spinlock, `dma_delay_timer`, and pending DMA enable/command register images. No disk state exists. The delayed DMA state is volatile but critical: `pending_dma_en` and `pending_dma_cmd` coalesce channel changes to avoid programming DMA too rapidly.

## Dependencies And Integration Points
The file integrates with Linux PCI, DMA mapping, IRQ, timer, V4L2 device lifetime, and the sibling TW686x video/audio layers. It depends on register offsets and bit definitions from `tw686x-regs.h` and structures/prototypes from `tw686x.h`. The PCI ID table encodes channel count and second-generation SG table behavior through `driver_data`.

## Risks
The core risk is hardware instability from register writes during streaming; the timer-based delayed enable and reset throttling are explicit mitigations. Hot-unplug is handled by setting `pci_dev` to NULL after resources are unavailable, so userspace file handles must honor that state in vb2 paths. IRQ reset uses `reset_ch = ~0` on DMA timeout; callers rely on channel masks being bounded later. Audio init failure is only a warning, so video-only operation is possible but audio regressions could be missed.

## Test Signals
Useful signals are successful module load/probe, one video node per channel, working capture in all three `dma_mode` values, no host lockups under repeated stream on/off, DMA timeout recovery logs, FIFO-error recovery logs, and clean hot-unplug/removal while file handles remain open. Interrupt behavior can be observed through frame delivery continuity and absence of stale DMA channels after stream stop.
