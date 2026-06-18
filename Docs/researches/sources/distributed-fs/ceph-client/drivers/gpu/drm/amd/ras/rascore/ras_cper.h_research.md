# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cper.h

Purpose: this header defines the CPER wire-format structures, GUID helpers, severity/type enums, ACA register slots, and the `ras_cper_generate_cper()` API. The structures are packed because callers write them directly into binary CPER buffers.

Important types and constants: `struct ras_cper_guid` and `CPER_GUID__INIT()` define GUID literals. `enum ras_cper_type` separates runtime, fatal, boot, and RMA records. `enum ras_cper_severity` maps CE/UE/RMA severities. Packed structs include `cper_section_hdr`, `cper_section_descriptor`, runtime headers/descriptors/register dumps, crashdump/fatal/boot sections, and `ras_cper_fatal_record`.

Control flow and persistence: no active behavior or persistence exists in the header; it defines the layout contract used by `ras_cper.c`. The section offset macros determine how binary sections are placed in the generated buffer.

Dependencies and integration: consumers must also understand ACA register ordering and log-ring events. A notable risk is that several length macros reference names such as `cper_sec_desc`, `cper_sec_crashdump_boot`, `cper_sec_crashdump_fatal`, and `cper_sec_nonstd_err`, while this header defines `cper_section_descriptor`, `cper_section_boot`, `cper_section_fatal`, and `cper_section_runtime`. If no aliases exist through other included headers, this is a compile-time break. Even with aliases, binary ABI tests are important because packed bitfields and enum widths can be compiler-sensitive. Test signals should include static size assertions, offset assertions, and compile coverage for all macros used by `ras_cper.c`.
