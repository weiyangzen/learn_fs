# sources/distributed-fs/ceph-client/drivers/scsi/nsp32_io.h

Purpose: inline register and FIFO access layer for the NinjaSCSI-32Bi/UDE driver.

Important APIs: `nsp32_write1/read1`, `write2/read2`, and `write4/read4` wrap port I/O. `nsp32_mmio_write*/read*` access memory-mapped registers using `NSP32_MMIO_OFFSET` and endian conversion. `nsp32_index_read*/write*` and MMIO-index variants select `INDEX_REG` and transfer via data registers. `nsp32_fifo_read()`/`nsp32_fifo_write()` use 32-bit string I/O.

Control flow/state: used throughout init, queueing, ISR, EEPROM, and debug code. It stores no state; correctness depends on valid base addresses and callers respecting hardware access-width limitations.

Dependencies/integration: architecture I/O primitives, endian helpers, and register constants from `nsp32.h`.

Risks/test signals: raw MMIO pointer casts weaken `__iomem` checking, and wrong access width/endian conversion can corrupt hardware programming. Test with register init, FIFO transfer, indexed register reads, and big-endian build/runtime coverage.
