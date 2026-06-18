# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91.h

## Purpose
Shared private header for the AT91 TWI driver family. It defines register offsets, bitfields, feature constants, and the private state structures used by the AT91 core, master, and optional slave files.

## APIs, Control Flow, and State
Key constants include `AT91_I2C_TIMEOUT`, `AT91_I2C_DMA_THRESHOLD`, `AUTOSUSPEND_TIMEOUT`, and `AT91_I2C_MAX_ALT_CMD_DATA_SIZE`. The register map covers control, mode, status, interrupt, FIFO, filter, alternative command, and version registers. `struct at91_twi_pdata` captures per-SoC capability flags; `struct at91_twi_dma` tracks DMA channels, SG entries, mapping direction, and in-progress state; `struct at91_twi_dev` holds MMIO, completion, clock, adapter, current buffer/message, IRQ masks/status, DMA, FIFO/filter settings, recovery info, and optional slave fields.

## Dependencies and Integration
Includes Linux clk, completion, DMA, I2C, and platform-device types. It declares the shared core helpers plus `at91_twi_probe_master()`/`at91_init_twi_bus_master()` and conditional slave prototypes or stubs.

## Risks and Test Signals
Risks are contract drift between compilation units, wrong bit masks for newer SoCs, and conditional slave fields being used outside the config guard. Test by building with and without `CONFIG_I2C_AT91_SLAVE_EXPERIMENTAL`, with DMA/FIFO-capable DTs, and by checking sparse/build warnings around register bit use and function prototypes.
