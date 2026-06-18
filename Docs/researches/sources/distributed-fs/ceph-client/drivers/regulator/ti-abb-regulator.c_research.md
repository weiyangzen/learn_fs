# sources/distributed-fs/ceph-client/drivers/regulator/ti-abb-regulator.c

Purpose: TI SoC Adaptive Body Bias regulator driver for ABB LDO blocks. It presents body-bias operating points as regulator voltage selectors so OPP code can move between nominal, forward body bias, and reverse body bias modes.

Important APIs/types/functions: `struct ti_abb`, `struct ti_abb_info`, and `struct ti_abb_reg` hold mapped MMIO, per-voltage ABB mode data, masks, clock/timing data, and optional efuse/LDOVBB override resources. Regulator operations are `regulator_list_voltage_table`, `ti_abb_set_voltage_sel`, and `ti_abb_get_voltage_sel`. Hardware sequencing lives in `ti_abb_set_opp`, with helpers for read-modify-write, transaction-done polling/clearing, and LDOVBB override programming. Probe selects register layout from `ti_abb_of_match` and registers one always-on voltage regulator.

Control flow: probe maps base/control/setup, shared interrupt status, optional efuse and LDO override registers, reads timing and ABB table properties, programs SR2 wait count from clock rate, registers the regulator, then enables the ABB LDO. Voltage changes validate selector bounds, avoid redundant transitions, optionally fold efuse recommendations into ABB mode/vset, clear stale transaction bits, program FBB/RBB and OPP selection, apply LDOVBB override in mode-dependent order, trigger `opp_change`, wait for transaction completion, and update `current_info_idx`.

State and persistence: persistent hardware state is in MMIO control/setup/LDOVBB registers and shared interrupt status. Driver state caches the current selector, but starts at `-EINVAL` because bootloader bias state is unknown. DT tables and efuse data define the supported selector-to-bias mapping.

Dependencies and integration points: platform device, OF properties/resources, clock framework, regulator core, MMIO accessors, and OPP/regulator consumers. The interrupt-status resource may be shared, so it is mapped without exclusive resource reservation.

Risks: transition sequencing is hardware sensitive; LDOVBB override ordering is explicitly required to avoid VBB glitches. Missing or zero DT timing/mask properties fail probe. Poll loops depend on `ti,settling-time`; bad values can cause false timeouts. Shared interrupt status clearing must not disturb other ABB users beyond the documented mask.

Test signals: boot probe with all compatible layouts, DT validation for `ti,abb_info`, efuse and no-efuse paths, voltage selector changes across all ABB modes, timeout injection for transaction done, and OPP transitions that verify no redundant writes when two selectors map to identical ABB data.
