# sources/distributed-fs/ceph-client/drivers/firmware/efi/cper.c

Purpose: implements common UEFI CPER utilities for record IDs, severity strings, bit-string conversion, memory/PCIe/firmware/CXL/processor section printing, and generic error-status validation.

Important APIs/types/functions: exports `cper_next_record_id()`, `cper_severity_str()`, `cper_bits_to_str()`, `cper_mem_err_type_str()`, `cper_mem_err_status_str()`, `cper_mem_err_location()`, `cper_dimm_err_location()`, `cper_mem_err_pack()`, `cper_estatus_print()`, `cper_estatus_check_header()`, and `cper_estatus_check()`. Important internals are `cper_print_proc_generic()`, `cper_print_mem()`, `cper_print_pcie()`, `cper_print_fw_err()`, `cper_print_tstamp()`, and `cper_estatus_print_section()`.

Control flow: CPER consumers call `cper_estatus_check()` to validate header/raw-data offsets and section record sizes, then `cper_estatus_print()` to log severity and walk each APEI generic data section. Section dispatch is by GUID: generic processor, memory, PCIe, ARM processor, IA processor, firmware record reference, CXL protocol error, ignored CXL event records, or unknown payload hex dump. Memory sections are compacted for trace/log reuse and enriched with DMI DIMM names when possible.

State and persistence behavior: record IDs use a static atomic64 seeded from real time so ERST records stay unique across boot epochs. Otherwise the file is stateless formatting and validation code.

Dependencies and integration points: integrates ACPI APEI/GHES, DMI memory-device data, PCIe AER structures, CXL event definitions, RAS trace support, and architecture CPER processor decoders.

Risks and test signals: firmware CPER payloads are untrusted; validation gaps can lead to misleading logs or unsafe traversal. Test signals include synthetic CPER validation failures, corrected/fatal GHES log formatting, DIMM location enrichment, PCIe AER field printing, and unique ERST record IDs after reboot.
