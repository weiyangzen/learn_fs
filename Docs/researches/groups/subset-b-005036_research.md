# subset-b-005036 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-ufs.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-ufs.c

## Purpose

This file is the Qualcomm QMP UFS PHY platform driver. It binds device-tree compatibles such as `qcom,sm8550-qmp-ufs-phy` to SoC-specific register programming tables, maps the PHY register blocks, exposes a Linux generic PHY, and sequences regulators, clocks, resets, register writes, and ready polling needed by the UFS host controller.

The file is mostly static initialization data. Its active logic is a small PHY state machine around those data tables:

- Select a `struct qmp_phy_cfg` from the OF match table.
- Map SERDES, PCS, TX, RX, and optional second-lane register windows.
- Register three fixed-rate symbol clocks for the UFS controller.
- On PHY use, enable supplies and clocks, program base and gear-specific tables, release reset, start SERDES, and poll PCS readiness.

## Important APIs, types, and data

- `struct qmp_ufs_offsets` describes offsets for single-register-space bindings: `serdes`, `pcs`, `tx`, `rx`, `tx2`, and `rx2`.
- `struct qmp_phy_cfg_tbls` groups SERDES/TX/RX/PCS initialization arrays and carries `max_gear` for overlay tables.
- `struct qmp_phy_cfg` is the per-compatible hardware description. It records lane count, offsets, max supported UFS HS gear, base tables, HS Series B tables, up to two gear overlays, regulator bulk definitions, per-generation PCS register layout, and `no_pcs_sw_reset`.
- `struct qmp_ufs` is runtime state: device pointer, selected cfg, mapped register bases, clocks, regulators, optional UFS reset, `struct phy`, and the last requested `mode`/`submode`.
- `qmp_phy_init_tbl` and `QMP_PHY_INIT_CFG()` come from shared QMP headers and drive the table writes via `qmp_configure()` and `qmp_configure_lane()`.
- `ufsphy_v2_regs_layout` through `ufsphy_v6_regs_layout` normalize PCS register offsets for reset, start, ready, and power-down registers.
- Per-SoC table families such as `sm8550_ufsphy_*`, `sm8650_ufsphy_*`, `sm8750_ufsphy_*`, and `milos_ufsphy_*` tune PLL, CDR, RX equalization, TX drive, Hibern8 timing, and advertised HS gear capabilities.

The exported integration surface is `qcom_qmp_ufs_phy_ops`:

- `.init = qmp_ufs_phy_init`
- `.power_on = qmp_ufs_power_on`
- `.power_off = qmp_ufs_power_off`
- `.calibrate = qmp_ufs_phy_calibrate`
- `.set_mode = qmp_ufs_set_mode`

## Control flow

Probe:

1. `qmp_ufs_probe()` allocates `struct qmp_ufs`, reads the OF match data, fetches all clocks via `devm_clk_bulk_get_all()`, and gets per-cfg supplies with `devm_regulator_bulk_get_const()`.
2. The driver supports two DT shapes. If a child node exists, `qmp_ufs_parse_dt_legacy()` maps parent resource 0 as SERDES and maps child resources by index for TX, RX, PCS, optional TX2/RX2, and optional `pcs_misc`. Without a child, `qmp_ufs_parse_dt()` maps one resource and derives block bases from `cfg->offsets`.
3. `qmp_ufs_register_clocks()` registers fixed-rate `rx_symbol_0`, `rx_symbol_1`, and `tx_symbol_0` clocks through an OF clock provider.
4. A generic PHY is created with `devm_phy_create()`, driver data is attached, and `devm_of_phy_provider_register()` publishes the PHY.

Runtime PHY operations:

1. `qmp_ufs_set_mode()` validates that the requested UFS gear submode is nonzero and within `cfg->max_supported_gear`, then stores mode/submode.
2. `qmp_ufs_power_on()` enables regulators and all clocks, then sets `SW_PWRDN` in the PCS power-down-control register to bring the active-low PHY power state up.
3. `qmp_ufs_phy_calibrate()` asserts the delayed `ufsphy` reset, writes the base register tables, applies the best matching gear overlay from `qmp_ufs_get_gear_overlay()`, optionally applies HS Series B overrides, deasserts reset, clears PCS software reset when present, starts SERDES, and waits up to `PHY_INIT_COMPLETE_TIMEOUT` for `PCS_READY`.
4. `qmp_ufs_power_off()` clears `SW_PWRDN`, disables clocks, and disables regulators.

`qmp_ufs_phy_init()` exists primarily for older hardware where `no_pcs_sw_reset` is true. It lazily requests the `"ufsphy"` reset to avoid a circular dependency between the UFS controller and its PHY.

## State and persistence behavior

The driver keeps only volatile kernel state in `struct qmp_ufs`. The persistent hardware programming is the register state written into the PHY while powered. There is no filesystem persistence or firmware handoff in this file.

`mode` and `submode` are stored until the next `set_mode()` call and influence calibration table overlays. If a consumer skips setting mode/submode or asks for an invalid gear, calibration may either use only base tables or fail earlier through `qmp_ufs_set_mode()`. The `ufs_reset` pointer is cached after the first successful lazy reset lookup.

## Dependencies and integration points

- Linux PHY framework: `devm_phy_create()`, `phy_set_drvdata()`, `devm_of_phy_provider_register()`, and the generic PHY callbacks.
- Device tree matching through `qmp_ufs_of_match_table`.
- Common QMP helpers and register definitions from `phy-qcom-qmp-common.h`, `phy-qcom-qmp.h`, PCS UFS headers, and QSERDES UFS headers.
- UFS mode constants from `<ufs/unipro.h>` such as `UFS_HS_G3`, `UFS_HS_G4`, and `UFS_HS_G5`.
- Regulators `vdda-phy` and `vdda-pll`, with SoC-specific initial load values.
- Reset framework for the delayed `"ufsphy"` reset.
- Clock framework for input clocks and fixed-rate UFS symbol clock providers.
- Platform resource mapping and legacy child-node mapping APIs.

## Risks and edge cases

- The register tables are hardware-tuning data. A wrong offset header, table value, lane count, or compatible-to-cfg association can cause silent link instability rather than a clear probe failure.
- `qmp_ufs_get_gear_overlay()` falls back to the lowest overlay when no exact gear match exists. That is deliberate, but a missing overlay `max_gear` can make a higher gear run with only base tuning.
- `qmp_ufs_set_mode()` rejects submode `0`. Consumers must set a valid UFS gear before calibration on paths that depend on overlays.
- Legacy binding resource indexes are fixed and differ between one-lane and two-lane configs. Device-tree mistakes can map the wrong block and lead to register writes into the wrong region.
- Some cfgs set `no_pcs_sw_reset`, which changes reset ownership and uses lazy reset acquisition. Reset naming or dependency mistakes can create deferred-probe or calibration failures.
- `qmp_ufs_power_on()` sets `SW_PWRDN` but does not program tables; table programming is in `.calibrate`, so the UFS host must call PHY ops in the expected order.

## Test signals

- Build coverage: `CONFIG_PHY_QCOM_QMP_UFS`, all included QMP register headers, and OF match table compile checks.
- Probe-time signals: successful regulator/clock/reset acquisition, successful ioremap path for both legacy and flat bindings, and symbol clock provider registration.
- Runtime signals: `phy initialization timed-out` from failed `PCS_READY` polling; regulator or clock enable errors; invalid submode errors.
- Hardware tests should include link bring-up for each compatible family, HS Series A/B mode selection, G4/G5 overlay selection, two-lane and one-lane devices, suspend/resume through the UFS stack, and repeated power-cycle/calibrate sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-ufs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb-legacy.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb-legacy.c

## Purpose

This file is the legacy Qualcomm QMP USB3 plus DP PHY driver. It covers older USB3 PHY bindings that also require DP common-block programming and dual-lane register maps. It exposes one generic PHY to the USB controller, registers the 125 MHz pipe clock source, manages runtime PM autonomous wake mode, and performs SoC-specific register table programming for QMP v3/v4/v5 USB3 PHYs.

The “legacy” distinction matters in three ways: the file keeps its own local `struct qmp_phy_init_tbl` and table writer, it explicitly programs `dp_com` reset/mode registers, and it expects legacy child-node resource layouts with TX/RX/PCS/TX2/RX2/PCS_MISC resources.

## Important APIs, types, and data

- `struct qmp_phy_init_tbl` and `QMP_PHY_INIT_CFG(_LANE)` define offset/value/lane-mask table entries local to this driver.
- `enum qphy_reg_layout` normalizes PCS offsets for software reset, start, status, autonomous mode, LFPS/RXTERM interrupt clear, and power-down control.
- `struct qmp_usb_legacy_offsets` exists for flat mappings, with offsets for `serdes`, `pcs`, `pcs_usb`, `tx`, and `rx`.
- `struct qmp_phy_cfg` binds each compatible to SERDES/TX/RX/PCS/PCS_USB tables, clock names, reset names, regulator names, register layout, and optional `pcs_usb_offset`.
- `struct qmp_usb` stores mapped register bases, `dp_com`, pipe clock, bulk clocks, resets, regulators, current `enum phy_mode`, generic PHY, and the fixed-rate pipe-clock provider.
- `qmp_usb_legacy_of_match_table` supports compatibles including `qcom,sc7180-qmp-usb3-phy`, `qcom,sdm845-qmp-usb3-phy`, `qcom,sm8150-qmp-usb3-phy`, `qcom,sm8250-qmp-usb3-phy`, `qcom,sm8350-qmp-usb3-phy`, and `qcom,sm8450-qmp-usb3-phy`.

The generic PHY ops are intentionally combined:

- `.init = qmp_usb_legacy_enable`, which calls init plus power-on.
- `.exit = qmp_usb_legacy_disable`, which calls power-off plus exit.
- `.set_mode = qmp_usb_legacy_set_mode`.

## Control flow

Probe:

1. `qmp_usb_legacy_probe()` allocates runtime state, stores driver data, fetches the compatible cfg, initializes bulk clocks, resets, and regulator arrays from cfg names.
2. If a child node exists, `qmp_usb_legacy_parse_dt_legacy()` maps parent resources 0 and 1 as SERDES and DP_COM, then maps child resources as TX, RX, PCS, TX2, RX2, optional PCS_MISC, and pipe clock from the child.
3. If no child exists, `qmp_usb_legacy_parse_dt()` maps one base resource, derives block bases from cfg offsets, and gets the `"pipe"` clock.
4. Runtime PM is enabled but forbidden by default, preserving opt-in sysfs behavior.
5. `phy_pipe_clk_register()` registers a 125 MHz fixed-rate pipe clock provider using `clock-output-names`.
6. The driver creates and publishes a generic PHY.

PHY enable:

1. `qmp_usb_legacy_init()` enables supplies, asserts/deasserts resets, enables configured clocks, initializes DP_COM via `qmp_usb_legacy_init_dp_com()`, and sets `SW_PWRDN`.
2. `qmp_usb_legacy_power_on()` writes SERDES tables, enables the pipe clock, writes lane 1 and lane 2 TX/RX tables, writes PCS tables, delays briefly, clears PCS software reset, starts SERDES and PCS, and polls `QPHY_PCS_STATUS` until `PHYSTATUS` clears.
3. If pipe-clock enable or polling fails, the function unwinds the pipe clock and returns an error.

PHY disable:

1. `qmp_usb_legacy_power_off()` disables the pipe clock, asserts PCS software reset, clears start bits, and powers the PHY down.
2. `qmp_usb_legacy_exit()` asserts resets, disables bulk clocks, and disables regulators.

Runtime PM:

- `qmp_usb_legacy_runtime_suspend()` checks `qmp->phy->init_count`, enables autonomous LFPS/RXTERM wake mode, then disables pipe and bulk clocks.
- `qmp_usb_legacy_runtime_resume()` restores clocks and disables autonomous mode.

## State and persistence behavior

The driver keeps volatile state only: current PHY mode, resource handles, mapped register bases, and the pipe-clock provider object. Register writes persist only while the PHY retains power. Runtime suspend intentionally leaves enough PCS autonomous-mode state for wake detection while disabling clocks.

`qmp->mode`, set by `qmp_usb_legacy_set_mode()`, controls which autonomous wake interrupt mask is used. Host/device SuperSpeed modes enable LFPS detection; other modes select receiver-detect behavior.

## Dependencies and integration points

- Linux platform, device tree, PHY, regulator, reset, clock, and runtime PM frameworks.
- QMP register headers for PCS USB v4/v5, PCS misc v3, and DP COM v3.
- USB controller consumers receive the PHY through the OF PHY provider.
- GCC/clock-controller integration depends on the fixed-rate pipe clock provider and a corresponding `"pipe"` clock consumer path.
- DP common-register programming is local to this driver and assumes USB3 plus DP shared reset/mode controls.

## Risks and edge cases

- The legacy child resource order is rigid. Misordered TX/RX/PCS/TX2/RX2 resources can write tuning values into the wrong MMIO region.
- DP_COM programming hard-codes default Type-C orientation to CC1 and enables both USB3 and DP mode bits. Boards with different orientation handling depend on higher-level muxing not represented here.
- The driver always configures `tx2` and `rx2` in power-on. The supported cfgs are dual-lane, but any future single-lane legacy cfg would need careful changes.
- Runtime PM reads `qmp->phy->init_count` directly. That is a common in-tree pattern but is sensitive to PHY core semantics.
- `pcs_usb` falls back to `pcs` for autonomous-mode registers. A bad `pcs_usb_offset` or missing layout entry can break wake signaling.
- Because `.init` includes power-on and `.exit` includes power-off, this driver’s operation ordering differs from newer drivers that separate `.power_on`.

## Test signals

- Build coverage under the relevant Qualcomm QMP USB legacy config, including local table helpers and DP COM register definitions.
- Probe should verify clock/reset/regulator acquisition, DP_COM ioremap for legacy bindings, pipe clock registration, and OF PHY provider publication.
- Runtime logs to watch: `reset assert failed`, `reset deassert failed`, `pipe_clk enable failed`, and `phy initialization timed-out`.
- Hardware tests should cover USB3 enumeration, host/device mode changes, runtime suspend/resume wake detection, pipe clock parenting through GCC, and boards using each listed compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb-legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb.c -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb.c

## Purpose

This file is the current standalone Qualcomm QMP USB3/USB3 UNI PHY platform driver. It supports many QMP generations and SoCs, including IPQ, MSM8996, QDU1000, SA8775P, SC8280XP, SDX55/65/75, SM8150/8250/8350, X1E80100, QCS8300, and Glymur USB3 UNI PHY. It programs SERDES/TX/RX/PCS/PCS_USB tables, registers the pipe clock source, supports runtime PM autonomous wake mode, and exposes a Linux generic PHY.

Compared with `phy-qcom-qmp-usb-legacy.c`, this driver uses shared QMP table helpers from `phy-qcom-qmp-common.h`, handles mostly single-lane USB3 PHYs, uses optional input clock acquisition for flat bindings, and has workarounds for overlapping legacy PCS mappings on selected compatibles.

## Important APIs, types, and data

- `struct qmp_usb_offsets` describes flat single-resource layouts: `serdes`, `pcs`, `pcs_misc`, `pcs_usb`, `tx`, and `rx`.
- `struct qmp_phy_cfg` maps a compatible to init tables, regulator data, register layout, optional power-down delay, and optional `pcs_usb_offset`.
- `struct qmp_usb` contains runtime state: device, cfg, register bases, pipe clock, bulk clocks/resets, regulators, current mode, generic PHY, and fixed-rate pipe clock object.
- Register layout arrays `qmp_v2_usb3phy_regs_layout` through `qmp_v7_usb3phy_regs_layout` abstract generation-specific PCS offsets.
- The table families tune PLL and spread-spectrum settings, TX impedance/drive, RX CDR/equalization, PCS lock detection, receiver detect delays, LFPS, and RXEQ training.
- `glymur_usb3_uniphy_cfg` uses v8-style SERDES/TX/RX/PCS/PCS_USB tables and `qmp_usb_offsets_v8`, but its standalone USB3 tables reference the non-USB43 `QSERDES_V8_*` and `QPHY_V8_*` maps rather than the USB4.3-specific headers.

The generic PHY ops are:

- `.init = qmp_usb_enable`
- `.exit = qmp_usb_disable`
- `.set_mode = qmp_usb_set_mode`

Internally, `.init` calls `qmp_usb_init()` and `qmp_usb_power_on()`, while `.exit` calls `qmp_usb_power_off()` and `qmp_usb_exit()`.

## Control flow

Probe:

1. `qmp_usb_probe()` allocates `struct qmp_usb`, stores it as device driver data, reads OF match data, and gets cfg-specific regulators with `devm_regulator_bulk_get_const()`.
2. If a legacy child node exists, `qmp_usb_parse_dt_legacy()` maps parent resource 0 as SERDES, maps child TX/RX/PCS/PCS_MISC resources, optionally sets `pcs_usb` from `pcs_usb_offset`, obtains the child pipe clock, gets all parent clocks, and initializes legacy reset names (`phy`, `common`). For SDX65 and SM8350 UNI legacy bindings it deliberately allows overlapping PCS mappings via `qmp_usb_iomap(..., exclusive=false)`.
3. If no child exists, `qmp_usb_parse_dt()` maps one resource, derives all sub-block bases from `cfg->offsets`, initializes optional standard clocks (`aux`, `cfg_ahb`, `ref`, `com_aux`), gets the `"pipe"` clock, and initializes flat-binding reset names (`phy_phy`, `phy`).
4. Runtime PM is enabled and then forbidden by default.
5. `phy_pipe_clk_register()` publishes a fixed 125 MHz pipe clock source from `clock-output-names`.
6. The generic PHY is created and registered with `of_phy_simple_xlate`.

Enable and link bring-up:

1. `qmp_usb_init()` enables regulators, asserts and deasserts reset controls, enables bulk clocks, and sets `SW_PWRDN`.
2. `qmp_usb_power_on()` writes SERDES tables, enables the pipe clock, programs TX/RX lane 1 tables, programs PCS and optional PCS_USB tables, applies a 10-20 microsecond delay when `has_pwrdn_delay` is set, clears PCS software reset, starts SERDES and PCS, and polls until `PHYSTATUS` clears.
3. `qmp_usb_power_off()` disables the pipe clock, asserts PCS software reset, clears start bits, and clears `SW_PWRDN`.
4. `qmp_usb_exit()` asserts resets, disables bulk clocks, and disables regulators.

Runtime PM:

- `qmp_usb_runtime_suspend()` enables autonomous wake mode, disables pipe and bulk clocks, and skips work if the PHY is not initialized.
- `qmp_usb_runtime_resume()` restores clocks and disables autonomous mode.
- Autonomous mode clears pending IRQ state, selects LFPS/RXTERM interrupt masks based on `qmp->mode`, and toggles optional PCS_MISC clamp bits only when the layout provides `QPHY_PCS_MISC_CLAMP_ENABLE`.

## State and persistence behavior

Runtime state is volatile and held in `struct qmp_usb`. The main state variable is `qmp->mode`, which is used only for autonomous wake interrupt policy. Hardware state is maintained by register writes while the PHY is powered or while autonomous mode remains armed during runtime suspend. There is no disk persistence.

Clock and reset counts are runtime-discovered for legacy bindings but fixed to the standard optional clock/reset lists for flat bindings. Devm-managed resources handle cleanup on probe failure or device removal.

## Dependencies and integration points

- Linux PHY framework, OF platform matching, runtime PM, regulator bulk APIs, reset bulk APIs, and clock provider APIs.
- `phy-qcom-qmp-common.h` provides `qmp_configure()` and `qmp_configure_lane()`.
- `phy-qcom-qmp.h` and included register-map headers define QSERDES, PCS, PCS_USB, and PCS_MISC offsets.
- The USB controller consumes the published PHY and `"pipe"` clock. GCC consumes the fixed-rate pipe clock source as a parent for its gated pipe clock.
- Device tree must provide either the legacy child-node resource layout or the newer flat register region with compatible-specific offsets.

## Risks and edge cases

- The file is highly table-driven. Mistakes in a table, offset layout, or compatible-to-cfg mapping can pass compilation but fail as link training, enumeration, or intermittent signal-integrity issues.
- The `glymur_usb3_uniphy_cfg` uses `qmp_v7_usb3phy_regs_layout` with v8 data tables. That may be intentional compatibility, but it is a high-value review point whenever v8 PCS status or control offsets change.
- Overlapping PCS mapping exceptions for SDX65 and SM8350 legacy bindings are explicit FIXME areas. Binding cleanup could break old DTs if not coordinated.
- Runtime PM autonomous mode depends on the current PHY mode. If consumers do not call `.set_mode`, wake-detection policy defaults to the non-host/device branch.
- `qmp_usb_init()` does not program tables; table programming happens in power-on inside the combined `.init` wrapper. Future refactors must preserve this sequencing.
- `has_pwrdn_delay` is per-cfg. Missing it on hardware that needs the delay can create flaky initialization.

## Test signals

- Compile with all referenced QMP headers and compatibles enabled.
- Probe checks should verify regulator acquisition, both legacy and flat resource mapping, optional clock handling, reset names, pipe clock provider creation, and PHY provider registration.
- Runtime failures appear as regulator/clock/reset errors, `pipe_clk enable failed`, and `phy initialization timed-out`.
- Hardware validation should include SuperSpeed enumeration, host/device mode selection, runtime suspend/resume wake, repeated cable attach/detach, pipe clock parenting, and per-compatible smoke tests for both legacy child-node and flat DT bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb43-pcs-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb43-pcs-v8.h

## Purpose

This header defines USB4.3 v8 QMP PCS register offsets. It has no executable logic; it is a register-map contract used by table-driven Qualcomm QMP PHY drivers that need USB4.3-specific PCS offsets.

The header is included indirectly through the broader QMP register header stack and is used by USB4.3/DP combo PHY data, notably in `phy-qcom-qmp-combo.c`. The standalone USB3 driver in this work item uses `QPHY_V8_PCS_*` names for Glymur USB3 UNI PHY rather than these `QPHY_V8_USB43_PCS_*` names.

## Important APIs, types, and data

- Include guard: `QCOM_PHY_QMP_USB43_PCS_V8_H_`.
- The file exports preprocessor constants only.
- Register groups include:
  - Core control/status: `QPHY_V8_USB43_PCS_SW_RESET`, `QPHY_V8_USB43_PCS_PCS_STATUS1`, `QPHY_V8_USB43_PCS_POWER_DOWN_CONTROL`, and `QPHY_V8_USB43_PCS_START_CONTROL`.
  - Power and lock-detection tuning: `POWER_STATE_CONFIG1`, `LOCK_DETECT_CONFIG1/2/3/6`, and `REFGEN_REQ_CONFIG1`.
  - Receiver detect and synchronization: `RX_SIGDET_LVL`, `RCVR_DTCT_DLY_P1U2_L/H`, `RATE_SLEW_CNTRL1`, `TSYNC_RSYNC_TIME`, `RX_CONFIG`, and `TSYNC_DLY_TIME`.
  - Alignment and equalization: `ALIGN_DETECT_CONFIG1/2`, `PCS_TX_RX_CONFIG`, `EQ_CONFIG1/2/5`.

## Control flow

There is no control flow in this header. Consumers use these macros inside initialization tables, register-layout arrays, or direct MMIO accessors. The usual flow is that a driver selects a compatible-specific table, then common QMP helpers write values at these offsets relative to the mapped PCS base.

## State and persistence behavior

The header stores no state. The defined offsets name hardware registers whose values persist only according to PHY power/reset behavior. Any persistence semantics are determined by the consuming driver and the PHY hardware.

## Dependencies and integration points

- Consumed by Qualcomm QMP PHY C files through `#include "phy-qcom-qmp.h"` or direct includes.
- Depends on the v8 USB4.3 hardware register layout matching these offsets.
- Integrates with `qmp_phy_init_tbl` arrays and QMP helpers such as `qmp_configure()` in consuming drivers.

## Risks and edge cases

- Offset errors are severe because all table writes using the macro silently target the wrong hardware register.
- The names are USB4.3-specific. Mixing them with non-USB43 v8 PCS macros can be wrong even when numeric ranges look similar.
- Since the header has no compile-time validation against hardware, review must compare against vendor register documentation or known-good downstream tables.

## Test signals

- Compile-time signal: all consumers build with these macro names resolved.
- Runtime signal: USB4.3/DP PHY init reaches PCS-ready/PHY-status completion and links at expected rates.
- Regression tests should cover every consuming compatible that uses `QPHY_V8_USB43_PCS_*` constants, especially after adding or renumbering offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb43-pcs-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb43-qserdes-com-v8.h -->
# sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb43-qserdes-com-v8.h

## Purpose

This header defines the USB4.3 v8 QSERDES COM register map for Qualcomm QMP PHYs. It is a dense list of offsets for PLL, clocking, spread-spectrum clocking, VCO tuning, calibration, adaptive analog controls, status, and debug registers. It has no runtime code and exists so table-driven PHY drivers can use named offsets instead of literals.

The header is included by `phy-qcom-qmp.h` and is referenced by USB4.3/DP combo PHY tables in `phy-qcom-qmp-combo.c`. It is distinct from `phy-qcom-qmp-qserdes-com-v8.h`, which provides non-USB43 v8 `QSERDES_V8_COM_*` names used by the standalone USB3 Glymur tables.

## Important APIs, types, and data

- Include guard: `QCOM_PHY_QMP_USB43_QSERDES_COM_V8_H_`.
- The file exports `QSERDES_V8_USB43_COM_*` macro constants only.
- Major register groups:
  - Mode-specific PLL programming for modes 0, 1, and 2: SSC step sizes, clock endpoint divisors, CP/R/C controls, core clock dividers, lock compare registers, DEC start, fractional dividers, integrator loop gains, VCO tune, IVCO, and HS clock selection.
  - Common clock and PLL control: `BG_TIMER`, SSC period/adjust registers, post dividers, bias and buffer enables, sysclk controls, PLL enable/control, reset state machine controls, lock compare enable/config, VCO tune ranges/timers, clock select, and core clock enable.
  - Common mode and analog controls: `CMN_CONFIG_*`, `CMN_MODE*`, VCO DC level, additional controls/misc, auto-gain adjustment, adaptive analog config, and adaptive PLL controls.
  - Calibration/status/debug: IVCO calibration, early lock compare, VCO/bias wait cycles, PSM calibration, clock-forwarding config, DCC and LDO calibration, mode-operation status, sysclk detect status, reset state, PLL calibration status, debug buses, and `C_READY_STATUS`.

## Control flow

There is no executable control flow. A consuming driver writes these offsets through init tables, typically after selecting an SoC-specific compatible and mapping the QSERDES COM base. The same table infrastructure may write different mode-specific offsets during USB4.3, DisplayPort, or combo PHY setup.

## State and persistence behavior

The header itself has no mutable state. The hardware registers it names hold PHY PLL/calibration/control state while the PHY is powered and may reset according to hardware reset sequencing. Persistence and ordering are entirely controlled by the driver that writes these registers.

## Dependencies and integration points

- Included through `phy-qcom-qmp.h`, making the macros available to QMP PHY drivers.
- Used by USB4.3/DP combo PHY initialization tables, including `QSERDES_V8_USB43_COM_*` references in `phy-qcom-qmp-combo.c`.
- Integrates with `struct qmp_phy_init_tbl` table writes and common QMP helper functions.
- Must remain consistent with adjacent v8 USB4.3 PCS, PCS USB, TX/RX, LALB, and DP PHY headers.

## Risks and edge cases

- This is a large raw register map; transcription errors can be difficult to detect at compile time and may only appear as unstable PLL lock, failed link training, or rate-specific failures.
- Similar non-USB43 v8 names exist with different macro prefixes and a smaller/different map. Using the wrong namespace in a table can silently program the wrong offset if the numeric layout diverges.
- Mode 0/1/2 regions are repetitive. Copy-paste mistakes between mode-specific groups are likely and should be reviewed against hardware documentation.
- Status and debug offsets near the end of the file are read-oriented in many drivers; writing them accidentally through a table would be a table-construction bug, not a header bug.

## Test signals

- Compile all consumers that include `phy-qcom-qmp.h` and use `QSERDES_V8_USB43_COM_*` names.
- Hardware bring-up should confirm PLL lock and `C_READY_STATUS`/PCS-ready behavior across all supported USB4.3/DP modes and rates.
- Regression tests should include rate switching and low-power transitions, because many offsets tune mode-specific PLL, SSC, calibration, and clock-forwarding behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/qualcomm/phy-qcom-qmp-usb43-qserdes-com-v8.h -->
