# sources/distributed-fs/ceph-client/drivers/net/pse-pd/pse_regulator.c

Purpose: implements a minimal platform PSE provider backed by a single regulator. It targets simple PoDL-style Ethernet power sourcing without automatic classification or chip-specific telemetry.

Important APIs and functions: `pse_reg_probe()` obtains the exclusive `"pse"` regulator, derives the initial admin state from `regulator_is_enabled()`, initializes `pse_controller_dev`, and registers it with the PSE core. PSE callbacks `pse_reg_pi_enable()`, `pse_reg_pi_disable()`, `pse_reg_pi_get_admin_state()`, and `pse_reg_pi_get_pw_status()` toggle/read the regulator and report PoDL admin/power status.

Control flow: platform probe requires an OF node compatible with `"podl-pse-regulator"`. After registration, the PSE core creates a PI regulator for consumers. Enable/disable requests from ethtool or regulator users call through the core into this driver, which directly enables or disables the underlying supply and updates cached admin state. Power status is simply delivering when the regulator is enabled and disabled otherwise.

State and persistence: `struct pse_reg_priv` stores the embedded `pse_controller_dev`, the backing regulator pointer, and cached PoDL admin state. There is no chip memory, port matrix, interrupt state, or durable persistence beyond the actual regulator output state.

Dependencies and integration: depends on platform driver binding, OF, regulator consumer APIs, and PSE core. It advertises `ETHTOOL_PSE_PODL` only and does not support C33 status, power class, power limits, voltage/current telemetry, or IRQ notifications.

Risks and test signals: risks are regulator exclusivity conflicts, cached admin state drifting if external regulator users modify state, lack of classification/status detail, and single-line assumptions from default `nr_lines`. Test signals include probe deferral for missing regulator, initial enabled/disabled state reporting, enable/disable idempotence through ethtool, module unload with devm cleanup, and behavior when regulator operations fail.
