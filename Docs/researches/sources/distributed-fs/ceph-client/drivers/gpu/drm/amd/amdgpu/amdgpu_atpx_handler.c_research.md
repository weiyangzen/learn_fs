# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atpx_handler.c

## Purpose
`amdgpu_atpx_handler.c` implements ACPI ATPX support for hybrid graphics and legacy switchable GPU platforms. It detects systems with AMD ATPX firmware methods, validates supported power/mux functions, applies platform quirks, and registers callbacks with `vga_switcheroo` for GPU switching and dGPU power control.

## Important APIs, types, and functions
The external APIs are `amdgpu_register_atpx_handler()`, `amdgpu_unregister_atpx_handler()`, `amdgpu_has_atpx()`, `amdgpu_has_atpx_dgpu_power_cntl()`, and `amdgpu_is_atpx_hybrid()`. Important internal state is `static struct amdgpu_atpx_priv amdgpu_atpx_priv`, containing detection flags, bridge PM usability, quirks, ACPI handles, and `struct amdgpu_atpx`. ACPI method wrappers include `amdgpu_atpx_call()`, `amdgpu_atpx_verify_interface()`, `amdgpu_atpx_validate()`, `amdgpu_atpx_set_discrete_state()`, display/I2C mux switching, and switch start/end notifications.

## Control flow
Registration calls `amdgpu_atpx_detect()`, which scans VGA and display-class PCI devices, finds an `ATPX` ACPI handle, counts display devices, records bridge D3 capability, and applies PCI subsystem quirks. When exactly two display devices and ATPX are present, it logs the ACPI path, sets global detection state, initializes ATPX, and registers a `vga_switcheroo_handler`.

Initialization verifies the ATPX interface by executing `ATPX_FUNCTION_VERIFY_INTERFACE`, checking the returned buffer size, and decoding supported function bits. Validation optionally calls `GET_PX_PARAMETERS`, interprets valid flags, promotes implied mux/power-control support, handles Microsoft Hybrid Graphics by preferring bridge PM when usable unless a quirk forces ATPX, and records whether displays require dGPU power. Runtime switch callbacks translate the requested `vga_switcheroo_client_id` into ATPX integrated/discrete IDs and call switch-start, display-mux, I2C-mux, and switch-end methods. Power callbacks ignore IGD power and call ATPX power control for the dGPU.

## State and persistence behavior
State is process-global kernel memory in `amdgpu_atpx_priv`: detected method, selected ACPI handles, function support, hybrid flag, bridge PM flag, quirks, and display-power requirement. ACPI calls may change platform firmware state, mux routing, or dGPU power state. There is no file-backed persistence.

## Dependencies and integration points
The file depends on ACPI object evaluation, PCI device enumeration, bridge D3 capabilities, `vga_switcheroo`, AMD ACPI ATPX constants from `amd_acpi.h`, and AMDGPU PCI IDs for quirks. It integrates early in AMDGPU module/device setup through register/unregister calls and provides global query helpers used by power-management and hybrid-graphics decisions.

## Risks and edge cases
ACPI firmware buffer parsing trusts the first `u16` size after ensuring a small minimum, so malformed buffers remain a risk. Device enumeration relies on exactly two display devices to enable ATPX; unusual hybrid systems may be missed. Global state means multiple GPUs share one ATPX handler. Hybrid systems with broken `_PR3` bridge power need quirks to force ATPX power control. ACPI calls return allocated buffers that must always be freed. The switch callback currently returns success even if one of the intermediate ATPX method calls fails.

## Test signals
Signals include boot on known ATPX and non-ATPX laptops, Microsoft Hybrid Graphics systems with and without bridge D3, quirked Dell/Acer/Lenovo devices, `vga_switcheroo` switch and power operations, ACPI failure injection for each ATPX method, suspend/resume dGPU power behavior, and absence of handler registration on systems without exactly two display devices.
