# sources/distributed-fs/ceph-client/drivers/clk/rockchip/gate-link.c

Purpose: implements late Rockchip linked-gate clocks that need a second clock kept active through runtime PM while the gate exists.

Important APIs/types/functions: `rk_clk_gate_link_probe()`, `rk_clk_gate_link_register()`, `struct rockchip_gate_link_platdata`, `rockchip_clk_get_lookup()`, `rockchip_clk_set_lookup()`, `pm_clk_add_clk()`, `devm_pm_runtime_enable()`, `devm_pm_clk_create()`, and runtime PM ops using `pm_clk_suspend`/`pm_clk_resume`.

Control flow: `rockchip_clk_register_late_branches()` creates a platform device carrying provider and branch platform data. The gate-link driver probes, enables runtime PM, creates a PM clock list, looks up the linked clock by `linked_clk_id`, adds it to PM clocks, registers the actual gate with `clk_register_gate()`, and stores it in the provider lookup table. On registration failure it removes the linked PM clock.

State and persistence: state is devres-managed PM runtime resources, PM clock membership, one registered gate clock, and the shared provider lookup table. Hardware gate state is still stored in the CRU register selected by the branch.

Dependencies and integration: Linux platform bus, CCF gate registration, PM clock framework, runtime PM, firmware node reuse from the parent clock controller, and Rockchip branch metadata.

Risks: missing platform data is fatal. A bad `linked_clk_id` can add an error-valued or wrong clock to PM handling. Since linked gates are registered late, consumers may defer until the platform device probes. Runtime PM behavior depends on parent device integration.

Test signals: linked gate consumer probing without permanent `-EPROBE_DEFER`, runtime suspend/resume toggling the linked clock as expected, clk summary showing the late gate, and negative tests for invalid linked IDs or unavailable PM clock setup.
