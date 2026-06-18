# sources/distributed-fs/ceph-client/drivers/usb/fotg210/fotg210.h

## Purpose
`fotg210.h` is the shared private header for the FOTG210 core, host, and gadget drivers. It defines the outer controller object shared by HCD and UDC code, role/port metadata, VBUS control entry point, and conditional host/device probe/remove declarations.

## Important APIs, Types, and Functions
`enum gemini_port` identifies the Gemini integration port as none, port 0, or port 1. `struct fotg210` holds the common device pointer, MMIO resource, mapped base address, peripheral clock, syscon regmap, and Gemini port selection. `fotg210_vbus()` is the shared VBUS control hook. Depending on `CONFIG_USB_FOTG210_HCD`, host functions `fotg210_hcd_probe()`, `fotg210_hcd_remove()`, `fotg210_hcd_init()`, and `fotg210_hcd_cleanup()` are declared or stubbed. Depending on `CONFIG_USB_FOTG210_UDC`, gadget functions `fotg210_udc_probe()` and `fotg210_udc_remove()` are declared or stubbed.

## Control Flow
The outer FOTG210 core includes this header and can call the host and/or gadget probe/remove functions without open-coded preprocessor branches. If a role driver is disabled, the inline stub returns success for probe/remove and does nothing for init/cleanup, allowing the core driver to compile across host-only, device-only, and dual-role configurations. Host and gadget implementations receive the same `struct fotg210 *` so they share resources and role-control behavior.

## State and Persistence Behavior
`struct fotg210` is the durable runtime container for the platform instance while the core driver is bound. It owns the common MMIO base and resource metadata consumed by both HCD and UDC implementations. It does not persist to disk. Role-specific state lives in `struct fotg210_hcd` or `struct fotg210_udc`, not in this header.

## Dependencies and Integration Points
This header integrates platform device code, clock framework, regmap/syscon integration, and USB host/device subdrivers. It is used by `fotg210-hcd.c` and `fotg210-udc.c`, and likely by the FOTG210 core file that matches Devicetree compatibles such as `faraday,fotg200`, `faraday,fotg210`, or `cortina,gemini-usb`. The VBUS hook connects gadget `vbus_session` behavior to board/SoC-specific power or role registers.

## Risks
The stub probes return success when a role is disabled, so the core must treat disabled roles as intentionally absent rather than as initialized hardware. Shared ownership of `base`, `res`, `pclk`, and `map` means host/device remove paths must not unmap or disable resources owned by the core. Role switching is sensitive because HCD and UDC share registers and IRQs on the same OTG block.

## Test Signals
Build matrix coverage should include host-only, gadget-only, both enabled, and both disabled if Kconfig allows it. Runtime testing should verify that the core probes successfully in each enabled role combination, disabled role stubs do not register devices, VBUS changes reach board control, and remove paths do not double-free shared resources.
