# sources/distributed-fs/ceph-client/drivers/nvmem/qnap-mcu-eeprom.c

Purpose: Read-only EEPROM NVMEM provider behind a QNAP MCU command protocol.

Important APIs/types/functions: `qnap_mcu_eeprom_read_block()` sends command `{0xf7, 0xa1, offset, bytes}` through `qnap_mcu_exec()` and validates echoed command bytes. `qnap_mcu_eeprom_read()` chunks arbitrary reads into 32-byte blocks. Probe registers a 256-byte EEPROM NVMEM device using the parent MCU drvdata.

Control flow: probe gets `struct qnap_mcu` from the parent, fills byte-granular read-only NVMEM config, and registers. Reads loop until requested bytes are consumed, issuing at most 32 bytes per MCU transaction.

State/persistence: EEPROM data persists behind the MCU. The driver allocates a temporary reply buffer per block read and keeps no cache.

Dependencies/integration: depends on `linux/mfd/qnap-mcu.h`, parent platform/MFD device, and NVMEM provider core; no OF match table because the child is platform-created by the MCU driver.

Risks: offset is encoded in one command byte, matching the fixed 256-byte size. Protocol echo mismatch returns `-EIO`; no retries are attempted. Block size was determined empirically, so larger transfers may be unreliable.

Test signals: zero-length reads, multi-block reads, echo mismatch, MCU transport errors, and NVMEM size boundary behavior.
