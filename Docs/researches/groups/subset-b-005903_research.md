# subset-b-005903 grouped research

This grouped report covers the exact source files assigned to `subset-b-005903`. Each file section is bounded by the reconciliation markers required for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgtable.h -->
# sources/distributed-fs/ceph-client/include/linux/pgtable.h

## Purpose
Generic Linux page-table API layer that sits above architecture `<asm/pgtable.h>` definitions. It supplies portable fallbacks, validation checks, walking helpers, batching helpers, TLB/cache hook declarations, page-protection utilities, huge-page helpers, PFN-map tracking hooks, and page-table modification tracking used by generic MM, vmalloc, ioremap, rmap, GUP, and fault paths.

## Important APIs, Types, and Functions
Key address traversal helpers include `pte_index()`, `pmd_index()`, `pud_index()`, `pgd_index()`, `pte_offset_kernel()`, `pmd_offset()`, `pud_offset()`, `pgd_offset()`, `pmd_off()`, `pmd_off_k()`, and `virt_to_kpte()`. PTE/PMD/PUD access helpers include `ptep_get()`, `pmdp_get()`, `pudp_get()`, lockless getters, `set_ptes()`, `set_pte_at()`, `ptep_get_and_clear()`, `get_and_clear_ptes()`, `clear_ptes()`, `wrprotect_ptes()`, `clear_young_dirty_ptes()`, `modify_prot_start_ptes()`, and `modify_prot_commit_ptes()`. Huge mapping support is represented by THP-oriented helpers such as `pmdp_huge_get_and_clear()`, `pudp_huge_get_and_clear()`, `pmdp_invalidate()`, `pmdp_invalidate_ad()`, deposit/withdraw hooks, `p?d_set_huge()`, `p?d_clear_huge()`, and `p?d_leaf()` fallbacks. `pgtbl_mod_mask` and `enum pgtable_level` describe modified page-table levels.

## Control Flow
Most logic is inline fallback control flow selected by `#ifndef` architecture overrides and `CONFIG_MMU`, THP, high-PTE, soft-dirty, huge-vmap, and lazy-MMU configuration. Page-table walkers compute level indexes and boundary ends, skip folded levels transparently, and clear bad entries through externally implemented `*_clear_bad()` routines. Batched PTE helpers loop over same-PMD, same-folio ranges, advance PFNs, and preserve dirty/accessed bits where needed. Lazy MMU mode uses per-task counters in `current->lazy_mmu_state`, entering architecture lazy mode only at the outer transition and flushing/leaving when nested sections close or pause/resume brackets require it.

## State and Persistence
The header does not own persistent storage, but it mutates durable MM state through caller-held page-table locks. It tracks PTE dirty/accessed metadata, soft-dirty metadata, swap metadata hooks, zero-page identity, PFN cache-mode tracking, and page-table synchronization masks. Correctness depends on refcounted pages, `mm_struct` page tables, `vm_area_struct` permissions, TLB flush ordering, RCU/highpte unmap discipline, and architecture page-table atomicity guarantees.

## Dependencies and Integration Points
Depends on `<asm/pgtable.h>`, `<linux/mm_types.h>`, `<linux/page_table_check.h>`, architecture TLB/cache hooks, THP, GUP, swap, vmalloc/ioremap, PAT-style PFN map tracking, and page-fault/rmap code. Architecture ports integrate by defining `__HAVE_ARCH_*` hooks, folded page-table macros, leaf predicates, pgprot modifiers, lockless accessors, and synchronization masks.

## Risks
The main risks are architecture fallback mismatch, lost hardware dirty/accessed bits during non-atomic updates, missing TLB flushes, incorrect behavior with folded levels, bad huge-page PFN fallbacks, and callers violating documented locking/context constraints. The lazy MMU API explicitly warns against sleeping and stale raw PTE reads while updates are batched.

## Test Signals
Relevant signals include MM selftests, GUP-fast stress, THP collapse/split/migration tests, mprotect/soft-dirty/userfaultfd tests, swap-in/out metadata tests, page-table-check failures, KASAN/KCSAN findings around page-table races, vmalloc/ioremap mapping tests, and architecture boot tests with different page-table level folding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgtable_api.h -->
# sources/distributed-fs/ceph-client/include/linux/pgtable_api.h

## Purpose
Compatibility include that exposes the generic page-table API by including `<linux/pgtable.h>`. It contains no independent declarations or logic.

## Important APIs, Types, and Functions
All exported API surface comes from `linux/pgtable.h`, including page-table walking, PTE mutation, huge-page, pgprot, and page-table synchronization helpers.

## Control Flow
No runtime control flow. Preprocessor inclusion delegates entirely to `pgtable.h`.

## State and Persistence
No owned state. Any page-table state affected by users of this header is managed by the APIs included from `pgtable.h`.

## Dependencies and Integration Points
Integrates consumers that include `pgtable_api.h` with the canonical page-table header. Its only dependency is `linux/pgtable.h`.

## Risks
The risk is only aliasing or include-order confusion if future code expects this file to define a separate API boundary. It should stay a thin wrapper unless callers are migrated.

## Test Signals
Build coverage for files including `linux/pgtable_api.h` is the primary signal; failures would be missing declarations from the delegated include.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pgtable_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phonet.h -->
# sources/distributed-fs/ceph-client/include/linux/phonet.h

## Purpose
Kernel-side Phonet socket interface header. It bridges internal networking code with the UAPI Phonet definitions and declares private ioctl payloads for Phonet network interface autoconfiguration.

## Important APIs, Types, and Functions
Defines `SIOCPNGAUTOCONF` as a private device ioctl, `struct if_phonet_autoconf` with a one-byte `device` selector, and `struct if_phonet_req` with a fixed interface name and union payload. The `ifr_phonet_autoconf` macro aliases the union member.

## Control Flow
No executable control flow. Consumers populate these structures and pass them through network ioctl paths; Phonet handlers interpret the union based on ioctl command.

## State and Persistence
No owned state. The header describes transient ioctl state used to configure or query Phonet device assignment.

## Dependencies and Integration Points
Depends on `<uapi/linux/phonet.h>` for protocol constants and on network device ioctl infrastructure through `SIOCDEVPRIVATE`. Integrates with Phonet socket, netdevice, and userspace ioctl handling.

## Risks
Fixed-size interface naming and private ioctl layout require ABI discipline. Any field-size change would break user/kernel expectations. The `uint8_t device` field constrains device identifiers to the UAPI-defined Phonet range.

## Test Signals
Build tests for Phonet-enabled kernels, ioctl ABI tests, and runtime Phonet autoconfiguration tests should validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phonet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy.h -->
# sources/distributed-fs/ceph-client/include/linux/phy.h

## Purpose
Main Ethernet PHY library contract. It defines MAC-to-PHY interface modes, MDIO bus representation, PHY device state, PHY driver callbacks, link diagnostics, ethtool integration, timestamping hooks, PLCA/MSE/EEE support, LED integration, fixed and SFP attachment points, and helper APIs used by network MAC drivers and PHY drivers.

## Important APIs, Types, and Functions
Core types are `phy_interface_t`, `struct mii_bus`, `enum phy_state`, `struct phy_c45_device_ids`, `struct phy_device`, `struct phy_driver`, `struct phy_tdr_config`, `struct phy_plca_cfg`, `struct phy_plca_status`, `struct phy_mse_capability`, `struct phy_mse_snapshot`, and `struct phy_led`. Bus/device APIs include `mdiobus_alloc()`, `mdiobus_register()`, `mdiobus_unregister()`, `get_phy_device()`, `phy_device_create()`, `phy_device_register()`, `phy_attach_direct()`, `phy_connect()`, `phy_disconnect()`, `phy_start()`, and `phy_stop()`. Register helpers include `phy_read()`, `phy_write()`, `phy_read_mmd()`, `phy_modify*()`, and paged variants. Driver registration uses `phy_drivers_register()` and `module_phy_driver()`.

## Control Flow
The PHY lifecycle flows from MDIO bus allocation/registration, PHY scan/device creation, driver probe/config init, MAC attach/connect, autonegotiation configuration, state-machine polling or interrupts, link status resolution, ethtool operations, suspend/resume, and detach/unregister. Inline helpers choose generic fallbacks when driver callbacks are absent, such as `phy_read_status()` falling back to `genphy_read_status()`.

## State and Persistence
`struct phy_device` is the persistent per-PHY state container: identifiers, Clause 45 IDs, interface and possible-interface bitmaps, link speed/duplex/pause/autoneg, EEE advertisements, PLCA and diagnostics support, timestamp callbacks, LED lists, SFP/phylink attachment, delayed work state machine, mutex, interrupt state, statistics support, port list, and driver-private/shared data. `struct mii_bus` persists bus identity, callbacks, device map, IRQ map, reset GPIO, lock, and per-address stats.

## Dependencies and Integration Points
Integrates with MDIO, MII, ethtool, netdevice, phylink, SFP, LED triggers, MACsec, PTP timestamping, rtnetlink, workqueues, timers, module registration, and device model PM. Generic PHY helpers integrate with Clause 22, Clause 37, Clause 45, 10G, Base-T1, EEE, PLCA, OATC14, cable test, and link statistics code.

## Risks
High-risk areas are MDIO locking context, interrupt versus polling state, state-machine races, incorrect advertisement masks, interface mode mismatches, EEE/autonomous EEE negotiation, PHY/MAC timestamp selection, optional callback error handling, and userspace-visible diagnostics with vendor-specific scaling. Many helpers must not run in interrupt context because MDIO transactions can sleep.

## Test Signals
Signals include PHYLIB build matrices, MDIO bus scan tests, MAC driver attach/detach tests, phylink integration tests, ethtool ksettings/EEE/WoL/stats/cable-test coverage, interrupt and polling link-change tests, suspend/resume/WoL tests, and KUnit or driver selftests for generic Clause 22/45 helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/omap_control_phy.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/omap_control_phy.h

## Purpose
TI OMAP control-module PHY interface for USB, PIPE3, PCIe, and related PHY power/mode controls. It exposes register bit definitions and optional helper calls used by OMAP PHY drivers and consumers.

## Important APIs, Types, and Functions
Defines `enum omap_control_phy_type`, `struct omap_control_phy`, `enum omap_control_usb_mode`, register bit masks for OTG validity, PHY power down, PIPE3 clock/power fields, PCIe PCS delay, and AM437x USB2 control. Exports `omap_control_phy_power()`, `omap_control_usb_set_mode()`, and `omap_control_pcie_pcs()` when `CONFIG_OMAP_CONTROL_PHY` is enabled, with no-op stubs otherwise.

## Control Flow
Consumers call mode or power helpers; implementation code writes the mapped control-module registers selected by `type`. When disabled at build time, helpers compile away.

## State and Persistence
`struct omap_control_phy` holds persistent device, MMIO register pointers, system clock, and PHY type. Hardware register state persists outside the header and affects power, VBUS/session flags, PIPE3 power, and PCIe PCS delay.

## Dependencies and Integration Points
Integrates with OMAP control-module drivers, USB2/OTG/PIPE3 PHY drivers, PCIe PHY setup, `struct device`, MMIO, and clocks.

## Risks
Incorrect bit programming can power down links, misreport USB role/session state, or mis-tune PCIe delay. Stubs can hide missing functionality if a consumer treats no-op behavior as success.

## Test Signals
Board boot tests on OMAP/DRA7/AM437x, USB host/device role switching, PIPE3 power-cycle tests, PCIe bring-up, and build tests with `CONFIG_OMAP_CONTROL_PHY` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/omap_control_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/omap_usb.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/omap_usb.h

## Purpose
OMAP USB2 PHY companion header. It declares the comparator binding hook used by OMAP USB2 PHY support.

## Important APIs, Types, and Functions
Defines `phy_to_omapusb(x)` for converting a generic USB PHY member to its containing `struct omap_usb`. Declares `omap_usb2_set_comparator()` when OMAP USB2 support is built, with an `-ENODEV` stub otherwise.

## Control Flow
Consumers install a `struct phy_companion` comparator through `omap_usb2_set_comparator()`. Disabled builds return immediately with `-ENODEV`.

## State and Persistence
The header itself has no state. Comparator registration persists in the OMAP USB2 implementation.

## Dependencies and Integration Points
Depends on `linux/usb/phy_companion.h` and integrates OMAP USB2 PHY code with USB comparator/companion logic.

## Risks
The container macro assumes the embedded member is named `phy`. Missing OMAP USB2 config produces an explicit error stub that callers must handle.

## Test Signals
Build tests for OMAP USB2 modular/built-in/disabled configs and USB2 comparator registration tests on supported OMAP platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/omap_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/pcie.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/pcie.h

## Purpose
PCIe PHY mode constants shared by PCIe PHY providers and consumers.

## Important APIs, Types, and Functions
Defines `PHY_MODE_PCIE_RC`, `PHY_MODE_PCIE_EP`, and `PHY_MODE_PCIE_BIFURCATION` numeric mode values for root-complex, endpoint, and bifurcated operation.

## Control Flow
No executable flow. Consumers pass these constants to PHY mode-setting code.

## State and Persistence
No state. Hardware mode persistence is managed by the PHY provider.

## Dependencies and Integration Points
Used with generic PHY configuration paths and PCIe controller/PHY drivers, notably Rockchip-originated mode definitions.

## Risks
Numeric constants must not collide with other provider-specific mode values expected by drivers. Incorrect mode selection can prevent PCIe link training.

## Test Signals
PCIe RC/EP/bifurcation probe tests and compile coverage for drivers using these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-common-props.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/phy-common-props.h

## Purpose
Common firmware-node property accessors for generic PHY polarity configuration.

## Important APIs, Types, and Functions
Declares `phy_get_rx_polarity()`, `phy_get_tx_polarity()`, `phy_get_manual_rx_polarity()`, and `phy_get_manual_tx_polarity()`. These functions parse receive/transmit polarity values for a named mode, validate them against supported flags from `dt-bindings/phy/phy.h`, and return chosen values via output pointers.

## Control Flow
No inline flow. Implementations are expected to read properties from a `struct fwnode_handle`, apply defaults, enforce supported masks, and report parse/validation errors.

## State and Persistence
No persistent state. Parsed polarity values become consumer or PHY-driver configuration state elsewhere.

## Dependencies and Integration Points
Depends on firmware-node abstractions and device-tree PHY binding constants. Integrates with PHY providers that share common RX/TX polarity properties.

## Risks
Risk centers on inconsistent binding names, unsupported polarity values being accepted, and callers ignoring `__must_check` errors.

## Test Signals
DT schema examples, fwnode property parser tests, and driver probe tests with default, automatic, and manual polarity settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-common-props.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-dp.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/phy-dp.h

## Purpose
DisplayPort/eDP configuration payload for the generic PHY framework.

## Important APIs, Types, and Functions
Defines `PHY_SUBMODE_DP`, `PHY_SUBMODE_EDP`, and `struct phy_configure_opts_dp` containing main-link rate, lane count, per-lane voltage swing, per-lane pre-emphasis, spread-spectrum clocking, and bit flags indicating which parts of the configuration should be applied.

## Control Flow
No functions. Consumers fill the structure and call generic `phy_configure()` or provider-specific validation/configuration ops. Providers inspect the `set_rate`, `set_lanes`, and `set_voltages` flags to limit reconfiguration.

## State and Persistence
The structure is transient input, but applied settings persist in DP PHY hardware until reconfigured or powered down.

## Dependencies and Integration Points
Included by `linux/phy/phy.h` and used by display bridge, controller, and PHY drivers for DisplayPort and embedded DisplayPort link training.

## Risks
Invalid lane counts, unsupported link rates, or out-of-range voltage/pre-emphasis values can break link training. Per-lane arrays assume up to four lanes.

## Test Signals
DP/eDP link-training tests across lane counts and rates, PHY validate failures for invalid inputs, and display mode-set regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-hdmi.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/phy-hdmi.h

## Purpose
HDMI configuration payload for the generic PHY framework, covering TMDS and FRL style operation.

## Important APIs, Types, and Functions
Defines `enum phy_hdmi_mode` with `PHY_HDMI_MODE_TMDS` and `PHY_HDMI_MODE_FRL`, plus `struct phy_configure_opts_hdmi` containing bits per color channel and either TMDS character rate or FRL per-lane rate/lane count.

## Control Flow
No inline logic. Display consumers select mode-specific fields before calling PHY validate/configure operations.

## State and Persistence
The structure is transient. Applied clocking and lane/rate settings persist in HDMI PHY hardware.

## Dependencies and Integration Points
Included by generic PHY `union phy_configure_opts` and used by HDMI display controller/bridge PHY providers.

## Risks
The union requires callers and providers to agree on TMDS versus FRL mode outside the structure. Wrong rate, lane, or color-depth assumptions can cause failed HDMI training or unstable output.

## Test Signals
HDMI mode-set tests for TMDS and FRL, PHY validation of rate/lane combinations, and display compliance tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-lvds.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/phy-lvds.h

## Purpose
LVDS configuration payload for generic PHY providers.

## Important APIs, Types, and Functions
Defines `struct phy_configure_opts_lvds` with bits per lane per differential clock cycle, differential clock rate, lane count, and `is_slave` for dual-link master/slave operation.

## Control Flow
No functions. Consumers pass the structure through `phy_configure()` and providers validate/program LVDS hardware.

## State and Persistence
Configuration is transient input. Applied lane/clock/master-slave state persists in the PHY until changed.

## Dependencies and Integration Points
Included by `linux/phy/phy.h`; integrates display pipelines and LVDS PHY providers.

## Risks
Incorrect clock or lane count causes panel timing failures. Dual-link slave state must match the paired master PHY and display bridge configuration.

## Test Signals
Panel bring-up tests, single/dual-link LVDS mode validation, and display timing regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-lvds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-mipi-dphy.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/phy-mipi-dphy.h

## Purpose
MIPI D-PHY timing configuration contract for generic PHY consumers and providers.

## Important APIs, Types, and Functions
`struct phy_configure_opts_mipi_dphy` enumerates D-PHY timing values for clock and data lanes: miss/post/pre/prepare/settle/term/trail/zero, turnaround timing, LPX, wakeup/init, HS and LP clock rates, and active lane count. It declares `phy_mipi_dphy_get_default_config()`, `phy_mipi_dphy_get_default_config_for_hsclk()`, and `phy_mipi_dphy_config_validate()`.

## Control Flow
Consumers can compute default timings from pixel clock, bits per pixel, and lane count, or from HS clock rate directly. Validation checks timing ranges before hardware configuration.

## State and Persistence
The timing structure is transient input. Applied values persist as PHY register programming and directly affect high-speed/low-power transitions.

## Dependencies and Integration Points
Included by generic PHY options and used by DRM/CSI/DSI camera/display PHY drivers. It bridges protocol timing requirements into PHY provider operations.

## Risks
Timing fields have strict unit expectations: picoseconds, microseconds, UI, and Hertz. Unit mistakes or invalid lane counts can cause intermittent DSI/CSI link failure. Providers must not silently accept invalid timing.

## Test Signals
Validation tests for min/max timing, DSI/CSI bring-up across lane counts and pixel clocks, and hardware link stability tests under power-cycle and mode-switch scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-mipi-dphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-sun4i-usb.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/phy-sun4i-usb.h

## Purpose
Allwinner sun4i USB PHY helper header for squelch-detect control.

## Important APIs, Types, and Functions
Declares `sun4i_usb_phy_set_squelch_detect(struct phy *phy, bool enabled)` and includes the generic PHY header.

## Control Flow
Consumers call the helper to enable or disable squelch detect on a sun4i USB PHY. Implementation-specific register programming lives outside this header.

## State and Persistence
No local state. The enabled setting persists in sun4i USB PHY hardware until changed or reset.

## Dependencies and Integration Points
Integrates Allwinner USB PHY drivers with generic `struct phy` consumers, likely USB controller glue that needs analog squelch behavior.

## Risks
Incorrect squelch settings can affect USB line-state detection and link reliability. There is no compile-time stub, so builds require the provider symbol when referenced.

## Test Signals
Allwinner USB host/device enumeration tests and suspend/resume or cable attach/detach tests with squelch toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy-sun4i-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/phy.h

## Purpose
Generic non-Ethernet PHY framework contract used by USB, UFS, PCIe, Ethernet SerDes, MIPI D-PHY, SATA, LVDS, DisplayPort, HDMI, and related providers/consumers.

## Important APIs, Types, and Functions
Defines `enum phy_mode`, `enum phy_media`, `enum phy_ufs_state`, `union phy_notify`, `union phy_configure_opts`, `struct phy_ops`, `struct phy_attrs`, `struct phy`, `struct phy_provider`, and `struct phy_lookup`. Consumer APIs include `phy_get()`, `devm_phy_get()`, optional and OF-index variants, `phy_init()`, `phy_exit()`, `phy_power_on()`, `phy_power_off()`, `phy_set_mode_ext()`, `phy_set_media()`, `phy_set_speed()`, `phy_configure()`, `phy_validate()`, `phy_reset()`, `phy_calibrate()`, and notification helpers. Provider APIs include `phy_create()`, `devm_phy_create()`, provider registration, lookup creation/removal, and xlate helpers.

## Control Flow
Consumers acquire a PHY by lookup or firmware node, optionally runtime-resume it, initialize, configure/validate, set mode/media/speed, power on, notify state changes, then power off/exit and put it. Providers create `struct phy` instances with operation tables and register firmware-node providers or static lookups. Disabled `CONFIG_GENERIC_PHY` builds return benign success for NULL optional PHYs and `-ENOSYS`/`-ENODEV` for real operations.

## State and Persistence
`struct phy` persists device identity, ops, mutex, init and power reference counts, attributes, regulator pointer, and debugfs state. The framework preserves shared-use semantics through counts so multiple consumers do not over-initialize or prematurely power off a PHY.

## Dependencies and Integration Points
Depends on device model, OF/fwnode, runtime PM, regulators, module ownership, and protocol-specific option headers for DP/HDMI/LVDS/MIPI. Integrates broad subsystem consumers through a common lifecycle and provider lookup model.

## Risks
Reference-count imbalance can leak power or power off active links. Optional-NULL success semantics must be distinguished from missing required PHY errors. Providers must serialize operations and validate mode-specific unions correctly.

## Test Signals
Builds with generic PHY enabled/disabled, devm cleanup tests, multi-consumer init/power count tests, DT lookup/xlate tests, and subsystem bring-up tests for each supported `phy_mode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/tegra/xusb.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/tegra/xusb.h

## Purpose
NVIDIA Tegra XUSB pad controller and PHY coordination API for USB3/HSIC/UTMI power, context, wake, and port mapping.

## Important APIs, Types, and Functions
Declares `tegra_xusb_padctl_get()`, `tegra_xusb_padctl_put()`, USB3 context save, HSIC idle, LFPS detect control, VBUS override, UTMI pad power and reset helpers, USB3 companion and port-number lookup, sleepwalk enable/disable, wake enable/disable, and remote wake detection.

## Control Flow
USB/XUSB controller code obtains a pad controller, configures port-specific PHY behavior, saves context before low-power transitions, enables sleepwalk/wake for suspend, checks remote wake, and releases the pad controller.

## State and Persistence
Persistent state is owned by the Tegra pad controller implementation and PHY hardware: port context, idle flags, LFPS detection, VBUS override, sleepwalk/wake configuration, and saved USB3 state.

## Dependencies and Integration Points
Integrates Tegra XUSB host/device controller code, generic `struct phy`, device model, and USB speed enumeration.

## Risks
Suspend/resume ordering and port-number mismatches can break wake or restore wrong lane context. Missing reference release can leak padctl references.

## Test Signals
Tegra USB2/USB3 enumeration, suspend/resume remote wake, HSIC idle tests, LFPS detection tests, and XUSB controller probe/remove tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/tegra/xusb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/ulpi_phy.h -->
# sources/distributed-fs/ceph-client/include/linux/phy/ulpi_phy.h

## Purpose
Helper for registering a generic PHY for a ULPI device and binding it to the parent USB controller through a lookup.

## Important APIs, Types, and Functions
Defines `ulpi_phy_create()` and `ulpi_phy_destroy()`. Creation calls `phy_create()` on `ulpi->dev`, creates a lookup named `"usb2-phy"` for the parent device, and destroys the PHY on lookup failure. Destruction removes the lookup and destroys the PHY.

## Control Flow
The helper wraps a two-step create/bind sequence with error unwinding. Consumers call destroy for symmetric cleanup.

## State and Persistence
Persistent state is the created `struct phy` and lookup entry linking the ULPI PHY to its controller. The header owns no global state.

## Dependencies and Integration Points
Depends on generic PHY APIs, ULPI device structures, device names, and USB controller parent-child topology.

## Risks
The lookup assumes the controller is always `ulpi->dev.parent` and the connection id is `"usb2-phy"`. If topology or naming differs, consumers may fail to find the PHY.

## Test Signals
ULPI PHY probe/remove tests, lookup resolution from parent USB controller, and error-path tests for lookup creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy/ulpi_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy_fixed.h -->
# sources/distributed-fs/ceph-client/include/linux/phy_fixed.h

## Purpose
Fixed-link PHY interface for network devices without a dynamic external PHY, such as switch CPU ports or board-wired links.

## Important APIs, Types, and Functions
Defines `struct fixed_phy_status` with speed, duplex, link, pause, and asymmetric pause. When `CONFIG_FIXED_PHY` is enabled, declares `fixed_phy_change_carrier()`, `fixed_phy_register()`, `fixed_phy_register_100fd()`, `fixed_phy_unregister()`, and `fixed_phy_set_link_update()`. Disabled builds return `ERR_PTR(-ENODEV)` for registration and no-op unregister.

## Control Flow
Drivers register a fixed PHY with static status or a default 100/full-duplex helper, optionally install a link-update callback, change carrier state, and unregister during teardown.

## State and Persistence
Fixed PHY state persists in the registered `phy_device` and status/callback managed by the fixed PHY implementation.

## Dependencies and Integration Points
Integrates with PHYLIB, netdevice carrier state, device-tree fixed-link descriptions, and MAC drivers that use PHY APIs without MDIO hardware.

## Risks
Static link parameters can diverge from actual board wiring. Disabled config stubs require callers to handle `-ENODEV`.

## Test Signals
Fixed-link MAC probe tests, carrier change tests, device-tree fixed-link parsing, and disabled-config build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy_fixed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy_led_triggers.h -->
# sources/distributed-fs/ceph-client/include/linux/phy_led_triggers.h

## Purpose
PHY link-speed LED trigger integration for PHYLIB.

## Important APIs, Types, and Functions
When `CONFIG_LED_TRIGGER_PHY` is enabled, defines name-size constants, `struct phy_led_trigger` embedding `struct led_trigger`, and declares `phy_led_triggers_register()`, `phy_led_triggers_unregister()`, and `phy_led_trigger_change_speed()`. Disabled builds provide success/no-op stubs.

## Control Flow
PHY probe/register paths create LED triggers, link speed changes update the active trigger, and teardown unregisters triggers.

## State and Persistence
Triggers persist per PHY while registered. Names encode MDIO bus/address and speed suffix; `struct phy_device` stores trigger pointers when LED support is enabled.

## Dependencies and Integration Points
Depends on LED trigger subsystem and `linux/phy.h`. Integrates PHY state changes with LED class trigger selection.

## Risks
Name-size calculations must match MDIO identifiers. Trigger updates must track speed/link transitions without stale LED state. Disabled stubs can mask absent visual feedback.

## Test Signals
LED trigger registration tests, link speed transition tests, sysfs LED trigger visibility, and build coverage with LED trigger support enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy_led_triggers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy_link_topology.h -->
# sources/distributed-fs/ceph-client/include/linux/phy_link_topology.h

## Purpose
Network-device PHY topology tracking API. It models chains of PHYs and SFP-attached PHYs so userspace can address individual PHY capabilities.

## Important APIs, Types, and Functions
Defines `struct phy_link_topology` with an `xarray` of PHY nodes and next index, and `struct phy_device_node` with upstream type, upstream netdev/PHY, optional parent SFP bus, and target PHY. Exposes `phy_link_topo_add_phy()`, `phy_link_topo_del_phy()`, and `phy_link_topo_get_phy()` when PHYLIB is enabled; otherwise stubs return success or NULL.

## Control Flow
PHYs are added to a netdevice topology when attached or discovered, looked up by `phyindex` for userspace operations, and removed on detach. The inline lookup handles absent topology by returning NULL.

## State and Persistence
Topology state persists in `net_device->link_topo`, an xarray, and assigned PHY indexes. Nodes track upstream relationships to support chained links.

## Dependencies and Integration Points
Depends on ethtool topology definitions, netdevice, xarray, PHYLIB, and SFP bus integration.

## Risks
Index allocation and deletion must be synchronized by implementation code. Stale nodes could expose detached PHYs to userspace. Disabled stubs mean callers must not assume topology exists.

## Test Signals
EtHTool PHY index queries, SFP-with-PHY attach/detach tests, chained PHY topologies, and xarray lifetime tests under netdevice teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy_link_topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy_port.h -->
# sources/distributed-fs/ceph-client/include/linux/phy_port.h

## Purpose
Represents physical ports exposed by a PHY, including MDI copper/fiber ports and MII/SerDes ports, with callbacks for link state and MII configuration.

## Important APIs, Types, and Functions
Defines `enum phy_port_parent`, `struct phy_port_ops`, and `struct phy_port`. APIs include `phy_port_alloc()`, `phy_port_destroy()`, `port_phydev()`, `phy_of_parse_port()`, `phy_port_is_copper()`, `phy_port_is_fiber()`, `phy_port_update_supported()`, `phy_port_restrict_mediums()`, and `phy_port_get_type()`.

## Control Flow
PHY drivers allocate or parse ports, attach them to a PHY, update supported modes, restrict advertised media, and invoke ops for out-of-band link changes or MII configuration.

## State and Persistence
`struct phy_port` persists list membership, parent PHY, ops, pair count, medium bitmask, supported link modes, interface bitmap, and flags for described/active/MII/SFP status.

## Dependencies and Integration Points
Depends on ethtool link mode/media definitions, generic Ethernet PHY interfaces, device-tree parsing, and PHY driver attach callbacks in `struct phy_driver`.

## Risks
Incorrect medium/interface masks can advertise impossible links. Active-port state must match physical routing, especially for multi-port PHYs or SFP cages.

## Test Signals
DT port parsing tests, copper/fiber/SFP detection, ethtool advertised mode checks, and multi-port PHY attach tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phy_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phylib_stubs.h -->
# sources/distributed-fs/ceph-client/include/linux/phylib_stubs.h

## Purpose
Small indirection layer allowing networking code to call selected PHYLIB services while tolerating PHYLIB being optional.

## Important APIs, Types, and Functions
When PHYLIB is enabled, declares global `phylib_stubs` and `struct phylib_stubs` callbacks for hardware timestamp get/set, PHY stats, and link extended stats. Inline wrappers `phy_hwtstamp_get()`, `phy_hwtstamp_set()`, `phy_ethtool_get_phy_stats()`, and `phy_ethtool_get_link_ext_stats()` assert RTNL, check the stub table, and dispatch or return/do nothing. Disabled builds return `-EOPNOTSUPP` or no-op.

## Control Flow
Callers enter under RTNL, wrapper checks whether PHYLIB registered the stub table, then dispatches. Registration/unregistration is synchronized externally under RTNL.

## State and Persistence
The only persistent state is the global callback-table pointer supplied by PHYLIB.

## Dependencies and Integration Points
Depends on rtnetlink locking, ethtool stats/timestamp structures, netlink extack, and optional PHYLIB module state.

## Risks
Calling without RTNL violates synchronization. Null stub table must be treated as unsupported. Callback pointer lifetime depends on PHYLIB registration discipline.

## Test Signals
Builds with PHYLIB enabled/disabled, RTNL lockdep assertions, timestamp get/set tests, and ethtool stats calls before and after PHYLIB stub registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phylib_stubs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phylink.h -->
# sources/distributed-fs/ceph-client/include/linux/phylink.h

## Purpose
PHYLINK MAC/PHY/PCS coordination contract for network drivers. It abstracts fixed links, PHY-managed links, and in-band-negotiated links, validating MAC/PCS capabilities and coordinating link-up/down, EEE, pause, WoL, suspend/resume, and ethtool operations.

## Important APIs, Types, and Functions
Defines mode and capability bits (`MLO_PAUSE_*`, `MLO_AN_*`, `PHYLINK_PCS_NEG_*`, `MAC_*`), `struct phylink_link_state`, `struct phylink_config`, `struct phylink_mac_ops`, `struct phylink_pcs`, and `struct phylink_pcs_ops`. Lifecycle APIs include `phylink_create()`, `phylink_destroy()`, `phylink_connect_phy()`, firmware-node connect helpers, fixed-link setup, `phylink_start()`, `phylink_stop()`, suspend/resume helpers, and MAC/PCS change notifications. EtHTool APIs cover ksettings, pause, EEE, WoL, nway reset, MII ioctl, and speed down/up.

## Control Flow
Drivers create phylink with MAC ops and config, connect a PHY/fixed link/fwnode, then start link management. Major reconfiguration calls `mac_prepare()`, `mac_config()`, PCS config/restart as needed, and `mac_finish()`. Link resolution calls PCS/MAC link-up/down in the correct order and supports in-band state changes through `phylink_mac_change()` or `phylink_pcs_change()`.

## State and Persistence
Opaque `struct phylink` holds runtime state outside the header. Persistent inputs in `phylink_config` include supported interfaces, MAC/LPI capabilities, PM policy, fixed-state callback, EEE defaults, and WoL policy. `phylink_pcs` persists PCS ops, supported interface bitmap, polling flag, and phylink backpointer.

## Dependencies and Integration Points
Depends on Ethernet PHYLIB, PCS drivers, netdevice, ethtool, workqueues, spinlocks, EEE config, fwnode/device-tree, and MAC drivers. It integrates media-specific MII C22/C45 PCS helpers and USXGMII/C73 decode helpers.

## Risks
MAC ops must not use invalid fields in `mac_config()`, and must avoid link bouncing for pause-only updates. Incorrect negotiation mode selection, PCS restart handling, or pause capability advertisement can cause unstable links. EEE and RX-clock stop interactions are sensitive during suspend and LPI.

## Test Signals
Phylink-enabled MAC driver tests, fixed/PHY/in-band mode coverage, PCS validation/config tests, ethtool ksettings/pause/EEE/WoL tests, suspend/resume with WoL, and link replay/change notification tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/phylink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pid.h -->
# sources/distributed-fs/ceph-client/include/linux/pid.h

## Purpose
Kernel internal PID object API. It provides stable `struct pid` references across numeric PID reuse, task attachment lists for PID/TGID/PGID/SID, PID namespace number translation, pidfd support, and task PID helper accessors.

## Important APIs, Types, and Functions
Defines `RESERVED_PIDS`, `struct upid`, `struct pid`, `init_struct_pid`, and helpers including `get_pid()`, `put_pid()`, `pid_task()`, `get_pid_task()`, `get_task_pid()`, `attach_pid()`, `detach_pid()`, `change_pid()`, `exchange_tids()`, `transfer_pid()`, `find_pid_ns()`, `find_vpid()`, `find_get_pid()`, `alloc_pid()`, `free_pid()`, `free_pids()`, `disable_pid_allocation()`, `pid_nr()`, `pid_nr_ns()`, and `pid_vnr()`. Pidfd functions include `pidfd_pid()`, `pidfd_get_pid()`, `pidfd_get_task()`, `pidfd_prepare()`, and `do_notify_pidfd()`.

## Control Flow
PID allocation creates a namespace-level number array, attaches tasks under tasklist locking, and exposes lookup under tasklist or RCU protection. Task helpers convert `task_struct` PID pointers to numbers in init/current/specified namespaces. Iteration macros walk task lists attached to a pid and handle thread-group cases.

## State and Persistence
`struct pid` persists a refcount, namespace level, lock, pidfs inode/hash/dentry/attrs, per-pid-type task hlist heads, inode list, pidfd waitqueue, RCU callback, and namespace-specific `struct upid numbers[]`. It deliberately outlives numeric PID reuse while references are held.

## Dependencies and Integration Points
Depends on pid namespaces, RCU hlist, refcounting, rhashtable, scheduler/task structures, waitqueues, pidfs, pidfd, tasklist locking, and namespace-aware task APIs.

## Risks
Dereferencing stale tasks without `pid_alive()` or RCU/tasklist locking is unsafe. Numeric PID storage can race PID reuse; code should hold `struct pid` references. Attachment changes require tasklist write lock. Namespace translation can return zero when a PID is not visible.

## Test Signals
Fork/exit stress, pid namespace tests, pidfd wait/notification tests, PID reuse tests, task iteration under RCU, and lockdep/KCSAN checks around attach/detach paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pid_namespace.h -->
# sources/distributed-fs/ceph-client/include/linux/pid_namespace.h

## Purpose
PID namespace state and lifecycle API. It defines the namespace object used to allocate and translate PIDs independently across nested process namespaces.

## Important APIs, Types, and Functions
Defines `MAX_PID_NS_LEVEL`, memfd noexec scope constants when applicable, `struct pid_namespace`, `init_pid_ns`, and `PIDNS_ADDING`. Enabled builds expose `to_pid_ns()`, `get_pid_ns()`, `pidns_memfd_noexec_scope()`, `copy_pid_ns()`, `zap_pid_ns_processes()`, `reboot_pid_ns()`, `put_pid_ns()`, and `pidns_is_ancestor()`. Common APIs include `task_active_pid_ns()`, `pidhash_init()`, `pid_idr_init()`, sysctl registration helpers, and `task_is_in_init_pid_ns()`.

## Control Flow
Namespace creation through `copy_pid_ns()` either reuses the existing namespace or creates a child when `CLONE_NEWPID` is set. Process teardown can zap namespace processes or record namespace reboot status. Memfd noexec scope walks parent namespaces and takes the maximum effective restriction.

## State and Persistence
`struct pid_namespace` persists an IDR allocator, allocated count, sysctl state, child reaper task, PID cache, nesting level, pid_max, parent namespace, BSD accounting pin, user namespace, ucounts, reboot code, namespace common object, and cleanup work item.

## Dependencies and Integration Points
Depends on scheduler, mm, workqueues, namespace core, IDR, sysctl, memfd, user namespaces, ucounts, and process accounting.

## Risks
Namespace nesting is capped by `MAX_PID_NS_LEVEL` because `struct pid` embeds per-level numbers. Reaper lifetime and namespace teardown are delicate; `zap_pid_ns_processes()` is invalid when PID namespaces are disabled. Sysctl state must follow namespace lifetime.

## Test Signals
PID namespace clone/unshare tests, nested namespace limits, namespace reboot tests, memfd noexec inheritance tests, pid_max sysctl tests, and process reaper teardown stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pid_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pid_types.h -->
# sources/distributed-fs/ceph-client/include/linux/pid_types.h

## Purpose
Shared PID type enumeration used by task, PID, process group, and session APIs.

## Important APIs, Types, and Functions
Defines `enum pid_type` values `PIDTYPE_PID`, `PIDTYPE_TGID`, `PIDTYPE_PGID`, `PIDTYPE_SID`, and `PIDTYPE_MAX`. Forward-declares `struct pid_namespace` and `init_pid_ns`.

## Control Flow
No runtime flow. The enum selects which PID list or numeric translation a caller wants.

## State and Persistence
No state. The values index arrays such as `struct pid::tasks[PIDTYPE_MAX]`.

## Dependencies and Integration Points
Included by PID and scheduler headers that need the enum without pulling full PID internals.

## Risks
Adding or reordering values affects array indexes and ABI-like internal assumptions. `PIDTYPE_MAX` must remain last.

## Test Signals
Build coverage and PID attach/lookup tests across PID, TGID, PGID, and SID categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pid_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pidfs.h -->
# sources/distributed-fs/ceph-client/include/linux/pidfs.h

## Purpose
PID filesystem integration API. It associates `struct pid` objects with filesystem dentries/files and supports pidfd allocation plus coredump integration.

## Important APIs, Types, and Functions
Declares `pidfs_alloc_file()`, `pidfs_init()`, `pidfs_prepare_pid()`, `pidfs_add_pid()`, `pidfs_remove_pid()`, `pidfs_exit()`, optional `pidfs_coredump()`, `pidfs_dentry_operations`, `pidfs_register_pid()`, and `pidfs_free_pid()`.

## Control Flow
PID lifecycle code prepares/registers PID filesystem state when PIDs are created, adds/removes them as tasks live and exit, allocates pidfd files for userspace handles, and releases pidfs data when the PID object is freed.

## State and Persistence
Persistent state is stored in `struct pid` fields declared in `pid.h`: inode number, hash node, stashed dentry, and pidfs attributes. The header itself declares operations.

## Dependencies and Integration Points
Integrates PID core, VFS files/dentries, pidfd, task exit, and coredump paths.

## Risks
VFS lifetime and PID lifetime must be synchronized to avoid stale dentries or leaked pidfs attributes. Coredump hooks must not outlive task/PID state.

## Test Signals
Pidfd creation tests, `/proc` or pidfs lookup tests where applicable, task exit cleanup tests, coredump path tests, and filesystem lifetime leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pidfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pim.h -->
# sources/distributed-fs/ceph-client/include/linux/pim.h

## Purpose
Protocol Independent Multicast header definitions and helpers for IPv4 multicast routing PIM-SM/DM handling.

## Important APIs, Types, and Functions
Defines PIM v1/v2 version constants, PIM message type enum values from RFC 7761, `PIM_NULL_REGISTER`, `struct pimhdr`, `struct pimreghdr`, `pim_rcv_v1()`, `ipmr_pimsm_enabled()`, `pim_hdr()`, `pim_hdr_version()`, `pim_hdr_type()`, and `pim_ipv4_all_pim_routers()`.

## Control Flow
Network receive paths can extract the PIM header from an skb transport header, classify version/type, detect all-PIM-routers multicast address, and dispatch v1 handling via `pim_rcv_v1()`.

## State and Persistence
No owned persistent state. It interprets packet header bytes in `sk_buff` instances.

## Dependencies and Integration Points
Depends on skbuff, byte-order helpers, multicast routing config symbols, and IPv4 multicast router code.

## Risks
Packet parsing assumes transport header points at a complete PIM header. Version/type extraction relies on packed high/low nibbles. Endianness constants must be used for wire-format flags and addresses.

## Test Signals
PIM packet receive tests, multicast route tests with PIM-SM v1/v2 configs, malformed skb tests, and all-PIM-routers address matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/pinctrl/consumer.h

## Purpose
Consumer-facing pinctrl API for devices and GPIO controllers. It lets drivers acquire pinctrl handles, select named states, and coordinate GPIO line ownership/direction/configuration with pin controllers.

## Important APIs, Types, and Functions
Declares opaque `struct pinctrl` and `struct pinctrl_state`. Enabled APIs include GPIO arbitration/config helpers, `pinctrl_get()`, `pinctrl_put()`, `pinctrl_lookup_state()`, `pinctrl_select_state()`, devm variants, default-state selection, and PM state selection helpers. Always-available convenience wrappers include `pinctrl_get_select()`, `pinctrl_get_select_default()`, `devm_pinctrl_get_select()`, and `devm_pinctrl_get_select_default()`.

## Control Flow
Typical flow gets a handle for a device, looks up a named state, selects it, and later releases the handle. Convenience helpers perform get/lookup/select with error unwinding. PM helpers select default/init/sleep/idle states when configured. Disabled `CONFIG_PINCTRL` builds return permissive GPIO results and NULL/no-op pinctrl state selection.

## State and Persistence
Pinctrl core owns persistent handles and states. Consumers hold returned handles and selected pin states affect hardware mux/config until another state is selected.

## Dependencies and Integration Points
Depends on error pointer helpers, `pinctrl-state.h`, GPIO chip integration, device model, and optional PM. Integrates driver probe/remove and suspend/resume state management.

## Risks
NULL stubs in disabled builds differ from error pointers, so callers must use standard helper semantics. Missing error unwinding can leak handles. Incorrect state selection can break GPIO or peripheral muxing.

## Test Signals
Driver probe tests with default/init/sleep/idle pin states, GPIO request/direction conflict tests, disabled-config build tests, and PM suspend/resume pin state checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/devinfo.h -->
# sources/distributed-fs/ceph-client/include/linux/pinctrl/devinfo.h

## Purpose
Device-core pinctrl metadata container used to associate a device with its pinctrl handle and common pin states.

## Important APIs, Types, and Functions
When pinctrl is enabled, defines `struct dev_pin_info` containing the device pinctrl handle plus default, init, and PM sleep/idle states. Declares `pinctrl_init_done()` and inline `dev_pinctrl()`. Disabled builds provide no-op/NULL stubs.

## Control Flow
Device core initializes pin information, calls `pinctrl_init_done()` when probe-time pinctrl setup is complete, and drivers/core code use `dev_pinctrl()` to access the associated handle.

## State and Persistence
`struct dev_pin_info` persists under `struct device::pins` and tracks selected/found pinctrl states for the device lifetime.

## Dependencies and Integration Points
Depends on device model, pinctrl consumer API, and PM. It is an internal bridge between pinctrl core and generic device structures.

## Risks
Consumers must handle `dev->pins == NULL`. PM-only fields are conditional, so code must respect `CONFIG_PM`.

## Test Signals
Device probe tests with pinctrl states, PM state tests, disabled pinctrl build coverage, and device teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/devinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/machine.h -->
# sources/distributed-fs/ceph-client/include/linux/pinctrl/machine.h

## Purpose
Board/machine pinctrl mapping API. It lets platform code describe how device state names map to controller mux groups and pin/group configuration entries.

## Important APIs, Types, and Functions
Defines `enum pinctrl_map_type`, `struct pinctrl_map_mux`, `struct pinctrl_map_configs`, and `struct pinctrl_map`. Provides macros for dummy states, mux-group states, default states, hog states, pin config states, and group config states. Enabled APIs include `pinctrl_register_mappings()`, `devm_pinctrl_register_mappings()`, `pinctrl_unregister_mappings()`, and `pinctrl_provide_dummies()`; disabled stubs return success/no-op.

## Control Flow
Machine code builds static `pinctrl_map` arrays using macros, registers them during platform setup or device-managed probe, and unregisters when appropriate. Pinctrl consumers later resolve state names against these mappings.

## State and Persistence
Registered mapping tables persist in the pinctrl core until explicitly unregistered or devm cleanup. The mapping entries point at device names, state names, controller names, mux functions, and configuration arrays.

## Dependencies and Integration Points
Depends on array-size macros and pinctrl state names. Integrates board files, platform data, pinmux providers, pinconf providers, and consumer state lookup.

## Risks
String names must match device/controller names exactly. Config arrays must outlive registered mappings. Disabled stubs can let board code build without pinctrl but no hardware muxing occurs.

## Test Signals
Board boot/probe tests, mapping registration/unregistration tests, pinmux hog tests, default/sleep state lookup tests, and disabled pinctrl build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pinctrl/machine.h -->
