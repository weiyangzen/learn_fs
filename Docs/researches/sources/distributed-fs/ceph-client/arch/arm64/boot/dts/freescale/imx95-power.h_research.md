## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-power.h

### Purpose
This header defines devicetree binding IDs for i.MX95 power domains and performance domains. It lets DTS files refer to platform domains symbolically instead of hard-coding firmware or GPC numeric IDs.

### Important APIs, Types, And Functions
There are no C functions or types. The public macros are `IMX95_PD_*` for 23 power domains and `IMX95_PERF_*` for 13 performance domains. The domains cover analog, always-on, BBSM, camera, CCM/SRC/GPC, six A55 cores plus A55 package, DDR, display, GPU, HSIO top and wake-always-on, M7, NETC, NoC, NPU, VPU, and wakeup.

### Control Flow
The header has no control flow. DTS compilation turns macro names into cells, and runtime power management providers later interpret those cells when attaching devices to genpd or performance-domain abstractions.

### State, Persistence, And Dependencies
No runtime state is stored here. The numeric IDs persist in compiled DTBs and must remain aligned with NXP firmware and kernel provider tables. The file depends on include guards only, but semantically depends on i.MX95 power-management firmware/domain layout.

### Integration Points
Integration points include i.MX95 DTSI nodes, NXP GPC or SCMI power/performance providers, Linux generic PM domains, OPP/performance-domain consumers, and drivers for display, GPU, VPU, NPU, camera, NETC, HSIO, DDR, and Cortex-A55 clusters.

### Risks
The main risk is stable-ID breakage. i.MX95 has more A55 core domains than i.MX94/i.MX952, so copy/paste between SoC variants can attach devices or CPUs to the wrong domain. GPU/VPU/NPU/camera/display domains also tend to expose failures only when a workload first accesses the accelerator.

### Test Signals
Useful signals include `dtbs_check`, boot logs from the i.MX95 power-domain provider, CPU idle and hotplug tests for A55 domains, runtime PM tests for accelerators and display, and firmware table comparison. Source reading signal: 47 lines; 37 `#define` entries; no includes or functions.
