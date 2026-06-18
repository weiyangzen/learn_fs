# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_acpi.h

## Purpose
This header defines AMD GPU ACPI method data contracts and constants for ATIF, ATPX, ATRM, and ATCS firmware interfaces. It is a shared ABI header between AMDGPU ACPI handling code and platform firmware buffers.

## Important APIs, Types, And Constants
Packed structures model method input and output buffers: `atif_verify_interface`, `atif_system_params`, `atif_sbios_requests`, `atif_qbtc_arguments`, `atif_qbtc_data_point`, `atif_qbtc_output`, `atcs_verify_interface`, `atcs_pref_req_input`, `atcs_pref_req_output`, `atcs_pwr_shift_input`, `atcs_get_uma_size_output`, and `atcs_set_uma_allocation_size_input`.

ATIF constants define function IDs and bit flags for interface verification, system parameters, system BIOS requests, thermal notifications, brightness transfer characteristics, undock notification, and external GPU information. ATPX constants define PowerXpress interface verification, PX parameters, dGPU power control, display and I2C mux control, switch notifications, connector mapping, and detection ports. ATCS constants define chipset-specific external state, PCIe performance requests, device-ready notification, bus-width control, power-shift control, UMA size query, and UMA allocation sizing.

`ATIF_QBTC_MAX_DATA_POINTS` is 99. The file has static assertions tying `atif_qbtc_data_point` to `amdgpu_dm_luminance_data` and the max point count to `MAX_LUMINANCE_DATA_POINTS`, so display-manager brightness-curve parsing depends on this layout.

## Control Flow
There is no executable code. Runtime control flow is driven by callers such as `amdgpu_acpi.c`, `amdgpu_atpx_handler.c`, and PowerPlay hardware-manager code. Those callers check the `*_SUPPORTED` function bitmasks, construct the packed input buffers, invoke ACPI control methods, then parse output buffers according to these structures and flags.

## State And Persistence
This header defines firmware ABI state but stores none itself. The values are transient ACPI method buffers and notification flags. Some data, such as supported function bits, pending SBIOS requests, connector mappings, external GPU info, power source, and brightness curves, may be cached by callers after parsing.

## Dependencies And Integration Points
The header includes `<linux/types.h>` and relies on packed layout compatibility with ACPI firmware. It integrates with display brightness handling, PowerXpress dGPU power and mux switching, PCIe performance requests, dock/external-state handling, UMA sizing, and system BIOS notifications.

The ATIF, ATPX, ATRM, and ATCS method comments in the file are part of the integration contract: each method receives an integer function code plus a 256-byte parameter buffer except ATRM, which fetches VBIOS ROM data by offset and size.

## Risks
The main risk is ABI drift. Structure padding, field width, or packed layout mistakes can misparse firmware buffers. Firmware may report unsupported functions, shorter structures, invalid sizes, or inconsistent masks, so callers must validate `size`, support bits, and error codes before consuming fields.

Brightness-curve structures are tied to display-manager constants through static assertions. If either side changes, this header deliberately breaks compilation rather than allowing incompatible luminance data parsing.

## Test Signals
Compile tests should cover all include sites and the static assertions. Runtime signals include ACPI method discovery on hybrid graphics systems, dGPU power switching, mux switching, external GPU enumeration, AC/DC power-source notifications, panel brightness notifications, custom brightness curve parsing, PCIe performance requests, and UMA sizing on APUs.
