## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-clock.h

### Purpose
This header defines clock IDs for the NXP i.MX952 devicetree binding. It is a symbolic ABI for clock consumers in DTS files and for the i.MX952 clock provider that decodes clock specifier cells.

### Important APIs, Types, And Functions
There are no functions or types. The exported `IMX952_CLK_*` macro API is organized into clock source IDs, clock root IDs, GPR selector IDs, and CGC gate IDs. It includes PLLs, external clocks, A55/DRAM/display/GPU/HSIO/M7/NETC/NoC/NPU/VPU roots, wakeup and peripheral roots, audio mix roots, general-purpose timers, and clock gates for accelerators and mix-local resources.

### Control Flow
No executable flow exists in this file. DTS macros expand into integers, then runtime clock lookup and enable/rate operations are handled by the common clock framework and the i.MX952 provider.

### State, Persistence, And Dependencies
The header has no local state. Its IDs persist in DTBs. It depends on the i.MX952 clock-controller register/firmware numbering and on matching provider code that treats sources, roots, GPR selectors, and CGCs as one shared ID namespace.

### Integration Points
Integration points include i.MX952 DTSI clock-controller definitions, peripheral `clocks` properties, common clock framework consumers, assigned-clock setup, and SoC subsystems such as camera, display, GPU, NPU, VPU, HSIO, NETC, audio, and wakeup peripherals.

### Risks
The flat numeric namespace is easy to damage through insertion or renumbering. Reserved placeholders intentionally preserve numbering and should not be removed. i.MX952 diverges from i.MX95 by adding or renaming several roots and CGCs, so sharing DTS snippets across SoCs can reference unavailable clocks.

### Test Signals
Useful signals include `dtbs_check`, boot-time clock registration logs, `clk_summary` inspection, assigned-clock application, and functional testing of USB/PCIe, NETC, audio, display, camera, GPU/NPU/VPU, and storage. Source reading signal: 215 lines; 199 `#define` entries; no includes or functions.
