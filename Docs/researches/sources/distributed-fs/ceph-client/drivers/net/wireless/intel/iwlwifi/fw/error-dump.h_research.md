<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/error-dump.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/error-dump.h

Purpose: binary dump format contract for legacy and INI iwlwifi firmware dumps.

Important APIs/types: defines dump barkers, `enum iwl_fw_error_dump_type`, generic TLV headers (`iwl_fw_error_dump_file`, `iwl_fw_error_dump_data`, `iwl_fw_ini_error_dump_data`), payload structs for FIFOs, PRPH, memory, monitor buffers, SMEM config, paging, receive buffers, trigger descriptors, and INI region headers/ranges/info records. `iwl_fw_error_next_data()` advances through legacy dump TLVs.

Control flow: this header has little executable logic, but its flexible-array layouts drive size calculations and pointer walking in `dbg.c`. INI structures encode region ids, names, range counts, FIFO/register metadata, firmware packet headers, and dump metadata such as timepoint, region mask, firmware/build tags, and external config state.

State and persistence: structures are persisted as devcoredump bytes and consumed by external parsers. Endianness is explicitly little-endian for wire/dump stability.

Dependencies/integration: depends on command header definitions and constants from firmware debug TLVs. It is included by `img.h` and `dbg.h`, making it shared across dump producers and firmware metadata code.

Risks/test signals: any layout, enum, barker, or alignment change can break parser compatibility. Test with dump parsers for legacy and INI files, flexible-array length accounting, endian conversion, max LMAC/FIFO constants, and trigger id compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/error-dump.h -->
