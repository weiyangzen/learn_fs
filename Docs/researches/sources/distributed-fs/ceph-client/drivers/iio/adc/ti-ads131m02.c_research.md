# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads131m02.c

Purpose: direct-mode SPI IIO driver for TI ADS131M02/M03/M04/M06/M08 24-bit differential ADCs, with input CRC, output CRC verification, optional external reference, optional hardware reset, and clock-source handling.

Important APIs/types/functions: `struct ads131m_configuration` describes per-variant channels, reset ACK, external reference support, and crystal support. `struct ads131m_priv` holds reusable full-frame SPI buffers, optimized message, scale values, config pointer, and a mutex. Protocol helpers include `ads131m_tx_frame_unlocked()`, `ads131m_read_reg_unlocked()`, `ads131m_write_reg_unlocked()`, `ads131m_check_status_crc_err()`, and `ads131m_verify_output_crc()`. `ads131m_adc_read()` and `ads131m_read_raw()` expose IIO raw/scale reads.

Control flow: probe selects variant data, creates a full-frame SPI message sized to channel count, enables `avdd`/`dvdd` and optional `refin`, enables the clock, resets via reset-control or SPI RESET, configures CLOCK for external reference or `clkin`/`xtal`, and enables CCITT input CRC in MODE. Reads send a NULL+CRC frame, inspect STATUS for prior CRC errors, verify output CRC over response and channel words, then sign-extend a 24-bit channel word.

State and persistence: scale numerator/denominator and `use_external_ref` are derived at probe and kept in memory. Hardware state is MODE/CLOCK register configuration and CRC state. Buffers are shared and protected by `lock`; there is no buffered capture path and no persistent storage.

Dependencies and integration: SPI, regulators, reset controller, common clock framework, crc-itu-t, IIO direct mode, and OF/SPI match tables for all ADS131M variants.

Risks: the command protocol is pipelined, so every register operation is multi-cycle and must stay mutex-serialized; hardware reset bypasses reset ACK identity validation; CRC mismatch returns `-EIO` but prior input CRC errors are only logged during data reads. Test signals include reset ACK mismatch, WREG ACK mismatch, CRC error injection, external-ref scale math, unsupported `xtal` on smaller packages, and raw reads for every channel count.
