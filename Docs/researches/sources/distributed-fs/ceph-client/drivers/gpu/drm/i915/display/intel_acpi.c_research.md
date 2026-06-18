# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_acpi.c

## Purpose

`intel_acpi.c` provides ACPI integration for the Intel display driver. It probes Intel display `_DSM` methods, logs platform mux information, evaluates a BIOS-data support DSM, assigns ACPI display device IDs to DRM connectors, associates connector firmware nodes, and registers ACPI video/backlight support when appropriate.

## Important APIs, Types, And Functions

Public functions are `intel_register_dsm_handler()`, `intel_unregister_dsm_handler()`, `intel_dsm_get_bios_data_funcs_supported()`, `intel_acpi_device_id_update()`, `intel_acpi_assign_connector_fwnodes()`, and `intel_acpi_video_register()`. Internal helpers include `intel_dsm_port_name()`, `intel_dsm_mux_type()`, `intel_dsm_platform_mux_info()`, `intel_dsm_pci_probe()`, `intel_dsm_detect()`, and `acpi_display_type()`. The file defines two Intel DSM GUIDs and ACPI `_DOD` display-device ID bitfields.

## Control Flow

DSM registration scans VGA-class PCI devices, checks for the Intel mux-info DSM, logs any mux package contents, and reports detection only when two VGA devices and an Intel DSM handle are present. The BIOS-data DSM helper obtains the i915 PCI ACPI handle and evaluates the second DSM function. Connector ACPI ID update iterates DRM connectors, maps connector type to ACPI display type, and assigns a per-type display index. Firmware-node assignment walks child fwnodes in connector order and prefers ACPI child address `0x1f` for integrated panels when available. ACPI video registration calls `acpi_video_register()` and registers ACPI video backlight only if an internal panel has native backlight functions but no backlight device.

## State And Persistence Behavior

Persistent state changes are connector-local: `connector->acpi_device_id` and `connector->fwnode` references. DSM probing itself is diagnostic and does not install a switcheroo handler in this implementation. ACPI video/backlight registration affects global ACPI video state managed outside this file. Fwnode references are acquired with `fwnode_handle_get()` and must be released by connector cleanup paths.

## Dependencies And Integration Points

The file integrates Linux ACPI, PCI device enumeration, ACPI video, DRM connector iteration, Intel connector/panel state, and display utility macros. It is called from display bring-up after connectors exist and connector order is final. The ACPI IDs follow ACPI spec `_DOD` encoding and feed firmware/user-space display identification.

## Risks And Edge Cases

DSM package parsing is defensive but only logs malformed objects. Connector fwnode assignment assumes firmware child-node order matches final connector order; calling it too early would attach wrong fwnodes. Integrated panel special handling assumes ACPI child address `0x1f` on most platforms but falls back when absent. ACPI video backlight registration must avoid racing native backlight registration on other GPUs. `intel_unregister_dsm_handler()` is intentionally empty.

## Test Signals

Useful validation includes hybrid-graphics systems with Intel mux DSM, malformed or absent DSM packages, connector ACPI ID stability across boot, internal panel fwnode assignment, external connector fwnode ordering, ACPI video backlight fallback when native device is missing, and builds with `CONFIG_ACPI` enabled and disabled via the header stubs.
