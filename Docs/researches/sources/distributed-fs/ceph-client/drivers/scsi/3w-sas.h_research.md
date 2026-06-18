# sources/distributed-fs/ceph-client/drivers/scsi/3w-sas.h

## Purpose

`3w-sas.h` defines the private hardware protocol, firmware command formats, ioctl ABI, and per-controller state for the LSI 3ware 9750 SAS/SATA RAID driver. It is the Liberator/SAS counterpart to `3w-9xxx.h`, with different register offsets, response encoding, SGL layout, and sense-buffer state.

## Important APIs, Types, and Definitions

Register definitions cover the Liberator status, inbound doorbell, host interrupt status/mask, outbound doorbell/clear, scratchpad, inbound queue, and outbound queue registers: `TWL_STATUS`, `TWL_HIBDB`, `TWL_HISTAT`, `TWL_HIMASK`, `TWL_HOBDB`, `TWL_HOBDBC`, `TWL_SCRPD3`, `TWL_HIBQPL/H`, and `TWL_HOBQPL/H`. Interrupt and status bits include `TWL_HISTATUS_VALID_INTERRUPT`, `TWL_HISTATUS_ATTENTION_INTERRUPT`, `TWL_HISTATUS_RESPONSE_INTERRUPT`, `TWL_STATUS_OVERRUN_SUBMIT`, `TWL_CONTROLLER_READY`, `TWL_DOORBELL_CONTROLLER_ERROR`, and `TWL_DOORBELL_ATTENTION_INTERRUPT`.

Firmware constants define `TW_OP_INIT_CONNECTION`, `TW_OP_GET_PARAM`, `TW_OP_SET_PARAM`, `TW_OP_EXECUTE_SCSI`, AEN codes, request states, 9750 compatibility values (`TW_9750_ARCH_ID`, `TW_CURRENT_DRIVER_SRL`), queue sizes, ioctl limits, parameter table IDs, and the 9750 PCI ID. Field macros include `TW_OPRES_IN()`, `TW_OPSGL_IN()`, `TW_OP_OUT()`, `TW_SGL_OUT()`, `TW_SEV_OUT()`, `TW_RESID_OUT()`, `TW_NOTMFA_OUT()`, `TW_REQ_LUN_IN()`, and `TW_LUN_OUT()`.

Wire structs are packed around `#pragma pack(1)`: `TW_SG_Entry_ISO`, `TW_Command`, `TW_Command_Apache`, `TW_Command_Apache_Header`, `TW_Command_Full`, `TW_Initconnect`, `TW_Event`, `TW_Ioctl_Driver_Command`, `TW_Ioctl_Buf_Apache`, `TW_Param_Apache`, and `TW_Compatibility_Info`. `TW_Device_Extension` stores the driver runtime state, including separate `sense_buffer_virt/phys` arrays that are unique to the SAS driver among the files in this work item.

## Control Flow Supported by the Header

The register macros implement the queue and doorbell protocol used by `3w-sas.c`: `TWL_MASK_INTERRUPTS()`, `TWL_UNMASK_INTERRUPTS()`, `TWL_CLEAR_DB_INTERRUPT()`, `TWL_SOFT_RESET()`, and address macros for high/low inbound/outbound queue writes and reads. The command-size and SGL-length macros adapt old and new command packets to 32-bit versus 64-bit `dma_addr_t` sizes: `TW_COMMAND_SIZE`, `TW_LIBERATOR_MAX_SGL_LENGTH`, `TW_LIBERATOR_MAX_SGL_LENGTH_OLD`, and padding lengths.

Response decoding differs from 9xxx: the outbound value may be an MFA or a normal response. `TW_NOTMFA_OUT()` identifies normal request-ID responses, while non-MFA responses are matched against pre-posted sense-buffer DMA addresses. LUN and request IDs are packed into 16-bit fields and converted by the C file with `cpu_to_le16()` around `TW_REQ_LUN_IN()`.

## State and Persistence Behavior

The header defines no durable storage. `TW_Device_Extension` persists only while the driver owns the PCI function. It contains command/generic/sense DMA buffers, request state, stats, AEN ring state, char-device state, compatibility info, and an `online` boolean. The AEN ring and compatibility data can be exposed through sysfs, but they are snapshots of volatile memory and are rebuilt after probe/reset from firmware events and `InitConnection` data.

## Dependencies and Integration Points

The header depends on kernel DMA, PCI, SCSI, waitqueue, mutex, and MMIO types supplied by the C file includes. Its ioctl packet layout is user-visible through the `twl` character device and must remain compatible with management tools such as smartmontools. The firmware-facing structs are sensitive to packing and architecture-dependent DMA address size.

## Risks and Edge Cases

`TW_SG_Entry_ISO` uses `dma_addr_t` for both address and length, making the SGL entry size architecture-dependent; the padding macros compensate, but any change in type assumptions can break command layout. `TW_CPU_TO_SGL()` selects `cpu_to_le64()` or `cpu_to_le32()` with a runtime `sizeof(dma_addr_t)` expression, so static analysis and endian testing are important. Several register macros take an argument `x` but reference `tw_dev` inside the macro body, which works only when the local variable is named `tw_dev`; this is fragile macro hygiene. Like the 9xxx header, `TW_PRINTK` is a raw multi-statement macro.

## Test Signals

Expected test signals include successful compilation on supported architectures, correct command and header sizes for 9750 firmware, successful reset-time sense-buffer registration, accurate request ID extraction from response and sense-buffer paths, working sysfs reads of `TW_Event` and `TW_Compatibility_Info`, and valid firmware passthrough for both old and Apache command variants.
