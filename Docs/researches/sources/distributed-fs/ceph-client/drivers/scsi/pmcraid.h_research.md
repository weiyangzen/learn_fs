# sources/distributed-fs/ceph-client/drivers/scsi/pmcraid.h

## Purpose
`pmcraid.h` defines the firmware ABI, command formats, DMA structures, state containers, constants, logging tables, and ioctl ABI for `pmcraid.c`. It is not a generic exported API; it is the private contract between the MaxRAID driver implementation, SCSI midlayer data structures, and PMC IOA firmware.

## Important APIs, types, and functions
Key constants describe adapter identity, limits, command opcodes, request flags, resource types, IOASC parsing, timeouts, interrupt bits, doorbells, and reset states. Core firmware data structures include `struct pmcraid_ioadl_desc`, `pmcraid_ioarcb`, `pmcraid_ioasa`, `pmcraid_config_table_entry`, `pmcraid_config_table`, HCAM CCN/LDN layouts, and `pmcraid_control_block`. Driver-side structures include `pmcraid_cmd`, `pmcraid_interrupts`, `pmcraid_isr_param`, `pmcraid_hostrcb`, `pmcraid_instance`, and `pmcraid_resource_entry`.

The header also defines `pmcraid_ioasc_error_table`, `pmcraid_err()`, `pmcraid_info()`, `SCSI_CMD_TYPE()`, `IS_SCSI_READ_WRITE()`, `struct pmcraid_ioctl_header`, and `PMCRAID_IOCTL_RESET_ADAPTER`.

## Control flow relevance
The header is effectively the map used by the C file's state machine and I/O path. `pmcraid_cmd` binds a DMA control block, an optional SCSI command, list membership, completion, timer, callback, and scratch fields used by reset, abort, HRRQ identification, and sense handling. `pmcraid_instance` gathers all live adapter state: MMIO pointers, interrupt vectors, HRRQ buffers, command pools, resource lists, HCAM buffers, reset flags, outstanding command counters, and SCSI/PCI handles. Resource exposure and queuecommand use `pmcraid_resource_entry` to translate SCSI bus/target/lun to firmware resource handles.

## State and persistence behavior
The structures model volatile kernel and firmware state. Packed/aligned firmware structures must remain layout-compatible with the IOA. No durable storage is defined. User ABI persistence is limited to stable ioctl signature/type/number choices and the char-device naming constants.

## Dependencies and integration points
The header includes Linux completion/list/cdev and SCSI command headers plus generic netlink headers. It relies on QEMU-independent Linux kernel endian types and packed/aligned attributes. Firmware coupling is strong: bit numbering macros, response-handle toggle bits, register interrupt masks, IOASC encodings, and command opcodes are all hardware protocol definitions.

## Risks and test signals
Risks include ABI/layout drift in packed structures, endian misuse, duplicated or misspelled IOASC table entries, off-by-one limits in command/resource arrays, and macros that evaluate opcodes through GNU statement expressions. Changes should be validated with compile-time layout expectations where available, sparse/endian checks, SCSI command submission tests, ioctl ABI compatibility, and reset/interrupt tests that prove state constants still match `pmcraid.c`.
