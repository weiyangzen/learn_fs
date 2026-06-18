# sources/distributed-fs/ceph-client/include/acpi/nhlt.h

Purpose: Declares helpers for parsing and searching ACPI NHLT audio topology tables, including endpoint and audio format iteration over variable-length payloads.

Important APIs, types, and functions: Exports pointer helpers `acpi_nhlt_endpoint_fmtscfg()`, endpoint/format iteration macros `for_each_nhlt_endpoint()`, `for_each_nhlt_fmtcfg()`, `for_each_nhlt_endpoint_fmtcfg()`, global table get/put APIs, endpoint matching/search functions, format matching functions, and `acpi_nhlt_endpoint_mic_count()`. Disabled builds return `AE_NOT_FOUND`, `NULL`, false, or zero.

Control flow: Iteration walks `endpoints_count`, using each endpoint `length`, then finds the formats block after endpoint capabilities and steps formats by each format’s config size. Search helpers match link type, device type, direction, bus id, channel count, sample rate, valid bits, and bits per sample.

State and persistence: NHLT bytes are firmware-provided table state. An optional global mapped table is reference-managed by get/put APIs to avoid repeated map/unmap overhead in sound drivers.

Dependencies and integration points: Depends on ACPI table types, overflow-safe pointer arithmetic expectations, and Intel/SOF/HDA audio drivers. Integrates with DMIC/SSP/SoundWire endpoint discovery and microphone geometry parsing.

Risks and test signals: Risks include malformed lengths causing overrun, endpoint count mismatch, OED-config skipping errors, disabled stubs hiding missing audio topology, and invalid microphone array metadata. Test with real NHLT dumps, malformed tables, endpoint/format matching unit tests, global table reference balance, and no-`CONFIG_ACPI_NHLT` builds.
