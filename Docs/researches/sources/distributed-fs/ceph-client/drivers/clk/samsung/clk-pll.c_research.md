# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-pll.c

Purpose: Samsung common clock framework PLL implementation. It turns `struct samsung_pll_clock` descriptors into CCF `clk_hw` providers and implements PLL-family-specific recalc, determine-rate, set-rate, enable/disable, and lock-wait behavior.

Important APIs/types/functions: private `struct samsung_clk_pll`; `samsung_get_pll_settings()`; `samsung_pll_determine_rate()`; `samsung_pll_lock_wait()`; `samsung_pll3xxx_enable()/disable()`; per-family ops for PLL2126, 3000, 35xx/142xx/A9FRACM, 36xx/2650, 0822x/0831x, 45xx, 46xx/1460x, 6552/6553, 2550x/2550xx, 2650x/2650xx, 531x/4311, 1031x, and A9FRACO; `_samsung_clk_register_pll()`; `samsung_clk_register_pll()`.

Control flow: registration allocates a PLL object, copies optional rate tables, selects `clk_ops` by `enum samsung_pll_type`, maps control/lock registers from the provider base, registers the hardware clock, and stores it by ID. Runtime recalc paths read hardware bitfields and compute output rates; set-rate paths find an exact table entry, update PMS/K/AFC/MFR/MRR/VSEL fields, program lock time, write registers, and poll the lock bit when active.

State and persistence behavior: persistent state is hardware PLL registers plus an in-memory copied rate table. This file does not save PM state directly; Samsung CMU code saves/restores relevant registers. Lock waiting intentionally uses atomic polling rather than timekeeping for early boot and suspend contexts.

Dependencies/integration points: Linux CCF, relaxed MMIO, atomic iopoll, Samsung `clk.h` descriptors, `clk-pll.h` rate-table macros, and SoC files that pass PLL arrays into `samsung_clk_register_pll()`.

Risks: dense hardware-specific bitfields make family mapping fragile; missing rate tables expose recalc-only PLLs; rate tables must be descending and sentinel-terminated; bypass/disable ordering is critical for PLLs such as A9FRACO. The local source also shows duplicated `pr_err()` text in `samsung_pll35xx_set_rate()`, a build/review signal for this copy.

Test signals: build all Samsung PLL users, boot representative SoCs, inspect `clk_summary`, exercise valid/invalid `clk_set_rate()` calls, and run suspend/resume with PLL lock verification.
