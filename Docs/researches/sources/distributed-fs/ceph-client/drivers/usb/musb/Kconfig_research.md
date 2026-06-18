# Research: sources/distributed-fs/ceph-client/drivers/usb/musb/Kconfig

Purpose: defines the kernel configuration surface for Mentor Graphics Inventra MUSB high-speed dual-role USB controller support, including role selection, platform glue drivers, and DMA engine choices.

Important APIs, types, and options: top-level `USB_MUSB_HDRC` builds the `musb-hdrc` core when USB host or gadget infrastructure and MMIO are available. The role choice offers `USB_MUSB_HOST`, `USB_MUSB_GADGET`, and `USB_MUSB_DUAL_ROLE`, with dependencies ensuring host/gadget framework availability and DMA for gadget/dual-role operation. Platform glue symbols include `USB_MUSB_SUNXI`, `USB_MUSB_DA8XX`, `USB_MUSB_TUSB6010`, `USB_MUSB_OMAP2PLUS`, `USB_MUSB_DSPS`, `USB_MUSB_UX500`, `USB_MUSB_JZ4740`, `USB_MUSB_MEDIATEK`, and `USB_MUSB_POLARFIRE_SOC`. DMA options include `MUSB_PIO_ONLY`, `USB_UX500_DMA`, `USB_INVENTRA_DMA`, `USB_TI_CPPI41_DMA`, and `USB_TUSB_OMAP_DMA`.

Control flow: enabling `USB_MUSB_HDRC` opens a role selection and then platform/DMA selections. Platform symbols select or depend on needed PHY, extcon, role-switch, architecture, OF, or DMAengine support. DMA options are hidden when `MUSB_PIO_ONLY` is selected, making PIO the guaranteed fallback and DMA a per-platform compile-time feature.

State and persistence: Kconfig state is build-time only and persists in the kernel `.config`. It controls which source objects are compiled by the Makefile and which conditional code paths are visible in the core and glue drivers.

Dependencies and integration points: integrates with Linux USB host core, USB gadget core, architecture symbols, PHY frameworks, extcon, role switch, DMAengine, TI CPPI41, and platform-specific SoC support. The Makefile consumes these symbols to build core, gadget, host, debugfs, platform glue, and DMA backend objects.

Risks: invalid combinations can be subtle because role symbols concatenate in the Makefile to include host/gadget objects. `USB_INVENTRA_DMA` is shared across OMAP2PLUS, MediaTek, JZ4740, and PolarFire, so enabling it without compatible platform ops would fail later. `USB_MUSB_POLARFIRE_SOC` selects dual-role mode directly, which can surprise configurations expecting role choice only from user selection. PIO-only builds must still compile all role paths that reference DMA abstractions through stubs.

Test signals: run Kconfig build matrix for host-only, gadget-only, dual-role, and PIO-only; compile each platform glue under its architecture and `COMPILE_TEST` where allowed; verify module names and dependencies; and check that DMA backends are included only when their platform and DMA symbols are selected.
