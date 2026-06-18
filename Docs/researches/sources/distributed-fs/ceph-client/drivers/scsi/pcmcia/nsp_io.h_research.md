# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_io.h

Purpose: inline I/O helper layer for the 16-bit NinjaSCSI PCMCIA driver.

Important APIs: `nsp_write()`/`nsp_read()` wrap byte I/O; `nsp_index_write()`/`nsp_index_read()` access indexed registers; FIFO helpers support 8/16/32-bit port transfers; MMIO helpers support mapped register and 32-bit FIFO access.

Control flow/state: `nsp_cs.c` uses these helpers for init, ISR status/control, and data phase movement. The file is stateless and relies on valid base addresses plus caller-managed alignment/counts.

Dependencies/integration: architecture I/O primitives and constants from `nsp_cs.h`.

Risks/test signals: raw pointer casts and integer MMIO bases are fragile, especially on 64-bit, matching Kconfig restrictions. Test IO8 baseline, aligned IO32/MEM32 transfers, mapped-window cards, and compile-test on restricted architectures.
