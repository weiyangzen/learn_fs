<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.h

Purpose: describes the serial EEPROM/NVRAM command constants and on-chip EEPROM data layout for qla4xxx legacy adapters. It is the structural map used by low-level NVRAM readers and initialization code to derive board, MAC, BIOS boot, external hardware, and subsystem information.

Important APIs/types/functions: command/format constants define FM93C56A/FM93C66A/FM93C86A sizes, READ/WRITE/WEN/WDS/ERASE opcodes, address/data bit widths, dummy/ready bits, and Auburn GPIO-style data/clock/chip-select bits. Layout structures include `struct bios_params`, `struct eeprom_port_cfg`, `struct eeprom_function_cfg`, and `struct eeprom_data`, whose union covers `isp4010` and `isp4022` EEPROM formats. Notable fields include board IDs/signatures, serial numbers, external hardware config, multiple MAC addresses, MAC/PHY config, buffer/table sizing, IP/TCP offload tables, per-function subsystem IDs, board ID string, per-port config, OEM space, and BIOS boot parameters.

Control flow: this header has no runtime flow, but `ql4_nvram.c` uses the opcode, bit-count, and GPIO bit definitions to clock EEPROM reads. `ql4_init.c` uses `offsetof(struct eeprom_data, isp4022.boardIdStr)` and external hardware config offsets/macros to set model and hardware configuration during adapter startup.

State and persistence: every structure describes persistent EEPROM content. The data includes identity, MAC addresses, boot settings, memory/table sizing, and checksum/signature words that survive driver unloads and system reboots.

Dependencies and integration: included by the qla4xxx definition stack and consumed by NVRAM, initialization, and hardware configuration code. It aligns with firmware register constants in `ql4_fw.h` and adapter predicates used to choose 4010 vs 4022/4032 layout.

Risks and test signals: packed layout correctness is critical because offsets are hardware-defined. Any field insertion or type-size change can corrupt reads of MACs, model strings, subsystem IDs, or checksum words. Bit definitions include write/erase opcodes even though this driver file reads only, so future write support would need stricter protection. Test signals include EEPROM checksum validation, model string extraction, external hardware config application, MAC address selection by function, boot parameter offsets for both ports, and builds on architectures with different alignment/endian behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nvram.h -->
