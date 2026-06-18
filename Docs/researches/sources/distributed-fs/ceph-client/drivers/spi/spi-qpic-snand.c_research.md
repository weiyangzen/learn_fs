# sources/distributed-fs/ceph-client/drivers/spi/spi-qpic-snand.c

## Purpose
`spi-qpic-snand.c` is a Qualcomm QPIC SPI-NAND controller driver for IPQ9574-class hardware. It exposes a `spi_controller` with `spi_mem` operations, maps SPI-NAND opcodes to QPIC NAND controller commands, integrates a pipelined on-host NAND ECC engine, and uses the common Qualcomm NAND controller BAM/DMA helper layer for register/data transactions.

## Important APIs, Types, And Functions
- `struct qpic_spi_nand` links the QPIC NAND controller, SPI controller, MTD, ECC engine/config, buffers, cached command/address values, codeword count, and current IO mode flags.
- `struct qpic_ecc` stores ECC geometry and precomputed raw/ECC register configurations.
- `qcom_spi_probe()` allocates QPIC/SPI/NAND state, maps resources, maps controller registers for DMA, allocates common NAND resources, initializes SPI config, registers the ECC engine, and registers the SPI controller.
- `qcom_spi_mem_ops` provides `supports_op` and `exec_op`; `qcom_spi_mem_caps` advertises ECC support.
- ECC engine callbacks `qcom_spi_ecc_init_ctx_pipelined()`, `cleanup_ctx`, `prepare_io_req`, and `finish_io_req` configure BCH ECC and record per-request flags/statistics.
- Page read/write paths include `qcom_spi_read_page_raw()`, `qcom_spi_read_page_ecc()`, `qcom_spi_read_page_oob()`, `qcom_spi_program_raw()`, `qcom_spi_program_ecc()`, and `qcom_spi_program_oob()`.
- `qcom_spi_cmd_mapping()`, `qcom_spi_send_cmdaddr()`, and `qcom_spi_io_op()` implement opcode-level SPI-NAND command handling.

## Control Flow
Probe sets up clocks (`core`, `aon`, `iom`), maps the NAND register resource, maps it for DMA, allocates common BAM/NAND structures, writes SPI config/address/busy-wait registers through descriptors, registers the pipelined ECC engine, and exposes a one-CS SPI memory controller with dual/quad mode bits.

ECC initialization derives codewords per page, validates step size and strength, allocates OOB buffer, re-allocates BAM transaction capacity for the page geometry, fills raw and ECC register configs, installs OOB layout, and initializes erased-page status registers. `prepare_io_req` sets `page_rw`, `oob_rw`, and `raw_rw` for later `spi_mem` operations; `finish_io_req` updates MTD ECC statistics.

For `spi_mem` execution, page operations are detected from bus widths/address shape. Page read paths build BAM descriptors for raw/ECC/OOB codeword reads, submit them, and inspect flash/ECC status. Program paths cache page data at `PROGRAM_LOAD`, then execute raw/ECC/OOB writes on `PROGRAM_EXECUTE`. Non-page commands handle reset, read ID, get/set feature, write-enable, erase, and read command/address sequencing.

## State And Persistence Behavior
The driver uses in-memory QPIC NAND controller state, BAM transaction state, ECC context stored in `nand->ecc.ctx.priv`, and buffers allocated for data/OOB. Current operation flags and cached command/address/data pointers in `qpic_spi_nand` persist only across the SPI-NAND multi-op sequence needed to load data then execute program/read. ECC statistics are accumulated into MTD stats after read requests.

## Dependencies And Integration Points
This driver depends on `linux/mtd/nand-qpic-common.h`, SPI memory, SPI-NAND/MTD NAND ECC APIs, DMA mapping, QCOM BAM/ADM DMA helpers, clocks, OF match data, and platform resources. It is not a generic SPI controller in practice; it is a SPI-NAND memory controller with ECC-aware `spi_mem` operations.

## Risks
- ECC support is limited to 512-byte step size and 4-bit or 8-bit strength.
- OOB/bad-block-marker handling includes a TODO workaround duplicating the bad block marker until SPI-NAND supports a single-byte marker.
- The code casts feature data through `u32 *` and copies fixed 4-byte buffers for feature/read-id paths; endianness and size assumptions need hardware coverage.
- BAM transaction allocation is resized during ECC init; failure paths must avoid leaving stale transaction state.
- Page operation detection is specialized and may reject valid future SPI-NAND op shapes.
- `qcom_spi_write_page()` currently caches data for `PROGRAM_LOAD` but otherwise returns after command mapping; sequencing depends on later `PROGRAM_EXECUTE`.

## Test Signals
- Probe on `qcom,ipq9574-snand` with all three clocks and BAM-capable resources.
- SPI-NAND reset, read ID, get/set feature, write-enable, erase, read, program-load, and program-execute operations.
- ECC init with default/user/required 4-bit and 8-bit strengths, plus unsupported strengths/step sizes.
- Raw, ECC, and OOB read/write modes and MTD ECC statistic updates.
- Bad block marker placement and erased-page detection.
- BAM descriptor submission failures and cleanup/unmap paths.
