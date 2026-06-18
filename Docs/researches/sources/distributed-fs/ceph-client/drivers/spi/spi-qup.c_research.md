# sources/distributed-fs/ceph-client/drivers/spi/spi-qup.c

## Purpose
`spi-qup.c` is the Qualcomm QUP SPI controller driver for QUP v1/v2 hardware. It supports FIFO, block, and BAM/DMOV-style DMA transfer modes, programs QUP/SPI state machines, handles native chip select for newer QUP versions, manages clocks/OPP/interconnect bandwidth, and provides runtime/system PM.

## Important APIs, Types, And Functions
- `struct spi_qup` stores register base, clocks, interconnect path, IRQ, FIFO/block sizes, active transfer state, completion/error state, word size/count, TX/RX buffer cursors, QUP version flag, DMA mode, DMA configs, and current bandwidth vote.
- `spi_qup_set_state()` transitions QUP among RESET/RUN/PAUSE with validity polling and special PAUSE-to-RESET handling.
- `spi_qup_io_prep()` chooses FIFO, block, or DMA mode based on transfer size, DMA mapping, and loopback constraints.
- `spi_qup_io_config()` resets/configures counters, IO modes, pack/unpack, SPI clock polarity/phase/loopback/high-speed mode, QUP config, and IRQ masks for a transfer.
- `spi_qup_do_pio()` runs FIFO/block transfers and waits for IRQ completion.
- `spi_qup_do_dma()` chunks SG lists to `SPI_MAX_XFER`, prepares DMA descriptors, starts QUP RUN state, issues DMA, and waits for completion.
- `spi_qup_qup_irq()` handles QUP/SPI error flags, FIFO/block service flags, DMA operational acks, and transfer completion.
- `spi_qup_probe()` maps resources, gets clocks/ICC/OPP, initializes DMA if available, discovers FIFO/block sizes, resets hardware, requests IRQ, enables PM, and registers the controller.

## Control Flow
Probe reads `spi-max-frequency` and `num-cs`, creates a SPI host, optionally acquires DMA channels, determines QUP version from OF match data, enables clocks, derives FIFO and block sizes from `QUP_IO_M_MODES`, resets the hardware, enables error interrupts, configures baseline SPI IO control, requests IRQ, enables runtime PM, and registers.

For each transfer, `spi_qup_transfer_one()` prepares mode and timeout, resets byte counters and error state, then runs DMA or PIO. PIO mode may split large transfers into `SPI_MAX_XFER` iterations and falls back to FIFO for small chunks; it sequences RESET, RUN, PAUSE, optional initial FIFO write, RUN, then waits for completion. DMA mode walks RX/TX SG lists in bounded chunks, configures IO for each chunk, starts QUP RUN, submits DMA descriptors, and waits for the DMA callback completion. Both paths reset QUP after completion and terminate DMA on errors.

## State And Persistence Behavior
Active transfer state is stored in `struct spi_qup` and protected by a spinlock where shared with IRQ. Completion state is per transfer via `struct completion done`. Bandwidth votes persist as `bw_speed_hz` and are changed on DMA transfer speed changes and PM suspend. Runtime suspend enables QUP clock auto-gating, disables clocks, votes ICC bandwidth to zero, and runtime resume reenables clocks and disables auto-gating.

## Dependencies And Integration Points
The driver integrates platform/OF probing for `qcom,spi-qup-v1.1.1`, `qcom,spi-qup-v2.1.1`, and `qcom,spi-qup-v2.2.1`; SPI core; DMA engine; OPP; interconnect; runtime/system PM; clock framework; and optional GPIO descriptors. It includes SPI internals for DMA mapping helpers and advertises 4-32 bpw, mode 0-3, loopback, and up to four native chip selects.

## Risks
- QUP state transitions are timing-sensitive and return `-EIO` after short polling loops.
- DMA eligibility depends on cache alignment, channel availability, QUP version block alignment, and transfer size; boundary coverage is important.
- Timeout is computed from speed and length with a 100x multiplier; extremely low or unusual speeds may stress the calculation.
- IRQ error handling stores only the first error and still services flags; races with completion need coverage.
- Runtime/system PM sequencing touches clocks and ICC in different orders; suspend while runtime-suspended has an explicit resume path.
- QUP v1 lacks native CS handling and masks input overrun differently from newer hardware.

## Test Signals
- FIFO, block, and DMA transfers with TX-only, RX-only, and full-duplex buffers.
- QUP v1 and v2 OF matches, native CS behavior, and GPIO CS fallback.
- DMA alignment and block-size rejection cases.
- QUP/SPI error flags: overrun, underrun, clock over/underrun.
- Loopback size limit and high-speed mode threshold.
- Runtime PM autosuspend/resume and system suspend/resume.
