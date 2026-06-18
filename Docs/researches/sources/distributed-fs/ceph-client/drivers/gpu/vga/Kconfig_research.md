# sources/distributed-fs/ceph-client/drivers/gpu/vga/Kconfig

Purpose: configuration entry for laptop hybrid graphics switching support.

Important symbols: `VGA_SWITCHEROO` is a boolean option depending on X86, ACPI, PCI, and framebuffer console compatibility; it selects `VGA_ARB`.

Control flow: no runtime logic. The symbol controls compilation of the switcheroo subsystem.

State and persistence: no state.

Dependencies and integration: targets muxed and muxless hybrid graphics laptops, including ATI PowerXpress and NVIDIA HybridPower style systems. Integrates with VGA arbitration and framebuffer console constraints.

Risks: platform dependencies are strict; enabling on unsupported architectures is blocked. Runtime usefulness still depends on GPU drivers and mux/power handlers registering.

Test signals: build inclusion of `vga_switcheroo.o` and debugfs switch interface on systems with two GPU clients plus a handler.
