# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_acpi.c

## Purpose
This file provides ACPI enumeration for the Atom SST LPE driver on Baytrail, Baytrail-CR, Cherrytrail/Braswell, and special `LPE0F28` systems. It selects the SST DSP driver when appropriate, matches a machine driver, installs platform data/resource descriptors, creates companion platform devices, maps ACPI resources into the shared SST context, and starts common SST initialization.

## Important APIs, types, and functions
Platform descriptors include `byt_fwparse_info`, `byt_ipc_info`, `byt_lib_dnld_info`, `byt_rvp_res_info`, `bytcr_res_info`, `lpe8086_res_info`, `byt_rvp_platform_data`, and `chv_platform_data`. Resource mapping is implemented by `sst_platform_get_resources()`. Bus lifecycle is `sst_acpi_probe()` and `sst_acpi_remove()`, registered through `sst_acpi_driver` with ACPI IDs `LPE0F28`, `80860F28`, and `808622A8`.

## Control flow
Probe validates ACPI match, consults `snd_intel_acpi_dsp_driver_probe()` to avoid binding when another DSP driver is selected, finds a matching ASoC machine, chooses Baytrail or Cherrytrail platform data, handles `LPE0F28` resource quirks, parses the ACPI HID as a device ID for normal IDs, and switches Baytrail-CR to a different IRQ resource index. It registers the SST platform component device and the machine device, fills firmware name from the machine data, maps IRAM, DRAM, SHIM, mailbox, DDR, and IRQ resources, calls `sst_context_init()`, enables runtime PM, and stores the context on the platform device.

## State and persistence behavior
Resource descriptors are static, with one mutable pointer in Baytrail platform data adjusted for Baytrail-CR or `LPE0F28`. Runtime state is held in `intel_sst_drv` and platform devices. No persistent storage is written.

## Dependencies and integration points
The file integrates ACPI, platform-device registration, Intel DSP selection, SOF/SST machine-match tables, Baytrail/Cherrytrail quirks, and common SST lifecycle helpers. It passes machine data to board drivers and `sst_platform_info` to the common SST core.

## Risks and edge cases
The static `byt_rvp_platform_data.res_info` is modified based on the probed system, which is acceptable for one device but fragile if multiple variants were present. `LPE0F28` mutates a resource range in place to synthesize an LPE base range. The code registers the platform and machine devices before resource mapping and context init; failures after registration may leave cleanup to device management outside this function.

## Test signals
Test ACPI match on `80860F28`, `808622A8`, Baytrail-CR IRQ index selection, `LPE0F28` resource patching, machine-driver discovery, firmware-name propagation, all ioremap failures, IRQ lookup, runtime PM enablement, and remove cleanup.
