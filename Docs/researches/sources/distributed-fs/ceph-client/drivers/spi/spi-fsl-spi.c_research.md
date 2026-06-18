# sources/distributed-fs/ceph-client/drivers/spi/spi-fsl-spi.c

## Purpose
Implements the classic Freescale MPC8xxx SPI controller driver with CPU, QE CPU, CPM/QE buffer-descriptor, GRLIB, OF, and optional legacy platform support. It configures per-device modes and clock divisors, transfers data synchronously through IRQ/completion, delegates CPM mode to `spi-fsl-cpm.c`, and manages native/GPIO chip selects.

## Important APIs, Types, And Functions
Important functions include `fsl_spi_change_mode()`, shift setup helpers, `mspi_apply_cpu_mode_quirks()`, `fsl_spi_setup_transfer()`, `fsl_spi_cpu_bufs()`, `fsl_spi_bufs()`, `fsl_spi_prepare_message()`, `fsl_spi_transfer_one()`, `fsl_spi_setup()`, `fsl_spi_irq()`, GRLIB CS/probe helpers, `fsl_spi_probe()`, `of_fsl_spi_probe()`, remove paths, and module init/exit.

## Control Flow
Probe obtains OF/platform data, maps chip-select boot override if requested, determines chip-select count, allocates a host, initializes shared `mpc8xxx_spi` state, sets callbacks, initializes CPM if needed, maps registers, configures GRLIB capabilities when applicable, requests IRQ, initializes mode/mask/command/event registers, enables the controller, and registers it. Message preparation enforces no speed changes inside a message, opportunistically widens CPU-mode byte transfers to 16/32 bits, and adjusts CPM word sizes/endian constraints. Each transfer sets mode/divisors, starts CPU or CPM transfer, waits on completion, disables interrupts, and completes.

## State And Persistence
Per-device `spi_mpc8xxx_cs` caches hardware mode, buffer callbacks, and shifts. Controller state includes current buffers, count, flags, completion, CPM resources, shifts, and native CS metadata. Hardware mode is temporarily disabled/re-enabled for mode changes. No persistent storage is used.

## Dependencies And Integration Points
Depends on `spi-fsl-lib`, optional `spi-fsl-cpm`, `spi-fsl-spi.h` registers, SPI bitbang-era platform data, OF/GPIO/IRQ/address helpers, Freescale SoC clock/IMMR helpers, and optional GRLIB compatible data.

## Risks
Mode changes can glitch SPI clock, so preparation rejects intra-message speed changes and changes mode before CS assertion. CPM endian limitations reject some LSB-first word sizes. CPU IRQ waits spin on not-full events. Legacy and OF paths share probe/remove but resource cleanup for boot CS mapping is only in some failure paths, worth auditing.

## Test Signals
CPU and CPM transfers, mode/clock divisor boundaries, large-transfer word widening, LSB-first rejection in CPM, GRLIB native CS, GPIO CS and `fsl,spisel_boot`, IRQ completion, legacy platform probe, and remove cleanup are key tests.
