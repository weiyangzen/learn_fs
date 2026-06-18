<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9462_2p1_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9462_2p1_initvals.h

Purpose: Provides the AR9462 2.1 revision delta tables. It reuses most AR9462 2.0 initialization data through macros and replaces only the MAC core, baseband postamble, and SoC preamble arrays needed for the later revision.

Important APIs/types/functions: This file defines no functions or types. Its direct data exports are `ar9462_2p1_mac_core`, `ar9462_2p1_baseband_postamble`, and `ar9462_2p1_soc_preamble`. Macro aliases map the 2.1 names for MAC postamble, baseband core, radio core/postamble, SoC postamble, radio system-to-antenna postamble, normal/mixed/no-XLNA/5G-XLNA RX gain tables, mixed RX gain auxiliary baseband tables, low/high/mixed TX gain tables, fast-clock table, Japan FIR, and PCIe clock-request table to their AR9462 2.0 equivalents.

Control flow: `ar9003_hw_init_mode_regs()` selects this header when `AR_SREV_9462_21(ah)` is true. The flow mirrors AR9462 2.0 but resolves many selected symbols to 2.0 arrays at compile time. Runtime TX gain modes 0, 1, and 4 and RX gain modes 0 through 3 use the same helper paths as 2.0, with aliases supplying the table bodies. The 2.1-specific `ar9462_2p1_baseband_postamble` and `ar9462_2p1_soc_preamble` are written during normal AR9003 split INI programming.

State and persistence behavior: The header stores immutable register matrices only. Runtime state is the `struct ath_hw` INI pointers set in `ar9003_hw.c` and the resulting hardware register state after `ar9003_hw_process_ini()` writes them. Because most symbols alias to 2.0, a 2.0 table change can persist into 2.1 hardware behavior without edits to this file.

Dependencies: Strongly depends on `ar9462_2p0_initvals.h` being included in the same translation unit before these aliases are used. It also depends on the AR9003 programming path for mixed/XLNA RX gain auxiliary arrays and PCIe PLL power-save arrays, even though those arrays physically live in the 2.0 header.

Integration points: This file is the revision-selection layer for AR9462 2.1. It plugs into the same MAC/baseband/radio/SoC, RX gain, TX gain, fast-clock, Japan FIR, system-to-antenna, and PCIe power-save integration points as 2.0 while overriding only the tables required by the 2.1 silicon revision.

Risks: The heavy aliasing makes dependency ordering and review clarity the main risks. A reader may assume a 2.1 symbol is locally defined when it actually expands to 2.0 data, and changes to `ar9462_2p0_initvals.h` can alter 2.1 behavior. The small number of local override tables must still preserve exact modal column layout; a mismatch in `ar9462_2p1_baseband_postamble` would affect all mode-specific PHY programming for this revision.

Test signals: Build validation should catch missing 2.0 aliases. Runtime validation should cover AR9462 2.1 probe/reset, both bands and HT widths, fast-clock channels, TX gain modes inherited from 2.0, RX gain modes 0 through 3 including mixed and XLNA auxiliary writes, PCIe PLL power-save D0/D3 paths, and comparison against AR9462 2.0 behavior to confirm that only intended revision deltas changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9462_2p1_initvals.h -->
