# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/udc.h

Purpose: tiny board-facing declaration for configuring the PXA2xx USB device controller.

Important APIs/types/functions: forward-facing API is `pxa_set_udc_info(struct pxa2xx_udc_mach_info *info)`.

Control flow: no local flow; board files call the setter to hand platform data to the UDC core.

State and persistence: no local state. Platform data influences UDC runtime wiring.

Dependencies and integration points: depends on `struct pxa2xx_udc_mach_info` from the PXA UDC platform data area and integrates board files with the USB gadget controller.

Risks: declaration-only header can drift if the core signature changes. Wrong platform data causes USB role/connect behavior failures.

Test signals: compile coverage and USB gadget enumeration on boards that call the setter.
