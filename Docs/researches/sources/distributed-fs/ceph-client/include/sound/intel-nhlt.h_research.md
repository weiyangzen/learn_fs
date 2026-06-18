# sources/distributed-fs/ceph-client/include/sound/intel-nhlt.h

Source read summary: 199 lines, Intel NHLT ACPI audio table parser declarations.

Purpose: declares structures and helpers for discovering audio endpoints, formats, DMIC geometry, SSP link masks, and SoundWire link masks from Intel NHLT ACPI tables.

Important APIs, types, and functions: forward-facing helpers include `intel_nhlt_init()`, `intel_nhlt_free()`, `intel_nhlt_get_dmic_geo()`, `intel_nhlt_ssp_endpoint_mask()`, `intel_nhlt_ssp_mclk_mask()`, `intel_nhlt_ssp_link_mask()`, `intel_nhlt_has_endpoint_type()`, and `intel_nhlt_get_sdw_endpoint_mask()`, with disabled stubs returning neutral values. The header defines NHLT endpoint/link constants, vendor MIC array identifiers, and packed table descriptors such as endpoint descriptors, wave format/extensible format, format config, specific config, device-specific config, and vendor DMIC array config variants.

Control flow: Intel DSP/HDA/SOF probe loads the ACPI NHLT table, walks endpoint descriptors, filters by link/device type, extracts format/config blobs, derives DMIC count/geometry and SSP/SoundWire masks, then frees the table handle.

State and persistence behavior: state is a parsed table handle (`struct nhlt_acpi_table *`) owned by caller during probe. The ACPI firmware table is platform-provided and persistent firmware data, but parser state is temporary.

Dependencies and integration points: depends on ACPI table access, device logging, Intel DSP/SOF machine selection, DMIC topology, SSP/I2S links, and SoundWire link discovery.

Risks and edge cases: packed ACPI structures require exact layout, firmware may advertise malformed endpoint lengths, vendor DMIC geometry may not match topology files, and stubs can hide missing NHLT support.

Test signals: parse valid and malformed NHLT tables, DMIC 2/4-array detection, SSP endpoint/mclk/link masks, SoundWire endpoint masks, missing-table fallback, and compile with ACPI/NHLT disabled.
