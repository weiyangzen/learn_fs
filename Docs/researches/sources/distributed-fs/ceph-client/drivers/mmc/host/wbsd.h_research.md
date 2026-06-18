# sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.h

## Purpose
This header defines the Winbond W83L51xD SD/MMC controller register map, bit definitions, DMA sizing, and the private `struct wbsd_host` used by `wbsd.c`.

## Important APIs, types, and definitions
- Super I/O configuration constants include `LOCK_CODE`, `WBSD_CONF_*` register offsets, `DEVICE_SD`, and card-detect pin configuration values.
- Runtime I/O register offsets include `WBSD_CMDR`, `WBSD_DFR`, `WBSD_EIR`, `WBSD_ISR`, `WBSD_FSR`, `WBSD_IDXR`, `WBSD_DATAR`, and `WBSD_CSR`.
- Interrupt enable/status masks define card detect, FIFO threshold, CRC, timeout, program/busy end, and transfer-complete events.
- FIFO and CSR masks describe FIFO empty/full threshold state, memory-stick LED/write-protect/card-present bits, and power control.
- Indexed SD register offsets describe clock, block size, timeouts, setup, DMA, FIFO enable, status, response bytes, CRC status, and ISR mirror registers.
- `struct wbsd_host` is the central private state shared by the implementation.

## Control flow relevance
The header has no executable flow, but its constants directly drive every hardware access path in `wbsd.c`. Request submission uses `WBSD_CMDR`; response parsing uses `WBSD_IDX_RESP*` and `WBSD_IDX_RSPLEN`; data setup uses block-size, timeout, setup, FIFO, and DMA indices; IRQ handling uses `WBSD_ISR` masks; card-detect and write-protect checks use `WBSD_CSR` masks.

## State and persistence
`struct wbsd_host` holds all volatile driver state: MMC host pointer, spinlock, flags (`WBSD_FCARD_PRESENT`, `WBSD_FIGNORE_DETECT`), active request, accumulated ISR, current SG entry/count/offset/remain, DMA buffer and bus address, first-error flag, clock, bus width, config/unlock data, chip ID, I/O base, IRQ, DMA channel, work structs, and ignore timer. There is no persistent state.

## Dependencies and integration points
The struct embeds Linux kernel types from the implementation context: `struct mmc_host`, `spinlock_t`, `struct mmc_request`, `struct scatterlist`, `dma_addr_t`, `struct work_struct`, and `struct timer_list`. It is private to the Winbond host driver rather than a public subsystem ABI.

## Risks and edge cases
- Hardware semantics are encoded as raw numeric constants; mistakes in bit use can affect power, card detect, FIFO, or DMA behavior.
- `WBSD_DMA_SIZE` fixes the DMA bounce buffer at 64 KiB and matches request-size limits in `wbsd.c`.
- `WBSD_IDX_RESP*` ordering is critical for correct short and long response assembly.
- The header uses older C style pointer spacing but is otherwise isolated.

## Test signals
Validation is indirect through `wbsd.c`: register access correctness can be observed through successful probe/config, card-detect state changes, command responses, FIFO transfer progress, DMA completion counts, write-protect state, and interrupt classification.
