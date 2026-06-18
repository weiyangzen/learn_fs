# sources/distributed-fs/ceph-client/drivers/usb/musb/musbhsdma.c

## Purpose

`musbhsdma.c` implements support for Mentor's high-speed DMA controller used by some MUSB instances. It allocates and manages up to eight DMA channels, programs channel address/count/control registers, handles DMA interrupts, aborts channels, and exposes controller create/destroy functions to platform glue. The source was read as a complete 455-line file.

## Important APIs, Types, and Functions

Important types are `struct musb_dma_channel` and `struct musb_dma_controller`. The DMA controller operations are `dma_channel_allocate`, `dma_channel_release`, `dma_channel_program`, and `dma_channel_abort`. Other key functions are `configure_channel`, `dma_controller_irq`, `musbhs_dma_controller_create`, `musbhs_dma_controller_create_noirq`, `musbhs_dma_controller_destroy`, `dma_controller_alloc`, and `dma_controller_stop`. Exported symbols include `dma_controller_irq`, create, create_noirq, and destroy.

## Control Flow

Platform glue creates the controller, optionally requests the named `"dma"` IRQ, and hands the `dma_controller` to core host/gadget code. Endpoint code allocates a free channel, then calls `channel_program`; programming rejects busy/unknown channels and unaligned DMA addresses on RTL 1.8+, records start/length/maxpacket metadata, writes address/count, and writes control bits for mode, burst, endpoint, direction, IRQ, and enable. The DMA IRQ handler clears interrupt status, detects spurious completion by checking zero counts, updates actual length from current address, marks channels free or bus-aborted, performs TX packet-ready fixups when needed, and calls `musb_dma_completion`.

## State and Persistence Behavior

The controller tracks used channels as a bitmask, per-channel endpoint/direction/start/length/maxpacket, channel status, desired mode, and actual length. Hardware channel registers persist until abort, completion, or controller reset. No disk persistence exists.

## Dependencies and Integration Points

The file depends on `musb_core.h`, `musb_dma.h`, MUSB HSDMA register offsets, IRQ APIs, platform devices, and the core `musb_dma_completion` callback. OMAP2430 platform ops can use this controller when `CONFIG_USB_INVENTRA_DMA` is enabled.

## Risks and Edge Cases

Risks include active channels during controller stop, DMA address alignment fallback, bus errors, spurious or coalesced DMA interrupts, correct TXCSR sequencing when aborting or completing mode 1 transfers, and actual length calculation by subtracting programmed start from current DMA address. `BUG_ON` is used for invalid busy/unknown programming states and mode 1 length smaller than packet size.

## Test Signals

Signals include DMA channel allocation exhaustion/release, unaligned DMA fallback to PIO, bulk TX/RX with mode 0 and mode 1, abort during active transfer, spurious interrupt handling, bus-error injection if possible, and platform create paths with and without a separate DMA IRQ.
