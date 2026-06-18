<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect-clk.h -->
# sources/distributed-fs/ceph-client/include/linux/interconnect-clk.h

Purpose: Declares helpers for registering clocks as interconnect providers.

Important APIs/types/functions: `struct icc_clk_data` maps interconnect ids/names to clocks and bandwidth behavior. APIs `icc_clk_register()`, `devm_icc_clk_register()`, and `icc_clk_unregister()` create and destroy an interconnect provider backed by clock controls.

Control flow: Clock/interconnect glue drivers register provider data at probe; consumers request ICC bandwidth and provider code translates it into clock rates.

State/persistence: Provider state persists until unregister or devm cleanup.

Dependencies/integration: Integrates clock framework, interconnect provider framework, and device-managed resources.

Risks: Bandwidth-to-clock mapping must be conservative enough for consumers; unregister while paths are active can break constraints.

Test signals: Provider registration, consumer `icc_set_bw()` changing clock rates, devm cleanup, and disabled provider paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/interconnect-clk.h -->
