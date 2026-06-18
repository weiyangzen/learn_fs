## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/socrates_nand.c

Purpose: this is the ABB/Emcraft Socrates board NAND driver for an FPGA-backed NAND access register. It adapts raw NAND legacy callbacks to a big-endian FPGA command/data/status register and defaults to software Hamming ECC.

Important APIs, types, and functions: `struct socrates_nand_host` embeds a `nand_controller`, a `nand_chip`, the FPGA MMIO base, and device pointer. `socrates_nand_cmd_ctrl()` emits command/address cycles through `FPGA_NAND_CMD_COMMAND` or `FPGA_NAND_CMD_ADDR`; `socrates_nand_read_buf()`, `write_buf()`, and `read_byte()` perform byte transfers through the register’s data field; `socrates_nand_device_ready()` reads `FPGA_NAND_BUSY`. `socrates_attach_chip()` selects soft Hamming when the core left the algorithm unknown.

Control flow: probe devm-allocates the host, maps the first OF resource with `of_iomap()`, initializes the NAND controller, links controller data and flash node, installs legacy callbacks, sets a conservative 20 us chip delay, defaults ECC engine type to software, scans one chip, and registers the MTD. Command and data paths are synchronous register writes/reads with no DMA or IRQ handling.

State and persistence: runtime state is the mapped FPGA register and embedded NAND objects. Persistent media behavior is generic raw NAND plus the selected software ECC. Remove unregisters MTD, calls `nand_cleanup()`, and unmaps the FPGA register.

Dependencies and integration points: it depends on OF matching for `abb,socrates-nand`, raw NAND legacy callbacks, MTD registration, big-endian IO accessors, and the FPGA register protocol defining command type, data shift, enable, and busy bits.

Risks: the driver writes one byte per 32-bit big-endian register access, so bus ordering and FPGA semantics are critical. There is no explicit timeout beyond generic NAND waits and fixed chip delay. Probe uses devm memory but manual `of_iomap()`/`iounmap()`. The comment admits the real command delay is unknown, so timing margins require hardware validation.

Test signals: successful DT probe, READID through command/address/data register paths, ready/busy polarity correctness, stable software-Hamming reads/writes, MTD registration, and no timeout or corrupted-byte symptoms under repeated page transfers.
