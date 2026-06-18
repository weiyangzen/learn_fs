# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/musb_dma.h

Purpose: defines the generic DMA abstraction used by the MUSB core and platform-specific DMA backends. It lets host/gadget endpoint code interact with different DMA engines through common channel/controller operations while preserving PIO-only fallback builds.

Important APIs, types, and symbols: register offsets define the Inventra HSDMA register block. `DMA_ADDR_INVALID` marks invalid DMA addresses. Capability macros include `is_dma_capable`, `musb_dma_ux500`, `musb_dma_cppi41`, `tusb_dma_omap`, `musb_dma_inventra`, and `is_cppi_enabled`. `enum dma_channel_status` defines unknown/free/busy/bus-abort/core-abort states. `struct dma_channel` tracks backend-private data, max length, actual length, status, desired mode, and RX packet completion. `struct dma_controller` provides channel allocation/release/program/abort/compatibility and optional platform completion callback.

Control flow: endpoint code asks a `dma_controller` for a channel tied to a hardware endpoint and direction, programs it with maxpacket, mode, DMA address, and length, observes completion through backend interrupts/callbacks, and calls `musb_dma_completion` to resume host/gadget endpoint state. Abort/release are used during dequeue, endpoint disable, teardown, and error recovery. In `CONFIG_MUSB_PIO_ONLY`, controller create/destroy stubs compile out DMA.

State and persistence: no persistent state. Runtime state lives in backend-defined `private_data`, status fields, actual length, mode, and controller callbacks. The MUSB core holds the selected controller pointer in `struct musb`.

Dependencies and integration points: forward-declares `struct musb_hw_ep` and integrates with MUSB core, host/gadget endpoint code, and backend implementations for Inventra HSDMA, TUSB OMAP DMA, CPPI41, and UX500. Platform glue installs the desired `dma_init`/`dma_exit` hooks through `musb_platform_ops`.

Risks: DMA status is protected by the overall controller spinlock by convention; backend code must follow that locking or endpoint code can race status changes. `private_data` is a generic `void *` and the comment notes it ideally should be more specific. PIO-only stubs return NULL, so callers must handle no DMA path cleanly. Backend `is_compatible` decisions are critical for hardware errata such as CPPI41 RX constraints. Global DMA factory pointers in `musb_core.c` mean heterogeneous platform combinations need scrutiny.

Test signals: compile PIO-only and all DMA backend configurations, run endpoint transfers with DMA enabled/disabled via module parameter, exercise channel allocation exhaustion, incompatible transfer fallback, abort on active transfers, bus/core abort reporting, short RX packet handling, and `musb_dma_completion` dispatch in host and gadget roles.
