# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/aspeed-vhub/core.c

Purpose: top-level platform driver and interrupt/hardware initialization for the Aspeed vHub UDC, a controller that emulates a USB hub with multiple downstream gadget ports.

Important APIs, types, and functions: `ast_vhub_done`, `ast_vhub_nuke`, `ast_vhub_alloc_request`, and `ast_vhub_free_request` provide shared request lifecycle helpers. `ast_vhub_irq` dispatches endpoint-pool ACKs, per-device interrupts, hub EP0 events, and bus resume/suspend/reset. `ast_vhub_init_hw` programs PHY/reset, descriptor-ring mode, endpoint interrupts, EP0 DMA, upstream pullup, and interrupt enables. `ast_vhub_probe` parses device-tree sizing, maps registers, enables clock/reset, requests IRQ, sets DMA mask, allocates coherent EP0 buffers, initializes root hub EP0, ports, hub emulation, and hardware. `ast_vhub_remove` tears all of it down.

Control flow: platform probe allocates `struct ast_vhub`, sizes port and generic endpoint arrays from DT or defaults, prepares hardware resources, installs the IRQ handler, allocates one coherent EP0 buffer per port plus one for the virtual hub, initializes children, and finally connects upstream. IRQ handling runs under `vhub->lock`, acknowledges interrupt sources, and delegates to `epn`, `dev`, `ep0`, and `hub` helpers.

State and persistence: runtime state lives in `struct ast_vhub`, including register base, clock/reset, IRQ, port array, generic endpoint pool, coherent EP0 buffers, speed/USB1 forcing, and spinlock. No durable state exists.

Dependencies and integration points: depends on platform/OF, clocks, reset control, DMA mapping, libcomposite/gadget UDC APIs, and internal `vhub.h` helpers from `hub.c`, `dev.c`, `ep0.c`, and `epn.c`. Device-tree compatibles choose 32-bit or 64-bit DMA masks.

Risks: interrupt dispatch and request completion deliberately drop/reacquire the spinlock around gadget callbacks. Teardown must prevent stale IRQs by checking `ep0_bufs` and masking hardware. Descriptor count assumptions are compile-time checked. Register accessibility during suspend influences the decision not to stop logic clock.

Test signals: probe on AST2400/2500/2600/2700 compatibles, vary DT port/endpoint counts, bind multiple gadget drivers to ports, enumerate through the virtual hub, exercise endpoint traffic, suspend/resume/reset bus events, remove the platform device, and run with DMA API debugging.
