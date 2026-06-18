# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.h Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio_ops.h

### Purpose
`sdio_ops.h` declares internal SDIO transport helpers and a small predicate for commands that keep SDIO I/O busy.

### Important APIs, Types, And Functions
It declares `mmc_send_io_op_cond()`, `mmc_io_rw_direct()`, `mmc_io_rw_extended()`, `sdio_reset()`, and `sdio_irq_work()`. The inline `sdio_is_io_busy()` returns true for CMD53 and for CMD52 operations except accesses to `SDIO_CCCR_ABORT` or `SDIO_CCCR_SUSPEND`.

### Control Flow
There is no standalone runtime flow beyond the inline predicate. The predicate decodes the address from command arguments and classifies SDIO I/O commands for host/core busy handling.

### State, Persistence, And Dependencies
No state is stored. It depends on `linux/types.h`, SDIO constants, and opaque `mmc_host`, `mmc_card`, and `work_struct`.

### Integration Points
SDIO attach, CIS parsing, IRQ handling, exported I/O APIs, and host/core request handling include this header for transport operations and busy classification.

### Risks
The inline predicate must stay aligned with SDIO command argument layout; incorrect classification can break retune, runtime PM, or command scheduling around SDIO I/O. Prototype changes affect many MMC core files.

### Test Signals
Compile coverage plus tests for CMD52 abort/suspend versus normal CMD52 and CMD53 paths validate the predicate and declarations.
