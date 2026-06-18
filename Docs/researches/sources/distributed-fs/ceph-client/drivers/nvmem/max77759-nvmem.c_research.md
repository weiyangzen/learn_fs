# sources/distributed-fs/ceph-client/drivers/nvmem/max77759-nvmem.c

Purpose: EEPROM-like NVMEM provider for Maxim MAX77759, using the parent MFD's MAXQ command transport.

Important APIs/types/functions: `struct max77759_nvmem` links the platform child to the parent `struct max77759`. `max77759_nvmem_reg_read()` sends `MAX77759_MAXQ_OPCODE_USER_SPACE_READ`; `max77759_nvmem_reg_write()` sends `MAX77759_MAXQ_OPCODE_USER_SPACE_WRITE`; probe registers an EEPROM-type NVMEM device with byte stride and `ignore_wp = true`.

Control flow: NVMEM reads/writes build MAXQ command and response buffers with a three-byte opcode/offset/length header. The response must echo the header for reads and the whole command for writes; otherwise the callback reports `-EIO`.

State/persistence: data persists inside MAX77759 user-space NVMEM. Driver state is per-device and devm-managed; no cache is kept.

Dependencies/integration: depends on `linux/mfd/max77759.h` and the parent MFD drvdata/command path; matches OF `maxim,max77759-nvmem` and platform id `max77759-nvmem`.

Risks: maximum readable/writable size is bounded by command payload length, and callers rely on NVMEM core to enforce `.size`. Protocol echo mismatches are warned but not retried. Write protection is explicitly ignored at NVMEM config level because access control is delegated to the transport/device.

Test signals: mock MAXQ responses for successful read/write, transport errors, header mismatch, oversized NVMEM requests, and parent drvdata absence.
