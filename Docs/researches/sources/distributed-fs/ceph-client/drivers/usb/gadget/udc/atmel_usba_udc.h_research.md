# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/atmel_usba_udc.h

## Purpose
Defines the Atmel USBA UDC hardware register map, bitfield helpers, endpoint/DMA constants, debug categories, EP0 state enum, endpoint/request/controller structures, errata/config descriptors, and object conversion helpers consumed by `atmel_usba_udc.c`.

## Important APIs, Types, And Functions
The header defines USB controller registers (`USBA_CTRL`, `FNUM`, interrupt registers, endpoint reset, test), endpoint registers (`USBA_EPT_*`), DMA registers (`USBA_DMA_*`), bitfields for control, frame number, interrupt status, endpoint config/control/status, and DMA control/status. `USBA_BF`, `USBA_BFEXT`, and `USBA_BFINS` encode/extract/insert bitfields, while `usba_readl`, `usba_writel`, `usba_ep_readl`, `usba_ep_writel`, `usba_dma_readl`, and `usba_dma_writel` wrap relaxed MMIO.

Key types are `enum usba_ctrl_state`, `struct usba_dma_desc`, `struct usba_fifo_cfg`, `struct usba_ep`, `struct usba_ep_config`, `struct usba_request`, `struct usba_udc_errata`, `struct usba_udc_config`, and `struct usba_udc`. Conversion helpers are `to_usba_ep`, `to_usba_req`, and `to_usba_udc`.

## Control Flow
No complex control flow is implemented in the header. It defines the state machine values that `usba_control_irq` and `handle_ep0_setup` use, the endpoint capabilities that OF-compatible config arrays fill, and the register helpers that every runtime path uses for controller, endpoint, and DMA access. The `ep_is_control` macro separates EP0 from data endpoints in queueing and interrupt paths.

## State And Persistence Behavior
The structures model runtime-only kernel and hardware state. `struct usba_ep` holds register bases, FIFO address, endpoint name, queue, FIFO sizing, hardware index, DMA/isoc capability, direction/type flags, and debugfs state. `struct usba_request` tracks queue node, DMA control word, submitted/last/dma flags. `struct usba_udc` owns locks, MMIO bases, gadget driver, platform device, errata hooks, VBUS GPIO, endpoint array, clocks, bias/clock/suspend status, devstatus, test mode, interrupt-enable cache, debugfs root, and PMC regmap. Nothing here persists beyond device lifetime.

## Dependencies And Integration Points
Depends on Linux GPIO descriptors and USB gadget structures through the including C file. The register helpers assume the controller has separate control, endpoint, DMA, and FIFO regions laid out by `USBA_EPT_BASE`, `USBA_DMA_BASE`, and `USBA_FIFO_BASE`. Errata callbacks integrate with platform PMC regmap handling in the C file.

## Risks
`ep_is_idle` references `EP_STATE_IDLE`, which is not part of the active `enum usba_ctrl_state` and appears to be a stale macro; it is harmless only because it is unused. Relaxed MMIO access means ordering must be provided by surrounding code or hardware semantics where required. Bitfield macros use shifts based on `_SIZE` and `_OFFSET`; incorrect constants silently corrupt register programming. `USBA_NR_DMAS` is fixed at seven while some endpoint arrays contain up to sixteen endpoints, so DMA interrupt dispatch intentionally covers only DMA-capable low endpoints and must stay aligned with hardware. Structure bitfields are lock-protected assumptions, not atomic state.

## Test Signals
Header edits should be validated by building `atmel_usba_udc.c`, probing each compatible platform, checking endpoint register programming, DMA and FIFO transfer paths, EP0 state transitions, debugfs output, suspend/resume, and VBUS handling. Compile failures around `ep_is_idle`, wrong endpoint FIFO addresses, DMA IRQs for nonexistent channels, or invalid endpoint mapping messages after reset indicate contract regressions.
