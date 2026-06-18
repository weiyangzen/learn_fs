## sources/distributed-fs/ceph-client/arch/mips/ath25/board.c

Purpose: provides shared ATH25 boot hooks, board/radio configuration discovery in flash, platform memory/time/IRQ dispatch selection, and halt behavior.

Important APIs and functions: `ath25_find_config()` scans mapped flash for board and radio configuration and populates `ath25_board`. `plat_mem_setup()`, `plat_irq_dispatch()`, `plat_time_init()`, `get_c0_compare_int()`, and `arch_init_irq()` are MIPS platform hooks. Helpers `find_board_config()`, `find_radio_config()`, `check_board_data()`, and `check_radio_magic()` implement the flash heuristics.

Control flow: `plat_mem_setup()` installs halt/poweroff, selects AR5312 or AR2315 memory setup, then disables watchpoints. `ath25_find_config()` maps the flash window, searches backward near the end for board data magic, optionally accepts broken board data using nearby radio magic, copies board config into RAM, searches forward for radio config, copies radio data into the same buffer with offset preservation, and patches blank radio MAC from board data. IRQ/time hooks dispatch to family-specific implementations.

State and persistence: global `ath25_board.config` and `.radio` point to allocated RAM copies. Broken board data may get randomized in-memory MACs, but flash is not written. `_machine_halt` and `pm_power_off` are set.

Dependencies and integration: depends on ATH25 platform data structures, AR5312/AR2315 hooks, memblock setup, MIPS IRQ/time, flash ioremap, and Ethernet address helpers.

Risks: flash scanning intentionally searches a possibly larger region than physical flash, relying on aliasing. Broken board data fixups are temporary RAM-only. Missing board/radio config causes warnings and `-ENODEV`, which can suppress wireless registration. `ath25_halt()` disables IRQs and calls `unreachable()`.

Test signals: boot should log radio config offset or warnings. WMAC MAC addresses should be valid. Platform hooks should select the correct family on CPU type, and CP0 compare IRQ should be legacy compare.
