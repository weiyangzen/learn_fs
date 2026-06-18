## sources/distributed-fs/ceph-client/drivers/fpga/altera-pr-ip-core-plat.c

Purpose: this small platform driver binds the generic Altera Partial Reconfiguration IP core implementation to OF-described MMIO devices.

Important APIs and functions: `alt_pr_platform_probe()` maps resource 0 with `devm_platform_ioremap_resource()` and passes the base address to `alt_pr_register()`. The OF table matches `altr,a10-pr-ip`.

Control flow: once a matching platform device probes, the driver maps the first MMIO resource and lets `altera-pr-ip-core.c` allocate private state and register an FPGA manager. There is no explicit remove path because all allocations and registration are devm-managed by the core register helper.

State and persistence: this wrapper has no independent runtime state. The associated FPGA manager state is stored by the core driver and hardware CSR registers.

Dependencies and integration: it depends on platform devices, OF matching, MMIO resource mapping, and the exported `alt_pr_register()` API from the core PR IP driver. Kconfig requires `ALTERA_PR_IP_CORE`, `OF`, and `HAS_IOMEM`.

Risks: the driver assumes the first resource is the PR IP CSR/data aperture. DT mistakes map directly into wrong MMIO access. It does not validate register revision or status before registration beyond the debug read performed in the core.

Test signals: test probe with missing resource, valid `altr,a10-pr-ip` DT node, deferred or failed MMIO mapping, and successful FPGA manager registration visible under the FPGA manager class.
