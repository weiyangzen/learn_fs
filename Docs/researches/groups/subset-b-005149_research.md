# subset-b-005149 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/core.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/core.c

## Purpose

`core.c` is the generic PM domain (genpd) framework implementation. It registers and removes `struct generic_pm_domain` instances, attaches devices to domains, links parent/child domains, handles runtime PM and system sleep callbacks, selects and accounts idle states, forwards performance-state votes, and exposes OF provider helpers plus debugfs state.

The file is infrastructure, not a hardware provider. SoC drivers such as the i.MX GPC and block-control drivers populate `generic_pm_domain` callbacks and call `pm_genpd_init()` plus OF provider registration; this core then mediates all consumer device power transitions.

## Important APIs, types, and functions

- Global state includes `gpd_list`, `gpd_list_lock`, OF provider list state, `genpd_ida`, the `genpd_provider` bus, and optional debugfs root `pm_genpd`.
- Locking is abstracted by `genpd_lock_ops`, with mutex, spinlock, and raw spinlock implementations selected by domain flags such as `GENPD_FLAG_IRQ_SAFE` and `GENPD_FLAG_CPU_DOMAIN`.
- Public exported helpers include `pm_genpd_init()`, `pm_genpd_remove()`, `pm_genpd_add_device()`, `pm_genpd_remove_device()`, `pm_genpd_add_subdomain()`, `pm_genpd_remove_subdomain()`, `dev_pm_genpd_set_performance_state()`, `dev_pm_genpd_set_next_wakeup()`, `dev_pm_genpd_get_next_hrtimer()`, `dev_pm_genpd_synced_poweroff()`, `dev_pm_genpd_set_hwmode()`, `dev_pm_genpd_rpm_always_on()`, and `dev_pm_genpd_is_on()`.
- OF integration is provided by `of_genpd_add_provider_simple()`, `of_genpd_add_provider_onecell()`, `of_genpd_del_provider()`, `of_genpd_add_device()`, `of_genpd_add_subdomain()`, `of_genpd_parse_idle_states()`, and `of_genpd_sync_state()`.
- Device attach helpers `genpd_dev_pm_attach()`, `genpd_dev_pm_attach_by_id()`, and `genpd_dev_pm_attach_by_name()` parse `power-domains` and optionally create virtual devices for multi-domain consumers.
- Power flow internals include `_genpd_power_on()`, `_genpd_power_off()`, `genpd_power_on()`, `genpd_power_off()`, `genpd_runtime_suspend()`, `genpd_runtime_resume()`, and system-sleep helpers around prepare/noirq/complete.

## Control flow

Domain providers initialize a `generic_pm_domain`, set callbacks such as `power_on`, `power_off`, `attach_dev`, `detach_dev`, `set_performance_state`, or hardware-mode hooks, then call `pm_genpd_init()`. If device tree should bind consumers, providers register either a simple provider or onecell provider. Consumer devices attach through direct APIs or OF parsing; the core allocates `generic_pm_domain_data`, installs the genpd PM callback table into `dev->pm_domain`, adds PM QoS notifiers, and optionally powers the domain on.

Runtime suspend first consults the governor `suspend_ok` callback, runs the device's normal runtime suspend callback chain, invokes optional genpd stop hooks, then attempts to power off the domain if all devices and child domains are suspended. Runtime resume restores pending performance-state votes, powers parents and the domain back on, starts the device, then calls the device runtime resume chain. System sleep uses noirq callbacks to count suspended devices and performs synchronous domain power transitions when every child and device is ready.

## State and persistence behavior

Persistent software state lives in each `generic_pm_domain`: current `status`, `state_idx`, power-state table, device list, parent/child links, performance state, `sd_count`, prepared/suspended counters, `stay_on`, `synced_poweroff`, notifier chains, CPU masks, and governor timing data. Per-device state tracks timing, cached QoS constraints, runtime performance-state vote, default required OPP vote, hardware-mode cache, and `rpm_always_on`.

The core does not persist hardware state itself. It calls provider callbacks, and those callbacks write MMIO registers, firmware RPCs, clocks, regulators, or resets. Debugfs accounting updates `idle_time`, `on_time`, usage, rejected counts, and residency counters based on framework-observed transitions.

## Dependencies and integration points

The file depends on runtime PM, PM domains, PM QoS, OPP, PM clocks, OF, platform devices, debugfs, CPU/cpuidle support, workqueues, IDA allocation, and core device model buses. It integrates with DT through `power-domains`, `power-domain-names`, `domain-idle-states`, required OPPs, and provider `#power-domain-cells`. It integrates with governors through `struct dev_power_governor`, with providers through `struct generic_pm_domain`, and with consumers through `struct dev_pm_domain` callbacks.

## Risks and edge cases

- Parent/child locking order is delicate. Performance-state propagation and power recursion rely on nested locks and rollback paths; provider callbacks that mutate domain topology can break assumptions.
- IRQ-safe devices in sleepable domains cause domains to remain powered, so platform DT and provider flags must match callback context.
- The `stay_on` and `sync_state` behavior intentionally keeps boot-on domains enabled until provider sync; missing sync can leave domains unnecessarily on.
- Multi-domain consumers use virtual genpd devices. Required OPPs, detach paths, and runtime PM state must be validated for both real and virtual devices.
- Runtime PM, system sleep, and provider-owned runtime PM can interact; block-control providers that drive upstream domains by runtime PM depend on this sequencing.
- Removal is intentionally conservative: providers, child links, device attachments, and prepared counts can all make removal fail.

## Test signals

Useful signals include boot with `CONFIG_PM_GENERIC_DOMAINS`, `CONFIG_PM_GENERIC_DOMAINS_OF`, `CONFIG_PM_SLEEP`, `CONFIG_DEBUG_FS`, and `CONFIG_CPU_IDLE`; device-tree attach and detach for onecell and simple providers; runtime suspend/resume under PM QoS constraints; parent-child power ordering; performance-state propagation with rollback; required OPP defaults; sync_state power-off after boot; virtual devices for named and indexed domains; debugfs `pm_genpd_summary` and per-domain state files; and negative tests for invalid domain indexes, missing providers, removal while devices remain attached, IRQ-safe mismatches, and `pd_ignore_unused`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/governor.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/governor.c

## Purpose

`governor.c` implements genpd governor policies. It decides whether devices may runtime suspend, whether a domain may power down, which idle state should be selected, and, for CPU domains, whether cpuidle and latency constraints permit powering off.

## Important APIs, types, and functions

- `default_suspend_ok()` evaluates device resume-latency QoS against measured suspend/resume latency and child constraints, caching the result in `gpd_timing_data`.
- `update_domain_next_wakeup()` aggregates device and subdomain next-wakeup hints for domains using `GENPD_FLAG_MIN_RESIDENCY`.
- `_default_power_down_ok()` and `default_power_down_ok()` choose the deepest acceptable power state after considering subdomain and device off-time constraints.
- `cpu_power_down_ok()` adds CPU latency QoS, cpuidle next hrtimer, online CPU masks, and pending IPI checks.
- `cpu_system_power_down_ok()` selects a system-sleep state that meets CPU wakeup-latency limits.
- Exported governor instances are `simple_qos_governor`, `pm_domain_always_on_gov`, and, with CPU idle support, `pm_domain_cpu_gov`.

## Control flow

During runtime suspend, genpd calls the governor's `suspend_ok()` for each device before invoking the device callback. The default path reads the device resume-latency QoS, subtracts measured suspend/resume latencies, folds in children, and caches whether the device can be suspended. When the domain is a candidate for power-off, genpd calls `power_down_ok()`. The default governor aggregates next wakeup hints, invalidates parent cached decisions when local constraints change, and walks from deepest to shallowest state until off/on latency and residency constraints pass.

For CPU domains, the governor first runs the default device/domain checks, then examines online CPUs in the domain cpumask, cpuidle `next_hrtimer`, global and wakeup latency QoS, per-CPU raw resume latency, and pending IPIs before accepting an idle state.

## State and persistence behavior

The governor stores cached device decisions in `gpd_timing_data` and domain-wide decisions in `genpd_governor_data`: `max_off_time_ns`, `max_off_time_changed`, `cached_power_down_ok`, cached state index, aggregated next wakeup, next hrtimer, last-enter timestamp, and residency reflection flags. It updates `genpd->state_idx`; the core later accounts usage and rejected counts when actual power transitions succeed or fail.

## Dependencies and integration points

The file depends on `linux/pm_domain.h`, `linux/pm_qos.h`, hrtimers, cpuidle, CPU masks, and ktime. Its only users are genpd core and domains that select a governor in `pm_genpd_init()`. Device drivers influence it through PM QoS, runtime PM, next-wakeup hints, and measured suspend/resume latencies.

## Risks and edge cases

- Cached QoS decisions rely on `constraint_changed` and `max_off_time_changed`; missing invalidation can choose stale states.
- A QoS value of zero means do not suspend, while `PM_QOS_RESUME_LATENCY_NO_CONSTRAINT_NS` means unrestricted; confusing these values changes policy.
- `GENPD_FLAG_MIN_RESIDENCY` depends on fresh next-wakeup hints. Stale past wakeups are ignored, but missing updates can still reduce energy savings.
- CPU-domain decisions can be invalidated late by pending IPIs or hrtimer changes.
- State arrays are assumed ordered from shallow to deep; provider tables must preserve that order.

## Test signals

Validate suspend rejection for zero resume-latency QoS, acceptance for no-constraint QoS, child-device QoS aggregation, measured latency updates, min-residency next-wakeup state selection, cache invalidation after QoS changes, multi-state fallback from deep to shallow, CPU-domain hrtimer and IPI rejection paths, and debugfs idle-state usage/above/below counters after representative residency durations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/governor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Kconfig

## Purpose

This Kconfig fragment defines the i.MX PM-domain provider options and their build-time dependencies. It groups GPCv2, i.MX8M/i.MX9 block controllers, and SCU firmware-backed domains under the "i.MX PM Domains" menu.

## Important APIs, types, and functions

- `IMX_GPCV2_PM_DOMAINS` enables the GPCv2 provider for i.MX7D and i.MX8M-family SoCs. It depends on `ARCH_MXC` or OF compile-testing plus `PM`, selects `PM_GENERIC_DOMAINS` and `REGMAP_MMIO`, and defaults on for `SOC_IMX7D`.
- `IMX8M_BLK_CTRL` is a bool selected by `SOC_IMX8M && IMX_GPCV2_PM_DOMAINS`; it depends on genpd and common clock support.
- `IMX9_BLK_CTRL` is a bool selected by `SOC_IMX9 && IMX_GPCV2_PM_DOMAINS`; it depends on genpd.
- `IMX_SCU_PD` enables firmware/SCFW-backed domains and depends on `IMX_SCU`.

## Control flow

The file contributes only configuration. Kconfig resolution decides which C objects the companion Makefile can include. Selecting GPCv2 implicitly makes genpd and regmap-mmio available; selecting block controllers depends on the matching SoC symbols and base genpd support.

## State and persistence behavior

No runtime state exists here. The persistent effect is the generated kernel configuration, which controls whether provider drivers are compiled in and whether their initcalls, module tables, and OF matches can be present.

## Dependencies and integration points

This integrates with architecture symbols such as `ARCH_MXC`, `SOC_IMX7D`, `SOC_IMX8M`, and `SOC_IMX9`, generic PM-domain infrastructure, common clock, regmap MMIO, and the i.MX SCU firmware driver.

## Risks and edge cases

- `IMX8M_BLK_CTRL` and `IMX9_BLK_CTRL` are not user-visible prompts, so unexpected missing SoC symbols can silently omit needed providers.
- `IMX_SCU_PD` does not explicitly select `PM_GENERIC_DOMAINS`; it relies on the broader platform configuration making genpd available.
- Compile-test coverage for block controllers is narrower than GPCv2 because the block-controller options default from SoC symbols.

## Test signals

Run configuration matrix checks for i.MX7D, i.MX8M, i.MX9, SCU-enabled SoCs, and COMPILE_TEST. Confirm expected objects appear in `drivers/pmdomain/imx/`, symbols select genpd/regmap/common-clock dependencies, and DT compatibles used by boards have matching compiled drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Makefile

## Purpose

The i.MX PM-domain Makefile maps Kconfig symbols to provider objects. It is the build glue for legacy i.MX GPC, GPCv2, SCU power domains, i.MX8M block controls, i.MX93 slice domains, and i.MX9 block controls.

## Important APIs, types, and functions

- `CONFIG_HAVE_IMX_GPC` builds `gpc.o`.
- `CONFIG_IMX_GPCV2_PM_DOMAINS` builds `gpcv2.o`.
- `CONFIG_IMX_SCU_PD` builds `scu-pd.o`.
- `CONFIG_IMX8M_BLK_CTRL` builds both `imx8m-blk-ctrl.o` and `imx8mp-blk-ctrl.o`.
- `CONFIG_SOC_IMX9` builds `imx93-pd.o`.
- `CONFIG_IMX9_BLK_CTRL` builds `imx93-blk-ctrl.o`.

## Control flow

There is no runtime flow. Kbuild expands the selected `obj-*` entries into built-in or modular objects according to the resolved kernel configuration.

## State and persistence behavior

No runtime state exists. The persistent output is the kernel build graph and, for modular objects, module artifacts and OF module aliases.

## Dependencies and integration points

The file depends entirely on symbols defined in i.MX PM-domain Kconfig and architecture Kconfig. It integrates with platform drivers registered by the compiled C objects.

## Risks and edge cases

- `CONFIG_IMX8M_BLK_CTRL` intentionally builds both generic i.MX8M and i.MX8MP-specific block-controller files; changing this could break i.MX8MP HSIO/HDMI domains.
- `imx93-pd.o` is keyed directly to `CONFIG_SOC_IMX9`, while `imx93-blk-ctrl.o` uses `CONFIG_IMX9_BLK_CTRL`; mismatched symbols can include slice domains but omit media block controls.

## Test signals

Inspect `make V=1` output or `modules.order` for representative configs, verify each expected object is compiled, and run `modinfo`/built-in OF alias checks for module-capable providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpc.c

## Purpose

`gpc.c` implements legacy i.MX6 General Power Controller PM domains. It supports ARM, PU, DISPLAY, and PCI domains, including old onecell DT bindings and newer `pgc` child-node bindings. It controls GPC/PGC registers, optional regulators, and reset-propagation clocks.

## Important APIs, types, and functions

- `struct imx_pm_domain` embeds `generic_pm_domain` and stores regmap, regulator, reset clocks, PGC register offset, GPC control bit, and IPG clock rate.
- `imx6_pm_domain_power_on()` enables the optional regulator, prepares reset clocks, requests power-up through `GPC_CNTR`, polls for request completion, waits for reset propagation, and disables reset clocks.
- `imx6_pm_domain_power_off()` programs PGC gate-on-powerdown, requests power-down, waits ISO delay cycles derived from PGC delay registers and IPG rate, then disables the regulator.
- `imx_pgc_power_domain_probe()` registers a child PGC domain as a simple OF provider.
- `imx_gpc_old_dt_init()` supports old DTs with a onecell provider.
- Static `imx_gpc_domains[]` supplies domain descriptors, while `imx_gpc_dt_data` captures SoC-specific domain count and errata flags.

## Control flow

The top-level `imx_gpc_probe()` maps the GPC MMIO region into a restricted regmap, applies i.MX6 errata flags, and then follows either old or new DT flow. Old DT flow initializes static domains directly and registers a onecell provider at the GPC node. New DT flow finds the `pgc` child, reads each child's `reg`, allocates an `imx-pgc-power-domain` platform device, copies the static domain descriptor into platform data, fills regmap and IPG rate, and lets the child driver register a simple provider for that child node.

Power transitions are invoked by genpd through each domain's callbacks. The PU domain powers up during initialization so GPU/VPU users start from a known state.

## State and persistence behavior

Software state is mostly static domain descriptors plus copied child platform data. Runtime state is in GPC registers: PGC control, power-up/down request bits, status bits, and regulator/clock state. `GENPD_FLAG_RPM_ALWAYS_ON` and `GENPD_FLAG_ALWAYS_ON` are applied for errata, causing genpd to preserve affected domains at runtime or always.

## Dependencies and integration points

The driver depends on regmap MMIO, clocks, regulators, platform devices, OF child nodes, genpd, and device links. It matches `fsl,imx6q-gpc`, `fsl,imx6qp-gpc`, `fsl,imx6sl-gpc`, and `fsl,imx6sx-gpc`. Consumers bind via `power-domains` to either the top-level onecell provider or child PGC providers.

## Risks and edge cases

- Static domain descriptors are copied into child platform data; later mutation of the static template or copied instance must be understood carefully.
- IPG clock rate is divided to MHz. A zero or inaccurate rate would distort power-down ISO delay calculations.
- Errata flags deliberately override normal runtime PM behavior for PU or DISPLAY domains.
- Old binding removal only removes ARM and PU in the visible path; DISPLAY/PCI handling depends on old binding domain count and should be validated on i.MX6SL/SX.
- Missing optional regulators or too many clocks change sequencing and can expose reset-propagation failures.

## Test signals

Test old and new DT bindings, each compatible's domain count, PU regulator enable/disable, clock acquisition and cleanup, GPC request polling timeout, errata behavior on i.MX6QP/i.MX6SL, provider registration, runtime PM of GPU/VPU/display/PCI consumers, and removal paths with devices still attached versus detached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpcv2.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpcv2.c

## Purpose

`gpcv2.c` implements the i.MX7D and i.MX8M-family GPCv2 PGC power-domain provider. It describes SoC-specific domains, register access windows, CPU mapping bits, software power-up/down request bits, PGC control bits, optional regulators/resets/clocks, and ADB400 handshake bits.

## Important APIs, types, and functions

- `struct imx_pgc_domain` embeds `generic_pm_domain` and stores regmap, PGC register set, regulator, reset array, bulk clocks, PGC bitmap, request/mapping/handshake bits, optional voltage, keep-clocks flag, and owning device.
- `imx_pgc_power_up()` resumes the provider device, enables regulator, asserts reset, enables clocks, issues PUP requests, clears PGC power-control bits, deasserts reset, triggers handshake bits, and optionally leaves clocks enabled.
- `imx_pgc_power_down()` enables needed clocks, clears handshake request bits and polls ack deassertion, sets PGC power-control bits, issues PDN requests, disables clocks/regulator, and runtime-suspends the provider device.
- Static domain arrays cover i.MX7, i.MX8MQ, i.MX8MM, i.MX8MN, and i.MX8MP domain IDs from DT binding headers.
- `imx_pgc_domain_probe()` initializes one child domain and registers a simple provider; `imx_gpcv2_probe()` maps the top-level GPC and instantiates children from the `pgc` node.

## Control flow

The top-level driver matches a SoC-specific `imx_pgc_domain_data`, creates a regmap constrained to that SoC's valid register ranges, then walks available `pgc` child nodes. Each child `reg` index selects a static domain template that is copied into an `imx-pgc-domain` platform device. The child probe retrieves optional regulator, clocks, resets, maps the domain to A-core bits, initializes genpd as initially off, and registers a simple OF provider.

Power-on and power-off happen through genpd callbacks. System sleep temporarily takes a runtime PM reference on child provider devices so genpd system sleep can power nested domains down and back up without conflicting with the driver's use of runtime PM.

## State and persistence behavior

Domain state is held in copied domain descriptors and genpd status. Hardware state persists in GPC CPU mapping registers, PUP/PDN request registers, PGC control registers, PWRHSK handshake registers, regulator state, reset line state, and clock state. `keep_clocks` domains intentionally retain clocks across power-up when hardware needs them for shared logic or handshakes.

## Dependencies and integration points

The file depends on regmap MMIO, regulators, resets, clocks, runtime PM, genpd, OF child nodes, platform devices, and DT binding constants for i.MX7/i.MX8M power IDs. It integrates with block-controller drivers that add bus-clock or reset handling needed for some ADB handshakes.

## Risks and edge cases

- PGC offsets are noted as RTL-derived because some reference manuals are wrong; accidental "cleanup" to manual values would break hardware.
- Handshake bits differ by SoC and domain. Wrong ack/request masks can hang power transitions or skip necessary isolation.
- The power-up path intentionally delays instead of polling some handshakes because BLK-CTL bus clocks are owned elsewhere.
- Domains with `pxx = 0` rely on handshake-only sequencing; tests must not assume all domains issue PUP/PDN requests.
- Runtime PM references in power callbacks and system sleep must stay balanced on every error path.

## Test signals

Build and boot with each compatible (`fsl,imx7d-gpc`, `fsl,imx8mq-gpc`, `fsl,imx8mm-gpc`, `fsl,imx8mn-gpc`, `fsl,imx8mp-gpc`), validate all DT domain indexes, regulator voltage programming, reset array handling, clock bulk handling, PUP/PDN timeout paths, ADB handshake behavior with block controllers loaded, `GENPD_FLAG_ACTIVE_WAKEUP` USB domains during suspend, and runtime PM balance through suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpcv2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8m-blk-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8m-blk-ctrl.c

## Purpose

`imx8m-blk-ctrl.c` implements i.MX8M block-control PM-domain providers for VPU, display, and media blocks. These block controllers sequence reset bits, block clocks, upstream GPC domains, bus domains, interconnect paths, and domain-specific notifier workarounds that the generic GPC provider cannot model as simple parent-child genpd links.

## Important APIs, types, and functions

- `struct imx8m_blk_ctrl` holds the provider device, bus power-domain device, regmap, notifier, domain array, and onecell provider data.
- `struct imx8m_blk_ctrl_domain_data` describes each exported block domain: name, clock names, interconnect paths, upstream GPC domain name, reset mask, clock mask, and optional MIPI PHY reset mask.
- `imx8m_blk_ctrl_power_on()` powers the bus domain, asserts resets, enables clocks and block clock bits, resumes the upstream GPC domain, releases resets, programs ICC bandwidth, and disables temporary clocks.
- `imx8m_blk_ctrl_power_off()` asserts resets, clears clocks, suspends the upstream GPC domain, and releases the bus domain.
- Notifiers such as `imx8mm_vpu_power_notifier()`, `imx8mq_vpu_power_notifier()`, `imx8mm_disp_power_notifier()`, `imx8mn_disp_power_notifier()`, and `imx8mp_media_power_notifier()` prepare bus/reset state around upstream domain power notifications.

## Control flow

Probe maps the BLK_CTRL registers, attaches to the named `bus` power domain, allocates one genpd per table entry, acquires each domain's clocks and optional ICC paths, attaches to the named upstream GPC domain, initializes the genpd as off, applies a distinct lock class for nested genpd locks, registers a onecell provider, registers a notifier on the bus domain, and populates child devices.

Consumer runtime PM calls into the exported block domain. The block domain drives bus and upstream GPC domains using runtime PM rather than genpd parent links because the hardware requires reset and clock manipulations between parent and child transitions.

## State and persistence behavior

Software state is the `imx8m_blk_ctrl` instance, domain descriptors, attached power-domain devices, ICC path handles, and notifier registration. Hardware state persists in `BLK_SFT_RSTN`, `BLK_CLK_EN`, optional `BLK_MIPI_RESET_DIV`, VPU fuse-like registers, media/display QoS/cache registers, upstream GPC domains, clocks, and interconnect settings.

## Dependencies and integration points

The driver depends on genpd, runtime PM, regmap, clocks, interconnect framework, OF platform population, and DT power binding IDs for i.MX8MM/i.MX8MN/i.MX8MP/i.MX8MQ. It matches VPU, display, and media block-control compatibles and expects `power-domain-names` entries such as `bus`, `g1`, `g2`, `mipi-csi`, `lcdif`, `isp`, and others.

## Risks and edge cases

- Power sequencing is intentionally not a normal genpd hierarchy. Removing runtime PM based upstream sequencing can violate reset/clock ordering.
- Notifiers are needed for ADB handshakes where reset/clock bits live in BLK_CTRL; missing notifier registration can hang GPC power transitions.
- ICC paths use placeholder bandwidth `1` to trigger NoC configuration; absent ICC providers are tolerated except probe deferral.
- i.MX8MQ VPU reset/clock masks are deliberately omitted for G1/G2 to avoid hangs; per-domain reset manipulation would be unsafe there.
- Cleanup paths must detach already attached upstream domains and remove genpds in reverse partial-probe order.

## Test signals

Validate probe for every compatible, named power-domain attachment, onecell domain indexes, clock and ICC acquisition, notifier registration/removal, child device population, VPU fuse programming, media/display QoS programming, MIPI PHY reset bits, i.MX8MQ VPU hang avoidance, runtime PM on/off for each block domain, system suspend/resume runtime PM reference balancing, and lockdep behavior under nested block/GPC transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8m-blk-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8mp-blk-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8mp-blk-ctrl.c

## Purpose

`imx8mp-blk-ctrl.c` implements i.MX8MP-specific HSIO and HDMI block-control PM domains. It provides onecell genpd providers for sub-blocks, sequences upstream GPC domains, programs block-specific clock/reset/control registers, exposes an HSIO PLL clock, and guards upstream power-off while child block domains remain on.

## Important APIs, types, and functions

- `struct imx8mp_blk_ctrl` stores provider state, regmap, bus power-domain device, domain array, onecell data, and domain-specific power-on/off function pointers.
- `struct imx8mp_blk_ctrl_domain_data` describes domain names, clocks, ICC paths, upstream GPC domain names, and genpd flags.
- `clk_hsio_pll_*()` implements a simple 100 MHz HSIO PLL clock backed by block-control PLL registers and a lock poll.
- `imx8mp_hsio_blk_ctrl_power_on/off()` toggles USB/PCIe module clock enables and PCIe PHY resets.
- `imx8mp_hdmi_blk_ctrl_power_on/off()` programs HDMI RTX clock/reset/control bits for IRQSTEER, LCDIF, PAI, PVI, TRNG, HDMI TX, HDMI PHY, and HRV.
- `imx8mp_blk_ctrl_gpc_notifier()` rejects upstream GPC `GENPD_NOTIFY_PRE_OFF` while the corresponding block genpd is still on.

## Control flow

Probe maps registers, attaches the bus power domain, allocates per-domain genpds, gets optional ICC paths and clocks, attaches each named upstream GPC domain, registers a per-domain notifier on each upstream domain, initializes genpd domains, registers a onecell provider, registers a bus-domain notifier, and runs optional compatible-specific probe such as HSIO PLL registration.

Power-on resumes the bus domain, enables local clocks, runs HSIO or HDMI register programming, resumes the upstream GPC domain, programs ICC bandwidth, then disables temporary clocks. Power-off enables clocks, runs domain-specific register shutdown, disables clocks, then releases upstream and bus runtime PM references. System sleep temporarily resumes all upstream domains so generic sleep ordering can complete without conflicting with runtime PM sequencing.

## State and persistence behavior

State persists in block-control registers: HSIO GPR clock/reset/PLL fields and HDMI RTX clock/reset/control fields. Software state includes attached upstream devices, per-domain notifier blocks, onecell domain pointers, ICC handles, and the registered HSIO PLL clock provider. `GENPD_FLAG_ACTIVE_WAKEUP` is set for USB PHY domains.

## Dependencies and integration points

The driver depends on genpd notifiers, runtime PM, common clock provider APIs, regmap, clocks, ICC, OF, and DT binding IDs from `imx8mp-power.h`. It matches `fsl,imx8mp-hsio-blk-ctrl` and `fsl,imx8mp-hdmi-blk-ctrl`.

## Risks and edge cases

- Upstream GPC pre-off rejection is essential. If a parent GPC powers down while a block domain is on, block register state and consumers can break.
- HSIO notifier temporarily enables USB clocks for ADB handshakes; missing USB clock data can make parent power transitions fail.
- HDMI registers do not clear on powerdown, so the notifier explicitly resets clock/reset registers on power-up before releasing ADB reset.
- PLL programming is fixed to 100 MHz; parent rate changes or hardware variants would need explicit handling.
- Runtime PM references, notifier removal, and genpd removal must remain balanced across partial probe failures.

## Test signals

Test HSIO and HDMI compatibles, HSIO PLL registration and lock timeout, USB/PCIe/PCIe PHY domain toggles, HDMI subdomain toggles, ICC path programming, upstream pre-off rejection when block child is on, notifier cleanup, active-wakeup USB PHY suspend behavior, runtime PM balance through system suspend/resume, and lockdep under nested block/GPC domain transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx8mp-blk-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-blk-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-blk-ctrl.c

## Purpose

`imx93-blk-ctrl.c` implements i.MX91/i.MX93 media block-control PM domains. It exports onecell domains for media sub-blocks, controls block reset and clock-gate bits, manages bus clocks and runtime PM for the parent media slice, and programs QoS priority registers for display/camera/image pipelines.

## Important APIs, types, and functions

- `struct imx93_blk_ctrl` holds provider device, regmap, bus clocks, domain array, and onecell data.
- `struct imx93_blk_ctrl_domain_data` describes each domain's clocks, reset mask, clock mask, and optional QoS entries.
- `struct imx93_blk_ctrl_qos` identifies QoS register offsets and priority nibbles.
- `imx93_blk_ctrl_power_on()` enables bus and domain clocks, runtime-resumes the provider device, ungates clocks, releases resets, and applies QoS.
- `imx93_blk_ctrl_power_off()` asserts resets, gates clocks, runtime-suspends the provider, and disables clocks.
- `imx93_blk_ctrl_probe()` builds genpds, optionally skips unsupported domains on i.MX91, registers a onecell provider, and populates child devices.

## Control flow

Probe selects match data for i.MX91 or i.MX93, maps registers with an access table, gets shared media bus clocks, then iterates domain descriptors. Domains masked by `skip_mask` are left absent in the onecell array. Others get their local clocks, genpd callbacks, and cleanup actions. Runtime PM is enabled on the block-controller device before registering the onecell provider and populating child devices.

Power-on enables shared and local clocks before accessing registers, takes a runtime PM reference for the parent slice domain, clears `BLK_CLK_EN` bits to ungate clocks, sets `BLK_SFT_RSTN` bits to release reset, then writes configured QoS priorities. Power-off reverses reset/clock state and releases runtime PM and clocks.

## State and persistence behavior

Runtime state is held in genpd status, shared and local clock enable counts, runtime PM usage count, and block-control register values. QoS priorities persist in LCDIF, PXP, and ISI registers until changed or reset. i.MX91 intentionally leaves MIPI DSI and PXP domains skipped.

## Dependencies and integration points

The file depends on genpd, runtime PM, regmap MMIO with access tables, clocks, OF platform population, and `fsl,imx93-power.h` domain IDs. It matches `fsl,imx91-media-blk-ctrl` and `fsl,imx93-media-blk-ctrl`; child media devices consume the exported domains through DT.

## Risks and edge cases

- `BLK_CLK_EN` uses cleared bits to ungate and set bits to gate; this inverted meaning is easy to misread.
- Power-on returns immediately after QoS setup and does not disable clocks on a QoS write failure, although current QoS helper always returns zero.
- Skipped i.MX91 domains leave NULL onecell entries; consumers using those indexes should receive no domain.
- Shared bus clocks and runtime PM must be enabled before register writes.
- QoS masks assume paired configured/default priority nibbles at `cfg_off` and `cfg_off + 4`.

## Test signals

Validate i.MX91 skip-mask behavior, i.MX93 all-domain registration, onecell indexes, shared bus clock enable/disable, local clock failures, reset and clock-gate polarity, runtime PM parent slice interactions, QoS register values for LCDIF/PXP/ISI, child device population, and devm cleanup removing genpds and providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-blk-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-pd.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-pd.c

## Purpose

`imx93-pd.c` implements simple i.MX93 SRC slice power domains. Each platform device represents one slice with MMIO control/status registers and optional clocks. It registers a simple OF genpd provider for that slice.

## Important APIs, types, and functions

- `struct imx93_power_domain` embeds `generic_pm_domain` and stores the provider device, mapped MMIO base, bulk clocks, and clock count.
- `imx93_pd_on()` enables clocks, clears the software power-down bit, and polls `MIX_FUNC_STAT_OFF` until SSAR status clears.
- `imx93_pd_off()` sets the software power-down bit, polls until power-switch status asserts, and disables clocks.
- `imx93_pd_probe()` maps resources, acquires clocks, derives initial off/on state from isolation status, synchronizes clocks for initially-on domains, initializes genpd, and registers a simple OF provider.
- `imx93_pd_remove()` deletes the provider and removes the genpd.

## Control flow

The platform driver matches `fsl,imx93-src-slice`. Probe creates one genpd named after the device, checks whether hardware is isolated, keeps clocks enabled if the slice is already on, and passes the initial off state to `pm_genpd_init()`. Consumers attach through the slice node's provider. Genpd later calls `imx93_pd_on()` and `imx93_pd_off()` for runtime transitions.

## State and persistence behavior

Software state is per-device and small. Hardware state persists in `MIX_SLICE_SW_CTRL_OFF` power-down control and `MIX_FUNC_STAT_OFF` status bits for power switch, reset, isolation, and SSAR. Clock state is synchronized with the detected initial hardware state.

## Dependencies and integration points

The driver depends on platform resources, MMIO polling, bulk clocks, genpd, modules, and OF matching. It is built for i.MX9 via the Makefile and provides parent domains that block-control drivers can runtime-resume.

## Risks and edge cases

- `imx93_pd_on()` does not disable clocks if the SSAR poll times out, leaving clocks prepared after a failed power-up.
- Initial state detection uses isolation status; if firmware leaves mixed status bits, genpd state can be out of sync.
- Poll timeouts are fixed at 10 ms. Slow hardware or clock problems surface as probe/runtime errors.
- The file defines unused masks for reset/isolation/power-switch status beyond the two paths currently polled.

## Test signals

Test probe with slices initially on and off, clock acquisition with zero and multiple clocks, power-on SSAR timeout, power-off PSW timeout, provider attach by DT, block-controller runtime PM interactions, removal with consumers detached, and clock enable counts across failed and successful transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/imx93-pd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/scu-pd.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/scu-pd.c

## Purpose

`scu-pd.c` implements power domains backed by NXP i.MX System Controller Firmware. Instead of direct MMIO, each domain maps to an SCU resource ID and powers resources on or to low-power mode through SCFW PM RPCs. It supports i.MX8QXP-style resource ranges and custom OF translation by resource ID.

## Important APIs, types, and functions

- RPC message structs encode `SET_RESOURCE_POWER_MODE` and `GET_RESOURCE_POWER_MODE`.
- `struct imx_sc_pm_domain` embeds `generic_pm_domain`, a fixed-size generated name, and an SCU resource ID.
- `struct imx_sc_pd_range` describes resource ranges, name prefixes, count, postfix behavior, and starting display index.
- `imx_sc_pd_power()` sends SCU RPCs to set ON or LP mode and refuses to power down the console resource when `no_console_suspend` is active.
- `imx_scu_pd_xlate()` maps a DT `power-domains` resource ID argument to the matching generated genpd.
- `imx_scu_add_pm_domain()` checks resource ownership, creates and initializes one domain, reads initial SCU mode, and marks console domains runtime-always-on.

## Control flow

Probe obtains the global SCU IPC handle, chooses SoC range data, parses the stdout power-domain resource if present, then expands every resource range. Owned resources become genpd instances; unowned resources are skipped. The driver builds a compact onecell array of created domains and registers it with a custom xlate callback that searches by resource ID rather than direct array index.

Power transitions are direct SCU RPC calls. Power-on requests `IMX_SC_PM_PW_MODE_ON`; power-off requests `IMX_SC_PM_PW_MODE_LP`, except the active console resource may return `-EBUSY` to keep console usable.

## State and persistence behavior

Software state consists of generated domain objects, their names and SCU resource IDs, the global SCU IPC handle, and the console resource ID. Actual power state persists in SCFW-managed resource modes, not kernel MMIO. Initial genpd state is synchronized by querying SCFW power mode.

## Dependencies and integration points

The driver depends on the i.MX SCU firmware IPC and resource-management APIs, DT binding resource IDs, OF stdout parsing, genpd, and platform driver infrastructure. It matches `fsl,imx8qxp-scu-pd` and `fsl,scu-pd`; consumers pass SCU resource IDs in `power-domains`.

## Risks and edge cases

- The onecell array is compacted after skipping unowned resources, so the custom xlate by resource ID is mandatory. Replacing it with default index translation would be wrong.
- `imx_sc_get_pd_power()` returns `msg.data.resp.mode` even after an RPC error, which may be stale or uninitialized.
- Domain names have a fixed 20-byte buffer; long prefixes plus indexes could truncate.
- Console keepalive depends on correctly parsing `of_stdout` and only covers the first power-domain specifier.
- There is no remove path deleting the OF provider; this is built-in and effectively permanent.

## Test signals

Validate SCU handle acquisition, resource ownership filtering, generated domain names, custom xlate for several resource IDs, initial mode synchronization, console `no_console_suspend` behavior, RPC failures for get/set mode, skipped unowned resources, consumers with multi-domain specs, and boot on both `fsl,imx8qxp-scu-pd` and fallback `fsl,scu-pd` compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/scu-pd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/Kconfig

## Purpose

This Kconfig fragment defines the Marvell PM-domain menu and the `PXA1908_PM_DOMAINS` provider option for Marvell MMP/PXA1908 systems.

## Important APIs, types, and functions

- The menu is visible when `ARCH_MMP` or `COMPILE_TEST` is enabled.
- `PXA1908_PM_DOMAINS` is a tristate prompt for Marvell PXA1908 power domains.
- It depends on OF and PM, defaults to `y` for `ARCH_MMP && ARM64`, and selects `AUXILIARY_BUS`, `MFD_SYSCON`, `PM_GENERIC_DOMAINS`, and `PM_GENERIC_DOMAINS_OF`.

## Control flow

The file only influences configuration. If enabled, the companion Makefile builds the PXA1908 power-controller object as built-in or module according to the tristate value.

## State and persistence behavior

No runtime state exists here. Persistent effects are the kernel configuration and selected framework dependencies required by the Marvell provider.

## Dependencies and integration points

The option integrates with OF-based genpd providers, syscon/regmap access through MFD syscon, auxiliary bus support, and Marvell MMP architecture symbols.

## Risks and edge cases

- The help text contains a typo ("power domanis"), harmless but visible in configuration UI.
- Default enablement is restricted to ARM64 ARCH_MMP; other build targets need explicit selection or COMPILE_TEST.
- Because the provider is tristate, module autoloading depends on correct OF module aliases in the C driver.

## Test signals

Validate Kconfig dependency closure, built-in and module builds, COMPILE_TEST builds, default selection on ARCH_MMP ARM64, and that enabling the option selects genpd OF, syscon, and auxiliary bus support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/Makefile

## Purpose

The Marvell PM-domain Makefile maps `CONFIG_PXA1908_PM_DOMAINS` to the PXA1908 power-controller object.

## Important APIs, types, and functions

- `obj-$(CONFIG_PXA1908_PM_DOMAINS) += pxa1908-power-controller.o` is the only build rule.

## Control flow

There is no runtime flow. Kbuild includes `pxa1908-power-controller.o` when the Kconfig symbol is enabled.

## State and persistence behavior

No runtime state exists. The persistent effect is whether the PXA1908 provider is present in the built kernel or as a module.

## Dependencies and integration points

The Makefile depends on the Marvell Kconfig symbol and integrates with the provider source file of the same directory.

## Risks and edge cases

- Any source rename must update this single object mapping or the Kconfig option will produce no driver.
- Module versus built-in behavior follows the tristate symbol, so tests should cover both paths.

## Test signals

Check `make drivers/pmdomain/marvell/` with `PXA1908_PM_DOMAINS=y` and `m`, inspect generated object/module lists, and confirm module aliases are available when built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/marvell/Makefile -->
