# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hw.h

## Purpose
`hw.h` is the DWC2 hardware register and bitfield definition header. It defines global, device-mode, host-mode, power-management, FIFO, endpoint/channel, transfer-size, and DMA descriptor constants used throughout the DWC2 core, host, gadget, platform, and parameter code.

## Important APIs, Types, And Functions
- Register address macro: `HSOTG_REG(x)` and register offsets such as `GOTGCTL`, `GAHBCFG`, `GUSBCFG`, `GRSTCTL`, `GINTSTS`, `GINTMSK`, `GHWCFG1-4`, `GLPMCFG`, `GPWRDN`, `HCFG`, `HFIR`, `HFNUM`, `HPRT0`, `HCCHAR(ch)`, `HCSPLT(ch)`, `HCINT(ch)`, `HCINTMSK(ch)`, `HCTSIZ(ch)`, and endpoint register macros.
- Bit masks and shifts for global interrupts, OTG state, reset, FIFO sizing, hardware configuration discovery, LPM, power-down, device endpoint control, host port control, host channel control, split transactions, and transfer sizes.
- Helper getter macros such as `FIFOSIZE_DEPTH_GET()`, `GNPTXSTS_NP_TXQ_SPC_AVAIL_GET()`, `DXEPTSIZ_PKTCNT_GET()`, and `DXEPTSIZ_XFERSIZE_GET()`.
- DMA type: `struct dwc2_dma_desc { u32 status; u32 buf; } __packed`.
- Host and device DMA descriptor status masks such as `HOST_DMA_A`, `HOST_DMA_IOC`, `HOST_DMA_NBYTES_MASK`, `DEV_DMA_BUFF_STS_MASK`, `DEV_DMA_STS_MASK`, and isochronous byte/count fields.

## Control Flow
This header has no executable control flow. It provides the symbolic interface used by C files that read, write, mask, shift, and compose DWC2 memory-mapped registers. Runtime flow emerges in callers: platform code validates `GSNPSID`, params code decodes `GHWCFG*`, host interrupt code decodes `GINTSTS`, `HPRT0`, `HCINT`, and `HCTSIZ`, queue code reads `HPRT0`, and gadget code uses endpoint definitions.

## State And Persistence Behavior
The header itself stores no state. The constants describe persistent hardware state in memory-mapped registers and DMA descriptors owned by the controller and driver. Correctness depends on masks and shifts matching the IP revision. The packed DMA descriptor layout is an ABI between CPU memory and DWC2 DMA engines.

## Dependencies And Integration Points
`hw.h` expects kernel bit macros such as `BIT()` and `GENMASK()` to be available through including headers. It is included indirectly through DWC2 core headers by most driver components. `params.c` depends on `GHWCFG*`, `FIFOSIZE_*`, and core revision masks to derive capabilities. `hcd_intr.c` and host code rely on host-channel and interrupt constants. Platform suspend/resume and power code use `GOTGCTL`, `GUSBCFG`, `GGPIO`, `PCGCTL`, and power-down bits.

## Risks
- Register aliases and overlapping bit definitions are intentional in several places, such as packet status values and endpoint interrupt bits. Callers must use the right symbolic name for host vs device context.
- Incorrect masks or shifts corrupt hardware programming globally; this header has high blast radius.
- Some constants encode hardware quirks or misspellings from register names, so cleanup can break code that mirrors documentation naming.
- DMA descriptor fields have different meanings for host/gadget and generic/isoc transfers. Reusing the wrong mask can produce data corruption.
- Channel and endpoint register macros assume a fixed stride; any IP variant with different layout would need separate handling.

## Test Signals
- Compile coverage is a primary signal: all DWC2 host/gadget/platform objects should build with no undefined or type issues.
- Runtime validation comes from successful core version and hardware parameter detection in probe.
- Host and gadget transfer tests validate the HC/EP masks and transfer-size fields indirectly.
- DMA and descriptor-DMA transfer tests validate descriptor layout and host/device DMA status constants.
- Suspend/resume and low-power tests exercise `GLPMCFG`, `GPWRDN`, `PCGCTL`, and restore-related bits.
