<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-ic.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-ic.c

Purpose: Implements the i.MX8 DC interrupt controller that maps many hardware interrupt lines into a generic IRQ domain and chained handlers.

Important APIs/types/functions: Defines `struct dc_ic_data`, `struct dc_ic_entry`, chained handler `dc_ic_irq_handler()`, probe/remove, runtime PM hooks, and platform driver `dc_ic_driver`.

Control flow: Probe maps the controller registers, initializes regmap, gets AXI clock, validates all platform IRQ resources except reserved IRQ 35, enables runtime PM, masks/clears all interrupts, sets user interrupt masks, creates a linear IRQ domain with generic chips, configures ack/mask registers, maps each parent IRQ from device tree, and installs chained handlers. The chained handler reads user status/enable for the bank and dispatches the matching virq.

State and persistence behavior: Stores regmap, AXI clock, parent IRQ mappings, and IRQ domain. Hardware mask/enable/clear state is initialized at probe and controlled through generic IRQ chip callbacks.

Dependencies: IRQ domain/generic chip APIs, chained IRQ helpers, OF IRQ parsing, runtime PM, clocks, regmap, and platform resources.

Integration points: Subdevices request named IRQs that are routed through this controller. The top-level DC driver excludes the interrupt controller from component matching because it is infrastructure rather than a display component.

Risks: The chained handler handles only the bit corresponding to the parent entry, so parent-to-child IRQ mapping must be exact. Reserved/unused masks are hardware-specific. Failure unwind must remove domains and runtime PM refs.

Test signals: IRQ domain creation, all named IRQs resolving for CRTC/extdst/display-engine, interrupt masking/unmasking, runtime suspend/resume clock control, and synthetic interrupt tests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-ic.c -->
