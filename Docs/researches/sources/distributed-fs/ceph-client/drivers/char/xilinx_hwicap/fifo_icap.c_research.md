<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.c -->
# sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.c

Purpose: Implements the FIFO-backed Xilinx HWICAP backend. It streams configuration and readback words through hardware write/read FIFOs, size/control/status registers, and polled occupancy/vacancy checks.

Important APIs/types/functions: Exports `fifo_icap_get_status()`, `fifo_icap_set_configuration()`, `fifo_icap_get_configuration()`, `fifo_icap_reset()`, and `fifo_icap_flush_fifo()`. Helpers wrap FIFO and control register operations: `fifo_icap_fifo_write()`, `fifo_icap_fifo_read()`, `fifo_icap_set_read_size()`, `fifo_icap_start_config()`, `fifo_icap_start_readback()`, `fifo_icap_busy()`, `fifo_icap_write_fifo_vacancy()`, and `fifo_icap_read_fifo_occupancy()`.

Control flow: write first rejects a busy ICAP, then repeatedly waits for write FIFO vacancy, pushes words, starts configuration after each filled burst, and finally waits for done. Read rejects busy ICAP, breaks requests into `XHI_MAX_READ_TRANSACTION_WORDS` chunks, programs read size, starts readback, waits for read FIFO occupancy, and drains words into the caller buffer. Reset toggles the software reset bit; flush toggles FIFO clear.

State and persistence: software state is only local loop counters; persistent state is in the ICAP hardware FIFOs/control registers. Parent driver locking serializes calls.

Dependencies and integration: used by `xilinx_hwicap.c` for Device Tree compatible `xlnx,xps-hwicap-1.00.a`. It relies on `xilinx_hwicap.h` status bits/retry count and big-endian MMIO accessors.

Risks: retry counters are shared across nested wait loops in each transfer and are not reset per FIFO wait, making very large or slow operations sensitive to `XHI_MAX_RETRIES`. `fifo_icap_set_configuration()` starts configuration after each FIFO fill and only reports `remaining_words` mismatch, so done-timeout paths require careful review. Interrupt registers are defined but the driver is purely polled.

Test signals: exercise FIFO backend configuration and readback, transfer sizes over FIFO depth and over the read-transaction limit, busy hardware rejection, timeout handling, reset/flush effects, and parent open/read/write byte-buffering paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xilinx_hwicap/fifo_icap.c -->
