# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/Makefile

Purpose: maps MUSB Kconfig symbols to kernel objects, assembling the common `musb_hdrc` core module plus optional host, gadget, debugfs, platform glue, and DMA backend objects.

Important APIs, types, and targets: `obj-$(CONFIG_USB_MUSB_HDRC) += musb_hdrc.o` builds the core module. `musb_hdrc-y` always includes `musb_core.o` and `musb_trace.o`. Host support adds `musb_virthub.o` and `musb_host.o`; gadget support adds `musb_gadget_ep0.o` and `musb_gadget.o`; debugfs adds `musb_debugfs.o`. Platform glue objects are `omap2430.o`, `musb_dsps.o`, `tusb6010.o`, `da8xx.o`, `ux500.o`, `jz4740.o`, `sunxi.o`, `mediatek.o`, and `mpfs.o`. DMA backend objects are `musbhsdma.o`, `tusb6010_omap.o`, `ux500_dma.o`, and `musb_cppi41.o`.

Control flow: Kbuild expands role symbols by concatenating `CONFIG_USB_MUSB_HOST` and `CONFIG_USB_MUSB_DUAL_ROLE` or gadget equivalents, so dual-role builds include both host and gadget objects. Trace compilation adds `-I$(src)` for `musb_trace.o` so `define_trace.h` can find the local trace header.

State and persistence: no runtime state. Build output shape persists in kernel/module artifacts: the main module is `musb_hdrc` while platform glue may be built as separate objects/modules depending on configuration.

Dependencies and integration points: consumes the symbols from `Kconfig` and depends on source files in the same directory. It integrates with Linux Kbuild's composite-object mechanism and tracepoint header include requirements.

Risks: role-object inclusion depends on string concatenation, so unusual Kconfig states could include or omit host/gadget code unexpectedly if dependencies regress. Tracepoint builds are sensitive to the local include path. Platform glue objects are built independently from the core object; symbol visibility through exports and module load ordering must remain valid.

Test signals: compile representative configurations for built-in and modular `USB_MUSB_HDRC`, all three roles, debugfs on/off, PIO-only and each DMA backend, and each platform glue as module where Kconfig permits. Verify `musb_trace.o` compiles with generated trace headers.
