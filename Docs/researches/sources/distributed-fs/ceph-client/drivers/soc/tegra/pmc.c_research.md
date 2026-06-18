# sources/distributed-fs/ceph-client/drivers/soc/tegra/pmc.c

## Purpose

`pmc.c` is the central NVIDIA Tegra Power Management Controller driver. It handles early PMC register access, powergate control, generic PM domains, core-domain OPP/regulator synchronization, CPU powergate helpers, I/O pad deep-power-down and voltage pinconf, wake IRQ routing, suspend wake-status handling, PMC clocks, reboot/power-off scratch programming, reset reason sysfs, USB sleepwalk regmap exposure, and SoC data tables for Tegra20 through Tegra264.

## Important APIs, Types, and Functions

Public/exported APIs include `devm_tegra_pmc_get()`, `tegra_pmc_powergate_power_on/off()`, legacy global `tegra_powergate_power_on/off()`, `tegra_pmc_powergate_remove_clamping()`, `tegra_powergate_remove_clamping()`, `tegra_pmc_powergate_sequence_power_up()`, `tegra_powergate_sequence_power_up()`, CPU helpers `tegra_pmc_cpu_is_powered()`, `tegra_pmc_cpu_power_on()`, `tegra_pmc_cpu_remove_clamping()`, I/O pad helpers `tegra_pmc_io_pad_power_enable/disable()` and global wrappers, suspend helpers under PM sleep, and `tegra_pmc_core_domain_state_synced()`.

Key private structures are `struct tegra_pmc`, `struct tegra_pmc_soc`, `struct tegra_powergate`, `struct tegra_pmc_core_pd`, `struct tegra_io_pad_soc`, `struct tegra_io_pad_vctrl`, `struct tegra_pmc_regs`, and `struct tegra_wake_event`. SoC descriptors encode powergate names, CPU gate IDs, pad tables, wake events, reset strings, register offsets, TrustZone-only possibility, clock support, USB sleepwalk support, and per-SoC callbacks.

## Control Flow

`tegra_pmc_early_init()` runs at early init, maps PMC MMIO, matches SoC data, detects TrustZone-only access on Tegra210-like systems by scratch write/read probing, initializes the powergate availability bitmap, and applies interrupt polarity. Later the built-in platform driver probes, parses suspend DT properties, remaps normal resources, maps wake/aotag/scratch apertures or aliases them for single-aperture SoCs, registers reboot and sys-off handlers, caches `pclk` rate with a clock notifier, initializes SoC-specific PMC state, configures thermal trip scratch registers, adds reset sysfs files, registers pinctrl, regmap, powergates/genpd, IRQ domain, replaces the early mapping, registers PMC clocks, initializes suspend, sets wake filters, and creates debugfs `powergate`.

Powergate sequencing asserts resets, toggles powergate state through Tegra20 or Tegra114+ register protocols, temporarily lowers clock rates to a safe 100 MHz before enabling, removes clamps, deasserts resets, runs Tegra210 MBIST workaround if needed, disables clocks if requested, and restores rates. Power-down reverses this through reset assertion, clock disable, powergate off, and rate restoration. OF powergate nodes become generic PM domains and are removed from legacy direct API availability.

I/O pad operations find pad metadata, optionally program DPD sample timing from `pclk`, write OFF/ON request codes, poll status, and expose low-power mode and power-source pinconf. Wake IRQ flow allocates a hierarchical IRQ domain, maps PMC wake IDs to parent GIC IRQs or GPIO/simple wake endpoints, programs wake masks/types, handles dual-edge wake polarity flipping on suspend, reads wake status on resume, and replays mapped IRQs through hard IRQ work.

## State and Persistence Behavior

The singleton `pmc` persists from early boot. It caches MMIO bases, clock rate, suspend timers and mode, LP0 vector, available powergate bitmap, lock, pinctrl and IRQ domain, wake bitmaps, wake status, reboot notifier, syscore state, and SoC descriptor. Hardware state persists in PMC registers: powergate state, clamp state, wake masks/types/status, scratch reboot reason, reset source/level, DPD pad state, pad voltage controls, thermal reset scratch values, and PMC clock mux/gate state.

No file-backed persistence is used, but scratch registers intentionally communicate reboot mode to firmware/bootloader and may survive warm resets depending on hardware. `core_domain_state_synced` becomes true only after driver sync-state for SoCs that support the core domain and is used by regulator couplers to relax boot voltage limits.

## Dependencies and Integration Points

The driver integrates with OF platform resources, ARM SMCCC, clocks and clock providers, resets, generic PM domains, OPP/regulators, pinctrl/pinconf, IRQ domains, wake IRQ hierarchy, syscore suspend/resume, reboot/sys-off, power supply, debugfs, regmap, USB sleepwalk consumers, Tegra clock MBIST workaround, Tegra fuse/APBMISC/common suspend helpers, and DT bindings for Tegra powergates, I/O pads, GPIOs, and interrupts.

## Risks and Edge Cases

This driver is high blast-radius hardware code. The global singleton and early mapping handoff require careful ordering; public APIs can be called before full platform probe. TrustZone-only detection writes scratch registers during early boot and must restore them. Powergate sequencing depends on correct reset arrays, clocks, rate restoration, and SoC-specific clamp behavior; a failure can leave devices reset, clocks changed, or domains unavailable. `tegra_pmc_powergate_sequence_power_up()` allocates `pg->clk_rates` but on that allocation failure attempts `kfree(pg->clks)` even though `pg->clks` was never allocated in that path, which is harmless for NULL but signals a stale cleanup pattern.

Wake handling is subtle for dual-edge events: suspend samples raw state, flips polarity for asserted dual-edge wake sources, clears status, and later replays wake IRQs. Incorrect wake event tables or parent IRQ mappings can break suspend/resume. SoC tables are large and offset-heavy; wrong DPD/status/vctrl offsets can cut power to active pads or misreport voltage. `tegra_pmc_sync_state()` marks core-domain sync only when DT contains `core-domain` and the SoC supports it, so regulator couplers must tolerate older DTs staying unsynced.

## Test Signals

Validation should cover early init and probe on every compatible, TrustZone-only Tegra210 access, reset reason/level sysfs, reboot commands `recovery`, `bootloader`, and `forced-recovery`, power-off handler on Nexus 7 charger mode, legacy and genpd powergate on/off, reset/clamp sequencing, MBIST workaround paths, pclk rate-change notifier locking, I/O pad low-power and 1.8V/3.3V pinconf, wake IRQ set_wake/type for Tegra210 and Tegra186+, SC7 suspend/resume wake replay, USB sleepwalk regmap access ranges, PMC clock output mux/gate operations, and `sync_state` regulator synchronization.
