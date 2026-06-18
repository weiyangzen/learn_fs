# sources/distributed-fs/ceph-client/drivers/cxl/cxlmem.h

Purpose: private CXL memory-device header that defines Type-3 memdev objects, mailbox opcodes/payloads, event/poison/security/firmware state, and interfaces used by PCI, mem, PMEM, poison, security, EDAC, firmware-update, and debug paths.

Important APIs/types/functions: `struct cxl_memdev`, `struct cxl_memdev_state`, `struct cxl_dpa_info`, `struct cxl_event_state`, `struct cxl_poison_state`, `struct cxl_security_state`, `struct cxl_fw_state`, `enum cxl_opcode`, mailbox payload structs for identify, partition, LSA, health, poison, security, and firmware, plus exported helpers such as `cxl_internal_send_cmd()`, `cxl_dev_state_identify()`, `cxl_enumerate_cmds()`, `cxl_mem_dpa_fetch()`, `cxl_poison_state_init()`, `cxl_mem_sanitize()`, and `devm_cxl_add_memdev()`.

Control flow and state: CXL PCI builds `cxl_memdev_state`, enumerates mailbox commands, identifies capacity/partitions, and registers a `cxl_memdev`; CXL bus drivers later attach that memdev into port topology. State includes partition resources, media-ready status, firmware slot transfer state, delayed sanitize polling, event buffer and mutex, poison command bitmap and list cache, security command bitmap/state, and dirty shutdown support.

Dependencies and integration: includes UAPI CXL memory ioctl definitions, PCI, cdev, UUID, node, CXL event/mailbox headers, libnvdimm security constants, and `cxl.h`. It bridges CXL hardware mailbox protocol to user-visible CXL char devices, libnvdimm labels/security, EDAC, debugfs, and firmware upload.

Risks and test signals: payload layout must remain packed/spec-correct, command return-code translation drives error propagation, and concurrency depends on mailbox/event/poison/security locks. Test command enumeration, unsupported-command masking, poison list/inject/clear, sanitize poll completion, LSA read/write, firmware transfer alignment, partition capacity setup, and CONFIG_CXL_* fallbacks.
