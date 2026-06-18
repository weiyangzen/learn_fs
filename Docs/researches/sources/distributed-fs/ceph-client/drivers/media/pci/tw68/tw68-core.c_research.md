
# sources/distributed-fs/ceph-client/drivers/media/pci/tw68/tw68-core.c

## Purpose
This file is the PCI core for Techwell TW6800/TW6801/TW6804/TW6816-family capture devices. It registers the PCI driver, initializes hardware registers, maps MMIO, configures DMA/interrupt masks, registers the V4L2 device, and handles suspend/resume.

## Important APIs, Types, And Functions
Key functions are `tw68_initdev`, `tw68_finidev`, `tw68_hw_init1`, `tw68_irq`, `tw68_suspend`, and `tw68_resume`. Module parameters are `latency`, `video_nr`, and `card`. The PCI ID table matches several Techwell devices. It calls video-layer functions `tw68_video_init1`, `tw68_video_init2`, `tw68_irq_video_done`, `tw68_video_start_dma`, and `tw68_set_tvnorm_hw`.

## Control Flow
Probe allocates `struct tw68_dev`, assigns a V4L2 device instance name, registers it, enables PCI, optionally sets the latency timer, logs PCI info, sets bus mastering and 32-bit DMA, determines decoder type and interrupt mask from PCI ID, reserves and maps BAR0, runs `tw68_hw_init1`, requests a shared IRQ, initializes/registers the video device, and enables interrupts. IRQ handling reads `TW68_INTSTAT & pci_irqmask`, loops up to ten times dispatching video interrupt bits to `tw68_irq_video_done`, and disables the interrupt mask if status cannot be drained. Remove stops DMA/FIFO and interrupts, unregisters V4L2 controls/video device, unmaps MMIO, releases the region, and unregisters V4L2. Suspend stops DMA/IRQs and discards done buffers; resume reapplies TV norm and restarts DMA on the active buffer.

## State And Persistence
State is held in `struct tw68_dev`: V4L2 device, decoder type, video device, controls, PCI/MMIO resources, IRQ masks, capture format/size/field, active buffer list, and selected input. Hardware registers hold current decoder/DMA state but are reinitialized on probe.

## Dependencies And Integration Points
The file depends on Linux PCI, PM, DMA mask setup, V4L2 device registration, videobuf2 state through the video layer, and TW68 register macros. It is the lifecycle owner for the video layer.

## Risks
`tw68_resume` assumes `dev->active.next` is a valid buffer and can be unsafe if no buffers are active during resume. Interrupt storms disable the mask after ten loops, which protects the system but can leave capture stopped. Register initialization is manually coded from hardware defaults and comments, so board variants may need tuning. The `card` module parameter is declared but not used in this file.

## Test Signals
Probe logs should show device, revision, IRQ, latency, and registered video node. Streaming should survive interrupt load without "INTERRUPT NOT HANDLED" messages. PM tests should suspend/resume during active and idle capture. Remove/unload should leave no mapped region, IRQ, or V4L2 device leaks.
