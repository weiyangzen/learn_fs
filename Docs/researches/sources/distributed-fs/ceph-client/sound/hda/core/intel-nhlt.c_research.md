## sources/distributed-fs/ceph-client/sound/hda/core/intel-nhlt.c

Purpose: parses Intel ACPI NHLT tables for digital microphone geometry, endpoint presence, SSP/I2S masks, MCLK selection, endpoint format blobs, and SSP device type.

Important APIs, types, and functions: `intel_nhlt_init()`, `intel_nhlt_free()`, `intel_nhlt_get_dmic_geo()`, `intel_nhlt_has_endpoint_type()`, `intel_nhlt_ssp_endpoint_mask()`, `intel_nhlt_ssp_mclk_mask()`, `intel_nhlt_get_endpoint_blob()`, `intel_nhlt_ssp_device_type()`, plus helpers `nhlt_get_specific_cfg()` and `nhlt_check_ep_match()`.

Control flow: callers acquire the ACPI table, pass it into query helpers, then release it. Helpers linearly walk variable-length `struct nhlt_endpoint` records by advancing `epnt->length`. DMIC geometry combines array configuration with max channel count from format configs. Endpoint blob lookup filters by bus ID, link type, direction, and device type, then finds exact channel/rate/bit-depth match, with a DMIC-specific valid-bits exception for 32-bit samples.

State and persistence: no ownership is retained after `intel_nhlt_free()`. All state comes from firmware table contents and local iteration variables.

Dependencies and integration points: used by Intel DSP selection and ASoC machine/SOF setup to decide DMIC topology, SSP ports, and binary configuration blobs. Depends on ACPI NHLT structure definitions in `<acpi/nhlt.h>` and sound header constants.

Risks: most loops trust firmware-provided endpoint and config lengths, so malformed NHLT can cause bad traversal unless ACPI table validation already caught it. `intel_nhlt_ssp_mclk_mask()` requires exactly one MCLK across formats and returns `-EINVAL` otherwise. Device type lookup is strict and logs errors when firmware lacks matching SSP data.

Test signals: feed systems with no NHLT, DMIC-only, SSP/I2S, Bluetooth SSP, vendor-defined mic arrays, and mixed MCLK blobs; verify selected blobs for common rates and bit depths; fuzz or inspect firmware length fields in static analysis.
