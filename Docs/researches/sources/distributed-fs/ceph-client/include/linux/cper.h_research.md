<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cper.h -->
# sources/distributed-fs/ceph-client/include/linux/cper.h

## Purpose

`cper.h` defines Linux's in-kernel representation of UEFI Common Platform Error Record data. It is the ABI-facing contract for firmware-first hardware error records, including record headers, section descriptors, processor, memory, PCIe, firmware-reference, ARM, IA, CXL, and DMAR section identifiers. The source was read as a complete 615-line file.

## Important APIs, Types, and Functions

Key constants include `CPER_SIG_RECORD`, `CPER_RECORD_REV`, `CPER_REC_LEN`, severity values, validation masks, record/section flag masks, notification GUIDs, section GUIDs, and memory extension bit helpers. Packed structs include `cper_record_header`, `cper_section_descriptor`, `cper_sec_proc_generic`, `cper_sec_proc_ia`, `cper_ia_err_info`, `cper_ia_proc_ctx`, `cper_sec_proc_arm`, `cper_arm_err_info`, `cper_arm_ctx_info`, `cper_sec_mem_err_old`, `cper_sec_mem_err`, `cper_mem_err_compact`, `cper_sec_pcie`, and `cper_sec_fw_err_rec_ref`. Public helpers include `cper_next_record_id()`, severity and memory error string helpers, `cper_print_bits()`, `cper_bits_to_str()`, memory pack/unpack/location helpers, processor printers, `cper_estatus_print()`, `cper_estatus_check_header()`, `cper_estatus_check()`, and `cxl_cper_print_prot_err()`.

## Control Flow

This header is mostly layout and parser/printer declaration. Firmware or ACPI paths receive error status records, validate the record and section headers, identify section types by GUID, and dispatch to CPER printers or packers. `cper_get_mem_extension()` is the only inline data path; it derives extended row bits when the memory error valid mask indicates an extended row field.

## State and Persistence Behavior

The file does not own storage, but the packed structs mirror persistent firmware-provided error records and must remain byte-exact. `cper_mem_err_compact` is a kernel trace-friendly compact representation used after extracting a full memory section.

## Dependencies and Integration Points

It depends on `linux/uuid.h` and `linux/trace_seq.h`, and integrates with ACPI HEST/GHES, RAS reporting, EDAC-like memory-error handling, tracepoints, CXL CPER protocol error printing, and userspace-facing error summaries.

## Risks and Edge Cases

The main risk is ABI drift: packing, field order, GUID values, validation masks, and endian-sized integer fields must match UEFI/CXL specifications. Callers must honor validation bits before interpreting optional fields. Memory extension helpers only make sense with the matching `CPER_MEM_VALID_ROW_EXT` bit. Record length and section offsets need strict bounds checking by implementations to avoid malformed firmware input.

## Test Signals

Useful signals include build coverage for ACPI/GHES/RAS/CXL paths, fixture-based parsing of valid and malformed CPER blobs, exact struct size/offset checks when specs change, validation-bit tests for optional memory and PCIe fields, trace formatting tests for compact memory errors, and injected firmware-first error records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cper.h -->
