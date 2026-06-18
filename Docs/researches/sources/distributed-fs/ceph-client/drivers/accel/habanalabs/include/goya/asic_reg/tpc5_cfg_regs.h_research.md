## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_cfg_regs.h

Purpose: auto-generated TPC5 configuration map. It has the same normalized layout as TPC4/TPC6/TPC7 CFG and defines 432 `mmTPC5_CFG_*` offsets from `0xF46400` to `0xF46E2C`.

Important API surface: eight kernel tensor descriptors and eight QM tensor descriptors, each with base, padding, tensor config, and five dimension descriptors; kernel/QM base addresses, TID base/size registers, 32 SRF entries per bank, kernel config and sync-object messages; shared TPC state/control registers for TBUF, semaphore, flags, status, CFG/SM translation, command, execute, stall, icache, MSS, TSB, interrupts, ARUSER/AWUSER, and MBIST.

Control flow and state: declarative register constants only. Firmware/driver code fills descriptors and controls execution through these MMIO addresses. Runtime state exists in TPC5 hardware registers and interrupt/status bits.

Dependencies and integration: included via `goya_regs.h`; the register family is addressed alongside `TPC_MAX_NUM` loops and event IDs such as `GOYA_ASYNC_EVENT_ID_TPC5_KRN_ERR`.

Risks and test signals: generated-offset drift can program the wrong tensor/kernel field or leave TPC5 unprotected. Test with TPC5 kernel launch, descriptor validation, TPC interrupt cause/mask handling, MBIST, context/security setup, and register-map checksum comparison to sibling TPCs.
