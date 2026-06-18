# sources/distributed-fs/ceph-client/drivers/spi/spi-qcom-qspi.c

## Purpose
`spi-qcom-qspi.c` is a Qualcomm QSPI controller driver for standard half-duplex SPI and SPI memory users. It supports PIO transfers through read/write FIFOs and optional descriptor-based DMA for larger transfers, manages core/interface clocks, OPP clock rates, interconnect bandwidth votes, runtime PM, and SPI memory transfer size adjustment.

## Important APIs, Types, And Functions
- `struct qcom_qspi` stores MMIO base, device, clocks, active transfer state, DMA descriptor pool/arrays, interconnect path, last speed, and an IRQ-protected spinlock.
- `struct qspi_xfer` tracks active buffer, remaining bytes, bus width, transfer direction, and fragment/last-transfer state.
- `struct qspi_cmd_desc` is the hardware DMA command descriptor.
- `qcom_qspi_transfer_one()` sets speed, records transfer direction/bus width, chooses DMA or PIO, and starts the hardware.
- `qcom_qspi_setup_dma_desc()` validates SG limits/alignment/read length and builds command descriptor chains.
- `qcom_qspi_irq()` handles PIO FIFO service, hardware errors, DMA-chain completion, descriptor freeing, and SPI transfer finalization.
- `qcom_qspi_prepare_message()` configures chip select, SPI mode, pin hold/wp, feedback clock, SBL mode, and timing delay fields.
- `qcom_qspi_adjust_op_size()` shrinks unaligned large SPI memory reads to a 4-byte multiple for DMA safety.
- Runtime/system PM hooks manage clocks, OPP rates, interconnect enablement, and pinctrl states.

## Control Flow
Probe maps registers, obtains core/interface clocks, gets the `qspi-config` interconnect path, initializes a minimal bandwidth vote for register access, requests IRQ, sets a 32-bit DMA mask, configures SPI controller capabilities, attaches optional DMA only when an IOMMU is present, sets up OPP support, creates a DMA descriptor pool, enables runtime PM, and registers the controller.

For each message, `prepare_message()` writes master config and clears DMA mode. For each transfer, `transfer_one()` updates OPP/interconnect bandwidth based on speed, records active transfer state under lock, uses DMA if the SPI core supplied SG lists, and falls back to PIO on descriptor alignment/size constraints. PIO writes are fed by `WR_FIFO_EMPTY`; PIO reads drain `RESP_FIFO_RDY`. DMA starts by writing `NEXT_DMA_DESC_ADDR`; `DMA_CHAIN_DONE` frees descriptors and finalizes.

## State And Persistence Behavior
Runtime state includes `last_speed`, interconnect bandwidth vote, active `xfer`, and outstanding DMA descriptors. The driver stores descriptor virtual and DMA addresses until IRQ completion or error handling frees them. Runtime suspend drops OPP rate, disables clocks, disables ICC, and selects sleep pinctrl; runtime resume reverses that and restores the last OPP-derived core rate.

## Dependencies And Integration Points
The driver integrates platform/OF probing, SPI core, `spi_mem` adjustment, DMA pools, DMA mapping constraints, interconnect framework, OPP, clock bulk API, pinctrl, runtime/system PM, and an optional IOMMU-aware DMA path. It advertises dual/quad TX/RX and `SPI_CONTROLLER_HALF_DUPLEX`.

## Risks
- DMA supports at most `QSPI_MAX_SG` entries and requires 32-byte aligned DMA addresses; otherwise it falls back to PIO.
- DMA reads with non-4-byte lengths are unsafe because hardware writes whole words, so `spi_mem` adjustment and fallback paths are critical.
- Error IRQs log FIFO/NOC faults but completion status propagation is limited because the IRQ finalizes through SPI core without storing a rich error in active state.
- Descriptor cleanup must occur on all error and completion paths to avoid DMA pool leaks.
- Speed changes affect both OPP and ICC; runtime resume uses `last_speed * 4`, so zero/initial-speed behavior depends on transfer ordering.

## Test Signals
- PIO reads/writes for 1/2/4 bus widths and short transfers.
- DMA transfers with aligned SG, too many SG entries, unaligned DMA address, and non-word-multiple reads.
- `spi_mem` large read adjustment and follow-up residual transfer.
- IRQ error bits: response FIFO underrun, write FIFO overrun, and NOC response error.
- Runtime PM suspend/resume with clock, OPP, ICC, and pinctrl transitions.
