# sources/distributed-fs/ceph-client/drivers/spi/spi-axi-spi-engine.c

## Purpose
Analog Devices AXI SPI Engine host driver. It compiles SPI messages into hardware instruction programs, streams command/TX/RX FIFOs under IRQ control, and optionally exposes SPI offload trigger support with static TX data or stream DMA channels.

## Important APIs, Types, and Functions
`struct spi_engine_program` is a flexible array of 16-bit instructions. `struct spi_engine_message_state` tracks pending command words and TX/RX transfer cursors. `struct spi_engine_offload` stores assigned/prepared state, offload number, optimized config, lane masks, and bits-per-word. `struct spi_engine` stores clocks, MMIO base, lock, completion, interrupt mask, CS inversion, offload memory sizes, caps, and sync behavior. Key functions are precompile/compile, FIFO read/write helpers, IRQ handler, optimize/unoptimize, transfer-one-message, offload prepare/trigger, setup, and probe.

## Control Flow
Probe allocates a controller, detects optional offload from `trigger-sources` and DMA names, enables AXI and SPI clocks, maps registers, validates ADI AXI version, reads data/offload widths, resets interrupt state, requests IRQ, sets controller capabilities by IP version, and registers. Message optimization validates lane modes and offload constraints, computes effective speeds, dry-runs then allocates an instruction program, appends a sync instruction for normal messages, and preloads offload memories when needed. Non-offload transfer initializes message state, writes as much command and TX FIFO as possible, enables FIFO and sync interrupts, waits up to 5 seconds for sync completion, and finalizes. IRQ drains pending bits, refills command/TX FIFOs, drains RX FIFO, and completes on matching sync ID.

## State and Persistence
Compiled programs live in `msg->opt_state` until unoptimized. Runtime FIFO cursors live in `msg_state`. `cs_inv` shadows chip-select inversion and is programmed through command FIFO during setup. Offload assignment/prepared flags prevent conflicting users. Hardware is reset and interrupts disabled by managed release action.

## Dependencies and Integration Points
It depends on ADI AXI common version helpers, clk, IRQ, MMIO, `spi_controller` optimize hooks, tracepoints, SPI offload provider APIs, DMAengine channel requests, OF compatible `adi,axi-spi-engine-1.00.a`, and SPI multi-lane metadata.

## Risks
Normal transfers depend on a final sync IRQ and have a hard 5 second timeout. Offload supports only one offload instance for now. Single-transfer offload through `transfer_one_message` is rejected. FIFO handlers assume SPI core has validated transfer lengths against bits-per-word. Version-gated features mean CS_HIGH, MOSI idle, and multi-data-lane behavior differ by hardware IP version.

## Test Signals
Use message optimization tests with varied speeds, bpw, delays, `cs_change`, `cs_off`, and lane modes; IRQ FIFO refill/drain stress; RX/TX-only and full-duplex transfers; timeout injection; CS_HIGH setup; offload assignment/preparation contention; trigger enable/disable; and DMA channel request naming for offload streams.
