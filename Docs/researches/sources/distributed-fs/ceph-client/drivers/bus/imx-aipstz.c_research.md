# sources/distributed-fs/ceph-client/drivers/bus/imx-aipstz.c

Purpose: configures the i.MX AIPSTZ secure AHB-to-IP bridge, applies SoC default access policy registers, enables runtime PM, and populates simple-bus children underneath the bridge.

Important APIs and types: `struct imx_aipstz_config` holds register defaults for MPR0 and OPACR0-4. `struct imx_aipstz_data` stores the mapped base and selected defaults. `imx_aipstz_apply_default()` writes the policy registers. Runtime resume reapplies the defaults after power-domain loss.

Control flow: probe allocates state, maps the first resource, retrieves match data, writes defaults, stores drvdata, marks runtime PM active, enables runtime PM with devm cleanup, and calls `of_platform_populate()` for `simple-bus` children. Remove depopulates children. Resume calls the same default writer.

State and persistence: policy register state lives in hardware and may be lost on power-off; the driver persists only the mapped base and immutable default config in memory. The imx8mp default sets MPR0 to allow trusted read/write and HPROT-derived privilege for masters 0-7.

Dependencies and integration: depends on OF matching, platform resources, runtime/system PM helpers, and child bus population. It integrates as a parent bus/bridge for devices behind AIPSTZ.

Risks: `devm_platform_get_and_ioremap_resource()` errors are reported as `-ENOMEM` rather than preserving the pointer error, which can hide probe-failure causes. Defaults are SoC-specific and sparse; unsupported OPACR defaults remain zero. Test signals include imx8mp probe, register writes, child device population, runtime suspend/resume restoring registers, system sleep force suspend/resume, and remove depopulation.
