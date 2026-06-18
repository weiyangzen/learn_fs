# sources/distributed-fs/ceph-client/drivers/scsi/3w-9xxx.h

## Purpose

`3w-9xxx.h` is the private protocol and state definition header for the 3ware 9000-family driver. It defines the command packet wire layouts, register bits, PCI IDs, firmware opcodes, AEN/error text tables, ioctl ABI structures, queue-state constants, SGL sizing rules, and `TW_Device_Extension` state used by `3w-9xxx.c`.

## Important APIs, Types, and Definitions

The AEN and error translation surfaces are `twa_message_type`, `twa_aen_table`, `twa_aen_severity_table`, and `twa_error_table`. Register definitions include control bits such as `TW_CONTROL_CLEAR_ATTENTION_INTERRUPT`, `TW_CONTROL_DISABLE_INTERRUPTS`, and `TW_CONTROL_ISSUE_SOFT_RESET`, plus status bits such as `TW_STATUS_RESPONSE_INTERRUPT`, `TW_STATUS_COMMAND_QUEUE_FULL`, `TW_STATUS_MICROCONTROLLER_READY`, and masks for expected/unexpected interrupt state.

Firmware opcodes and protocol constants include `TW_OP_INIT_CONNECTION`, `TW_OP_GET_PARAM`, `TW_OP_SET_PARAM`, `TW_OP_EXECUTE_SCSI`, `TW_OP_DOWNLOAD_FIRMWARE`, and `TW_OP_RESET`. Compatibility constants such as `TW_9000_ARCH_ID`, `TW_CURRENT_DRIVER_SRL`, `TW_BASE_FW_SRL`, and `TW_FW_SRL_LUNS_SUPPORTED` drive reset-time SRL negotiation. The header also defines request states `TW_S_INITIAL`, `TW_S_STARTED`, `TW_S_POSTED`, `TW_S_PENDING`, `TW_S_COMPLETED`, and `TW_S_FINISHED`.

Command wire types are `TW_SG_Entry`, `TW_Command` for older command packets, `TW_Command_Apache` for 9000+ execute-SCSI packets, `TW_Command_Apache_Header` for sense/error metadata, `TW_Command_Full` as a header-plus-union wrapper, and `TW_Initconnect` for controller connection negotiation. Management ABI types are `TW_Event`, `TW_Ioctl_Driver_Command`, `TW_Ioctl_Buf_Apache`, `TW_Lock`, `TW_Param_Apache`, `TW_Response_Queue`, and `TW_Compatibility_Info`. `TW_Device_Extension` is the main in-memory adapter object.

## Control Flow Supported by the Header

The macros encode all controller register access patterns used by the C file: `TW_CONTROL_REG_ADDR()`, `TW_STATUS_REG_ADDR()`, command/response queue address macros for normal and large queues, `TW_CLEAR_*`, `TW_DISABLE_INTERRUPTS()`, `TW_ENABLE_AND_CLEAR_INTERRUPTS()`, `TW_MASK_COMMAND_INTERRUPT()`, `TW_UNMASK_COMMAND_INTERRUPT()`, and `TW_SOFT_RESET()`. Packet-field macros pack and unpack firmware bitfields without C bitfields: `TW_OPRES_IN()`, `TW_OPSGL_IN()`, `TW_OP_OUT()`, `TW_SGL_OUT()`, `TW_SEV_OUT()`, `TW_RESID_OUT()`, `TW_REQ_LUN_IN()`, and `TW_LUN_OUT()`.

DMA width controls are centralized through `twa_addr_t` and `TW_CPU_TO_SGL()`, switching between little-endian 64-bit and 32-bit SGL addresses based on `CONFIG_ARCH_DMA_ADDR_T_64BIT`. `TW_COMMAND_SIZE`, `TW_APACHE_MAX_SGL_LENGTH`, `TW_ESCALADE_MAX_SGL_LENGTH`, and `TW_PADDING_LENGTH` adapt packet layout to DMA address size.

## State and Persistence Behavior

`TW_Device_Extension` contains only runtime state. It stores the MMIO base, coherent buffers and DMA addresses for command packets and per-request generic data, request-to-SCSI-command mappings, free and pending queues, request states, posted and pending counters, SGL/sector/reset/AEN counters, host and PCI pointers, bit flags for reset/MSI/attention-loop state, a circular `TW_Event` queue with wrap/clobber indicators, char-device lock and waitqueue state, and cached compatibility information. None of these structures are persistent across unload or reboot; persistent controller facts are retrieved from firmware parameter tables.

## Dependencies and Integration Points

The header assumes kernel types such as `__le16`, `__le32`, `__le64`, `dma_addr_t`, `struct pci_dev`, `struct scsi_cmnd`, `struct Scsi_Host`, `wait_queue_head_t`, `struct mutex`, and `ktime_t`. It is tightly coupled to Linux SCSI, PCI, DMA, MMIO, and uaccess code in `3w-9xxx.c`. The ioctl structures form a user-visible ABI for 3ware management tools, so field order, packing, flexible array placement, and command padding are compatibility-sensitive.

## Risks and Edge Cases

The header contains static lookup tables in a header rather than `extern` declarations; that is acceptable because it is included by one C file, but including it elsewhere would create duplicated table definitions. Several wire structures are `__packed` or manually padded; changes can silently break firmware ABI, especially around 32-bit versus 64-bit DMA address sizes. The AEN event timestamp is 32-bit seconds and the C file notes a year-2106 overflow. `TW_PRINTK` is a multi-statement macro without `do { } while (0)`, so use in unusual conditional contexts would be fragile. Ioctl constants and error codes are part of the management ABI and should not be renumbered.

## Test Signals

Header-level validation comes from successful compilation on 32-bit and 64-bit DMA configurations, correct `sizeof()` and alignment of command packet structures, working firmware passthrough for old and Apache packets, correct LUN/request ID packing, successful AEN text decoding, and probe-time SRL compatibility output matching firmware values. Regression tests should include sparse/endian checks because the 9000 header deliberately uses little-endian fields in firmware-facing structures.
