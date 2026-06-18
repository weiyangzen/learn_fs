<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-pspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-pspi.c

## Purpose

`spi-npcm-pspi.c` is the Nuvoton NPCM peripheral SPI controller driver. It implements an interrupt-driven, register-FIFO style SPI host for normal SPI devices, supporting 8- and 16-bit words, modes 0-3, GPIO descriptors for chip select, and reset/clock setup.

## Important APIs, Types, and Functions

`struct npcm_pspi` stores completion, reset control, controller, remaining TX/RX byte counts, MMIO base, cached mode/word/speed parameters, TX/RX pointers, clock, and id. Small helpers enable/disable IRQ bits and the SPI engine. `npcm_pspi_set_mode()`, `npcm_pspi_set_transfer_size()`, and `npcm_pspi_set_baudrate()` program control register fields.

`npcm_pspi_setup_transfer()` caches buffers and transfer parameters, optionally upgrades even-length 8-bit transfers to 16-bit hardware words, and updates hardware only when mode/word/speed changed. `npcm_pspi_send()` and `npcm_pspi_recv()` move one hardware word. `npcm_pspi_handler()` drives the interrupt state machine. `npcm_pspi_transfer_one()` starts the engine and waits for completion. Probe maps registers, enables the clock, gets reset and IRQ, resets hardware, requests IRQ, initializes the controller, and registers it.

## Control Flow

Before transfer, the driver records TX/RX buffers and sets both byte counters to transfer length. It programs SPI mode, transfer size, and divider if cached values differ. Transfer execution reinitializes completion, enables the SPI engine, and waits up to two seconds.

The interrupt handler reads status. For TX transfers, it drains receive-buffer-full by reading dummy data, completes when no TX bytes remain, and sends the next word whenever the controller is not busy. For RX transfers, it reads data when receive-buffer-full is set, completes when RX bytes reach zero, and writes dummy zero bytes when the controller is idle and no TX buffer exists, causing clocks for further RX data. Prepare/unprepare hardware enables or disables read/write interrupts around message processing.

## State and Persistence Behavior

Cached `mode`, `bits_per_word`, `speed_hz`, and `is_save_param` reduce repeated register writes. TX/RX byte counters and buffer pointers are active-transfer state only. The driver has no file persistence; writes affect only external SPI devices.

The hardware is reset at probe and remove. The clock is enabled for the lifetime of the registered controller; no runtime PM path is implemented.

## Dependencies and Integration Points

The driver integrates with SPI core, platform devices, OF compatibles `nuvoton,npcm750-pspi` and `nuvoton,npcm845-pspi`, clock framework, reset framework, MMIO helpers, interrupts, completions, and GPIO descriptor chip selects.

## Risks and Edge Cases

`npcm_pspi_setup_transfer()` mutates `t->bits_per_word` from 8 to 16 for even-length transfers, which is efficient but surprising and assumes byte order handling remains correct. The baud-rate divider is not clamped in `npcm_pspi_set_baudrate()` even though min/max divider constants exist; the SPI core's min/max speed fields should prevent invalid rates. The switch in `npcm_pspi_set_mode()` has no default assignment, relying on `SPI_MODE_X_MASK` to produce one of four cases.

Completion depends entirely on interrupts; lost interrupts lead to a two-second timeout and engine disable.

## Test Signals

Tests should cover modes 0-3, 8-bit odd length, 8-bit even length upgraded to 16-bit, explicit 16-bit transfers, TX-only, RX-only dummy-clock generation, timeout when IRQ is missing, min/max speed bounds, reset failure, IRQ request failure, remove reset behavior, and repeated transfers that reuse cached mode/speed/word settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-npcm-pspi.c -->
