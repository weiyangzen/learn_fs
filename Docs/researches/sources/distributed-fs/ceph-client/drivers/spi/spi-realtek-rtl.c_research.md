# sources/distributed-fs/ceph-client/drivers/spi/spi-realtek-rtl.c

## Purpose
`spi-realtek-rtl.c` is a simple half-duplex SPI controller driver for Realtek RTL838x/RTL839x SoC SPI flash blocks. It sends or receives data through 1-byte and 4-byte register accesses, controls CS0, initializes byte ordering, and registers a basic SPI controller.

## Important APIs, Types, And Functions
- `struct rtspi` stores the MMIO base.
- `rt_set_cs()` toggles CS0 through `RTL_SPI_SFCSR`.
- `set_size()` selects 1-byte or 4-byte transfer length in the status/control register.
- `wait_ready()` busy-waits for `RTL_SPI_SFCSR_RDY`.
- `send4()`, `send1()`, `rcv4()`, and `rcv1()` perform blocking register transfers.
- `transfer_one()` handles TX-only or RX-only transfers in 4-byte chunks followed by 1-byte residue.
- `init_hw()` enables read/write big-endian byte ordering, disables CS1, and selects CS0.
- `realtek_rtl_spi_probe()` maps registers, initializes hardware, configures half-duplex callbacks, and registers the controller.

## Control Flow
Probe allocates a SPI host, maps the register resource, calls `init_hw()`, sets `SPI_CONTROLLER_HALF_DUPLEX`, assigns `set_cs` and `transfer_one`, and registers. Transfer execution checks whether TX or RX is present, then loops over 4-byte operations and remaining bytes. Each operation waits for hardware ready, sets transfer size, and writes or reads `SFDR`; completion is signaled immediately after the loop.

## State And Persistence Behavior
The driver holds only the register base as runtime state. There is no per-device state, no DMA, no IRQ, and no PM logic. Hardware byte-order and CS1-disabled state are initialized at probe and remain until reset/remove.

## Dependencies And Integration Points
It integrates with platform/OF matching for RTL8380/RTL8382/RTL8391/RTL8392/RTL8393 SPI blocks, the SPI core, and MMIO resource mapping. It exposes only half-duplex transfer behavior and does not advertise mode/bpw constraints beyond defaults.

## Risks
- `wait_ready()` has no timeout, so hardware lockup can spin forever.
- No explicit mode bits, speed programming, IRQ, DMA, or runtime PM are implemented.
- `init_hw()` uses `value &= RTL_SPI_SFCSR_CS`, which preserves only the CS select bit and clears other fields before writing; this depends on hardware reset/default expectations.
- TX and RX are mutually exclusive; full-duplex clients rely on SPI core half-duplex constraints.

## Test Signals
- Probe on each listed Realtek compatible.
- TX-only and RX-only transfers with lengths divisible by 4 and with 1-3 byte residues.
- CS0 assert/deassert polarity.
- Hardware-ready wait behavior under slow flash.
