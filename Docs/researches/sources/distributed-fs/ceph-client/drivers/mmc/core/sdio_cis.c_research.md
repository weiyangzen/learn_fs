# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_cis.c

### Purpose
`sdio_cis.c` reads and parses SDIO Card Information Structure tuples for the common function and individual SDIO functions. It extracts identity, revision, info strings, block size, max transfer rate, enable timeout, and preserves unknown/vendor tuples for function drivers.

### Important APIs, Types, And Functions
Public/internal APIs are `sdio_read_common_cis()`, `sdio_free_common_cis()`, `sdio_read_func_cis()`, and `sdio_free_func_cis()`. Tuple parsers include `cistpl_vers_1()`, `cistpl_manfid()`, `cistpl_funce_common()`, `cistpl_funce_func()`, `cistpl_funce()`, and dispatcher `cis_tpl_parse()`. `struct cis_tpl` maps tuple codes to minimum lengths and parsers.

### Control Flow
`sdio_read_cis()` reads the three-byte CIS pointer from CCCR/FBR space, walks tuples until 0xff/end, allocates storage for each tuple, reads tuple payload bytes with CMD52, parses known tuples, queues unknown or intentionally unparsed tuples, and advances the pointer. Common CIS data populates `card->cis`, card revision, and card info strings. Function CIS data populates `func->vendor`, `func->device`, revision, info strings, `func->max_blksize`, and `func->enable_timeout`; missing function vendor/device falls back to card CIS values. Function tuple lists are terminated by the common tuple list so drivers can see both.

### State, Persistence, And Dependencies
State is in allocated info-string arrays and linked `struct sdio_func_tuple` lists owned by the card or function. It depends on SDIO register constants, `mmc_io_rw_direct()`, `jiffies`, SDIO revision values, and MMC card/function structures.

### Integration Points
`sdio.c` calls common CIS reading before function initialization and function CIS reading inside `sdio_init_func()`. `sdio_bus.c` frees function CIS data on device release. Function drivers, including `sdio_uart.c`, inspect queued tuples for device-specific data.

### Risks
CIS parsing reads byte-by-byte and trusts tuple links enough to allocate `sizeof(*tuple) + tpl_link`; malformed cards can cause long reads, warnings, or memory pressure. The per-loop timeout is scoped inside the tuple loop and only affects unknown tuple warning behavior, not a global CIS traversal timeout. Function tuple lists share the common tuple tail, so free logic must stop before freeing card-owned tuples. Broken SDIO 1.1 CIS lengths are special-cased by downgrading parsing to SDIO 1.0 semantics.

### Test Signals
Use cards with valid common/function CIS, absent optional function vendor/device, unknown/vendor tuples, tuple 0x91 for UART/GPS, broken SDIO 1.1 FUNCE length, malformed short tuples, duplicate CIS reads, and cleanup after partial attach failure.
