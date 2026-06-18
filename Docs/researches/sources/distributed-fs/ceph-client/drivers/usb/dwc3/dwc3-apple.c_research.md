# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-apple.c

## Purpose
`dwc3-apple.c` is the Apple Silicon DWC3 glue driver. It handles a platform where DWC3, USB2/USB3 PHY mode selection, Type-C cable orientation, resets, and Apple-specific CIO registers must be sequenced very carefully. Unlike normal glue, the core probe may be deferred until the first cable role event.

## Important APIs, Types, and Functions
The state model is `enum dwc3_apple_state`: `PROBE_PENDING`, `NO_CABLE`, `HOST`, and `DEVICE`. `struct dwc3_apple` embeds `struct dwc3`, stores Apple MMIO, reset, USB role switch, lock, and resource pointers. Key functions are `dwc3_apple_core_probe()`, `dwc3_apple_core_init()`, `dwc3_apple_init()`, `dwc3_apple_exit()`, role-switch set/get callbacks, `dwc3_apple_setup_role_switch()`, `dwc3_apple_probe()`, and `dwc3_apple_remove()`.

## Control Flow
Probe asserts reset, obtains the DWC3 core resource and Apple-specific MMIO, sets state to `PROBE_PENDING`, and registers a USB role switch. It deliberately does not call `dwc3_core_probe()` yet because the PHY needs cable mode/orientation first. On role switch to host or device, the mutex-protected set callback exits any current role, configures the USB2 PHY mode while powered off, deasserts reset, probes or reinitializes the core, programs Apple CIO timing/LFPS registers, sets DWC3 `dr_mode` and PRTCAP, enables SUSPHY, sets USB3 PHY mode, and starts xHCI or gadget. On `USB_ROLE_NONE`, it tears down host/gadget, keeps SUSPHY enabled for PHY shutdown sequencing, exits the core, asserts reset, and returns to `NO_CABLE`.

## State and Persistence Behavior
State is the explicit enum plus the embedded `struct dwc3`. The driver intentionally destroys and recreates live hardware state on every cable disconnect or role change. No persistent storage exists. `dwc3_core_probe()` is called once after first cable connect; later cable cycles use `dwc3_core_init()`.

## Dependencies and Integration Points
The driver uses reset controls, USB role switch, generic PHY modes, Apple-specific MMIO registers, and the exported DWC3 core/host/gadget APIs. It passes `ignore_clocks_and_resets` and `skip_core_init_mode` to `dwc3_core_probe()` because this glue owns the reset and role startup sequence.

## Risks
Ordering is the dominant risk. Comments document possible nonfunctional ports, watchdog resets, or SoC-level reset if PHY/core sequencing is wrong. State transitions must be serialized by the mutex. Remove currently obtains driver data via the embedded core pointer, which only exists after core probe has set drvdata; if no cable ever connected, that path must remain valid in the surrounding driver model. Unknown Apple CIO register values are empirical and hardware-specific.

## Test Signals
Test no-cable boot, first host connect, first device connect, repeated connect/disconnect, host-to-device flips, duplicate role notifications, remove before first cable event, remove after active role, USB2-only and USB3 devices, Type-C orientation changes, and absence of watchdog resets. Verify DWC3 debug output, xHCI/gadget enumeration, and reset assertion/deassertion order.
