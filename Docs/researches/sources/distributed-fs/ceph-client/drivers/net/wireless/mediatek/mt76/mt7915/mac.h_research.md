# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mac.h

Purpose: MAC descriptor bit definitions and DFS radar specification structures shared by MT7915 MAC code.

Important definitions: TX-free descriptor masks for old/new formats, TX status fields for MPDU counts/noise/RCPI/retry/fail bytes, and `struct mt7915_dfs_pulse`, `struct mt7915_dfs_pattern`, `struct mt7915_dfs_radar_spec`.

Control flow: no executable flow. `mac.c` consumes the TX-free masks while parsing firmware notifications and uses DFS structures to build region-specific radar tables passed to MCU commands.

State and persistence: the header defines descriptor ABI state exchanged with firmware/hardware and packed DFS radar pattern data. The DFS structures encode regulatory detection parameters such as pulse width, power, PRI ranges, and staggered radar properties.

Dependencies and integration: includes `mt76_connac2_mac.h`; used by `mac.c`, `debugfs.c`, and init paths that need MAC/DFS declarations.

Risks: bit masks must match firmware descriptor versions exactly. Confusing V0/V3 TX-free fields can corrupt token release or retry accounting. DFS structures are packed, so field ordering and width are part of the MCU command payload contract.

Test signals: compile-time use across `mac.c`/`debugfs.c`, txfree parsing on descriptor versions 0 and 4, retry/failure stat accuracy, DFS radar setup command payload inspection, and sparse/endian checks for packed structures.
