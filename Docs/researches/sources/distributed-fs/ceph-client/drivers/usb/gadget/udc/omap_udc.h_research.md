# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/omap_udc.h

## Purpose

`omap_udc.h` is the private register and state header for the OMAP full-speed USB device controller driver. It defines the UDC register offsets, bit fields for endpoint selection/control/status, device status, IRQ and DMA control, endpoint RX/TX FIFO configuration, private request/endpoint/controller structures, debug macros, and OMAP1 VBUS/HMC helper macros used by `omap_udc.c`.

## Important APIs, Types, and Functions

The header maps controller registers such as `UDC_EP_NUM`, `UDC_DATA`, `UDC_CTRL`, `UDC_STAT_FLG`, `UDC_SYSCON1`, `UDC_SYSCON2`, `UDC_DEVSTAT`, `UDC_IRQ_EN`, `UDC_DMA_IRQ_EN`, `UDC_IRQ_SRC`, `UDC_EPN_STAT`, `UDC_DMAN_STAT`, `UDC_RXDMA_CFG`, `UDC_TXDMA_CFG`, `UDC_TXDMA(chan)`, `UDC_RXDMA(chan)`, `UDC_EP_RX(endpoint)`, and `UDC_EP_TX(endpoint)`. Their bit definitions express endpoint selection, FIFO enable/clear/halt/toggle, ACK/NAK/stall/FIFO status, device attach/reset/suspend/configuration state, endpoint and DMA IRQ bits, and FIFO buffer configuration.

`struct omap_req` wraps `struct usb_request` with queue linkage, current DMA segment byte count, and a mapped flag. `struct omap_ep` wraps `struct usb_ep` with queue/list state, endpoint name, hardware maxpacket/address/type, double-buffer and stopped flags, FIFO/ACK tracking, DMA channel and logical channel IDs, DMA counter, back-pointer to `struct omap_udc`, and the PIO OUT recovery timer. `struct omap_udc` wraps `struct usb_gadget` with the bound driver, spinlock, 32 endpoint slots, device status, clear-halt command, transceiver pointer, ISO list, softconnect/VBUS/EP0 flags, remove completion, clocks, and clock-request state.

Debug macros `ERR`, `WARNING`, `INFO`, `DBG`, and optional `VDBG` standardize logging. VBUS/HMC macros (`VBUS_W2FC_1510`, `VBUS_CTRL_1510`, `VBUS_MODE_1510`, `HMC_1510`, `HMC_1610`, `HMC`) abstract board and SoC register differences used during probe and VBUS handling.

## Control Flow

This header has no standalone execution, but it defines the register contract used by every path in `omap_udc.c`. `use_ep()` selects endpoints by writing `UDC_EP_NUM`, PIO reads and writes use `UDC_DATA`, endpoint operations use `UDC_CTRL` and `UDC_STAT_FLG`, EP0 and state IRQs use `UDC_IRQ_SRC`, and DMA paths program `UDC_RXDMA_CFG`, `UDC_TXDMA_CFG`, and per-channel DMA control registers. Probe-time endpoint layout uses `UDC_EP_RX()` and `UDC_EP_TX()` before `UDC_CFG_LOCK` is set.

The structure layout also dictates runtime lookup: OUT endpoints occupy `udc->ep[endpoint_number]`, IN endpoints occupy `udc->ep[16 + endpoint_number]`, and EP0 is `udc->ep[0]`. That convention is used by request queueing, IRQ decoding, DMA completion, and setup request endpoint-halt handling.

## State and Persistence Behavior

All state is runtime-only. Register definitions describe volatile hardware state; structure fields describe in-memory state for the currently registered platform device. The header does not define persistent storage. State visible outside the driver is reflected through USB gadget registration, USB bus attach/configuration state, endpoint FIFOs, DMA programming, clocks, PHY/OTG state, and optional proc debug output.

The fixed-size `ep[32]` array is a notable state convention: it supports 16 endpoint numbers in each direction by offsetting IN endpoints by 16. Endpoint names are bounded to 14 bytes, and FIFO allocation assumes the controller's 2 KiB packet RAM.

## Dependencies and Integration Points

The header assumes OMAP-specific symbols such as `UDC_BASE`, `MOD_CONF_CTRL_0`, `OTG_SYSCON_2`, `omap_readl()`, and CPU/machine helpers are available through the source file's OMAP includes. It integrates local driver state with the USB gadget API, Linux timers and lists, USB PHY/OTG types, clocks, completions, and OMAP1 platform/SoC register access.

## Risks and Test Signals

Risks include incorrect register-bit definitions, endpoint direction index mistakes in the split `ep[32]` array, FIFO allocation overflow beyond 2 KiB, endpoint name truncation, and mismatched `UDC_CLR_HALT` behavior across UDC revisions. DMA channel macros number channels 1-3, so off-by-one mistakes can corrupt DMA IRQ enables or endpoint/channel routing.

Useful test signals include compile coverage on OMAP15xx and OMAP16xx configurations, probe-time register programming for every `fifo_mode`, endpoint lookup for IN and OUT endpoint numbers, DMA IRQ enable/disable bit calculations for channels 1-3, EP0 and non-EP0 halt/clear paths, device-status change decoding, VBUS/HMC detection on supported boards, and proc/debug output matching actual endpoint/register state.
