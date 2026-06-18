# subset-b-004789 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2056.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2056.h

## Purpose
`radio_2056.h` is the N-PHY 2056 radio register map and channel-switch contract for the b43 Broadcom wireless driver. It defines SYN/TX/RX bank selectors, hundreds of symbolic offsets for synthesizer, transmit, receive, RSSI, PLL, LO generator, filter, amplifier, and calibration registers, and the `b43_nphy_channeltab_entry_rev3` layout consumed by N-PHY channel setup code.

## Important APIs, types, and constants
The bank selectors `B2056_SYN`, `B2056_TX0`, `B2056_TX1`, `B2056_RX0`, `B2056_RX1`, `B2056_ALLTX`, and `B2056_ALLRX` encode high address bits used with register offsets. The file exports power/select bit masks such as `B2056_LNA1_A_PU`, `B2056_RSSI_W1_SEL`, and `B2056_VCM_MASK`. `struct b43_nphy_channeltab_entry_rev3` combines radio programming values for both cores with `struct b43_phy_n_sfo_cfg` PHY bandwidth values. It declares `b2056_upload_inittabs()`, `b2056_upload_syn_pll_cp2()`, and `b43_nphy_get_chantabent_rev3()`.

## Control flow, state, and persistence
This header has no runtime control flow and no persisted state. Its constants are compiled into callers that write MMIO/radio registers. Channel table entries are immutable data contracts; register state lives in the device hardware after callers upload values.

## Dependencies and integration points
It depends on Linux integer types and `tables_nphy.h` for `b43_phy_n_sfo_cfg`. The declared functions are implemented elsewhere in the b43 N-PHY radio path and are integrated with channel switching, PLL setup, and initialization code.

## Risks and test signals
The file contains a duplicated block of 2056 bank/register definitions before the channel table struct. Values are identical, so builds tolerate it, but edits can diverge silently if one copy is changed. Tests should at least build N-PHY configurations with warnings enabled and exercise 2056 initialization/channel switching on supported 2.4/5 GHz devices. Review should validate register offsets against vendor dumps because mistakes manifest as radio misconfiguration rather than ordinary software failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2056.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2057.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2057.c

## Purpose
`radio_2057.c` provides static initialization tables and channel lookup tables for Broadcom 2057 radios used by N-PHY devices. It translates PHY revision/radio revision combinations into radio register writes and channel-specific PLL, LO, TX, RX, and PHY bandwidth programming values.

## Important APIs, types, and functions
The private `r2057_rev*_init` arrays hold `{ register, value }` pairs for radio revisions 4, 5, 5a, 7, 9, and 14. `RADIOREGS7`, `RADIOREGS7_2G`, and `PHYREGS` are initializer macros for the structures declared in `radio_2057.h`. Channel tables include `b43_nphy_chantab_phy_rev8_radio_rev5`, `b43_nphy_chantab_phy_rev17_radio_rev14`, and `b43_nphy_chantab_phy_rev16_radio_rev9`. The exported `r2057_upload_inittabs()` writes revision-specific init arrays with `b43_radio_write()`. `r2057_get_chantabent_rev7()` returns either a full `b43_nphy_chantabent_rev7` or compact 2 GHz `b43_nphy_chantabent_rev7_2g` pointer through output parameters.

## Control flow, state, and persistence
Initialization switches on `dev->phy.rev` and then refines by `dev->phy.radio_rev`; unsupported combinations trigger `B43_WARN_ON(!table)` and skip writes. Lookup clears both output pointers, selects the applicable table, scans linearly for `freq`, and leaves both pointers NULL on a missing channel. The only persistent effects are hardware radio register writes during initialization.

## Dependencies and integration points
The file includes `b43.h`, `radio_2057.h`, and `phy_common.h`. It is called from N-PHY setup and channel-switching paths in `phy_n.c`; channel entries carry `tables_nphy.h` SFO/PHY register values used alongside radio writes.

## Risks and test signals
Risk centers on revision matching, sparse channel coverage, and table provenance from MMIO dumps. Rev8 init data is present but disabled behind a TODO. `len` is assigned only inside supported cases, so preserving the existing `e_r7`/`e_r7_2g` guard pattern is important. Build tests should cover `CONFIG_B43_NPHY`; hardware or emulator tests should verify all supported channel frequencies for rev8/5, rev16/9, and rev17/14 return expected table pointers and do not regress RF calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2057.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2057.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2057.h

## Purpose
`radio_2057.h` is the public register map and data-structure interface for b43 N-PHY 2057 radio support. It gives meaningful names to common, core-0, core-1, TX, AFE, calibration, and revision-7-specific radio register offsets.

## Important APIs, types, and constants
The register constants cover PLL/VCO calibration, LOGEN, TX gain and mixer tuning, IPA/PAD/PGA paths, LNA/RXMIX/TIA/RXBB/RSSI blocks, RCCAL/RCAL status, override registers, and per-core TX IQ/TSSI controls. `R2057_VCM_MASK` defines the VCM field mask used by calibration code. `struct b43_nphy_chantabent_rev7` stores full 2.4/5 GHz channel programming values plus `struct b43_phy_n_sfo_cfg`; `struct b43_nphy_chantabent_rev7_2g` is a smaller 2 GHz-only variant. The file declares `r2057_upload_inittabs()` and `r2057_get_chantabent_rev7()`.

## Control flow, state, and persistence
This file contains no executable logic. It defines compile-time contracts for callers that read or write hardware registers. Any state changes occur in implementation files through radio register writes.

## Dependencies and integration points
It depends on `linux/types.h` and `tables_nphy.h`. `radio_2057.c` fills the structs, while N-PHY code uses these fields to program channel-specific radio and PHY values.

## Risks and test signals
The header is hardware-contract heavy: a wrong offset can corrupt unrelated RF blocks. The two channel-entry structures have similar field names but different layouts; caller code must distinguish them by which output pointer is non-NULL. Test signals include clean compilation for N-PHY paths, channel switching across 2.4 and 5 GHz on supported revisions, and register trace comparison against known-good vendor dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2057.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2059.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2059.c

## Purpose
`radio_2059.c` supplies initialization and channel-switch tables for 2059 radios used by b43 HT-PHY devices. It maps channel frequencies to radio synthesizer/RXTX fields and PHY bandwidth fields, and uploads revision-specific radio defaults.

## Important APIs, types, and functions
`r2059_phy_rev1_init` is a small `{ register, value }` array applied to PHY revision 1. `RADIOREGS` and `PHYREGS` populate `struct b43_phy_ht_channeltab_e_radio2059`. `b43_phy_ht_channeltab_radio2059` covers 2.4 GHz and 5 GHz channels, with comments noting values came from MMIO dumps and that channels 12 and 13 are outdated from older driver data. `r2059_upload_inittabs()` writes init entries to `R2059_ALL | register`, broadcasting to all radio cores. `b43_phy_ht_get_channeltab_e_r2059()` linearly searches by MHz frequency and returns NULL on miss.

## Control flow, state, and persistence
Initialization supports only `phy->rev == 1`; other revisions warn and return. Successful upload writes hardware radio state through `b43_radio_write()`. Channel lookup is read-only and uses immutable static table data.

## Dependencies and integration points
The file includes `b43.h` and `radio_2059.h`. HT-PHY initialization calls `r2059_upload_inittabs()` from `phy_ht.c`, and HT channel switching retrieves entries with `b43_phy_ht_get_channeltab_e_r2059()`.

## Risks and test signals
The main risks are stale table values, especially channels 2467 and 2472 called out in comments, and unsupported revisions silently doing only a warning. Broadcast writes through `R2059_ALL` assume all cores should receive the same init values. Build HT-PHY configurations, run channel lookup tests over the table frequencies, and compare register traces during HT channel changes against known-good hardware captures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2059.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2059.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2059.h

## Purpose
`radio_2059.h` defines the HT-PHY 2059 radio core selectors, selected register offsets, channel-entry structure, and exported functions used by b43 HT radio initialization and channel switching.

## Important APIs, types, and constants
`R2059_C1`, `R2059_C2`, `R2059_C3`, and `R2059_ALL` select individual or all radio cores. The named offsets cover RCAL/RCCAL, RFPLL control, XTAL config, and calibration status. `struct b43_phy_ht_channeltab_e_radio2059` stores a channel frequency, 21 radio programming fields, and a `struct b43_phy_ht_channeltab_e_phy` block. The exported functions are `r2059_upload_inittabs()` and `b43_phy_ht_get_channeltab_e_r2059()`.

## Control flow, state, and persistence
No executable code is present. The file defines immutable compile-time contracts; persistence happens only when callers write fields to hardware registers.

## Dependencies and integration points
It includes `linux/types.h` and `phy_ht.h`, tying the radio table to HT-PHY channel programming. `radio_2059.c` owns the table data and implementation; `phy_ht.c` consumes the API.

## Risks and test signals
Because the structure order encodes how channel-table values map to hardware registers, inserting fields or reordering them without updating initializer macros and consumers would misprogram the RF path. Tests should build HT-PHY support and exercise 2059 init/channel-switch code, including NULL handling for unsupported channel frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2059.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/rfkill.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/rfkill.c

## Purpose
`rfkill.c` implements b43 hardware radio-kill polling. It checks the device's hardware radio enable bit and synchronizes that state with cfg80211/mac80211 rfkill state and b43 software radio state.

## Important APIs and functions
`b43_is_hw_radio_enabled()` reads `B43_MMIO_RADIO_HWENABLED_HI` and returns true when `B43_MMIO_RADIO_HWENABLED_HI_MASK` is clear. `b43_rfkill_poll()` is the mac80211 rfkill poll callback registered from the b43 hw ops.

## Control flow, state, and persistence
The poll callback converts `ieee80211_hw` to `b43_wl`, locks `wl->mutex`, and ensures the device is powered/initialized enough to read the hardware bit. If the device was below `B43_STAT_INITIALIZED`, it powers up the bus, enables the device temporarily, reads state, then disables/powers down before returning. When the hardware state changes, it updates `dev->radio_hw_enable`, logs the transition, calls `wiphy_rfkill_set_hw_state()`, and invokes `b43_software_rfkill()` if hardware and software radio state differ.

## Dependencies and integration points
It depends on core b43 helpers from `b43.h`, bus power management, device enable/disable, `wiphy_rfkill_set_hw_state()`, and the mac80211 rfkill poll hook in `main.c`.

## Risks and test signals
The function must not leave a suspended device powered after a poll, so the `brought_up` cleanup path is critical. Lock ordering around `wl->mutex` and bus power calls must remain consistent with the rest of b43. Test signals include rfkill toggle polling while the interface is down, while started, and during suspend/resume, plus confirmation that hardware-disabled state maps to `wiphy` blocked state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/rfkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/rfkill.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/rfkill.h

## Purpose
`rfkill.h` declares the small rfkill interface between b43 core code and the rfkill implementation.

## Important APIs and types
It forward-declares `struct ieee80211_hw` and `struct b43_wldev`, then declares `b43_rfkill_poll(struct ieee80211_hw *hw)` and `b43_is_hw_radio_enabled(struct b43_wldev *dev)`.

## Control flow, state, and persistence
The header has no executable logic or state. It exposes functions that read and synchronize hardware rfkill state.

## Dependencies and integration points
The declarations are consumed by b43 main registration code, where the mac80211 rfkill poll callback is wired to `b43_rfkill_poll()`, and by code that needs direct hardware radio-enable checks.

## Risks and test signals
The API assumes callers pass a valid b43 device context and that implementation-side locking/power management is respected. Build tests should cover inclusion from main b43 code, and runtime tests should verify rfkill polling still links and executes for devices with hardware radio switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/rfkill.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sdio.c

## Purpose
`sdio.c` is the SDIO transport glue that lets b43 operate over an SSB bus backed by an SDIO function. It handles SDIO device probing, chip-id extraction from tuples, SSB bus registration, interrupt dispatch, and driver registration.

## Important APIs, types, and functions
`b43_sdio_quirk` maps vendor/device IDs to SSB quirks; currently Broadcom 0x4318 gets `SSB_QUIRK_SDIO_READ_AFTER_WRITE32`. `b43_sdio_get_quirks()` performs the lookup. `b43_sdio_request_irq()` and `b43_sdio_free_irq()` install/remove a b43 interrupt handler through `sdio_claim_irq()` and `sdio_release_irq()`. `b43_sdio_probe()` parses tuple code `0x80` for `HNBU_CHIPID`, sets a 64-byte block size, enables the function, allocates `struct b43_sdio`, and calls `ssb_bus_sdiobus_register()`. `b43_sdio_remove()`, `b43_sdio_init()`, and `b43_sdio_exit()` manage teardown and SDIO driver registration.

## Control flow, state, and persistence
Probe fails with `-ENODEV` if the tuple lacks a vendor/device chip ID. Resource acquisition unwinds through labeled error paths that release host ownership, disable the function, and free allocation. Interrupt dispatch ignores interrupts before `B43_STAT_STARTED`, temporarily releases the SDIO host lock while running the b43 IRQ handler, then reclaims it. Runtime state is held in `struct b43_sdio` attached via `sdio_set_drvdata()`.

## Dependencies and integration points
The file depends on Linux MMC/SDIO APIs, `ssb_bus_sdiobus_register()`, b43 status helpers, and module init/exit calls in `main.c`. It supports Broadcom Nintendo Wii and C-guys EW-CG1102GC SDIO IDs.

## Risks and test signals
Risks include malformed tuple data access, host-claim balancing, IRQ callbacks racing with teardown, and preserving the release/reclaim pattern around b43 IRQ handling to avoid SDIO deadlocks. Test signals include probe/remove fault injection for each failure label, SDIO IRQ delivery after start only, and module load/unload with `CONFIG_B43_SDIO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sdio.h

## Purpose
`sdio.h` defines the conditional SDIO interface used by b43 core code. It provides real declarations when SDIO support is enabled and harmless stubs otherwise.

## Important APIs and types
Under `CONFIG_B43_SDIO`, `struct b43_sdio` embeds `struct ssb_bus` and stores an IRQ handler opaque pointer plus callback. The header declares `b43_sdio_request_irq()`, `b43_sdio_free_irq()`, `b43_sdio_init()`, and `b43_sdio_exit()`. Without SDIO support, request IRQ returns `-ENODEV`, init returns success, and free/exit are no-ops.

## Control flow, state, and persistence
The header itself has no runtime state beyond the structure definition. The stub behavior lets common b43 code call SDIO hooks unconditionally without forcing SDIO support into every build.

## Dependencies and integration points
It includes `linux/ssb/ssb.h` and forward-declares `struct b43_wldev`. `main.c` uses these APIs for driver init/exit and interrupt setup; `sdio.c` implements the enabled path.

## Risks and test signals
The stub `b43_sdio_init()` returning 0 means module initialization can proceed on non-SDIO builds, so callers must treat SDIO presence separately from successful core module init. Build matrix coverage should include `CONFIG_B43_SDIO=y/m` and disabled configurations to verify signatures stay consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sysfs.c

## Purpose
`sysfs.c` exposes b43 sysfs controls, currently the `interference` attribute for G-PHY interference mitigation. It lets privileged users read or set mitigation modes.

## Important APIs and functions
`get_integer()` copies up to ten bytes into a local buffer and parses a decimal integer with `simple_strtol()`. `b43_attr_interfmode_show()` returns the current G-PHY interference mode as a number plus label. `b43_attr_interfmode_store()` maps values 0 through 3 to `B43_INTERFMODE_*` constants and calls `wldev->phy.ops->interf_mitigation()` when available. `DEVICE_ATTR(interference, 0644, ...)` defines the sysfs file. `b43_sysfs_register()` and `b43_sysfs_unregister()` create/remove the attribute.

## Control flow, state, and persistence
Both show and store require `CAP_NET_ADMIN`. Show locks `wldev->wl->mutex`, rejects non-G PHY with `-ENOSYS`, reads `wldev->phy.g->interfmode`, emits text, and unlocks. Store parses input, validates mode, locks, invokes the PHY operation, and returns either an error or the byte count. State persists in driver PHY state and hardware programming performed by the mitigation callback.

## Dependencies and integration points
The file depends on Linux capability/sysfs helpers, b43 device conversion helpers, `main.h`, and `phy_common.h`. Registration is tied to b43 device initialization and teardown.

## Risks and test signals
`simple_strtol()` accepts partial/loose input and the show path documents only modes 0-2 even though store accepts mode 3 autowlan. Non-G PHY behavior and missing `interf_mitigation` must return stable errors. Test with CAP_NET_ADMIN and unprivileged users, valid/invalid numeric input, G-PHY versus non-G-PHY devices, and register/unregister lifetime around device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sysfs.h

## Purpose
`sysfs.h` declares b43 sysfs registration helpers for device lifecycle code.

## Important APIs and types
It forward-declares `struct b43_wldev` and declares `b43_sysfs_register(struct b43_wldev *dev)` and `b43_sysfs_unregister(struct b43_wldev *dev)`.

## Control flow, state, and persistence
There is no executable logic. The implementation creates and removes sysfs attributes that expose mutable driver/device state.

## Dependencies and integration points
The header is consumed by b43 initialization and teardown code, while `sysfs.c` implements the interface using Linux device attributes.

## Risks and test signals
The lifecycle contract requires unregister to be called for devices that successfully registered the attribute. Build tests should ensure declarations match the implementation; runtime tests should check sysfs file presence after initialization and removal after device teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables.c

## Purpose
`tables.c` contains shared b43 PHY calibration/filter lookup tables and helper functions for reading/writing OFDM and G-PHY hardware tables. The constants are used by legacy PHY workarounds and initialization routines.

## Important APIs, types, and functions
Exported data arrays include `b43_tab_rotor`, `b43_tab_retard`, `b43_tab_finefreqa`, `b43_tab_finefreqg`, noise tables, noise-scale tables, sigma-square tables, and RSSI AGC tables. `assert_sizes()` uses `BUILD_BUG_ON()` against size macros from `tables.h`; it is referenced after a return in `b43_ofdmtab_read16()` specifically to force compile-time checking. `b43_ofdmtab_read16/write16/read32/write32()` access OFDM tables through `B43_PHY_OTABLECTL`, `B43_PHY_OTABLEI`, and `B43_PHY_OTABLEQ`. `b43_gtab_read()` and `b43_gtab_write()` access G tables through `B43_PHY_GTABCTL` and `B43_PHY_GTABDATA`.

## Control flow, state, and persistence
The OFDM helpers cache the last table address and direction in `dev->phy.g->ofdmtab_addr` and `ofdmtab_addr_direction`. If the next access is sequential in the same direction, they avoid rewriting the hardware address register. Writes persist into PHY hardware table memory; reads return current hardware table contents.

## Dependencies and integration points
The file includes `b43.h`, `tables.h`, and `phy_g.h`. `wa.c` consumes the data arrays and size macros for PHY workarounds; G-PHY code uses the table access helpers.

## Risks and test signals
Risks include size macro drift, relying on unreachable code to instantiate compile-time assertions, and stale address-cache state if external code changes table control registers without updating `gphy`. Tests should build with warnings/static analysis, validate `BUILD_BUG_ON` coverage by changing a size in a scratch build, and exercise sequential/nonsequential 16-bit and 32-bit table access paths on G-PHY hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables.h

## Purpose
`tables.h` declares the shared PHY lookup tables exported by `tables.c` and defines their expected lengths for compile-time and caller loop bounds.

## Important APIs and constants
The header defines sizes for rotor, retard, fine frequency A/G, noise, noise-scale, sigma-square, and RSSI AGC tables. It declares extern arrays: `b43_tab_rotor`, `b43_tab_retard`, `b43_tab_finefreqa`, `b43_tab_finefreqg`, `b43_tab_noise*`, `b43_tab_noisescale*`, `b43_tab_sigmasqr*`, and `b43_tab_rssiagc*`.

## Control flow, state, and persistence
No logic or state is present. The constants define static data contracts and bounds used by implementation and callers.

## Dependencies and integration points
It is included by `tables.c` and users such as `wa.c`, which loops over arrays using the size macros while uploading or applying PHY workarounds.

## Risks and test signals
The size macros must exactly match array definitions. Mismatches are caught by `tables.c` compile-time assertions, but only if the file is built. Test signals include building b43 G-PHY support and checking workaround code loops use the declared macros rather than hard-coded lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables.h -->
