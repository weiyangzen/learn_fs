# Research: sources/distributed-fs/ceph-client/include/linux/pata_arasan_cf_data.h

Purpose: `pata_arasan_cf_data.h` provides platform data for the Arasan CompactFlash PATA host controller.

Important APIs/types/functions: `struct arasan_cf_pdata` carries `cf_if_clk` encoded by `CF_IF_CLK_*` constants from 25 MHz through 200 MHz and a `quirk` bitmask with `CF_BROKEN_PIO`, `CF_BROKEN_MWDMA`, and `CF_BROKEN_UDMA`. `set_arasan_cf_pdata()` stores the platform data pointer into `pdev->dev.platform_data`.

Control flow and state: board/platform setup initializes static platform data, calls the setter, and the PATA driver consumes clock and quirk information during probe to choose transfer modes. State persists as platform-device data for the device lifetime.

Dependencies and integration points: depends on `linux/platform_device.h` and integrates with the Arasan CF low-level ATA driver, platform board files, and libata mode selection.

Risks and test signals: risks include dangling platform-data lifetime, invalid clock encoding, and underdeclared quirks causing unsupported transfer modes. Tests should probe with each quirk combination, verify mode masks, and validate board data survives device probe/remove.
