# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm.h

## Purpose
Defines the common OMAP2+ PRM interface, feature flags, timeout constants, standardized reset-source IDs, and the `prm_ll_data` callback table used to dispatch generic PRM operations to SoC-specific implementations.

## APIs, Flow, And State
Exports global state `prm_base`, `prm_features`, and `prm_reboot_mode`, plus init APIs `omap_prcm_init()` and `omap2_prcm_base_init()`. The `struct prm_reset_src_map` translates hardware reset bits to standardized reset-source bits. `struct prm_ll_data` contains callbacks for reset source reads, context-loss handling, late init, hardreset control, system reset, wake IRQ clearing, and VP transaction completion. Generic wrappers include `omap_prm_assert_hardreset()`, `omap_prm_deassert_hardreset()`, `omap_prm_reset_system()`, `omap_prm_clear_mod_irqs()`, and VP helpers.

## Dependencies And Integration
Includes `prcm-common.h`; implemented primarily by `prm_common.c` and populated by `prm2xxx.c`, `prm3xxx.c`, `prm33xx.c`, and `prm44xx.c`. Used by hwmod, powerdomain, clockdomain, voltage, watchdog, and platform reboot paths.

## Risks And Test Signals
This is a low-level dispatch interface with weak runtime checking: missing callbacks produce warnings or `-EINVAL`, and reset paths may not return. Test signals are callback registration ordering, hardreset deassert timeout behavior, watchdog reset-source reads, and platform reboot modes.
