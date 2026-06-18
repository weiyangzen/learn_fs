# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/main.c

Purpose: Shared mac80211 core initialization, registration, supported bands/rates, module parameters, DPLL mapping, and exported probe/release functions for CW1200 bus modules.

Important APIs and functions: Defines module parameters `macaddr`, `cw1200_sdd_path`, `cw1200_refclk`, `cw1200_power_mode`, and block-ack TID masks. Provides `cw1200_init_common`, `cw1200_register_common`, `cw1200_unregister_common`, `cw1200_dpll_from_clk`, `cw1200_core_probe`, and `cw1200_core_release`. `cw1200_ops` binds mac80211 callbacks to STA, scan, TX/RX, PM, and AP functions.

Control flow: Bus probe calls `cw1200_core_probe`, which allocates and initializes `ieee80211_hw`, stores bus/platform values, registers BH, loads firmware, waits for WSM startup, configures operational mode and multi-TX confirm, then registers with mac80211. Release disables IRQs, unregisters mac80211/BH/debugfs/queues/PM, and frees the hardware object.

State and persistence: Initializes `cw1200_common` fields, workqueues, delayed works, spinlocks, wait queues, WSM buffers, queue stats, TX queues, bands, permanent MAC address, and firmware/SDD overrides. Runtime state is not persistent beyond module/device lifetime.

Dependencies and integration: Integrates mac80211, cfg80211, firmware loading, WSM, queues, scan, STA/AP code, PM, debugfs, and bus modules through exported GPL symbols.

Risks: Error unwinding must keep BH/core lifetimes correct. Randomizing the lower MAC bytes when template bytes are zero is convenient but may surprise users. Static band tables are mutated before registration, so shared state must be treated carefully across re-registration. `cw1200_core_probe` sets `*core` before all initialization finishes and resets it on failure.

Test signals: Build and probe over each bus, mac80211 registration, firmware startup indication within 3 seconds, supported band exposure with/without 5 GHz, module parameter overrides, and clean unload after partial probe failures.
