# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_acpi.h

## Purpose

`radeon_acpi.h` is the Radeon driver's local contract for AMD GPU-related ACPI control methods. It does not implement ACPI calls itself; instead it names method function IDs, bitfields, request codes, display vectors, and conditional helper prototypes used by the ACPI and VGA switcheroo integration paths elsewhere in the driver.

The file documents four firmware interfaces: `ATIF` for graphics-driver/SBIOS interaction and display/power notifications, `ATPX` for PowerXpress mux and discrete-GPU power control, `ATRM` for reading a discrete GPU VBIOS image through ACPI, and `ATCS` for AMD chipset-specific PCIe state and performance requests.

## Important APIs, Types, And Constants

The header forward-declares `struct radeon_device` and `struct acpi_bus_event`, then defines ACPI method IDs and payload bit meanings. `ATIF_FUNCTION_VERIFY_INTERFACE`, `ATIF_FUNCTION_GET_SYSTEM_PARAMETERS`, `ATIF_FUNCTION_GET_SYSTEM_BIOS_REQUESTS`, `ATIF_FUNCTION_SELECT_ACTIVE_DISPLAYS`, lid/TV/panel helpers, graphics-device enumeration, and external-GPU information constants describe the ATIF call surface. Their companion masks include notification capabilities, supported-function bits, pending SBIOS request bits, panel expansion modes, target GPU IDs, power-source IDs, ATIF display vector bits, and external/removable GPU flags.

The `ATPX_*` constants describe hybrid graphics support: verification, PX parameter discovery, dGPU power control, display mux control, I2C/AUX/HPD mux control, switch-start/end notifications, connector mapping, and display detection ports. Key flags include dynamic PowerXpress support, dynamic dGPU power-off, dGPU display requirements, Microsoft hybrid graphics support, per-connector output/HPD/I2C ownership, and symbolic integrated/discrete GPU selectors.

The `ATCS_*` constants describe chipset functions for dock/external state, PCIe performance requests, device-ready notification, and PCIe bus width setting. The performance request constants encode advertise/wait flags, link-speed request type, remove/low-power/Gen1/Gen2/Gen3 requests, and return states such as refused, complete, and in progress.

Under `CONFIG_VGA_SWITCHEROO`, the file exposes `radeon_register_atpx_handler()`, `radeon_unregister_atpx_handler()`, `radeon_has_atpx_dgpu_power_cntl()`, `radeon_is_atpx_hybrid()`, `radeon_has_atpx()`, and `radeon_atpx_dgpu_req_power_for_displays()`. These are the only function prototypes in this header and form the public Radeon-side hook into Linux hybrid-GPU switching.

## Control Flow

There is no executable control flow in this header. Its comments define the expected ACPI transaction flow: the driver verifies an interface, discovers system parameters and notification mode, receives `Notify(VGA, 0x81)` or a custom VGA notification, calls `GET_SYSTEM_BIOS_REQUESTS`, then reacts to pending request bits by performing driver work such as display detection or display switching before calling a method such as `SELECT_ACTIVE_DISPLAYS`.

For PowerXpress, the implied control flow is capability discovery through ATPX, then optional dGPU power control and mux switching. For ATCS, the implied flow is external-state or PCIe capability discovery, followed by a PCIe performance or bus-width request and interpretation of the returned status.

## State And Persistence Behavior

This file stores no runtime state. The persistent state it describes lives in platform firmware or CMOS: TV standard, panel expansion mode, system BIOS request queues, mux ownership, dGPU power state, dock state, and PCIe/link settings. The driver-visible state is represented as bitmasks and small integer values parsed from ACPI buffers.

Because ACPI buffers are firmware ABI payloads, the sizes and fields in the comments are part of the driver's state contract even though the header does not declare packed C structs for them.

## Dependencies And Integration Points

The direct dependencies are kernel ACPI support, Radeon device structures, and optional `CONFIG_VGA_SWITCHEROO`. The constants are consumed by Radeon ACPI implementation code that evaluates ACPI methods and by switcheroo paths that need to know whether a platform has ATPX and whether the dGPU must be powered for displays.

The integration boundary is firmware-facing and display/power-management-facing: display hotplug/reconfiguration, panel brightness, lid state, dock/external GPU state, hybrid graphics muxes, VBIOS retrieval, and PCIe performance management all depend on these definitions matching platform firmware.

## Risks And Edge Cases

The main risk is ABI drift or misinterpretation of firmware bitfields. A wrong bit position can power off a display-driving dGPU, select the wrong mux owner, miss a BIOS display-switch request, or issue a PCIe performance request that firmware refuses. Several payloads have variable structure sizes, repeated structures, or optional trailing fields, so callers must validate returned buffer sizes before reading fields.

Hybrid graphics platforms are particularly fragile because old PowerXpress, dynamic PX, A+A systems, and Microsoft hybrid graphics use overlapping but not identical ATPX features. ATIF notification handling also depends on whether firmware uses standard VGA notify code `0x81` or a custom `0xd0`-range code.

## Test Signals

Useful signals include boot and resume tests on systems with and without ATPX/ATIF/ATCS, VGA switcheroo registration state, dGPU runtime power transitions, display mux switching, hotplug/display-switch notifications, lid and brightness events, VBIOS retrieval through ATRM on PowerXpress laptops, and ACPI method buffer validation under firmware with older interface versions. Regression logs to watch include ACPI evaluation failures, missing switcheroo handlers, unexpected dGPU power requirements, and failed PCIe performance requests.
