# sources/distributed-fs/ceph-client/sound/soc/sof/mediatek/mt8195/mt8195-loader.c

Purpose: Implements MT8195 HIFIxDSP boot and shutdown register sequencing.

Important APIs: `sof_hifixdsp_boot_sequence()` writes `DSP_ALTRESETVEC`, asserts RUNSTALL and STATVECTOR_SEL, toggles DReset/BReset with a 1 us delay, enables PDebug, and releases RUNSTALL. `sof_hifixdsp_shutdown()` asserts RUNSTALL and D/B reset.

Control flow and integration: `mt8195_run()` calls boot with `SRAM_PHYS_BASE_FROM_DSP_VIEW`; suspend and remove paths use shutdown before SRAM/clock poweroff.

State and persistence: Alters reset, runstall, alternate reset vector, stat-vector selection, and pdebug register state.

Risks: Reset polarity and delay are vendor-sequenced; reordering can prevent boot. PDebug must be enabled before crash diagnostics are useful. The boot vector assumes firmware is loaded at the DSP-view SRAM base.

Test signals: FW_READY after boot, debug register availability after boot, shutdown during suspend, and recovery after repeated run/shutdown cycles.
