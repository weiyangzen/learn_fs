# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_hw.h

## Purpose

`t4_hw.h` is a compact hardware-constant contract for the Chelsio T4-family Ethernet driver. It centralizes adapter-wide dimensions, queue and mailbox sizes, SGE response descriptor layouts, flash partition offsets, PCIe memory window identifiers, and optical-module EEPROM/SFP diagnostic constants. The file does not implement behavior; it gives `cxgb4` C code stable symbolic names for hardware limits and wire/register bit encodings.

## Important APIs, Types, and Constants

- Global dimensions include `NCHAN`, `MAX_MTU`, `EEPROMSIZE`, `EEPROMVSIZE`, `EEPROMPFSIZE`, `RSS_NENTRIES`, `T6_RSS_NENTRIES`, `TCB_SIZE`, `NMTUS`, `NCCTRL_WIN`, `NTX_SCHED`, `PM_NSTATS`, `T6_PM_NSTATS`, `MBOX_LEN`, `TRACE_LEN`, and `FILTER_OPT_LEN`.
- Debug/logic-analyzer sizes include `CIM_NUM_IBQ`, `CIM_NUM_OBQ`, `CIM_NUM_OBQ_T5`, `CIMLA_SIZE`, `CIM_PIFLA_SIZE`, `CIM_MALA_SIZE`, `CIM_IBQ_SIZE`, `CIM_OBQ_SIZE`, `TPLA_SIZE`, and `ULPRX_LA_SIZE`.
- `enum ctxt_type` defines SGE context categories: `CTXT_EGRESS`, `CTXT_INGRESS`, `CTXT_FLM`, and `CTXT_CNM`.
- SGE constants describe work request size, context size, interrupt timer/counter counts, doorbell queue timer count, ingress queue max size, queue index granularity, interrupt destinations, ingress update delivery modes, host flow-control modes, fetch burst encodings, flush thresholds, and ingress padding shifts.
- `enum pcie_memwin` names PCIe BAR memory windows for NIC, RDMA, FCoE/iSCSI, and CSIO storage access.
- `struct sge_qstat` is a big-endian queue status entry containing `qid`, `cidx`, and `pidx`.
- `struct rsp_ctrl` describes the last 128 bits of an SGE response descriptor and exposes header-buffer length, payload-buffer length, QID, response type, generation bit, and final flit.
- Bit helpers include `RSPD_NEWBUF_*`, `RSPD_LEN_*`, `RSPD_QID_*`, `RSPD_TYPE_*`, `QINTR_CNT_EN_*`, `QINTR_TIMER_IDX_*`, and `SGE_TIMESTAMP_*`.
- Flash layout macros compute byte offsets and maximum sizes from sector numbers. Named sections cover expansion ROM, iBFT/driver parameters, boot configuration, firmware image, firmware bootstrap, iSCSI and FCoE crash/persistent areas, firmware configuration, FPGA configuration, minimum supported flash size, and failover-reserved sectors.
- Optical EEPROM/SFP constants include I2C device addresses `I2C_DEV_ADDR_A0` and `I2C_DEV_ADDR_A2`, `I2C_PAGE_SIZE`, SFP diagnostic type and SFF revision fields, and feature bits such as `SFP_DIAG_ADDRMODE` and `SFP_DIAG_IMPLEMENTED`.

## Control Flow and State Behavior

This header has no executable control flow. Its constants drive control flow elsewhere by bounding loops over channels, queues, timers, RSS tables, MTU tables, flash sectors, CIM buffers, and SGE contexts. The response descriptor helpers define how RX completion handlers interpret descriptor state, especially buffer ownership, response type, queue identity, and generation rollover. Flash layout constants determine persistent address ranges used by firmware-update, configuration, and crash-log routines.

Persistent state represented by this file is external hardware or nonvolatile media state. The header names flash regions but does not read, write, erase, validate, or persist anything itself. It also describes descriptor/status memory written by hardware and consumed by the driver, but it owns no in-memory state.

## Dependencies and Integration Points

- Includes `<linux/types.h>` for fixed-width and endian-qualified kernel types.
- Uses `BIT()` for SFP diagnostic feature bits; callers must include a Linux bitops context that provides it.
- Integrates with SGE queue setup and completion paths through `struct sge_qstat`, `struct rsp_ctrl`, SGE mode constants, and interrupt deferral fields.
- Integrates with firmware, flash, and EEPROM code through flash offsets, sizes, and I2C/SFP field addresses.
- Integrates with PCIe memory access code through `enum pcie_memwin`.
- Closely complements `t4_regs.h`, `t4_msg.h`, `t4_tcb.h`, and `t4_values.h`: this file gives high-level dimensions while those headers provide register, CPL message, TCB, and register-value details.

## Risks and Edge Cases

- The constants are hardware ABI. Incorrect values silently corrupt queue sizing, descriptor parsing, flash offsets, or firmware mailbox access.
- T4/T5/T6 differences are embedded in separate constants such as `T6_RSS_NENTRIES`, `T6_PM_NSTATS`, and `CIM_NUM_OBQ_T5`; call sites must select by adapter generation.
- `struct rsp_ctrl` relies on big-endian fields and packed hardware layout expectations. Consumers must continue using endian conversions and avoid assuming host endianness.
- Flash region sizes and `FLASH_MIN_SIZE` encode assumptions about sector size and fixed layout; firmware update code must not use them for incompatible flash parts without explicit generation checks.
- The file defines broad constants in the global macro namespace, so new names can collide with nearby hardware headers if not kept specific.

## Test Signals

- Build coverage of `cxgb4` catches missing type/macro dependencies and field-name regressions.
- Queue bring-up and RX/TX traffic tests validate SGE dimensions, response descriptor parsing, and interrupt deferral values.
- Firmware update/configuration tests validate flash region offsets and minimum-size checks.
- EEPROM/SFP diagnostics via ethtool or driver debug paths validate I2C offsets and feature bits.
- Adapter matrix testing across T4, T5, and T6 is important because this header contains generation-specific table sizes and stats counts.
