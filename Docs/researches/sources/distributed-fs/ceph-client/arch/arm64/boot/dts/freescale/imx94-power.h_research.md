## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx94-power.h

### Purpose
This header is a devicetree binding constant file for NXP i.MX94 power and performance domains. It gives DTS authors stable integer IDs for SCMI or platform power-domain references, so board `.dts` files can request domains such as A55 cores, DDR, display, HSIO, NETC, NPU, wakeup, and NoC without embedding raw numeric literals.

### Important APIs, Types, And Functions
There are no C functions or types. The exported API is the macro namespace: `IMX94_PD_*` for 19 power domains and `IMX94_PERF_*` for 11 performance domains. The domain IDs are contiguous, starting at zero, and therefore behave like ABI values rather than arbitrary local constants.

### Control Flow
The file has no executable control flow. It is preprocessed into DTS/DTSI sources or other binding consumers. Runtime behavior happens later in the Linux power-domain and performance-domain providers that interpret the numeric IDs from the flattened device tree.

### State, Persistence, And Dependencies
The header has only include guards and numeric macros. It depends on consumers preserving the firmware-facing ID order implied by the comment history and NXP platform binding. It persists no state, but compiled DTBs persist these values as firmware/kernel boot ABI data.

### Integration Points
Integration points are i.MX94 SoC DTSI files, board DTS files, SCMI or NXP GPC/power-domain providers, generic PM domain users, and OPP/performance-domain bindings. Kernel drivers indirectly depend on these IDs when their device nodes list `power-domains` or performance constraints.

### Risks
The primary risk is ABI drift: renumbering or reusing an existing macro would silently change the domain requested by already-authored device trees. A second risk is mismatch with firmware domain ordering, especially for similarly named M70/M71, A55 core/package, and HSIO top/wake-always-on domains.

### Test Signals
Useful signals include `dtbs_check` on i.MX94 DTS files, successful boot with power-domain provider probe logs, runtime PM suspend/resume of devices in display/HSIO/NETC/NPU domains, and comparison against the SCMI firmware domain table. Source reading signal: 41 lines; 31 `#define` entries; no includes or functions.
