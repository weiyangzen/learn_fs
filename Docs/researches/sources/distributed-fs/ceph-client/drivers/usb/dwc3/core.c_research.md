# sources/distributed-fs/ceph-client/drivers/usb/dwc3/core.c

## Purpose
`core.c` is the central Synopsys DesignWare USB3 DWC3 controller driver. It validates the hardware ID and hardware parameters, maps the DWC3 global/device register window, discovers clocks, resets, PHYs, extcon/role-switch state, and power-supply integration, then initializes the controller in host, gadget, or dual-role mode. It also exports core lifecycle and PM helpers for platform glue drivers that embed `struct dwc3` directly.

## Important APIs, Types, and Functions
The exported core API includes `dwc3_core_probe()`, `dwc3_core_remove()`, `dwc3_core_init()`, `dwc3_core_exit()`, `dwc3_core_soft_reset()`, `dwc3_set_prtcap()`, `dwc3_set_mode()`, `dwc3_enable_susphy()`, event-buffer setup/cleanup, runtime PM helpers, and system PM helpers. `dwc3_probe()` is the standalone platform wrapper for compatible strings such as `snps,dwc3`.

Important internal setup functions are `dwc3_get_properties()`, `dwc3_get_software_properties()`, `dwc3_get_dr_mode()`, `dwc3_core_is_valid()`, `dwc3_cache_hwparams()`, `dwc3_core_get_phy()`, `dwc3_phy_setup()`, `dwc3_phy_init()`, `dwc3_phy_power_on()`, `dwc3_get_num_ports()`, and `dwc3_core_init_mode()`. Register programming is concentrated in helpers for GCTL/GUCTL/GFLADJ, GSBUSCFG0, threshold registers, USB2/USB3 PHY config, and DWC31/DWC32 revision-specific workarounds.

## Control Flow
Probe takes the memory resource, reserves the DWC3 global range while leaving xHCI registers for the child xHCI driver, maps registers, reads properties, grabs power supply, resets/clocks, validates IP ID, caches HWPARAMS, sets DMA masks, determines port counts, enables runtime PM, allocates event buffers, resolves extcon, coerces `dr_mode` to match hardware and build-time host/gadget support, initializes the core, starts debugfs, then initializes the selected role. Error paths unwind in reverse order: role/debugfs/event buffers, PHYs, ULPI, runtime PM, clocks, reset, and power supply.

Dual-role changes are asynchronous through `dwc3_set_mode()` and `__dwc3_set_mode()` on `system_freezable_wq`. The worker exits the current host/gadget/OTG role, may issue a GCTL core soft reset for DRD switching, sets `GCTL.PrtCapDir`, and initializes the target role, including VBUS and generic PHY mode changes. Gadget transitions set event buffers before gadget init; host transitions set VBUS and all PHY ports to host mode.

## State and Persistence Behavior
All persistent runtime state lives in `struct dwc3`: cached hardware params, IP/revision/version type, current/desired role, OTG role state, event buffer pointer, PHY pointers, clocks, reset, debugfs regset, power-supply pointer, quirk bits, runtime PM flags, and suspend bookkeeping. No disk persistence exists. Hardware register state is reprogrammed on probe, role switch, resume, and full reinit paths. Event buffers are coherent DMA allocations with a software cache and are masked/cleared on cleanup.

## Dependencies and Integration Points
The file integrates Linux platform driver, OF/ACPI properties, runtime PM, pinctrl PM, clk/reset frameworks, USB PHY and generic PHY frameworks, extcon, usb-role-switch, xHCI child resources, power_supply current limit programming, debugfs, and the DWC3 gadget/host/OTG modules. Platform glue drivers can call `dwc3_core_probe()` with `ignore_clocks_and_resets`, `skip_core_init_mode`, or software `dwc3_properties`.

## Risks
Main risks are ordering-sensitive register and PHY sequencing, revision-specific workarounds, DRD races between workqueue mode changes and PM, array bounds for multiport PHYs, event-buffer cleanup when device halt fails, and property combinations that force unsupported speeds or modes. PM paths are especially sensitive: host runtime suspend may leave PHY PM to xHCI, gadget suspend tears down the core when active, and system suspend may force SUSPHY for wake-capable platforms.

## Test Signals
Useful signals are successful probe/remove in host, peripheral, and OTG configurations; xHCI child enumeration; gadget enumeration and disconnect; role switch via extcon, USB role switch, and debugfs; runtime autosuspend/resume while disconnected; system suspend/resume with wake enabled and disabled; soft-reset timeout logging; debugfs `regdump`, `mode`, and `link_state`; DMA mask setup on 64-bit DWC3; multiport host enumeration; and regression tests for all quirk properties parsed in `dwc3_get_properties()`.
