## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-power.h

### Purpose
This header defines i.MX952 power-domain and performance-domain binding IDs for devicetree users. It is the symbolic mapping from DTS `power-domains` and performance-domain references to the provider's numeric domain table.

### Important APIs, Types, And Functions
There are no C functions or types. The exported macros are `IMX952_PD_*` for 21 power domains and `IMX952_PERF_*` for 12 performance domains. Domains cover analog, always-on, BBSM, camera, CCM/SRC/GPC, four A55 core domains plus A55 package, DDR, display, GPU, HSIO, M7, NETC, NoC, NPU, VPU, and wakeup.

### Control Flow
The header has no control flow. Its only behavior is preprocessor expansion into DTS cells, later decoded by Linux power/performance-domain providers during device attachment and runtime PM.

### State, Persistence, And Dependencies
The file persists no runtime state; compiled DTBs persist the numeric IDs. The values depend on the i.MX952 domain order exposed by firmware and the matching Linux provider tables.

### Integration Points
Integration points include i.MX952 DTSI files, generic PM domains, SCMI or NXP GPC providers, OPP/performance-domain bindings, and drivers for CPU clusters, DDR, camera, display, GPU, NPU, VPU, NETC, and HSIO devices.

### Risks
The key risk is cross-SoC confusion: i.MX952 has fewer A55 core domains than i.MX95 and lacks some i.MX95-specific performance IDs. Renumbering or transplanting macros between variants can power down the wrong block or fail to attach devices to PM domains.

### Test Signals
Useful signals include `dtbs_check`, provider probe logs, runtime PM cycling of each major domain, CPU idle/hotplug tests, suspend/resume, and comparison with firmware domain enumeration. Source reading signal: 44 lines; 34 `#define` entries; no includes or functions.
