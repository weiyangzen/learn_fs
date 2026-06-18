# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_hwi.h

## Purpose

`pm80xx_hwi.h` is the PM80xx/SPCv firmware-interface contract used by `pm80xx_hwi.c` and the common PM8001 driver code. It defines inbound and outbound MPI opcodes, packed IOMB request/response layouts, hardware event/status code values, controller configuration-table offsets, queue-table offsets, scratchpad/reset/MMIO register offsets, encryption/thermal/SAS timer constants, and timeout values.

## Important APIs, Types, and Functions

There are no functions in this header. The important API surface is the collection of constants and packed structures that must match firmware ABI. Opcode defines cover inbound requests such as `OPC_INB_PHYSTART`, `OPC_INB_SSPINIIOSTART`, `OPC_INB_SMP_REQUEST`, `OPC_INB_SATA_HOST_OPSTART`, `OPC_INB_LOCAL_PHY_CONTROL`, `OPC_INB_SET_CONTROLLER_CONFIG`, `OPC_INB_REG_DEV`, encryption opcodes, KEK/DEK management, and outbound completions/events such as `OPC_OUB_SSP_COMP`, `OPC_OUB_SMP_COMP`, `OPC_OUB_SATA_COMP`, `OPC_OUB_HW_EVENT`, `OPC_OUB_DEV_REGIST`, and SPCv-specific response opcodes.

Core IOMB structures include `struct mpi_msg_hdr`, `phy_start_req`, `phy_stop_req`, `sata_completion_resp`, `hw_event_resp`, `thermal_hw_event`, `reg_dev_req`, `dereg_dev_req`, `dev_reg_resp`, `local_phy_ctl_req`, `hw_event_ack_req`, `phy_start_resp`, `phy_stop_resp`, `ssp_completion_resp`, `sata_event_resp`, `ssp_event_resp`, `smp_req`, `smp_completion_resp`, `task_abort_req`, diagnostic request/response structs, `set_dev_state_req`, `sata_start_req`, `ssp_ini_tm_start_req`, `ssp_info_unit`, `ssp_ini_io_start_req`, `ssp_dif_enc_io_req`, flash/NVM structs, controller config structs, `kek_mgmt_req`, `dek_mgmt_req`, PHY profile structs, `SASProtocolTimerConfig_t`, and SPCv response structs.

The header also defines bitfield `struct sas_identify_frame_local` separately for little- and big-endian bitfield order, data-plane response status values (`IO_SUCCESS`, `IO_UNDERFLOW`, `IO_OPEN_CNX_ERROR_*`, `IO_XFER_*`, encryption/DIF errors), hardware event values (`HW_EVENT_SAS_PHY_UP`, `HW_EVENT_PHY_DOWN`, `HW_EVENT_BROADCAST_CHANGE`, reset/recovery events), port states, and register/table offsets such as `MSGU_IBDB_SET`, `MSGU_ODMR`, `MSGU_SCRATCH_PAD_*`, `MAIN_*`, `GST_*`, `PSPA_*`, `IB_*`, `OB_*`, `SPC_REG_SOFT_RESET`, and `MEMBASE_II_SHIFT_REGISTER`.

## Control Flow

This file has no runtime control flow, but it determines the control flow in `pm80xx_hwi.c`: opcodes select cases in `process_one_iomb()`, hardware event constants select cases in `mpi_hw_event()`, status constants select cases in SSP/SMP/SATA completion handlers, and table/register offsets determine how initialization, reset, interrupts, and dump capture read or write hardware state. The struct layouts also dictate what payload fields request builders populate before calling `pm8001_mpi_build_cmd()` and what fields completion handlers decode after firmware writes an outbound IOMB.

## State and Persistence Behavior

The header itself stores no runtime state. It defines the binary representation of transient IOMBs exchanged through DMA queues and the layout of firmware-persistent or firmware-owned MMIO tables. Some constants control persistent or semi-persistent controller behavior when used by implementation code, such as PHY profiles, encryption key management, event-log buffers, thermal thresholds, SAS protocol timers, fatal dump tables, and NVM/flash partition operations.

All structures are packed and 4-byte aligned where the firmware ABI expects dword IOMB layout. Fields are mostly `__le32`/`__le64`, so callers must convert CPU endian values before queueing requests and convert firmware values after reading completions.

## Dependencies and Integration Points

The header depends on `<linux/types.h>` and `<scsi/libsas.h>` for fixed-width types, endian annotations, SAS address sizes, and SAS frame/FIS types. It is included by `pm80xx_hwi.c` and may be consumed by common PM8001 helper code that handles shared responses. It forms the local mirror of firmware documentation, so changes must remain synchronized with controller firmware for all chip generations that share `pm8001_80xx_dispatch`.

## Risks and Edge Cases

The main risk is ABI drift or layout mismatch. A wrong opcode, field offset, alignment, endian annotation, or structure size can cause firmware to interpret host requests incorrectly or the driver to mis-handle completions. The header contains very large status enumerations with sparse and overlapping-looking values; adding new statuses without updating completion switch logic can lead to generic failures. One define appears malformed, `IO_XFR_ERROR_DEK_INDEX_OUT_OF_BOUNDS0x2046`, which lacks the normal separation between name and value and is a candidate audit target if this code is built with encryption error paths enabled.

The duplicate definitions for `MBIC_AAP1_ADDR_BASE`, `MBIC_IOP_ADDR_BASE`, and `GSM_ADDR_BASE` should be kept consistent if modified. Bitfield `sas_identify_frame_local` depends on kernel bitfield-order macros; unsupported architectures fail compilation intentionally. Queue/table offsets are byte offsets even where comments mention dwords, so callers must not accidentally multiply them.

## Test Signals

Useful validation includes compiling this driver on little- and big-endian configurations, checking `sizeof()` and field offsets for every firmware IOMB struct against the controller specification, exercising every outbound opcode handled by `process_one_iomb()`, injecting representative status/event values, verifying endian conversions with sparse or smatch, and building with encryption/DIF-related code paths enabled. Runtime tests should correlate MMIO table offsets and queue descriptors programmed by `pm80xx_hwi.c` with firmware-reported values.
