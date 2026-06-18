<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/ux500_dma.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/ux500_dma.c

## Purpose

`ux500_dma.c` implements a DMAEngine-backed MUSB DMA controller for Ux500 platforms. It preallocates fixed RX/TX DMA channels associated with MUSB endpoint pairs and exposes MUSB DMA callbacks for allocation, compatibility testing, programming, abort, create, and destroy.

## Important APIs, Types, and Functions

`struct ux500_dma_channel` wraps a MUSB `dma_channel`, DMAEngine channel, endpoint pointer, transfer length, cookie, logical channel number, direction, and allocation flag. `struct ux500_dma_controller` owns RX and TX channel arrays plus the MUSB private pointer and physical register base.

Key functions are `ux500_dma_controller_create()`, `ux500_dma_controller_destroy()`, `ux500_dma_controller_start()`, `ux500_dma_controller_stop()`, `ux500_dma_channel_allocate()`, `ux500_dma_channel_release()`, `ux500_dma_channel_program()`, `ux500_dma_channel_abort()`, `ux500_dma_is_compatible()`, `ux500_configure_channel()`, and `ux500_dma_callback()`.

## Control Flow

Creation allocates the controller, records the MUSB physical base resource, installs MUSB DMA callbacks, and requests DMAEngine channels. Requesting first tries named channels such as `iep_1_9` or `oep_1_9`, then falls back to board-data DMA filters and parameter arrays. Allocation maps endpoint number to one of eight RX or TX channels, enforcing one user per direction/channel. Programming marks the channel busy, builds a one-entry scatterlist from the DMA address, configures the DMA slave endpoint FIFO address, chooses 1-byte or 4-byte bus width by transfer alignment, prepares a slave SG descriptor with callback, submits, and issues pending.

Completion runs under `musb->lock`, records actual length, marks status free, and calls `musb_dma_completion()`. Abort clears MUSB TX/RX DMA CSR bits, terminates the DMAEngine channel, and marks the channel free. Destroy releases all DMAEngine channels and frees controller memory.

## State and Persistence Behavior

State is per-controller memory plus external DMAEngine channel state. `cur_len`, `cookie`, `status`, and `is_allocated` are active-transfer state. Hardware-visible state includes DMA controller descriptors and MUSB endpoint CSR DMA bits. No persistent storage exists.

## Dependencies and Integration Points

The file depends on DMAEngine slave APIs, MUSB DMA controller interfaces, Ux500 MUSB platform data, named DMA channels, endpoint FIFO offset callbacks, and Linux DMA mapping helpers. It is wired from `ux500_ops`.

## Risks and Test Signals

Risks include use of `pfn_to_page(PFN_DOWN(dma_addr))` on DMA addresses, no explicit `dmaengine_submit()` error check, named/fallback channel mismatch, endpoint 8/16 pairing assumptions, and compatibility restrictions that may force PIO for unaligned or short transfers. Tests should cover all endpoint-to-channel mappings, repeated allocate/release, named-channel and filter fallback paths, unaligned rejection, TX/RX program/complete, abort while busy, DMA request failure cleanup, and removal after partially allocated channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/ux500_dma.c -->
