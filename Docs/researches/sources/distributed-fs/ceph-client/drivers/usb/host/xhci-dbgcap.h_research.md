# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgcap.h

Purpose: declares the xHCI DbC register layout, context/string/request data structures, constants, state machine values, endpoint helpers, and public DbC APIs used by `xhci-dbgcap.c` and `xhci-dbgtty.c`.

Important APIs and types: `struct dbc_regs` mirrors the DbC extended capability register block; `struct dbc_info_context` and descriptor/string structs describe the DMA context data written to DbC; `enum dbc_state` defines `DS_DISABLED` through `DS_CONFIGURED`; `struct dbc_ep`, `struct xhci_dbc`, `struct dbc_port`, and `struct dbc_request` are the core runtime objects. Public APIs include `xhci_create_dbc_dev()`, `xhci_remove_dbc_dev()`, `xhci_dbc_init/exit()`, `xhci_dbc_suspend/resume()`, `xhci_alloc_dbc()`, `xhci_dbc_remove()`, `dbc_alloc_request()`, `dbc_free_request()`, and `dbc_ep_queue()`.

Control flow: this header shapes the split between the hardware DbC engine and the tty backend. `struct dbc_driver` provides `configure()` and `disconnect()` callbacks invoked by the hardware layer. Endpoint helper macros map context byte offsets and ring enqueue DMA addresses for bulk IN/OUT. Conditional stubs compile DbC calls away when `CONFIG_USB_XHCI_DBGCAP` is disabled.

State and persistence: `struct xhci_dbc` centralizes volatile state: MMIO regs, rings, ERST, context, DMA string table, identity strings, state enum, delayed work, endpoints, backend driver, and backend private pointer. `struct dbc_port` stores tty-side pools, queues, kfifo-related state, minor number, tasklet, and registration flags. No persistent storage is defined.

Dependencies and integration points: includes Linux tty and kfifo support and depends on xHCI core types declared elsewhere. The header is included by the DbC hardware and tty sources and referenced from generic xHCI lifecycle code. Compile-time behavior depends on `CONFIG_USB_XHCI_DBGCAP` and `CONFIG_PM`.

Risks: layout definitions must match the xHCI DbC specification exactly; any incorrect offset or endian annotation corrupts hardware interaction. `DBC_CONTEXT_SIZE` and context-offset macros assume three 64-byte contexts. `dbc_ep_dma_direction()` encodes direction as a boolean convention, so inconsistent `BULK_IN/BULK_OUT` use would invert DMA mapping direction. Stubs return success when disabled, so call sites must not rely on side effects if DbC is not configured.

Test signals: build with DbC enabled/disabled; sparse/endian checking on `__le*` fields; structure offset validation against spec during review; tty backend compile coverage; PM-enabled and PM-disabled builds.
