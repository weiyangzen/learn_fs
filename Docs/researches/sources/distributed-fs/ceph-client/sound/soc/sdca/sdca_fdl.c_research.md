# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_fdl.c

## Purpose
Implements SDCA File Download host-side support. It resets functions, waits for firmware download activity, locates firmware files from ACPI SWFT or disk, transfers files through UMP buffers, and drives the FDL status/response state machine.

## APIs, Types, and Functions
Exports `sdca_reset_function()`, `sdca_fdl_sync()`, `sdca_fdl_process()`, and `sdca_fdl_alloc_state()`. Internal helpers include `fdl_get_sku_filename()`, `fdl_load_file()`, `fdl_get_set()`, `fdl_end()`, `sdca_fdl_timeout_work()`, and `fdl_status_process()`. Per-interrupt FDL state is stored in `struct fdl_state` via `interrupt->priv`.

## Control Flow, State, and Persistence
`sdca_reset_function()` writes Entity 0 function action reset and polls until the action clears, allowing unimplemented reset writes. `sdca_fdl_sync()` waits for FDL begin/done completions on matching XU owner interrupts, retrying to infer that firmware setup is complete when no new begin arrives. On an owner interrupt, `sdca_fdl_process()` verifies host UMP ownership, cancels timeout work, reads FDL status, delegates response selection and file loading, writes the response back with preserved device bits, returns UMP ownership to the device, and optionally schedules a timeout or resets the function. Firmware is chosen from SWFT unless a newer or matching disk SWF is found under SKU-specific or generic `sdca/<vendor>/<file>.bin` paths.

## Dependencies and Integration
Depends on firmware loader, ACPI SWFT structures, DMI/PCI identifiers, runtime PM, regmap, SDCA UMP helpers, SDCA interrupt metadata, and parsed file-set data from `sdca_functions.c`. It is invoked by early and normal SDCA IRQ handlers and by class-function boot/resume synchronization.

## Risks and Test Signals
Risks include heuristic completion detection due to no explicit spec completion signal, firmware path/version selection mistakes, not releasing firmware on every error path after successful request, UMP buffer size/ownership failures, timeout/reset races with IRQ handling, and unsupported reset mechanisms falling back to function reset. Test signals are FDL with SWFT-only firmware, disk override by newer SWF, missing firmware error paths, multi-file sets, request reset/abort handling, timeout work triggering reset, and resume-time FDL when runtime PM cannot be waited on normally.
