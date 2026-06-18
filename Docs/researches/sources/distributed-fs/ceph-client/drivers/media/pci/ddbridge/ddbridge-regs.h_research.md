# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-regs.h

Purpose: centralizes ddbridge MMIO register offsets and bit definitions for SPI, GPIO, board control, interrupts, temperature monitor, I2C, DMA/TS, CI, and LNB command blocks.

Important APIs/types/functions: register macros include `SPI_CONTROL`, `GPIO_*`, `BOARD_CONTROL`, `INTERRUPT_*`, `MSI*_ENABLE`, `TEMPMON_*`, `I2C_*`, `TS_CONTROL*`, `DMA_BUFFER_*`, `CI_*`, and `LNB_*`. Parameterized macros derive per-I/O or per-CI offsets.

Control flow: no executable flow. These constants drive all MMIO in core, main, I2C, MAX, and CI paths.

State and persistence: no state; constants represent hardware layout.

Dependencies/integration: included by ddbridge C files that access hardware registers.

Risks and test signals: wrong offsets or bit masks can corrupt unrelated hardware functions. Test through register-level smoke tests: interrupts enable/ack, I2C transfer, DMA start/stop, CI access, temp monitor, and LNB DiSEqC commands on supported board revisions.
