# sources/distributed-fs/ceph-client/drivers/firmware/efi/cper_cxl.c

Purpose: prints CXL protocol error sections embedded in CPER records, translating agent type, agent address, device ID, serial number, capability, DVSEC, and RAS error-log fields into kernel diagnostics.

Important APIs/types/functions: exports `cxl_cper_print_prot_err()`. It uses `struct cxl_cper_sec_prot_err`, `struct cxl_ras_capability_regs`, valid-bit flags, and agent-type constants from CXL event headers.

Control flow: the printer checks each valid-bit flag before output. Address formatting depends on agent type: most CXL device/port agents use segment:bus:device.function, while RCH downstream ports use RCRB base address. Device identity, serial, capability, DVSEC, and error-log payloads are printed only for agent types where the UEFI definition makes those fields meaningful.

State and persistence behavior: no persistent state; emits diagnostic logs.

Dependencies and integration points: called by `cper.c` for `CPER_SEC_CXL_PROT_ERR` sections. Depends on CXL event ABI structures and CPER PCIe slot encoding.

Risks and test signals: variable-length DVSEC/error-log data follows the fixed structure, so malformed lengths can shift parsing. Test signals include CPER CXL protocol records with each agent class, correct RAS register printing, and no output for invalid agent/type combinations.
