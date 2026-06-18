# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_atpx_handler.c

Purpose: implements ACPI ATPX support for hybrid Intel/ATI or integrated/discrete Radeon switchable graphics systems and registers Radeon callbacks with `vga_switcheroo`.

Important APIs/functions/types: public queries `radeon_has_atpx`, `radeon_has_atpx_dgpu_power_cntl`, `radeon_is_atpx_hybrid`, and `radeon_atpx_dgpu_req_power_for_displays` expose detected capability state. `radeon_register_atpx_handler` and `radeon_unregister_atpx_handler` manage switcheroo registration. Internal types model ATPX function masks and ACPI buffers: `radeon_atpx_functions`, `radeon_atpx`, `atpx_verify_interface`, `atpx_px_params`, `atpx_power_control`, and `atpx_mux`. Core helpers include `radeon_atpx_call`, `radeon_atpx_verify_interface`, `radeon_atpx_validate`, mux switch helpers, and `radeon_atpx_set_discrete_state`.

Control flow: registration calls `radeon_atpx_detect`, which scans PCI VGA and display-other devices, looks for an ACPI `ATPX` handle, counts GPUs, records bridge D3 support, and initializes ATPX only on two-GPU systems. Initialization verifies the ACPI interface, parses function bits, reads PX parameters when available, derives required mux/power-control behavior, and marks Microsoft hybrid graphics. `vga_switcheroo` callbacks then translate client IDs into ATPX integrated/discrete mux values, call switch-start, display mux, I2C mux, switch-end in order, or call power control for the discrete GPU.

State and persistence: all persistent state is process-lifetime kernel memory in the static `radeon_atpx_priv`: detection flag, bridge power-management usability, ACPI device handle, ATPX handle, supported function booleans, and hybrid flags. ACPI calls may change platform firmware state, display mux state, and discrete GPU power state. There is no filesystem persistence.

Dependencies and integration: depends on Linux ACPI, PCI enumeration, `vga_switcheroo`, bridge D3 metadata, and Radeon ATPX constants from `radeon_acpi.h`. The handler integrates Radeon GPUs with generic Linux switchable graphics policy and platform firmware.

Risks: ACPI method buffers are firmware-provided and only minimally size-checked before casts. Device enumeration assumes exactly two relevant display devices for ATPX registration. Power control is disabled for some hybrid systems when bridge D3 is usable, so platform-specific PM behavior can diverge. Switch and power callbacks ignore several helper return values, making partial ACPI failures hard to surface. A fixed 200 ms delay after power-off is required and may be platform-sensitive.

Test signals: hybrid laptop boot logs showing detected ATPX method and version/function bits; `vga_switcheroo` switch and power-cycle tests; suspend/resume and runtime PM tests on muxed and muxless hybrid platforms; ACPI failure-path tests for missing or short buffers; verification that display and I2C muxes follow the selected GPU.
