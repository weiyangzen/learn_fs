<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/omap_prm.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/ti/omap_prm.c

Purpose: Register-backed OMAP2+/AM3/AM4/DRA7 PRM driver providing generic PM domains and reset-controller services for PRM instances selected by DT resource base.

Important APIs/types/functions: `omap_prm_data` tables encode SoC-specific PRM base addresses, domain names, power-state registers, reset registers, clockdomain names, reset maps, and quirks. `omap_prm_domain` wraps genpd state and saved `PWRSTCTRL`. `omap_reset_data` wraps `reset_controller_dev`. Key functions: `omap_prm_domain_power_on/off()`, `omap_prm_domain_attach_dev/detach_dev()`, `omap_prm_domain_init()`, `omap_reset_status/assert/deassert()`, `omap_prm_reset_init()`, and `omap_prm_probe()`.

Control flow: probe matches a compatible table, maps resource 0, finds the table row whose `.base` equals `res->start`, initializes a genpd provider if `#power-domain-cells` exists, then registers reset controls if the instance has reset registers. Power-on restores saved control bits or current state and requests active/retention depending on flags, then polls transition clear. Power-off saves control, programs the lowest supported state, adjusts statechange/logic retention bits, and polls. Reset deassert clears status, optionally denies clockdomain idle, clears reset bit, waits for control/status completion, then allows idle.

State/persistence: PRM registers hold power and reset state. The driver saves `pwrstctrl_saved` across off/on so prior policy can be restored. Reset mask is synthesized from reset maps. `uses_pm_clk` tracks per-attached-device PM clock setup for `simple-pm-bus` children.

Dependencies/integration: integrates generic PM domains, reset-controller framework, TI platform data callbacks for clockdomain lookup/idle control, DT compatibles `ti,omap4-prm-inst`, `ti,omap5-prm-inst`, `ti,dra7-prm-inst`, `ti,am3-prm-inst`, `ti,am4-prm-inst`, and `linux/platform_data/ti-prm.h`.

Risks: table row selection by physical base address makes DT resource correctness critical. `omap_prm_domain_init()` calls `of_node_put(dev->of_node)`, which is unusual for an owned device node and should be reviewed carefully when changing probe lifetime. Reset code depends on platform data callbacks even in DT-era code. Power-off returns 0 even after a transition timeout, making failure visible only in logs. `rst_map_012` quirk asserts all resets on init.

Test signals: boot OMAP4/5/DRA7/AM3/AM4 DTs, validate genpd attach/detach for `simple-pm-bus`, reset controller xlate/status/deassert for each mapped reset line, suspend/resume transition polling, and timeout/error logging on invalid PRM instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/omap_prm.c -->
