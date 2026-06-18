<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/constants.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/constants.c

Purpose: this file provides shared SCSI debug/stringification helpers: opcode names, service-action names, sense-key text, additional sense code text, host-byte result names, and SCSI midlayer return-code names.

Important APIs, types, and functions: the key exported functions are `scsi_sense_key_string()`, `scsi_extd_sense_format()`, `scsi_hostbyte_string()`, and `scsi_mlreturn_string()`. `scsi_opcode_sa_name()` is a non-exported helper that maps an opcode and service action to CDB and service-action strings. Tables include `cdb_byte0_names`, service-action `value_name_pair` arrays, `sa_names_arr`, `additional[]`, generated `additional_text` from `sense_codes.h`, fallback ranged `additional2[]`, `snstext`, `hostbyte_table`, and `scsi_mlreturn_arr`.

Control flow: opcode/service-action lookup first rejects vendor-specific opcodes, optionally names opcode byte 0, finds a matching service-action table, then scans it for the action value. Sense-key lookup is a direct bounds-checked table read. Additional sense lookup builds a 16-bit ASC/ASCQ key, scans compact `additional[]` entries while accumulating offsets into the concatenated `additional_text` string table, then checks ranged fallback cases such as diagnostic failures and tagged overlapped commands. Host-byte lookup uses `host_byte(result)` to index `hostbyte_table`. Midlayer return lookup scans the named result array.

State and persistence behavior: all state is static read-only table data built into the kernel object. There is no mutation, allocation, locking, or persistence beyond the module/kernel image.

Dependencies and integration points: it includes SCSI core headers and is used by diagnostics across SCSI drivers and error handling. It relies on `sense_codes.h` to generate compact ASC/ASCQ metadata and text. Exported symbols are available to other kernel modules.

Risks: table drift versus current SPC/SBC/MMC standards is the main correctness risk. `scsi_extd_sense_format()` is O(number of sense codes), which is fine for diagnostics but not ideal for hot paths. Some opcode names are combined or overloaded, so users should treat them as diagnostic labels, not as authoritative parsers.

Test signals: unit-style tests can verify known sense key, ASC/ASCQ, host byte, and midlayer return mappings; unknown values should return `NULL`; ranged `additional2[]` entries should set `fmt`; generated `sense_codes.h` offsets should remain aligned after updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/constants.c -->
