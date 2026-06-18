# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_mr.h

## Purpose
`qla_mr.h` defines FX00 multi-role adapter constants, IOCB wire formats, firmware discovery payloads, MMIO register offsets, register access macros, mailbox/resource limits, firmware state codes, and the `struct mr_data_fx00` per-adapter runtime state used by `qla_mr.c` and the wider `qla2xxx` driver.

It is primarily an ABI contract between driver code and FX00 firmware/hardware. The structures in this file are laid out to match firmware IOCBs and discovery responses, so field sizes, endian annotations, packing, and offsets are semantically important.

## Important APIs, Types, And Functions
Core SCSI and response IOCB formats are `struct cmd_type_7_fx00`, `struct sts_entry_fx00`, `struct multi_sts_entry_fx00`, `struct tsk_mgmt_entry_fx00`, and `struct abort_iocb_entry_fx00`. These carry command handles, target ids, LUNs, CDBs, DSDs, residuals, SCSI status, sense data, TMF flags, and abort handles.

Vendor/management IOCB formats are `struct ioctl_iocb_entry_fx00`, `struct fxdisc_entry_fx00`, `struct qla_mt_iocb_rqst_fx00`, and `struct qla_mt_iocb_rsp_fx00`. They support FXDISC requests, BSG/vendor pass-through, request/response DSDs, adapter ids, sequence numbers, status words, and dataword fields.

Firmware discovery payloads include `struct qlafx00_tgt_node_info`, `struct port_info_data`, `struct host_system_info`, `struct register_host_info`, and `struct config_info_data`. These define target WWNN/WWPN state, local port identity and link parameters, Linux host identity registration, adapter model/serial/firmware strings, cluster/capability data, and nominal temperature.

Register and interrupt constants include `QLAFX00_HBA_ICNTRL_REG`, `QLAFX00_HST_RST_REG`, `QLAFX00_SOC_TEMP_REG`, `QLAFX00_HST_TO_HBA_REG`, `QLAFX00_HBA_TO_HOST_REG`, queue BAR-window offsets, `QLAFX00_INTR_MB_CMPLT`, `QLAFX00_INTR_RSP_CMPLT`, `QLAFX00_INTR_ASYNC_CMPLT`, and the FX00 AEN values for system error, temperature, link up/down, port update, and shutdown requested.

Register access macros include `QLAFX00_SET_HST_INTR()`, `QLAFX00_CLR_HST_INTR()`, `QLAFX00_RD_INTR_REG()`, `QLAFX00_CLR_INTR_REG()`, `QLAFX00_SET_HBA_SOC_REG()`, `QLAFX00_GET_HBA_SOC_REG()`, `QLAFX00_HBA_RST_REG()`, `QLAFX00_ENABLE_ICNTRL_REG()`, `QLAFX00_DISABLE_ICNTRL_REG()`, `QLAFX00_RD_REG()`, and `QLAFX00_WR_REG()`.

`struct mr_data_fx00` is the main runtime data block embedded in `struct qla_hw_data`. It stores adapter identity strings, a generic `fcport` for unassociated requests, firmware heartbeat counters, reset and critical-temperature timers, prior AEN state, critical temperature threshold, extended-IO support, and host-info resend state.

## Control Flow
The header does not execute control flow itself, but it shapes the control flow in `qla_mr.c`.

Command submission uses `cmd_type_7_fx00`: the driver fills `entry_type = FX00_COMMAND_TYPE_7`, a firmware handle, target id, timeout, DSD count, LUN, control flags, CDB, byte count, and first DSD. Additional DSDs are emitted as `CONTINUE_A64_TYPE_FX00` continuation entries.

Firmware responses use `sts_entry_fx00`, `multi_sts_entry_fx00`, and `STATUS_CONT_TYPE_FX00`. The response parser dispatches by `entry_type`, validates handles, applies completion and SCSI status fields, copies `data[32]` sense/response bytes, and uses continuation entries when sense data exceeds the first status entry.

Discovery and management requests use `fxdisc_entry_fx00`. `qlafx00_fxdisc_iocb()` chooses request and response DSDs based on `SRB_FXDISC_*` flags, sets `func_num` to one of `FXDISC_GET_CONFIG_INFO`, `FXDISC_GET_PORT_INFO`, `FXDISC_GET_TGT_NODE_INFO`, `FXDISC_GET_TGT_NODE_LIST`, `FXDISC_REG_HOST_INFO`, or `FXDISC_ABORT_IOCTL`, and optionally passes scalar request data in `dataword`.

Reset and interrupt flows use the register macros. `qla_mr.c` writes host-to-HBA interrupt codes, clears HBA-to-host interrupt status by writing inverted masks, toggles the interrupt-control enable bit, reads SoC temperature through `QLAFX00_GET_TEMPERATURE()`, and manipulates SoC reset/fabric/timer registers during warm reset.

## State And Persistence
The header defines volatile in-kernel and hardware state only. There is no on-disk persistence.

`struct mr_data_fx00` persists while the HBA object exists. Identity fields are populated from `config_info_data`, heartbeat/timer fields are updated by the timer routine, `old_aenmbx0_state` tracks reset progress, `critical_temperature` is populated from firmware config or defaults to `QLAFX00_CRITEMP_THRSHLD`, `extended_io_enabled` reflects firmware capability bit `QLAFX00_EXTENDED_IO_EN_MASK`, and `host_info_resend`/`hinfo_resend_timer_tick` defer host registration retry.

Firmware state constants `FSTATE_FX00_CONFIG_WAIT` and `FSTATE_FX00_INITIALIZED` describe transient adapter firmware states observed through mailbox commands. Ring counts, target/lun limits, default RATOV, loop-down time, heartbeat intervals, reset intervals, critical-temperature intervals, and can-queue limits provide policy values consumed by runtime code.

## Dependencies And Integration Points
The header includes `qla_dsd.h` for `struct dsd64` and relies on definitions from the broader qla2xxx headers such as `WWN_SIZE`, `MAX_CMDSZ`, `MAX_ISA_DEVICES`, `fc_port_t`, register accessors, and bit constants.

It integrates with Linux SCSI through `struct scsi_lun` embedded in command and task-management IOCBs. It integrates with the FC transport through WWNN/WWPN fields and port/link speed values consumed by host attribute updates.

The MMIO macros assume `struct qla_hw_data` has `cregbase` mapped to FX00 control registers. The command/status structures assume request/response queue entries are `REQUEST_ENTRY_SIZE`-sized and firmware interprets little-endian fields as annotated.

## Risks And Edge Cases
Many structures represent firmware ABI and are not all marked `__packed`; changing layout, alignment, or field types can break hardware communication. The explicitly packed discovery payloads must remain byte-exact.

The `fxdisc_entry_fx00` embeds one request and one response DSD as one-element arrays even though code appends continuation entries. Bounds-checking tools may misread this pattern; driver code must keep entry-count and continuation IOCB accounting correct.

The register macros perform raw MMIO writes/reads and rely on caller locking and ordering. They do not validate offsets, state, or PCI channel health.

`QLAFX00_GET_TEMPERATURE()` performs integer arithmetic on a firmware-specific bitfield. If the register is invalid or reads all ones during PCI failure, callers must avoid trusting the resulting temperature.

`host_system_info` stores fixed-length strings copied from `utsname()`. It is safe only when callers use bounded copy as `qla_mr.c` does.

## Test Signals
Compile-time checks should cover endian annotations, packed discovery structs, and all users of FX00 IOCB types. Any change to these structures should be validated by sizeof/offset review against firmware documentation or existing hardware traces.

Runtime tests should verify command, status, multi-status, TMF, abort, IOCTL, and FXDISC IOCBs are filled with expected entry types and little-endian fields. Discovery tests should validate config/port/target payload parsing and host-info registration field truncation.

Hardware/diagnostic tests should exercise interrupt-control macros, interrupt status clear semantics, temperature conversion, heartbeat/reset interval constants, extended-IO capability detection, and critical-temperature threshold defaults.
