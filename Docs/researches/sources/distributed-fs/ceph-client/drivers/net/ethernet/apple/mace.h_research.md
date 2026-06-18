## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/mace.h

Purpose: MACE register layout and bit definitions for both PowerMac DBDMA MACE and Macintosh 68k PSC-DMA MACE drivers.

Important APIs/types: `struct mace` models the byte-wide register layout with 16-byte spacing through `REG(x)`. Constants cover transmit control/status (`XMTFC`, `XMTFS`, `XMTRC`), receive status (`RCVFS`), FIFO counts, interrupt/mask bits, bus interface control, FIFO configuration, MAC control, physical layer selection, address programming, and test/loopback modes.

Control flow: no functions. Drivers use this map to soft-reset, select ports, program station and logical multicast addresses, interpret TX/RX status bytes, configure FIFO watermarks, enable TX/RX, and read counters that clear on access.

State and persistence: describes volatile MMIO state only. Some status registers clear on read, so driver order matters. The `REG()` layout encodes hardware spacing and must match bus access width.

Dependencies/integration: included by `mace.c` and `macmace.c`; the same constants support DBDMA and PSC-DMA implementations.

Risks: duplicate macro name `XMTSV` appears for both `XMTFS` and `PR` status meanings, intentionally same value but easy to misuse. Because counters clear when read, instrumentation can perturb state. Port selection and `ADDRCHG` handling are chip-revision sensitive.

Test signals: successful reset/interrupt handling in both MACE drivers, correct multicast filter loading, accurate TX/RX error statistics, and port link behavior.
