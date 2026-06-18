# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/psoc_spi_regs.h

Purpose: maps the PSOC SPI controller registers. The 60 macros cover the DesignWare-style controller setup, enable, slave-enable, baud rate, FIFO thresholds/levels, status, interrupt mask/status/clear registers, identification/version registers, 36 data registers, sample delay, and reserved locations.

Important APIs/types/functions: macro-only `mmPSOC_SPI_*` definitions from `mmPSOC_SPI_CTRLR0` at `0xC43000` through `mmPSOC_SPI_RSVD_2` at `0xC430FC`. Data register macros `mmPSOC_SPI_DR0..DR35` represent the FIFO/data window.

Control flow: firmware or driver SPI access configures CTRLR registers and baud rate, enables the controller, selects a target through `SER`, transfers through `DR*`, polls FIFO/status registers, handles interrupts, then clears interrupt state.

State and persistence: controller configuration, FIFO contents, interrupt latches, and enable state live in hardware. The header retains no state.

Dependencies and integration: included by `goya_regs.h` and tied to PSOC boot/flash flows and SPI image status in global configuration. It may be used by firmware more than host code, but the host register map still needs the definitions for diagnostics and low-level access.

Risks: incorrect FIFO/status address definitions can corrupt SPI transactions or hang boot flash access. Reserved registers should not be repurposed without updated hardware documentation.

Test signals: firmware image read/write, SPI flash boot, interrupt clear behavior, FIFO depth/threshold tests, and controller version ID readback.
