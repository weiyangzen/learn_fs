# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_power.c

Purpose: implements IPA clock/interconnect power management, runtime/system PM callbacks, and optional AOSS/QMP register-retention signaling.

Important APIs/functions: `ipa_power_init()` gets and sets the core clock, allocates interconnect bulk data, sets bandwidth, initializes retention QMP, and enables runtime PM autosuspend. `ipa_power_exit()` reverses that. `ipa_core_clock_rate()` supplies endpoint timing code. `ipa_power_retention()` sends AOSS QMP messages to enable/disable register retention. `ipa_pm_ops` wires system and runtime suspend/resume callbacks.

Control flow: runtime resume enables interconnects then the core clock, then resumes GSI/endpoints if setup is complete. Runtime suspend suspends modem/AP endpoints and GSI before disabling clock/interconnects. System suspend disables the IPA IRQ line before forcing runtime suspend; resume forces runtime resume and re-enables IRQ so threaded interrupt handling cannot race while PM runtime is disabled.

State/persistence: `struct ipa_power` owns device pointer, core clock, optional QMP handle, interconnect count, and flexible interconnect array. Runtime PM autosuspend delay is 500 ms. Power state is otherwise managed by PM core reference counts.

Dependencies/integration: depends on Linux clock, interconnect, runtime/system PM, Qualcomm AOSS QMP, endpoint suspend/resume, GSI suspend/resume, interrupt IRQ enable/disable, and modem resume queue wake behavior.

Risks: ordering matters: buses before clock on enable, endpoints/GSI before power off on suspend, IRQ disabled around forced runtime PM. Fixed interconnect bandwidth/clock rates come from `ipa_data`; wrong data can underpower traffic. Retention QMP failures are logged but not fatal.

Test signals: runtime autosuspend occurs without traffic loss, system suspend wakes through IPA IRQ when configured, core clock rate is nonzero during endpoint timer programming, and interconnect/clock errors unwind cleanly at probe.
