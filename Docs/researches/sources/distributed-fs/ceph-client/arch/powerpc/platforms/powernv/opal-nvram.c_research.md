## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-nvram.c

### Purpose
`opal-nvram.c` implements the PowerNV `ppc_md` NVRAM hooks on top of OPAL read/write calls and initializes NVRAM partition scanning for logs/oops storage.

### Important APIs, Types, And Functions
The file provides `opal_nvram_size()`, `opal_nvram_read()`, `opal_nvram_write()`, `opal_nvram_init()`, and the arch initcall `opal_nvram_init_log_partitions()`.

### Control Flow
Boot discovers `ibm,opal-nvram`, reads its `#bytes` property, stores `nvram_size`, and installs read/write/size callbacks in `ppc_md`. Reads clamp offsets to the NVRAM size and call `opal_read_nvram()`. Writes clamp similarly, then loop on `OPAL_BUSY` and `OPAL_BUSY_EVENT`, using `mdelay()` when interrupts are off and `msleep()` otherwise; busy-event responses also poll OPAL events.

### State, Persistence, And Dependencies
Linux stores only the NVRAM size and platform callbacks. NVRAM contents persist in firmware-backed nonvolatile storage. Dependencies include OPAL NVRAM calls, `ppc_md`, device tree, delay APIs, and generic NVRAM partition/oops helpers.

### Integration Points
Generic PowerPC NVRAM users call through `ppc_md`. Partition scanning and oops partition setup happen as an arch initcall after callbacks are registered.

### Risks
Writes can spin for repeated busy statuses, including panic paths with interrupts disabled. All OPAL failures are collapsed to `-EIO`. The code assumes buffers passed to OPAL are physically addressable via `__pa()`.

### Test Signals
Exercise boundary reads/writes, offsets at and beyond end of NVRAM, OPAL busy and busy-event retry loops, panic/interrupt-disabled writes, missing `#bytes`, partition scanning, and OPAL error conversion.
