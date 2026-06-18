# sources/distributed-fs/ceph-client/drivers/nvmem/rave-sp-eeprom.c

Purpose: Read/write EEPROM NVMEM provider for ZII RAVE SP devices over the parent service processor protocol.

Important APIs/types/functions: `struct rave_sp_eeprom` stores parent SP pointer, mutex, EEPROM address, header size, and device. `rave_sp_eeprom_io()` formats low-level read/write page commands and validates response type/success. `rave_sp_eeprom_page_access()` handles single-page reads/writes, including read-modify-write for partial pages. `rave_sp_eeprom_access()` splits arbitrary NVMEM access at 32-byte page boundaries.

Control flow: probe parses `reg = <address size>`, rejects sizes too large for 16-bit page addressing, selects 4- or 5-byte command header depending on size > 8 KiB, initializes mutex, and registers byte-granular read/write NVMEM. Runtime access is serialized and chunked so no low-level operation crosses a page.

State/persistence: EEPROM contents persist on the RAVE SP-managed device. The driver keeps only protocol parameters and no data cache.

Dependencies/integration: OF compatible `zii,rave-sp-eeprom`; depends on parent `rave_sp_exec()`, NVMEM provider, OF `zii,eeprom-name`, and legacy fixed cells.

Risks: partial writes require a prior read; if read succeeds but write fails, data is unchanged but caller only sees protocol failure. All accesses serialize through one mutex, which is safe but limits throughput. Protocol response validation is minimal: type and success flag.

Test signals: small versus big header command formatting, page-boundary chunking, partial write read-modify-write, response type mismatch `-EPROTO`, failed success flag `-EIO`, and maximum-size validation.
