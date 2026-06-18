# subset-b-000562 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun4i-a10-mbus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun4i-a10-mbus.yaml

## Purpose
The MBUS controller drives the MBUS that other devices in the SoC will use to perform DMA. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun5i-a13-mbus`, `allwinner,sun8i-a33-mbus`, `allwinner,sun8i-a50-mbus`, `allwinner,sun8i-a83t-mbus`, `allwinner,sun8i-h3-mbus`, `allwinner,sun8i-r40-mbus`, `allwinner,sun8i-v3s-mbus`, `allwinner,sun8i-v536-mbus`, `allwinner,sun20i-d1-mbus`, `allwinner,sun50i-a64-mbus`, plus 5 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun5i-a13-mbus, allwinner,sun8i-a33-mbus, allwinner,sun8i-a50-mbus, allwinner,sun8i-a83t-mbus...), `reg` (items 1..?), `reg-names` (items 1..?), `interrupts` (items ?..1; MBUS PMU activity interrupt.), `clocks` (items 1..?), `clock-names` (items 1..?), `#address-cells`, `#size-cells`, `#interconnect-cells` (const 1; The content of the cell is the MBUS ID.), `dma-ranges` (See section 2.3.9 of the DeviceTree Specification.). Required properties are `#interconnect-cells`, `compatible`, `reg`, `clocks`, `dma-ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/sun50i-a64-ccu.h, dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/sunxi/allwinner,sun4i-a10-mbus.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun5i-a13-mbus`, `allwinner,sun8i-a33-mbus`, `allwinner,sun8i-a50-mbus`, `allwinner,sun8i-a83t-mbus`, `allwinner,sun8i-h3-mbus`, `allwinner,sun8i-r40-mbus`, `allwinner,sun8i-v3s-mbus`, `allwinner,sun8i-v536-mbus`, `allwinner,sun20i-d1-mbus`, `allwinner,sun50i-a64-mbus`, plus 5 more
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun4i-a10-mbus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun6i-a31-cpuconfig.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun6i-a31-cpuconfig.yaml

## Purpose
Device-tree schema for Allwinner CPU Configuration Controller. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun6i-a31-cpuconfig`, `allwinner,sun8i-a23-cpuconfig`, `allwinner,sun8i-a83t-cpucfg`, `allwinner,sun8i-a83t-r-cpucfg`, `allwinner,sun9i-a80-cpucfg`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun6i-a31-cpuconfig, allwinner,sun8i-a23-cpuconfig, allwinner,sun8i-a83t-cpucfg, allwinner,sun8i-a83t-r-cpucfg...), `reg` (items ?..1). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/sunxi/allwinner,sun6i-a31-cpuconfig.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun6i-a31-cpuconfig`, `allwinner,sun8i-a23-cpuconfig`, `allwinner,sun8i-a83t-cpucfg`, `allwinner,sun8i-a83t-r-cpucfg`, `allwinner,sun9i-a80-cpucfg`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun6i-a31-cpuconfig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun9i-a80-prcm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun9i-a80-prcm.yaml

## Purpose
Device-tree schema for Allwinner A80 PRCM. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun9i-a80-prcm`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun9i-a80-prcm), `reg` (items ?..1). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/sunxi/allwinner,sun9i-a80-prcm.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun9i-a80-prcm`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sunxi/allwinner,sun9i-a80-prcm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra.yaml

## Purpose
Device-tree schema for NVIDIA Tegra. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Thierry Reding <thierry.reding@gmail.com>, Jonathan Hunter <jonathanh@nvidia.com> and gives dt-schema a canonical contract for nodes matching `compal,paz00`, `compulab,trimslice`, `nvidia,harmony`, `nvidia,seaboard`, `nvidia,ventana`, `nvidia,tegra20`, `ad,medcom-wide`, `ad,plutux`, `ad,tec`, `ad,tamonten`, plus 112 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/tegra.yaml`
- run `make dtbs_check` on DTS files using `compal,paz00`, `compulab,trimslice`, `nvidia,harmony`, `nvidia,seaboard`, `nvidia,ventana`, `nvidia,tegra20`, `ad,medcom-wide`, `ad,plutux`, `ad,tec`, `ad,tamonten`, plus 112 more
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra-ccplex-cluster.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra-ccplex-cluster.yaml

## Purpose
The Tegra CPU COMPLEX CLUSTER area contains memory-mapped registers that initiate CPU frequency/voltage transitions. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Sumit Gupta <sumitg@nvidia.com>, Mikko Perttunen <mperttunen@nvidia.com>, Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <thierry.reding@gmail.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra186-ccplex-cluster`, `nvidia,tegra234-ccplex-cluster`, `nvidia,tegra238-ccplex-cluster`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum nvidia,tegra186-ccplex-cluster, nvidia,tegra234-ccplex-cluster, nvidia,tegra238-ccplex-cluster), `reg` (items ?..1), `nvidia,bpmp` (ref phandle; Specifies the BPMP node that needs to be queried to get operating point data for all CPUs.). Required properties are `compatible`, `reg`, `nvidia,bpmp`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/tegra/nvidia,tegra-ccplex-cluster.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra186-ccplex-cluster`, `nvidia,tegra234-ccplex-cluster`, `nvidia,tegra238-ccplex-cluster`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra-ccplex-cluster.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra186-pmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra186-pmc.yaml

## Purpose
Device-tree schema for NVIDIA Tegra Power Management Controller (PMC). It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra186-pmc`, `nvidia,tegra194-pmc`, `nvidia,tegra234-pmc`, `nvidia,tegra264-pmc`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum nvidia,tegra186-pmc, nvidia,tegra194-pmc, nvidia,tegra234-pmc, nvidia,tegra264-pmc), `reg` (items 3..5), `reg-names` (items 3..?), `interrupt-controller`, `#interrupt-cells` (const 2; Specifies the number of cells needed to encode an interrupt source.), `nvidia,invert-interrupt` (ref flag; If present, inverts the PMU interrupt signal.). Required properties are `compatible`, `reg`, `reg-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 3 `allOf` composition block(s), 4 conditional `if` branch(es), child-node patterns `^[a-z0-9]+-[a-z0-9]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/flag, /schemas/types.yaml#/definitions/string, /schemas/types.yaml#/definitions/uint32, example includes dt-bindings/clock/tegra186-clock.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/memory/tegra186-mc.h, dt-bindings/pinctrl/pinctrl-tegra-io-pad.h, plus 1 more. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/tegra/nvidia,tegra186-pmc.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra186-pmc`, `nvidia,tegra194-pmc`, `nvidia,tegra234-pmc`, `nvidia,tegra264-pmc`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra186-pmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra194-axi2apb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra194-axi2apb.yaml

## Purpose
Device-tree schema for NVIDIA Tegra194 AXI2APB bridge. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Sumit Gupta <sumitg@nvidia.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra194-axi2apb`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum nvidia,tegra194-axi2apb), `reg` (items ?..6; Physical base address and length of registers for all bridges). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/tegra/nvidia,tegra194-axi2apb.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra194-axi2apb`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra194-axi2apb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra194-cbb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra194-cbb.yaml

## Purpose
The Control Backbone (CBB) is comprised of the physical path from an initiator to a target's register configuration space. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Sumit Gupta <sumitg@nvidia.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra194-cbb-noc`, `nvidia,tegra194-aon-noc`, `nvidia,tegra194-bpmp-noc`, `nvidia,tegra194-rce-noc`, `nvidia,tegra194-sce-noc`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum nvidia,tegra194-cbb-noc, nvidia,tegra194-aon-noc, nvidia,tegra194-bpmp-noc, nvidia,tegra194-rce-noc...), `reg` (items ?..1), `interrupts` (CCPLEX receives secure or nonsecure interrupt depending on error type.), `nvidia,apbmisc` (ref phandle; Specifies the apbmisc node which need to be used for reading the ERD register.), `nvidia,axi2apb` (ref phandle; Specifies the node having all axi2apb bridges which need to be checked for any error logged in their). Required properties are `compatible`, `reg`, `interrupts`, `nvidia,apbmisc`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle, example includes dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/tegra/nvidia,tegra194-cbb.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra194-cbb-noc`, `nvidia,tegra194-aon-noc`, `nvidia,tegra194-bpmp-noc`, `nvidia,tegra194-rce-noc`, `nvidia,tegra194-sce-noc`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra194-cbb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra234-cbb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra234-cbb.yaml

## Purpose
The Control Backbone (CBB) is comprised of the physical path from an initiator to a target's register configuration space. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Sumit Gupta <sumitg@nvidia.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra234-aon-fabric`, `nvidia,tegra234-bpmp-fabric`, `nvidia,tegra234-cbb-fabric`, `nvidia,tegra234-dce-fabric`, `nvidia,tegra234-rce-fabric`, `nvidia,tegra234-sce-fabric`, `nvidia,tegra238-ape-fabric`, `nvidia,tegra238-aon-fabric`, `nvidia,tegra238-bpmp-fabric`, `nvidia,tegra238-cbb-fabric`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum nvidia,tegra234-aon-fabric, nvidia,tegra234-bpmp-fabric, nvidia,tegra234-cbb-fabric, nvidia,tegra234-dce-fabric...), `reg` (items ?..1), `interrupts`. Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/tegra/nvidia,tegra234-cbb.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra234-aon-fabric`, `nvidia,tegra234-bpmp-fabric`, `nvidia,tegra234-cbb-fabric`, `nvidia,tegra234-dce-fabric`, `nvidia,tegra234-rce-fabric`, `nvidia,tegra234-sce-fabric`, `nvidia,tegra238-ape-fabric`, `nvidia,tegra238-aon-fabric`, `nvidia,tegra238-bpmp-fabric`, `nvidia,tegra238-cbb-fabric`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tegra/nvidia,tegra234-cbb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tesla.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tesla.yaml

## Purpose
Device-tree schema for Tesla Full Self Driving(FSD) platforms. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Alim Akhtar <alim.akhtar@samsung.com>, linux-fsd@tesla.com and gives dt-schema a canonical contract for nodes matching `tesla,fsd-evb`, `tesla,fsd`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/tesla.yaml`
- run `make dtbs_check` on DTS files using `tesla,fsd-evb`, `tesla,fsd`
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/tesla.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/k3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/k3.yaml

## Purpose
Platforms based on Texas Instruments K3 Multicore SoC architecture shall have the following properties. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Nishanth Menon <nm@ti.com> and gives dt-schema a canonical contract for nodes matching `ti,am62a7-sk`, `ti,am62a7`, `ti,am62d2-evm`, `ti,am62d2`, `phytec,am62a7-phyboard-lyra-rdk`, `phytec,am62a-phycore-som`, `ti,am62l3-evm`, `ti,am62l3`, `ti,am62p5-sk`, `ti,am62p5`, plus 80 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/ti/k3.yaml`
- run `make dtbs_check` on DTS files using `ti,am62a7-sk`, `ti,am62a7`, `ti,am62d2-evm`, `ti,am62d2`, `phytec,am62a7-phyboard-lyra-rdk`, `phytec,am62a-phycore-som`, `ti,am62l3-evm`, `ti,am62l3`, `ti,am62p5-sk`, `ti,am62p5`, plus 80 more
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/k3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/nspire.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/nspire.yaml

## Purpose
Device-tree schema for TI-NSPIRE calculators. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Daniel Tang <dt.tangr@gmail.com> and gives dt-schema a canonical contract for nodes matching `ti,nspire-cx`, `ti,nspire-tp`, `ti,nspire-clp`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/ti/nspire.yaml`
- run `make dtbs_check` on DTS files using `ti,nspire-cx`, `ti,nspire-tp`, `ti,nspire-clp`
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/nspire.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/omap.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/omap.yaml

## Purpose
Platforms based on Texas Instruments OMAP SoC architecture. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Tony Lindgren <tony@atomide.com> and gives dt-schema a canonical contract for nodes matching `nokia,n800`, `nokia,n810`, `nokia,n810-wimax`, `ti,omap2420-h4`, `ti,omap2420`, `ti,omap2`, `ti,omap2430-sdp`, `ti,omap2430`, `compulab,omap3-cm-t3530`, `logicpd,dm3730-som-lv-devkit`, plus 75 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/ti/omap.yaml`
- run `make dtbs_check` on DTS files using `nokia,n800`, `nokia,n810`, `nokia,n810-wimax`, `ti,omap2420-h4`, `ti,omap2420`, `ti,omap2`, `ti,omap2430-sdp`, `ti,omap2430`, `compulab,omap3-cm-t3530`, `logicpd,dm3730-som-lv-devkit`, plus 75 more
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/omap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/ti,davinci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/ti,davinci.yaml

## Purpose
DA850/OMAP-L138/AM18x based boards It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Sekhar Nori <nsekhar@ti.com> and gives dt-schema a canonical contract for nodes matching `ti,da850-evm`, `ti,da850-lcdk`, `enbw,cmc`, `lego,ev3`, `ti,da850`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/ti/ti,davinci.yaml`
- run `make dtbs_check` on DTS files using `ti,da850-evm`, `ti,da850-lcdk`, `enbw,cmc`, `lego,ev3`, `ti,da850`
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/ti,davinci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/ti,keystone.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/ti,keystone.yaml

## Purpose
Device-tree schema for TI Keystone Platforms. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Nishanth Menon <nm@ti.com>, Santosh Shilimkar <ssantosh@kernel.org> and gives dt-schema a canonical contract for nodes matching `ti,k2g-evm`, `ti,k2g-ice`, `ti,k2g`, `ti,keystone`, `ti,k2e-evm`, `ti,k2e`, `ti,k2l-evm`, `ti,k2l`, `ti,k2hk-evm`, `ti,k2hk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/ti/ti,keystone.yaml`
- run `make dtbs_check` on DTS files using `ti,k2g-evm`, `ti,k2g-ice`, `ti,k2g`, `ti,keystone`, `ti,k2e-evm`, `ti,k2e`, `ti,k2l-evm`, `ti,k2l`, `ti,k2hk-evm`, `ti,k2hk`
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/ti,keystone.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/ti,omap-prm-inst.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/ti,omap-prm-inst.yaml

## Purpose
Power and Reset Manager is an IP block on OMAP family of devices which handle the power domains and their current state, and provide reset handling for the domains and/or separate IP blocks under the power domain hierarchy. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Aaro Koskinen <aaro.koskinen@iki.fi>, Andreas Kemnade <andreas@kemnade.info>, Kevin Hilman <khilman@baylibre.com>, Roger Quadros <rogerq@kernel.org>, plus 1 more and gives dt-schema a canonical contract for nodes matching `ti,am3-prm-inst`, `ti,am4-prm-inst`, `ti,omap4-prm-inst`, `ti,omap5-prm-inst`, `ti,dra7-prm-inst`, `ti,omap-prm-inst`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `#reset-cells` (const 1), `#power-domain-cells` (const 0). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/ti/ti,omap-prm-inst.yaml`
- run `make dtbs_check` on DTS files using `ti,am3-prm-inst`, `ti,am4-prm-inst`, `ti,omap4-prm-inst`, `ti,omap5-prm-inst`, `ti,dra7-prm-inst`, `ti,omap-prm-inst`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ti/ti,omap-prm-inst.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/toshiba.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/toshiba.yaml

## Purpose
Device-tree schema for Toshiba Visconti Platform. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Nobuhiro Iwamatsu <nobuhiro1.iwamatsu@toshiba.co.jp> and gives dt-schema a canonical contract for nodes matching `toshiba,tmpv7708-rm-mbrc`, `toshiba,tmpv7708-visrobo-vrb`, `toshiba,tmpv7708`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/toshiba.yaml`
- run `make dtbs_check` on DTS files using `toshiba,tmpv7708-rm-mbrc`, `toshiba,tmpv7708-visrobo-vrb`, `toshiba,tmpv7708`
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/toshiba.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ux500.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ux500.yaml

## Purpose
Device-tree schema for Ux500 platforms. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Linus Walleij <linusw@kernel.org> and gives dt-schema a canonical contract for nodes matching `st-ericsson,mop500`, `st-ericsson,u8500`, `st-ericsson,href520`, `st-ericsson,hrefv60+`, `calaosystems,snowball-a9500`, `st-ericsson,u9500`, `samsung,codina`, `samsung,codina-tmo`, `samsung,gavini`, `samsung,golden`, plus 3 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/ux500.yaml`
- run `make dtbs_check` on DTS files using `st-ericsson,mop500`, `st-ericsson,u8500`, `st-ericsson,href520`, `st-ericsson,hrefv60+`, `calaosystems,snowball-a9500`, `st-ericsson,u9500`, `samsung,codina`, `samsung,codina-tmo`, `samsung,gavini`, `samsung,golden`, plus 3 more
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/ux500.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/vexpress-config.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/vexpress-config.yaml

## Purpose
This is a system control register block, acting as a bridge to the platform's configuration bus via "system control" interface, addressing devices with site number, position in the board stack, config controller, function and device numbers - see motherboard's It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Andre Przywara <andre.przywara@arm.com> and gives dt-schema a canonical contract for nodes matching `arm,vexpress,config-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const arm,vexpress,config-bus), `arm,vexpress,config-bridge` (ref phandle; Phandle to the sysreg node.), `muxfpga`, `shutdown`, `reboot`, `dvimode`. Required properties are `compatible`, `arm,vexpress,config-bridge`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^clock-controller.*$`, `^regulator-.+$`, `^amp-.+$`, `^temp-.+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/regulator/regulator.yaml#, /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32-array. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/vexpress-config.yaml`
- run `make dtbs_check` on DTS files using `arm,vexpress,config-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/vexpress-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/vexpress-sysreg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/vexpress-sysreg.yaml

## Purpose
This is a system control registers block, providing multiple low level platform functions like board detection and identification, software interrupt generation, MMC and NOR Flash control, etc. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Andre Przywara <andre.przywara@arm.com> and gives dt-schema a canonical contract for nodes matching `arm,vexpress-sysreg`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const arm,vexpress-sysreg), `reg` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 1), `ranges`, `gpio-controller`, `#gpio-cells` (const 2). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^gpio@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/vexpress-sysreg.yaml`
- run `make dtbs_check` on DTS files using `arm,vexpress-sysreg`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/vexpress-sysreg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/vt8500.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/vt8500.yaml

## Purpose
Device-tree schema for VIA/Wondermedia VT8500 Platforms. It is a ARM/platform binding used for board or SoC top-level platform matching and platform support bring-up. The binding is maintained by Alexey Charkov <alchark@gmail.com> and gives dt-schema a canonical contract for nodes matching `via,vt8500`, `wm,wm8505`, `wm,wm8650`, `wm,wm8750`, `wm,wm8850`, `via,apc-rock`, `wm,wm8950`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=arm/vt8500.yaml`
- run `make dtbs_check` on DTS files using `via,vt8500`, `wm,wm8505`, `wm,wm8650`, `wm,wm8750`, `wm,wm8850`, `via,apc-rock`, `wm,wm8950`
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/vt8500.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ahci-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ahci-common.yaml

## Purpose
This document defines device tree properties for a common AHCI SATA controller implementation. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Hans de Goede <hdegoede@redhat.com>, Damien Le Moal <dlemoal@kernel.org> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `reg` (Generic AHCI registers space conforming to the Serial ATA AHCI specification.), `reg-names` (CSR space IDs), `interrupts` (items 1..32; Generic AHCI state change interrupt.), `phys` (items ?..1; Reference to the SATA PHY node), `phy-names` (const sata-phy), `ports-implemented` (ref uint32; Mask that indicates which ports the HBA supports.), `hba-cap` (ref uint32; Bitfield of the HBA generic platform capabilities like Staggered Spin-up or Mechanical Presence Swit), `ahci-supply` (Power regulator for AHCI controller), `target-supply` (Power regulator for SATA target device), `phy-supply` (Power regulator for SATA PHY). Required properties are `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), child-node patterns `^sata-port@[0-9a-f]+$`, local `$defs` entries `ahci-port`. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs #/$defs/ahci-port, /schemas/ata/sata-common.yaml#/$defs/sata-port, /schemas/types.yaml#/definitions/uint32, sata-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/ahci-common.yaml`
- run `make dtbs_check` on DTS files using `ahci-common` nodes
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ahci-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ahci-platform.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ahci-platform.yaml

## Purpose
SATA nodes are defined to describe on-chip Serial ATA controllers. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Hans de Goede <hdegoede@redhat.com>, Jens Axboe <axboe@kernel.dk> and gives dt-schema a canonical contract for nodes matching `brcm,iproc-ahci`, `marvell,armada-8k-ahci`, `marvell,berlin2-ahci`, `marvell,berlin2q-ahci`, `qcom,apq8064-ahci`, `qcom,ipq806x-ahci`, `socionext,uniphier-pro4-ahci`, `socionext,uniphier-pxs2-ahci`, `socionext,uniphier-pxs3-ahci`, `cavium,octeon-7130-ahci`, plus 3 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items 1..2), `reg-names` (items ?..1), `interrupts` (items ?..1), `clocks` (items 1..5), `clock-names` (items 1..5), `resets` (items 1..3), `power-domains` (items ?..1), `iommus` (items ?..1). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 3 `allOf` composition block(s), 3 conditional `if` branch(es), child-node patterns `^sata-port@[0-9a-f]+$`. Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/ata/ahci-common.yaml#/$defs/ahci-port, ahci-common.yaml#, example includes dt-bindings/ata/ahci.h, dt-bindings/clock/berlin2q.h, dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/ahci-platform.yaml`
- run `make dtbs_check` on DTS files using `brcm,iproc-ahci`, `marvell,armada-8k-ahci`, `marvell,berlin2-ahci`, `marvell,berlin2q-ahci`, `qcom,apq8064-ahci`, `qcom,ipq806x-ahci`, `socionext,uniphier-pro4-ahci`, `socionext,uniphier-pxs2-ahci`, `socionext,uniphier-pxs3-ahci`, `cavium,octeon-7130-ahci`, plus 3 more
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ahci-platform.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/allwinner,sun4i-a10-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/allwinner,sun4i-a10-ahci.yaml

## Purpose
Device-tree schema for Allwinner A10 AHCI SATA Controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun4i-a10-ahci), `reg` (items ?..1), `interrupts` (items ?..1), `clocks`, `target-supply` (Regulator for SATA target power). Required properties are `compatible`, `reg`, `clocks`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/allwinner,sun4i-a10-ahci.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/allwinner,sun4i-a10-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/allwinner,sun8i-r40-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/allwinner,sun8i-r40-ahci.yaml

## Purpose
Device-tree schema for Allwinner R40 AHCI SATA Controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun8i-r40-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun8i-r40-ahci), `reg` (items ?..1), `interrupts` (items ?..1), `clocks`, `resets` (items ?..1), `reset-names` (const ahci), `ahci-supply` (Regulator for the AHCI controller), `phy-supply` (Regulator for the SATA PHY power). Required properties are `compatible`, `reg`, `clocks`, `interrupts`, `resets`, `reset-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/sun8i-r40-ccu.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/reset/sun8i-r40-ccu.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/allwinner,sun8i-r40-ahci.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun8i-r40-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/allwinner,sun8i-r40-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/apm,xgene-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/apm,xgene-ahci.yaml

## Purpose
Device-tree schema for APM X-Gene 6.0 Gb/s SATA host controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Rob Herring <robh@kernel.org> and gives dt-schema a canonical contract for nodes matching `apm,xgene-ahci`, `apm,xgene-ahci-v2`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum apm,xgene-ahci, apm,xgene-ahci-v2), `reg` (items 4..?), `interrupts` (items ?..1), `clocks` (items ?..1). Required properties are `compatible`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs ahci-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/apm,xgene-ahci.yaml`
- run `make dtbs_check` on DTS files using `apm,xgene-ahci`, `apm,xgene-ahci-v2`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/apm,xgene-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/arasan,cf-spear1340.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/arasan,cf-spear1340.yaml

## Purpose
Device-tree schema for Arasan PATA Compact Flash Controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Viresh Kumar <viresh.kumar@linaro.org> and gives dt-schema a canonical contract for nodes matching `arasan,cf-spear1340`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const arasan,cf-spear1340), `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items ?..1), `dmas` (items ?..1), `dma-names`, `arasan,broken-udma` (UDMA mode is unusable), `arasan,broken-mwdma` (MWDMA mode is unusable), `arasan,broken-pio` (PIO mode is unusable). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/arasan,cf-spear1340.yaml`
- run `make dtbs_check` on DTS files using `arasan,cf-spear1340`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/arasan,cf-spear1340.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ata-generic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ata-generic.yaml

## Purpose
Generic Parallel ATA controllers supporting PIO modes only. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Linus Walleij <linusw@kernel.org> and gives dt-schema a canonical contract for nodes matching `arm,vexpress-cf`, `fsl,mpc8349emitx-pata`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg`, `interrupts` (items ?..1), `reg-shift` (enum 1, 2), `ata-generic,use16bit` (Use 16-bit accesses instead of 32-bit for data transfers), `pio-mode` (ref uint32; Maximum ATA PIO transfer mode). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/ata-generic.yaml`
- run `make dtbs_check` on DTS files using `arm,vexpress-cf`, `fsl,mpc8349emitx-pata`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ata-generic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/brcm,sata-brcm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/brcm,sata-brcm.yaml

## Purpose
SATA nodes are defined to describe on-chip Serial ATA controllers. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Florian Fainelli <f.fainelli@gmail.com> and gives dt-schema a canonical contract for nodes matching `brcm,bcm7216-ahci`, `brcm,bcm7445-ahci`, `brcm,bcm7425-ahci`, `brcm,bcm63138-ahci`, `brcm,sata3-ahci`, `brcm,bcm-nsp-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..2), `reg-names`, `interrupts` (items ?..1). Required properties are `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs ahci-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/brcm,sata-brcm.yaml`
- run `make dtbs_check` on DTS files using `brcm,bcm7216-ahci`, `brcm,bcm7445-ahci`, `brcm,bcm7425-ahci`, `brcm,bcm63138-ahci`, `brcm,sata3-ahci`, `brcm,bcm-nsp-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/brcm,sata-brcm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cavium,ebt3000-compact-flash.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cavium,ebt3000-compact-flash.yaml

## Purpose
The Cavium Compact Flash device is connected to the Octeon Boot Bus, and is thus a child of the Boot Bus device. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Rob Herring <robh@kernel.org> and gives dt-schema a canonical contract for nodes matching `cavium,ebt3000-compact-flash`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const cavium,ebt3000-compact-flash), `reg` (The base address of the CF chip select banks.), `cavium,bus-width` (ref uint32; enum 8, 16), `cavium,true-ide` (True IDE mode when present.), `cavium,dma-engine-handle` (ref phandle; A phandle for the DMA Engine connected to this device.). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/cavium,ebt3000-compact-flash.yaml`
- run `make dtbs_check` on DTS files using `cavium,ebt3000-compact-flash`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cavium,ebt3000-compact-flash.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ceva,ahci-1v84.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ceva,ahci-1v84.yaml

## Purpose
The Ceva SATA controller mostly conforms to the AHCI interface with some special extensions to add functionality, is a high-performance dual-port SATA host controller with an AHCI compliant command layer which supports advanced features such as native command  It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Radhey Shyam Pandey <radhey.shyam.pandey@amd.com> and gives dt-schema a canonical contract for nodes matching `ceva,ahci-1v84`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const ceva,ahci-1v84), `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items ?..1), `resets` (items ?..1), `phys` (items ?..1), `phy-names`, `dma-coherent`, `iommus` (items ?..4), `power-domains` (items ?..1), plus 2 more. Required properties are `compatible`, `reg`, `clocks`, `interrupts`, `ceva,p0-cominit-params`, `ceva,p0-comwake-params`, `ceva,p0-burst-params`, `ceva,p0-retry-params`, `ceva,p1-cominit-params`, `ceva,p1-comwake-params`, `ceva,p1-burst-params`, `ceva,p1-retry-params`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/flag, /schemas/types.yaml#/definitions/uint16-array, /schemas/types.yaml#/definitions/uint8-array, example includes dt-bindings/interrupt-controller/irq.h, dt-bindings/phy/phy.h, dt-bindings/power/xlnx-zynqmp-power.h, dt-bindings/reset/xlnx-zynqmp-resets.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/ceva,ahci-1v84.yaml`
- run `make dtbs_check` on DTS files using `ceva,ahci-1v84`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ceva,ahci-1v84.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cirrus,ep9312-pata.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cirrus,ep9312-pata.yaml

## Purpose
Device-tree schema for Cirrus Logic EP9312 PATA controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Damien Le Moal <dlemoal@kernel.org> and gives dt-schema a canonical contract for nodes matching `cirrus,ep9312-pata`, `cirrus,ep9315-pata`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/cirrus,ep9312-pata.yaml`
- run `make dtbs_check` on DTS files using `cirrus,ep9312-pata`, `cirrus,ep9315-pata`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cirrus,ep9312-pata.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cortina,gemini-sata-bridge.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cortina,gemini-sata-bridge.yaml

## Purpose
The Gemini SATA bridge in a SoC-internal PATA to SATA bridge that takes two Faraday Technology FTIDE010 PATA controllers and bridges them in different configurations to two SATA ports. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Linus Walleij <linusw@kernel.org> and gives dt-schema a canonical contract for nodes matching `cortina,gemini-sata-bridge`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const cortina,gemini-sata-bridge), `reg` (items ?..1), `clocks` (items ?..2; phandles to the compulsory peripheral clocks), `clock-names`, `resets` (items ?..2; phandles to the reset lines for both SATA bridges), `reset-names`, `syscon` (ref phandle; a phandle to the global Gemini system controller), `cortina,gemini-ata-muxmode` (ref uint32; enum 0, 1, 2, 3), `cortina,gemini-enable-ide-pins` (Enables the PATA to IDE connection.), `cortina,gemini-enable-sata-bridge` (Enables the PATA to SATA bridge inside the Gemnini SoC.). Required properties are `clocks`, `clock-names`, `cortina,gemini-ata-muxmode`, `resets`, `reset-names`, `compatible`, `reg`, `syscon`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32, example includes dt-bindings/clock/cortina,gemini-clock.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/cortina,gemini-sata-bridge.yaml`
- run `make dtbs_check` on DTS files using `cortina,gemini-sata-bridge`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/cortina,gemini-sata-bridge.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/eswin,eic7700-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/eswin,eic7700-ahci.yaml

## Purpose
AHCI SATA controller embedded into the EIC7700 SoC is based on the DWC AHCI SATA v5.00a IP core. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Yulin Lu <luyulin@eswincomputing.com>, Huan He <hehuan1@eswincomputing.com> and gives dt-schema a canonical contract for nodes matching `eswin,eic7700-ahci`, `snps,dwc-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `clocks` (items 2..2), `clock-names`, `resets` (items ?..1), `reset-names` (const arst), `ports-implemented` (const 1). Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `phys`, `phy-names`, `ports-implemented`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs snps,dwc-ahci-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/eswin,eic7700-ahci.yaml`
- run `make dtbs_check` on DTS files using `eswin,eic7700-ahci`, `snps,dwc-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/eswin,eic7700-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/faraday,ftide010.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/faraday,ftide010.yaml

## Purpose
This controller is the first Faraday IDE interface block, used in the StorLink SL3512 and SL3516, later known as the Cortina Systems Gemini platform. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Linus Walleij <linusw@kernel.org> and gives dt-schema a canonical contract for nodes matching `faraday,ftide010`, `cortina,gemini-pata`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items 1..?), `clock-names` (const PCLK), `sata` (ref phandle; phandle to the Gemini PATA to SATA bridge, if available). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle, pata-common.yaml#, example includes dt-bindings/clock/cortina,gemini-clock.h, dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/faraday,ftide010.yaml`
- run `make dtbs_check` on DTS files using `faraday,ftide010`, `cortina,gemini-pata`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/faraday,ftide010.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,ahci.yaml

## Purpose
Device-tree schema for Freescale QorIQ AHCI SATA Controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Frank Li <Frank.Li@nxp.com> and gives dt-schema a canonical contract for nodes matching `fsl,ls1012a-ahci`, `fsl,ls1043a-ahci`, `fsl,ls1021a-ahci`, `fsl,ls1028a-ahci`, `fsl,ls1046a-ahci`, `fsl,ls1088a-ahci`, `fsl,ls2080a-ahci`, `fsl,lx2160a-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items 1..2), `reg-names` (items 1..?), `interrupts` (items ?..1), `clocks` (items ?..1), `dma-coherent`. Required properties are `compatible`, `reg`, `clocks`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/fsl,ahci.yaml`
- run `make dtbs_check` on DTS files using `fsl,ls1012a-ahci`, `fsl,ls1043a-ahci`, `fsl,ls1021a-ahci`, `fsl,ls1028a-ahci`, `fsl,ls1046a-ahci`, `fsl,ls1088a-ahci`, `fsl,ls2080a-ahci`, `fsl,lx2160a-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,imx-pata.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,imx-pata.yaml

## Purpose
Device-tree schema for Freescale i.MX PATA Controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Animesh Agarwal <animeshagarwal28@gmail.com> and gives dt-schema a canonical contract for nodes matching `fsl,imx31-pata`, `fsl,imx51-pata`, `fsl,imx27-pata`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts`, `clocks`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/fsl,imx-pata.yaml`
- run `make dtbs_check` on DTS files using `fsl,imx31-pata`, `fsl,imx51-pata`, `fsl,imx27-pata`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,imx-pata.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,pq-sata.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,pq-sata.yaml

## Purpose
SATA nodes are defined to describe on-chip Serial ATA controllers. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by J. Neuschfer <j.ne@posteo.net> and gives dt-schema a canonical contract for nodes matching `fsl,mpc8377-sata`, `fsl,mpc8536-sata`, `fsl,mpc8315-sata`, `fsl,mpc8379-sata`, `fsl,pq-sata`, `fsl,pq-sata-v2`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `cell-index` (ref uint32; enum 1, 2, 3, 4). Required properties are `compatible`, `interrupts`, `cell-index`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32, example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/fsl,pq-sata.yaml`
- run `make dtbs_check` on DTS files using `fsl,mpc8377-sata`, `fsl,mpc8536-sata`, `fsl,mpc8315-sata`, `fsl,mpc8379-sata`, `fsl,pq-sata`, `fsl,pq-sata-v2`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/fsl,pq-sata.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/imx-sata.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/imx-sata.yaml

## Purpose
The Freescale i.MX SATA controller mostly conforms to the AHCI interface with some special extensions at integration level. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Shawn Guo <shawn.guo@linaro.org> and gives dt-schema a canonical contract for nodes matching `fsl,imx53-ahci`, `fsl,imx6q-ahci`, `fsl,imx6qp-ahci`, `fsl,imx8qm-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum fsl,imx53-ahci, fsl,imx6q-ahci, fsl,imx6qp-ahci, fsl,imx8qm-ahci), `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items 2..?), `clock-names` (items 2..?), `phys`, `phy-names`, `fsl,transmit-level-mV` (ref uint32; transmit voltage level, in millivolts.), `fsl,transmit-boost-mdB` (ref uint32; transmit boost level, in milli-decibels.), `fsl,transmit-atten-16ths` (ref uint32; transmit attenuation, in 16ths.), plus 2 more. Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 `allOf` composition block(s), 2 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/flag, /schemas/types.yaml#/definitions/uint32, example includes dt-bindings/clock/imx6qdl-clock.h, dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/imx-sata.yaml`
- run `make dtbs_check` on DTS files using `fsl,imx53-ahci`, `fsl,imx6q-ahci`, `fsl,imx6qp-ahci`, `fsl,imx8qm-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/imx-sata.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/intel,ixp4xx-compact-flash.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/intel,ixp4xx-compact-flash.yaml

## Purpose
The IXP4xx network processors have a CompactFlash interface that presents a CompactFlash card to the system as a true IDE (parallel ATA) device. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Linus Walleij <linusw@kernel.org> and gives dt-schema a canonical contract for nodes matching `intel,ixp4xx-compact-flash`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const intel,ixp4xx-compact-flash), `reg`, `interrupts` (items ?..1). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml#, pata-common.yaml#, example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/intel,ixp4xx-compact-flash.yaml`
- run `make dtbs_check` on DTS files using `intel,ixp4xx-compact-flash`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/intel,ixp4xx-compact-flash.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/marvell,orion-sata.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/marvell,orion-sata.yaml

## Purpose
Device-tree schema for Marvell Orion SATA. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Andrew Lunn <andrew@lunn.ch>, Gregory Clement <gregory.clement@bootlin.com> and gives dt-schema a canonical contract for nodes matching `marvell,orion-sata`, `marvell,armada-370-sata`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum marvell,orion-sata, marvell,armada-370-sata), `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items 1..8), `clock-names` (items 1..?), `phys` (items 1..8), `phy-names` (items 1..?), `nr-ports` (ref uint32; Number of SATA ports in use.). Required properties are `compatible`, `reg`, `interrupts`, `nr-ports`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32, sata-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/marvell,orion-sata.yaml`
- run `make dtbs_check` on DTS files using `marvell,orion-sata`, `marvell,armada-370-sata`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/marvell,orion-sata.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/mediatek,mtk-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/mediatek,mtk-ahci.yaml

## Purpose
Device-tree schema for MediaTek Serial ATA controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Ryder Lee <ryder.lee@mediatek.com> and gives dt-schema a canonical contract for nodes matching `mediatek,mt7622-ahci`, `mediatek,mtk-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items ?..5), `clock-names`, `resets` (items ?..3), `reset-names`, `interrupt-names` (const hostc), `power-domains` (items ?..1), `mediatek,phy-mode` (ref phandle; System controller phandle, used to enable SATA function). Required properties are `reg`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `phys`, `phy-names`, `ports-implemented`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle, ahci-common.yaml#, example includes dt-bindings/clock/mt7622-clk.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/phy/phy.h, dt-bindings/power/mt7622-power.h, plus 1 more. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/mediatek,mtk-ahci.yaml`
- run `make dtbs_check` on DTS files using `mediatek,mt7622-ahci`, `mediatek,mtk-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/mediatek,mtk-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/nvidia,tegra-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/nvidia,tegra-ahci.yaml

## Purpose
Device-tree schema for Tegra AHCI SATA Controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Thierry Reding <thierry.reding@gmail.com>, Jonathan Hunter <jonathanh@nvidia.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra124-ahci`, `nvidia,tegra132-ahci`, `nvidia,tegra210-ahci`, `nvidia,tegra186-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum nvidia,tegra124-ahci, nvidia,tegra132-ahci, nvidia,tegra210-ahci, nvidia,tegra186-ahci), `reg` (items 2..?), `interrupts` (items ?..1), `clocks` (items ?..2), `clock-names`, `resets` (items 2..3), `reset-names` (items 2..?), `phys` (items ?..1), `phy-names`, `iommus` (items ?..1), plus 2 more. Required properties are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `reset-names`, `resets`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 3 `allOf` composition block(s), 3 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/tegra210-car.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/reset/tegra210-car.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/nvidia,tegra-ahci.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra124-ahci`, `nvidia,tegra132-ahci`, `nvidia,tegra210-ahci`, `nvidia,tegra186-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/nvidia,tegra-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/pata-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/pata-common.yaml

## Purpose
This document defines device tree properties common to most Parallel ATA (PATA, also known as IDE) AT attachment storage devices. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Linus Walleij <linusw@kernel.org> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `#address-cells` (const 1), `#size-cells` (const 0). Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^ide-port@[0-1]$`. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/pata-common.yaml`
- run `make dtbs_check` on DTS files using `pata-common` nodes
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/pata-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/renesas,rcar-sata.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/renesas,rcar-sata.yaml

## Purpose
Device-tree schema for Renesas R-Car Serial-ATA Interface. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Geert Uytterhoeven <geert+renesas@glider.be> and gives dt-schema a canonical contract for nodes matching `renesas,sata-r8a7779`, `renesas,sata-r8a7742`, `renesas,sata-r8a7790-es1`, `renesas,sata-r8a7790`, `renesas,sata-r8a7791`, `renesas,sata-r8a7793`, `renesas,rcar-gen2-sata`, `renesas,sata-r8a774b1`, `renesas,sata-r8a774e1`, `renesas,sata-r8a7795`, plus 2 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items ?..1), `resets` (items ?..1), `iommus` (items ?..1), `power-domains` (items ?..1). Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `power-domains`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/r8a7791-cpg-mssr.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/power/r8a7791-sysc.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/renesas,rcar-sata.yaml`
- run `make dtbs_check` on DTS files using `renesas,sata-r8a7779`, `renesas,sata-r8a7742`, `renesas,sata-r8a7790-es1`, `renesas,sata-r8a7790`, `renesas,sata-r8a7791`, `renesas,sata-r8a7793`, `renesas,rcar-gen2-sata`, `renesas,sata-r8a774b1`, `renesas,sata-r8a774e1`, `renesas,sata-r8a7795`, plus 2 more
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/renesas,rcar-sata.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/rockchip,dwc-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/rockchip,dwc-ahci.yaml

## Purpose
This document defines device tree bindings for the Synopsys DWC implementation of the AHCI SATA controller found in Rockchip devices. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Serge Semin <fancer.lancer@gmail.com> and gives dt-schema a canonical contract for nodes matching `rockchip,rk3568-dwc-ahci`, `rockchip,rk3576-dwc-ahci`, `rockchip,rk3588-dwc-ahci`, `snps,dwc-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `ports-implemented` (const 1), `power-domains` (items ?..1), `sata-port@0` (ref dwc-ahci-port). Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `ports-implemented`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 3 `allOf` composition block(s), 2 conditional `if` branch(es), child-node patterns `^sata-port@[1-9a-e]$`. Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/ata/snps,dwc-ahci-common.yaml#/$defs/dwc-ahci-port, snps,dwc-ahci-common.yaml#, example includes dt-bindings/ata/ahci.h, dt-bindings/clock/rockchip,rk3588-cru.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/phy/phy.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/rockchip,dwc-ahci.yaml`
- run `make dtbs_check` on DTS files using `rockchip,rk3568-dwc-ahci`, `rockchip,rk3576-dwc-ahci`, `rockchip,rk3588-dwc-ahci`, `snps,dwc-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/rockchip,dwc-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/sata-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/sata-common.yaml

## Purpose
This document defines device tree properties common to most Serial AT attachment (SATA) storage devices. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Linus Walleij <linusw@kernel.org> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `#address-cells` (const 1), `#size-cells` (const 0), `dma-coherent`. Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^sata-port@[0-9a-e]$`, local `$defs` entries `sata-port`. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs #/$defs/sata-port, /schemas/graph.yaml#/properties/port. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/sata-common.yaml`
- run `make dtbs_check` on DTS files using `sata-common` nodes
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/sata-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/sata_highbank.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/sata_highbank.yaml

## Purpose
The Calxeda SATA controller mostly conforms to the AHCI interface with some special extensions to add functionality, to map GPIOs for activity LEDs and for mapping the ComboPHYs. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Andre Przywara <andre.przywara@arm.com> and gives dt-schema a canonical contract for nodes matching `calxeda,hb-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const calxeda,hb-ahci), `reg` (items ?..1), `interrupts` (items ?..1), `dma-coherent`, `calxeda,pre-clocks` (ref uint32; Indicates the number of additional clock cycles to transmit before sending an SGPIO pattern.), `calxeda,post-clocks` (ref uint32; Indicates the number of additional clock cycles to transmit after sending an SGPIO pattern.), `calxeda,led-order` (ref uint32-array; items 1..8), `calxeda,port-phys` (ref phandle-array; items 1..8), `calxeda,tx-atten` (ref uint32-array; items 1..8), `calxeda,sgpio-gpio` (items ?..3; phandle-gpio bank, bit offset, and default on or off, which indicates that the driver supports SGPIO). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle-array, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/sata_highbank.yaml`
- run `make dtbs_check` on DTS files using `calxeda,hb-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/sata_highbank.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/snps,dwc-ahci-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/snps,dwc-ahci-common.yaml

## Purpose
This document defines device tree schema for the generic Synopsys DWC AHCI controller properties. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Serge Semin <fancer.lancer@gmail.com> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items 1..6; Basic DWC AHCI SATA clock sources like application AXI/AHB BIU clock, PM-alive clock, RxOOB detectio), `clock-names` (items 1..6), `resets` (items 1..4; At least basic application and reference clock domains resets are normally supported by the DWC AHCI), `reset-names` (items 1..4). Required properties are none declared.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), child-node patterns `^sata-port@[0-9a-e]$`, local `$defs` entries `dwc-ahci-port`. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs #/$defs/dwc-ahci-port, /schemas/ata/ahci-common.yaml#/$defs/ahci-port, /schemas/types.yaml#/definitions/uint32, ahci-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/snps,dwc-ahci-common.yaml`
- run `make dtbs_check` on DTS files using `snps,dwc-ahci-common` nodes
- coverage depends on in-tree DTS users because this binding has no embedded example block
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/snps,dwc-ahci-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/snps,dwc-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/snps,dwc-ahci.yaml

## Purpose
This document defines device tree bindings for the generic Synopsys DWC implementation of the AHCI SATA controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Serge Semin <fancer.lancer@gmail.com> and gives dt-schema a canonical contract for nodes matching `snps,dwc-ahci`, `snps,spear-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `iommus` (items 1..3). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), child-node patterns `^sata-port@[0-9a-e]$`. Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/ata/snps,dwc-ahci-common.yaml#/$defs/dwc-ahci-port, snps,dwc-ahci-common.yaml#, example includes dt-bindings/ata/ahci.h, dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/snps,dwc-ahci.yaml`
- run `make dtbs_check` on DTS files using `snps,dwc-ahci`, `snps,spear-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/snps,dwc-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/st,ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/st,ahci.yaml

## Purpose
Device-tree schema for STMicroelectronics STi SATA controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Patrice Chotard <patrice.chotard@foss.st.com> and gives dt-schema a canonical contract for nodes matching `st,ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const st,ahci), `clocks` (items ?..1), `clock-names`, `resets`, `reset-names`, `interrupt-names`. Required properties are `compatible`, `interrupt-names`, `phys`, `phy-names`, `clocks`, `clock-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs ahci-common.yaml#, example includes dt-bindings/clock/stih407-clks.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/phy/phy.h, dt-bindings/reset/stih407-resets.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/st,ahci.yaml`
- run `make dtbs_check` on DTS files using `st,ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/st,ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ti,da850-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ti,da850-ahci.yaml

## Purpose
Device-tree schema for TI DA850 AHCI SATA Controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Animesh Agarwal <animeshagarwal28@gmail.com> and gives dt-schema a canonical contract for nodes matching `ti,da850-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const ti,da850-ahci), `reg`, `interrupts` (items ?..1). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/ti,da850-ahci.yaml`
- run `make dtbs_check` on DTS files using `ti,da850-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ti,da850-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ti,dm816-ahci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ti,dm816-ahci.yaml

## Purpose
Device-tree schema for TI DM816 AHCI SATA Controller. It is a ATA/AHCI storage binding used for SATA/PATA/CompactFlash controller discovery, register mapping, interrupts, clocks, PHYs, and per-port wiring. The binding is maintained by Bartosz Golaszewski <brgl@bgdev.pl> and gives dt-schema a canonical contract for nodes matching `ti,dm816-ahci`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const ti,dm816-ahci), `reg` (items ?..1), `clocks`, `ti,hwmods` (const sata). Required properties are `compatible`, `clocks`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs ahci-common.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=ata/ti,dm816-ahci.yaml`
- run `make dtbs_check` on DTS files using `ti,dm816-ahci`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/ata/ti,dm816-ahci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/arm,versatile-lcd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/arm,versatile-lcd.yaml

## Purpose
This binding defines the character LCD interface found on ARM Versatile AB and PB reference platforms. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Linus Walleij <linusw@kernel.org>, Rob Herring <robh@kernel.org> and gives dt-schema a canonical contract for nodes matching `arm,versatile-lcd`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const arm,versatile-lcd), `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items ?..1), `clock-names` (items ?..1). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/arm,versatile-lcd.yaml`
- run `make dtbs_check` on DTS files using `arm,versatile-lcd`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/arm,versatile-lcd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/gpio-7-segment.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/gpio-7-segment.yaml

## Purpose
Device-tree schema for GPIO based LED segment display. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Chris Packham <chris.packham@alliedtelesis.co.nz> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const gpio-7-segment), `segment-gpios` (items 7..8; An array of GPIOs one per segment.). Required properties are `segment-gpios`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/gpio/gpio.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/gpio-7-segment.yaml`
- run `make dtbs_check` on DTS files using `gpio-7-segment` nodes
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/gpio-7-segment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/hit,hd44780.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/hit,hd44780.yaml

## Purpose
The Hitachi HD44780 Character LCD Controller is commonly used on character LCDs that can display one or more lines of text. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Geert Uytterhoeven <geert@linux-m68k.org> and gives dt-schema a canonical contract for nodes matching `hit,hd44780`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const hit,hd44780), `data-gpios` (GPIO pins connected to the data signal lines DB0-DB7 (8-bit mode) or DB4-DB7 (4-bit mode) of the LCD), `enable-gpios` (items ?..1; GPIO pin connected to the "E" (Enable) signal line of the LCD Controller's bus interface.), `rs-gpios` (items ?..1; GPIO pin connected to the "RS" (Register Select) signal line of the LCD Controller's bus interface.), `display-height-chars` (ref uint32; Height of the display, in character cells,), `display-width-chars` (ref uint32; Width of the display, in character cells.), `rw-gpios` (items ?..1; GPIO pin connected to the "RW" (Read/Write) signal line of the LCD Controller's bus interface.), `backlight-gpios` (items ?..1; GPIO pin used for enabling the LCD's backlight.), `internal-buffer-width` (ref uint32; Internal buffer width (default is 40 for displays with 1 or 2 lines, and display-width-chars for dis). Required properties are `compatible`, `data-gpios`, `enable-gpios`, `rs-gpios`, `display-height-chars`, `display-width-chars`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32, example includes dt-bindings/gpio/gpio.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/hit,hd44780.yaml`
- run `make dtbs_check` on DTS files using `hit,hd44780`
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/hit,hd44780.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/holtek,ht16k33.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/holtek,ht16k33.yaml

## Purpose
Device-tree schema for Holtek HT16K33 RAM mapping 16*8 LED controller with keyscan. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Robin van der Gracht <robin@protonic.nl> and gives dt-schema a canonical contract for nodes matching `adafruit,3108`, `adafruit,3130`, `holtek,ht16k33`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `refresh-rate-hz` (items ?..1; Display update interval in Hertz for dot-matrix displays), `debounce-delay-ms`, `linux,keymap`, `linux,no-autorepeat` (Disable keyrepeat), `default-brightness-level` (Initial brightness level), `led` (ref common.yaml#). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/input/input.yaml#, /schemas/input/matrix-keymap.yaml#, /schemas/leds/common.yaml#, example includes dt-bindings/input/input.h, dt-bindings/interrupt-controller/irq.h, dt-bindings/leds/common.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/holtek,ht16k33.yaml`
- run `make dtbs_check` on DTS files using `adafruit,3108`, `adafruit,3130`, `holtek,ht16k33`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/holtek,ht16k33.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/img,ascii-lcd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/img,ascii-lcd.yaml

## Purpose
Device-tree schema for ASCII LCD displays on Imagination Technologies boards. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Paul Burton <paulburton@kernel.org> and gives dt-schema a canonical contract for nodes matching `img,boston-lcd`, `mti,malta-lcd`, `mti,sead3-lcd`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum img,boston-lcd, mti,malta-lcd, mti,sead3-lcd), `reg` (items ?..1), `offset` (ref uint32; Offset in bytes to the LCD registers within the system controller). Required properties are `compatible`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/img,ascii-lcd.yaml`
- run `make dtbs_check` on DTS files using `img,boston-lcd`, `mti,malta-lcd`, `mti,sead3-lcd`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/img,ascii-lcd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/maxim,max6959.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/maxim,max6959.yaml

## Purpose
The Maxim MAX6958/6959 7-segment LED display controller provides an I2C interface to up to four 7-segment LED digits. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Andy Shevchenko <andriy.shevchenko@linux.intel.com> and gives dt-schema a canonical contract for nodes matching `maxim,max6959`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const maxim,max6959), `reg` (items ?..1). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/maxim,max6959.yaml`
- run `make dtbs_check` on DTS files using `maxim,max6959`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/maxim,max6959.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/modtronix,lcd2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/modtronix,lcd2s.yaml

## Purpose
The LCD2S is a Character LCD Display manufactured by Modtronix Engineering. It is a auxiliary display binding used for character, segment, or board display device probing and GPIO/I2C/backlight wiring. The binding is maintained by Lars Poeschel <poeschel@lemonage.de> and gives dt-schema a canonical contract for nodes matching `modtronix,lcd2s`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const modtronix,lcd2s), `reg` (items ?..1; I2C bus address of the display.), `display-height-chars` (ref uint32; Height of the display, in character cells.), `display-width-chars` (ref uint32; Width of the display, in character cells.). Required properties are `compatible`, `reg`, `display-height-chars`, `display-width-chars`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=auxdisplay/modtronix,lcd2s.yaml`
- run `make dtbs_check` on DTS files using `modtronix,lcd2s`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/auxdisplay/modtronix,lcd2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,bcsr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,bcsr.yaml

## Purpose
Device-tree schema for Board Control and Status. It is a board-management binding used for board FPGA/CPLD or control-block discovery and child bus exposure. The binding is maintained by Frank Li <Frank.Li@nxp.com> and gives dt-schema a canonical contract for nodes matching `fsl,mpc8360mds-bcsr`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum fsl,mpc8360mds-bcsr), `reg` (items ?..1). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=board/fsl,bcsr.yaml`
- run `make dtbs_check` on DTS files using `fsl,mpc8360mds-bcsr`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,bcsr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,fpga-qixis-i2c.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,fpga-qixis-i2c.yaml

## Purpose
Device-tree schema for Freescale on-board FPGA connected on I2C bus. It is a board-management binding used for board FPGA/CPLD or control-block discovery and child bus exposure. The binding is maintained by Frank Li <Frank.Li@nxp.com> and gives dt-schema a canonical contract for nodes matching `fsl,bsc9132qds-fpga`, `fsl,fpga-qixis-i2c`, `fsl,ls1028aqds-fpga`, `fsl,lx2160aqds-fpga`, `simple-mfd`, `fsl,lx2160ardb-fpga`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 0), `mux-controller` (ref reg-mux.yaml). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), 1 conditional `if` branch(es), child-node patterns `^gpio@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/mux/reg-mux.yaml. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=board/fsl,fpga-qixis-i2c.yaml`
- run `make dtbs_check` on DTS files using `fsl,bsc9132qds-fpga`, `fsl,fpga-qixis-i2c`, `fsl,ls1028aqds-fpga`, `fsl,lx2160aqds-fpga`, `simple-mfd`, `fsl,lx2160ardb-fpga`
- the 3 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,fpga-qixis-i2c.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,fpga-qixis.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,fpga-qixis.yaml

## Purpose
Device-tree schema for Freescale on-board FPGA/CPLD. It is a board-management binding used for board FPGA/CPLD or control-block discovery and child bus exposure. The binding is maintained by Frank Li <Frank.Li@nxp.com> and gives dt-schema a canonical contract for nodes matching `fsl,p1022ds-fpga`, `fsl,fpga-ngpixis`, `fsl,ls1088aqds-fpga`, `fsl,ls1088ardb-fpga`, `fsl,ls2080aqds-fpga`, `fsl,ls2080ardb-fpga`, `fsl,fpga-qixis`, `fsl,ls1043aqds-fpga`, `fsl,ls1043ardb-fpga`, `fsl,ls1046aqds-fpga`, plus 8 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 1), `ranges` (items ?..1). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^mdio-mux@[a-f0-9,]+$`, `^gpio@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/net/mdio-mux-mmioreg.yaml, example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=board/fsl,fpga-qixis.yaml`
- run `make dtbs_check` on DTS files using `fsl,p1022ds-fpga`, `fsl,fpga-ngpixis`, `fsl,ls1088aqds-fpga`, `fsl,ls1088ardb-fpga`, `fsl,ls2080aqds-fpga`, `fsl,ls2080ardb-fpga`, `fsl,fpga-qixis`, `fsl,ls1043aqds-fpga`, `fsl,ls1043ardb-fpga`, `fsl,ls1046aqds-fpga`, plus 8 more
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/board/fsl,fpga-qixis.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/allwinner,sun50i-a64-de2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/allwinner,sun50i-a64-de2.yaml

## Purpose
Device-tree schema for Allwinner A64 Display Engine Bus. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun50i-a64-de2`, `allwinner,sun50i-h6-de3`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 1), `ranges`, `allwinner,sram` (ref phandle-array; The SRAM that needs to be claimed to access the display engine bus.). Required properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`, `allwinner,sram`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle-array. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/allwinner,sun50i-a64-de2.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun50i-a64-de2`, `allwinner,sun50i-h6-de3`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/allwinner,sun50i-a64-de2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/allwinner,sun8i-a23-rsb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/allwinner,sun8i-a23-rsb.yaml

## Purpose
Device-tree schema for Allwinner A23 RSB. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun8i-a23-rsb`, `allwinner,sun8i-a83t-rsb`, `allwinner,sun50i-h616-rsb`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `clocks` (items ?..1), `resets` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 0), `clock-frequency`. Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `resets`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/allwinner,sun8i-a23-rsb.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun8i-a23-rsb`, `allwinner,sun8i-a83t-rsb`, `allwinner,sun50i-h616-rsb`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/allwinner,sun8i-a23-rsb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/arm,integrator-ap-lm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/arm,integrator-ap-lm.yaml

## Purpose
The Integrator/AP is a prototyping platform and as such has a site for stacking up to four logic modules (LM) designed specifically for use with this platform. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Linus Walleij <linusw@kernel.org> and gives dt-schema a canonical contract for nodes matching `arm,integrator-ap-lm`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `#address-cells` (const 1), `#size-cells` (const 1), `ranges`, `dma-ranges`. Required properties are `compatible`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^bus(@[0-9a-f]*)?$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/arm,integrator-ap-lm.yaml`
- run `make dtbs_check` on DTS files using `arm,integrator-ap-lm`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/arm,integrator-ap-lm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/aspeed,ast2600-ahbc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/aspeed,ast2600-ahbc.yaml

## Purpose
Advanced High-performance Bus Controller (AHBC) supports plenty of mechanisms including a priority arbiter, an address decoder and a data multiplexer to control the overall operations of Advanced High-performance Bus (AHB). It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Neal Liu <neal_liu@aspeedtech.com>, Chia-Wei Wang <chiawei_wang@aspeedtech.com> and gives dt-schema a canonical contract for nodes matching `aspeed,ast2600-ahbc`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/aspeed,ast2600-ahbc.yaml`
- run `make dtbs_check` on DTS files using `aspeed,ast2600-ahbc`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/aspeed,ast2600-ahbc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/brcm,gisb-arb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/brcm,gisb-arb.yaml

## Purpose
Device-tree schema for Broadcom GISB bus Arbiter controller. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Florian Fainelli <f.fainelli@gmail.com> and gives dt-schema a canonical contract for nodes matching `brcm,bcm7445-gisb-arb`, `brcm,gisb-arb`, `brcm,bcm74165-gisb-arb`, `brcm,bcm7278-gisb-arb`, `brcm,bcm7435-gisb-arb`, `brcm,bcm7400-gisb-arb`, `brcm,bcm7038-gisb-arb`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items 2..?), `brcm,gisb-arb-master-mask` (ref uint32; 32-bits wide bitmask used to specify which GISB masters are valid at the system level), `brcm,gisb-arb-master-names` (ref string-array; String list of the literal name of the GISB masters.). Required properties are `compatible`, `reg`, `interrupts`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/string-array, /schemas/types.yaml#/definitions/uint32. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/brcm,gisb-arb.yaml`
- run `make dtbs_check` on DTS files using `brcm,bcm7445-gisb-arb`, `brcm,gisb-arb`, `brcm,bcm74165-gisb-arb`, `brcm,bcm7278-gisb-arb`, `brcm,bcm7435-gisb-arb`, `brcm,bcm7400-gisb-arb`, `brcm,bcm7038-gisb-arb`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/brcm,gisb-arb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/cznic,moxtet.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/cznic,moxtet.yaml

## Purpose
Turris Mox module status and configuration bus (over SPI) The driver finds the devices connected to the bus by itself, but it may be needed to reference some of them from other parts of the device tree. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Marek Behn <kabel@kernel.org> and gives dt-schema a canonical contract for nodes matching `cznic,moxtet`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const cznic,moxtet), `reg` (items ?..1), `interrupts` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 0), `spi-cpol`, `spi-cpha`, `spi-max-frequency`, `interrupt-controller`, `#interrupt-cells` (const 1), plus 1 more. Required properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `spi-cpol`, `spi-cpha`, `interrupts`, `interrupt-controller`, `#interrupt-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: {'type': 'object', 'required': ['reg']}`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/cznic,moxtet.yaml`
- run `make dtbs_check` on DTS files using `cznic,moxtet`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/cznic,moxtet.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,imx8mp-aipstz.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,imx8mp-aipstz.yaml

## Purpose
The secure AIPS bridge (AIPSTZ) acts as a bridge for AHB masters issuing transactions to IP Slave peripherals. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Laurentiu Mihalcea <laurentiu.mihalcea@nxp.com> and gives dt-schema a canonical contract for nodes matching `fsl,imx8mp-aipstz`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const fsl,imx8mp-aipstz), `reg` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 1), `ranges`, `power-domains` (items ?..1), `#access-controller-cells` (const 3; First cell - consumer ID Second cell - consumer type (master or peripheral) Third cell - configurati). Required properties are `compatible`, `reg`, `power-domains`, `#address-cells`, `#size-cells`, `#access-controller-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@(0|[1-9a-f][0-9a-f]*)$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/flag, example includes dt-bindings/clock/imx8mp-clock.h, dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/fsl,imx8mp-aipstz.yaml`
- run `make dtbs_check` on DTS files using `fsl,imx8mp-aipstz`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,imx8mp-aipstz.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,imx8qxp-pixel-link-msi-bus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,imx8qxp-pixel-link-msi-bus.yaml

## Purpose
i.MX8qxp pixel link MSI bus is used to control settings of PHYs, I/Os sitting together with the PHYs. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Liu Ying <victor.liu@nxp.com> and gives dt-schema a canonical contract for nodes matching `fsl,imx8qxp-display-pixel-link-msi-bus`, `fsl,imx8qm-display-pixel-link-msi-bus`, `simple-pm-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `clocks`, `clock-names`. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), child-node patterns `@[0-9a-f]+$`. Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs simple-pm-bus.yaml#, example includes dt-bindings/clock/imx8-lpcg.h, dt-bindings/firmware/imx/rsrc.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/fsl,imx8qxp-pixel-link-msi-bus.yaml`
- run `make dtbs_check` on DTS files using `fsl,imx8qxp-display-pixel-link-msi-bus`, `fsl,imx8qm-display-pixel-link-msi-bus`, `simple-pm-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,imx8qxp-pixel-link-msi-bus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,spba-bus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,spba-bus.yaml

## Purpose
A simple bus enabling access to shared peripherals. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Shawn Guo <shawnguo@kernel.org> and gives dt-schema a canonical contract for nodes matching `fsl,aips`, `fsl,emi`, `fsl,spba-bus`, `simple-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`. Required properties are `compatible`, `#address-cells`, `#size-cells`, `reg`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: {'type': 'object'}`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/fsl,spba-bus.yaml`
- run `make dtbs_check` on DTS files using `fsl,aips`, `fsl,emi`, `fsl,spba-bus`, `simple-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/fsl,spba-bus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/microsoft,vmbus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/microsoft,vmbus.yaml

## Purpose
VMBus is a software bus that implements the protocols for communication between the root or host OS and guest OS'es (virtual machines). It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Saurabh Sengar <ssengar@linux.microsoft.com> and gives dt-schema a canonical contract for nodes matching `microsoft,vmbus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const microsoft,vmbus), `interrupts` (items ?..1; Interrupt is used to report a message from the host.), `#address-cells` (const 2), `#size-cells` (const 1), `ranges`, `dma-coherent`. Required properties are `compatible`, `ranges`, `interrupts`, `#address-cells`, `#size-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/microsoft,vmbus.yaml`
- run `make dtbs_check` on DTS files using `microsoft,vmbus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/microsoft,vmbus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/mti,mips-cdmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/mti,mips-cdmm.yaml

## Purpose
Defines a location of the MIPS Common Device Memory Map registers. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by James Hogan <jhogan@kernel.org> and gives dt-schema a canonical contract for nodes matching `mti,mips-cdmm`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const mti,mips-cdmm), `reg` (items ?..1; Base address and size of an unoccupied memory region, which will be used to map the MIPS CDMM regist). Required properties are `compatible`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/mti,mips-cdmm.yaml`
- run `make dtbs_check` on DTS files using `mti,mips-cdmm`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/mti,mips-cdmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/nvidia,tegra210-aconnect.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/nvidia,tegra210-aconnect.yaml

## Purpose
The Tegra ACONNECT bus is an AXI switch which is used to connect various components inside the Audio Processing Engine (APE). It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Jon Hunter <jonathanh@nvidia.com> and gives dt-schema a canonical contract for nodes matching `nvidia,tegra210-aconnect`, `nvidia,tegra264-aconnect`, `nvidia,tegra234-aconnect`, `nvidia,tegra186-aconnect`, `nvidia,tegra194-aconnect`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `clocks`, `clock-names`, `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, `power-domains` (items ?..1). Required properties are `compatible`, `clocks`, `clock-names`, `power-domains`, `#address-cells`, `#size-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/nvidia,tegra210-aconnect.yaml`
- run `make dtbs_check` on DTS files using `nvidia,tegra210-aconnect`, `nvidia,tegra264-aconnect`, `nvidia,tegra234-aconnect`, `nvidia,tegra186-aconnect`, `nvidia,tegra194-aconnect`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/nvidia,tegra210-aconnect.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/palmbus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/palmbus.yaml

## Purpose
The ralink palmbus controller can be found in all ralink MIPS SoCs. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Sergio Paracuellos <sergio.paracuellos@gmail.com> and gives dt-schema a canonical contract for nodes matching none declared.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const palmbus), `reg` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 1), `ranges`. Required properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/irq.h, dt-bindings/interrupt-controller/mips-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/palmbus.yaml`
- run `make dtbs_check` on DTS files using `palmbus` nodes
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/palmbus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/qcom,ssbi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/qcom,ssbi.yaml

## Purpose
Some Qualcomm MSM devices contain a point-to-point serial bus used to communicate with a limited range of devices (mostly power management chips). It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Andy Gross <agross@kernel.org>, Bjorn Andersson <andersson@kernel.org> and gives dt-schema a canonical contract for nodes matching `qcom,ssbi`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const qcom,ssbi), `reg` (items ?..1), `qcom,controller-type` (enum ssbi, ssbi2, pmic-arbiter; Indicates the SSBI bus variant the controller should use to talk with the slave device.), `pmic` (ref qcom-pm8xxx.yaml#). Required properties are `compatible`, `reg`, `qcom,controller-type`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/mfd/qcom-pm8xxx.yaml#, example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/qcom,ssbi.yaml`
- run `make dtbs_check` on DTS files using `qcom,ssbi`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/qcom,ssbi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/qcom,ssc-block-bus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/qcom,ssc-block-bus.yaml

## Purpose
This binding describes the dependencies (clocks, resets, power domains) which need to be turned on in a sequence before communication over the AHB bus becomes possible. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Michael Srba <Michael.Srba@seznam.cz> and gives dt-schema a canonical contract for nodes matching `qcom,msm8998-ssc-block-bus`, `qcom,ssc-block-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg`, `reg-names`, `clocks` (items ?..6), `clock-names`, `resets`, `reset-names`, `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, plus 2 more. Required properties are `compatible`, `reg`, `reg-names`, `#address-cells`, `#size-cells`, `ranges`, `clocks`, `clock-names`, `power-domains`, `power-domain-names`, `resets`, `reset-names`, plus 1 more.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: {'type': 'object'}`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle-array, example includes dt-bindings/clock/qcom,gcc-msm8998.h, dt-bindings/clock/qcom,rpmcc.h, dt-bindings/power/qcom-rpmpd.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/qcom,ssc-block-bus.yaml`
- run `make dtbs_check` on DTS files using `qcom,msm8998-ssc-block-bus`, `qcom,ssc-block-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/qcom,ssc-block-bus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/renesas,bsc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/renesas,bsc.yaml

## Purpose
The Renesas Bus State Controller (BSC, sometimes called "LBSC within Bus Bridge", or "External Bus Interface") can be found in several Renesas ARM SoCs. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Geert Uytterhoeven <geert+renesas@glider.be> and gives dt-schema a canonical contract for nodes matching `renesas,bsc-r8a73a4`, `renesas,bsc-sh73a0`, `renesas,bsc`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1). Required properties are `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), child-node patterns `@[0-9a-f]+$`. Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs simple-pm-bus.yaml#, example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/renesas,bsc.yaml`
- run `make dtbs_check` on DTS files using `renesas,bsc-r8a73a4`, `renesas,bsc-sh73a0`, `renesas,bsc`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/renesas,bsc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/simple-pm-bus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/simple-pm-bus.yaml

## Purpose
A Simple Power-Managed Bus is a transparent bus that doesn't need a real driver, as it's typically initialized by the boot loader. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Geert Uytterhoeven <geert+renesas@glider.be> and gives dt-schema a canonical contract for nodes matching `simple-pm-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (Shall contain "simple-pm-bus" in addition to a optional bus-specific compatible strings defined in i), `clocks`, `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, `power-domains` (items 1..?). Required properties are `compatible`, `#address-cells`, `#size-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: true`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/qcom,gcc-msm8996.h, dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/simple-pm-bus.yaml`
- run `make dtbs_check` on DTS files using `simple-pm-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/simple-pm-bus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/socionext,uniphier-system-bus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/socionext,uniphier-system-bus.yaml

## Purpose
The UniPhier System Bus is an external bus that connects on-board devices to the UniPhier SoC. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Masahiro Yamada <yamada.masahiro@socionext.com> and gives dt-schema a canonical contract for nodes matching `socionext,uniphier-system-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const socionext,uniphier-system-bus), `reg` (items ?..1), `#address-cells` (const 2; The first cell is the bank number (chip select).), `#size-cells` (const 1), `ranges` (Provide address translation from the System Bus to the parent bus.). Required properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^.*@[1-5],[1-9a-f][0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/socionext,uniphier-system-bus.yaml`
- run `make dtbs_check` on DTS files using `socionext,uniphier-system-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/socionext,uniphier-system-bus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32-etzpc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32-etzpc.yaml

## Purpose
The ETZPC configures TrustZone security in a SoC having bus masters and devices with programmable-security attributes (securable resources). It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Gatien Chevallier <gatien.chevallier@foss.st.com> and gives dt-schema a canonical contract for nodes matching `st,stm32-etzpc`, `simple-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `#address-cells` (const 1), `#size-cells` (const 1), `ranges`, `#access-controller-cells` (const 1; Contains the firewall ID associated to the peripheral.). Required properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `#access-controller-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/stm32mp13-clks.h, dt-bindings/interrupt-controller/arm-gic.h, dt-bindings/reset/stm32mp13-resets.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/st,stm32-etzpc.yaml`
- run `make dtbs_check` on DTS files using `st,stm32-etzpc`, `simple-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32-etzpc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32mp131-dbg-bus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32mp131-dbg-bus.yaml

## Purpose
The STM32 debug bus is in charge of checking the debug configuration of the platform before probing the peripheral drivers that rely on the debug domain. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Gatien Chevallier <gatien.chevallier@foss.st.com> and gives dt-schema a canonical contract for nodes matching `st,stm32mp131-dbg-bus`, `st,stm32mp151-dbg-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `#address-cells` (const 1), `#size-cells` (const 1), `ranges` (items 1..2), `#access-controller-cells` (const 1; Contains the debug profile necessary to access the peripheral.). Required properties are `#access-controller-cells`, `#address-cells`, `#size-cells`, `compatible`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/stm32mp1-clks.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/st,stm32mp131-dbg-bus.yaml`
- run `make dtbs_check` on DTS files using `st,stm32mp131-dbg-bus`, `st,stm32mp151-dbg-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32mp131-dbg-bus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32mp25-rifsc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32mp25-rifsc.yaml

## Purpose
Resource isolation framework (RIF) is a comprehensive set of hardware blocks designed to enforce and manage isolation of STM32 hardware resources like memory and peripherals. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Gatien Chevallier <gatien.chevallier@foss.st.com> and gives dt-schema a canonical contract for nodes matching `st,stm32mp21-rifsc`, `st,stm32mp25-rifsc`, `simple-bus`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `#address-cells` (const 1), `#size-cells` (enum 1, 2), `ranges`, `#access-controller-cells` (const 1; Contains the firewall ID associated to the peripheral.). Required properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `#access-controller-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/st,stm32mp25-rifsc.yaml`
- run `make dtbs_check` on DTS files using `st,stm32mp21-rifsc`, `st,stm32mp25-rifsc`, `simple-bus`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/st,stm32mp25-rifsc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/ti-sysc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/ti-sysc.yaml

## Purpose
Texas Instruments SoCs can have a generic interconnect target module for devices connected to various interconnects such as L3 interconnect using Arteris NoC, and L4 interconnect using Sonics s3220. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Tony Lindgren <tony@atomide.com> and gives dt-schema a canonical contract for nodes matching `ti,sysc-omap2`, `ti,sysc-omap4`, `ti,sysc-omap4-simple`, `ti,sysc-omap2-timer`, `ti,sysc-omap4-timer`, `ti,sysc-omap3430-sr`, `ti,sysc-omap3630-sr`, `ti,sysc-omap4-sr`, `ti,sysc-omap3-sham`, `ti,sysc-omap-aes`, plus 6 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items 1..3; Interconnect target module control registers consisting of REVISION, SYSCONFIG and SYSSTATUS registe), `reg-names` (Interconnect target module control register names consisting of "rev", "sysc" and "syss".), `clocks` (items 1..4; Target module clocks consisting of one functional clock, one interface clock, and up to 8 module spe), `clock-names` (Target module clock names like "fck", "ick", "optck1", "optck2" if the clocks are configurable.), `resets` (items ?..1; Target module reset bit in the RSTCTRL register if wired for the module.), `reset-names` (Target module reset names in the RSTCTRL register, typically named "rstctrl" if only one reset bit i), `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, plus 2 more. Required properties are `compatible`, `#address-cells`, `#size-cells`, `ranges`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: {'type': 'object'}`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/string, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array, example includes dt-bindings/bus/ti-sysc.h, dt-bindings/clock/omap4.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/ti-sysc.yaml`
- run `make dtbs_check` on DTS files using `ti,sysc-omap2`, `ti,sysc-omap4`, `ti,sysc-omap4-simple`, `ti,sysc-omap2-timer`, `ti,sysc-omap4-timer`, `ti,sysc-omap3430-sr`, `ti,sysc-omap3630-sr`, `ti,sysc-omap4-sr`, `ti,sysc-omap3-sham`, `ti,sysc-omap-aes`, plus 6 more
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/ti-sysc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/xlnx,versal-net-cdx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/xlnx,versal-net-cdx.yaml

## Purpose
CDX bus controller for AMD devices is implemented to dynamically detect CDX bus and devices using the firmware. It is a bus/interconnect binding used for SoC bus fabric discovery, address translation, child-node enumeration, and security or error-reporting integration. The binding is maintained by Nipun Gupta <nipun.gupta@amd.com>, Nikhil Agarwal <nikhil.agarwal@amd.com> and gives dt-schema a canonical contract for nodes matching `xlnx,versal-net-cdx`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const xlnx,versal-net-cdx), `#address-cells` (enum 1, 2), `#size-cells` (enum 1, 2), `ranges`, `iommu-map`, `msi-map`, `xlnx,rproc` (ref phandle; phandle to the remoteproc_r5 rproc node using which APU interacts with remote processor.). Required properties are `compatible`, `iommu-map`, `msi-map`, `xlnx,rproc`, `ranges`, `#address-cells`, `#size-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/phandle. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=bus/xlnx,versal-net-cdx.yaml`
- run `make dtbs_check` on DTS files using `xlnx,versal-net-cdx`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/bus/xlnx,versal-net-cdx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/andestech,ax45mp-cache.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/andestech,ax45mp-cache.yaml

## Purpose
A level-2 cache (L2C) is used to improve the system performance by providing a large amount of cache line entries and reasonable access delays. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Lad Prabhakar <prabhakar.mahadev-lad.rj@bp.renesas.com> and gives dt-schema a canonical contract for nodes matching `andestech,qilai-ax45mp-cache`, `renesas,r9a07g043f-ax45mp-cache`, `andestech,ax45mp-cache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items ?..1), `cache-line-size` (const 64), `cache-level` (const 2), `cache-sets` (enum 1024, 2048), `cache-size` (enum 131072, 262144, 524288, 1048576...), `cache-unified`, `next-level-cache`. Required properties are `compatible`, `reg`, `interrupts`, `cache-line-size`, `cache-level`, `cache-sets`, `cache-size`, `cache-unified`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/irq.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/andestech,ax45mp-cache.yaml`
- run `make dtbs_check` on DTS files using `andestech,qilai-ax45mp-cache`, `renesas,r9a07g043f-ax45mp-cache`, `andestech,ax45mp-cache`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/andestech,ax45mp-cache.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/l2c2x0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/l2c2x0.yaml

## Purpose
ARM cores often have a separate L2C210/L2C220/L2C310 (also known as PL210/ PL220/PL310 and variants) based level 2 cache controller. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Rob Herring <robh@kernel.org> and gives dt-schema a canonical contract for nodes matching `arm,pl310-cache`, `arm,l220-cache`, `arm,l210-cache`, `bcm,bcm11351-a2-pl310-cache`, `brcm,bcm11351-a2-pl310-cache`, `marvell,aurora-system-cache`, `marvell,aurora-outer-cache`, `marvell,tauros3-cache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items 1..9), `cache-level` (const 2), `cache-unified`, `cache-size`, `cache-sets`, `cache-block-size`, `cache-line-size`, `arm,data-latency` (ref uint32-array; items 2..3), plus 2 more. Required properties are `compatible`, `cache-unified`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/cache-controller.yaml#, /schemas/types.yaml#/definitions/uint32, /schemas/types.yaml#/definitions/uint32-array. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/l2c2x0.yaml`
- run `make dtbs_check` on DTS files using `arm,pl310-cache`, `arm,l220-cache`, `arm,l210-cache`, `bcm,bcm11351-a2-pl310-cache`, `brcm,bcm11351-a2-pl310-cache`, `marvell,aurora-system-cache`, `marvell,aurora-outer-cache`, `marvell,tauros3-cache`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/l2c2x0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/marvell,kirkwood-cache.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/marvell,kirkwood-cache.yaml

## Purpose
Device-tree schema for Marvell Feroceon/Kirkwood Cache. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Andrew Lunn <andrew@lunn.ch>, Gregory Clement <gregory.clement@bootlin.com> and gives dt-schema a canonical contract for nodes matching `marvell,feroceon-cache`, `marvell,kirkwood-cache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum marvell,feroceon-cache, marvell,kirkwood-cache), `reg` (items ?..1). Required properties are `compatible`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s), 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/marvell,kirkwood-cache.yaml`
- run `make dtbs_check` on DTS files using `marvell,feroceon-cache`, `marvell,kirkwood-cache`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/marvell,kirkwood-cache.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/marvell,tauros2-cache.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/marvell,tauros2-cache.yaml

## Purpose
Device-tree schema for Marvell Tauros2 Cache. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Andrew Lunn <andrew@lunn.ch>, Gregory Clement <gregory.clement@bootlin.com> and gives dt-schema a canonical contract for nodes matching `marvell,tauros2-cache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const marvell,tauros2-cache), `marvell,tauros2-cache-features` (ref uint32; Specify the features supported for the tauros2 cache.). Required properties are `compatible`, `marvell,tauros2-cache-features`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/types.yaml#/definitions/uint32. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/marvell,tauros2-cache.yaml`
- run `make dtbs_check` on DTS files using `marvell,tauros2-cache`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/marvell,tauros2-cache.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/qcom,llcc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/qcom,llcc.yaml

## Purpose
LLCC (Last Level Cache Controller) provides last level of cache memory in SoC, that can be shared by multiple clients. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Bjorn Andersson <andersson@kernel.org> and gives dt-schema a canonical contract for nodes matching `qcom,glymur-llcc`, `qcom,ipq5424-llcc`, `qcom,kaanapali-llcc`, `qcom,qcs615-llcc`, `qcom,qcs8300-llcc`, `qcom,qdu1000-llcc`, `qcom,sa8775p-llcc`, `qcom,sar1130p-llcc`, `qcom,sar2130p-llcc`, `qcom,sc7180-llcc`, plus 15 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum qcom,glymur-llcc, qcom,ipq5424-llcc, qcom,kaanapali-llcc, qcom,qcs615-llcc...), `reg` (items 1..14), `reg-names` (items 1..14), `interrupts` (items ?..1), `nvmem-cells`, `nvmem-cell-names`. Required properties are `compatible`, `reg`, `reg-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 10 `allOf` composition block(s), 10 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/interrupt-controller/arm-gic.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/qcom,llcc.yaml`
- run `make dtbs_check` on DTS files using `qcom,glymur-llcc`, `qcom,ipq5424-llcc`, `qcom,kaanapali-llcc`, `qcom,qcs615-llcc`, `qcom,qcs8300-llcc`, `qcom,qdu1000-llcc`, `qcom,sa8775p-llcc`, `qcom,sar1130p-llcc`, `qcom,sar2130p-llcc`, `qcom,sc7180-llcc`, plus 15 more
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/qcom,llcc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/sifive,ccache0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/sifive,ccache0.yaml

## Purpose
The SiFive Composable Cache Controller is used to provide access to fast copies of memory for masters in a Core Complex. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Paul Walmsley <paul.walmsley@sifive.com> and gives dt-schema a canonical contract for nodes matching `sifive,ccache0`, `sifive,fu540-c000-ccache`, `sifive,fu740-c000-ccache`, `eswin,eic7700-l3-cache`, `starfive,jh7100-ccache`, `starfive,jh7110-ccache`, `microchip,mpfs-ccache`, `microchip,pic64gx-ccache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `interrupts` (items 3..?), `cache-block-size` (const 64), `cache-level` (enum 2, 3), `cache-sets` (enum 1024, 2048, 4096), `cache-size` (enum 2097152, 4194304), `cache-unified`, `next-level-cache`, `memory-region` (items ?..1; The reference to the reserved-memory for the L2 Loosely Integrated Memory region.). Required properties are `compatible`, `cache-block-size`, `cache-level`, `cache-sets`, `cache-size`, `cache-unified`, `interrupts`, `reg`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 7 `allOf` composition block(s), 6 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/cache-controller.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/sifive,ccache0.yaml`
- run `make dtbs_check` on DTS files using `sifive,ccache0`, `sifive,fu540-c000-ccache`, `sifive,fu740-c000-ccache`, `eswin,eic7700-l3-cache`, `starfive,jh7100-ccache`, `starfive,jh7110-ccache`, `microchip,mpfs-ccache`, `microchip,pic64gx-ccache`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/sifive,ccache0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/socionext,uniphier-system-cache.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/socionext,uniphier-system-cache.yaml

## Purpose
UniPhier ARM 32-bit SoCs are integrated with a full-custom outer cache controller system. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Masahiro Yamada <yamada.masahiro@socionext.com> and gives dt-schema a canonical contract for nodes matching `socionext,uniphier-system-cache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const socionext,uniphier-system-cache), `reg` (items ?..3; should contain 3 regions: control register, revision register, operation register, in this order.), `interrupts` (items 1..4; Interrupts can be used to notify the completion of cache operations.), `cache-unified`, `cache-size`, `cache-sets`, `cache-line-size`, `cache-level`, `next-level-cache`. Required properties are `compatible`, `reg`, `interrupts`, `cache-unified`, `cache-size`, `cache-sets`, `cache-line-size`, `cache-level`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/cache-controller.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; interrupt cardinality or naming mistakes can pass review until dtbs_check or runtime IRQ setup exercises the node.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/socionext,uniphier-system-cache.yaml`
- run `make dtbs_check` on DTS files using `socionext,uniphier-system-cache`
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/socionext,uniphier-system-cache.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/starfive,jh8100-starlink-cache.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/starfive,jh8100-starlink-cache.yaml

## Purpose
StarFive's StarLink Cache Controller manages the L3 cache shared between clusters of CPU cores. It is a cache-controller binding used for cache-controller description for CPU/system cache drivers and cache hierarchy validation. The binding is maintained by Joshua Yeong <joshua.yeong@starfivetech.com> and gives dt-schema a canonical contract for nodes matching `starfive,jh8100-starlink-cache`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1). Required properties are `compatible`, `reg`, `cache-block-size`, `cache-level`, `cache-sets`, `cache-size`, `cache-unified`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 `allOf` composition block(s). Property policy is `unevaluatedProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/cache-controller.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=cache/starfive,jh8100-starlink-cache.yaml`
- run `make dtbs_check` on DTS files using `starfive,jh8100-starlink-cache`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cache/starfive,jh8100-starlink-cache.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/chrome/google,cros-ec-typec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/chrome/google,cros-ec-typec.yaml

## Purpose
Chrome OS devices have an Embedded Controller(EC) which has access to Type C port state. It is a Chrome EC binding used for Chrome OS embedded-controller Type-C connector enumeration and role-switch integration. The binding is maintained by Benson Leung <bleung@chromium.org>, Abhishek Pandit-Subedi <abhishekpandit@chromium.org>, Andrei Kuchynski <akuchynski@chromium.org>, ukasz Bartosik <ukaszb@chromium.org>, plus 1 more and gives dt-schema a canonical contract for nodes matching `google,cros-ec-typec`, `google,cros-ec-ucsi`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum google,cros-ec-typec, google,cros-ec-ucsi), `#address-cells` (const 1), `#size-cells` (const 0). Required properties are `compatible`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses child-node patterns `^connector@[0-9a-f]+$`. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include refs /schemas/connector/usb-connector.yaml#. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; child node regexes must be kept broad enough for real DTS node names while still rejecting unrelated children.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=chrome/google,cros-ec-typec.yaml`
- run `make dtbs_check` on DTS files using `google,cros-ec-typec`, `google,cros-ec-ucsi`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/chrome/google,cros-ec-typec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/actions,owl-cmu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/actions,owl-cmu.yaml

## Purpose
The Actions Semi Owl Clock Management Unit generates and supplies clock to various controllers within the SoC. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Manivannan Sadhasivam <manivannan.sadhasivam@linaro.org> and gives dt-schema a canonical contract for nodes matching `actions,s500-cmu`, `actions,s700-cmu`, `actions,s900-cmu`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum actions,s500-cmu, actions,s700-cmu, actions,s900-cmu), `reg` (items ?..1), `clocks`, `#clock-cells` (const 1), `#reset-cells` (const 1). Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`, `#reset-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/actions,owl-cmu.yaml`
- run `make dtbs_check` on DTS files using `actions,s500-cmu`, `actions,s700-cmu`, `actions,s900-cmu`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/actions,owl-cmu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/adi,axi-clkgen.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/adi,axi-clkgen.yaml

## Purpose
The axi_clkgen IP core is a software programmable clock generator, that can be synthesized on various FPGA platforms. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Lars-Peter Clausen <lars@metafoo.de>, Michael Hennerich <michael.hennerich@analog.com> and gives dt-schema a canonical contract for nodes matching `adi,axi-clkgen-2.00.a`, `adi,zynqmp-axi-clkgen-2.00.a`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum adi,axi-clkgen-2.00.a, adi,zynqmp-axi-clkgen-2.00.a), `reg` (items ?..1), `clocks` (items 2..3; Specifies the reference clock(s) from which the output frequency is derived.), `clock-names`, `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/adi,axi-clkgen.yaml`
- run `make dtbs_check` on DTS files using `adi,axi-clkgen-2.00.a`, `adi,zynqmp-axi-clkgen-2.00.a`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/adi,axi-clkgen.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/airoha,en7523-scu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/airoha,en7523-scu.yaml

## Purpose
This node defines the System Control Unit of the EN7523 SoC, a collection of registers configuring many different aspects of the SoC. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Felix Fietkau <nbd@nbd.name>, John Crispin <nbd@nbd.name> and gives dt-schema a canonical contract for nodes matching `airoha,en7523-scu`, `airoha,en7581-scu`, `econet,en751221-scu`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items 1..?), `#clock-cells` (const 1; The first cell indicates the clock number, see [1] for available clocks.), `#reset-cells` (const 1; ID of the controller reset line). Required properties are `compatible`, `reg`, `#clock-cells`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 `allOf` composition block(s), 2 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/en7523-clk.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/airoha,en7523-scu.yaml`
- run `make dtbs_check` on DTS files using `airoha,en7523-scu`, `airoha,en7581-scu`, `econet,en751221-scu`
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/airoha,en7523-scu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ahb-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ahb-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 AHB Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-ahb-clk`, `allwinner,sun6i-a31-ahb1-clk`, `allwinner,sun8i-h3-ahb2-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun4i-a10-ahb-clk, allwinner,sun6i-a31-ahb1-clk, allwinner,sun8i-h3-ahb2-clk), `reg` (items ?..1), `clocks` (items 1..4; The parent order must match the hardware programming order.), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 3 `allOf` composition block(s), 3 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-ahb-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-ahb-clk`, `allwinner,sun6i-a31-ahb1-clk`, `allwinner,sun8i-h3-ahb2-clk`
- the 3 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ahb-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-apb0-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-apb0-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 APB0 Bus Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-apb0-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun4i-a10-apb0-clk), `reg` (items ?..1), `clocks` (items ?..1), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-apb0-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-apb0-clk`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-apb0-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-apb1-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-apb1-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 APB1 Bus Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-apb1-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun4i-a10-apb1-clk), `reg` (items ?..1), `clocks` (items ?..3; The parent order must match the hardware programming order.), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-apb1-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-apb1-clk`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-apb1-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-axi-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-axi-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 AXI Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-axi-clk`, `allwinner,sun8i-a23-axi-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun4i-a10-axi-clk, allwinner,sun8i-a23-axi-clk), `reg` (items ?..1), `clocks` (items ?..1), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-axi-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-axi-clk`, `allwinner,sun8i-a23-axi-clk`
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-axi-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ccu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ccu.yaml

## Purpose
Device-tree schema for Allwinner Clock Control Unit. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-ccu`, `allwinner,sun5i-a10s-ccu`, `allwinner,sun5i-a13-ccu`, `allwinner,sun6i-a31-ccu`, `allwinner,sun7i-a20-ccu`, `allwinner,sun8i-a23-ccu`, `allwinner,sun8i-a33-ccu`, `allwinner,sun8i-a83t-ccu`, `allwinner,sun8i-a83t-r-ccu`, `allwinner,sun8i-h3-ccu`, plus 18 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun4i-a10-ccu, allwinner,sun5i-a10s-ccu, allwinner,sun5i-a13-ccu, allwinner,sun6i-a31-ccu...), `reg` (items ?..1), `clocks` (items 2..?), `clock-names` (items 2..?), `#clock-cells` (const 1), `#reset-cells` (const 1). Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 2 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-ccu.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-ccu`, `allwinner,sun5i-a10s-ccu`, `allwinner,sun5i-a13-ccu`, `allwinner,sun6i-a31-ccu`, `allwinner,sun7i-a20-ccu`, `allwinner,sun8i-a23-ccu`, `allwinner,sun8i-a33-ccu`, `allwinner,sun8i-a83t-ccu`, `allwinner,sun8i-a83t-r-ccu`, `allwinner,sun8i-h3-ccu`, plus 18 more
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ccu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-cpu-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-cpu-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 CPU Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-cpu-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun4i-a10-cpu-clk), `reg` (items ?..1), `clocks` (items ?..4; The parent order must match the hardware programming order.), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-cpu-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-cpu-clk`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-cpu-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-display-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-display-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 Display Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-display-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun4i-a10-display-clk), `reg` (items ?..1), `clocks` (items ?..3; The parent order must match the hardware programming order.), `#clock-cells` (const 0), `#reset-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-display-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-display-clk`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-display-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-gates-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-gates-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 Bus Gates Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-gates-clk`, `allwinner,sun4i-a10-axi-gates-clk`, `allwinner,sun4i-a10-ahb-gates-clk`, `allwinner,sun5i-a10s-ahb-gates-clk`, `allwinner,sun5i-a13-ahb-gates-clk`, `allwinner,sun7i-a20-ahb-gates-clk`, `allwinner,sun6i-a31-ahb1-gates-clk`, `allwinner,sun8i-a23-ahb1-gates-clk`, `allwinner,sun9i-a80-ahb0-gates-clk`, `allwinner,sun9i-a80-ahb1-gates-clk`, plus 21 more.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible`, `reg` (items ?..1), `clocks` (items ?..1), `#clock-cells` (const 1; This additional argument passed to that clock is the offset of the bit controlling this particular g), `clock-indices` (items 1..64), `clock-output-names` (items 1..64). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-indices`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-gates-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-gates-clk`, `allwinner,sun4i-a10-axi-gates-clk`, `allwinner,sun4i-a10-ahb-gates-clk`, `allwinner,sun5i-a10s-ahb-gates-clk`, `allwinner,sun5i-a13-ahb-gates-clk`, `allwinner,sun7i-a20-ahb-gates-clk`, `allwinner,sun6i-a31-ahb1-gates-clk`, `allwinner,sun8i-a23-ahb1-gates-clk`, `allwinner,sun9i-a80-ahb0-gates-clk`, `allwinner,sun9i-a80-ahb1-gates-clk`, plus 21 more
- the 3 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-gates-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mbus-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mbus-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 MBUS Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun5i-a13-mbus-clk`, `allwinner,sun8i-a23-mbus-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun5i-a13-mbus-clk, allwinner,sun8i-a23-mbus-clk), `reg` (items ?..1), `clocks` (items ?..3; The parent order must match the hardware programming order.), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-mbus-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun5i-a13-mbus-clk`, `allwinner,sun8i-a23-mbus-clk`
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mbus-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mmc-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mmc-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 Module 1 Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-mmc-clk`, `allwinner,sun9i-a80-mmc-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun4i-a10-mmc-clk, allwinner,sun9i-a80-mmc-clk), `reg` (items ?..1), `clocks` (items 2..3; The parent order must match the hardware programming order.), `#clock-cells` (const 1; There is three different outputs: the main clock, with the ID 0, and the output and sample clocks, w), `clock-output-names` (items ?..3). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses 1 conditional `if` branch(es). Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-mmc-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-mmc-clk`, `allwinner,sun9i-a80-mmc-clk`
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mmc-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mod0-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mod0-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 Module 0 Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-mod0-clk`, `allwinner,sun9i-a80-mod0-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun4i-a10-mod0-clk, allwinner,sun9i-a80-mod0-clk), `reg` (items ?..1), `clocks` (items 2..3; The parent order must match the hardware programming order.), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-mod0-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-mod0-clk`, `allwinner,sun9i-a80-mod0-clk`
- the 2 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mod0-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mod1-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mod1-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 Module 1 Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-mod1-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun4i-a10-mod1-clk), `reg` (items ?..1), `clocks` (items ?..4; The parent order must match the hardware programming order.), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include example includes dt-bindings/clock/sun4i-a10-pll2.h. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-mod1-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-mod1-clk`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-mod1-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-osc-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-osc-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 Gateable Oscillator Clock. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-osc-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun4i-a10-osc-clk), `reg` (items ?..1), `#clock-cells` (const 0), `clock-frequency` (Frequency of the main oscillator.), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clock-frequency`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-osc-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-osc-clk`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-osc-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll1-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll1-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 CPU PLL. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-pll1-clk`, `allwinner,sun6i-a31-pll1-clk`, `allwinner,sun8i-a23-pll1-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (enum allwinner,sun4i-a10-pll1-clk, allwinner,sun6i-a31-pll1-clk, allwinner,sun8i-a23-pll1-clk), `reg` (items ?..1), `clocks` (items ?..1), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-pll1-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-pll1-clk`, `allwinner,sun6i-a31-pll1-clk`, `allwinner,sun8i-a23-pll1-clk`
- the 3 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll1-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll3-clk.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll3-clk.yaml

## Purpose
Device-tree schema for Allwinner A10 Video PLL. It is a clock-controller binding used for clock provider registration, parent clock selection, register mapping, and reset/clock-output validation. The binding is maintained by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org> and gives dt-schema a canonical contract for nodes matching `allwinner,sun4i-a10-pll3-clk`.

## Important APIs/types/functions
This file is declarative YAML rather than executable code. Its operational entry points are `$id`, `$schema`, `title`, `maintainers`, `description`, top-level `properties`, `required`, optional composition keywords, and examples consumed by Linux `dt-schema`. Important properties are `compatible` (const allwinner,sun4i-a10-pll3-clk), `reg` (items ?..1), `clocks` (items ?..1), `#clock-cells` (const 0), `clock-output-names` (items ?..1). Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`.

## Control flow
Validation flows through dt-schema object matching: the node is selected by `compatible`, required keys are checked, property cardinality and enum/const rules are applied, and referenced common schemas are evaluated. This file uses a straight top-level object schema. Property policy is `additionalProperties: false`.

## State and persistence behavior
The binding stores no runtime state and persists no data. Its persistent contract is the checked-in schema itself: once DTS files adopt the documented compatibles, property names, cell counts, child-node names, or phandle layouts, kernel drivers and boot firmware rely on those values staying compatible.

## Dependencies and integration points
Dependencies include depends mainly on the dt-schema core/meta-schemas and compatible strings. Integration points are board DTS files under `arch/*/boot/dts`, dt-schema validation, the Linux driver or subsystem selected by the compatible string, and any common binding referenced for clocks, resets, GPIOs, interrupts, PHYs, power domains, buses, or cache topology.

## Risks and edge cases
compatible ordering and fallback strings must stay aligned with the in-kernel driver match tables and board DTS files; register region count, names, and address-cell assumptions are easy to break when SoC variants add windows; clock parent/order changes can silently alter provider indices or consumer phandles.

## Test signals
- run `make dt_binding_check DT_SCHEMA_FILES=clock/allwinner,sun4i-a10-pll3-clk.yaml`
- run `make dtbs_check` on DTS files using `allwinner,sun4i-a10-pll3-clk`
- the 1 embedded example block(s) should compile through dtc and validate against referenced schemas
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll3-clk.yaml -->
