# sources/distributed-fs/ceph-client/drivers/spi/spi-geni-qcom.c

## Purpose

`spi-geni-qcom.c` is the Qualcomm GENI/QUP SPI controller driver. It registers either a SPI host or target controller depending on firmware properties, programs GENI SPI protocol state, and moves SPI transfers through FIFO, SE DMA, or GPI DMA paths. The driver is tightly coupled to the Qualcomm GENI serial engine, interconnect bandwidth voting, runtime PM, OPP clock selection, and the SPI core transfer lifecycle.

## Important APIs, Types, and Functions

The central runtime object is `struct spi_geni_master`, which embeds `struct geni_se`, device and IRQ references, FIFO geometry, cached mode/CS/speed/bits-per-word, active transfer counters, completions for command cancellation/abort/DMA reset, DMA channels, and the current transfer mode. Probe wires `spi_geni_prepare_message()`, `spi_geni_transfer_one()`, `geni_can_dma()`, `spi_geni_handle_err()`, and optional `spi_geni_target_abort()` into `struct spi_controller`.

Key setup helpers are `spi_geni_init()`, `spi_slv_setup()`, `get_spi_clk_cfg()`, `geni_spi_set_clock_and_bw()`, `setup_fifo_params()`, `spi_setup_word_len()`, and `spi_geni_grab_gpi_chan()`. Transfer helpers split into `setup_se_xfer()` plus `geni_spi_handle_tx()`/`geni_spi_handle_rx()` for FIFO/SE DMA, and `setup_gsi_xfer()` with `spi_gsi_callback_result()` for GPI DMA. Error handling is in `handle_se_timeout()`, `handle_gpi_timeout()`, and `spi_geni_is_abort_still_pending()`. Interrupt completion is centralized in `geni_spi_isr()`.

## Control Flow

Probe maps the SE resource, gets the `se` clock, allocates a host or target controller, configures OPP/interconnect/runtime PM, initializes completions and the lock, calls `spi_geni_init()`, requests the IRQ, and registers the controller. `spi_geni_init()` validates or loads GENI SPI firmware, reads FIFO depth/width, initializes GENI FIFO thresholds, selects oversampling from QUP hardware version, and chooses GPI DMA if the FIFO interface is disabled and DMA channels are available, otherwise FIFO mode.

For each message, `spi_geni_prepare_message()` verifies no abort IRQ is still pending and, for SE modes, updates cached CS, loopback, CPHA, CPOL, CS polarity, and demux registers. `spi_geni_transfer_one()` rejects new work after a failed abort, completes zero-length transfers immediately, and dispatches to `setup_se_xfer()` or `setup_gsi_xfer()`. The SE path programs word packing, clock/divider, transfer lengths, M command parameters, mode selection, DMA descriptors or initial FIFO fill, then returns positive so the SPI core waits for interrupt completion. The GPI path configures DMA peripheral metadata, prepares RX if needed and TX always, submits descriptors, and finalizes in the DMA callback.

The ISR handles FIFO RX watermarks, FIFO TX watermarks, command done, SE DMA done/reset interrupts, cancel/abort completions, and interrupt acknowledgement under `mas->lock`. FIFO command done finalizes the current transfer and logs premature completion if byte counters remain. Error callbacks cancel then abort M commands, reset DMA FSMs when needed, and prevent new transfers while enabled pending IRQs indicate the abort path has not drained.

## State and Persistence Behavior

State is volatile per controller. `spi_geni_master` persists cached mode/clock/CS settings, active byte counters, current transfer pointer, DMA channel ownership, and abort health. Hardware state persists in GENI registers while the device is runtime-active and is reconstructed by message/transfer setup. No file-backed state exists.

Runtime PM saves power by disabling GENI resources and ICC paths on suspend, dropping OPP votes, and restoring resources plus the last source clock vote on resume. A failed abort sets `abort_failed`; later prepares poll pending IRQ state to avoid starting transfers while stale GENI interrupts could collide with a new transaction.

## Dependencies and Integration Points

The driver depends on the SPI core, Qualcomm GENI SE helpers, QCOM GPI DMA metadata, Linux DMAengine, OPP, interconnect bandwidth APIs, runtime/system PM, platform resources, and firmware/device properties. It consumes `qcom,geni-spi` compatibles and `spi-slave` to select target mode. The SPI core supplies DMA-mapped scatterlists and finalization callbacks; GENI hardware supplies M IRQ and DMA IRQ status bits.

## Risks and Edge Cases

The GPI path requires a TX descriptor even for RX-only transfers; failure to provide mapped TX SG data would break GPI semantics, hence `SPI_CONTROLLER_MUST_TX`. SE DMA only supports single-entry SG lists and silently falls back to FIFO for multi-entry lists. Length calculations for non-byte-aligned words depend on consistent word-count programming; premature done logging explicitly points at risks when `bits_per_word != 8`. Abort timeout paths must handle races where an ISR completed the transfer while error handling waited for the lock. Runtime resume restores `cur_sclk_hz`, so clock state must be initialized before suspend.

## Test Signals

Useful tests include host and target probe, FIFO-disabled systems with working and missing GPI DMA channels, loopback/CPOL/CPHA/CS-high mode changes across devices, 4 to 32 bit words, zero-length transfers, RX-only/TX-only/full-duplex transfers, multi-transfer messages with and without `cs_change`, SE DMA single-entry SG, forced FIFO fallback for multi-entry SG, timeout-induced cancel/abort and DMA FSM reset, runtime suspend/resume during idle, and pending-interrupt recovery after an abort failure.
