# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-io.h

Purpose: provides inline MMIO helpers for ddbridge devices and links.

Important APIs/types/functions: `ddbreadl()`/`ddbwritel()` access device registers, `ddblreadl()`/`ddblwritel()` access link-tagged registers through the same mapped BAR, `ddbcpyto()`/`ddbcpyfrom()` copy to and from MMIO buffers, and `safe_ddbreadl()` detects all-ones MMIO read failures and logs an error.

Control flow: all runtime files use these helpers to access hardware registers, I2C buffers, DMA tables, interrupts, SPI flash, LNB control, MCI commands, and temp monitor registers.

State and persistence: no state; operations directly read/write memory-mapped hardware.

Dependencies/integration: includes `<linux/io.h>` and `ddbridge.h`.

Risks and test signals: register offsets must already include any required link tag; misuse can affect the wrong link. `safe_ddbreadl()` only catches `~0`, not stale or semantically invalid values. Test by checking probe logs, IRQ counters, I2C transactions, and register dump attributes on real hardware.
