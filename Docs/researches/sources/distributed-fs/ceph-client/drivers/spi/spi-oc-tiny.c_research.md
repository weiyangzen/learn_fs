# sources/distributed-fs/ceph-client/drivers/spi/spi-oc-tiny.c

Purpose: OpenCores tiny SPI host driver using `spi_bitbang`. It supports a simple MMIO controller with TX/RX data, status, control, and baud registers, optionally interrupt-driven transfers, and platform data or device tree properties for base clock and baud register width.

Important APIs, types, and functions: `struct tiny_spi` embeds `struct spi_bitbang` first and tracks MMIO base, optional IRQ, frequency, baud width/current baud, mode, transfer counters, and current buffers. `tiny_spi_baud()` calculates a divider from controller frequency. `tiny_spi_setup()` caches mode and default baud; `tiny_spi_setup_transfer()` writes the selected baud and mode. `tiny_spi_txrx_bufs()` implements either IRQ or polling transfers; `tiny_spi_irq()` advances byte-at-a-time interrupt state. Probe allocates a host, maps resource 0, optionally requests IRQ, reads platform/OF timing data, and starts the bitbang engine.

Control flow: SPI core calls bitbang setup and transfer callbacks. In IRQ mode the driver primes one or two bytes, enables status interrupts by writing TXR/TXE status bits, then waits on a completion completed by `tiny_spi_irq()`. In polling mode it writes each byte, waits for TX ready or TX empty, and reads returned bytes when an RX buffer exists.

State and persistence: state is volatile per-controller and per-transfer counters in `struct tiny_spi`; no persistent storage. `speed_hz`, `baud`, and `mode` are cached to avoid repeated divider calculation. Remove stops bitbang and drops the host reference.

Dependencies and integration points: depends on `spi_bitbang`, platform resources, optional OF properties `clock-frequency` and `baud-width`, optional IRQ, and GPIO descriptors for chip select. It accepts SPI CPOL/CPHA/CS_HIGH mode bits.

Risks: there is no timeout in polling waits, so wedged hardware can spin forever. If neither platform data nor OF properties provide sane `freq` and `baudwidth`, baud calculation can be wrong. IRQ mode uses shared mutable transfer fields and assumes one active transfer through bitbang serialization. The hardware is byte-oriented only and does not advertise bits-per-word flexibility.

Test signals: verify polling and IRQ transfer paths, RX-only/TX-only/full-duplex byte streams, mode changes, divider selection at min/max speeds, GPIO chip select behavior, missing optional IRQ, and DT/platform-data initialization.
