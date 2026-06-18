# sources/distributed-fs/ceph-client/drivers/fpga/microchip-spi.c

Purpose: FPGA manager for Microchip PolarFire programming over slave SPI. It parses the Microchip bitstream header to find the actual bitstream and data size, enters ISC/program mode, writes fixed 16-byte frames, and exits program mode.

Important APIs and functions: `struct mpf_priv` stores the SPI device, program-mode flag, and aligned single-byte TX/RX buffers for status commands. `mpf_read_status` performs two status reads and treats SPI violation/error bits as `-EIO`. `mpf_ops_parse_header` discovers lookup-table blocks for component sizes and bitstream start, setting `info->header_size` and `info->data_size`. Manager ops include `mpf_ops_state`, `mpf_ops_write_init`, `mpf_ops_write`, and `mpf_ops_write_complete`.

Control flow: the manager requests an initial 71-byte header and asks the core to skip the parsed header. Header parsing may return `-EAGAIN` to request a larger buffer. Write-init rejects partial reconfiguration, enables ISC with a readback status word, sends frame-init program-mode command, and marks `program_mode`. Write validates 16-byte frame alignment and sends each frame behind an `MPF_SPI_FRAME` command after status polling. Write-complete disables ISC, delays, sends release, and clears `program_mode`.

State and persistence: state is the manager private structure and the hardware status/program mode. Header-derived `info->header_size` and `info->data_size` steer the manager core. The driver does not track a persistent image version; configuration persistence is device-dependent.

Dependencies and integration points: depends on SPI, FPGA manager header parsing support, unaligned little-endian helpers, iopoll, OF compatible `microchip,mpf-spi-fpga-mgr`, and SPI ID `mpf-spi-fpga-mgr`.

Risks and test signals: risks include malformed lookup tables, accumulating `info->data_size` if parse is re-entered without reset, status polling without sleep interval, frame-size strictness, and state reporting unknown whenever status is nonzero. Test signals are parser behavior on short headers, correct header skip/data size, successful ISC enable readback, frame write counts, final release command, and injected SPI violation returning `-EIO`.
