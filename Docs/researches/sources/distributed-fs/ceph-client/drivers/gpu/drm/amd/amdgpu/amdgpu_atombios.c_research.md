# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.c

## Purpose
`amdgpu_atombios.c` is the legacy ATOMBIOS parser and interpreter integration layer for AMDGPU. It converts VBIOS data tables into driver-visible display, clock, voltage, memory, scratch-register, and sysfs state, and provides register callbacks used by the ATOM bytecode interpreter.

## Important APIs, types, and functions
External entry points include `amdgpu_atombios_init()`, `amdgpu_atombios_fini()`, `amdgpu_atombios_sysfs_init()`, `amdgpu_atombios_i2c_init()`, `amdgpu_atombios_oem_i2c_init()`, `amdgpu_atombios_lookup_i2c_gpio()`, `amdgpu_atombios_lookup_gpio()`, `amdgpu_atombios_get_connector_info_from_object_table()`, `amdgpu_atombios_get_clock_info()`, `amdgpu_atombios_get_gfx_info()`, `amdgpu_atombios_get_vram_width()`, `amdgpu_atombios_get_asic_ss_info()`, `amdgpu_atombios_get_clock_dividers()`, `amdgpu_atombios_get_data_table()`, and scratch helpers. SI-only helpers under `CONFIG_DRM_AMDGPU_SI` expose memory PLL, voltage, SVI2, and memory-controller register-table parsing. Important internal unions mirror firmware table revisions: `firmware_info`, `igp_info`, `asic_ss_info`, `get_clock_dividers`, `voltage_object_info`, and `vram_info`.

## Control flow
Initialization allocates `struct card_info`, installs MMIO and placeholder PLL/MC callbacks, parses the already-fetched VBIOS with `amdgpu_atom_parse()`, initializes the ATOM mutex, and then branches between newer atomfirmware helpers and legacy scratch/FB-scratch allocation depending on `adev->is_atom_fw`. Display discovery parses the object header, display path, connector, encoder, and router tables. It maps ATOM connector object IDs to DRM connector types, creates encoders, decodes router DDC/clock routing records, looks up DDC and HPD GPIOs, adds connectors, and finally links encoders to connectors.

Clock and capability discovery reads the legacy `FirmwareInfo` table to seed PPLL/SPLL/MPLL ranges, default SCLK/MCLK/DISPCLK, DP external clock, max pixel clock, firmware flags, and current PM clocks. `amdgpu_atombios_get_clock_dividers()` executes the `ComputeMemoryEnginePLL` command table using the revision-specific parameter layout and decodes returned PLL divisors. Spread-spectrum and IGP override helpers parse ASIC/internal system info tables. SI-specific paths execute ATOM command tables for memory PLL, dynamic memory settings, and voltage, and parse voltage object and VRAM timing tables.

Scratch handling writes BIOS scratch registers to hand display switching and DPMS semantics to the driver, expose engine-hung and backlight state, and test whether ASIC init is required. Sysfs setup publishes read-only `vbios_version` and conditionally `vbios_build`. Finalization frees ATOM scratch, indirect I/O storage, context, and card-info structures.

## State and persistence behavior
The file populates runtime fields in `adev->mode_info`, `adev->clock`, `adev->pm`, `adev->gfx.config`, `adev->gfx.cu_info`, `adev->bios_scratch_reg_offset`, display connector/encoder lists, and sysfs device attributes. ATOM context scratch memory is heap-allocated and freed during shutdown. Persistent input is only the VBIOS image already stored in memory; no output is persisted beyond hardware registers and driver structures.

## Dependencies and integration points
It depends on `atom.c` parser/executor APIs, legacy ATOM table definitions, AMDGPU display helpers, AMDGPU I2C helpers, DRM connector types, MMIO access macros, SI configuration, and the newer `amdgpu_atomfirmware` helpers for atomfirmware devices. It is reached after BIOS acquisition in `amdgpu_bios.c` and before display, clock, power, and memory-management subsystems consume parsed VBIOS data.

## Risks and edge cases
Table parsing is pointer arithmetic over firmware-controlled binary layouts. Bad sizes, unsupported revisions, connector object IDs beyond the conversion table, malformed record chains, or bogus offsets can break discovery. Several MC/PLL callbacks are stubs returning zero, so command tables that require those spaces would not work through this integration. Clock default fallbacks and unit conversions differ by table revision. FB scratch allocation and SR-IOV VRAM reservations must match TTM expectations. Big-endian `copy_swap()` only supports small stack arrays sized for current ATOM parameter blocks.

## Test signals
Test signals include boot on legacy pre-Vega ASICs with diverse connector object tables, HPD/DDC/router combinations, sysfs `vbios_version` and `vbios_build`, display hotplug, PLL divider command execution for supported ATOM revisions, spread-spectrum lookup, SI voltage and memory timing parsing, SR-IOV VRAM reservation tables, malformed VBIOS table rejection, and clean init/fini under probe failure.
