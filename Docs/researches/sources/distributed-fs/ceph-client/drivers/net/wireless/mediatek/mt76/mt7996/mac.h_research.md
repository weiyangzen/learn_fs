# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/mac.h

Purpose: Provides the mt7996 MAC-facing header needed by the C files in this subset. It includes shared connac3 MAC definitions and defines packed DFS/radar pattern structures used when programming or interpreting radar detector parameters.

Important APIs and types: `struct mt7996_dfs_pulse` describes pulse constraints in host-friendly units and signed power thresholds: maximum width, maximum/minimum power, staggered PRI range, and constant-radar PRI range. `struct mt7996_dfs_pattern` is the packed hardware/firmware layout with enable/stagger flags, CR/STG pulse counts, pulse width, PRI ranges, reserved bytes, and minimum stagger PRI difference. The header includes `../mt76_connac3_mac.h`, exposing common RX/TX descriptor and radiotap decode definitions to mt7996 code.

Control flow: The header has no executable control flow. It shapes data passed to MAC/MCU radar handling code in `mac.c` and related mt7996 MCU implementation files. The `__packed` annotation on `mt7996_dfs_pattern` is a control-plane ABI decision: callers can serialize the structure without compiler-inserted padding.

State and persistence behavior: The header owns no runtime state. Its structures describe transient DFS/radar configuration or match data. Because the packed layout is part of the firmware/hardware command contract, changing fields or alignment would affect persistent driver-firmware compatibility even though the file itself stores nothing.

Dependencies and integration points: It is included by `init.c`, `mac.c`, and `main.c` in this subset, and by other mt7996 files that need connac3 MAC definitions or DFS pattern structures. The definitions integrate with cfg80211 DFS states, MCU RDD commands, and register/firmware layouts declared elsewhere.

Risks and edge cases: The structures use fixed-width integer fields and packed layout; any reordering, type widening, or removal of reserved bytes can break firmware interpretation. `mt7996_dfs_pulse` uses `int` for power values while `mt7996_dfs_pattern` uses small unsigned fields, so conversions must clamp and encode carefully in the producer code. The header guard is conventional and prevents duplicate definitions.

Test signals: Compile coverage of all mt7996 MAC/MCU files, static layout checks if available for `sizeof(struct mt7996_dfs_pattern)`, and runtime DFS/RDD tests that start radar detectors for FCC/ETSI/JP regions and verify firmware accepts the encoded pattern data.
