# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.c

### Purpose
`sdio_ops.c` implements low-level SDIO command helpers for CMD5, CMD52, CMD53, and SDIO reset. It is the transport layer below SDIO card attach and exported function-driver I/O APIs.

### Important APIs, Types, And Functions
The APIs are `mmc_send_io_op_cond()`, `mmc_io_rw_direct()`, `mmc_io_rw_extended()`, and `sdio_reset()`. `mmc_io_rw_direct_host()` is the host-based CMD52 helper used before a `struct mmc_card` exists.

### Control Flow
CMD5 polls up to 100 times with 10 ms delays unless probing with OCR zero, returning the R4 OCR from the SPI/native response slot. CMD52 validates function number and 17-bit address, encodes read/write and RAW flag, submits the command, decodes native R5 error/function/out-of-range bits, and returns the byte response. CMD53 validates address, builds block or byte mode arguments, maps the caller buffer into one or more scatterlist entries based on `host->max_seg_size`, submits pre/post request hooks around `mmc_wait_for_req()`, decodes command/data/R5 errors, and frees dynamic scatterlists. Reset reads CCCR_ABORT if possible, sets bit 3, and writes it back.

### State, Persistence, And Dependencies
The helpers mutate only command/request structures, host pre/post request state, and SDIO CCCR registers. Dependencies include scatterlists, SDIO/MMC constants, generic command submission, host limits, and card/host response layout helpers.

### Integration Points
`sdio.c` uses CMD5 and reset during attach/reinit. `sdio_io.c`, `sdio_cis.c`, `sdio_bus.c`, and `sdio_irq.c` build higher-level APIs on CMD52/CMD53.

### Risks
SPI response slots differ from native response slots. CMD53 scatterlist splitting by `max_seg_size` must match host DMA expectations and preserve buffer lifetime through pre/post hooks. Byte mode uses `blocks == 0` but sets `data.blocks` to 1 because host drivers expect at least one block. Reset before a card object exists depends on the host helper, not `mmc_card`.

### Test Signals
Exercise CMD5 probe and ready timeout, CMD52 invalid function/address and R5 errors, CMD53 byte and block mode, multi-segment DMA splitting, SPI/native response decoding, reset on cards that fail the initial abort read, and host pre/post request paths.
