# sources/distributed-fs/ceph-client/drivers/mtd/devices/powernv_flash.c

Purpose: exposes PowerNV OPAL PNOR flash as a Linux MTD NOR device. Actual flash access is delegated to firmware OPAL async calls.

Important APIs/types/functions: `struct powernv_flash` embeds `mtd_info` and OPAL flash id. `enum flash_op` selects read/write/erase. `powernv_flash_async_op()` is the shared operation engine. MTD callbacks are `powernv_flash_read()`, `powernv_flash_write()`, and `powernv_flash_erase()`. Probe helpers are `powernv_flash_set_driver_info()` and `powernv_flash_probe()`.

Control flow: probe allocates state, reads `ibm,opal-id`, reads erase size and total size from OF properties, fills MTD callbacks/geometry/name, and registers the device. Each operation obtains an OPAL async token, starts the requested firmware operation with physical buffer address when needed, waits for completion if OPAL reports async completion, maps OPAL result codes to errno, updates retlen on success, and releases the token.

State and persistence: persistent state is platform PNOR content managed by firmware. Runtime state is minimal: OPAL id and registered MTD. OPAL owns flash serialization and may return busy if service processor or firmware activity conflicts.

Dependencies/integration: PowerNV OPAL API, OF properties `ibm,opal-id`, `ibm,flash-block-size`, and `reg`, MTD core, and platform bus matching `ibm,opal-flash`.

Risks: interruptible wait handling is subtle: if interrupted, the driver must still wait for OPAL completion so the MTD buffer is not freed while firmware is using it. `OPAL_BUSY` is intentionally surfaced so userspace can notice possible flash changes. Buffers passed to OPAL must be physically addressable.

Test signals: OF property absence, OPAL token failure including interrupt conversion, successful async read/write retlen, erase failure setting `fail_addr`, OPAL_BUSY propagation, and unregister on platform remove.
